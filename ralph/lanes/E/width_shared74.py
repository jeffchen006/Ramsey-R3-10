#!/usr/bin/env python3
"""Price narrower I8 cuts on an already checked four-window pilot queue."""

import argparse
from collections import Counter
from itertools import groupby
from pathlib import Path
from time import process_time

from batch_shared74 import limited
from involution_sat import from_graph6
from m11_sat import FastCuts, calibration, encode
from replay_shared74 import read


def dimacs(variables, clauses):
    return (f'p cnf {variables} {len(clauses)}\n' +
            ''.join(' '.join(map(str, (*row, 0)))+'\n' for row in clauses)).encode('ascii')


def pilot(cover, trace, original, output, width, fast):
    queue = tuple((index, lift) for index, lift, verdict, *_ in read(trace) if verdict == 'open')
    assert queue and tuple(sorted(set(queue))) == queue
    expected = {f'{index}_{lift}' for index, lift in queue}
    for suffix in ('cnf', 'lrat', 'lrat.log'):
        assert {path.name for path in original.glob(f'*.{suffix}')} == {f'{key}.{suffix}' for key in expected}
    output.mkdir()
    stats = Counter()
    batches = iter(groupby(queue, key=lambda row: row[0]))
    batch = next(batches, None)
    for index, (key, profile, parts, omitted) in enumerate(read(cover)):
        if batch is None:
            break
        if index < batch[0]:
            continue
        assert index == batch[0]
        core = from_graph6(key)
        for _, lift in batch[1]:
            prefix = f'{index}_{lift}'
            assert 's VERIFIED UNSAT' in (original/f'{prefix}.lrat.log').read_text(encoding='ascii').splitlines()
            groups = (*parts, omitted[lift])
            assert [sum(map(int.bit_count, group)) for group in groups] == profile == [10, 10, 11, 11]
            start = process_time()
            variables, clauses, _, _ = encode(core, groups, (7,)*4, (7,)*24, cut_size=width, fast=fast)
            new = dimacs(variables, clauses)
            encode_cpu = process_time()-start
            wide_header, *wide_clauses = (original/f'{prefix}.cnf').read_bytes().splitlines()
            narrow_header, *narrow_clauses = new.splitlines()
            assert int(wide_header.split()[2]) == int(narrow_header.split()[2]) == variables
            assert len(wide_clauses) == int(wide_header.split()[3])
            assert len(narrow_clauses) == int(narrow_header.split()[3])
            assert not (Counter(narrow_clauses) - Counter(wide_clauses))
            cnf, proof = output/f'{prefix}.cnf', output/f'{prefix}.lrat'
            cnf.write_bytes(new)
            result = limited('cadical', 12, 32, ('-q', '--lrat', cnf, proof), output/f'{prefix}.solve.log')
            if result == 20:
                check = output/f'{prefix}.lrat.log'
                passed = limited('cake_lpr', 10, 30, (cnf, proof), check) == 0 and \
                    's VERIFIED UNSAT' in check.read_text(encoding='ascii').splitlines()
                verdict = 'CHECKED' if passed else 'BAD_CHECK'
            elif result == 10:
                verdict = 'SAT_NARROW'
            else:
                verdict = f'INCOMPLETE_{result}'
            stats[verdict] += 1
            stats['cnf_bytes'] += len(new)
            stats['base_bytes'] += (original/f'{prefix}.cnf').stat().st_size
            stats['encode_msec'] += round(1000*encode_cpu)
            print(prefix, verdict, 'encode_cpu', round(encode_cpu, 3), 'cnf_bytes', len(new), flush=True)
        batch = next(batches, None)
    assert batch is None and sum(count for name, count in stats.items() if not name.endswith(('bytes', 'msec'))) == len(queue)
    print('width', width, dict(stats), flush=True)
    return not any(name.startswith(('BAD_CHECK', 'INCOMPLETE_')) for name in stats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fastcuts', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    scan = sub.add_parser('pilot')
    for path in ('cover', 'trace', 'original', 'output'):
        scan.add_argument(path, type=Path)
    scan.add_argument('width', type=int, choices=range(1, 9))
    args = parser.parse_args()
    fast = FastCuts(args.fastcuts)
    if args.mode == 'calibrate':
        calibration(fast)
        return 0
    return 0 if pilot(args.cover, args.trace, args.original, args.output, args.width, fast) else 1


if __name__ == '__main__':
    raise SystemExit(main())
