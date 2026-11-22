"""Physically pinned d6/d7 lift with unpinned private cross edges (round 24)."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from pysat.solvers import Solver

from paircut_r23 import Lift, decode, independent


class Floating(Lift):
    def __init__(self, frame_size, stem_size, fixed, possible):
        super().__init__((), frame_size, (), stem_size, ())
        self.var = {edge: self.pool.id(edge) for edge in sorted(possible)}
        self.fixed = set(fixed)
        assert not self.fixed & set(self.var)
        self.sites = self.frame + self.stem
        self.edges = self.fixed | set(self.var)
        for first, last in self.fixed:
            self.known[first].add(last)
            self.known[last].add(first)
        self.possible = {site: set(neighbors) for site, neighbors in self.known.items()}
        for first, last in self.var:
            self.possible[first].add(last)
            self.possible[last].add(first)

    def indicators(self, variables, exact=True):
        terms = tuple(sorted(variables))
        if len(terms) == 1:
            return terms[0]
        marker = self.pool.id(('and', terms))
        for lit in terms:
            self.clause(-marker, lit)
        if exact:
            self.clause(marker, *(-lit for lit in terms))
        return marker

    def graph(self, alpha, min_stem):
        for triple in combinations(self.sites, 3):
            edges = tuple(combinations(triple, 2))
            if all(edge in self.edges for edge in edges):
                self.clause(*(-self.var[edge] for edge in edges if edge in self.var))
        for count in range(alpha + 2 - min_stem):
            shores = tuple(independent(self.frame, self.fixed, count))
            if not shores:
                continue
            stems = tuple(independent(self.stem, self.fixed, alpha + 1 - count))
            clauses = {tuple(self.var[edge] for edge in combinations(shore + stem, 2) if edge in self.var)
                       for shore, stem in product(shores, stems)
                       if not any((row, site) in self.fixed for row, site in product(shore, stem))}
            for clause in sorted(clauses):
                self.clause(*clause)
        for first, last in combinations(self.sites, 2):
            if (first, last) in self.fixed or self.known[first] & self.known[last]:
                continue
            options = [self.var[first, last]] if (first, last) in self.var else []
            for mid in sorted(self.possible[first] & self.possible[last]):
                edges = [tuple(sorted((end, mid))) for end in (first, last)]
                options.append(self.indicators([self.var[edge] for edge in edges if edge in self.var]))
            self.clause(*options)

    def mask(self, rows, site, chosen):
        terms = []
        for row in rows:
            edge = tuple(sorted((row, site)))
            wanted = row in chosen
            if edge in self.var:
                terms.append(self.var[edge] if wanted else -self.var[edge])
            elif (edge in self.fixed) != wanted:
                return None
        return self.indicators(terms)

    def mask_count(self, rows, sites, chosen, lower, upper):
        terms = [term for site in sites if (term := self.mask(rows, site, chosen)) is not None]
        self.bound(terms, lower, upper)

    def lex_equal_rows(self, rows, sites):
        for left, right in zip(rows, rows[1:]):
            prefix = self.indicators(())
            for site in sites:
                first, last = self.var[left, site], self.var[right, site]
                self.clause(-prefix, -first, last)
                suffix = self.pool.id(('lex-prefix', left, right, site))
                self.clause(-prefix, first, last, suffix)
                self.clause(-prefix, -first, -last, suffix)
                prefix = suffix


def find_rows(stem_text):
    size, edges = decode(stem_text)
    assert size == 20
    adj = [set() for _ in range(size)]
    for first, last in edges:
        adj[first].add(last)
        adj[last].add(first)
    possible = [site for site in range(size) if len(adj[site]) in (4, 5, 6)]
    for chosen in combinations(possible, 4):
        selected = set(chosen)
        if sum(len(adj[site]) for site in chosen) != 20 or any(adj[site] & selected for site in chosen):
            continue
        census = Counter(frozenset(adj[site] & selected) for site in range(size) if site not in selected)
        if all(census[frozenset({site})] == 3 for site in chosen) and all(
                (len(mask) == 1 and count == 3) or (len(mask) == 2 and count == 1)
                for mask, count in census.items()):
            yield chosen


def make_lift(stem_text, marked, min_stem, normalized=False):
    stem_size, stem_edges = decode(stem_text)
    assert stem_size == 20 and marked in tuple(find_rows(stem_text))
    fixed = {(first + 12, last + 12) for first, last in stem_edges}
    common, private, opposite = (2, 3, 4), (5, 6, 7), (8, 9, 10, 11)
    root, partner, low = 0, 1, 2
    fixed |= {(root, site) for site in common + private} | {(partner, site) for site in common + opposite}
    marked = set(site + 12 for site in marked)
    sites = tuple(range(12, 32))
    fixed |= {(low, site) for site in marked}
    variable = set(product(private, opposite))
    variable |= {(row, site) for row, site in product(common[1:] + private + opposite, sites)
                 if row not in private or site not in marked}
    if normalized:
        variable -= set(product((common[2],) + opposite[1:], marked))
    lift = Floating(12, stem_size, fixed, variable)
    lift.graph(8, min_stem)
    for site in lift.sites[3:]:
        lift.degree(site, 6, 8)
    u_rows = common + private
    u_cols = opposite + sites
    if normalized:
        opposite_to_x = 65 - len(stem_edges)
        lift.bound((lit for (row, site), lit in lift.var.items() if row in opposite and site in sites),
                   opposite_to_x, opposite_to_x)
        plain_sites = tuple(site for site in sites if site not in marked)
        lift.lex_equal_rows(private, plain_sites)
        lift.lex_equal_rows(opposite[1:], plain_sites)
    else:
        lift.bound(lift.var.values(), 108 - len(fixed), 108 - len(fixed))
        fixed_weight = sum(len(lift.known[site]) for site in u_rows)
        lift.bound((lit for edge, lit in lift.var.items() if set(edge) & set(u_rows)),
                   39 - fixed_weight, 39 - fixed_weight)
    for site in u_cols:
        fixed_size = len(lift.known[site] & set(u_rows))
        lift.bound((lift.var[tuple(sorted((row, site)))] for row in u_rows
                    if tuple(sorted((row, site))) in lift.var), 1 - fixed_size, 2 - fixed_size)
    for row in u_rows:
        lift.mask_count(u_rows, u_cols, {row}, 3, 3)
    for pair in combinations(u_rows, 2):
        lift.mask_count(u_rows, u_cols, set(pair), 0, 1)
    v_rows = common + opposite
    for row in v_rows:
        lift.mask_count(v_rows, private + sites, {row}, 0, 2)
    lift.bound((lift.var[row, site] for row, site in product(opposite, sorted(marked))
                if (row, site) in lift.var), 1, 1)
    lift.bound((lift.var[row, site] for row, site in product(common[1:], sorted(marked))
                if (row, site) in lift.var), 1, 1)
    for site in sorted(marked):
        for first, last in product(common[1:], opposite):
            if (first, site) in lift.var and (last, site) in lift.var:
                lift.clause(-lift.var[first, site], -lift.var[last, site])
    for row in common[1:]:
        if normalized:
            if row == common[1]:
                lift.degree(row, 7, 8)
            continue
        force = -lift.indicators([-lift.var[row, site] for site in sorted(marked)])
        degree = len(lift.known[row])
        terms = [lit for edge, lit in lift.var.items() if row in edge]
        lift.bound(terms + [-force], 7 - degree, len(terms) + 1)
    return lift


def control():
    original = {tuple(sorted((index, (index + step) % 8)))
                for index in range(8) for step in (1, 4)}
    perm = {vertex: index for index, vertex in enumerate((0, 3, 1, 7, 4, 2, 6, 5))}
    expected = {tuple(sorted((perm[first], perm[last]))) for first, last in original}
    cross = set(product((2, 3), (5, 6))) | {(4, 7), (5, 7), (6, 7), (3, 7)}
    cross |= (expected - cross) & {(2, 7), (6, 7)}
    assert cross & expected and cross - expected and any(last < 7 for _, last in cross)
    fixed = expected - cross
    keys = tuple(sorted(cross))
    for alpha in (2, 3, 4):
        lift = Floating(7, 1, fixed, cross)
        lift.graph(alpha, 0)
        for site in range(8):
            lift.degree(site, 3, 3)
        total = 0
        with Solver(name='cadical195', bootstrap_with=lift.formula) as solver:
            for signs in product((False, True), repeat=len(keys)):
                edges = fixed | {edge for edge, sign in zip(keys, signs) if sign}
                adj = [{other for other in range(8) if tuple(sorted((site, other))) in edges}
                       for site in range(8)]
                literal = (all(len(row) == 3 for row in adj)
                           and all(not adj[left] & adj[right] for left, right in edges)
                           and all(right in adj[left] or adj[left] & adj[right]
                                   for left, right in combinations(range(8), 2))
                           and all(any(right in adj[left] for left, right in combinations(test, 2))
                                   for test in combinations(range(8), alpha + 1)))
                solved = solver.solve(assumptions=[lift.var[edge] if sign else -lift.var[edge]
                                                   for edge, sign in zip(keys, signs)])
                assert solved == literal
                if edges == expected:
                    assert solved == (alpha >= 3)
                total += solved
        assert bool(total) == (alpha >= 3)
        print(f'M8 alpha<={alpha}: {total}/{1 << len(keys)} labelled matches, exact agreement')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--min-stem', type=int, default=6)
    parser.add_argument('--normalized', action='store_true')
    parser.add_argument('marked', nargs='?')
    parser.add_argument('stem', nargs='?', type=Path)
    parser.add_argument('cnf', nargs='?', type=Path)
    args = parser.parse_args()
    if args.control:
        control()
        return
    marked = tuple(map(int, args.marked.split(',')))
    lift = make_lift(args.stem.read_text().strip(), marked, args.min_stem, args.normalized)
    lift.formula.to_file(args.cnf)
    print(f'cnf clauses={len(lift.formula.clauses)} vars={lift.formula.nv} min_stem={args.min_stem}')


if __name__ == '__main__':
    main()
