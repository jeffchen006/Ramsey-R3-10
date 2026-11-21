#!/usr/bin/env python3
"""Complete a fixed induced X by selecting unordered attachment neighborhoods.

Outer vertices with equal open neighborhoods in the fixed outer graph P are
one type. A Boolean selects a distinct independent attachment set for a type;
the multiplicity of that type is imposed as a cardinality equality. Repeated
sets of a type would give two nonadjacent twins of degree d, impossible if
d + 2 >= k. At each model, separate exact Ramsey rows and optional codegree rows.
"""

import argparse
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def independent(neighbors, available, limit):
    yield 0
    if limit <= 0:
        return
    while available:
        bit = available & -available
        available ^= bit
        for sub in independent(neighbors, available & ~neighbors[bit.bit_length() - 1], limit - 1):
            yield bit | sub


class Completion:
    def __init__(self, inner, outer, degree, forbidden, codegree, mtf, r7, side_pairs, fixed_sides):
        if degree + 2 < forbidden:
            raise ValueError('cannot exclude repeated attachments')
        if list(inner) != list(range(len(inner))) or list(outer) != list(range(len(outer))):
            raise ValueError('nonconsecutive or unsorted vertex labels')
        if any(nx.triangles(inner).values()) or any(nx.triangles(outer).values()):
            raise ValueError('fixed graph is not triangle-free')
        self.inner, self.outer, self.degree, self.forbidden = inner, outer, degree, forbidden
        self.codegree, self.mtf, self.r7 = codegree, mtf, r7
        self.inner_masks = [sum(1 << adj for adj in inner[node]) for node in inner]
        outer_masks = [sum(1 << adj for adj in outer[node]) for node in outer]
        self.groups = tuple(dict.fromkeys(outer_masks))
        self.vertex_group = [self.groups.index(mask) for mask in outer_masks]
        self.counts = Counter(outer_masks)
        self.qadj = [sum(1 << idx for idx in set(self.vertex_group[v] for v in indices(mask)))
                     for mask in self.groups]
        self.qsets = []
        for choice in independent(self.qadj, (1 << len(self.groups)) - 1, len(self.groups)):
            selected = tuple(indices(choice))
            if not all(choice & (1 << idx) or choice & mask for idx, mask in enumerate(self.qadj)):
                continue
            self.qsets.append((selected, sum(self.counts[self.groups[idx]] for idx in selected)))
        self.free = (1 << len(inner)) - 1
        self.independent = [[] for _ in range(forbidden + 1)]
        for mask in independent(self.inner_masks, self.free, forbidden):
            self.independent[mask.bit_count()].append(mask)
        self.candidates = []
        self.side_pairs = side_pairs
        self.pool = IDPool()
        self.stats = Counter()
        side_types = [group for group in self.groups if self.counts[group] == 2 and group.bit_count() == 3]
        if fixed_sides is not None and len(side_types) != 2:
            raise ValueError('fixed sides require two pairs of false twins of outer degree three')
        fixed = dict(zip(side_types, (fixed_sides[:2], fixed_sides[2:]), strict=True)) if fixed_sides else {}
        for group in self.groups:
            need = degree - group.bit_count()
            if need < 0 or need >= len(self.independent):
                raise ValueError('unsupported outer degree deficit')
            options = self.independent[need]
            if group in fixed:
                selected = set(fixed[group])
                if len(selected) != 2 or not selected <= set(options):
                    raise ValueError('invalid fixed attachment')
                options = [option for option in options if option in selected]
            self.candidates.append([(self.pool.id((group, mask)), mask)
                                    for mask in options])
        self.candidate_vars = self.pool.top

    def add_upper(self, solver, literals, bound):
        if bound < 0:
            solver.add_clause([])
        elif bound < len(literals):
            encoded = CardEnc.atmost(literals, bound, vpool=self.pool, encoding=EncType.seqcounter)
            solver.append_formula(encoded.clauses)

    def add_lower(self, solver, literals, bound):
        if bound > len(literals):
            solver.add_clause([])
        elif bound > 0:
            encoded = CardEnc.atleast(literals, bound, vpool=self.pool, encoding=EncType.seqcounter)
            solver.append_formula(encoded.clauses)

    def require_count(self, solver, literals, count):
        self.add_upper(solver, literals, count)
        self.add_lower(solver, literals, count)

    def fixed_pair_conflict(self, idx, first, jdx, second):
        outer_first, outer_second = self.groups[idx], self.groups[jdx]
        adjacent = self.qadj[idx] & (1 << jdx)
        if adjacent:
            return bool(first & second)
        joint = (outer_first & outer_second).bit_count() + (first & second).bit_count()
        if (self.mtf and joint == 0) or (self.codegree is not None and joint > self.codegree):
            return True
        if self.r7 and joint == 7 and outer_first == outer_second:
            return any(second & ~first & ~self.inner_masks[vertex] for vertex in indices(first & ~second))
        return False

    def initialize(self, solver):
        if self.independent[self.forbidden]:
            solver.add_clause([])
        for group, candidates in zip(self.groups, self.candidates):
            self.require_count(solver, [var for var, _ in candidates], self.counts[group])
        for vertex, inner in enumerate(self.inner_masks):
            bit = 1 << vertex
            members = [[var for var, mask in group if mask & bit] for group in self.candidates]
            hubs = [self.pool.id(('hub', idx, vertex)) for idx in range(len(self.groups))]
            for hub, literals in zip(hubs, members, strict=True):
                for literal in literals:
                    solver.add_clause([-literal, hub])
                solver.add_clause([-hub, *literals])
            self.require_count(solver, [var for group in members for var in group],
                               self.degree - inner.bit_count())
            for idx, mask in enumerate(self.qadj):
                for jdx in indices(mask):
                    if jdx < idx:
                        solver.add_clause([-hubs[idx], -hubs[jdx]])
            if self.mtf:
                for idx, candidates in enumerate(self.candidates):
                    support = [hubs[jdx] for jdx in indices(self.qadj[idx])]
                    for var, mask in candidates:
                        if not (bit | inner) & mask:
                            solver.add_clause([-var, *support])
        for idx, left in enumerate(self.candidates):
            for jdx in range(idx + 1):
                if self.qadj[idx] & (1 << jdx):
                    continue
                if jdx == idx:
                    count = self.counts[self.groups[idx]]
                    if count == 1:
                        continue
                    if count == 2:
                        if self.side_pairs is not None and self.groups[idx].bit_count() == 3:
                            partners = {mask: [] for _, mask in left}
                            variables = {mask: var for var, mask in left}
                            for first, second in self.side_pairs:
                                partners[first].append(variables[second])
                                partners[second].append(variables[first])
                            for var, mask in left:
                                solver.add_clause([-var, *partners[mask]])
                            self.stats['filtered_partner_clauses'] += len(left)
                        else:
                            for var, mask in left:
                                solver.add_clause([-var, *(peer for peer, candidate in left if peer != var
                                    and not self.fixed_pair_conflict(idx, mask, idx, candidate))])
                            self.stats['partner_clauses'] += len(left)
                        continue
                for first_pos, (first_var, first) in enumerate(left):
                    right = self.candidates[jdx]
                    if jdx == idx:
                        right = right[:first_pos]
                    for second_var, second in right:
                        if self.fixed_pair_conflict(idx, first, jdx, second):
                            solver.add_clause([-first_var, -second_var])
                            self.stats['pair_conflicts'] += 1
        for first, second in itertools.combinations(range(len(self.inner)), 2):
            nm_first, nm_second = self.inner_masks[first], self.inner_masks[second]
            if nm_first & (1 << second):
                continue
            joint = (nm_first & nm_second).bit_count()
            both = (1 << first) | (1 << second)
            support = [var for group in self.candidates for var, mask in group if mask & both == both]
            if self.mtf and joint == 0:
                self.add_lower(solver, support, 1)
            if self.codegree is not None:
                self.add_upper(solver, support, self.codegree - joint)

    def ramsey_cuts(self, picked):
        for size in range(self.forbidden - 1, -1, -1):
            upper = self.forbidden - 1 - size
            for subset in self.independent[size]:
                for group_ids, group_size in self.qsets:
                    if group_size <= upper:
                        continue
                    if sum(not subset & mask for idx in group_ids for _, mask in picked[idx]) > upper:
                        yield ([var for idx in group_ids for var, mask in self.candidates[idx]
                                if not subset & mask], upper)

    def cross_cuts(self, picked):
        if self.codegree is None:
            return
        for vertex, inner in enumerate(self.inner_masks):
            bit = 1 << vertex
            for idx, selected in enumerate(picked):
                adjacent_types = tuple(indices(self.qadj[idx]))
                joint = sum(bool(mask & bit) for jdx in adjacent_types for _, mask in picked[jdx])
                for var, mask in selected:
                    bound = self.codegree - (mask & inner).bit_count()
                    if joint > bound:
                        support = [peer for jdx in adjacent_types for peer, candidate in self.candidates[jdx]
                                   if candidate & bit]
                        yield ([*support, var], bound + 1, var, bound)

    def graph(self, picked):
        result = nx.disjoint_union(self.inner, self.outer)
        for idx, selected in enumerate(picked):
            outer_vertices = [node for node, kind in enumerate(self.vertex_group) if kind == idx]
            for node, (_, mask) in zip(outer_vertices, selected, strict=True):
                result.add_edges_from((vertex, len(self.inner) + node) for vertex in indices(mask))
        return result

    def run(self, solver_name, batch):
        print(json.dumps({'independent_counts': list(map(len, self.independent)),
                          'candidates': list(map(len, self.candidates)), 'outer_maximal_sets': self.qsets}), flush=True)
        start = time.process_time()
        with Solver(name=solver_name) as solver:
            self.initialize(solver)
            print(f'initialized cpu={time.process_time()-start:.3f}, vars={self.pool.top}, {self.stats}', flush=True)
            while solver.solve():
                self.stats['solve_models'] += 1
                positive = {lit for lit in solver.get_model() if 0 < lit <= self.candidate_vars}
                picked = [[(var, mask) for var, mask in group if var in positive] for group in self.candidates]
                cross = list(self.cross_cuts(picked))
                for augmented, rhs, switch, bound in cross:
                    if bound < 0:
                        solver.add_clause([-switch])
                    else:
                        rows = CardEnc.atmost(augmented[:-1], rhs - 1, vpool=self.pool,
                                              encoding=EncType.seqcounter)
                        for row in rows.clauses:
                            solver.add_clause([-switch, *row])
                    self.stats['cross_cuts'] += 1
                cuts = list(itertools.islice(self.ramsey_cuts(picked), batch))
                for literals, bound in cuts:
                    self.add_upper(solver, literals, bound)
                    self.stats['ramsey_cuts'] += 1
                if not cuts and not cross:
                    print(f'SAT cpu={time.process_time()-start:.3f}: {self.stats}', flush=True)
                    return self.graph(picked)
                if self.stats['solve_models'] % 100 == 0:
                    print(f'running cpu={time.process_time()-start:.3f}: {self.stats}', flush=True)
        print(f'UNSAT cpu={time.process_time()-start:.3f}: {self.stats}', flush=True)
        return None


def control(source, index, want_cd):
    full = nx.from_graph6_bytes(source.read_bytes().splitlines()[index])
    for first, second in nx.non_edges(full):
        if len(set(full[first]) & set(full[second])) == want_cd:
            out = {first, second, *full[first], *full[second]}
            inner = sorted(set(full) - out)
            outer = sorted(out)
            return (nx.convert_node_labels_to_integers(full.subgraph(inner), ordering='sorted'),
                    nx.convert_node_labels_to_integers(full.subgraph(outer), ordering='sorted'))
    raise ValueError('no such anchor pair')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--control-cd', type=int)
    parser.add_argument('--degree', type=int, default=9)
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--codegree', type=int, default=7)
    parser.add_argument('--solver', default='cadical300')
    parser.add_argument('--batch', type=int, default=32)
    parser.add_argument('--mtf', action='store_true')
    sides = parser.add_mutually_exclusive_group()
    sides.add_argument('--side-filter', type=Path)
    sides.add_argument('--fixed-sides', nargs=4, type=int)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.control_cd is not None:
        inner, outer = control(args.source, args.index, args.control_cd)
    else:
        inner = nx.from_graph6_bytes(args.source.read_bytes().splitlines()[args.index])
        outer = nx.empty_graph(13)
        outer.add_edges_from((anchor, vertex) for anchor in (0, 1) for vertex in range(2, 9))
        outer.add_edges_from(((0, 9), (0, 10), (1, 11), (1, 12)))
        outer.add_edges_from(itertools.product((9, 10), (11, 12)))
    print(f'inner={len(inner)} outer={len(outer)}', flush=True)
    side_pairs = json.loads(args.side_filter.read_text())['pairs'] if args.side_filter else None
    result = Completion(inner, outer, args.degree, args.k, args.codegree, args.mtf,
                        args.control_cd is None, side_pairs, args.fixed_sides).run(args.solver, args.batch)
    if result is not None:
        nx.write_graph6(result, args.out, header=False)


if __name__ == '__main__':
    main()
