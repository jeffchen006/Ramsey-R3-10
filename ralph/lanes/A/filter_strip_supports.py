#!/usr/bin/env python3
"""Exact support-only e168 filter for a marked paired path/leaf c=3 window."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path

from audit_floor_covers import require
from audit_path_leaf import vertices
from residue_bundle import parse_graph6, triangle_free


def coverage(left, right, width):
    return sum(right << (width * anchor) for anchor in vertices(left))


def pairs_cover(supports, width):
    cover = 0
    for left, right in supports:
        if left & right & 1:
            return None
        cover |= coverage(left, right, width)
    return cover


@lru_cache(maxsize=None)
def ordered_types(occurrences):
    return sorted(set(permutations(occurrences)))


def assignments(known, gaps, central, shared, width):
    wanted = ((1 << (width * width)) - 1) ^ 1
    observed = pairs_cover(known, width)
    if observed is None:
        return
    left_gap, right_gap = gaps
    require(len(left_gap) + shared == len(central[1]) and len(right_gap) + shared == len(central[0]),
            'bad centre cardinalities')
    left_prefix = len(right_gap)
    right_prefix = len(left_gap)
    left_ways = []
    for order in ordered_types(tuple(sorted(central[0]))):
        exclusive = tuple(zip(order[:left_prefix], right_gap, strict=True))
        cover = pairs_cover(exclusive, width)
        if cover is not None:
            left_ways.append((order[left_prefix:], exclusive, cover))
    right_ways = []
    for order in ordered_types(tuple(sorted(central[1]))):
        exclusive = tuple(zip(left_gap, order[:right_prefix], strict=True))
        cover = pairs_cover(exclusive, width)
        if cover is not None:
            right_ways.append((order[right_prefix:], exclusive, cover))
    centre = width - 1
    central_bit = 1 << centre
    peripheral_cross = ((1 << centre) - 1) | sum(1 << (width * index) for index in range(centre))
    for (left_common, left_exclusive, left_cover), (right_common, right_exclusive, right_cover) in product(left_ways, right_ways):
        seen = observed | left_cover | right_cover
        if wanted & peripheral_cross & ~seen:
            continue
        common = tuple(zip(left_common, right_common, strict=True))
        require(all(left & central_bit and right & central_bit for left, right in common), 'not common to both centres')
        common_cover = pairs_cover(common, width)
        if common_cover is not None and (seen | common_cover) == wanted:
            yield left_exclusive, right_exclusive, common


def matching(supports):
    matched = {}

    def augment(row, seen):
        for anchor in vertices(supports[row]):
            if anchor in seen:
                continue
            seen.add(anchor)
            if anchor not in matched or augment(matched[anchor], seen):
                matched[anchor] = row
                return True
        return False

    return all(augment(row, set()) for row in range(len(supports)))


def hall(nonedge, supports, width, stats):
    whole = (1 << (2 * width)) - 1
    boundaries = (whole ^ 1, whole ^ (1 << width))
    for anchor in range(2 * width):
        star = [support for support in supports if support >> anchor & 1]
        if any(not matching([support & boundary for support in star]) for boundary in boundaries):
            return False
    stats['column_hall'] += 1

    def check(clique, active, used):
        if not (active | used):
            return all(matching([supports[vertex] & boundary for vertex in clique]) for boundary in boundaries)
        pivot = max(vertices(active | used), key=lambda vertex: (active & nonedge[vertex]).bit_count())
        for vertex in vertices(active & ~nonedge[pivot]):
            if not check((*clique, vertex), active & nonedge[vertex], used & nonedge[vertex]):
                return False
            active ^= 1 << vertex
            used |= 1 << vertex
        return True

    return check((), (1 << len(supports)) - 1, 0)


def gap_list(roles, private, known):
    wanted = Counter([1 << anchor for anchor in range(roles) for _ in range(private)])
    wanted.update((1 << first) | (1 << second) for first, second in combinations(range(roles), 2))
    got = Counter(known)
    require(not got - wanted, 'window signature margins exceeded')
    return sorted((wanted - got).elements())


def bounded_degrees(supports, possible, graph_degrees, required, known_count, target_deficit, profile):
    attainable = {(0, 0, 0)}
    for index, mask in enumerate(supports):
        ceilings = graph_degrees[index] + possible[index].bit_count()
        absent_edges_deficit = index >= known_count
        choices = [degree for degree in (7, 8, 9)
                   if graph_degrees[index] + required[index] <= degree <= ceilings
                   and (degree != 7 or mask.bit_count() == 2)]
        attainable = {(sevens + (degree == 7), eights + (degree == 8), deficit + (9 - degree) * absent_edges_deficit)
                      for sevens, eights, deficit in attainable for degree in choices
                      if sevens + (degree == 7) <= profile[0] and eights + (degree == 8) <= profile[1]
                      and deficit + (9 - degree) * absent_edges_deficit <= target_deficit}
        if not attainable:
            return set()
    return {deficit for sevens, eights, deficit in attainable if (sevens, eights) == profile}


def inspect(graph, left, right, stats):
    require(len(graph) == 27 and triangle_free(graph), 'bad paired source graph')
    left, right = tuple(vertices(left)), tuple(vertices(right))
    require(len(left) == len(right) == 4 and not set(left) & set(right), 'bad column sets')
    cross, = [(first, second) for first in left for second in right if graph[first] >> second & 1]
    left = (cross[0], *(vertex for vertex in left if vertex != cross[0]))
    right = (cross[1], *(vertex for vertex in right if vertex != cross[1]))
    require(not any(graph[first] >> second & 1 for side in (left, right) for first, second in combinations(side, 2)),
            'nonindependent strip')
    exterior = tuple(sorted(set(range(27)) - set(left) - set(right)))
    known = tuple(tuple(sum(1 << index for index, anchor in enumerate(side) if graph[vertex] >> anchor & 1)
                        for side in (left, right)) for vertex in exterior)
    gaps = tuple(gap_list(4, 4, [support[side] for support in known]) for side in (0, 1))
    require(all(len(part) == 3 for part in gaps), 'not exactly three surviving signature gaps')
    core_edges = sum(mask.bit_count() for mask in graph) // 2
    target_deficit = core_edges - 76
    if not 0 <= target_deficit <= 21:
        return set()
    forced_gaps = tuple(part[0] | part[1] | part[2] for part in gaps)
    degrees = [graph[vertex].bit_count() for vertex in exterior]
    known_neighbors = [sum(1 << index for index, other in enumerate(exterior) if graph[vertex] >> other & 1)
                       for vertex in exterior]
    accepted = set()
    for left_leaf, right_leaf in product(range(1, 4), repeat=2):
        if not (forced_gaps[0] >> left_leaf & 1 and forced_gaps[1] >> right_leaf & 1):
            continue
        central = tuple((16, 16, 16, 16, *(16 | (1 << index) for index in range(1, 4) if index != leaf))
                        for leaf in (left_leaf, right_leaf))
        for left_removed, right_removed, common in assignments(known, gaps, central, 3, 5):
            stats['cross'] += 1
            supports = tuple(left_support | (right_support << 5)
                             for left_support, right_support in (*known, *left_removed, *right_removed, *common))
            count = len(supports)
            allowed = [sum(1 << other for other in range(count) if not supports[vertex] & supports[other]
                           and ((vertex < 19) != (other < 19) or (vertex < 19 and known_neighbors[vertex] >> other & 1)
                                or (19 <= vertex < 22 and 22 <= other < 25) or (19 <= other < 22 and 22 <= vertex < 25)))
                       for vertex in range(count)]
            stars = [sum(1 << index for index, support in enumerate(supports) if support >> bit & 1)
                     for bit in range(10)]
            first_centre, second_centre = stars[4], stars[9]
            if any(not allowed[index] & first_centre or not allowed[index] & second_centre for index in range(19)):
                continue
            stats['both_centres'] += 1
            if any(not (stars[anchor] >> index & 1 or allowed[index] & stars[anchor]
                        or (anchor in (0, 5) and stars[5 - anchor] >> index & 1))
                   for index in range(count) for anchor in range(10)):
                continue
            stats['all_columns'] += 1
            cap_lr = sum((allowed[index] & (7 << 22)).bit_count() for index in range(19, 22))
            strip_degrees = [*degrees, *(support.bit_count() for support in supports[19:])]
            full = (1 << count) - 1
            ext_possible = [mask & ~((1 << 19) - 1) if index < 19 else mask for index, mask in enumerate(allowed)]
            lower = [1 if possible & first_centre & second_centre else 2 for possible in allowed[:19]] + [0] * 9
            profiles = {(6, 0), (5, 2)} - accepted
            potential = {profile for profile in profiles if any(
                0 <= target_deficit - deficit <= cap_lr for deficit in bounded_degrees(
                    supports, ext_possible, strip_degrees, lower, 19, target_deficit, profile))}
            if not potential:
                continue
            stats['degree'] += 1
            nonedge = [full & ~((1 << index) | mask) for index, mask in enumerate(allowed)]
            if hall(nonedge, supports, 5, stats):
                stats['full_hall'] += 1
                accepted.update(potential)
                if len(accepted) == 2:
                    return accepted
    return accepted


def controls():
    cycle = [sum(1 << ((vertex + offset) % 7) for offset in (-1, 1)) for vertex in range(7)]
    require(triangle_free(cycle), 'bad cycle')
    for first in range(7):
        for direction in (-1, 1):
            ordered = [(first + direction * index) % 7 for index in range(7)]
            sides = ((ordered[0], ordered[3]), (ordered[1], ordered[5]))
            external = ordered[2], ordered[6], ordered[4]
            actual = tuple(tuple(sum(1 << bit for bit, anchor in enumerate(side) if cycle[vertex] >> anchor & 1)
                                 for side in sides) for vertex in external)
            found = list(assignments((), ([1], [1]), ((2, 2), (2, 2)), 1, 2))
            require(found == [tuple((pair,) for pair in actual)], 'did not uniquely reconstruct C7 supports')
            supports = tuple(left | right << 2 for left, right in actual)
            nonedge = [sum(1 << index for index, other in enumerate(external) if vertex != other and not cycle[vertex] >> other & 1)
                       for vertex in external]
            require(hall(nonedge, supports, 2, Counter()), 'Hall rejected actual C7')
    require(not list(assignments((), ([2], [1]), ((2, 2), (2, 2)), 1, 2)), 'accepted missing cross coverage control')
    require(not hall([2, 1], (9, 9), 2, Counter()), 'accepted deficient Hall control')
    print('14 C7 placements uniquely reconstructed; deleted required contact and duplicate Hall signature rejected')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path, nargs='?')
    parser.add_argument('--sample', type=int)
    args = parser.parse_args()
    controls()
    if not args.keys:
        return
    rows = args.keys.read_text().splitlines()
    if args.sample:
        rows = [rows[index * len(rows) // args.sample] for index in range(args.sample)]
    stats = Counter()
    outputs = Counter()
    for line in rows:
        index, left, right, raw = line.split()
        accepted = inspect(parse_graph6(raw), int(left), int(right), stats)
        for profile in sorted(accepted):
            outputs[profile] += 1
            print(index, left, right, *profile, flush=True)
    print('rows', len(rows), 'surviving marks by outside degree-seven/eight profile', sorted(outputs.items()),
          'examined stages (not orbits)', sorted(stats.items()))


if __name__ == '__main__':
    main()
