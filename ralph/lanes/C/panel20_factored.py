#!/usr/bin/env python3
import argparse
from collections import Counter
from functools import cache
from itertools import combinations
from pathlib import Path

import networkx as nx

from panel18_bind import frame_binding, read_integer_rows
from panel19_bind import frame_rows
from panel19_fifth import (catalogue, edge_sets, forbidden_independent, independent, nxgraph,
                           rooted_cards, trace, triangle_free, word)
from verify_panel17 import bits


def singleton_masks(marks):
    return tuple(mark & ~word_mask(other for index, other in enumerate(marks) if index != pole)
                 for pole, mark in enumerate(marks))


def word_mask(masks):
    result = 0
    for mask in masks:
        result |= mask
    return result


def row_eligible(graph, neutral, marks, row, pair_limit):
    return (independent(graph, row | (1 << neutral))
            and all((mark & row).bit_count() <= pair_limit for mark in marks))


def factored(graph, neutral, marks, row_order=3, pair_limit=2):
    groups = singleton_masks(marks)
    need_low = [max(0, group.bit_count() - 3) for group in groups]
    need_high = [max(0, group.bit_count() - 4) for group in groups]
    private = ((1 << len(graph)) - 1) ^ (1 << neutral)
    eligible = private & ~graph[neutral]
    result = {}
    for sites in combinations(bits(eligible), row_order):
        row = word(sites)
        if not row_eligible(graph, neutral, marks, row, pair_limit):
            continue
        hits = tuple((row & group).bit_count() for group in groups)
        result[row] = tuple(all(hit >= required for hit, required in zip(hits, need, strict=True))
                            for need in (need_low, need_high))
    return result


def deletion_templates(card, fixed_core, root, root_sites, alpha_limit):
    assert triangle_free(card) and not forbidden_independent(card, alpha_limit + 1)
    assert set(bits(card[root])) == set(root_sites)
    assert set(fixed_core).isdisjoint({root, *root_sites})
    assert set(fixed_core) | {root, *root_sites} == set(range(len(card)))
    return {trace(card, (*fixed_core, *keep, root))
            for order in range(len(root_sites) + 1) for keep in combinations(root_sites, order)}


def physical_restore(core, templates):
    orders = {}
    for template in sorted(templates):
        ports = len(template) - len(core) - 1
        assert ports >= 0
        assert trace(template, tuple(range(len(core)))) == core
        assert set(bits(template[-1])) == set(range(len(core), len(template) - 1))
        assert independent(template, word(range(len(core), len(template) - 1)))
        orders.setdefault(ports, []).append(edge_sets(template))

    @cache
    def restore(physical_sites, frozen_edges):
        if any(other in frozen_edges[site] for site, other in combinations(physical_sites, 2)):
            return False
        core_labels = tuple(('H', site) for site in range(len(core)))
        pole = ('pole', 0)
        singleton_labels = tuple(('W17', site) for site in physical_sites)
        labels = (*core_labels, *singleton_labels, pole)
        for template in orders.get(len(physical_sites), ()):
            restored = {label: frozenset(labels[peer] for peer in template[index])
                        for index, label in enumerate(labels)}
            if (restored[pole] == frozenset(singleton_labels)
                    and all(not restored[label].intersection(singleton_labels) for label in singleton_labels)
                    and all(restored[label].intersection(core_labels) ==
                            frozenset(core_labels[peer] for peer in bits(core[index]))
                            for index, label in enumerate(core_labels))):
                return True
        return False

    return restore


def literal(graph, neutral, marks, restores, row_order=3, pair_limit=2):
    edges = edge_sets(graph)
    mark_sets = tuple(set(bits(mark)) for mark in marks)
    private = set(range(len(graph))) - {neutral}
    groups = tuple({site for site in private if site in mark
                    and sum(site in peer for peer in mark_sets) == 1} for mark in mark_sets)
    result = {}
    for sites in combinations(sorted(private), row_order):
        if any(second in edges[first] for first, second in combinations((*sites, neutral), 2)):
            continue
        selected = set(sites)
        if any(len(mark & selected) > pair_limit for mark in mark_sets):
            continue
        residual = tuple(tuple(sorted(group - selected)) for group in groups)
        result[word(sites)] = tuple(all(restore(group, edges) for group in residual) for restore in restores)
    return result


def control():
    control35 = tuple(word((site + sign * jump) % 35 for jump in (1, 7, 11, 16) for sign in (-1, 1))
                      for site in range(35))
    assert triangle_free(control35) and not forbidden_independent(control35, 9)
    cap = max((control35[first] & control35[second]).bit_count() for first, second in combinations(range(35), 2))
    assert cap == 4
    counts = Counter()
    for first, second in combinations(range(35), 2):
        poles = control35[first] & control35[second]
        if poles.bit_count() != 4:
            continue
        counts['pairs'] += 1
        exterior = ((1 << 35) - 1) & ~(poles | word((first, second)))
        core = tuple(site for site in bits(exterior) if not (control35[site] & poles))
        assert len(core) == 13
        for pole in bits(poles):
            others = poles ^ (1 << pole)
            own_sites = tuple(site for site in bits(exterior) if control35[site] & poles == (1 << pole))
            right_sites = tuple(site for site in bits(exterior) if control35[site] & others)
            known_row = tuple(site for site in right_sites if control35[pole] >> site & 1)
            assert len(own_sites) == 2 and len(known_row) == 4
            card = trace(control35, (*core, *own_sites, pole))
            templates = deletion_templates(card, tuple(range(13)), 15, (13, 14), 5)
            residual = trace(control35, core)
            restores = (physical_restore(residual, {card for card in templates if len(card) < 16}),
                        physical_restore(residual, templates))
            for neutral in own_sites:
                sites = (*right_sites, neutral)
                graph = trace(control35, sites)
                marked = tuple(tuple(index for index, site in enumerate(sites) if control35[b] >> site & 1)
                               for b in bits(others))
                marks = tuple(word(mark) for mark in marked)
                row = word(sites.index(site) for site in known_row)
                residuals = tuple(tuple(index for index in bits(group & ~row)) for group in singleton_masks(marks))
                physical = tuple(tuple(index for index, site in enumerate(sites)
                                       if control35[site] & poles == (1 << b)) for b in bits(others))
                assert residuals == physical and all(len(group) == 2 for group in physical)
                assert row_eligible(graph, len(sites) - 1, marks, row, cap - 2)
                factored_flags = tuple(all(len(group) <= limit for group in residuals) for limit in (1, 2))
                literal_flags = tuple(all(restore(group, edge_sets(graph)) for group in physical) for restore in restores)
                assert factored_flags == literal_flags == (False, True)
                counts['planted rows'] += 1
    assert counts == {'pairs': 105, 'planted rows': 840}
    print('C35 K2,4 pairs 105; 840 planted physical rows under both (scaled) flags')

    star4 = (2, 1, 64, 64, 64, 64, 60)
    templates = deletion_templates(star4, (0, 1), 6, (2, 3, 4, 5), 5)
    restores = (physical_restore((2, 1), {card for card in templates if len(card) <= 6}),
                physical_restore((2, 1), templates))
    marks = (31, 96, 192, 128)
    count_legal = 0
    for forbidden in (0, 7, 15, 31):
        graph = tuple(256 * bool(forbidden >> site & 1) for site in range(8)) + (forbidden,)
        result = factored(graph, 8, marks)
        assert result == literal(graph, 8, marks, restores)
        if forbidden == 0:
            assert 7 not in result and result[35] == (True, True)
        assert tuple(any(flags[index] for flags in result.values()) for index in range(2)) == (
            forbidden in (0, 7), forbidden in (0, 7, 15))
        count_legal += len(result)
    print('original-size-five controls: four graphs;', count_legal, 'legal rows; both flags and cap mutation checked')


def bind_left(cat16, cat17, left_frames, frozen):
    row = next(row for index, row, key in frame_rows(left_frames) if index == 42679 and key == (66, 4))
    host, neutral, *marks = row
    root = 0
    card = cat16[host]
    own_sites = tuple(bits(card[root]))
    assert (host, neutral) == (97, 7) and len(own_sites) == 3
    assert frame_binding(card, neutral, tuple(marks), 9, 5, 4, 9)[:2] == (66, 4)
    core_sites = tuple(site for site in range(16) if site not in {root, *own_sites})
    private_parts = tuple(set(bits(mark)) - {root} for mark in marks if mark >> root & 1)
    assert tuple(map(len, private_parts)) == (4, 4, 4) and set().union(*private_parts) == set(core_sites)
    assert neutral in own_sites
    low = deletion_templates(card, core_sites, root, own_sites, 5)
    core = trace(card, core_sites)
    residual_roots = []
    qualifying = 0
    for card_host, card_root, keep, singles, residual in rooted_cards(cat17, 4):
        qualifying += 1
        mapping = next(nx.algorithms.isomorphism.GraphMatcher(nxgraph(core), nxgraph(residual)).isomorphisms_iter(), None)
        if mapping is not None:
            residual_roots.append((card_host, card_root, tuple(keep[mapping[index]] for index in range(12)), singles))
    assert qualifying == 21 and len(residual_roots) == 14
    card_host, card_root, mapped, singles = residual_roots[0]
    high = deletion_templates(cat17[card_host], mapped, card_root, singles, 5)
    reference = {tuple(map(int, part.split()[:3])) for part in frozen.read_text().splitlines()[1:]}
    assert all(first == 42679 for first, _, _ in reference) and len(reference) == 578
    print('frozen left 42679 host', host, 'x', root, 'neutral', neutral, 'N(x)', *own_sites,
          'H-parts', '/'.join(','.join(map(str, sorted(part))) for part in private_parts))
    print('frozen raw degree-four roots', len(residual_roots), '/', qualifying, 'first host/root', card_host, card_root)
    return (physical_restore(core, low), physical_restore(core, low | high)), reference


def right_roster(frames, frozen):
    handoff = {row[1]: row[8:] for row in read_integer_rows(frozen, 14)}
    count = 0
    selected = {}
    for index, row, key in frame_rows(frames):
        count += 1
        if key == (75, 5):
            marks = row[2:]
            if any(sum(mark >> site & 1 for mark in marks) == 3 for site in range(17)):
                selected[index] = row
    assert count == 59521 and len(handoff) == 116 and selected == handoff
    return selected


def target(args):
    cat16, cat17 = catalogue(args.cat16), catalogue(args.cat17)
    assert (len(cat16), len(cat17)) == (2576, 7)
    restores, old_rows = bind_left(cat16, cat17, args.left, args.old_rows)
    roster = right_roster(args.right, args.frozen)
    if args.sample:
        roster = dict(item for index, item in enumerate(roster.items()) if index % 10 == 0)
    counts = Counter()
    failures = ([], [])
    print('frame17 host neutral m0 m1 m2 m3 s0 s1 s2 s3 legal pass3 pass4 witness3 witness4', file=args.out)
    for identity, (host, neutral, *marks) in roster.items():
        graph = cat17[host]
        groups = singleton_masks(marks)
        sizes = tuple(group.bit_count() for group in groups)
        bound = frame_binding(graph, neutral, tuple(marks), 9, 5, 4, 9)
        assert bound[:2] == (75, 5) and groups == tuple(map(word, bound[2]))
        assert sorted(sizes) == [3, 3, 3, 4]
        result = factored(graph, neutral, marks)
        other = literal(graph, neutral, marks, restores)
        assert result == other, identity
        survivors = tuple(sorted(row for row, flags in result.items() if flags[index]) for index in range(2))
        for index, rows in enumerate(survivors):
            if not rows:
                failures[index].append(identity)
        counts['legal'] += len(result)
        counts['pass3'] += len(survivors[0])
        counts['pass4'] += len(survivors[1])
        frozen_here = {row for _, key, row in old_rows if key == identity}
        if frozen_here:
            assert frozen_here == set(result) == set(survivors[1])
            counts['old'] += len(frozen_here)
            counts['old3'] += len(frozen_here.intersection(survivors[0]))
        print(identity, host, neutral, *marks, *sizes, len(result), *map(len, survivors),
              *(rows[0] if rows else '-' for rows in survivors), file=args.out)
    if not args.sample:
        assert counts['old'] == 578
    print('right frames', len(roster), 'legal/pass3/pass4/old', *(counts[key] for key in ('legal', 'pass3', 'pass4', 'old')))
    print('frozen already-tested rows passing tau3', counts['old3'])
    print('tau3 failures', len(failures[0]), *failures[0])
    print('tau4 failures', len(failures[1]), *failures[1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sample', action='store_true')
    for name in ('cat16', 'cat17', 'left', 'right', 'old_rows', 'frozen'):
        parser.add_argument('--' + name.replace('_', '-'), type=Path)
    parser.add_argument('--out', type=argparse.FileType('w'))
    args = parser.parse_args()
    if args.control:
        control()
    else:
        target(args)


if __name__ == '__main__':
    main()
