#!/usr/bin/env python3
"""Price both terminal proof routes, including a newly made original reference."""

import argparse
from collections import Counter
from itertools import groupby
from pathlib import Path
from time import process_time

from batch_shared74 import limited
from bind_width74 import binding, dimacs
from involution_sat import from_graph6
from m11_sat import FastCuts, encode
from replay_shared74 import read


def formula(core, groups, bounds, degrees, width, fast):
    variables, clauses, _, _ = encode(core, groups, bounds, degrees, cut_size=width, fast=fast)
    return dimacs(variables, clauses)


def check(cnf, proof, log):
    return limited('cake_lpr', 10, 30, (cnf, proof), log) == 0 and \
        's VERIFIED UNSAT' in log.read_text(encoding='ascii').splitlines()


def solve(cnf):
    proof = cnf.with_suffix('.lrat')
    code = limited('cadical', 7, 15, ('-q', '--lrat', cnf, proof), cnf.with_suffix('.solve.log'))
    if code == 20:
        return ('CHECKED' if check(cnf, proof, cnf.with_suffix('.lrat.log')) else 'BAD_CHECK'), proof
    return ('SAT' if code == 10 else f'INCOMPLETE_{code}'), proof


def route(core, groups, bounds, degrees, fast, folder, stem, mode):
    start = process_time()
    wide = folder / f'{stem}_wide.cnf'
    wide.write_bytes(formula(core, groups, bounds, degrees, 8, fast))
    attempt = 'NOT_RUN'
    if mode == 'narrow':
        narrow = folder / f'{stem}_narrow.cnf'
        narrow.write_bytes(formula(core, groups, bounds, degrees, 3, fast))
        try:
            binding(core, groups, bounds, degrees, wide, narrow)
        except AssertionError:
            attempt = 'MISMATCH'
        else:
            attempt, proof = solve(narrow)
            if attempt == 'CHECKED':
                if check(narrow, proof, narrow.with_suffix('.replay.log')):
                    return attempt, 'NARROW', process_time() - start
                attempt = 'BAD_RECHECK'
    verdict, proof = solve(wide)
    if verdict == 'CHECKED':
        assert wide.read_bytes() == formula(core, groups, bounds, degrees, 8, fast)
        if not check(wide, proof, wide.with_suffix('.replay.log')):
            verdict = 'BAD_RECHECK'
    return attempt, f'WIDE_{verdict}', process_time() - start


def selected(trace, stride, offset):
    assert 0 <= offset < stride
    want = [(index, lift) for index, lift, verdict, *_ in read(trace) if verdict == 'open']
    assert want and want == sorted(set(want))
    return want[offset::stride]


def cover_lifts(cover, want):
    batches = iter(groupby(want, key=lambda row: row[0]))
    pending = next(batches, None)
    for index, (key, profile, parts, omitted) in enumerate(read(cover)):
        if pending is None:
            break
        if index < pending[0]:
            continue
        assert index == pending[0]
        core = from_graph6(key)
        for _, lift in pending[1]:
            groups = (*parts, omitted[lift])
            assert [sum(map(int.bit_count, group)) for group in groups] == profile == [10, 10, 11, 11]
            yield f'{index}_{lift}', core, groups
        pending = next(batches, None)
    assert pending is None


def passed(log):
    return log.is_file() and 's VERIFIED UNSAT' in log.read_text(encoding='ascii').splitlines()


def rebind_lift(core, groups, bounds, degrees, fast, folder, stem):
    narrow, wide = (folder / f'{stem}_{width}.cnf' for width in ('narrow', 'wide'))
    use_narrow = passed(narrow.with_suffix('.replay.log'))
    use_wide = passed(wide.with_suffix('.replay.log'))
    assert use_narrow != use_wide, stem
    if use_narrow:
        binding(core, groups, bounds, degrees, wide, narrow)
    else:
        assert wide.read_bytes() == formula(core, groups, bounds, degrees, 8, fast)
    cnf = narrow if use_narrow else wide
    assert check(cnf, cnf.with_suffix('.lrat'), cnf.with_suffix('.fresh.log')), stem
    return 'NARROW' if use_narrow else 'WIDE_CHECKED'


def retained(folder):
    return sum(path.stat().st_size for path in folder.iterdir())


def compare(cover, trace, folder, mode, fast, stride, offset):
    want = selected(trace, stride, offset)
    folder.mkdir()
    counts = Counter()
    for stem, core, groups in cover_lifts(cover, want):
        attempt, verdict, parent_cpu = route(core, groups, (7,)*4, (7,)*24, fast, folder, stem, mode)
        counts[verdict] += 1
        print(stem, attempt, verdict, f'encode_bind_cpu={parent_cpu:.3f}', flush=True)
        assert retained(folder) < 210 * 1024**2
    assert sum(counts.values()) == len(want)
    print(mode, dict(counts), 'retained bytes', retained(folder), flush=True)
    return 0 if counts['NARROW'] + counts['WIDE_CHECKED'] == len(want) else 1


def rebind(cover, trace, folder, fast, stride, offset):
    want = selected(trace, stride, offset)
    expected = {f'{index}_{lift}' for index, lift in want}
    assert {path.name for path in folder.glob('*_wide.cnf')} == {f'{stem}_wide.cnf' for stem in expected}
    counts = Counter()
    for stem, core, groups in cover_lifts(cover, want):
        verdict = rebind_lift(core, groups, (7,)*4, (7,)*24, fast, folder, stem)
        counts[verdict] += 1
        print(stem, verdict, flush=True)
        assert retained(folder) < 210 * 1024**2
    assert sum(counts.values()) == len(want)
    print('fresh exact-queue inclusion/width-eight replay', dict(counts), flush=True)


def calibrate(folder, fast):
    folder.mkdir()
    core, groups, bounds = (0,), ((1,), (0,), (0,), (0, 0)), (3,)*4
    for name, degree, want in (('positive', (2, 1, 2, 1, 1), 'SAT'),
                               ('negative', (3, 1, 1, 1, 1), 'CHECKED')):
        wide = route(core, groups, bounds, degree, fast, folder, f'{name}_only', 'wide')
        narrow = route(core, groups, bounds, degree, fast, folder, f'{name}_first', 'narrow')
        assert wide[:2] == ('NOT_RUN', f'WIDE_{want}')
        assert narrow[:2] == (want, 'NARROW' if want == 'CHECKED' else 'WIDE_SAT')
        if want == 'CHECKED':
            assert rebind_lift(core, groups, bounds, degree, fast, folder, f'{name}_only') == 'WIDE_CHECKED'
            assert rebind_lift(core, groups, bounds, degree, fast, folder, f'{name}_first') == 'NARROW'
        print(name, 'wide-only', wide[:2], 'narrow-first', narrow[:2], flush=True)
    trace = folder / 'control.trace.jsonl'
    trace.write_text('[0,0,"open"]\n[0,1,"open"]\n[1,0,"open"]\n', encoding='ascii')
    assert selected(trace, 2, 0) == [(0, 0), (1, 0)] and selected(trace, 2, 1) == [(0, 1)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fastcuts', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate').add_argument('folder', type=Path)
    for mode in ('wide', 'narrow', 'rebind'):
        command = sub.add_parser(mode)
        for path in ('cover', 'trace', 'folder'):
            command.add_argument(path, type=Path)
        command.add_argument('--stride', type=int, default=1)
        command.add_argument('--offset', type=int, default=0)
    args = parser.parse_args()
    fast = FastCuts(args.fastcuts)
    if args.mode == 'calibrate':
        calibrate(args.folder, fast)
        return 0
    if args.mode == 'rebind':
        rebind(args.cover, args.trace, args.folder, fast, args.stride, args.offset)
        return 0
    return compare(args.cover, args.trace, args.folder, args.mode, fast, args.stride, args.offset)


if __name__ == '__main__':
    raise SystemExit(main())
