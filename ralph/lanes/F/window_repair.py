#!/usr/bin/env python3
"""Degree-constrained orbit-window repairs with lazy independent-set budgets."""

import argparse
from contextlib import ExitStack
import ctypes
from itertools import accumulate, combinations
from math import comb
from pathlib import Path
from random import Random
from time import process_time

from pysat.card import CardEnc, ITotalizer
from pysat.solvers import Cadical195

from orbit_extend import image, independent, parse_graph6, perm_for, to_graph6, vertices


class SetEngine:
    def __init__(self, library):
        self.library = ctypes.CDLL(str(library.resolve()))
        self.find = self.library.window_sets
        maskptr = ctypes.POINTER(ctypes.c_uint64)
        self.find.argtypes = (maskptr, ctypes.c_uint64, ctypes.c_int, maskptr, ctypes.c_size_t)
        self.find.restype = ctypes.c_size_t

    def sets(self, graph, size, limit, candidates=None):
        array = ctypes.c_uint64 * len(graph)
        output = (ctypes.c_uint64 * limit)()
        if candidates is None:
            candidates = (1 << len(graph)) - 1
        count = self.find(array(*graph), candidates, size, output, limit)
        return output[:count]


def orbit_representative(mask, permutation):
    changed = image(mask, permutation)
    canonical, copies = mask, 1
    while changed != mask:
        canonical = min(canonical, changed)
        copies += 1
        changed = image(changed, permutation)
    return canonical, copies


class Window:
    def __init__(self, seed, permutation, base_vertices, movable, args):
        self.seed, self.movable, self.args = seed, movable, args
        self.size = len(seed)
        self.base = [0] * self.size
        self.edge_ids, self.orbits, self.clauses = {}, [], []
        self.upper = 0
        for pair in combinations(range(self.size), 2):
            left, right = pair
            if not ((1 << left | 1 << right) & movable):
                symbol = -1 if seed[left] >> right & 1 else 0
                self.edge_ids[pair] = symbol
                if symbol == -1:
                    self.base[left] |= 1 << right
                    self.base[right] |= 1 << left
            elif pair not in self.edge_ids:
                orbit = [pair]
                shifted = tuple(sorted((permutation[left], permutation[right])))
                while shifted != pair:
                    orbit.append(shifted)
                    shifted = tuple(sorted(permutation[vertex] for vertex in shifted))
                self.orbits.append(orbit)
                self.upper += 1
                for edge in orbit:
                    self.edge_ids[edge] = self.upper
        self.phases = [index if seed[orbit[0][0]] >> orbit[0][1] & 1 else -index
                       for index, orbit in enumerate(self.orbits, 1)]
        triangle_clauses = set()
        for triple in combinations(range(self.size), 3):
            literals = {self.edge_ids[pair] for pair in combinations(triple, 2)}
            if 0 not in literals:
                triangle_clauses.add(tuple(-lit for lit in sorted(literals) if lit > 0))
        self.clauses.extend(sorted(triangle_clauses))
        fixed = [vertex for vertex in base_vertices if permutation[vertex] == vertex]
        for vertex in base_vertices:
            incident = self.incident(vertex, range(self.size))
            degree = self.base[vertex].bit_count()
            self.atmost(incident, args.max_degree - degree)
            self.atmost([-lit for lit in incident], len(incident) + degree - args.min_degree)
            if args.attachment is not None and permutation[vertex] != vertex:
                self.atmost(self.incident(vertex, fixed),
                            args.attachment - sum(self.base[vertex] >> other & 1 for other in fixed))
        max_edges = getattr(args, 'max_edges', None)
        if args.min_edges or max_edges is not None:
            fixed_edges = sum(mask.bit_count() for mask in self.base) // 2
            mutable_edges = [index for index, orbit in enumerate(self.orbits, 1) for _ in orbit]
            if args.min_edges:
                self.atmost([-index for index in mutable_edges], len(mutable_edges) + fixed_edges - args.min_edges)
            if max_edges is not None:
                self.atmost(mutable_edges, max_edges - fixed_edges)
        if args.flips is not None:
            self.atmost([-lit for lit in self.phases], args.flips)
        if getattr(args, 'deviation', 0):
            self.atmost(self.phases, len(self.phases) - args.deviation)

    def incident(self, vertex, others):
        symbols = (self.edge_ids[tuple(sorted((vertex, other)))] for other in others if vertex != other)
        return [symbol for symbol in symbols if symbol > 0]

    def atmost(self, literals, bound):
        if bound < 0:
            self.clauses.append(())
        elif bound < len(literals):
            formula = CardEnc.atmost(literals, bound, top_id=self.upper)
            self.upper = max(self.upper, formula.nv)
            self.clauses.extend(formula.clauses)

    def graph(self, model):
        result = self.base[:]
        present = set(model)
        for index, orbit in enumerate(self.orbits, 1):
            if index in present:
                for left, right in orbit:
                    result[left] |= 1 << right
                    result[right] |= 1 << left
        return result

    def disjunction(self, bad):
        return tuple(sorted({self.edge_ids[pair] for pair in combinations(vertices(bad), 2)} - {0}))


def frontier(window, engine, permutation, cap):
    """Collect short rows using few window vertices and an independent frozen side."""
    movable = list(vertices(window.movable))
    outside = ((1 << window.size) - 1) ^ window.movable
    limit = min(window.args.k, len(movable))
    rows = set()
    for count in range(1, limit + 1):
        space = comb(len(movable), count)
        left = cap - len(rows)
        if count > 1 and space > left:
            break
        outer = engine.sets(window.base, window.args.k - count, left // space + 1, outside)
        for offsets in combinations(movable, count):
            inner = sum(1 << vertex for vertex in offsets)
            canonical, _ = orbit_representative(inner, permutation)
            if canonical != inner:
                continue
            for frozen in outer:
                rows.add(window.disjunction(frozen | inner))
                if len(rows) >= cap:
                    return rows
    return rows


def repair(window, initial_bad, frozen_count, permutation, engine, goal):
    args = window.args
    slack = goal - frozen_count
    seen, assumptions = set(), []
    frontier_cap = getattr(args, 'frontier', 0)
    seed_rows = frontier(window, engine, permutation, frontier_cap) if frontier_cap and not slack else set()
    with Cadical195(bootstrap_with=window.clauses) as solver, ExitStack() as allocations:
        if seed_rows:
            solver.append_formula(sorted(seed_rows))
            seen.update(seed_rows)
        counter = None
        solver.set_phases(window.phases)
        added, rounds, conflicts = len(seed_rows), 0, 0
        bad = initial_bad
        top = window.upper
        while True:
            costs = []
            emitted = 0
            if slack:
                for witness in bad:
                    if not (witness & window.movable):
                        continue
                    canonical, weight = orbit_representative(witness, permutation)
                    if canonical in seen:
                        continue
                    clause = window.disjunction(canonical)
                    assert -1 not in clause
                    seen.add(canonical)
                    top += 1
                    solver.add_clause([*clause, top])
                    if weight > slack:
                        solver.add_clause([-top])
                    else:
                        penalty = top
                        costs.append(penalty)
                        for _ in range(weight - 1):
                            top += 1
                            solver.add_clause([-penalty, top])
                            costs.append(top)
                    emitted += 1
                    if emitted == args.batch:
                        break
            else:
                for witness in bad:
                    if not (witness & window.movable):
                        continue
                    clause = window.disjunction(witness)
                    assert -1 not in clause
                    if clause in seen:
                        continue
                    seen.add(clause)
                    solver.add_clause(clause)
                    emitted += 1
                    if emitted == args.batch:
                        break
            if costs:
                if counter is None:
                    counter = allocations.enter_context(ITotalizer(lits=costs, ubound=slack, top_id=top))
                    solver.append_formula(counter.cnf.clauses)
                else:
                    counter.extend(lits=costs, ubound=slack, top_id=top)
                    if counter.nof_new:
                        solver.append_formula(counter.cnf.clauses[-counter.nof_new:])
                top = counter.top_id
                if len(counter.rhs) > slack:
                    assumptions = [-counter.rhs[slack]]
            added += emitted
            if rounds and not emitted:
                raise AssertionError('SAT model did not respect installed independent-set rows')
            remaining = args.conflicts - conflicts
            if remaining <= 0 or rounds == args.rounds:
                return 'cap', None, None, (rounds, conflicts, added)
            solver.conf_budget(remaining)
            solved = solver.solve_limited(assumptions=assumptions)
            conflicts = solver.accum_stats()['conflicts']
            rounds += 1
            if solved is not True:
                return ('unsat' if solved is False else 'cap'), None, None, (rounds, conflicts, added)
            graph = window.graph(solver.get_model())
            limit = max(args.batch + goal + 1, 2 * (goal + 1))
            bad = engine.sets(graph, args.k, limit)
            if len(bad) <= goal:
                return 'model', graph, len(bad), (rounds, conflicts, added)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seed', type=Path)
    parser.add_argument('cycles', help='comma-separated lengths, in order')
    parser.add_argument('--library', type=Path, default=Path('../build/window_sets.so'))
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--min-degree', type=int, default=0)
    parser.add_argument('--max-degree', type=int, default=9)
    parser.add_argument('--min-edges', type=int, default=0)
    parser.add_argument('--max-edges', type=int)
    parser.add_argument('--attachment', type=int)
    parser.add_argument('--flips', type=int)
    parser.add_argument('--deviation', type=int, default=0, help='minimum edited edge orbits')
    parser.add_argument('--width', type=int, default=3)
    parser.add_argument('--goal', type=int, default=0)
    parser.add_argument('--frozen-only', action='store_true', help='require no bad set touching window')
    parser.add_argument('--batch', type=int, default=192)
    parser.add_argument('--frontier', type=int, default=0, help='prefill short rows in zero-active-score windows')
    parser.add_argument('--conflicts', type=int, default=10000)
    parser.add_argument('--rounds', type=int, default=100)
    parser.add_argument('--limit', type=int, default=12)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--shuffle', type=int)
    parser.add_argument('--scan', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cycles = list(map(int, args.cycles.split(',')))
    seed = parse_graph6(args.seed.read_text().strip())
    if sum(cycles) != len(seed) or not 0 < min(cycles) <= max(cycles) or len(seed) > 63:
        parser.error('cycle lengths must be positive and sum to graph order <= 63')
    if not 1 <= args.width <= len(cycles) or not 1 <= args.k <= len(seed):
        parser.error('bad width or independent set size')
    if min(args.goal, args.limit, args.offset, args.frontier, args.deviation) < 0 or min(args.batch, args.conflicts, args.rounds) <= 0:
        parser.error('invalid budget')
    permutation = perm_for(cycles)
    if any(image(seed[vertex], permutation) != seed[permutation[vertex]] for vertex in range(len(seed))):
        parser.error('seed does not have given symmetry')
    if any(not independent(mask, seed) for mask in seed):
        parser.error('seed is not triangle-free')
    base_vertices = [0, *list(accumulate(cycles))[:-1]]
    orbits = [((1 << length) - 1) << base for base, length in zip(base_vertices, cycles)]
    engine = SetEngine(args.library)
    bad = engine.sets(seed, args.k, 1_000_000)
    if not len(bad) < 1_000_000:
        parser.error('seed witness enumeration capped')
    ranked = []
    for chosen in combinations(range(len(cycles)), args.width):
        movable = sum(orbits[index] for index in chosen)
        counts = [(movable & witness).bit_count() for witness in bad]
        frozen = counts.count(0)
        if frozen <= args.goal:
            ranked.append((frozen, -sum(count * count for count in counts), chosen, movable))
    ranked.sort()
    if args.shuffle is not None:
        Random(args.shuffle).shuffle(ranked)
        ranked.sort(key=lambda item: item[0])
    print(f'seed={args.seed} bad={len(bad)} width={args.width} goal={args.goal} '
          f'eligible={len(ranked)} offset={args.offset} limit={args.limit}', flush=True)
    status_counts = {'model': 0, 'cap': 0, 'unsat': 0}
    for index, (frozen, _, chosen, movable) in enumerate(ranked[args.offset:args.offset + args.limit], args.offset):
        goal = frozen if args.frozen_only else args.goal
        if args.scan:
            print(f'index={index} cycles={chosen} size={movable.bit_count()} frozen={frozen}', flush=True)
            continue
        elapsed = process_time()
        window = Window(seed, permutation, base_vertices, movable, args)
        status, graph, count, (rounds, conflicts, clauses) = repair(window, bad, frozen, permutation, engine, goal)
        status_counts[status] += 1
        print(f'index={index} cycles={chosen} size={movable.bit_count()} frozen={frozen} goal={goal} '
              f'{status} rounds={rounds} conflicts={conflicts} rows={clauses} cpu={process_time() - elapsed:.5f}'
              f' vars={len(window.orbits)} baseclauses={len(window.clauses)}', flush=True)
        if graph is None:
            continue
        degrees = [mask.bit_count() for mask in graph]
        edges = sum(degrees) // 2
        assert args.min_degree <= min(degrees) and max(degrees) <= args.max_degree and edges >= args.min_edges
        assert args.max_edges is None or edges <= args.max_edges
        assert all(independent(mask, graph) and image(mask, permutation) == graph[permutation[index]]
                   for index, mask in enumerate(graph))
        assert all(not ((graph[index] ^ seed[index]) & ~movable)
                   for index in vertices(((1 << len(seed)) - 1) & ~movable))
        path = args.output.with_name(f'{args.output.name}.{count}.{index}.g6')
        path.write_text(to_graph6(graph) + '\n')
        print(f'checkpoint={path} bad={count} e={edges} degrees={min(degrees)}..{max(degrees)}', flush=True)
        if count == 0:
            break
    print(f'END {status_counts}', flush=True)


if __name__ == '__main__':
    main()
