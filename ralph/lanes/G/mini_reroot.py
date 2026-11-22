#!/usr/bin/env python3
"""Price the exact two-window join inside the fixed pivot's antineighbourhood."""

from argparse import ArgumentParser
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations, islice, product
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from check_root_cover import graph, vertices
from pinned_anchor_window import preclude_triangles, sort_contacts, support_constraints, unpack
from prove_strip_windows import BIN, bounded, verify
from reroot_shell_jobs import EDGE_FLOOR, assigned_roles, unpaired_floor
from root_glue import independent
from strip_completion import Completion


def window_problem(adj, small, large, widths, doubled, slots, floors, unpaired_floor, *,
                   alpha=8, paired_edges=None, sorted_groups=False):
    core = len(adj)
    first, second, common = widths
    pivots = (core, core + 1)
    root = core + 2
    groups = (tuple(range(root + 1, root + 1 + first)), tuple(range(root + 1 + first, root + 1 + first + second)))
    order = groups[1][-1] + 1 + common
    center = (order - 1,) if common else ()
    shell = (*groups[0], *groups[1], *center)
    fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(core), 2)}
    for vertex in range(order):
        if vertex != root:
            fixed[tuple(sorted((vertex, root)))] = vertex in pivots or vertex in small
    fixed[pivots] = False
    for pivot, group, doubles in zip(pivots, groups, doubled, strict=True):
        for vertex in range(order):
            if vertex not in (*pivots, root):
                fixed[tuple(sorted((vertex, pivot)))] = vertex in group or vertex in center
        fixed.update({pair: False for pair in combinations((*group, *center), 2)})
        for vertex, anchor in product((*group, *center), small):
            if vertex in center or not (doubles >> anchor & 1):
                fixed[anchor, vertex] = False
    preclude_triangles(fixed, order)
    problem = Completion(order, fixed)
    problem.triangles()
    get = problem.edgeof
    if sorted_groups:
        for group in groups:
            sort_contacts(problem, group, (*large, *small))
    large_counts = Counter(tuple(vertices(slot)) for slot in slots)
    bounds = {part: (large_counts[part], large_counts[part]) for width in (1, 2)
              for part in combinations(large, width)}
    support_constraints(problem, shell, large, bounds, exact=True)
    for group in groups:
        for vertex in group:
            problem.bound((get(vertex, anchor) for anchor in small), 0, 1)
        for anchor in small:
            problem.bound((get(vertex, anchor) for vertex in group), 0, 1)
        singles = [problem.and_all(-get(vertex, anchor) for anchor in small) for vertex in group]
        problem.bound(singles, 0, 4)
    for index, (pivot, group, minimum) in enumerate(zip(pivots, groups, floors, strict=True)):
        window = (*range(core), pivot, *group)
        for vertex in window:
            problem.bound((get(vertex, peer) for peer in window if vertex != peer), minimum, alpha - 1)
        minimum_edges = EDGE_FLOOR[len(window)] if paired_edges is None else paired_edges[index]
        problem.bound((get(left, right) for left, right in combinations(window, 2)), minimum_edges,
                      (alpha - 1) * len(window) // 2)
    for vertex in range(order):
        problem.bound(problem.incident(vertex), order - 28 if paired_edges is None else 0, alpha)
    problem.bound(problem.edge.values(), unpaired_floor, alpha * order // 2)
    if paired_edges is None:
        parity = -1
        for edge in problem.edge.values():
            if edge == 1:
                parity = -parity
            elif edge != -1:
                swapped = problem.formula.new()
                problem.add((-parity, -edge, -swapped))
                problem.add((-parity, edge, swapped))
                problem.add((parity, -edge, swapped))
                problem.add((parity, edge, -swapped))
                parity = swapped
        problem.add((parity if unpaired_floor % 2 else -parity,))
    return problem


def floors_for(kind, width):
    first, second, _ = width
    if kind.startswith('B.'):
        return 4, (4 if second == 4 else (3 if 'middle' in kind else 2))
    return tuple(max(2, size - 1) for size in (first, second))


def eager_cuts(problem, adj, alpha=8):
    core = len(adj)
    groups = combinations(range(core, problem.order), 3)
    possible = [(shell, [problem.edgeof(*pair) for pair in combinations(shell, 2)]) for shell in groups]
    possible = [(shell, edges) for shell, edges in possible if 1 not in edges]
    cuts = set()
    for chosen in independent(adj, (1 << core) - 1, alpha - 2, alpha - 2):
        for shell, local in possible:
            edges = (*local, *(problem.edgeof(left, right) for left, right in product(chosen, shell)))
            if 1 not in edges:
                cuts.add(tuple(sorted({lit for lit in edges if lit != -1})))
    for clause in sorted(cuts):
        problem.add(clause)
    return len(cuts)


def solve(problem, limit, *, batch=80, alpha=8):
    counter = Counter()
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        while counter['conflicts'] < limit:
            solver.conf_budget(limit - counter['conflicts'])
            answer = solver.solve_limited()
            counter['conflicts'] = solver.accum_stats()['conflicts']
            if answer is None:
                return 'CAP', counter
            if answer is False:
                return 'UNSAT', counter
            counter['models'] += 1
            adj = problem.adjacency(solver.get_model())
            assert graph.triangle_free(adj)
            witnesses = list(islice(independent(adj, (1 << len(adj)) - 1, alpha + 1, alpha + 1), batch))
            if not witnesses:
                assert graph.alpha(adj) <= alpha
                return graph.to_graph6(adj), counter
            for witness in witnesses:
                solver.add_clause(problem.independent_clause(witness))
    return 'CAP', counter


def proof_run(problem, limit, destination, replay):
    cnf, lrat, stored = (Path(f'{destination}{suffix}') for suffix in ('.cnf', '.lrat', '.lrat.gz'))
    problem.formula.write(cnf)
    try:
        if replay:
            if not stored.is_file():
                return ('NO_TRACE',)
            lrat.write_bytes(gzip.decompress(stored.read_bytes()))
        else:
            result = bounded([BIN / 'cadical', '-q', '-n', '--lrat', '--no-binary', '-c', limit, cnf, lrat], 16)
            if result.returncode != 20:
                states = {0: 'CAP', 10: 'RELAXED_SAT', 124: 'TIMEOUT', 137: 'SIGNAL', 152: 'CPU_CAP'}
                assert result.returncode in states, (result.returncode, result.stdout, result.stderr)
                return (states[result.returncode],)
            assert b's UNSATISFIABLE' in result.stdout.splitlines()
        verify(cnf, lrat)
        if not replay:
            stored.write_bytes(gzip.compress(lrat.read_bytes(), compresslevel=1, mtime=0))
        receipt = ('REPLAY' if replay else 'CERT', sha256(cnf.read_bytes()).hexdigest(),
                   sha256(stored.read_bytes()).hexdigest(), stored.stat().st_size)
        return receipt
    finally:
        cnf.unlink(missing_ok=True)
        lrat.unlink(missing_ok=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('cores', type=Path)
    parser.add_argument('shell_map', type=Path)
    parser.add_argument('--type', action='append', required=True)
    parser.add_argument('--count', type=int, default=8)
    parser.add_argument('--limit', type=int, default=2000)
    parser.add_argument('--eager', action='store_true')
    parser.add_argument('--sorted-groups', action='store_true')
    parser.add_argument('--proof-dir', type=Path)
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--shard', nargs=2, type=int, default=(0, 1))
    args = parser.parse_args()
    if args.proof_dir:
        assert args.eager and args.sorted_groups
        args.proof_dir.mkdir(parents=True, exist_ok=True)
    assert not args.replay or args.proof_dir
    wanted = None if args.selection is None else {tuple(row.split()[:3]) for row in args.selection.read_text().splitlines()}
    if wanted is not None:
        assert all(kind in args.type for kind, _, _ in wanted)
    survivors = set()
    for row in args.shell_map.read_text().splitlines():
        kind, key, var, _, _, passed, *_ = row.split()
        if int(passed) and kind in args.type:
            survivors.add((key, var))
    collected = {kind: [] for kind in args.type}
    for row in args.cores.read_text().splitlines():
        _, adj, small, large = unpack(row)
        for kind, key, var, first, second, shared, one, two, slots in assigned_roles(row):
            if kind in collected and (key, var) in survivors and (wanted is None or (kind, key, var) in wanted):
                collected[kind].append((key, var, adj, small, large, (first, second, shared), (one, two), slots))
    if wanted is not None:
        assert sum(map(len, collected.values())) == len(wanted)
    rank, shards = args.shard
    assert 0 <= rank < shards
    for kind, choices in collected.items():
        count = len(choices) if wanted is not None else min(args.count, len(choices))
        for idx in range(rank, count, shards):
            key, var, adj, small, large, width, doubled, slots = choices[idx * len(choices) // count]
            started = process_time()
            problem = window_problem(adj, small, large, width, doubled, slots, floors_for(kind, width),
                                     unpaired_floor(kind), sorted_groups=args.sorted_groups)
            added = eager_cuts(problem, adj) if args.eager else 0
            if args.proof_dir:
                receipt = proof_run(problem, args.limit, args.proof_dir / f'{kind}_{key}_{var}', args.replay)
                print(kind, key, var, *receipt, f'{process_time() - started:.4f}', flush=True)
                continue
            result, stats = solve(problem, args.limit)
            print(kind, key, var, result, stats['conflicts'], stats['models'], added,
                  f'{process_time() - started:.4f}', flush=True)


if __name__ == '__main__':
    main()
