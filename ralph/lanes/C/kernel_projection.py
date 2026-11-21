"""Project regular triangle-free extensions of a rooted edge to mask counts."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import sys
import time


MAX_ORDER = (0, 2, 5, 8, 13, 17, 22, 27, 35)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def decode(text):
    text = text.strip()
    size = ord(text[0]) - 63
    if not 0 <= size <= 62 or len(text) != 1 + (size * (size - 1) // 2 + 5) // 6:
        raise ValueError(f"invalid short graph6: {text}")
    adj = [0] * size
    data = (ord(char) - 63 for char in text[1:])
    stream = (block >> shift & 1 for block in data for shift in range(5, -1, -1))
    for right in range(size):
        for left in range(right):
            if next(stream):
                adj[left] |= 1 << right
                adj[right] |= 1 << left
    return adj


def encode(adj):
    data = [adj[right] >> left & 1 for right in range(len(adj)) for left in range(right)]
    data.extend([0] * (-len(data) % 6))
    return chr(63 + len(adj)) + ''.join(
        chr(63 + sum(data[start + ind] << (5 - ind) for ind in range(6)))
        for start in range(0, len(data), 6)
    )


def independent_masks(adj, allowed):
    yield 0
    while allowed:
        low = allowed & -allowed
        allowed ^= low
        for rest in independent_masks(adj, allowed & ~adj[low.bit_length() - 1]):
            yield low | rest


def by_edge(adj, left, right):
    side_a = list(bits(adj[left] & ~(1 << right)))
    side_b = list(bits(adj[right] & ~(1 << left)))
    kernel = side_a + side_b
    kernel_set = set(kernel) | {left, right}
    small = [sum(1 << j for j, y in enumerate(kernel) if adj[x] >> y & 1) for x in kernel]
    counts = Counter(sum(1 << j for j, y in enumerate(kernel) if adj[x] >> y & 1)
                     for x in range(len(adj)) if x not in kernel_set)
    return small, counts


class Projection:
    def __init__(self, kernel, order, degree, cap, depth=3, strong=False, min_edge=False):
        width = 2 * (degree - 1)
        if len(kernel) != width:
            raise ValueError(f"expected bipartite kernel on {width} vertices")
        side_a = (1 << (degree - 1)) - 1
        full = (1 << width) - 1
        side_b = full ^ side_a
        if any(adj & (side_a if i < degree - 1 else side_b) for i, adj in enumerate(kernel)):
            raise ValueError("kernel graph6 must list the two bipartition classes in order")
        roots = (1 << width) | (1 << (width + 1))
        adj = [mask | (1 << (width + (i >= degree - 1))) for i, mask in enumerate(kernel)]
        adj += [side_a | (1 << (width + 1)), side_b | (1 << width)]
        indeps = list(independent_masks(adj, full | roots))
        if any(mask.bit_count() > degree for mask in indeps):
            self.masks = []
            self.rows = [((), -1, "alpha-kernel")]
            return
        full_indep = [mask for mask in indeps if mask.bit_count() == degree]
        self.masks = [mask for mask in indeps if not mask & roots and
                      1 <= (mask & side_a).bit_count() <= cap and
                      1 <= (mask & side_b).bit_count() <= cap and
                      all(mask & indep for indep in full_indep)]
        idx = {mask: i for i, mask in enumerate(self.masks)}

        def subcols(allowed):
            if allowed.bit_count() >= len(self.masks).bit_length():
                return tuple(i for i, mask in enumerate(self.masks) if mask & ~allowed == 0)
            result = []
            submask = allowed
            while submask:
                col = idx.get(submask)
                if col is not None:
                    result.append(col)
                submask = (submask - 1) & allowed
            return tuple(sorted(result))

        self.rows = []

        def add(cols, bound, name, sign=1):
            if cols or bound < 0:
                self.rows.append((tuple((col, sign) for col in cols), bound, name))

        allcols = tuple(range(len(self.masks)))
        size_x = order - 2 * degree
        add(allcols, size_x, 'order+')
        add(allcols, -size_x, 'order-', -1)
        for vertex in range(width):
            cols = tuple(i for i, mask in enumerate(self.masks) if mask >> vertex & 1)
            deficit = degree - adj[vertex].bit_count()
            add(cols, deficit, f'deg+:{vertex}')
            add(cols, -deficit, f'deg-:{vertex}', -1)
            side = side_a if side_a >> vertex & 1 else side_b
            private = tuple(i for i, mask in enumerate(self.masks) if mask & side == 1 << vertex)
            add(private, 1, f'private:{vertex}')
        for left, right in itertools.combinations(range(width), 2):
            fixed = (adj[left] & adj[right]).bit_count()
            if adj[left] >> right & 1:
                continue
            both = (1 << left) | (1 << right)
            cols = tuple(i for i, mask in enumerate(self.masks) if mask & both == both)
            add(cols, cap - fixed, f'codeg+:{left}:{right}')
            add(cols, fixed - 1, f'codeg-:{left}:{right}', -1)
        for indep in indeps:
            need = degree - indep.bit_count()
            if not 1 <= need <= depth:
                continue
            residual = (full | roots) ^ indep
            for vertex in bits(indep):
                residual &= ~adj[vertex]
            cols = subcols(full & ~indep)
            bound = MAX_ORDER[need] - residual.bit_count()
            add(cols, bound, f'ramsey:{indep}')
            for vertex in bits((full & ~indep) if strong else (residual & full)):
                fixed_degree = (adj[vertex] & residual).bit_count() if residual >> vertex & 1 else 0
                bound = need - fixed_degree
                seen = tuple(col for col in cols if self.masks[col] >> vertex & 1)
                add(seen, bound, f'star:{indep}:{vertex}')
        if strong:
            supersets = defaultdict(list)
            for col, mask in enumerate(self.masks):
                for subset in itertools.combinations(bits(mask), cap + 1):
                    supersets[subset].append(col)
            for subset, cols in sorted(supersets.items()):
                add(cols, 1, f'shared:{subset}')
        if min_edge:
            total = sum(mask.bit_count() for mask in kernel) // 2
            for vertex in range(width):
                side = side_a if side_a >> vertex & 1 else side_b
                fixed = sum(kernel[inner].bit_count() for inner in bits(kernel[vertex]))
                terms = tuple((col, 1 - (mask & side).bit_count()) for col, mask in enumerate(self.masks)
                              if mask >> vertex & 1 and (mask & side).bit_count() > 1)
                self.rows.append((terms, fixed - total, f'min-edge:{vertex}'))

    def replay(self, counts):
        if counts.keys() - set(self.masks):
            raise AssertionError("outside mask was omitted")
        for terms, bound, name in self.rows:
            lhs = sum(coeff * counts[self.masks[col]] for col, coeff in terms)
            if lhs > bound:
                raise AssertionError((name, lhs, bound))

    def check(self, cert):
        totals = [0] * len(self.masks)
        rhs = 0
        if not isinstance(cert, list):
            raise ValueError("not a certificate list")
        for row, weight in cert:
            if type(row) is not int or type(weight) is not int or weight <= 0 or not 0 <= row < len(self.rows):
                raise ValueError(f"invalid multiplier: {row}, {weight}")
            terms, bound, _ = self.rows[row]
            rhs += weight * bound
            for col, coeff in terms:
                totals[col] += weight * coeff
        if rhs >= 0 or any(total < 0 for total in totals):
            raise ValueError("Farkas combination is not a contradiction")

    def solve(self):
        import numpy as np
        from scipy.optimize import linprog
        from scipy.sparse import coo_matrix

        col_ids, row_ids, coeffs = [], [], []
        bounds = []
        for row, (terms, bound, _) in enumerate(self.rows):
            if not terms and bound < 0:
                cert = [[row, 1]]
                self.check(cert)
                return 'cert', cert
            row_ids.extend([row] * (len(terms) + 1))
            col_ids.extend(col for col, _ in terms)
            coeffs.extend(coeff for _, coeff in terms)
            col_ids.append(len(self.masks))
            coeffs.append(-1)
            bounds.append(bound)
        if not bounds:
            return 'feasible', None
        mat = coo_matrix((coeffs, (row_ids, col_ids)), shape=(len(self.rows), len(self.masks) + 1)).tocsc()
        obj = np.zeros(len(self.masks) + 1)
        obj[-1] = 1
        result = linprog(obj, A_ub=mat, b_ub=bounds, method='highs',
                         options={'time_limit': 15.0})
        if not result.success:
            return f'unknown-{result.status}', None
        if result.fun < 1e-8:
            return 'feasible', None
        for denominator in (32, 128, 1024, 8192, 65536):
            weights = [(row, Fraction(float(-val)).limit_denominator(denominator))
                       for row, val in enumerate(result.ineqlin.marginals) if val < -1e-10]
            lcm = math.lcm(*(weight.denominator for _, weight in weights))
            cert = [[row, int(weight * lcm)] for row, weight in weights if weight]
            try:
                self.check(cert)
            except ValueError:
                continue
            return 'cert', cert
        return 'infeas-unchecked', None


def calibration(small_path, depth, strong, min_edge):
    c35 = [sum(1 << ((vertex + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16))
           for vertex in range(35)]
    c5 = [sum(1 << ((vertex + step) % 5) for step in (1, -1)) for vertex in range(5)]
    datasets = [("C5", [c5], 2, 1), ("C35", [c35], 8, 4),
                ("reg6_22", [decode(line) for line in Path(small_path).read_text().splitlines()], 6, 4)]
    for name, graphs, degree, cap in datasets:
        edges = 0
        distinct = 0
        for adj in graphs:
            assert all(neighbors.bit_count() == degree for neighbors in adj)
            examples = defaultdict(list)
            for left, neighbors in enumerate(adj):
                for right in bits(neighbors):
                    if right <= left:
                        continue
                    kernel, counts = by_edge(adj, left, right)
                    examples[tuple(kernel)].append(counts)
            minimum = min(sum(mask.bit_count() for mask in kernel) for kernel in examples)
            for kernel, instances in examples.items():
                if min_edge and sum(mask.bit_count() for mask in kernel) != minimum:
                    continue
                proj = Projection(kernel, len(adj), degree, cap, depth, strong, min_edge)
                for counts in instances:
                    proj.replay(counts)
                distinct += 1
                edges += len(instances)
        print(name, f'{len(graphs)} graphs, replayed {edges} edge projections ({distinct} per-graph labelled kernels)')
    result = Projection([0, 0], 6, 2, 1, depth, strong, min_edge)
    status, cert = result.solve()
    assert status == 'cert'
    result.check(cert)
    print('C6 order/degree negative control: only eligible kernel (empty 1+1) eliminated exactly')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('scan', 'verify', 'calibrate'))
    parser.add_argument('--order', type=int, default=40)
    parser.add_argument('--degree', type=int, default=9)
    parser.add_argument('--cap', type=int, default=3)
    parser.add_argument('--depth', type=int, default=3, choices=range(1, 9))
    parser.add_argument('--strong', action='store_true')
    parser.add_argument('--min-edge', action='store_true')
    parser.add_argument('--small', default='duo/reg6_22.g6')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibration(args.small, args.depth, args.strong, args.min_edge)
        return
    summary = Counter()
    start = time.process_time()
    for line in itertools.islice(sys.stdin, args.limit):
        if args.mode == 'verify':
            item = json.loads(line)
            if item['status'] != 'cert':
                summary[item['status']] += 1
                continue
            graph = item['g6']
        else:
            graph = line.strip().split('\t')[-1]
        proj = Projection(decode(graph), args.order, args.degree, args.cap, args.depth, args.strong, args.min_edge)
        if args.mode == 'scan':
            status, cert = proj.solve()
            item = dict(g6=graph, status=status, cert=cert, columns=len(proj.masks), rows=len(proj.rows))
            print(json.dumps(item, separators=(',', ':')), flush=True)
        else:
            status = item['status']
            proj.check(item['cert'])
        summary[status] += 1
    print(dict(summary), f'cpu {time.process_time()-start:.3f} s', file=sys.stderr)


if __name__ == '__main__':
    main()
