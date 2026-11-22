"""Independent unary-SAT census of the eight-anchor boundary; dual proof replay."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess
import time

from pysat.card import CardEnc
from pysat.formula import IDPool
from pysat.solvers import Cadical195

from path_links import make
from path_growth import ROOT, bits, fixed_graph, independent_path_max, read_profiles


def reflect(profile):
    return {sum(1 << dest for vertex, dest in enumerate((4, 6, 5, 7, 0, 2, 1, 3)) if mask >> vertex & 1): amount
            for mask, amount in profile.items()}


def sat_census(source):
    all_profiles = list(read_profiles(source))
    target = {tuple(sorted(other.items())) for profile in all_profiles for other in (profile, reflect(profile))}
    assert len(target) == 4756
    adj = {vertex: set() for vertex in range(8)}
    for src in range(4):
        for dst in range(4, 8):
            if (src, dst) not in [(1, 5), (1, 6), (2, 6), (3, 7)]:
                adj[src].add(dst)
                adj[dst].add(src)
    pool = IDPool()
    levels = {}
    with Cadical195() as solver:
        for mask in range(256):
            points = [vertex for vertex in range(8) if mask >> vertex & 1]
            if any(dst in adj[src] for src, dst in combinations(points, 2)):
                continue
            upper = min([32] + [9 - len(adj[vertex]) for vertex in points] +
                        [3 - len(adj[src] & adj[dst]) for src, dst in combinations(points, 2)])
            levels[mask] = [pool.id() for _ in range(upper)]
            for first, last in zip(levels[mask], levels[mask][1:]):
                solver.add_clause([first, -last])
        for vertex in range(8):
            values = [lit for mask, flags in levels.items() if mask >> vertex & 1 for lit in flags]
            solver.append_formula(CardEnc.equals(values, 9 - len(adj[vertex]), vpool=pool).clauses)
        for src, dst in combinations(range(8), 2):
            if dst in adj[src]:
                continue
            values = [lit for mask, flags in levels.items() if mask >> src & mask >> dst & 1 for lit in flags]
            solver.append_formula(CardEnc.atmost(values, 3 - len(adj[src] & adj[dst]), vpool=pool).clauses)
        solver.append_formula(CardEnc.equals([lit for flags in levels.values() for lit in flags], 32, vpool=pool).clauses)
        found = 0
        while solver.solve():
            model = set(solver.get_model())
            counts = {mask: sum(lit in model for lit in flags) for mask, flags in levels.items()}
            key = tuple(sorted((mask, count) for mask, count in counts.items() if count))
            assert key in target
            target.remove(key)
            found += 1
            solver.add_clause([-flags[count - 1] for mask, flags in levels.items() if (count := counts[mask])])
    assert not target
    print('PASS independent unary boundary SAT, exhausted', found, 'labelled patterns, exact union of both orientations', flush=True)


def replay(folder):
    profiles = list(read_profiles(folder / 'path.tsv'))
    closed = set()
    for mode in ('links', 'exact', 'packed'):
        for proof in sorted((folder / mode).glob('*.cake')):
            index = int(proof.stem)
            tmp = folder / 'recheck-temp.cnf'
            formula = make(profiles[index], 9, 6, exact=mode != 'links', packing=mode == 'packed',
                           square_range=(0, 13) if mode == 'packed' else None)
            formula.write(tmp)
            assert tmp.read_bytes() == proof.with_suffix('.cnf').read_bytes()
            witness = proof.with_suffix('.lrat')
            if [] in formula.clauses:
                witness = proof.with_suffix('.empty.lrat')
                witness.write_text(f'{len(formula.clauses) + 1} 0 {1 + formula.clauses.index([])} 0\n')
            for tool, prefix in [('cake_lpr', 's VERIFIED UNSAT'), ('lrat-check', 'c VERIFIED')]:
                command = ['nice', '-n', '5', 'timeout', '60', 'prlimit', '--cpu=45:46', '--as=17179869184',
                           ROOT / 'opt/bin' / tool, tmp, witness]
                result = subprocess.run(command, capture_output=True, text=True)
                assert result.returncode == 0 and prefix in result.stdout.splitlines(), (proof, witness, tool, result.stdout)
            print('DUAL', mode, index, witness, flush=True)
            assert index not in closed
            closed.add(index)
            tmp.unlink()
    max6 = {int(line.split()[0]) for line in (folder / 'growth.tsv').read_text().splitlines() if line.split()[1] == '6'}
    assert len(max6) == 22 and len(closed) == 19 and max6 - closed == {2298, 2424, 2431}
    print('PASS byte-exact rebuild + two LRAT checkers:', len(closed), 'conditional CNFs; residual', sorted(max6 - closed), flush=True)
    crossed = subprocess.run(['nice', '-n', '5', 'timeout', '40', 'prlimit', '--cpu=25:26', ROOT / 'opt/bin/cake_lpr',
                              folder / 'links/461.cnf', folder / 'exact/2388.lrat'], capture_output=True, text=True)
    assert 's VERIFIED UNSAT' not in crossed.stdout.splitlines()
    print('PASS crossed LRAT is not accepted', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('mode', choices=('boundary', 'paths', 'proofs'))
    args = parser.parse_args()
    start = time.process_time()
    if args.mode == 'boundary':
        sat_census(args.folder / 'path.tsv')
    elif args.mode == 'paths':
        expected = dict(tuple(map(int, line.split())) for line in (args.folder / 'growth.tsv').read_text().splitlines())
        observed = Counter()
        for index, profile in enumerate(read_profiles(args.folder / 'path.tsv')):
            size = independent_path_max([set(bits(row)) for row in fixed_graph(profile)])
            assert size == expected[index]
            observed[size] += 1
        assert observed == {6: 22, 7: 1184, 8: 1228}
        print('PASS exhaustive simple path walks on every fixed-star profile:', sorted(observed.items()), flush=True)
    else:
        replay(args.folder)
    print('CPU driver', round(time.process_time() - start, 3), flush=True)
