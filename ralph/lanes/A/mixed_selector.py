#!/usr/bin/env python3
"""Independent mixed-strip reroot selector; no solver or proof dependencies."""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, permutations
import argparse
import json
from pathlib import Path

from audit_path_leaf import vertices
from audit_strip_extensions import independent, mark, validate_graph
from residue_bundle import parse_graph6, triangle_free


def bitset(items):
    return sum(1 << item for item in items)


def pairs(side):
    return tuple(bitset(pair) for pair in combinations(side, 2))


def signatures(side, holes):
    return Counter({1 << anchor: 4 for anchor in side}) + Counter(set(pairs(side)) - set(holes))


def shapes(side, star):
    for holes in combinations(pairs(side), 2):
        intersection = holes[0] & holes[1]
        if not intersection and (holes[0] | holes[1]) >> star & 1:
            yield 'matching', holes
        if intersection == 1 << star:
            yield 'middle', holes


def remaining_floor(degree, common, terminal=True):
    order = 31 - degree + common
    if common < 1 or order > 27:
        return None
    if terminal:
        if order == 27:
            return None
        if degree == 8 and common == 3:
            return 4
    return max(0, order - 23)


def support_choices(wanted, number):
    options = sorted(wanted)
    for choice in combinations_with_replacement(options, number):
        if all(count <= wanted[support] for support, count in Counter(choice).items()):
            yield choice


def b_profile(side, star, holes, inside, terminal=True):
    cross_bit = 1 << star
    inside_types = set(inside)
    common = {vertex: sum(support >> vertex & 1 for support in inside) for vertex in side}
    hole_counts = {vertex: sum(hole >> vertex & 1 for hole in holes) for vertex in side}
    rows = {}
    for pivot in side:
        if pivot == star:
            continue
        degree = 9 - hole_counts[pivot]
        required = remaining_floor(degree, common[pivot], terminal)
        if required is None:
            return None
        columns = {}
        for anchor in side:
            if anchor == pivot:
                continue
            double = (1 << pivot) | (1 << anchor)
            columns[anchor] = (8 + (1 << anchor == cross_bit) - hole_counts[anchor]
                               - (double not in holes) - common[anchor] + (double in inside_types))
        if min(columns.values()) < required or max(columns.values()) > 7:
            return None
        rows[pivot] = (degree, common[pivot], required, columns)
    return rows


def a_profile(active, star, outside, b_rows):
    for pivot, (_, _, floor, _) in b_rows.items():
        for anchor in active:
            retained = 7 + (anchor == star)
            lost = sum((a_mask >> anchor & 1) and (b_mask >> pivot & 1) for a_mask, b_mask in outside)
            if not floor <= retained - lost <= 7:
                return False
    return True


@dataclass(frozen=True)
class Window:
    source: str
    masks: tuple
    line: str
    adj: tuple
    active: tuple
    stars: tuple
    seen: tuple
    outside: tuple

    @property
    def order(self):
        return len(self.adj)

    @property
    def pivots(self):
        return self.order + 2, self.order + 3

    @property
    def sides(self):
        return tuple((*side, pivot) for side, pivot in zip(self.active, self.pivots, strict=True))

    @classmethod
    def parse(cls, row, reverse=False):
        source, first, second, line = row.split()
        masks = (int(second), int(first)) if reverse else (int(first), int(second))
        adj = validate_graph(line)
        active, stars, counts = mark(adj, *masks)
        seen = tuple(Counter({bitset(support): count for support, count in counter.items()}) for counter in counts)
        outside = tuple((adj[vertex] & masks[0], adj[vertex] & masks[1])
                        for vertex in range(len(adj)) if not (masks[0] | masks[1]) >> vertex & 1)
        return cls(source, masks, line, adj, active, stars, seen, outside)


def role_id(window, degree, shape, holes):
    pivot = 1 << window.pivots[1]
    if degree == 8:
        retained, = (hole for hole in holes if not hole & pivot)
        incident, = (hole ^ pivot for hole in holes if hole & pivot)
        identifiers = (*vertices(retained), *vertices(incident))
    else:
        identifiers = tuple(anchor for pair in sorted(tuple(vertices(hole)) for hole in holes) for anchor in pair)
        shape = 'full-' + shape
    return ' '.join(map(str, (window.source, *window.masks, shape, *identifiers, window.line)))


def roles(window, degree):
    for shape, holes in shapes(window.sides[1], window.stars[1]):
        pivot = window.pivots[1]
        if 9 - sum(hole >> pivot & 1 for hole in holes) != degree:
            continue
        if not any(window.seen[1][hole] for hole in holes):
            yield shape, holes


def project(window, degree, holes, *, joint, terminal):
    """First exact anchor witness, or None after all support placements fail."""
    if any(window.seen[1][hole] for hole in holes):
        return None
    first_pivot, pivot = window.pivots
    pivot_bit = 1 << pivot
    shared_count = window.order - 31 + degree
    floor = remaining_floor(degree, shared_count, terminal=terminal)
    if floor is None or min(ns.bit_count() for ns in window.adj) < floor:
        return None
    a_base = signatures(window.active[0], ())
    b_base = signatures(window.active[1], holes)
    if window.seen[0] - a_base or window.seen[1] - b_base:
        return None
    a_only = tuple(sorted((b_base - window.seen[1]).elements()))
    b_only = tuple(sorted((a_base - window.seen[0]).elements()))
    assert (len(a_only), len(b_only)) == (6-shared_count, degree-1-shared_count)
    star_a, star_b = (1 << vertex for vertex in window.stars)
    doubles = tuple(support for support in pairs(window.sides[1]) if support & pivot_bit and support not in holes)
    for shared_double_count in range(max(0, shared_count-4), min(len(doubles), shared_count)+1):
        for selected in combinations(doubles, shared_double_count):
            common = (*selected, *((pivot_bit,) * (shared_count-shared_double_count)))
            inside = (*common, *a_only)
            if joint:
                rows = b_profile(window.sides[1], window.stars[1], holes, inside, terminal=terminal)
                if rows is None:
                    continue
            add = tuple(support for support in doubles if support not in selected)
            assert 0 <= len(b_only) - len(add) <= 4
            for positions in permutations(range(len(b_only)), len(add)):
                if any(support & star_b and b_only[position] & star_a
                       for position, support in zip(positions, add, strict=True)):
                    continue
                extra = dict(zip(positions, add, strict=True))
                b_only_aligned = tuple((support, extra.get(index, pivot_bit)) for index, support in enumerate(b_only))
                if joint and not a_profile(window.active[0], window.stars[0], (*window.outside, *b_only_aligned), rows):
                    continue
                leaf = next(anchor for anchor in window.active[0] if anchor != window.stars[0])
                first_bit = 1 << first_pivot
                a_doubles = tuple(first_bit | 1 << anchor for anchor in window.active[0]
                                  if anchor not in (leaf, window.stars[0]))
                a_inside = (*a_doubles, *((first_bit,) * 4))
                return (*zip(a_inside, inside, strict=True), *b_only_aligned)
    return None


def window_degrees(adj, first, second):
    removed = adj[first] | adj[second] | (1 << first) | (1 << second)
    keep = bitset(range(len(adj))) & ~removed
    return {vertex: (adj[vertex] & keep).bit_count() for vertex in vertices(keep)}


def validate_witness(window, degree, holes, cut, *, joint, terminal):
    adj = list(window.adj) + [0] * (40 - window.order)

    def edge(first, second):
        adj[first] |= 1 << second
        adj[second] |= 1 << first

    roots = (window.order, window.order + 1)
    edge(*roots)
    for root, side in zip(roots, window.sides, strict=True):
        for anchor in side:
            edge(root, anchor)
    for vertex, (mask_a, mask_b) in enumerate(cut, window.order + 4):
        for anchor in vertices(mask_a | mask_b):
            edge(vertex, anchor)
    assert triangle_free(adj)
    first, pivot = window.pivots
    assert adj[first].bit_count() == 7 and adj[pivot].bit_count() == degree
    assert set(window_degrees(adj, first, pivot)) == set(range(window.order))
    assert tuple(ns & bitset(range(window.order)) for ns in adj[:window.order]) == window.adj
    exterior = bitset(range(40)) & ~bitset((*roots, *window.sides[0], *window.sides[1]))
    a_holes = tuple(hole for hole in pairs(window.sides[0]) if not any(adj[x] & hole == hole for x in vertices(exterior)))
    for side, absent in zip(window.sides, (a_holes, holes), strict=True):
        assert Counter(adj[x] & bitset(side) for x in vertices(exterior)) == signatures(side, absent)
    assert len(a_holes) == 2 and all(hole >> first & 1 for hole in a_holes)
    assert any(hole >> window.stars[0] & 1 for hole in a_holes)
    if joint:
        inside = tuple(adj[x] & bitset(window.sides[1]) for x in vertices(adj[first] & exterior))
        rows = b_profile(window.sides[1], window.stars[1], holes, inside, terminal=terminal)
        assert rows is not None
        for other in window.sides[1]:
            if other == window.stars[1]:
                continue
            expected_degree, expected_common, floor, columns = rows[other]
            assert expected_degree == adj[other].bit_count()
            assert expected_common == (adj[first] & adj[other]).bit_count()
            observed = window_degrees(adj, first, other)
            assert len(observed) == 31 - expected_degree + expected_common
            assert all(observed[anchor] == deg for anchor, deg in columns.items())
            assert all(floor <= observed[anchor] <= 7 for anchor in (*window.active[0], *columns))
    return adj


def small_control(path):
    adj = tuple(parse_graph6(Path(path).read_text().splitlines()[0]))
    assert len(adj) == 13 and triangle_free(adj)
    assert next(independent(adj, 4), None) is not None and next(independent(adj, 5), None) is None
    total = 0
    for first, second in combinations(range(len(adj)), 2):
        if adj[first] >> second & 1:
            continue
        degrees = window_degrees(adj, first, second)
        removed = adj[first] | adj[second] | (1 << first) | (1 << second)
        for retained, degree in degrees.items():
            assert degree == adj[retained].bit_count() - (adj[retained] & removed).bit_count()
            assert degree <= 2
        assert next(independent(adj, 3, bitset(degrees)), None) is None
        total += 1
    print('C13 R(3,5) control', total, 'windows', flush=True)


def direct_control(path):
    """Enumerate all B placements on a J and an S record, testing actual anchor degrees."""
    checked = set()
    for line in path.read_text().splitlines():
        status, row = line.split('\t')
        if status not in {'J', 'S'} - checked:
            continue
        source, first, second, shape, *_, encoded = row.split()
        if shape != 'matching':
            continue
        window = Window.parse(' '.join((source, first, second, encoded)))
        _, holes = next((name, holes) for name, holes in roles(window, 8)
                        if role_id(window, 8, name, holes) == row)
        cut = project(window, 8, holes, joint=False, terminal=True)
        assert cut and window.order == 26
        base = validate_witness(window, 8, holes, cut, joint=False, terminal=True)
        first_pivot, second_pivot = window.pivots
        cut_labels = tuple(vertices(base[second_pivot] & ~bitset((window.order+1,))))
        assert len(cut_labels) == 7
        all_exterior = bitset(range(40)) & ~bitset((window.order, window.order+1, *window.sides[0], *window.sides[1]))
        b_mask = bitset(window.active[1])
        doubles = tuple((base[vertex] & b_mask) for vertex in cut_labels if base[vertex] & b_mask)
        assert len(doubles) == len(set(doubles)) == 3
        cleared = list(base)
        for vertex in cut_labels:
            for anchor in window.active[1]:
                cleared[anchor] &= ~(1 << vertex)
            cleared[vertex] &= ~b_mask
        geometry = simultaneous = 0
        for assigned in permutations(cut_labels, 3):
            adj = list(cleared)
            for vertex, support in zip(assigned, doubles, strict=True):
                anchor, = vertices(support)
                adj[anchor] |= 1 << vertex
                adj[vertex] |= support
            if not triangle_free(adj):
                continue
            geometry += 1
            required = []
            for other in window.sides[1]:
                if other == window.stars[1]:
                    continue
                degree = adj[other].bit_count()
                common = (adj[first_pivot] & adj[other] & all_exterior).bit_count()
                floor = remaining_floor(degree, common)
                degrees = window_degrees(adj, first_pivot, other)
                anchors = (*window.active[0], *(anchor for anchor in window.sides[1] if anchor != other))
                required.append(floor is not None and all(floor <= degrees[anchor] <= 7 for anchor in anchors))
            simultaneous += all(required)
        assert geometry and bool(simultaneous) == (status == 'J')
        print('direct', status, row.split()[:-1], 'triangle-free', geometry, 'joint', simultaneous)
        checked.add(status)
    assert checked == {'J', 'S'}


def table():
    for degree in (8, 9):
        for common in range(1, 28 - (31-degree)):
            order = 31-degree+common
            a_sum_cap = 30-degree+common
            b_sum_cap = (21 if degree == 8 else 19)+common
            emax = (a_sum_cap+b_sum_cap+7*(order-8))//2
            floor = remaining_floor(degree, common)
            print('table', degree, common, order, floor, min(a_sum_cap, b_sum_cap)//4, emax)
    side, star = (0, 1, 2, 3, 4), 0
    for shape, holes in shapes(side, star):
        if holes != next(pair for name, pair in shapes(side, star) if name == shape):
            continue
        all_rows = 0
        kept = Counter()
        witness = None
        for inside in support_choices(signatures(side, holes), 6):
            all_rows += 1
            rows = b_profile(side, star, holes, inside)
            if rows is not None:
                profile = tuple(sorted((degree, shared) for degree, shared, _, _ in rows.values()))
                kept[profile] += 1
                if witness is None or max(shared for _, shared in profile) < witness[0]:
                    witness = (max(shared for _, shared in profile), inside, profile)
        print('global', shape, 'holes', holes, 'states', all_rows, 'survive', sum(kept.values()),
              'profiles', len(kept), 'example', witness)
        for profile, count in sorted(kept.items()):
            print('profile', shape, profile, count)


def scan(args):
    stats = Counter()
    first_witness = {}
    observations = []
    with args.output.open('w') as stream:
        for row in args.keys.read_text().splitlines():
            for reverse in (False, True):
                window = Window.parse(row, reverse)
                for degree in args.degree:
                    for shape, holes in roles(window, degree):
                        tag = degree, shape, int(reverse)
                        stats[(*tag, 'roles')] += 1
                        key = role_id(window, degree, shape, holes)
                        if args.roles_only:
                            print(key, file=stream)
                            continue
                        single = project(window, degree, holes, joint=False, terminal=not args.calibration)
                        joint = project(window, degree, holes, joint=True, terminal=not args.calibration)
                        assert not joint or single
                        status = 'J' if joint else ('S' if single else 'N')
                        stats[(*tag, status)] += 1
                        print(f'{status}\t{key}', file=stream)
                        observations.append((window, holes, degree, shape, joint, single))
                        if joint:
                            validate_witness(window, degree, holes, joint, joint=True, terminal=not args.calibration)
                            first_witness.setdefault(tag, (key, joint))
    for tag, count in sorted(stats.items()):
        print('scan', *tag, count)
    if args.witness is not None:
        args.witness.write_text(json.dumps({str(key): value for key, value in first_witness.items()}, indent=2)+'\n')
    if args.calibration:
        positive = occupied = 0
        for window, holes, degree, shape, joint, single in observations:
            if single:
                validate_witness(window, degree, holes, single, joint=False, terminal=False)
                positive += 1
            pivot = 1 << window.pivots[1]
            alternate = next((candidate for name, candidate in shapes(window.sides[1], window.stars[1])
                              if name == shape and sum(bool(pivot & hole) for hole in candidate) == 9-degree
                              and any(window.seen[1][hole] for hole in candidate)), None)
            if alternate:
                assert project(window, degree, alternate, joint=False, terminal=False) is None
                assert project(window, degree, alternate, joint=True, terminal=False) is None
                occupied += 1
        assert positive and occupied
        print('addback and occupied-hole controls', positive, occupied, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('table')
    control = sub.add_parser('small-control')
    control.add_argument('g6')
    direct = sub.add_parser('direct-control')
    direct.add_argument('tsv', type=Path)
    samples = sub.add_parser('scan')
    samples.add_argument('keys', type=Path)
    samples.add_argument('output', type=Path)
    samples.add_argument('--degree', nargs='+', type=int, choices=(8, 9), default=(8, 9))
    samples.add_argument('--roles-only', action='store_true')
    samples.add_argument('--calibration', action='store_true')
    samples.add_argument('--witness', type=Path)
    args = parser.parse_args()
    if args.command == 'table':
        table()
    elif args.command == 'small-control':
        small_control(args.g6)
    elif args.command == 'direct-control':
        direct_control(args.tsv)
    else:
        scan(args)


if __name__ == '__main__':
    main()
