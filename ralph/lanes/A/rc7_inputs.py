#!/usr/bin/env python3
"""Rebuild the reported R(7) base, extract fresh cubes, and assemble DIMACS inputs."""

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def cubes(source, log):
    for raw in source.read_text().splitlines():
        if log and raw.startswith('Decisions:'):
            row = tuple(map(int, raw.split()[1:]))
        elif not log and raw.startswith('a '):
            tokens = raw.split()
            if tokens[-1] != '0':
                raise ValueError('no terminator')
            row = tuple(map(int, tokens[1:-1]))
        else:
            continue
        if any(not 1 <= abs(lit) <= 780 for lit in row) or len({abs(lit) for lit in row}) != len(row):
            raise ValueError(f'invalid cube {row}')
        yield row


def extend(base, target, clauses):
    with base.open() as source, target.open('w') as output:
        prefix, kind, variables, number = source.readline().split()
        if (prefix, kind) != ('p', 'cnf'):
            raise ValueError('bad base')
        print('p cnf', variables, int(number) + len(clauses), file=output)
        output.writelines(source)
        for clause in clauses:
            print(*clause, 0, file=output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cmd = parser.add_subparsers(dest='mode', required=True)
    base = cmd.add_parser('base')
    base.add_argument('target', type=Path)
    extract = cmd.add_parser('extract')
    extract.add_argument('source', type=Path)
    extract.add_argument('target', type=Path)
    for name in ('cover', 'units'):
        extend_parser = cmd.add_parser(name)
        extend_parser.add_argument('base', type=Path)
        extend_parser.add_argument('cubes', type=Path)
        extend_parser.add_argument('target', type=Path)
        if name == 'units':
            extend_parser.add_argument('cube', type=int, help='1-based cube index')
    args = parser.parse_args()
    if args.mode == 'base':
        subprocess.run([sys.executable, ROOT / 'sms/gen_ramsey.py', '-n', '40', '-k', '10',
                        '--dmin', '9', '--dmax', '9', '--mtf', '--fix-nbhd', '9', '--codeg-max', '7',
                        '--codeg-pair', '7', '--edges', '10-11,10-12,8-11,8-12,9-11,9-12',
                        '--block-from', '13', '--block-e', '85', '-o', args.target], check=True)
    elif args.mode == 'extract':
        extracted = list(cubes(args.source, log=True))
        if not extracted:
            raise ValueError('no cubes')
        with args.target.open('w') as output:
            for row in extracted:
                print('a', *row, 0, file=output)
        print(f'{len(extracted)} cubes extracted; coverage is not assumed')
    else:
        rows = list(cubes(args.cubes, log=False))
        if args.mode == 'cover':
            clauses = [tuple(-lit for lit in row) for row in rows]
        else:
            if not 1 <= args.cube <= len(rows):
                raise ValueError('cube index out of range')
            clauses = [(lit,) for lit in rows[args.cube - 1]]
        extend(args.base, args.target, clauses)


if __name__ == '__main__':
    main()
