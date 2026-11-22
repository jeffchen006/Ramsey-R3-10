#!/usr/bin/env python3
"""Shared W-edge counts for the paired equality projection, not a graph search."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path
from time import process_time

from round13_signatures import (compact, counts_map, graph, groups, integer, joint_assignment,
                                make_model, paired_model, root_degrees, roster, validate, vertices)
from scan import verify
from signature_rows import lower_edges
from typed_lp import RAMSEY


def mask(indices):
    return sum(1 << index for index in indices)


def shared(model, doubles, width, private, total, target, windows):
    types = tuple(key for key in model.bounds if key[0] == 'site')
    limits = {key: model.bounds[key] for key in types}
    support = {key: key[1:3] for key in types}
    signatures = [groups(width, side) for side in doubles]
    indices = [{cell: index for index, cell in enumerate(side)} for side in signatures]
    cross = tuple(range(1, width - private))
    alpha = width + private - 1
    degree = [root_degrees(width, private, side) for side in doubles]
    attachment = sum(private * (width - 1) + 2 * sum(0 not in pair for pair in side) for side in doubles)
    interior_edges = total - (2 * width - 1) - len(cross) - attachment
    neighbors = defaultdict(dict)
    margins = defaultdict(dict)
    edges = {}
    for first, second in combinations(types, 2):
        if any(set(left).intersection(right) for left, right in zip(support[first], support[second])):
            continue
        column = model.col(('Wedge', first, second), limits[first] * limits[second])
        edges[first, second] = column
        for endpoint, other in ((first, second), (second, first)):
            neighbors[endpoint][other] = column
            model.le({column: 1, endpoint: -limits[other]}, 0, 'edge_population_capacity')
        for side in range(2):
            old_pair = sorted((indices[side][support[first][side]], indices[side][support[second][side]]))
            margins[(side, 'edge', *old_pair)][column] = 1
    for side in range(2):
        kept = [index for index, support in enumerate(signatures[side]) if 0 not in support]
        for first, second in combinations(kept, 2):
            cell = (side, 'edge', first, second)
            row = margins[cell]
            if cell in model.bounds:
                row[cell] = -1
            model.eq(row, 0, 'same_W_edge_marginal')
    model.eq({column: 1 for column in edges.values()}, interior_edges, 'W_edges')
    for endpoint in types:
        model.eq({**{column: 1 for column in neighbors[endpoint].values()},
                  endpoint: sum(map(len, support[endpoint])) - endpoint[3]}, 0, 'W_type_degree')
        for side in range(2):
            for anchor in range(1, width):
                if anchor in support[endpoint][side]:
                    continue
                via_cross = int(anchor in cross and anchor in support[endpoint][1 - side])
                row = {column: 1 for other, column in neighbors[endpoint].items()
                       if anchor in support[other][side]}
                if not via_cross:
                    model.le({**{column: -1 for column in row}, endpoint: 1}, 0, 'W_type_domination')
                if target:
                    cap = endpoint[3] + degree[side][anchor] - 11 - via_cross
                    model.le({**row, endpoint: -cap}, 0, 'W_type_codegree')
                if len(support[endpoint][side]) == 1:
                    matching = {column: 1 for other, column in neighbors[endpoint].items()
                                if support[other][side] == (anchor,)}
                    private_pair = tuple(sorted((support[endpoint][side][0], anchor)))
                    model.le({**{column: -1 for column in matching}, endpoint: 1},
                             int(private_pair not in doubles[side]), 'W_type_private_matching')
    if windows:
        add_windows(model, width, alpha, cross, types, edges)
    return compact(model), edges


@lru_cache(maxsize=None)
def lines(target):
    """Integer inequalities below every tabulated point of the lower convex hull."""
    hull = []
    for order in range(RAMSEY[target]):
        point = (order, lower_edges(target, order))
        while len(hull) > 1:
            left, right = hull[-2:]
            if (right[1] - left[1]) * (point[0] - right[0]) < (point[1] - right[1]) * (right[0] - left[0]):
                break
            hull.pop()
        hull.append(point)
    result = []
    for left, right in zip(hull, hull[1:]):
        dx, dy = right[0] - left[0], right[1] - left[1]
        offset = dx * left[1] - dy * left[0]
        assert all(dx * lower_edges(target, order) >= dy * order + offset for order in range(RAMSEY[target]))
        if dy:
            result.append((dx, dy, offset))
    return result


def add_windows(model, width, alpha, cross, types, edges):
    wing_size = width - 1
    wing_mask = (1 << (2 * wing_size)) - 1
    root_left, root_right = 2 * wing_size, 2 * wing_size + 1
    boundary_order = 2 * width
    boundary = [(root_left, root_right), *((root_left, index) for index in range(wing_size)),
                *((root_right, wing_size + index) for index in range(wing_size)),
                *((index - 1, wing_size + index - 1) for index in cross)]
    edge_masks = tuple(mask(pair) for pair in boundary)
    type_masks = {key: mask(index - 1 for index in key[1]) |
                  mask(wing_size + index - 1 for index in key[2]) for key in types}
    edge_support = [(type_masks[first] | type_masks[second], col) for (first, second), col in edges.items()]
    descriptors = set()
    for independent in range(1 << boundary_order):
        size = independent.bit_count()
        if not (max(1, alpha - 6) <= size <= alpha) or any(independent & pair == pair for pair in edge_masks):
            continue
        forbidden = independent
        for first, second in boundary:
            forbidden |= ((1 << second) if independent >> first & 1 else 0)
            forbidden |= ((1 << first) if independent >> second & 1 else 0)
        available = ((1 << boundary_order) - 1) ^ forbidden
        blocked = independent & wing_mask
        target = alpha + 1 - size
        descriptors.add((blocked, 0, target))
        descriptors.add((blocked, available, target))
    for blocked, added, target in sorted(descriptors):
        population = [key for key in types if not type_masks[key] & blocked]
        if not population:
            continue
        fixed_order = added.bit_count()
        fixed_edges = sum(added & pair == pair for pair in edge_masks)
        model.le({key: 1 for key in population}, RAMSEY[target] - 1 - fixed_order, 'W_window_order')
        table = lines(target)
        if not table:
            continue
        internal = [column for support, column in edge_support if not support & blocked]
        attached = {key: (type_masks[key] & added).bit_count() for key in population}
        for dx, dy, offset in table:
            model.le({**{key: dy - dx * attached[key] for key in population},
                      **{column: -dx for column in internal}},
                     dx * fixed_edges - dy * fixed_order - offset, 'W_window_edges')


def lift_capacity(model, pair, column):
    """Enforce the population product at integer points without fixing populations."""
    first, second = sorted(pair, key=model.bounds.__getitem__)
    first_limit, second_limit = model.bounds[first], model.bounds[second]
    if first_limit == 1:
        return
    thresholds = [model.col(('threshold', first, index), 1) for index in range(1, first_limit + 1)
                  if ('threshold', first, index) not in model.bounds]
    if thresholds:
        assert len(thresholds) == first_limit
        model.eq({**{key: 1 for key in thresholds}, first: -1}, 0, 'unary_population')
        for low, high in zip(thresholds, thresholds[1:]):
            model.le({high: 1, low: -1}, 0, 'unary_order')
    caps = [model.col(('edge_tile', first, second, index), second_limit) for index in range(1, first_limit + 1)]
    for index, cap in enumerate(caps, 1):
        model.le({cap: 1, ('threshold', first, index): -second_limit}, 0, 'edge_tile_exists')
        model.le({cap: 1, second: -1}, 0, 'edge_tile_capacity')
    model.le({column: 1, **{cap: -1 for cap in caps}}, 0, 'edge_population_product')


def unpack(model, artifact):
    columns = tuple(model.bounds)
    return {columns[int(index)]: count for index, count in artifact.items()}


def pack(model, assignment):
    return {str(index): assignment[key] for index, key in enumerate(model.bounds) if assignment.get(key)}


def excess(edges, assignment):
    return [pair for pair, col in edges.items() if assignment.get(col, 0) >
            assignment.get(pair[0], 0) * assignment.get(pair[1], 0)]


def binding(adj, roots, wings, doubles, model, edges):
    assignment = joint_assignment(adj, roots, wings, doubles, model)
    edge_keys = {frozenset(pair): column for pair, column in edges.items()}
    common = set(range(len(adj))).difference(roots, *wings)
    types = {}
    for site in common:
        types[site] = ('site', *(tuple(index for index, anchor in enumerate(wing, 1) if adj[site] >> anchor & 1)
                                for wing in wings), adj[site].bit_count())
    for first, second in combinations(sorted(common), 2):
        if adj[first] >> second & 1:
            assignment[edge_keys[frozenset((types[first], types[second]))]] += 1
    return assignment, types


def descriptors(adj, alpha):
    assert graph.alpha(adj) == alpha and graph.triangle_free(adj)
    assert all(adj[first] & adj[second] or adj[first] >> second & 1
               for first, second in combinations(range(len(adj)), 2))
    counts = Counter(map(int.bit_count, adj))
    for roots in combinations(range(len(adj)), 2):
        first, second = roots
        width = adj[first].bit_count()
        private = alpha + 1 - width
        if not (adj[first] >> second & 1) or not private or private >= width or adj[second].bit_count() != width:
            continue
        equality = width + 2 * (len(adj) - width - 1) - width * private
        if any(sum(adj[vertex].bit_count() for vertex in vertices(adj[root])) != equality for root in roots):
            continue
        wings = [list(vertices(adj[root] & ~(1 << roots[1 - side]))) for side, root in enumerate(roots)]
        crossing = [(left, right) for left in wings[0] for right in wings[1] if adj[left] >> right & 1]
        assert len(crossing) == width - 1 - private
        if crossing:
            wings = [list(ends) + [vertex for vertex in wing if vertex not in ends]
                     for wing, ends in zip(wings, zip(*crossing))]
        assert all(len(wing) == len(set(wing)) == width - 1 for wing in wings)
        doubles = []
        for side, root in enumerate(roots):
            anchors = (roots[1 - side], *wings[side])
            outside = tuple(vertices(((1 << len(adj)) - 1) & ~(adj[root] | 1 << root)))
            cell = [tuple(index for index, anchor in enumerate(anchors) if adj[vertex] >> anchor & 1)
                    for vertex in outside]
            assert all(1 <= len(support) <= 2 for support in cell)
            doubles.append(tuple(sorted(support for support in cell if len(support) == 2)))
        yield roots, wings, doubles, width, private, counts, sum(counts[degree] * degree for degree in counts) // 2


def controls():
    adj = [sum(1 << ((vertex + step) % 13) for step in (1, -1, 5, -5)) for vertex in range(13)]
    run = 0
    for roots, wings, doubles, width, private, counts, total in descriptors(adj, 4):
        base = paired_model(doubles, width, private, counts, total, star=True)
        literal = joint_assignment(adj, roots, wings, doubles, base)
        model, edges = shared(base, doubles, width, private, total, False, True)
        planted, _ = binding(adj, roots, wings, doubles, paired_model(doubles, width, private, counts, total, star=True),
                             edges)
        assert all(planted[key] == value for key, value in literal.items())
        validate(model, planted)
        assert not excess(edges, planted)
        run += 1
    assert run == 26
    print('C13(1,5): 26 literal paired equality roots retain their same W edges, exact', flush=True)
    trials = 0
    from typed_lp import Model
    for first_size in range(2, 5):
        for second_size in range(first_size, 5):
            model = Model()
            pair = model.col(('a',), first_size), model.col(('b',), second_size)
            edge = model.col(('m',), first_size * second_size)
            lift_capacity(model, pair, edge)
            for left in range(first_size + 1):
                for right in range(second_size + 1):
                    point = {pair[0]: left, pair[1]: right, edge: left * right}
                    for row in range(1, first_size + 1):
                        point['threshold', pair[0], row] = int(row <= left)
                        point[('edge_tile', *pair, row)] = right if row <= left else 0
                    validate(model, point)
                    if left * right < model.bounds[edge]:
                        point[edge] += 1
                        try:
                            validate(model, point)
                        except AssertionError as error:
                            assert error.args[0][0] == 'edge_population_product'
                        else:
                            raise AssertionError('one extra edge passed capacity')
                    trials += 1
    print('population-product controls:', trials, 'population pairs; exact maximal assignment and one-more check',
          flush=True)


def instances():
    table = {(key, tag): signature for key, tag, signature in roster(True)}
    pilot = json.loads(Path(__file__).with_name('round14_pilot.json').read_text())
    for key, tag in pilot:
        yield tuple(key), tag, table[tuple(key), tag]


def build(key, signature, windows):
    return shared(make_model(True, key, signature), signature, 6, 4, key[0], True, windows)


def bounded_lp(model, cap):
    from warnings import catch_warnings, simplefilter

    import numpy as np
    from scipy.optimize import OptimizeWarning, linprog
    from scipy.sparse import csr_matrix, eye, hstack, vstack

    indices = {key: index for index, key in enumerate(model.bounds)}
    terms, rows, columns, rhs = [], [], [], []
    for index, (row, bound, _) in enumerate(model.rows):
        rhs.append(bound)
        for key, coefficient in row.items():
            rows.append(index)
            columns.append(indices[key])
            terms.append(coefficient)
    matrix = csr_matrix((terms, (rows, columns)), shape=(len(rhs), len(indices)))
    options = {'threads': 1, 'time_limit': cap, 'run_crossover': 'off'}
    with catch_warnings():
        simplefilter('ignore', OptimizeWarning)
        result = linprog(np.zeros(len(indices)), A_ub=matrix, b_ub=rhs,
                         bounds=list(zip([0] * len(indices), model.bounds.values())), method='highs-ipm', options=options)
        if result.status == 0:
            return 'feasible', None
        if result.status != 2:
            return f'lp-{result.status}', None
        dual = vstack((-matrix.T, csr_matrix(np.ones((1, len(rhs))))), format='csr')
        bound_columns = vstack((-eye(len(indices), format='csr'), csr_matrix((1, len(indices)))), format='csr')
        result = linprog(rhs + list(model.bounds.values()), A_ub=hstack((dual, bound_columns), format='csr'),
                         b_ub=np.append(np.zeros(len(indices)), 1), bounds=(0, None), method='highs-ipm', options=options)
        if result.x is None or result.fun >= 0:
            return f'uncertified-lp-2/dual-{result.status}', None
    for denominator in (10**3, 10**6, 10**9):
        weights = {index: Fraction(float(value)).limit_denominator(denominator)
                   for index, value in enumerate(result.x[:len(rhs)]) if value > 0}
        weights = {index: value for index, value in weights.items() if value}
        if verify(model, weights):
            return 'cert', {str(index): str(weight) for index, weight in weights.items()}
    return 'uncertified-lp-2', None


def pilot(mode, directory, cap, lp_cap):
    windows = mode == 'windows'
    with (directory / f'{mode}.jsonl').open('w') as output:
        for key, tag, signature in instances():
            start = process_time()
            model, edges = build(key, signature, windows)
            print('BUILD', key, tag, len(model.bounds), len(model.rows), round(process_time() - start, 3), flush=True)
            status, artifact = bounded_lp(model, lp_cap) if lp_cap else ('not-run', None)
            print('LP', key, tag, status, round(process_time() - start, 3), flush=True)
            history = []
            if (status in ('feasible', 'not-run') or status.startswith('lp-')) and cap:
                for attempt in range(4):
                    status, point = integer(model, cap)
                    if status != 'integer-witness':
                        artifact = None
                        break
                    invalid = excess(edges, point)
                    if not invalid:
                        artifact = pack(model, point)
                        break
                    print('capacity refinements', key, tag, attempt, len(invalid), flush=True)
                    status = 'violated-product'
                    if attempt == 3:
                        break
                    for pair in invalid:
                        assert pair not in history
                        history.append(pair)
                        lift_capacity(model, pair, edges[pair])
                if status == 'mip-2' and history and lp_cap:
                    exact, dual = bounded_lp(model, lp_cap)
                    if exact == 'cert':
                        status, artifact = exact, dual
            print('END', key, tag, status, round(process_time() - start, 3), flush=True)
            edge_index = {pair: index for index, pair in enumerate(edges)}
            print(json.dumps({'key': key, 'tag': tag, 'status': status, 'artifact': artifact,
                              'lifted': [edge_index[pair] for pair in history]}), file=output, flush=True)


def replay(mode, directory):
    expected = {(key, tag): signature for key, tag, signature in instances()}
    tally = Counter()
    for line in (directory / f'{mode}.jsonl').read_text().splitlines():
        record = json.loads(line)
        key, tag = tuple(record['key']), record['tag']
        model, edges = build(key, expected.pop((key, tag)), mode == 'windows')
        pairs = tuple(edges)
        for index in record['lifted']:
            pair = pairs[index]
            lift_capacity(model, pair, edges[pair])
        status, artifact = record['status'], record['artifact']
        if status == 'cert':
            assert verify(model, {int(index): Fraction(weight) for index, weight in artifact.items()})
        elif status == 'integer-witness':
            assignment = unpack(model, artifact)
            validate(model, assignment)
            assert not excess(edges, assignment)
        else:
            assert artifact is None
        tally[status] += 1
    assert not expected
    print(mode, dict(tally), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'plain', 'windows'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--cap', type=float, default=0, help='seconds per optional integer price')
    parser.add_argument('--lp-cap', type=float, default=10, help='seconds per LP price; zero skips it')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.mode == 'control':
        controls()
    elif args.verify:
        replay(args.mode, args.directory)
    else:
        pilot(args.mode, args.directory, args.cap, args.lp_cap)


if __name__ == '__main__':
    main()
