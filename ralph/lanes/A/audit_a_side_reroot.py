#!/usr/bin/env python3
"""Map bounded rerooted window covers to exact round-11 A-small IDs."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from itertools import combinations, islice
from pathlib import Path
from random import Random
import sys

import pynauty

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from check_graph import alpha, parse_graph6

from audit_pinned_anchor_cnf import oracle_roles
from audit_short_anchor import vertices


def mask(items):
    return sum(1 << vertex for vertex in items)


def induce(adj, order):
    return tuple(sum(((adj[left] >> right) & 1) << index for index, right in enumerate(order))
                 for left in order)


def take(adj, order, group):
    return Counter(adj[vertex] & group for vertex in order)


def capacity(side, holes):
    return Counter({**{1 << vertex: 4 for vertex in vertices(side)},
                    **{mask(pair): 1 for pair in combinations(vertices(side), 2) if mask(pair) not in holes}})


def remnant(full, seen):
    return None if seen - full else full - seen


def cross_edge(adj, left, right):
    edge, = ((first, second) for first in vertices(left) for second in vertices(adj[first] & right))
    return edge


def holes_on_b(active, crossing, pivot, degree, occupied):
    for pair, peer in combinations(map(mask, combinations(vertices(active | 1 << pivot), 2)), 2):
        if pair in occupied or peer in occupied:
            continue
        touches = (pair | peer) >> pivot & 1
        if touches != (degree == 8) or pair & peer == 1 << pivot:
            continue
        if not (pair | peer) >> crossing & 1:
            continue
        if pair & peer not in (0, 1 << crossing):
            continue
        yield 'middle' if pair & peer else 'matching', (pair, peer)


def role_form(adj, arm_a, arm_b, pivot_b, degree, holes):
    cross_a, cross_b = cross_edge(adj, arm_a, arm_b)
    links = {idx: list(vertices(row)) for idx, row in enumerate(adj)}
    colors = [{cross_a}, set(vertices(arm_a)) - {cross_a}, {cross_b},
              set(vertices(arm_b)) - {cross_b}, set(range(len(adj))) - set(vertices(arm_a | arm_b))]
    marks = [set(), set()]
    for index, hole in enumerate(holes, len(adj)):
        endpoints = list(vertices(hole & arm_b))
        links[index] = endpoints
        for endpoint in endpoints:
            links[endpoint].append(index)
        marks[(hole >> pivot_b) & 1].add(index)
    assert len(marks[0]) + len(marks[1]) == 2 and len(marks[1]) == (degree == 8)
    colors.extend(group for group in marks if group)
    return pynauty.Graph(len(adj) + 2, adjacency_dict=links, vertex_coloring=colors)


def permutation(source, target):
    first = pynauty.canon_label(source)
    second = pynauty.canon_label(target)
    by_source = dict(zip(first, second, strict=True))
    assert len(by_source) == len(first) and len(set(by_source.values())) == len(first)
    for vertex, adjacent in source.adjacency_dict.items():
        assert {by_source[peer] for peer in adjacent} == set(target.adjacency_dict[by_source[vertex]])
    for source_color, target_color in zip(source.vertex_coloring, target.vertex_coloring, strict=True):
        assert {by_source[vertex] for vertex in source_color} == target_color
    return [by_source[vertex] for vertex in range(len(first))]


def cases(degree):
    old_overlap = degree - 7
    for epsilon, triple in [(0, 0), (1, 0), (1, 1)]:
        new_overlap = degree - 2 - old_overlap + triple
        new_n = 38 - (8 + epsilon) - degree + new_overlap
        assert new_n == 28 - epsilon - old_overlap + triple
        yield ('leaf' if epsilon == 0 else 'full', triple, new_overlap, new_n)


def original_index(path):
    index = {8: defaultdict(list), 9: defaultdict(list)}
    all_ids = set()
    for line in path.read_text().splitlines():
        row, first, second, encoded = line.split()
        arm_a, arm_b = int(first), int(second)
        adj = tuple(parse_graph6(encoded))
        for degree in index:
            for orientation, _, _, _, _, shape, hole, peer in oracle_roles(adj, arm_a, arm_b, degree):
                if orientation:
                    continue
                original = '_'.join(map(str, (row, first, second, degree, orientation, shape, *hole, *peer)))
                assert original not in all_ids
                all_ids.add(original)
                form = role_form(adj, arm_a, arm_b, 27, degree, tuple(map(mask, (hole, peer))))
                index[degree][pynauty.certificate(form)].append((original, form))
    return index


def margins(remainder_a, remainder_b, old_overlap, new_overlap, triple, pivot_a, pivot_s, pivot_b):
    counts_a = Counter()
    for signature, count in remainder_a.items():
        counts_a[(signature >> pivot_a & 1, signature >> pivot_s & 1)] += count
    required_b = {(1, 1): triple, (1, 0): old_overlap - triple,
                  (0, 1): new_overlap - triple, (0, 0): 1}
    size_b = sum(count for signature, count in remainder_b.items() if signature >> pivot_b & 1)
    return (sum(remainder_a.values()) == sum(remainder_b.values()) and
            size_b == sum(required_b.values()) and
            all(0 <= needed <= counts_a[status] for status, needed in required_b.items()) and
            all(counts_a[(status, 0)] == required_b[(status, 0)] for status in (0, 1)))


def audit_windows(path, index, output, order, minimum, limit=None):
    stats = Counter()
    surviving = defaultdict(set)
    reroot_keys = set()
    admissible = [(degree, tag, triple, new_overlap) for degree in (8, 9)
                  for tag, triple, new_overlap, new_n in cases(degree) if new_n == order]
    spare_s, spare_b = order, order + 1
    universe = (1 << order) - 1
    equality_deg = order - 22
    for row in islice(path.read_text().splitlines(), limit):
        number, first, second, encoded = row.split()
        adj = parse_graph6(encoded)
        assert len(adj) == order
        if minimum is not None:
            assert min(row.bit_count() for row in adj) == minimum
        for arm_a, arm_b in [(int(first), int(second)), (int(second), int(first))]:
            stats['orientations'] += 1
            cross_a, cross_b = cross_edge(adj, arm_a, arm_b)
            exteriors = tuple(vertices(universe ^ arm_a ^ arm_b))
            seen_a, seen_b = take(adj, exteriors, arm_a), take(adj, exteriors, arm_b)
            for centre in vertices(arm_a ^ (1 << cross_a)):
                if adj[centre].bit_count() != equality_deg:
                    continue
                stats['equality_degree'] += 1
                all_core = tuple(vertices(universe & ~(adj[centre] | 1 << centre)))
                assert len(all_core) == 21
                small = mask(index for index, vertex in enumerate(all_core) if arm_a >> vertex & 1)
                large = mask(index for index, vertex in enumerate(all_core) if arm_b >> vertex & 1)
                assert (small.bit_count(), large.bit_count()) == (3, 4)
                core_exterior = set(exteriors) - set(vertices(adj[centre]))
                missing = remnant(capacity(arm_a ^ (1 << centre), ()),
                                   take(adj, core_exterior, arm_a ^ (1 << centre)))
                if missing != {1 << cross_a: 1}:
                    continue
                stats['singleton-core'] += 1
                core_adj = induce(adj, all_core)
                for degree, tag, triple, new_overlap in admissible:
                    for leaf in ((spare_s,) if tag == 'leaf' else tuple(vertices(arm_a & ~(1 << cross_a | 1 << centre)))):
                        shell_a = (mask((centre, cross_a)), mask((centre, leaf)))
                        remain_a = remnant(capacity(arm_a | 1 << spare_s, shell_a), seen_a)
                        if remain_a is None:
                            continue
                        stats[(degree, tag, 'A-holes')] += 1
                        for shape, holes in holes_on_b(arm_b, cross_b, spare_b, degree, seen_b):
                            remain_b = remnant(capacity(arm_b | 1 << spare_b, holes), seen_b)
                            assert remain_b is not None
                            if not margins(remain_a, remain_b, degree - 7, new_overlap, triple,
                                           centre, spare_s, spare_b):
                                continue
                            stats[(degree, tag, shape, 'margins')] += 1
                            core_holes = tuple(mask(all_core.index(vertex) if vertex != spare_b else 27
                                                    for vertex in vertices(hole)) for hole in holes)
                            form = role_form(core_adj, small, large, 27, degree, core_holes)
                            sources = index[degree].get(pynauty.certificate(form), ())
                            assert sources, (number, arm_a, arm_b, centre, leaf, holes)
                            key = (degree, number, arm_a, arm_b, centre, leaf, shape, *holes)
                            assert key not in reroot_keys
                            reroot_keys.add(key)
                            for original, old_form in sources:
                                old_to_core = permutation(old_form, form)[:21]
                                old_to_window = ','.join(str(all_core[value]) for value in old_to_core)
                                assert len(set(old_to_core)) == 21
                                surviving[degree, tag].add(original)
                                print(original, tag, triple, *key, old_to_window, file=output, sep='\t')
                                stats[(degree, tag, shape, 'links')] += 1
    for degree, tag, _, _ in admissible:
        print('projected IDs', order, minimum, degree, tag, len(surviving[degree, tag]))
    print('window union', order, minimum, len(set().union(*surviving.values())), 'rooted signatures', len(reroot_keys))
    for key, value in sorted(stats.items(), key=str):
        print(key, value)
    return surviving


def controls():
    table = {8: [('leaf', 0, 5, 27), ('full', 0, 5, 26), ('full', 1, 6, 27)],
             9: [('leaf', 0, 5, 26), ('full', 0, 5, 25), ('full', 1, 6, 26)]}
    assert all(list(cases(degree)) == row for degree, row in table.items())
    rng = Random(31410)
    for order, dist, expected_alpha in [(13, (1, 5), 4), (13, (1,), 6)]:
        adj = tuple(mask({(vertex + hop) % order for hop in (*dist, *(-offset for offset in dist))})
                    for vertex in range(order))
        assert all(not adj[vertex] & adj[peer] for vertex in range(order) for peer in vertices(adj[vertex]))
        assert alpha(adj) == expected_alpha
        by_min = Counter()
        for centre, swapped, pivot in combinations(range(order), 3):
            if (adj[centre] >> swapped & 1 or adj[centre] >> pivot & 1 or adj[swapped] >> pivot & 1):
                continue
            start = ((1 << order) - 1) & ~(adj[centre] | adj[pivot] | mask((centre, pivot)))
            reroot = ((1 << order) - 1) & ~(adj[swapped] | adj[pivot] | mask((swapped, pivot)))
            same = start & ~(adj[swapped] | 1 << swapped)
            assert same == reroot & ~(adj[centre] | 1 << centre)
            first_deg = (start & adj[swapped]).bit_count()
            next_deg = (reroot & adj[centre]).bit_count()
            assert start.bit_count() - first_deg == reroot.bit_count() - next_deg == same.bit_count() + 1
            next_min = min((adj[vertex] & reroot).bit_count() for vertex in vertices(reroot))
            by_min[next_deg == next_min] += 1
            if next_deg > next_min and by_min[False] == 1:
                relabel = list(range(order))
                rng.shuffle(relabel)
                again = induce(adj, relabel)
                re_ids = [relabel.index(label) for label in (centre, swapped, pivot)]
                induced = ((1 << order) - 1) & ~(again[re_ids[1]] | again[re_ids[2]] | mask(re_ids[1:]))
                assert mask(relabel[v] for v in vertices(induced)) == reroot
                assert (again[re_ids[0]] & induced).bit_count() == next_deg
                assert not next_deg == next_min
                print('relabelled nonminimum', order, dist, centre, swapped, pivot, next_deg, next_min,
                      relabel)
        print('independent-triple controls', order, dist, 'minimum/nonminimum', by_min[True], by_min[False])
    relabel = (12, 9, 2, 4, 7, 10, 0, 11, 5, 1, 8, 6, 3)
    cycle = tuple(mask(((vertex + 1) % 13, (vertex - 1) % 13)) for vertex in range(13))
    centre, swapped, pivot = (relabel.index(value) for value in (0, 2, 6))
    anchor_a = mask(relabel.index(value) for value in (4, 9))
    anchor_b = mask(relabel.index(value) for value in (8, 11))
    known_core = mask(relabel.index(value) for value in (4, 8, 9, 10, 11))
    for mutation in (False, True):
        planted = list(cycle)
        if mutation:
            planted[4] |= 1 << 12
            planted[12] |= 1 << 4
        planted = induce(planted, relabel)
        assert alpha(planted) == 6
        assert all(not planted[vertex] & planted[peer] for vertex in range(13) for peer in vertices(planted[vertex]))
        universe = (1 << 13) - 1
        old = universe & ~(planted[centre] | planted[pivot] | mask((centre, pivot)))
        new = universe & ~(planted[swapped] | planted[pivot] | mask((swapped, pivot)))
        assert known_core == old & ~(planted[swapped] | 1 << swapped)
        assert known_core == new & ~(planted[centre] | 1 << centre)
        assert cross_edge(planted, anchor_a, anchor_b) == (relabel.index(9), relabel.index(8))
        for short, long in ((anchor_a, anchor_b), (anchor_b, anchor_a)):
            assert not any(planted[vertex] & short for vertex in vertices(short))
            assert cross_edge(planted, short, long) == (relabel.index(9 if short == anchor_a else 8),
                                                        relabel.index(8 if long == anchor_b else 9))
            assert all(planted[vertex] & short for vertex in vertices(known_core & ~(short | long)))
        minimum = min((planted[vertex] & new).bit_count() for vertex in vertices(new))
        assert (planted[centre] & new).bit_count() == new.bit_count() - known_core.bit_count() - 1 == 1
        assert minimum == int(mutation)
    print('planted C13 2+2 marked relabel, both orientations: touching 4--12 changes minimum 0→1, '
          'keeps equality 1, both projected marks and alpha 6', flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path, nargs='?')
    parser.add_argument('windows', type=Path, nargs='?')
    parser.add_argument('output', type=Path, nargs='?')
    parser.add_argument('--limit-marks', type=int)
    parser.add_argument('--order', type=int, choices=(25, 26, 27), default=27)
    parser.add_argument('--minimum', type=int)
    args = parser.parse_args()
    controls()
    if args.original is None:
        return
    index = original_index(args.original)
    for degree, items in sorted(index.items()):
        print('original A-small', degree, sum(map(len, items.values())), 'colored roles', len(items))
    with args.output.open('w') as output:
        surviving = audit_windows(args.windows, index, output, args.order, args.minimum, args.limit_marks)
    for (degree, tag), ids in sorted(surviving.items()):
        args.output.with_name(f'{args.output.name}.d{degree}.{tag}').write_text(''.join(key + '\n' for key in sorted(ids)))
    for degree in sorted({degree for degree, _ in surviving}):
        remaining = {key for group in index[degree].values() for key, _ in group}
        remaining.difference_update(set.union(*(ids for (value, _), ids in surviving.items() if value == degree)))
        args.output.with_name(f'{args.output.name}.d{degree}.no-window').write_text(
            ''.join(key + '\n' for key in sorted(remaining)))


if __name__ == '__main__':
    main()
