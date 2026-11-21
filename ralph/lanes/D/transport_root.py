#!/usr/bin/env python3
"""Couple mask counts and outside adjacencies in an orbit-averaged LP."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import time

from max_root import MaxProjection, catalogue, count_edges, squares_floor
from forest_root import arc_bad, blocked_arcs, blocked_triples
from outer_star import Star
from kernel_projection import Projection, bits, decode


class Transport(Projection):
    def __init__(self, kernel, order, degree, keep=None, use_squares=True, star_caps=False, forest=False,
                 pinned_twos=None):
        star = Star(kernel, order, degree)
        if keep is not None:
            assert keep <= set(star.masks)
            star.masks = [mask for mask in star.masks if mask in keep]
        if forest:
            banned = tuple(blocked_triples(kernel))
            star.masks = [mask for mask in star.masks if all(mask & triple != triple for triple in banned)]
        forbidden = tuple(blocked_arcs(kernel)) if forest else ()
        blocks = list(star.orbits())
        self.mask_columns = len(blocks)
        self.p = {mask: index for index, (_, block) in enumerate(blocks) for mask in block}
        generators = [{mask: sum(1 << permutation[coord] for coord in bits(mask)) for mask in star.masks}
                      for permutation in star.generators()]
        assert all(set(generator.values()) == set(star.masks) for generator in generators)

        self.masks = [tuple(block) for _, block in blocks]
        self.arcs = {}
        neighbors = {mask: {} for mask in star.masks}
        outside_pairs = [(left, right) for left, right in combinations(sorted(star.masks), 2)
                         if not left & right and (not forbidden or not arc_bad(left, right, forbidden))]
        for pair in outside_pairs:
            if pair in self.arcs:
                continue
            column = len(self.masks)
            orbit = {pair}
            queue = [pair]
            for left, right in queue:
                for generator in generators:
                    other = tuple(sorted((generator[left], generator[right])))
                    if other not in orbit:
                        orbit.add(other)
                        queue.append(other)
            self.masks.append(tuple(sorted(orbit)))
            for left, right in orbit:
                assert (left, right) not in self.arcs and not left & right and not arc_bad(left, right, forbidden)
                self.arcs[left, right] = column
                neighbors[left][right] = column
                neighbors[right][left] = column
        assert len(self.arcs) == len(outside_pairs)
        self.rows = []
        seen = set()

        def add(terms, bound, name):
            row = tuple(sorted((col, coeff) for col, coeff in terms.items() if coeff))
            if (row or bound < 0) and (row, bound) not in seen:
                self.rows.append((row, bound, name))
                seen.add((row, bound))

        def equal(terms, bound, name):
            add(terms, bound, name + '+')
            add({col: -coeff for col, coeff in terms.items()}, -bound, name + '-')

        projection = MaxProjection(kernel, order, degree)
        maximum = count_edges(kernel)
        tight = degree * maximum == 2 * squares_floor(order, degree)
        if pinned_twos is not None:
            assert tight
            equal(Counter(column for mask, column in self.p.items() if mask.bit_count() == 4),
                  pinned_twos, 'count-22-masks')
        for terms, bound, name in projection.rows:
            aggregate = Counter()
            for col, coeff in terms:
                mask = projection.masks[col]
                if mask in self.p:
                    aggregate[self.p[mask]] += coeff
            add(aggregate, bound, name)
        if forest:
            width = star.interior.bit_length()
            for anchor in range(width):
                root = width + (anchor >= degree - 1)
                left = star.adj[root] ^ (1 << anchor)
                others = star.adj[anchor] ^ (1 << root)
                fixed_pairs = [star.adj[coord] & left for coord in bits(others)
                               if (star.adj[coord] & left).bit_count() == 2]
                possible = [(mask & left, col) for mask, col in self.p.items()
                            if mask >> anchor & 1 and (mask & left).bit_count() == 2]
                subset = left
                while subset:
                    size = subset.bit_count()
                    if size >= 2:
                        fixed = sum(pair & subset == pair for pair in fixed_pairs)
                        terms = Counter(col for pair, col in possible if pair & subset == pair)
                        add(terms, size - 1 - fixed, f'root-forest-rank:{anchor}:{subset}')
                    subset = (subset - 1) & left
        for mask, _ in blocks:
            column = self.p[mask]
            add({column: 1}, 1, f'multiplicity:{mask}')
            edges = Counter(neighbors[mask].values())
            edges[column] -= degree - mask.bit_count()
            equal(edges, 0, f'outside-degree:{mask}')
            for coord in bits(star.interior ^ mask):
                inside_common = (star.adj[coord] & mask).bit_count()
                terms = Counter(col for other, col in neighbors[mask].items() if other >> coord & 1)
                lower = {col: -coeff for col, coeff in terms.items()}
                lower[column] = star.floor - inside_common
                add(lower, 0, f'outside-codeg-:{mask}:{coord}')
                terms[column] = inside_common - 3
                add(terms, 0, f'outside-codeg+:{mask}:{coord}')
            if star_caps:
                groups = defaultdict(Counter)
                for other, edge_column in neighbors[mask].items():
                    for size in (2, 3):
                        for subset in combinations(bits(other), size):
                            groups[subset][edge_column] += 1
                for subset, terms in sorted(groups.items()):
                    upper = 1 if len(subset) == 3 else 3 - (star.adj[subset[0]] & star.adj[subset[1]]).bit_count()
                    terms[column] = -upper
                    add(terms, 0, f'outside-star-cap:{mask}:{subset}')
                if tight:
                    for coord in bits(mask):
                        fixed_threes = sum((star.adj[coord] & star.adj[other]).bit_count() >= 2
                                           for other in bits(mask) if other != coord)
                        terms = Counter(edge_column for other, edge_column in neighbors[mask].items()
                                        if (other & star.adj[coord]).bit_count() >= 2)
                        terms[column] = fixed_threes - (maximum - (degree - 1))
                        add(terms, 0, f'outside-star-square:{mask}:{coord}')
        for column in range(len(blocks), len(self.masks)):
            left, right = self.masks[column][0]
            for mask in (left, right):
                add({column: 1, self.p[mask]: -1}, 0, f'edge-implies-mask:{left}:{right}:{mask}')

        if use_squares:
            for first, second in combinations(range(len(star.adj)), 2):
                if not star.adj[first] >> second & 1:
                    continue
                a_side = star.adj[first] ^ (1 << second)
                b_side = star.adj[second] ^ (1 << first)
                fixed = sum((star.adj[coord] & b_side).bit_count() for coord in bits(a_side))
                terms = Counter()
                for mask, col in self.p.items():
                    if mask >> first & 1:
                        terms[col] += (mask & b_side).bit_count()
                    if mask >> second & 1:
                        terms[col] += (mask & a_side).bit_count()
                if second < star.interior.bit_length():
                    for (left, right), col in self.arcs.items():
                        if (left >> first & 1 and right >> second & 1) or (left >> second & 1 and right >> first & 1):
                            terms[col] += 1
                name = f'exact-anchored-square:{first}:{second}'
                if tight:
                    equal(terms, maximum - fixed, name)
                else:
                    add(terms, maximum - fixed, name)

    def append_unit_bounds(self):
        first = len(self.rows)
        self.rows.extend((((column, 1),), 1, f'unit-bound:{column}') for column in range(len(self.masks)))
        return first

    def solve_bounded(self, first_unit, method='highs', seconds=18.0):
        import numpy as np
        from scipy.optimize import linprog
        from scipy.sparse import coo_matrix

        row_ids, col_ids, entries, bounds = [], [], [], []
        width = len(self.masks)
        for row, (terms, bound, _) in enumerate(self.rows):
            row_ids.extend([row] * (len(terms) + 1))
            col_ids.extend(column for column, _ in terms)
            col_ids.append(width)
            entries.extend(coeff for _, coeff in terms)
            entries.append(-1)
            bounds.append(bound)
        matrix = coo_matrix((entries, (row_ids, col_ids)), shape=(len(bounds), width + 1)).tocsc()
        goal = np.zeros(width + 1)
        goal[-1] = 1
        result = linprog(goal, A_ub=matrix, b_ub=bounds, method=method, options={'time_limit': seconds})
        if not result.success:
            return f'unknown-{result.status}', None
        if result.fun < 1e-8:
            return 'feasible', None
        for scale in (1024, 65536, 10**7, 10**9, 10**12):
            weights = Counter({row: round(float(-value) * scale) for row, value in enumerate(result.ineqlin.marginals)
                               if value < 0 and round(float(-value) * scale) > 0})
            combined = [0] * width
            for row, weight in weights.items():
                for column, coeff in self.rows[row][0]:
                    combined[column] += weight * coeff
            for column, coeff in enumerate(combined):
                if coeff < 0:
                    weights[first_unit + column] -= coeff
            proof = [[row, weight] for row, weight in sorted(weights.items())]
            try:
                self.check(proof)
            except ValueError:
                continue
            return 'cert', proof
        return 'infeas-unchecked', None

    def solve_integer_masks(self, seconds):
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp
        from scipy.sparse import coo_matrix

        sizes = np.array([len(orbit) for orbit in self.masks])
        row_ids, col_ids, entries, bounds = [], [], [], []
        for row, (terms, bound, _) in enumerate(self.rows):
            row_ids.extend([row] * len(terms))
            col_ids.extend(column for column, _ in terms)
            entries.extend(coeff / sizes[column] for column, coeff in terms)
            bounds.append(bound)
        matrix = coo_matrix((entries, (row_ids, col_ids)), shape=(len(bounds), len(sizes))).tocsc()
        result = milp(np.zeros(len(sizes)), integrality=(np.arange(len(sizes)) < self.mask_columns).astype(int),
                      bounds=Bounds(0, sizes), constraints=LinearConstraint(matrix, ub=bounds),
                      options={'time_limit': seconds})
        return {0: 'integer-masks-feasible', 1: 'integer-masks-limit', 2: 'integer-masks-infeas-unchecked'}.get(
            result.status, f'integer-masks-unknown-{result.status}'), None

    def replay_graph(self, graph, degree):
        outside = range(2 * degree, len(graph))
        interior = (1 << (2 * degree - 2)) - 1
        elements = {vertex: graph[vertex] & interior for vertex in outside}
        assert len(set(elements.values())) == len(elements)
        observed = Counter(self.p[mask] for mask in elements.values())
        for first, second in combinations(outside, 2):
            if graph[first] >> second & 1:
                pair = tuple(sorted((elements[first], elements[second])))
                observed[self.arcs[pair]] += 1
        projection = {col: Fraction(count, len(self.masks[col])) for col, count in observed.items()}
        for terms, bound, name in self.rows:
            total = sum(coeff * projection.get(col, 0) for col, coeff in terms)
            assert total <= bound, (name, total, bound)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('index', type=int)
    parser.add_argument('--keep', type=Path)
    parser.add_argument('--control', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--no-squares', action='store_true')
    parser.add_argument('--star-caps', action='store_true')
    parser.add_argument('--bounded-dual', action='store_true')
    parser.add_argument('--integer-masks', action='store_true')
    parser.add_argument('--forest', action='store_true')
    parser.add_argument('--pin-22-count', type=int)
    parser.add_argument('--lp-method', choices=('highs', 'highs-ds', 'highs-ipm'), default='highs')
    parser.add_argument('--lp-seconds', type=float, default=18.0)
    args = parser.parse_args()
    assert not args.integer_masks or not args.bounded_dual
    codes = list(catalogue(args.order, args.degree))
    start = time.process_time()
    if args.control:
        assert args.order == 16 and args.degree == 5 and not args.keep
        cases = 0
        for path in sorted(args.control.glob('eager-*.g6')):
            index = int(path.stem.split('-')[-1])
            graphs = [decode(line) for line in path.read_text().splitlines()]
            if not graphs:
                continue
            kernel = decode(codes[index])
            tight = 5 * count_edges(kernel) == 2 * squares_floor(16, 5)
            model = Transport(kernel, 16, 5, use_squares=not args.no_squares,
                              star_caps=args.star_caps, forest=args.forest and tight,
                              pinned_twos=args.pin_22_count if tight else None)
            for graph in graphs:
                model.replay_graph(graph, 5)
                cases += 1
        assert cases == 13
        print(f'PASS {cases} exact rational orbit averages from C16 CPU={time.process_time()-start:.3f}')
        return
    code = codes[args.index]
    assert not args.forest or (args.order, args.degree) == (40, 9) and 19 <= args.index <= 34
    assert args.pin_22_count is None or (args.order, args.degree) == (40, 9) and 6 <= args.pin_22_count <= 14
    keep = None
    if args.keep:
        item = json.loads(args.keep.read_text())
        assert item['index'] == args.index and item['code'] == code
        keep = set(item['kept'])
    model = Transport(decode(code), args.order, args.degree, keep=keep, use_squares=not args.no_squares,
                      star_caps=args.star_caps, forest=args.forest, pinned_twos=args.pin_22_count)
    first_unit = model.append_unit_bounds() if args.bounded_dual else None
    if args.verify:
        result = json.loads(args.verify.read_text())
        assert result['index'] == args.index and result['code'] == code and result['status'] == 'cert'
        assert result['rows'] == len(model.rows) and result['columns'] == len(model.masks)
        model.check(result['proof'])
        print(f'PASS index={args.index} exact integer Farkas replay cpu={time.process_time()-start:.3f}')
        return
    build = time.process_time() - start
    if args.integer_masks:
        status, proof = model.solve_integer_masks(args.lp_seconds)
    else:
        status, proof = (model.solve() if first_unit is None else
                         model.solve_bounded(first_unit, args.lp_method, args.lp_seconds))
    print(json.dumps(dict(index=args.index, code=code, status=status, proof=proof,
                          masks=len(model.p), arcs=len(model.arcs), rows=len(model.rows), columns=len(model.masks),
                          build_cpu=round(build, 3), cpu=round(time.process_time()-start, 3)), separators=(',', ':')))


if __name__ == '__main__':
    main()
