#!/usr/bin/env python3
"""Audit the exact profile-A case index and freeze completed proof bundles."""

import argparse
import ast
from collections import Counter
import hashlib
from pathlib import Path
import re

from audit_m11 import audit, read_json


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('graph', 'freeze'))
    parser.add_argument('--stride', type=int, default=16)
    parser.add_argument('--with-rescue', action='store_true')
    args = parser.parse_args()
    covers = [Path(f'cover.a{index}.jsonl') for index in range(19)]
    graph_certs = [Path(f'checked.a{index}.jsonl') for index in range(19)]
    plan_file = Path('plan.a11.tsv')
    expected = [tuple(map(int, row.split())) for row in plan_file.read_text(encoding='ascii').splitlines()]
    assert expected == sorted(set(expected))
    if args.mode == 'graph':
        actual = []
        totals = Counter()
        for index, (cover, report) in enumerate(zip(covers, graph_certs)):
            todo, stats = audit(read_json(cover), read_json(report), True)
            actual.extend((index, row) for row in todo)
            totals.update(stats)
            print('core', index, stats['rows'], stats['projection_witness'], len(todo), sha(cover), sha(report), flush=True)
        assert actual == expected
        print('all graph traces checked and plan matched:', dict(totals), flush=True)
        return

    paths = [*covers, *graph_certs, plan_file, Path('graph.a11.replay.log'),
             Path('../r5_saturated/e11.g6'), Path('profile_a_pilot.log'),
             *sorted(Path().glob('profile_a.[0-5].log'))]
    root = Path('proof.a11')
    total = Counter()
    timing_cpu = 0.0
    terminal = []
    for offset in range(args.stride):
        bind = root/f'bind.{offset}.jsonl'
        worker = root/f'worker.{offset}.log'
        log = worker.read_text(encoding='ascii')
        end = re.search(r'^batch \((\d+), (\d+)\) (\{.+\})$', log, re.M)
        timing = re.search(r'^wall=([0-9.]+) cpu=([0-9.]+)\+([0-9.]+) RSS=', log, re.M)
        assert end and timing and tuple(map(int, end.groups()[:2])) == (offset, args.stride), offset
        timing_cpu += float(timing[2])+float(timing[3])
        rows = list(read_json(bind))
        assert [tuple(row[:2]) for row in rows] == expected[offset::args.stride], offset
        statuses = Counter()
        for core, row, status, cnf_hash, proof_hash, _wall in rows:
            assert re.fullmatch(r'[a-f0-9]{64}', cnf_hash)
            statuses[status] += 1
            if status == 'CHECKED':
                proof = root/str(core)/f'{row}.lrat'
                assert sha(proof) == proof_hash, (core, row)
                paths.append(proof)
            else:
                terminal.append((core, row, status))
        assert dict(statuses) == ast.literal_eval(end[3]), offset
        total.update(statuses)
        paths.extend((bind, worker))
    print('all terminal plan/status bindings:', dict(total), flush=True)
    print('measured production CPU hours:', round(timing_cpu/3600, 4), flush=True)
    assert sum(total.values()) == len(expected)
    if terminal:
        exceptional = Path('profile_a11.open.tsv')
        exceptional.write_text(''.join(f'{core}\t{row}\t{status}\n' for core, row, status in sorted(terminal)),
                               encoding='ascii')
        print('PRIMARY EXCEPTION RECORDS:', len(terminal), flush=True)
        if not args.with_rescue:
            return
        from types import SimpleNamespace
        from rescue_a11 import cover_file

        trace = Path('rescue.a11.jsonl')
        directory = Path('rescue.a11')
        stats = cover_file(exceptional, trace, True, SimpleNamespace(prove=directory, cap=12))
        assert stats['projections'] == len(terminal)
        assert stats['lrat_checked'] + stats['checked'] == stats['omitted_supports']
        paths.extend((exceptional, trace, *sorted(directory.glob('*.cnf')), *sorted(directory.glob('*.lrat'))))
        print('all primary exceptions excluded by the omitted-group rescue:', dict(stats), flush=True)
    assert 'all graph traces checked and plan matched:' in Path('graph.a11.replay.log').read_text(encoding='ascii')
    frozen = Path('profile_a11.certificates.sha256')
    with frozen.open('w', encoding='ascii') as manifest:
        for path in paths:
            print(f'{sha(path)}  {path}', file=manifest)
    print(sha(frozen), frozen, flush=True)


if __name__ == '__main__':
    main()
