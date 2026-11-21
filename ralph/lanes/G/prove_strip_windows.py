#!/usr/bin/env python3
"""Produce or replay independently checked proofs for paired strip core keys."""

from argparse import ArgumentParser, FileType
from hashlib import sha256
from pathlib import Path
from subprocess import PIPE, run
import gzip
import shutil
from time import monotonic

from strip_completion import window


ROOT = Path(__file__).resolve().parents[3]
BIN = ROOT / 'opt/bin'


def bounded(command, seconds):
    return run(['nice', '-n', '5', 'timeout', '-k', '3s', f'{seconds*3}s',
                'prlimit', f'--cpu={seconds}:{seconds+2}', '--', *map(str, command)], stdout=PIPE, stderr=PIPE)


def verify(cnf, proof):
    for name, marker in (('cake_lpr', b's VERIFIED UNSAT'), ('lrat-check', b'c VERIFIED')):
        checked = bounded([BIN / name, cnf, proof], 35)
        if checked.returncode != 0 or marker not in checked.stdout.splitlines():
            raise RuntimeError((name, checked.returncode, checked.stdout[-1000:], checked.stderr[-1000:]))


def solve_key(row, args):
    *fields, line = row.split()
    _, first, second, *roles = fields
    assert args.mixed == bool(roles)
    key = '_'.join(fields)
    cnf = args.out / f'.{key}.cnf'
    proof = args.out / f'.{key}.lrat'
    stored = args.out / f'{key}.lrat.gz'
    start = monotonic()
    try:
        if args.mixed:
            from mixed_strip_completion import instance
            case, hole_first, hole_second, hole_peer = roles
            problem = instance(line, int(first), int(second), case, int(hole_first), int(hole_second),
                               int(hole_peer), args.eager)
        else:
            problem = window(line, int(first), int(second), args.eager, True, args.cut_budget, args.overlays)
        if args.overlays:
            print(key, problem.overlay_count, file=args.overlay_counts, flush=True)
        if args.cuts:
            for raw in (args.cuts / key).read_text().splitlines():
                witness = tuple(map(int, raw.split()))
                if len(witness) != 10 or len(set(witness)) != 10 or min(witness) < 0 or max(witness) >= 40:
                    raise ValueError('bad independent-set cut')
                problem.add(problem.independent_clause(witness))
        problem.formula.write(cnf)
        if args.replay:
            with gzip.open(stored, 'rb') as source, proof.open('wb') as output:
                shutil.copyfileobj(source, output)
        else:
            solver = bounded([BIN / 'cadical', '-q', '-n', '--lrat', '--no-binary',
                              '--seed=' + str(args.seed), '-c', args.conflicts, cnf, proof], args.cpu)
            if solver.returncode != 20:
                status = {0: 'CAP', 10: 'RELAXED_SAT', 124: 'TIMEOUT', 137: 'SIGNAL', 152: 'CPU_CAP',
                          -24: 'CPU_CAP'}.get(solver.returncode, 'ERROR')
                print(key, status, solver.returncode, f'{monotonic() - start:.3f}', flush=True)
                if status == 'ERROR':
                    raise RuntimeError((solver.stdout, solver.stderr))
                return
            if b's UNSATISFIABLE' not in solver.stdout.splitlines():
                raise RuntimeError((solver.stdout, solver.stderr))
        verify(cnf, proof)
        if not args.replay:
            with proof.open('rb') as source, stored.open('wb') as stored_stream:
                with gzip.GzipFile(filename='', mode='wb', compresslevel=1, fileobj=stored_stream, mtime=0) as output:
                    shutil.copyfileobj(source, output)
        print(key, 'REPLAY' if args.replay else 'CERT', sha256(cnf.read_bytes()).hexdigest(),
              stored.stat().st_size, f'{monotonic()-start:.3f}', flush=True)
    finally:
        cnf.unlink(missing_ok=True)
        proof.unlink(missing_ok=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--shard', type=int, nargs=2, default=(0, 1), metavar=('INDEX', 'TOTAL'))
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--conflicts', type=int, default=100000)
    parser.add_argument('--cpu', type=int, default=18)
    parser.add_argument('--eager', type=int, default=0)
    parser.add_argument('--cut-budget', action='store_true')
    parser.add_argument('--overlays', action='store_true')
    parser.add_argument('--mixed', action='store_true')
    parser.add_argument('--overlay-counts', type=FileType('w'))
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--cuts', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    index, count = args.shard
    assert 0 <= index < count
    keys = args.keys.read_text().splitlines()
    for key in keys[index::count]:
        solve_key(key, args)


if __name__ == '__main__':
    main()
