#!/usr/bin/env python3
"""Produce checked LRAT proofs for pure alternate pivots."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip
import shutil

from prove_strip_windows import BIN, bounded, verify
from pure_pivot import instance


def prove(row, output, eager, replay):
    *fields, encoded = row.split()
    _, first, second, role, centre, peer, repeated = fields
    assert peer == repeated
    key = '_'.join(fields)
    cnf = output / f'.{key}.cnf'
    proof = output / f'.{key}.lrat'
    stored = output / f'{key}.lrat.gz'
    start = monotonic()
    try:
        problem = instance(encoded, int(first), int(second), role, int(centre), int(peer), eager)
        problem.formula.write(cnf)
        if replay:
            with gzip.open(stored, 'rb') as source, proof.open('wb') as stream:
                shutil.copyfileobj(source, stream)
        else:
            solver = bounded([BIN / 'cadical', '-q', '-n', '--lrat', '--no-binary', '--seed=0',
                              '-c', '100000', cnf, proof], 18)
            if solver.returncode != 20:
                status = {0: 'CAP', 10: 'RELAXED_SAT', 124: 'TIMEOUT', 137: 'SIGNAL',
                          152: 'CPU_CAP', -24: 'CPU_CAP'}.get(solver.returncode, 'ERROR')
                print(key, status, solver.returncode, f'{monotonic()-start:.3f}', flush=True)
                if status == 'ERROR':
                    raise RuntimeError((solver.stdout, solver.stderr))
                return
            if b's UNSATISFIABLE' not in solver.stdout.splitlines():
                raise RuntimeError(solver.stdout)
        verify(cnf, proof)
        if not replay:
            with proof.open('rb') as source, stored.open('wb') as stream:
                with gzip.GzipFile(filename='', mode='wb', compresslevel=1, fileobj=stream, mtime=0) as compressed:
                    shutil.copyfileobj(source, compressed)
        print(key, 'REPLAY' if replay else 'CERT', sha256(cnf.read_bytes()).hexdigest(),
              stored.stat().st_size, f'{monotonic()-start:.3f}', flush=True)
    finally:
        cnf.unlink(missing_ok=True)
        proof.unlink(missing_ok=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--eager', type=int, default=0)
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--shard', type=int, nargs=2, default=(0, 1))
    args = parser.parse_args()
    index, count = args.shard
    assert 0 <= index < count
    args.output.mkdir(parents=True, exist_ok=True)
    for row in args.keys.read_text().splitlines()[index::count]:
        prove(row, args.output, args.eager, args.replay)


if __name__ == '__main__':
    main()
