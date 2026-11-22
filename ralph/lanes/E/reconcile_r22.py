#!/usr/bin/env python3
"""Check independent proof partitions and report CPU accounting for round 22."""

import argparse
from collections import Counter
from datetime import datetime, timedelta
import json
from pathlib import Path
import re


PIECES = {6: 6, 9: 13, 18: 6}


def reconcile():
    total = 0
    for core, pieces in PIECES.items():
        root = Path(f'audit.{core}.final')
        checked = [tuple(json.loads(line)) for line in (root/'checked.jsonl').read_text().splitlines()]
        assert not (root/'residual.jsonl').read_bytes() and not (root/'unfinished-shards.jsonl').read_bytes()
        assert checked == sorted(set(checked))
        seen = []
        for offset in range(pieces):
            source = Path(f'recheck.{core}.{offset}.log').read_text().splitlines()
            assert source[-1].endswith('exit=0'), (core, offset)
            assert any(line.startswith(f'complete recheck partition {core} {offset} {pieces} ') for line in source)
            got = []
            for line in source:
                if line.startswith('DUAL_RECHECK '):
                    _, case, index, ordinal, width, proof_hash = line.split()
                    assert int(case) == core
                    got.append((int(index), int(ordinal), int(width), proof_hash))
            assert got == checked[offset::pieces], (core, offset)
            seen.extend(got)
        assert sorted(seen) == checked
        print(f'core {core}: {pieces} disjoint replay subsets, {len(seen)}/{len(checked)} fresh dual rechecks, zero residual')
        total += len(seen)
    print('total fresh dual rechecks:', total)


def accounting():
    jobs = []
    for row in Path('jobs.tsv').read_text().splitlines():
        pid, start, deadline, slots, log, command = row.split('\t', maxsplit=5)
        jobs.append((int(pid), datetime.fromisoformat(start), datetime.fromisoformat(deadline), int(slots), log, command))
    exits = {}
    for row in Path('exits.tsv').read_text().splitlines():
        time, log, status = row.split('\t')
        assert log not in exits
        exits[log] = datetime.fromisoformat(time), int(status)
    terminated = [job for job in jobs if re.fullmatch(r'worker\.6\.([0-9]|1[0-9]|2[01])\.log', job[4])]
    assert len(terminated) == 22
    last = max(end for end, _ in exits.values())
    first = min(job[1] for job in jobs)
    measurement = re.compile(r'wall=([0-9.]+) cpu=([0-9.]+)\+([0-9.]+) RSS=(\d+) exit=(\d+)')
    categories, statuses = Counter(), Counter()
    occupancy = []
    peak = 0
    for pid, start, deadline, slots, log, _ in jobs:
        line = (Path(log).read_text().splitlines() or [''])[-1]
        match = measurement.fullmatch(line)
        if match is None:
            assert log in {job[4] for job in terminated}, (pid, log, line)
            statuses['operator_terminated_EXDEV'] += 1
            end = min(deadline, datetime.fromisoformat('2026-11-22T19:27:35+01:00'))
        else:
            wall, user, sys, rss = map(float, match.groups()[:4])
            exit_code = int(match[5])
            end = exits[log][0] if log in exits else start + timedelta(seconds=wall)
            statuses[f'exit_{exit_code}'] += 1
            categories[log.split('.')[0]] += user + sys
            peak = max(peak, int(rss))
        occupancy.append((start, end, slots))
    elapsed = (last-first).total_seconds()
    subtotal = sum(categories.values())
    print('normal/time-measured wrappers', dict(statuses), 'CPU-s by class:', dict(categories))
    print(f'{subtotal:.2f} measured CPU-s ({subtotal/3600:.4f} h) / {elapsed:.0f} elapsed s; '
          f'{subtotal/elapsed:.2f} mean measured cores; peak measured per-wrapper RSS {peak} KiB')
    print('Missing CPU object: 22 EXDEV stops, not TIMEOUTs; maximum extra from observed stop window '
          f'{sum((datetime.fromisoformat("2026-11-22T19:27:35+01:00")-job[1]).total_seconds() for job in terminated):.0f} CPU-s')
    for minute in (25, 30, 35, 40):
        mark = datetime.fromisoformat(f'2026-11-22T19:{minute:02}:00+01:00')
        print('scheduled slots at', mark.isoformat(), sum(slots for start, end, slots in occupancy if start <= mark < end))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proofs-only', action='store_true')
    args = parser.parse_args()
    reconcile()
    if not args.proofs_only:
        accounting()
