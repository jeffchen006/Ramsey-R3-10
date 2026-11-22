#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, product
from pathlib import Path
from time import process_time_ns

import networkx as nx

from panel18_bind import frame_binding, read_integer_rows
from verify_panel17 import bits, graph6


def word(sites):
    return sum(1 << site for site in sites)


def trace(graph, sites):
    return tuple(word(new for new, old in enumerate(sites) if graph[site] >> old & 1)
                 for site in sites)


def edge_sets(graph):
    return tuple(frozenset(bits(row)) for row in graph)


def independent(graph, subset):
    return all(not graph[site] & subset for site in bits(subset))


def forbidden_independent(graph, size):
    def extend(remaining, needed):
        if not needed:
            return True
        while remaining.bit_count() >= needed:
            first = remaining & -remaining
            remaining ^= first
            if extend(remaining & ~graph[first.bit_length() - 1], needed - 1):
                return True
        return False

    return extend((1 << len(graph)) - 1, size)


def triangle_free(graph):
    return all(not graph[site] & graph[other]
               for site, row in enumerate(graph) for other in bits(row))


def nxgraph(graph):
    result = nx.Graph()
    result.add_nodes_from(range(len(graph)))
    result.add_edges_from((site, other) for site, row in enumerate(graph) for other in bits(row))
    return result


@cache
def small_card(core, neutral, count, contacts, alpha_cap):
    if count <= 1:
        return True
    assert count == 2 and -1 <= neutral < len(core)
    need = tuple(word(sites) for sites in combinations(range(len(core)), alpha_cap - 1)
                 if independent(core, word(sites)))
    full = (1 << len(need)) - 1
    covers = [set(), set()]
    for row in range(1 << len(core)):
        if independent(core, row):
            sign = (row >> neutral & 1) if neutral >= 0 else 0
            covers[sign].add(word(index for index, witness in enumerate(need) if row & witness))
    return any(first | second == full
               for first in covers[contacts == 2] for second in covers[contacts >= 1])


def join_card(core, singleton_rows):
    core_order = len(core)
    root = core_order + len(singleton_rows)
    return (tuple(row | word(core_order + index for index, mask in enumerate(singleton_rows)
                             if mask >> site & 1) for site, row in enumerate(core))
            + tuple((1 << root) | row for row in singleton_rows)
            + (word(range(core_order, root)),))


@cache
def literal_small(core, neutral, count, contacts, alpha_cap):
    rows = tuple(mask for mask in range(1 << len(core))
                 if all(not ((mask >> site & 1) and (mask >> other & 1))
                        for site, other in combinations(range(len(core)), 2)
                        if core[site] >> other & 1))
    for proposed in product(rows, repeat=count):
        if neutral >= 0 and sum(mask >> neutral & 1 for mask in proposed) != contacts:
            continue
        if not forbidden_independent(join_card(core, proposed), alpha_cap + 1):
            return True
    return False


def catalogue(path):
    return tuple(map(tuple, graph6(path)))


def rooted_cards(graphs, count):
    for host, graph in enumerate(graphs):
        for root, row in enumerate(graph):
            if row.bit_count() == count:
                singles = tuple(bits(row))
                keep = tuple(site for site in range(len(graph)) if site != root and site not in singles)
                yield host, root, keep, singles, trace(graph, keep)


def filt_signature(graph):
    return tuple(sorted((row.bit_count(), tuple(sorted(graph[other].bit_count() for other in bits(row))))
                        for row in graph))


def literal_card_table(core, neutral, graphs):
    target = nxgraph(core)
    signature = filt_signature(core)
    result = {}
    considered = Counter()
    for count, category in graphs.items():
        for host, root, keep, singles, residual in rooted_cards(category, count):
            considered[count] += 1
            if signature != filt_signature(residual):
                continue
            support = set()
            for mapping in nx.algorithms.isomorphism.GraphMatcher(target, nxgraph(residual)).isomorphisms_iter():
                if neutral < 0:
                    support.add(-1)
                    break
                card_site = keep[mapping[neutral]]
                support.add(sum(category[host][card_site] >> site & 1 for site in singles))
            if support:
                result[count, host, root] = tuple(sorted(support))
    return result, considered


def indexed_card_table(core, neutral, graphs, index_path):
    data = json.loads(index_path.read_text())
    assert data['format'] == 'r310.deletion-cards/1'
    target = nxgraph(core)
    result = {}
    considered = Counter()
    match_count = 0
    seen = set()
    for key, group in sorted(data['groups'].items()):
        canonical_graph = nx.from_graph6_bytes(key.encode('ascii'))
        assert len(canonical_graph) == len(core)
        matcher = nx.algorithms.isomorphism.GraphMatcher(target, canonical_graph)
        mapping = next(matcher.isomorphisms_iter(), None)
        for order, host, root, canonical_core, singletons, contacts in group['cards']:
            count = len(singletons)
            assert order == 13 + count and count in graphs
            identity = (count, host, root)
            assert identity not in seen
            seen.add(identity)
            considered[count] += 1
            if mapping is None:
                continue
            graph = graphs[count][host]
            assert set(singletons) == set(bits(graph[root])) and len(canonical_core) == len(core)
            assert set(canonical_core) == set(range(order)) - {root, *singletons}
            assert tuple(contacts) == tuple(word(index for index, site in enumerate(canonical_core)
                                                if graph[singleton] >> site & 1) for singleton in singletons)
            assert all(bool(graph[first] >> second & 1) == canonical_graph.has_edge(pos, other)
                       for pos, first in enumerate(canonical_core) for other, second in enumerate(canonical_core))
            result[identity] = ((-1,) if neutral < 0 else
                                tuple(sorted({sum(mask >> auto[mapping[neutral]] & 1 for mask in contacts)
                                              for auto in group['aut']})))
        if mapping is not None:
            match_count += 1
            exact_aut = {tuple(permutation[site] for site in range(len(core))) for permutation in
                         nx.algorithms.isomorphism.GraphMatcher(canonical_graph, canonical_graph).isomorphisms_iter()}
            assert {tuple(auto) for auto in group['aut']} == exact_aut
    assert match_count == 1
    return result, considered


def old_groups(marks, graph_order):
    groups = [0] * len(marks)
    for site in range(graph_order):
        where = tuple(index for index, mark in enumerate(marks) if mark >> site & 1)
        if len(where) == 1:
            groups[where[0]] |= 1 << site
    return tuple(groups)


def row_join(rows, groups, neutral_row, card_ok):
    results = []
    for selected in rows:
        cards = [(remaining.bit_count(),
                  (remaining & neutral_row).bit_count() if neutral_row is not None else -1)
                 for group in groups for remaining in (group & ~selected,)]
        flags = tuple(card_ok(*card) for card in cards)
        results.append((selected, word(index for index, flag in enumerate(flags) if flag), cards))
    return results


def production_rows(graph, neutral, marks, neutral_bit):
    neutral_mask = (1 << neutral) if neutral_bit else 0
    for sites in combinations((site for site in range(len(graph)) if site != neutral), 3):
        row = word(sites)
        if independent(graph, row | neutral_mask) and all((row & mark).bit_count() <= 2 for mark in marks):
            yield row


def literal_rows(graph, neutral, marks, neutral_bit):
    edges = edge_sets(graph)
    pools = tuple(set(bits(mark)) for mark in marks)
    for selected in range(1 << len(graph)):
        if selected >> neutral & 1 or selected.bit_count() != 3:
            continue
        sites = set(bits(selected))
        if any(len(pool & sites) > 2 for pool in pools):
            continue
        vertices = sites | ({neutral} if neutral_bit else set())
        if any(second in edges[first] for first, second in combinations(vertices, 2)):
            continue
        yield selected


def bind_bins(args, cases):
    left = cases[0][0]
    host, neutral, *marks = cases[0][2:8]
    graph = args.graphs[3][host]
    assert len(graph) == 16 and len(args.graphs[4][0]) == 17
    total, degree, _ = frame_binding(graph, neutral, tuple(marks), 9, 5, 4, 9)
    assert (total, degree) == (66, 4)
    root = args.root
    assert graph[root].bit_count() == 3 and sum(mark >> root & 1 for mark in marks) == 3
    core_sites = tuple(site for site in range(len(graph)) if site != root and not (graph[root] >> site & 1))
    core = trace(graph, core_sites)
    assert len(core) == 12 and triangle_free(core) and not forbidden_independent(core, 5)
    core_neutral = core_sites.index(neutral) if neutral in core_sites else -1
    assert (core_neutral < 0) == bool(graph[root] >> neutral & 1)
    assert sum(mask & (1 << root) != 0 for mask in marks) == 3
    assert len({case[:2] for case in cases}) == len(cases)
    for case in cases:
        assert case[0] == left and case[2:8] == tuple([host, neutral, *marks])
        right_host, right_neutral, *right_marks = case[8:]
        opposite = args.graphs[4][right_host]
        total, degree, _ = frame_binding(opposite, right_neutral, tuple(right_marks), 9, 5, 4, 9)
        assert (total, degree) == (75, 5)
        assert sum(sum(mark >> site & 1 for mark in right_marks) == 3 for site in range(len(opposite))) == 1
    return core, core_neutral, host, root


def all_literal_rows(graph, neutral, marks, neutral_bit, rows, card_ok):
    memberships = tuple(tuple(pole for pole, mark in enumerate(marks) if mark >> site & 1)
                        for site in range(len(graph)))
    answer = []
    for selected in rows:
        restored = [[] for _ in marks]
        for site, support in enumerate(memberships):
            if len(support) == 1 and not (selected >> site & 1):
                restored[support[0]].append(site)
        cards = [(len(singles), -1 if neutral_bit else sum(graph[neutral] >> site & 1 for site in singles))
                 for singles in restored]
        flags = word(index for index, (size, contacts) in enumerate(cards) if card_ok(size, contacts))
        answer.append((selected, flags, cards))
    return answer


def run_target(args):
    started = process_time_ns()
    args.graphs = {3: catalogue(args.cat16), 4: catalogue(args.cat17)}
    assert {len(category) for category in args.graphs.values()} == {2576, 7}
    cases = tuple(read_integer_rows(args.cases, 14))
    assert cases and tuple(sorted(cases)) == cases
    core, core_neutral, host, root = bind_bins(args, cases)
    neutral_bit = core_neutral < 0
    after_bind = process_time_ns()
    table, considered = (literal_card_table(core, core_neutral, args.graphs) if args.mode == 'literal'
                         else indexed_card_table(core, core_neutral, args.graphs, args.indexed))
    assert considered == {3: 1458, 4: 21}
    assert (3, host, root) in table
    high_accept = {(count, contacts) for (count, _, _), contacts_set in table.items() for contacts in contacts_set}
    low_card = literal_small if args.mode == 'literal' else small_card

    @cache
    def card_ok(count, contacts):
        if count <= 2:
            return low_card(core, core_neutral, count, contacts, 5)
        return (count, contacts) in high_accept

    with args.card_detail.open('w') as stream:
        print('core_neutral', core_neutral, 'core_rows', *core, file=stream)
        for (count, catalog_host, catalog_root), contacts in sorted(table.items()):
            print(count, catalog_host, catalog_root, *contacts, file=stream)
    after_cards = process_time_ns()
    row_ns = filter_ns = 0
    totals = Counter()
    survivors = []
    with args.detail.open('w') as stream:
        print('frame16\tframe17\trow\tpole_mask\t(k,z)0\t(k,z)1\t(k,z)2\t(k,z)3', file=stream)
        print('frame16 frame17 rows live all_four_marginals k0 k1 k2 k3 k4')
        for case in cases:
            left, right = case[:2]
            right_host, right_neutral, *right_marks = case[8:]
            graph = args.graphs[4][right_host]
            before_row = process_time_ns()
            row_function = literal_rows if args.mode == 'literal' else production_rows
            rows = tuple(row_function(graph, right_neutral, right_marks, neutral_bit))
            before_filter = process_time_ns()
            if args.mode == 'literal':
                answers = all_literal_rows(graph, right_neutral, right_marks, neutral_bit, rows, card_ok)
            else:
                answers = row_join(rows, old_groups(right_marks, len(graph)),
                                   graph[right_neutral] if not neutral_bit else None, card_ok)
            row_ns += before_filter - before_row
            filter_ns += process_time_ns() - before_filter
            flags_or = 0
            counts = Counter()
            live = 0
            for selected, flags, cards in sorted(answers):
                flags_or |= flags
                live += flags == 15
                counts.update(count for count, contacts in cards)
                print(left, right, selected, flags, *(f'{count},{contacts}' for count, contacts in cards),
                      sep='\t', file=stream)
            assert sum(counts.values()) == 4 * len(answers) and not any(count > 4 for count in counts)
            print(left, right, len(answers), live, int(flags_or == 15), *(counts[k] for k in range(5)))
            if live:
                survivors.append((left, right))
            totals['rows'] += len(answers)
            totals['live rows'] += live
            totals['all four marginals'] += flags_or == 15
    print('case totals', len(cases), 'surviving headers', len(survivors), sorted(totals.items()))
    print('timing_ns pre_bind', after_bind - started, 'cards', after_cards - after_bind,
          'row_generation', row_ns, 'filter', filter_ns, 'total_run', process_time_ns() - started)


def run_control():
    control = tuple(word((site + sign * jump) % 35 for jump in (1, 7, 11, 16) for sign in (-1, 1))
                    for site in range(35))
    assert triangle_free(control) and not forbidden_independent(control, 9)
    count_pairs = count_cards = count_joint = count_paired = 0
    for first, second in combinations(range(35), 2):
        poles = control[first] & control[second]
        if poles.bit_count() != 4:
            continue
        count_pairs += 1
        exterior = tuple(site for site in range(35) if not ((1 << site) & (poles | word((first, second)))))
        core_sites = tuple(site for site in exterior if not control[site] & poles)
        core = trace(control, core_sites)
        assert len(core) == 13 and not forbidden_independent(core, 5)
        groups = defaultdict(list)
        for site in exterior:
            groups[control[site] & poles].append(site)
        for pole in bits(poles):
            singles = tuple(groups[1 << pole])
            assert len(singles) == 2
            restored = trace(control, (*core_sites, *singles, pole))
            rows = tuple(word(index for index, site in enumerate(core_sites) if control[vertex] >> site & 1)
                         for vertex in singles)
            assert restored == join_card(core, rows) and not forbidden_independent(restored, 6)
            count_cards += 1
        for fifth in bits(poles):
            old = poles ^ 1 << fifth
            available = word(site for site in exterior if control[site] & old)
            row = control[fifth] & available
            assert row.bit_count() == 4 and independent(control, row)
            old_singletons = [word(site for site in exterior if control[site] & old == 1 << pole)
                              for pole in bits(old)]
            assert all(group & ~row == word(groups[1 << pole])
                       for group, pole in zip(old_singletons, bits(old), strict=True))
            table = row_join([row], old_singletons, control[core_sites[0]],
                             lambda size, contacts: small_card(core, 0, size, contacts, 5))
            assert table[0][1] == 7 and small_card(core, 0, 2,
                                                   (control[core_sites[0]] & word(groups[1 << fifth])).bit_count(), 5)
            count_joint += 1
        tight_pairs = tuple(pair for pair in combinations(tuple(bits(poles)), 2)
                            if len(groups[word(pair)]) == 2)
        for pair, other in combinations(tight_pairs, 2):
            if set(pair).isdisjoint(other):
                for selection in (pair, other):
                    full = (*core_sites, *groups[1 << selection[0]], *groups[1 << selection[1]],
                            *groups[word(selection)], *selection)
                    assert not forbidden_independent(trace(control, full), 7)
                count_paired += 1
    assert (count_pairs, count_cards, count_joint, count_paired) == (105, 420, 420, 210)
    print('C35 pairs', count_pairs, 'restored cards', count_cards, 'shared-row plants', count_joint,
          'disjoint pair plants', count_paired)


def exhaustive_control():
    histogram = Counter()
    for order in range(1, 5):
        edges = tuple(combinations(range(order), 2))
        for mask in range(1 << len(edges)):
            rows = [0] * order
            for edge in bits(mask):
                first, second = edges[edge]
                rows[first] |= 1 << second
                rows[second] |= 1 << first
            core = tuple(rows)
            if not triangle_free(core):
                continue
            for cap in range(2, min(5, order + 2)):
                if forbidden_independent(core, cap):
                    continue
                for count in range(3):
                    for neutral in range(-1, order):
                        for contacts in ((-1,) if neutral < 0 else range(count + 1)):
                            fast = small_card(core, neutral, count, contacts, cap)
                            literal = literal_small(core, neutral, count, contacts, cap)
                            assert fast == literal, (core, count, neutral, contacts, cap)
                            histogram[count, fast] += 1
    assert histogram[2, False] > 0 and histogram[2, True] > 0
    print('exhaustive labelled small controls', sum(histogram.values()), sorted(histogram.items()))
    sets = (3, 12, 0, 0)
    rows = (1, 2, 4, 8)
    test = lambda size, contacts: small_card((2, 1), 0, size, contacts, 2)
    negative = row_join(rows, sets, 15, test)
    positive = row_join(rows, sets, 7, test)
    assert [flags for _, flags, _ in negative] == [13, 13, 14, 14]
    assert [flags for _, flags, _ in positive] == [15, 15, 14, 14]
    print('joint planted rows 2; corrupt neutral incidence permits each pole separately but common rows 0')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('control', 'indexed', 'literal'))
    parser.add_argument('--cat16', type=Path)
    parser.add_argument('--cat17', type=Path)
    parser.add_argument('--cases', type=Path)
    parser.add_argument('--root', type=int)
    parser.add_argument('--indexed', type=Path)
    parser.add_argument('--detail', type=Path)
    parser.add_argument('--card-detail', type=Path)
    args = parser.parse_args()
    if args.mode == 'control':
        exhaustive_control()
        run_control()
        return
    run_target(args)


if __name__ == '__main__':
    main()
