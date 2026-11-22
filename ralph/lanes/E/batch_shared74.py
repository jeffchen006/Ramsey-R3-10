#!/usr/bin/env python3
"""Produce and check four-window LRATs with one streaming encoder per worker."""

import argparse
from itertools import groupby
from pathlib import Path
import subprocess
from time import process_time

from batch_a11 import LIMIT, TOOLS
from involution_sat import from_graph6
from m11_sat import FastCuts, encode
from replay_shared74 import read


def limited(tool, cpu, wall, args, log):
    with log.open('x', encoding='ascii') as out:
        return subprocess.run(['nice', '-n', '5', 'timeout', str(wall),
                               'bash', str(LIMIT), str(cpu), str(TOOLS/tool),
                               *map(str, args)], stdout=out, stderr=subprocess.STDOUT).returncode


def proofs(args):
    assert 0 <= args.offset < args.stride
    args.output.mkdir(exist_ok=True)
    fast = FastCuts(args.fastcuts)
    queued = ((index, lift) for index, lift, result, *_ in read(args.trace) if result == 'open')
    selected = ((index, lift) for number, (index, lift) in enumerate(queued)
                if number % args.stride == args.offset)
    batches = iter(groupby(selected, key=lambda result: result[0]))
    batch = next(batches, None)
    checked = total = 0
    for index, (key, profile, parts, omitted) in enumerate(read(args.cover)):
        if batch is None:
            break
        if index < batch[0]:
            continue
        assert index == batch[0]
        core = from_graph6(key)
        for _, lift in batch[1]:
            groups = (*parts, omitted[lift])
            assert [sum(map(int.bit_count, group)) for group in groups] == profile == [10, 10, 11, 11]
            prefix = args.output/f'{index}_{lift}'
            cnf, proof = prefix.with_suffix('.cnf'), prefix.with_suffix('.lrat')
            started = process_time()
            variables, clauses, _, _ = encode(core, groups, (7,) * 4, (7,) * 24, cut_size=8, fast=fast)
            with cnf.open('x', encoding='ascii') as out:
                print('p cnf', variables, len(clauses), file=out)
                out.writelines(' '.join(map(str, (*row, 0)))+'\n' for row in clauses)
            cpu = process_time() - started
            result = limited('cadical', 15, 40, ('-q', '--lrat', cnf, proof), prefix.with_suffix('.solve.log'))
            check_ok = False
            if result == 20:
                check = prefix.with_suffix('.lrat.log')
                check_ok = limited('cake_lpr', 12, 37, (cnf, proof), check) == 0 and \
                    's VERIFIED UNSAT' in check.read_text(encoding='ascii').splitlines()
            checked += check_ok
            total += 1
            print(index, lift, 'CHECKED' if check_ok else f'INCOMPLETE_{result}',
                  f'encode_cpu={cpu:.3f}', 'cnf_bytes', cnf.stat().st_size, flush=True)
            if total == args.limit:
                return 0 if total == checked else 1
        batch = next(batches, None)
    assert batch is None
    print('checked', checked, '/', total, flush=True)
    return 0 if total == checked else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cover', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--fastcuts', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    parser.add_argument('--limit', type=int)
    raise SystemExit(proofs(parser.parse_args()))
