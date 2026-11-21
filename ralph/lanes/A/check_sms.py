#!/usr/bin/env python3
"""Validate logged SMS clauses and check LRAT for the augmented CNF.

This does not establish the soundness of the input CNF or the coverage of
any cube split. For cube proofs, --blocks is the partition preserved by the
uncubed problem, not a claim that each cube is invariant under this group.
"""

import argparse
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def run(args, verdict=None):
    checked = subprocess.run(args, stdout=subprocess.PIPE, text=True, check=True)
    print(checked.stdout, end='', flush=True)
    if verdict is not None and verdict not in checked.stdout.splitlines():
        raise ValueError(f'{args[0]}: missing verdict {verdict!r}')


def witnesses(sym_file, prefix, order, blocks):
    part = [index for index, size in enumerate(blocks) for _ in range(size)]
    edge_vars = {edge: index for index, edge in enumerate(combinations(range(order), 2), 1)}
    rows = json.loads(sym_file.read_text())['sym_clauses']
    witnesses_file = Path(str(prefix) + '.wit')
    clauses_file = Path(str(prefix) + '.sb.cnf')
    with witnesses_file.open('w') as witness, clauses_file.open('w') as clauses:
        print('p cnf', len(edge_vars), len(rows), file=clauses)
        for lits, perm in rows:
            if sorted(perm) != list(range(order)):
                raise ValueError('invalid permutation')
            inv = [0] * order
            for source, target in enumerate(perm):
                if part[source] != part[target]:
                    raise ValueError('permutation does not preserve the partition')
                inv[target] = source
            row = []
            for sign, first, second in lits:
                if sign not in (-1, 1):
                    raise ValueError('invalid literal sign')
                row.append(sign * edge_vars[tuple(sorted((first, second)))])
            print(*row, 0, '|', *inv, file=witness)
            print(*row, 0, file=clauses)
    return witnesses_file, clauses_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('plog', type=Path)
    parser.add_argument('sym', type=Path)
    parser.add_argument('--n', required=True, type=int)
    parser.add_argument('--k', required=True, type=int)
    parser.add_argument('--blocks', nargs='+', type=int)
    parser.add_argument('--heap', type=int, default=10000)
    parser.add_argument('--stack', type=int, default=2000)
    parser.add_argument('--allow-input-extras', action='store_true')
    args = parser.parse_args()
    blocks = args.blocks or [args.n]
    if sum(blocks) != args.n or min(blocks) < 1:
        raise ValueError('invalid partition')
    tool = ROOT / 'opt/bin'
    prefix = args.plog.with_suffix('.cert')
    cnf_file = str(prefix) + '.cnf'
    run([tool / 'lratlog2lrat', args.input, args.plog, prefix])
    witness, sb_cnf = witnesses(args.sym, prefix, args.n, blocks)
    run([sys.executable, ROOT / 'cert/check_sb.py', '--n', str(args.n),
         '--better', 'min', '--order', 'rowmajor', '--allow-empty', witness], 'RESULT: OK')
    extra = ['--extra', args.input] if args.allow_input_extras else []
    run([sys.executable, ROOT / 'cert/check_cnf.py', '--n', str(args.n), '--s', str(args.k),
         '--order', 'rowmajor', '--require-all-tri', '--extra', sb_cnf, *extra, cnf_file],
        'RESULT: OK (every clause is valid or listed as extra)')
    run([tool / 'cake_lpr', f'--CML_HEAP_SIZE={args.heap}', f'--CML_STACK_SIZE={args.stack}',
         cnf_file, str(prefix) + '.lrat'], 's VERIFIED UNSAT')
    print('s VERIFIED logged CNF')


if __name__ == '__main__':
    main()
