#!/usr/bin/env python3
"""Audit proof routes and separate rechecks against an exact ordered queue."""

import argparse
from collections import Counter
from pathlib import Path
import re

from m11_sat import FastCuts
from price_width74 import cover_lifts, retained, route, selected


ROUTE = re.compile(r'(\d+_\d+) (\S+) (\S+) encode_bind_cpu=\d+\.\d+')
REBIND = re.compile(r'(\d+_\d+) (NARROW|WIDE_CHECKED)')
MARKER = 's VERIFIED UNSAT'


def bound_route(stem, attempt, choice):
    if choice == 'NARROW':
        assert attempt == 'CHECKED', (stem, attempt)
        return 'narrow'
    assert choice == 'WIDE_CHECKED', (stem, choice)
    assert attempt in ('NOT_RUN', 'SAT', 'INCOMPLETE_124', 'INCOMPLETE_152', 'INCOMPLETE_137'), (stem, attempt)
    return 'wide'


def run(cover, trace, folder, mode, stride, offset, mib):
    want = selected(trace, stride, offset)
    fastcuts = FastCuts(Path('../r6_e11/m11_fastcuts.so'))
    folder.mkdir()
    stats = Counter()
    for stem, core, groups in cover_lifts(cover, want):
        attempt, choice, cpu = route(core, groups, (7,)*4, (7,)*24, fastcuts, folder, stem, mode)
        print(stem, attempt, choice, f'encode_bind_cpu={cpu:.3f}', flush=True)
        bound_route(stem, attempt, choice)
        assert retained(folder) < mib * 1024**2, folder
        stats[attempt, choice] += 1
    assert sum(stats.values()) == len(want)
    print(mode, dict(stats), 'retained bytes', retained(folder), flush=True)


def recheck(records, fresh, folder, expected):
    routes = [match.groups() for line in records.read_text(encoding='ascii').splitlines()
              if (match := ROUTE.fullmatch(line))]
    assert [stem for stem, _, _ in routes] == expected, records
    for stem, attempt, choice in routes:
        width = bound_route(stem, attempt, choice)
        path = folder/f'{stem}_{width}'
        assert path.with_suffix('.cnf').stat().st_size and path.with_suffix('.lrat').stat().st_size
        for suffix in ('.lrat.log', '.replay.log', '.fresh.log'):
            assert MARKER in path.with_suffix(suffix).read_text(encoding='ascii').splitlines(), (stem, suffix)
    checked = [match.groups() for line in fresh.read_text(encoding='ascii').splitlines()
               if (match := REBIND.fullmatch(line))]
    assert checked == [(stem, choice) for stem, _, choice in routes], fresh
    return Counter((attempt, choice) for _, attempt, choice in routes)


def audit(trace, prefix, stride):
    stats = Counter()
    for offset in range(stride):
        folder = Path(f'{prefix}.{offset}' if stride > 1 else prefix)
        expected = [f'{index}_{lift}' for index, lift in selected(trace, stride, offset)]
        assert expected
        stats.update(recheck(Path(f'{folder}.log'), Path(f'{folder}.rebind.log'), folder, expected))
    print('exact ordered proof and recheck rosters:', sum(stats.values()), dict(stats), flush=True)


def calibrate(controls, folder):
    folder.mkdir()
    source = controls.resolve()
    for label, stem in (('negative_first_narrow', '0_0_narrow'), ('negative_only_wide', '0_1_wide')):
        for suffix in ('.cnf', '.lrat', '.lrat.log', '.replay.log', '.fresh.log'):
            (folder/f'{stem}{suffix}').symlink_to(source/f'{label}{suffix}')
    records, fresh = folder/'routes.log', folder/'fresh.log'
    good_routes = '0_0 CHECKED NARROW encode_bind_cpu=0.000\n0_1 NOT_RUN WIDE_CHECKED encode_bind_cpu=0.000\n'
    good_fresh = '0_0 NARROW\n0_1 WIDE_CHECKED\n'
    for bad, fresh_rows in ((None, good_fresh), (good_routes.replace('NOT_RUN', 'MISMATCH'), good_fresh),
                            (good_routes, good_fresh.replace('0_1', '0_2'))):
        records.write_text(bad or good_routes, encoding='ascii')
        fresh.write_text(fresh_rows, encoding='ascii')
        try:
            answer = recheck(records, fresh, folder, ['0_0', '0_1'])
        except AssertionError:
            assert bad is not None
        else:
            assert bad is None and answer == {('CHECKED', 'NARROW'): 1, ('NOT_RUN', 'WIDE_CHECKED'): 1}
    print('six-site roster controls: both checked routes accepted; misbinding and wrong fresh ID rejected', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    runner = commands.add_parser('run')
    runner.add_argument('mode', choices=('wide', 'narrow'))
    for key in ('cover', 'trace', 'folder'):
        runner.add_argument(key, type=Path)
    runner.add_argument('--stride', type=int, default=1)
    runner.add_argument('--offset', type=int, default=0)
    runner.add_argument('--mib', type=int, default=150)
    auditing = commands.add_parser('audit')
    auditing.add_argument('trace', type=Path)
    auditing.add_argument('prefix')
    auditing.add_argument('--stride', type=int, default=1)
    control = commands.add_parser('calibrate')
    control.add_argument('controls', type=Path)
    control.add_argument('folder', type=Path)
    args = parser.parse_args()
    if args.command == 'run':
        run(args.cover, args.trace, args.folder, args.mode, args.stride, args.offset, args.mib)
    elif args.command == 'audit':
        audit(args.trace, args.prefix, args.stride)
    else:
        calibrate(args.controls, args.folder)
