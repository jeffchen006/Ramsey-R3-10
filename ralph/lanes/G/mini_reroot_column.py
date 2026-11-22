#!/usr/bin/env python3
"""One mandatory maximal-column addback to the two-window projection."""

from argparse import ArgumentParser
from itertools import combinations, islice
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from check_root_cover import graph, induced, vertices
from mini_reroot import eager_cuts, floors_for, proof_run, window_problem
from pinned_anchor_window import unpack
from reroot_shell_jobs import assigned_roles, unpaired_floor
from root_glue import independent


def add_column(problem, force, forbidden, opposite, choices=(6, 8)):
    old = problem.order
    problem.order += 1
    force, forbidden = frozenset(force), frozenset(forbidden)
    get = problem.edgeof
    for vertex in range(old):
        problem.edge[vertex, old] = 1 if vertex in force else -1 if vertex in forbidden else problem.formula.new()
    for left, right in combinations(range(old), 2):
        problem.add((-get(left, right), -get(left, old), -get(right, old)))
    for x in range(old):
        if get(x, old) != 1:
            problem.add((get(x, old), *(problem.and2(get(x, y), get(y, old)) for y in range(old) if y != x)))
    selector = problem.exact_degree(old, choices)
    if opposite:
        problem.bound((get(left, old) for left in opposite), 0, 1)
        for vertex in opposite:
            problem.add((-get(vertex, old), selector[choices[-1]]))
    return old


def attach_marked(problem, adj, small, large):
    cross, = (anchor for anchor in small if any(adj[anchor] >> opposite & 1 for opposite in large))
    c = len(adj)
    return add_column(problem, (cross,), tuple(v for v in (*small, c, c + 1, c + 2) if v != cross), large)


def lazy(problem, limit, old, recorded):
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        while solver.accum_stats()['conflicts'] < limit:
            solver.conf_budget(limit - solver.accum_stats()['conflicts'])
            answer = solver.solve_limited()
            if answer is not True:
                return ('CAP' if answer is None else 'UNSAT'), solver.accum_stats()['conflicts']
            adj = problem.adjacency(solver.get_model())
            witnesses = list(islice(independent(adj, (1 << old) - 1, 9, 9), 80))
            if not witnesses:
                assert graph.alpha(induced(adj, (1 << old) - 1)) <= 8 and graph.triangle_free(adj)
                if old < len(adj):
                    assert all(adj[-1] >> idx & 1 or row & adj[-1] for idx, row in enumerate(adj[:-1]))
                    assert adj[-1].bit_count() in (6, 8)
                return graph.to_graph6(adj), solver.accum_stats()['conflicts']
            for witness in witnesses:
                recorded.add(tuple(witness))
                solver.add_clause(problem.independent_clause(witness))
        return 'CAP', solver.accum_stats()['conflicts']


def control(source):
    from strip_completion import Completion

    for enc in source.read_text().splitlines():
        original = graph.parse_graph6(enc)
        for left, right in combinations(range(len(original)), 2):
            if not ((original[left] >> right & 1) or original[left] & original[right]):
                original[left] |= 1 << right
                original[right] |= 1 << left
        assert graph.triangle_free(original)
        example = 0
        for pivot in range(len(original)):
            outside = ((1 << len(original)) - 1) & ~(original[pivot] | 1 << pivot)
            old = induced(original, outside)
            for w in vertices(original[pivot]):
                support = tuple(idx for idx, vertex in enumerate(vertices(outside)) if original[w] >> vertex & 1)
                assert len(support) == original[w].bit_count() - 1
                for positive in (True, False):
                    fix = {(left, right): bool(old[left] >> right & 1)
                           for left, right in combinations(range(len(old)), 2)}
                    want = support if positive else support[1:]
                    formula = Completion(len(old), fix)
                    add_column(formula, want, (v for v in range(len(old)) if v not in want), (), (len(want),))
                    with Cadical195(bootstrap_with=formula.formula.clauses) as solver:
                        assert solver.solve() == positive
                example += 1
        print(f'n={len(original)} {example} exact dominating columns plus one-contact deletions', flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('cores', type=Path)
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--limit', type=int, default=6500)
    parser.add_argument('--no-column', action='store_true')
    parser.add_argument('--proof-dir', type=Path)
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--cuts', type=Path)
    parser.add_argument('--learn', action='store_true')
    parser.add_argument('--shard', type=int, nargs=2, default=(0, 1))
    parser.add_argument('--floor-file', type=Path)
    args = parser.parse_args()
    if args.selection is None:
        control(args.cores)
        return
    rank, shards = args.shard
    assert 0 <= rank < shards
    selected = set([tuple(row.split()[:3]) for row in args.selection.read_text().splitlines()][rank::shards])
    if args.proof_dir:
        args.proof_dir.mkdir(parents=True, exist_ok=True)
    if args.cuts:
        args.cuts.mkdir(parents=True, exist_ok=True)
    assert not args.learn or (args.cuts and not args.proof_dir)
    strengthened = {}
    if args.floor_file:
        for line in args.floor_file.read_text().splitlines():
            kind, key, minimum = line.split()
            strengthened[(kind, key)] = int(minimum)
    for row in args.cores.read_text().splitlines():
        _, adj, small, large = unpack(row)
        for kind, key, var, first, second, shared, one, two, slots in assigned_roles(row):
            if (kind, key, var) not in selected:
                continue
            selected.remove((kind, key, var))
            begun = process_time()
            width = first, second, shared
            floor_first, floor_second = floors_for(kind, width)
            floor_second = max(floor_second, strengthened.get((kind, key), 0))
            cnf = window_problem(adj, small, large, width, (one, two), slots, (floor_first, floor_second),
                                 unpaired_floor(kind), sorted_groups=True)
            eager_cuts(cnf, adj)
            old = cnf.order if args.no_column else attach_marked(cnf, adj, small, large)
            token = f'{kind}_{key}_{var}'
            if args.proof_dir:
                if args.cuts:
                    for line in (args.cuts / token).read_text().splitlines():
                        witness = tuple(map(int, line.split()))
                        assert len(witness) == len(set(witness)) == 9 and min(witness) >= 0 and max(witness) < old
                        cnf.add(cnf.independent_clause(witness))
                receipt = proof_run(cnf, args.limit, args.proof_dir / token, args.replay)
            else:
                recorded = set()
                receipt = lazy(cnf, args.limit, old, recorded)
                if args.learn:
                    (args.cuts / token).write_text(''.join(' '.join(map(str, cut)) + '\n' for cut in sorted(recorded)))
            print(kind, key, var, *receipt, f'{process_time() - begun:.4f}', flush=True)
    assert not selected, selected


if __name__ == '__main__':
    main()
