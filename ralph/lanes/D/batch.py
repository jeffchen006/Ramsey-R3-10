#!/usr/bin/env python3
"""Run one calibrated fixed-kernel encoding on an explicit subset of a catalogue."""

import argparse
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import time

from kernel_cnf import MODES, ROOT, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('n', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('maximum', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('mode', choices=MODES)
    parser.add_argument('out', type=Path)
    parser.add_argument('--indices', type=Path)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--seconds', type=int, required=True, help='CPU limit per solver')
    parser.add_argument('--smsg', type=Path, default=ROOT / 'opt/bin/smsg')
    parser.add_argument('--proof', action='store_true')
    args = parser.parse_args()
    catalogue = args.catalogue.read_text().splitlines()
    indices = list(map(int, args.indices.read_text().split())) if args.indices else list(range(len(catalogue)))
    assert len(set(indices)) == len(indices) and all(0 <= index < len(catalogue) for index in indices)
    args.out.mkdir(parents=True, exist_ok=False)
    if args.mode == 'base':
        warm = args.out / 'warm.cnf'
        write(args.n, args.degree, args.degree + 1, args.maximum, catalogue[indices[0]], args.mode, warm)
        warm.unlink()

    def solve(index):
        prefix = args.out / f'k{index:04d}'
        cnf, trace = prefix.with_suffix('.cnf'), prefix.with_suffix('.time')
        logfile, solutions = prefix.with_suffix('.log'), prefix.with_suffix('.sol')
        start = time.monotonic()
        write(args.n, args.degree, args.degree + 1, args.maximum, catalogue[index], args.mode, cnf)
        encode = time.monotonic() - start
        command = ['/usr/bin/time', '-o', str(trace), '-f', '%U %S %e %M', 'nice', '-n', '5',
                   'timeout', '-k', '5', str(2 * args.seconds + 10), 'prlimit', '--as=17179869184',
                   f'--cpu={args.seconds}:{args.seconds + 1}', args.smsg.resolve(), '-v', str(args.n),
                   '--dimacs', cnf, '--forbid-independent-set', str(args.degree + 1), '--cutoff', '0', '-a']
        if args.proof:
            command += ['--proof-log', prefix.with_suffix('.plog'), '--sym-break-clauses', prefix.with_suffix('.sym.json')]
            command[command.index('prlimit') + 1:command.index('prlimit') + 1] = ['--fsize=300000000']
        command += ['--initial-partition', *(['1'] * (2 * args.degree)), str(args.n - 2 * args.degree)]
        with logfile.open('w') as stream:
            run = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
        lines = logfile.read_text().splitlines()
        models = [line for line in lines if line.startswith('[(')]
        if models:
            solutions.write_text('\n'.join(models) + '\n')
        timing = trace.read_text().splitlines()[-1].split()
        cpu = float(timing[0]) + float(timing[1])
        if run.returncode in (124, 152, -24):
            verdict = 'TIMEOUT'
        elif run.returncode in (137, -9):
            verdict = 'KILLED'
        elif run.returncode == 20 and ('Result: 20' in lines or 's UNSATISFIABLE' in lines):
            verdict = 'DONE'
        else:
            verdict = 'ERROR'
        if not args.proof and verdict != 'ERROR':
            cnf.unlink()
        return [index, verdict, run.returncode, len(models), f'{cpu:.3f}', timing[2], timing[3], f'{encode:.3f}']

    with ThreadPoolExecutor(max_workers=args.workers) as pool, (args.out / 'results.tsv').open('w') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['idx', 'verdict', 'rc', 'models', 'cpu_s', 'wall_s', 'peak_kib', 'encode_s'])
        stream.flush()
        futures = [pool.submit(solve, index) for index in indices]
        for future in as_completed(futures):
            row = future.result()
            writer.writerow(row)
            stream.flush()
    print(f'Finished {len(indices)} kernels in {args.out} (pid {os.getpid()})', flush=True)


if __name__ == '__main__':
    main()
