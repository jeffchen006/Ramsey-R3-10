#!/usr/bin/env python3
"""Audit the marked boundary additions for adjacent private-equality roots."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from audit_floor_covers import digest, has_independent, require
from audit_residue_moves import checked_catalogue, expect_rejection
from residue_bundle import parse_graph6, read_catalogue, to_graph6, triangle_free


def bit_vertices(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def edge_count(graph):
    return sum(map(int.bit_count, graph)) // 2


def induced(graph, vertices):
    return [sum(1 << col for col, other in enumerate(vertices) if graph[vertex] >> other & 1)
            for vertex in vertices]


def toggle(graph, pairs):
    changed = graph.copy()
    for first, second in pairs:
        changed[first] ^= 1 << second
        changed[second] ^= 1 << first
    return changed


def boundary(graph, vertices, private):
    mask = sum(1 << vertex for vertex in vertices)
    outside = ((1 << len(graph)) - 1) ^ mask
    supports = Counter(graph[other] & mask for other in bit_vertices(outside))
    if any(signature.bit_count() not in (1, 2) or (signature.bit_count() == 2 and count != 1)
           for signature, count in supports.items()):
        return None
    if any(supports[1 << vertex] != private for vertex in vertices):
        return None
    return tuple((first, second) for first, second in combinations(vertices, 2)
                 if (1 << first) | (1 << second) not in supports)


def inverse(graph, width, private, added, remaining=0):
    require(triangle_free(graph), 'inverse expects a triangle-free upper row')
    ceiling = private + width - 1
    slack = [ceiling - nbrs.bit_count() for nbrs in graph]
    pool = [vertex for vertex, value in enumerate(slack) if 0 <= value <= remaining]
    for vertices in combinations(pool, width):
        if sum(slack[vertex] for vertex in vertices) != 2 * remaining:
            continue
        internal = tuple((first, second) for first, second in combinations(vertices, 2)
                         if graph[first] >> second & 1)
        if len(internal) != added:
            continue
        missing = boundary(graph, vertices, private)
        if missing is None or len(missing) != added + remaining or not set(internal) <= set(missing):
            continue
        yield vertices, internal


def inverse_with_alpha(graph, width, private, added, remaining, cap):
    for vertices, internal in inverse(graph, width, private, added, remaining):
        original = toggle(graph, internal)
        yield vertices, internal, original, not has_independent(original, cap + 1)


def marks(graph, width, private, prefilter=True):
    full = (1 << len(graph)) - 1
    allowed = [full ^ neighbors for neighbors in graph]
    if prefilter:
        for first, second in combinations(range(len(graph)), 2):
            if (graph[first] & graph[second]).bit_count() > 1:
                allowed[first] &= ~(1 << second)
                allowed[second] &= ~(1 << first)

    def independent(active, prefix, remaining):
        if not remaining:
            yield prefix
            return
        while active.bit_count() >= remaining:
            low = active & -active
            vertex = low.bit_length() - 1
            active ^= low
            yield from independent(active & allowed[vertex], (*prefix, vertex), remaining - 1)

    for vertices in independent(full, (), width):
        absent = boundary(graph, vertices, private)
        if absent is not None:
            yield vertices, absent


def validate_index(received, expected):
    require(len(set(received)) == len(received), 'duplicate marked boundary')
    require(set(received) == set(expected), 'omitted or unexpected marked boundary')


def independently_legal(graph, vertices):
    return tuple(pair for pair in combinations(vertices, 2)
                 if not graph[pair[0]] >> pair[1] & 1 and triangle_free(toggle(graph, [pair])))


def calibrate_graph(graph, degree, alpha_cap, name):
    require(triangle_free(graph) and not has_independent(graph, alpha_cap + 1)
            and has_independent(graph, alpha_cap), 'wrong positive control graph')
    private = alpha_cap + 1 - degree
    width = degree - 1
    rows = []
    universe = (1 << len(graph)) - 1

    def locally_maximal(vertex):
        return all(graph[vertex] & graph[other]
                   for other in bit_vertices(universe & ~((1 << vertex) | graph[vertex])))

    for root, peer in combinations(range(len(graph)), 2):
        if not graph[root] >> peer & 1:
            continue
        for first, second in ((root, peer), (peer, root)):
            if any(graph[vertex].bit_count() != degree or not locally_maximal(vertex) or
                   sum(graph[other].bit_count() for other in bit_vertices(graph[vertex])) !=
                   degree + 2 * (len(graph) - 1 - degree) - degree * private
                   for vertex in (first, second)):
                continue
            exterior = list(bit_vertices(universe & ~((1 << first) | graph[first])))
            side = tuple(index for index, vertex in enumerate(exterior) if graph[second] >> vertex & 1)
            section = induced(graph, exterior)
            legal = independently_legal(section, side)
            forward = dict(marks(section, width, private))
            require(forward == dict(marks(section, width, private, prefilter=False)),
                    'optimized forward marks disagree with exhaustive control')
            require(len(side) == width and legal and forward[side] == legal,
                    'planted boundary missing from forward marks')
            exclusive = graph[first] ^ (1 << second)
            require(sum((graph[vertex] & exclusive).bit_count() for vertex in exterior
                        if graph[second] >> vertex & 1) == width - private,
                    'wrong planted cross-edge count')
            completed = toggle(section, legal)
            require(triangle_free(completed) and not has_independent(completed, alpha_cap)
                    and (side, legal) in list(inverse(completed, width, private, len(legal)))
                    and toggle(completed, legal) == section, 'planted inverse failed')
            for first_edge in legal:
                partial = toggle(section, [first_edge])
                require((side, (first_edge,)) in list(inverse(partial, width, private, 1, len(legal) - 1)),
                        'planted partial inverse failed')
            rows.append((first, second, side, legal))
    if rows:
        validate_index(rows[::-1], rows)
        expect_rejection(lambda: validate_index(rows[1:], rows), 'omitted')
        expect_rejection(lambda: validate_index([*rows, rows[0]], rows), 'duplicate')
    print(f'{name}: {len(rows)} planted directed equality pairs; added-counts '
          f'{sorted(Counter(len(row[3]) for row in rows).items())}', flush=True)
    return rows


def calibrate(small, medium):
    cyclic = [sum(1 << ((vertex + step) % 13) for step in (-5, -1, 1, 5)) for vertex in range(13)]
    require(len(calibrate_graph(cyclic, 4, 4, 'C13(1,5)')) == 52, 'wrong C13 control count')
    rows, _ = checked_catalogue(small, 8, 3)
    require(len(rows) == 3, 'wrong (3,4;8) count')
    total = sum(len(calibrate_graph(parse_graph6(row.decode('ascii')), 3, 3, f'C8 row {index}'))
                for index, row in enumerate(rows, 1))
    print(f'C8: {total} adjacent degree-3 equality pair controls')
    rows, _ = checked_catalogue(medium, 12, 4)
    require(len(rows) == 12, 'wrong (3,5;12) count')
    two_edge = [entry for index, row in enumerate(rows, 1)
                for entry in calibrate_graph(parse_graph6(row.decode('ascii')), 4, 4, f'C12 row {index}')]
    require(two_edge and all(len(entry[3]) == 2 for entry in two_edge), 'no planted two-edge control')
    print(f'C12: {len(two_edge)} planted two-edge completions')
    cycle = [sum(1 << ((vertex + step) % 5) for step in (-1, 1)) for vertex in range(5)]
    require(not independently_legal(cycle, tuple(range(5))), 'C5 saturation control failed')
    require(not list(inverse(cycle, 2, 1, 1)), 'C5 should fail the inverse support test')
    square = [0b1010, 0b0101, 0b1010, 0b0101]
    square_marks = tuple(inverse_with_alpha(square, 3, 0, 2, 0, 2))
    require(not has_independent(square, 3) and square_marks and not any(hit[3] for hit in square_marks),
            'inverse must check alpha again after deleting edges')
    print('PASS saturated negative, lower-alpha rejection, and omitted/duplicate index controls', flush=True)


def pilot(path, sample, compare):
    rows = read_catalogue(path)
    require(digest(path.read_bytes()) == '7db2550bbfc2f03238c74e9e62f7199008db509e4df54ebff89645ca9cde3e16'
            and len(rows) == 1223 and 0 < sample <= len(rows), 'wrong e120 baseline or sample')
    distinct = set()
    found = 0
    completed = 0
    for ordinal in (step * len(rows) // sample for step in range(sample)):
        row = rows[ordinal]
        section = parse_graph6(row.decode('ascii'))
        require(len(section) == 33 and edge_count(section) == 120 and triangle_free(section)
                and not has_independent(section, 9), 'bad pilot e120 row')
        hits = tuple(marks(section, 5, 4))
        if compare:
            require(hits == tuple(marks(section, 5, 4, prefilter=False)), 'forward pilot mismatch')
        if hits:
            found += 1
        for vertices, legal in hits:
            require(len(legal) == 2 and legal == independently_legal(section, vertices),
                    'independent one-edge toggle disagrees')
            above = toggle(section, legal)
            require(triangle_free(above) and edge_count(above) == 122 and
                    (vertices, legal) in list(inverse(above, 5, 4, 2)), 'e122 inverse disagrees')
            distinct.add(to_graph6(above))
            completed += 1
    print(f'{sample}/{len(rows)} supplied e120 checked: {found} marked rows, {completed} labelled marks, '
          f'{len(distinct)} distinct labelled completions; no scope or census exclusion')


def inspect_upper(path, edge):
    rows, _ = checked_catalogue(path, 33, 8, {edge: len(read_catalogue(path))})
    print('row\tupper_sha256\tmark_0based\tremoved_0based\tlower_sha256\tlower_alpha_at_most_8')
    found = accepted = 0
    for ordinal, row in enumerate(rows, 1):
        upper = parse_graph6(row.decode('ascii'))
        for vertices, internal, original, alpha_ok in inverse_with_alpha(upper, 5, 4, edge - 120, 122 - edge, 8):
            require(edge_count(original) == 120 and triangle_free(original), 'invalid inverse lower shape')
            print(ordinal, digest(row), ','.join(map(str, vertices)),
                  ','.join(f'{first}-{second}' for first, second in internal),
                  digest(to_graph6(original).encode('ascii')), int(alpha_ok), sep='\t')
            found += 1
            accepted += alpha_ok
    print(f'e{edge}: {len(rows)} valid supplied upper rows, {found} structural marks, {accepted} alpha-valid lower marks',
          file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    control = actions.add_parser('calibrate')
    control.add_argument('small', type=Path)
    control.add_argument('medium', type=Path)
    probe = actions.add_parser('pilot')
    probe.add_argument('catalogue', type=Path)
    probe.add_argument('sample', type=int)
    probe.add_argument('--compare', action='store_true')
    upper = actions.add_parser('inspect-upper')
    upper.add_argument('catalogue', type=Path)
    upper.add_argument('edge', type=int, choices=[121, 122])
    args = parser.parse_args()
    if args.action == 'calibrate':
        calibrate(args.small, args.medium)
    elif args.action == 'pilot':
        pilot(args.catalogue, args.sample, args.compare)
    else:
        inspect_upper(args.catalogue, args.edge)
