#!/usr/bin/env python3
"""Bind path-centre projections and build an independent complete-window CNF."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from audit_adjacent_residues import boundary, calibrate_graph, edge_count, induced, toggle
from audit_floor_covers import digest, has_independent, require
from audit_residue_moves import checked_catalogue, expect_rejection
from residue_bundle import parse_graph6, read_catalogue, to_graph6, triangle_free


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def matches(graph, mark, private):
    mask = sum(1 << vertex for vertex in mark)
    return (not any(graph[vertex] & mask for vertex in mark)
            and boundary(graph, mark, private) == ())


def projections(graph, mark, cross, private, alpha_cap, require_dominating):
    require(len(mark) >= 3 and len(set(mark)) == len(mark) and cross in mark,
            'invalid path/leaf mark')
    require(triangle_free(graph) and not has_independent(graph, alpha_cap + 1),
            'invalid upper graph')
    missing = boundary(graph, mark, private)
    require(missing is not None and len(missing) == 2, 'invalid strip signatures')
    incidence = Counter(vertex for pair in missing for vertex in pair)
    require(sorted(incidence.values()) == [1, 1, 2] and incidence[cross] == 1,
            'not a path with cross at a leaf')
    centre = next(vertex for vertex, degree in incidence.items() if degree == 2)
    leaf = next(vertex for vertex, degree in incidence.items() if degree == 1 and vertex != cross)
    internal = tuple(pair for pair in combinations(mark, 2) if graph[pair[0]] >> pair[1] & 1)
    require(set(internal) <= set(missing), 'internal addition outside missing pairs')
    lower = toggle(graph, internal)
    require(not has_independent(lower, alpha_cap + 1), 'lower graph fails alpha after deletion')
    retained = tuple(sorted(set(mark) - {centre}))
    universe = (1 << len(graph)) - 1
    available = universe & ~((1 << centre) | lower[centre])
    exterior = tuple(vertices(available & ~sum(1 << vertex for vertex in retained)))
    order = (*retained, *exterior)
    window = induced(lower, order)
    require(matches(window, tuple(range(len(retained))), private), 'missing complete-window mark')
    require(not has_independent(window, alpha_cap), 'window alpha projection failed')
    require(edge_count(window) == edge_count(lower) - sum(lower[other].bit_count()
                                                         for other in vertices(lower[centre])),
            'window edge identity failed')
    if require_dominating:
        require(all(lower[leaf] & lower[other] for other in exterior if not lower[leaf] >> other & 1),
                'noncross leaf does not dominate the window')
    return lower, window, centre, order


def scan(path, width, private, maximum, expected):
    order = width + width * private + width * (width - 1) // 2
    rows, _ = checked_catalogue(path, order, maximum)
    if expected is not None:
        require(len(rows) == expected, 'input census mismatch')
    shapes = Counter()
    print('row\trow_sha256\tmark_0based\tdominating_0based\tmarked_g6')
    for ordinal, line in enumerate(rows, 1):
        graph = parse_graph6(line.decode('ascii'))
        pool = [vertex for vertex in range(order) if graph[vertex].bit_count() == private + width - 1]
        for mark in combinations(pool, width):
            if not matches(graph, mark, private):
                continue
            dominating = tuple(vertex for vertex in mark if all(
                graph[vertex] & graph[other] for other in range(order)
                if vertex != other and not graph[vertex] >> other & 1))
            exterior = tuple(vertex for vertex in range(order) if vertex not in mark)
            print(ordinal, digest(line), ','.join(map(str, mark)), ','.join(map(str, dominating)),
                  to_graph6(induced(graph, (*mark, *exterior))), sep='\t')
            shapes[edge_count(graph), len(dominating)] += 1
    print(f'{path.name}: {len(rows)} valid distinct supplied rows; marks by (edges, dominant anchors): '
          f'{sorted(shapes.items())}', file=sys.stderr)


def calibrate(path):
    rows, _ = checked_catalogue(path, 12, 4)
    require(len(rows) == 12, 'wrong smaller census')
    count = 0
    dominated = 0
    for ordinal, row in enumerate(rows, 1):
        graph = parse_graph6(row.decode('ascii'))
        for root, _, mark, missing in calibrate_graph(graph, 4, 4, f'C12 row {ordinal}'):
            kept = tuple(vertices(((1 << 12) - 1) & ~((1 << root) | graph[root])))
            lower = induced(graph, kept)
            incidence = Counter(vertex for pair in missing for vertex in pair)
            for cross in (vertex for vertex in mark if incidence[vertex] == 1):
                results = [projections(toggle(lower, added), mark, cross, 1, 3, False)
                           for added in ((), (missing[0],), (missing[1],), missing)]
                require(all(result == results[0] for result in results) and results[0][0] == lower,
                        'projection changes with addition level')
                centre = results[0][2]
                expect_rejection(lambda: projections(lower, mark, centre, 1, 3, False), 'not a path')
                independent_leaf = next(vertex for vertex in mark if vertex not in (cross, centre))
                if all(lower[independent_leaf] & lower[other] for other in results[0][3]
                       if other not in mark and not lower[independent_leaf] >> other & 1):
                    require(projections(lower, mark, cross, 1, 3, True) == results[0], 'dominant test disagrees')
                    dominated += 1
                count += 1
    require(count > 0 and dominated > 0, 'no planted positive path/leaf controls')
    square = [0b1010, 0b0101, 0b1010, 0b0101]
    expect_rejection(lambda: projections(square, (0, 1, 2), 0, 0, 2, False), 'lower graph fails alpha')
    print(f'{count} smaller half-strip/leaf labels, {dominated} with required domination; '
          'all four addition levels bind to the same lower window; bad cross and lower alpha rejected')


def window_formula(width, private, dominates, cap, ceiling):
    from pysat.card import CardEnc, EncType

    identity = [1 << column for column in range(width) for _ in range(private)]
    identity += [(1 << left) | (1 << right) for left, right in combinations(range(width), 2)]
    supports = [0] * width + identity
    order = len(supports)
    maximum = private + width - 1
    pairs = list(combinations(range(order), 2))
    def fixed_edge(left, right):
        if right < width:
            return False
        if left < width:
            return bool(supports[right] >> left & 1)
        if supports[left] & supports[right]:
            return False
        if left < width + private and right < width + width * private and (left - width) % private == (right - width) % private:
            return True
        return None

    fixed = {pair: fixed_edge(*pair) for pair in pairs}
    labels = {pair: index for index, pair in enumerate((pair for pair in pairs if fixed[pair] is None), 1)}
    fixed_neighbours = [0] * order
    for (left, right), value in fixed.items():
        if value:
            fixed_neighbours[left] |= 1 << right
            fixed_neighbours[right] |= 1 << left

    clauses = set()
    for triangle in combinations(range(width, order), 3):
        triples = tuple(combinations(triangle, 2))
        if all(fixed[pair] is not False for pair in triples):
            clauses.add(tuple(-labels[pair] for pair in triples if pair in labels))

    def candidates(active, target):
        if target == 0:
            yield ()
        while target and active.bit_count() >= target:
            bit = active & -active
            active ^= bit
            vertex = bit.bit_length() - 1
            for tail in candidates(active & ~fixed_neighbours[vertex], target - 1):
                yield (vertex, *tail)

    for independent in candidates((1 << order) - 1, maximum + 1):
        clauses.add(tuple(labels[pair] for pair in combinations(independent, 2) if pair in labels))
    for anchor in dominates:
        for vertex in range(width, order):
            if fixed[anchor, vertex]:
                continue
            options = [tuple(sorted((vertex, other))) for other in vertices(fixed_neighbours[anchor])]
            if not any(fixed[pair] for pair in options):
                clauses.add(tuple(sorted(labels[pair] for pair in options if pair in labels)))
    rows = sorted(clauses, key=lambda clause: (len(clause), clause))
    last = len(labels)
    limits = []
    if ceiling:
        for vertex in range(width, order):
            incident = [label for pair, label in labels.items() if vertex in pair]
            limits.append((incident, maximum - fixed_neighbours[vertex].bit_count()))
    if cap is not None:
        limits.append((list(labels.values()), cap - sum(neighborhood.bit_count()
                                                      for neighborhood in fixed_neighbours) // 2))
    for literals, budget in limits:
        if budget < 0:
            rows.append(())
        elif budget < len(literals):
            encoding = CardEnc.atmost(lits=literals, bound=budget, top_id=last, encoding=EncType.seqcounter)
            rows.extend(encoding.clauses)
            last = max(last, encoding.nv)
    return fixed_neighbours, labels, rows, last


def build(args):
    neighbourhoods, labels, rows, last = window_formula(args.width, args.private, args.dominate,
                                                         args.cap, args.ceiling)
    with args.cnf.open('w', encoding='ascii') as output:
        output.write(f'p cnf {last} {len(rows)}\n')
        for row in rows:
            output.write(' '.join(map(str, (*row, 0))) + '\n')
    print(f'n={len(neighbourhoods)} vars={last} clauses={len(rows)} graph_vars={len(labels)} '
          f'sha256={digest(args.cnf.read_bytes())}')


def read_model(args):
    neighbourhoods, labels, _, _ = window_formula(args.width, args.private, args.dominate, args.cap, args.ceiling)
    lines = args.model.read_text().splitlines()
    require('s SATISFIABLE' in lines, 'solver did not report SAT')
    assigned = [int(value) for line in lines if line.startswith('v ') for value in line.split()[1:] if value != '0']
    present = set(assigned)
    require(all((label in present) ^ (-label in present) for label in labels.values()), 'incomplete or inconsistent model')
    for (left, right), label in labels.items():
        if label in present:
            neighbourhoods[left] |= 1 << right
            neighbourhoods[right] |= 1 << left
    require(triangle_free(neighbourhoods) and not has_independent(neighbourhoods, args.private + args.width),
            'invalid graph extracted from SAT model')
    require(args.cap is None or edge_count(neighbourhoods) <= args.cap, 'edge cap exceeded')
    require(matches(neighbourhoods, tuple(range(args.width)), args.private), 'missing prescribed mark')
    for anchor in args.dominate:
        require(all(neighbourhoods[anchor] & neighbourhoods[other] for other in range(len(neighbourhoods))
                    if other != anchor and not neighbourhoods[anchor] >> other & 1), 'requested domination failed')
    args.graph.write_text(to_graph6(neighbourhoods) + '\n', encoding='ascii')
    print(f'validated graph n={len(neighbourhoods)} e={edge_count(neighbourhoods)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    student = modes.add_parser('calibrate')
    student.add_argument('catalogue', type=Path)
    finder = modes.add_parser('scan')
    finder.add_argument('catalogue', type=Path)
    finder.add_argument('width', type=int)
    finder.add_argument('private', type=int)
    finder.add_argument('maximum', type=int)
    finder.add_argument('--expected', type=int)
    for mode in ('build', 'model'):
        sub = modes.add_parser(mode)
        sub.add_argument('width', type=int)
        sub.add_argument('private', type=int)
        sub.add_argument('--dominate', type=int, action='append', default=[])
        sub.add_argument('--cap', type=int)
        sub.add_argument('--ceiling', action='store_true')
        if mode == 'build':
            sub.add_argument('cnf', type=Path)
        else:
            sub.add_argument('model', type=Path)
            sub.add_argument('graph', type=Path)
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibrate(args.catalogue)
    elif args.mode == 'scan':
        scan(args.catalogue, args.width, args.private, args.maximum, args.expected)
    elif args.mode == 'build':
        build(args)
    else:
        read_model(args)


if __name__ == '__main__':
    main()
