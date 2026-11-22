"""Build the exact two-root lift on fixed shores; see ROUND23_PAIRCUT.md."""

import argparse
from itertools import combinations, permutations, product
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def decode(text):
    size = ord(text[0]) - 63
    values = [ord(char) - 63 for char in text[1:]]
    assert 0 < size < 63 and len(values) == (size * (size - 1) // 2 + 5) // 6
    assert all(0 <= value < 64 for value in values)
    pairs = ((left, right) for right in range(size) for left in range(right))
    edges = [pair for index, pair in enumerate(pairs)
             if values[index // 6] & (32 >> (index % 6))]
    return size, edges


def independent(vertices, edges, size):
    if size == 0:
        yield ()
    elif len(vertices) >= size:
        for index, first in enumerate(vertices[:len(vertices) - size + 1]):
            tail = [second for second in vertices[index + 1:]
                    if (first, second) not in edges]
            for suffix in independent(tail, edges, size - 1):
                yield (first,) + suffix


class Lift:
    def __init__(self, roots, frame_size, frame_edges, stem_size, stem_edges):
        self.frame = tuple(range(frame_size))
        self.stem = tuple(range(frame_size, frame_size + stem_size))
        self.roots = tuple(roots)
        self.wires = tuple(vertex for vertex in self.frame if vertex not in roots)
        self.fixed = set(frame_edges) | {(a + frame_size, b + frame_size) for a, b in stem_edges}
        self.pool, self.formula = IDPool(), CNF()
        self.var = {pair: self.pool.id(pair) for pair in product(self.wires, self.stem)}
        self.known = {vertex: set() for vertex in self.frame + self.stem}
        for left, right in self.fixed:
            self.known[left].add(right)
            self.known[right].add(left)

    def clause(self, *literals):
        self.formula.append(literals)

    def bound(self, literals, lower, upper):
        literals = list(literals)
        if lower > upper or lower > len(literals) or upper < 0:
            self.clause()
            return
        if lower > 0:
            self.formula.extend(CardEnc.atleast(literals, bound=lower, vpool=self.pool,
                                                encoding=EncType.seqcounter).clauses)
        if upper < len(literals):
            self.formula.extend(CardEnc.atmost(literals, bound=upper, vpool=self.pool,
                                               encoding=EncType.seqcounter).clauses)

    def degree(self, vertex, lower, upper):
        fixed = len(self.known[vertex])
        self.bound((lit for edge, lit in self.var.items() if vertex in edge),
                   lower - fixed, upper - fixed)

    def graph_rules(self, alpha, min_stem_indep=0):
        for left, right in self.fixed:
            if self.known[left] & self.known[right]:
                self.clause()
            if right in self.frame:
                if left in self.wires and right in self.wires:
                    for site in self.stem:
                        self.clause(-self.var[left, site], -self.var[right, site])
            elif left in self.stem:
                for site in self.wires:
                    self.clause(-self.var[site, left], -self.var[site, right])

        for count in range(alpha + 2):
            if alpha + 1 - count < min_stem_indep:
                continue
            frame_indep = tuple(independent(self.frame, self.fixed, count))
            if not frame_indep:
                continue
            stem_indep = tuple(independent(self.stem, self.fixed, alpha + 1 - count))
            clauses = {tuple(self.var[row, site] for row in shore if row in self.wires
                             for site in remainder)
                       for shore, remainder in product(frame_indep, stem_indep)}
            for clause in sorted(clauses):
                self.clause(*clause)

        for left, right in combinations(self.frame + self.stem, 2):
            if (left, right) in self.fixed or self.known[left] & self.known[right]:
                continue
            clauses = []
            if (left, right) in self.var:
                clauses.append(self.var[left, right])
            for middle in self.wires + self.stem:
                if middle in (left, right):
                    continue
                factors = []
                for end in (left, right):
                    if end in self.known[middle]:
                        continue
                    edge = tuple(sorted((end, middle)))
                    if edge not in self.var:
                        break
                    factors.append(self.var[edge])
                else:
                    assert factors
                    if len(factors) == 1:
                        clauses.extend(factors)
                    else:
                        marker = self.pool.id(('sat', left, right, middle))
                        clauses.append(marker)
                        for factor in factors:
                            self.clause(-marker, factor)
            self.clause(*clauses)

    def sorted_rows(self, rows):
        for left, right in zip(rows, rows[1:]):
            prefix = self.pool.id(('lex', left, right, -1))
            self.clause(prefix)
            for site in self.stem:
                bit_left, bit_right = self.var[left, site], self.var[right, site]
                self.clause(-prefix, bit_left, -bit_right)
                if site != self.stem[-1]:
                    next_prefix = self.pool.id(('lex', left, right, site))
                    self.clause(-prefix, -bit_left, -bit_right, next_prefix)
                    self.clause(-prefix, bit_left, bit_right, next_prefix)
                    prefix = next_prefix

    def root_columns(self, rows, common):
        for site in self.stem:
            for triple in combinations(rows, 3):
                self.clause(*(-self.var[row, site] for row in triple))
        for first, second in combinations(rows, 2):
            for each, other in combinations(self.stem, 2):
                self.clause(-self.var[first, each], -self.var[second, each],
                            -self.var[first, other], -self.var[second, other])
        for row in common:
            others = [site for site in rows if site != row]
            for each, other in combinations(self.stem, 2):
                for first, second in product(others, repeat=2):
                    self.clause(-self.var[row, each], -self.var[row, other],
                                -self.var[first, each], -self.var[second, other])

    def compact_columns(self, common, private, opposite):
        for left, right in combinations(common, 2):
            for site in self.stem:
                self.clause(-self.var[left, site], -self.var[right, site])

        def double(left, right, site):
            row_left, row_right = self.var[left, site], self.var[right, site]
            marker = self.pool.id(('double', left, right, site))
            self.clause(-marker, row_left)
            self.clause(-marker, row_right)
            self.clause(marker, -row_left, -row_right)
            return marker

        for row in common:
            self.bound((double(row, other, site) for other, site in product(private, self.stem)), 1, 1)
        for left, right in combinations(private, 2):
            if self.known[left] & self.known[right] & set(opposite):
                for site in self.stem:
                    self.clause(-self.var[left, site], -self.var[right, site])
            else:
                self.bound((double(left, right, site) for site in self.stem), 1, 1)
        for site in self.stem:
            self.clause(*(-self.var[row, site] for row in private))

    def general_columns(self, common, private, opposite, degrees):
        rows = common + private
        markers = {}
        for left, right in combinations(rows, 2):
            if self.known[left] & self.known[right] & set(opposite):
                for site in self.stem:
                    self.clause(-self.var[left, site], -self.var[right, site])
                continue
            pair = left, right
            markers[pair] = []
            for site in self.stem:
                bit_left, bit_right = self.var[left, site], self.var[right, site]
                marker = self.pool.id(('general', left, right, site))
                self.clause(-marker, bit_left)
                self.clause(-marker, bit_right)
                self.clause(marker, -bit_left, -bit_right)
                markers[pair].append(marker)
            self.bound(markers[pair], 0, 1)
        for row, degree in zip(common, degrees):
            self.bound((marker for pair, values in markers.items() if row in pair for marker in values),
                       degree - 5, degree - 5)
        for site in self.stem:
            for triple in combinations(rows, 3):
                self.clause(*(-self.var[row, site] for row in triple))
        return [marker for pair, values in markers.items() if common[0] in pair and pair[1] in common
                for marker in values]


MATCHING = 273


def load_cross(code):
    return tuple(tuple((code >> (3 * row + col)) & 1 for col in range(3)) for row in range(3))


def cross_ok(matrix):
    for side in (matrix, tuple(zip(*matrix))):
        if any(sum(line) not in (1, 2) for line in side):
            return False
        doubles = [line for line in side if sum(line) == 2]
        if len(set(doubles)) != len(doubles):
            return False
    return True


def cross_roster():
    actions = list(permutations(range(3)))
    reps = {}
    for code in range(512):
        matrix = load_cross(code)
        if not cross_ok(matrix):
            continue
        orbit = {sum(side[left[row]][right[col]] << (3 * row + col)
                     for row in range(3) for col in range(3))
                 for side, left, right in product((matrix, tuple(zip(*matrix))), actions, actions)}
        rep = min(orbit)
        reps.setdefault(rep, set()).add(code)
        assert all(cross_ok(load_cross(member)) for member in orbit)
    for rep, members in sorted(reps.items(), key=lambda item: (item[0].bit_count(), item[0])):
        print(rep.bit_count(), MATCHING if rep.bit_count() == 3 else rep, len(members), flush=True)


def make_target(stem, cross=MATCHING, min_stem_indep=0, compact=False):
    stem_size, stem_edges = decode(stem)
    assert stem_size == 21 and len(stem_edges) == 48 + cross.bit_count()
    matrix = load_cross(cross)
    assert 0 <= cross < 512 and cross_ok(matrix)
    common, first, second = (2, 3, 4), (5, 6, 7), (8, 9, 10)
    edges = [(0, vertex) for vertex in common + first] + [(1, vertex) for vertex in common + second]
    edges += [(row, col) for row, col in product(first, second) if matrix[row - 5][col - 8]]
    lift = Lift((0, 1), 11, edges, stem_size, stem_edges)
    lift.graph_rules(8, min_stem_indep)
    for vertex in common:
        lift.degree(vertex, 6, 6)
    for vertex in first + second + lift.stem:
        lift.degree(vertex, 6, 8)
    for private, opposite in ((first, second), (second, first)):
        private_need = 18 - cross.bit_count()
        lift.bound((lift.var[row, site] for row, site in product(private, lift.stem)), private_need, private_need)
        if compact:
            lift.compact_columns(common, private, opposite)
        else:
            lift.root_columns(common + private, common)
    lift.sorted_rows(common)
    if cross in (MATCHING, 238):
        lift.sorted_rows(first)
    return lift


def make_common_profile(stem, cross, min_stem_indep, degrees):
    stem_size, stem_edges = decode(stem)
    assert stem_size == 21 and len(stem_edges) == 30 + sum(degrees) + cross.bit_count()
    assert degrees in ((6, 7, 7), (6, 7, 8), (6, 8, 8), (7, 7, 7))
    matrix = load_cross(cross)
    assert 0 <= cross < 512 and cross_ok(matrix)
    common, first, second = (2, 3, 4), (5, 6, 7), (8, 9, 10)
    edges = [(0, vertex) for vertex in common + first] + [(1, vertex) for vertex in common + second]
    edges += [(row, col) for row, col in product(first, second) if matrix[row - 5][col - 8]]
    lift = Lift((0, 1), 11, edges, stem_size, stem_edges)
    lift.graph_rules(8, min_stem_indep)
    if degrees[0] == 6:
        full = set(lift.stem)
        degree = {site: len(lift.known[site]) for site in lift.stem}
        pin, = (sites for sites in independent(lift.stem, lift.fixed, 4)
                if sum(degree[site] for site in sites) == 22
                and set(sites).union(*(lift.known[site] for site in sites)) == full)
        for site in lift.stem:
            lift.clause(lift.var[common[0], site] if site in pin else -lift.var[common[0], site])
    for row, exact in zip(common, degrees):
        lift.degree(row, exact, exact)
    for vertex in first + second + lift.stem:
        limit = 6 if degrees == (7, 7, 7) and vertex in first + second else 8
        lift.degree(vertex, 6, limit)
    for private, opposite in ((first, second), (second, first)):
        private_need = 36 - sum(degrees) - cross.bit_count()
        lift.bound((lift.var[row, site] for row, site in product(private, lift.stem)), private_need, private_need)
        mixed = lift.general_columns(common, private, opposite, degrees)
        if degrees[0] == 6:
            lift.bound(mixed, 1, 1)
    if degrees == (7, 7, 7):
        lift.sorted_rows(common)
    elif degrees[1] == degrees[2]:
        lift.sorted_rows(common[1:])
    if cross in (MATCHING, 238):
        lift.sorted_rows(first)
    return lift


def control():
    old_edges = {tuple(sorted((index, (index + step) % 8)))
                 for index in range(8) for step in (1, 4)}
    old_roots = (0, 3)
    frame = sorted(set(old_roots) | {vert for edge in old_edges if set(edge) & set(old_roots)
                                     for vert in edge})
    remainder = [vert for vert in range(8) if vert not in frame]
    perm = {vert: index for index, vert in enumerate(frame + remainder)}
    expected = {tuple(sorted((perm[left], perm[right]))) for left, right in old_edges}
    size = len(frame)
    frame_edges = {edge for edge in expected if edge[1] < size}
    stem_edges = {(left - size, right - size) for left, right in expected if left >= size}
    for alpha in (2, 3, 4):
        lift = Lift(tuple(perm[root] for root in old_roots), size, frame_edges, len(remainder), stem_edges)
        lift.graph_rules(alpha)
        for vertex in range(8):
            lift.degree(vertex, 3, 3)
        keys = sorted(lift.var)
        count = 0
        with Solver(name='cadical195', bootstrap_with=lift.formula) as solver:
            for bits in product((False, True), repeat=len(keys)):
                edges = lift.fixed | {edge for edge, bit in zip(keys, bits) if bit}
                adj = [{other for other in range(8) if tuple(sorted((vert, other))) in edges}
                       for vert in range(8)]
                no_triangle = not any(adj[left] & adj[right] for left, right in edges)
                saturation = all(right in adj[left] or adj[left] & adj[right]
                                 for left, right in combinations(range(8), 2))
                no_large_indep = all(any(tuple(sorted(pair)) in edges for pair in combinations(test, 2))
                                     for test in combinations(range(8), alpha + 1))
                literal = no_triangle and saturation and no_large_indep and all(len(row) == 3 for row in adj)
                solved = solver.solve(assumptions=[lift.var[edge] if bit else -lift.var[edge]
                                                   for edge, bit in zip(keys, bits)])
                assert literal == solved
                if edges == expected:
                    assert solved == (alpha >= 3)
                count += solved
        print(f'control M8 alpha<={alpha} span={len(keys)} labelled={count} all-agree', flush=True)
        assert (count > 0) == (alpha >= 3)

    common, first, second = (2, 3, 4), (5, 6, 7), (8, 9, 10)
    for cross in (MATCHING, 238):
        matrix = load_cross(cross)
        frame_edges = [(0, vertex) for vertex in common + first] + [(1, vertex) for vertex in common + second]
        frame_edges += [(row, col) for row, col in product(first, second) if matrix[row - 5][col - 8]]
        lift = Lift((0, 1), 11, frame_edges, 21, ())
        nonedges = [(row, col) for row, col in product(first, second) if (row, col) not in frame_edges]
        matched_nonedges = next(choices for choices in combinations(nonedges, 3)
                                if len({row for row, col in choices}) == len({col for row, col in choices}) == 3)
        columns = [(row,) for row in common for _ in range(3)]
        columns += [(row,) + pair for row, pair in zip(common, matched_nonedges)]
        if cross == MATCHING:
            columns += [tuple(row for row in first if row != left) + (right,)
                        for left, right in zip(first, second)]
            columns += [(left,) + tuple(row for row in second if row != right)
                        for left, right in zip(first, second)]
            columns += list(matched_nonedges)
        else:
            columns += [pair for pair in matched_nonedges for _ in range(3)]
        assert len(columns) == len(lift.stem) and not any(
            left in column and right in column for column in columns for left, right in frame_edges)
        for private, opposite, root in ((first, second, 1), (second, first, 0)):
            masks = [set(column) & set(common + private) for column in columns]
            masks += [lift.known[row] - {root} for row in opposite] + [set(common)]
            assert sorted(map(len, masks)) == [1] * 18 + [2] * 6 + [3]
            assert all(masks.count({row}) == 3 for row in common + private)
            assert len({tuple(sorted(mask)) for mask in masks if len(mask) == 2}) == 6
            lift.compact_columns(common, private, opposite)
            marks = lift.general_columns(common, private, opposite, (6, 6, 6))
            lift.bound(marks, 0, 0)
        for wire in common:
            lift.degree(wire, 6, 6)
        for wire in first + second:
            lift.degree(wire, 6, 8)
        witness = [lit if row in columns[site - 11] else -lit for (row, site), lit in lift.var.items()]
        with Solver(name='cadical195', bootstrap_with=lift.formula) as solver:
            assert solver.solve(assumptions=witness)
            extra_common_edge = lift.var[common[1], lift.stem[0]]
            adverse = [extra_common_edge if lit == -extra_common_edge else lit for lit in witness]
            assert not solver.solve(assumptions=adverse)
        print(f'control compact {cross}: two 25-column covers and adverse shared edge', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--cross-roster', action='store_true')
    parser.add_argument('--cross', type=int, default=MATCHING)
    parser.add_argument('--min-stem-indep', type=int, default=0)
    parser.add_argument('--compact', action='store_true')
    parser.add_argument('--one-low', type=str, choices=('677', '678', '688', '777'))
    parser.add_argument('stem', type=Path, nargs='?')
    parser.add_argument('cnf', type=Path, nargs='?')
    args = parser.parse_args()
    if args.control:
        control()
    elif args.cross_roster:
        cross_roster()
    else:
        key, = args.stem.read_text().splitlines()
        if args.one_low:
            lift = make_common_profile(key, args.cross, args.min_stem_indep, tuple(map(int, args.one_low)))
        else:
            lift = make_target(key, args.cross, args.min_stem_indep, args.compact)
        lift.formula.to_file(str(args.cnf))
        print(f'{key} {len(lift.var)} wires {lift.formula.nv} vars {len(lift.formula.clauses)} clauses', flush=True)


if __name__ == '__main__':
    main()
