"""Static projected CNF: contracted edge-kernel paths on eight pinned stars."""

import argparse
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import subprocess
import time

from pysat.solvers import Cadical195

from kernel_cnf import Cnf, neg
from path_growth import ROOT, bits, core_instances, decode, fixed_graph, independent_path_max, neighbors, pairs, read_profiles


def disjunction(formula, literals):
    if any(literal is True for literal in literals):
        return True
    terms = [literal for literal in literals if literal is not False]
    if len(terms) <= 1:
        return terms[0] if terms else False
    out = formula.new()
    for term in terms:
        formula.add(-term, out)
    formula.add(-out, *terms)
    return out


def make(profile, degree, cap, cycle=False, eager=True, exact=False, panel=None, square_range=None, packing=False):
    graph = fixed_graph(profile, cycle)
    order = len(graph)
    fixed = {(src, dst): bool(graph[src] >> dst & 1) for src, dst in pairs(range(order))
             if src < 8 or graph[src] & graph[dst]}
    if panel is not None:
        rows = [vertex for vertex in range(8, order) if graph[vertex] == 1]
        cols = [vertex for vertex in range(8, order) if graph[vertex] == 16]
        assert len(rows) == len(cols) == degree - 4
        for ri, src in enumerate(rows):
            for ci, dst in enumerate(cols):
                fixed[tuple(sorted((src, dst)))] = (ri, ci + len(rows)) in panel
    formula = Cnf(order, fixed)
    for vertex in range(order):
        formula.cardinality([formula.edge(vertex, other) for other in range(order) if other != vertex], degree, degree)
    for anchor in range(8):
        hood = list(bits(graph[anchor]))
        non = [vertex for vertex in range(order) if vertex != anchor and vertex not in hood]
        for vertex in non:
            formula.cardinality([formula.edge(vertex, pivot) for pivot in hood], 1, 3)
        high = {}
        square_terms = {center: [] for center in hood}
        if exact and cap == 6 or square_range is not None:
            for first, second in pairs(hood):
                common = [formula.conjunction(formula.edge(first, vertex), formula.edge(second, vertex)) for vertex in non]
                flags = formula.thresholds(common, 2)
                high[first, second] = flags[1]
                for point in (first, second):
                    square_terms[point].extend(flags)
        if square_range is not None:
            for terms in square_terms.values():
                formula.cardinality(terms, *square_range)
        trip = {}
        for triple in combinations(hood, 3):
            terms = []
            for vertex in non:
                lits = [formula.edge(vertex, pivot) for pivot in triple]
                if any(lit is False for lit in lits):
                    continue
                terms.append(formula.conjunction(formula.conjunction(lits[0], lits[1]), lits[2]))
            trip[triple] = disjunction(formula, terms)
        if eager:
            formula.cardinality(list(trip.values()), max(0, degree * (degree - 1) - 2 * len(non)), len(trip))
        if packing:
            formula.cardinality(list(trip.values()), 0, degree * (degree - 1) // 5)
            for center, mid, left, right in permutations(hood, 4):
                edge = lambda first, second: high[tuple(sorted((first, second)))]
                key = lambda first, second: trip[tuple(sorted((center, first, second)))]
                formula.add(neg(key(mid, left)), neg(key(mid, right)), neg(edge(center, right)), edge(left, right))
        for center in hood:
            rest = sorted(set(hood) - {center})
            conn = {(first, last): trip[tuple(sorted((center, first, last)))] for first, last in pairs(rest)}
            if cap == 6:
                for triple in combinations(rest, 3):
                    formula.add(*(neg(conn[edge]) for edge in pairs(triple)))
                    if exact:
                        for mid in triple:
                            first, last = sorted(set(triple) - {mid})
                            formula.add(neg(conn[tuple(sorted((first, mid)))]), neg(conn[tuple(sorted((last, mid)))]),
                                        neg(high[tuple(sorted((center, first)))]), neg(high[tuple(sorted((center, last)))]))
            size = cap // 2 + 1
            for path in permutations(rest, size):
                if path[0] < path[-1]:
                    formula.add(*(neg(conn[tuple(sorted(edge))]) for edge in zip(path, path[1:])))
    if exact:
        for triple in combinations(range(8, order), 3):
            formula.add(*(neg(formula.edge(*edge)) for edge in pairs(triple)))
        singleton = [[] for vertex in range(order)]
        for first, second in pairs(range(order) if packing else range(8, order)):
            paths = [formula.conjunction(formula.edge(first, vertex), formula.edge(second, vertex))
                     for vertex in range(order) if vertex not in (first, second)]
            flags = formula.thresholds(paths, 4)
            formula.add(neg(flags[3]))
            formula.add(formula.edge(first, second), flags[0])
            if packing:
                term = formula.conjunction(neg(formula.edge(first, second)), neg(flags[1]))
                for vertex in (first, second):
                    singleton[vertex].append(term)
        if packing:
            for terms in singleton:
                formula.cardinality(terms, 0, degree * (degree - 1) // 5 - degree * (degree - 1) + 2 * (order - degree - 1))
    return formula


def control(exact, packing=False):
    seen = set()
    counts = Counter()
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex]), vertex))
            profile = Counter(sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex]) for vertex in outer)
            key = tuple(sorted(profile.items()))
            if key in seen:
                continue
            seen.add(key)
            order = core + outer
            for cap in (6, 8):
                expected = True
                for anchor in core:
                    for center in adj[anchor]:
                        half = adj[anchor] - {center}
                        other = adj[center] - {anchor}
                        links = {pivot: {terminal for terminal in half - {pivot} if adj[pivot] & adj[terminal] & other} for pivot in half}
                        walks = [(pivot,) for pivot in half]
                        for _ in range(cap // 2):
                            walks = [path + (terminal,) for path in walks for terminal in links[path[-1]] - set(path)]
                        if walks:
                            expected = False
                        if cap == 6 and any(links[first] & links[last] for first in half for last in links[first]):
                            expected = False
                        if exact and cap == 6:
                            kernel = half | other
                            walks = [(vertex,) for vertex in kernel]
                            for _ in range(6):
                                walks = [path + (terminal,) for path in walks for terminal in (adj[path[-1]] & kernel) - set(path)]
                            expected &= not walks
                packed = packing and cap == 6
                if packed:
                    for anchor in core:
                        hood = adj[anchor]
                        supports = [row & hood for vertex, row in enumerate(adj) if vertex != anchor and vertex not in hood]
                        triples = {frozenset(mask) for mask in supports if len(mask) == 3}
                        expected &= len(triples) <= 6
                        for center, mid, left, right in permutations(hood, 4):
                            if frozenset((center, mid, left)) in triples and frozenset((center, mid, right)) in triples and len(adj[center] & adj[right]) == 3:
                                expected &= len(adj[left] & adj[right]) == 3
                    expected &= all(sum(len(row & other) == 1 for other in adj) <= 6 for row in adj)
                formula = make(profile, 6, cap, cycle, exact=exact, square_range=(0, 13) if packed else None, packing=packed)
                pins = [formula.edge(src, dst, simplify=False) * (1 if order[dst] in adj[order[src]] else -1) for src, dst in pairs(range(22))]
                with Cadical195(bootstrap_with=formula.clauses) as solver:
                    assert solver.solve(assumptions=pins) == expected
                counts[cap, expected] += 1
    assert counts[8, True] == len(seen) and counts[6, False]
    print('PASS forced exact anchored-link truth table on C22 input:', dict(counts), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--index', type=int)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--exact', action='store_true')
    parser.add_argument('--packing', action='store_true')
    args = parser.parse_args()
    if args.index is None:
        control(args.exact or args.packing, args.packing)
    else:
        formula = make(list(read_profiles(args.source))[args.index], 9, 6, exact=args.exact or args.packing,
                       square_range=(0, 13) if args.packing else None, packing=args.packing)
        formula.write(args.out)
        print(args.index, formula.nvars, len(formula.clauses), flush=True)
