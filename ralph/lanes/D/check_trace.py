#!/usr/bin/env python3
"""Check a fixed-kernel SMS trace (sec7 links b,c,e; not encoding or cover)."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from kernel_cnf import Cnf, ROOT


def checked(command, logfile, verdict=None):
    wrapped = ['nice', '-n', '5', 'timeout', '210', 'prlimit', '--as=17179869184', '--cpu=150:151'] + command
    with logfile.open('w') as output:
        result = subprocess.run(wrapped, stdout=output, stderr=subprocess.STDOUT, check=False)
    if result.returncode != 0 or (verdict is not None and verdict not in logfile.read_text().splitlines()):
        raise SystemExit(f'FAIL {command[0]}: check {logfile}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('n', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('prefix', type=Path, help='common path of .cnf, .plog, .sym.json')
    parser.add_argument('--lean-sb', type=Path)
    args = parser.parse_args()
    prefix = args.prefix.resolve()
    output = Path(f'{prefix}.checked')
    output.mkdir(exist_ok=False)
    suffix = lambda ext: Path(f'{prefix}.{ext}')
    merged = output / 'merged'
    checked([ROOT / 'opt/bin/lratlog2lrat', suffix('cnf'), suffix('plog'), merged], output / 'convert.log')

    witness_file = output / 'sym.wit'
    witness_cnf = output / 'sym.cnf'
    symmetries = json.loads(suffix('sym.json').read_text())['sym_clauses']
    edges = Cnf(args.n, {})
    fixed = 2 * args.degree
    blocks = ','.join(['1'] * fixed + [str(args.n - fixed)])
    with witness_file.open('w') as witnesses, witness_cnf.open('w') as symmetry_clauses:
        witnesses.write(f'c order positions=rowmajor better=min vars=rowmajor d=0 n={args.n} s={args.degree + 1} blocks={blocks}\n')
        symmetry_clauses.write(f'p cnf {edges.nvars} {len(symmetries)}\n')
        for clause, permutation in symmetries:
            if sorted(permutation) != list(range(args.n)) or permutation[:fixed] != list(range(fixed)):
                raise SystemExit('FAIL witness violates kernel partition')
            inverse = [0] * args.n
            for vertex, target in enumerate(permutation):
                inverse[target] = vertex
            literals = ' '.join(str(sign * edges.edge(left, right)) for sign, left, right in clause)
            symmetry_clauses.write(f'{literals} 0\n')
            witnesses.write(f'{literals} 0 | ' + ' '.join(map(str, inverse)) + '\n')
    checked([sys.executable, '-B', ROOT / 'cert/check_sb.py', '--n', str(args.n), '--order', 'rowmajor',
             '--better', 'min', '--allow-empty', witness_file], output / 'sym-python.log', 'RESULT: OK')
    if args.lean_sb:
        checked([args.lean_sb.resolve(), witness_file], output / 'sym-lean.log',
                f's VERIFIED {len(symmetries)} clauses')
    elif symmetries:
        print('NOTE: Lean symmetry check not run.')
    checked([sys.executable, '-B', ROOT / 'cert/check_cnf.py', '--n', str(args.n), '--s', str(args.degree + 1),
             '--order', 'rowmajor', '--extra', suffix('cnf'), '--extra', witness_cnf, merged.with_suffix('.cnf')],
            output / 'cnf.log', 'RESULT: OK (every clause is valid or listed as extra)')
    checked([ROOT / 'opt/bin/cake_lpr', '--CML_HEAP_SIZE=8000', '--CML_STACK_SIZE=512',
             merged.with_suffix('.cnf'), merged.with_suffix('.lrat')], output / 'cake.log', 's VERIFIED UNSAT')
    print(f'TRACE CHECKED ({len(symmetries)} SB witnesses); encoding and cover not certified.')


if __name__ == '__main__':
    main()
