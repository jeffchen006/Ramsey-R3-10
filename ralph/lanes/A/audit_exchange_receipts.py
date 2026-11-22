#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re

from audit_panel_receipts import (HEXHASH, SIZE, audit_metadata, audit_terminal, demand, load_census,
                                  ordered, published_reports, terminal_rows, text_rows)


CUT = 24576
KINDS = ('ordered', 'LL', 'LH', 'HL', 'HH', 'HHrep', 'HHdiag', 'HHlower', 'LLupper', 'LLlower')
EMPTY = sha256(b'').hexdigest()


@dataclass(frozen=True)
class Binding:
    zero: int
    one: int
    digest: str

    def pair(self):
        return self.zero, self.one

    def total(self):
        return self.zero + self.one


def load_exchange(path, original, full):
    roster = {}
    for line in path.read_text().splitlines():
        low, high, kind, count0, count1, digest = line.split()
        interval = (int(low), int(high))
        binding = Binding(int(count0), int(count1), digest)
        key = (*interval, kind)
        demand(key not in roster and HEXHASH.fullmatch(digest) and min(binding.pair()) >= 0 and
               (binding.total() == 0) == (digest == EMPTY), f'malformed exchange binding: {line}')
        roster[key] = binding
    demand(roster.pop((0, SIZE, 'full')) == full, 'full ordered roster changed')
    low_intervals = [(low, high) for low, high in original if high <= CUT]
    high_intervals = [(low, min(SIZE, low + 1024)) for low in range(CUT, SIZE, 1024)]
    intervals = low_intervals + high_intervals
    demand(set(roster) == {(*interval, kind) for interval in intervals for kind in KINDS},
           'exchange census lost/added a domain or shard')
    for interval in low_intervals:
        demand(roster[(*interval, 'ordered')] == Binding(*original[interval]), f'ordered prefix roster changed at {interval}')
    for interval in intervals:
        rows = {kind: roster[(*interval, kind)] for kind in KINDS}
        for index in range(2):
            count = {kind: rows[kind].pair()[index] for kind in KINDS}
            demand(count['ordered'] == sum(count[key] for key in ('LL', 'LH', 'HL', 'HH')) and
                   count['HH'] == count['HHrep'] + count['HHlower'] and count['HHdiag'] <= count['HHrep'],
                   f'nonpartitioned domains at {interval}/{index}')
            must_be_empty = ('HL', 'HH') if interval[0] < CUT else ('LL', 'LH')
            demand(all(count[kind] == 0 for kind in must_be_empty), f'wrong exchange domain at {interval}/{index}')
    totals = {kind: tuple(sum(roster[(*interval, kind)].pair()[index] for interval in intervals) for index in range(2))
              for kind in KINDS}
    for index in range(2):
        count = {kind: totals[kind][index] for kind in KINDS}
        demand(count['ordered'] == full.pair()[index] and count['LH'] == count['HL'] and
               count['HHlower'] == count['HHrep'] - count['HHdiag'] and count['LLupper'] == count['LLlower'],
               f'global exchange multiplicities broken at map bit {index}')
    expected = {'LL': 27198813, 'LH': 40218398, 'HL': 40218398, 'HH': 49836392,
                'HHrep': 24924719, 'HHdiag': 13046}
    demand(all(sum(totals[kind]) == value for kind, value in expected.items()), 'wrong full block inventory')
    return roster, low_intervals, high_intervals, totals


def prefix_receipts(path, intervals, original, round13):
    reports = published_reports(path)
    demand(list(reports) == intervals, 'not exactly the original 12 ordered receipts')
    pilot = {row[:3]: row for row, _ in terminal_rows(round13 / 'C.terminal.tsv') if row[0] < intervals[0][1]}
    demand(bool(pilot), 'missing original pilot controls')
    terminal_hash = sha256()
    for interval, (shard, summary) in reports.items():
        audit_metadata(shard, summary, original[interval])
        _, _, canonical = audit_terminal(shard, summary, pilot if interval == intervals[0] else {})
        demand(summary['unresolved'] == 0, f'{shard}: old ordered negative not established')
        terminal_hash.update(canonical)
    demand(terminal_hash.hexdigest() == 'b41dddffbf00ade7f4c669b9456d5c707deda28c585bd5d2197c81a4bbd935bf',
           'old negative receipt bindings changed')


def upper_terminal(shard, summary):
    panel = list(text_rows(shard / 'panels.ids', 3))
    terminals = [list(terminal_rows(shard / name)) for name in ('C.terminal', 'scout.terminal')]
    keyed_path = shard / 'terminal.keyed'
    keyed = list(text_rows(keyed_path, 8))
    demand(len(panel) == summary['counts'][4] and [row[:3] for row in keyed] == panel and
           all([row for row, _ in reports] == keyed for reports in terminals), f'{shard}: terminal ID/reason mismatch')
    previous = None
    for item in panel:
        ordered(item, previous, summary['low'], summary['high'])
        demand(item[0] <= item[1], f'{shard}: non-upper terminal ID')
        previous = item
    canonical = ''.join(' '.join(map(str, row)) + '\n' for row in keyed).encode()
    demand(canonical == keyed_path.read_bytes() and sha256(canonical).hexdigest() == summary['terminal_sha256'],
           f'{shard}: terminal digest mismatch')
    fills = [sum(row[index] for row in keyed) for index in range(3, 8)]
    counts = [sum(row[3:]) for row in keyed]
    tails = [max((elapsed for _, elapsed in reports), default=0.0) for reports in terminals]
    demand(fills[-1] == summary['unresolved'] == 0 and
           (fills, sum(count > 0 for count in counts), max(counts, default=0), tails) ==
           (summary['fillings'], summary['joint'], summary['max_fill'], summary['tail_ms']),
           f'{shard}: live filling or incorrect terminal summary')
    return canonical


def upper_receipt(shard, summary, expected, diagonal):
    low, high = summary['low'], summary['high']
    counts = summary['counts']
    raw_per_map = (high - low) * (2 * SIZE - low - high + 1) // 2
    demand(len(counts) == 5 and counts == sorted(counts, reverse=True) and counts[-1] >= 0 and
           counts[0] == expected.total() and summary['roster_sha256'] == expected.digest,
           f'{shard}: wrong upper roster or stage totals')
    demand(summary['diagonal'] == diagonal.total() and summary['by_exchange'] == expected.total() - diagonal.total(),
           f'{shard}: wrong reported diagonal or transfer total')
    demand(summary['raw'] == 2 * raw_per_map, f'{shard}: wrong upper raw domain')
    screen = json.loads((shard / 'screen.json').read_text())
    for key in ('low', 'high', 'counts', 'roster_sha256', 'stage_sha256'):
        demand(screen[key] == summary[key], f'{shard}: screen/receipt disagree at {key}')
    demand(HEXHASH.fullmatch(summary['stage_sha256']), f'{shard}: invalid stage digest')
    rows = {}
    for line in (shard / 'A.screen.log').read_text().splitlines():
        match = re.fullmatch(r'flip=([01]) raw/header/fwd/rev/local/panel: (.*)', line)
        if match:
            flip = int(match[1])
            demand(flip not in rows, f'{shard}: duplicate scanner map counter')
            rows[flip] = tuple(map(int, match[2].split()))
    demand(set(rows) == {0, 1} and all(len(row) == 6 for row in rows.values()), f'{shard}: bad scanner map counters')
    for flip in range(2):
        demand(rows[flip][:2] == (raw_per_map, expected.pair()[flip]), f'{shard}: map bit {flip} census differs')
    demand(list(map(sum, zip(*rows.values())))[1:] == counts, f'{shard}: per-map counts do not reconstruct')
    return upper_terminal(shard, summary)


def coverage(roster, low_intervals, high_intervals, reports, stream, require_full):
    demand(set(reports) <= set(high_intervals), 'new receipts are not from disjoint HH representative shards')
    terminal_hash = sha256()
    print('low high basis direct_scans by_exchange unresolved_ordered ordered_covered_or_queued', file=stream)
    direct = exchange = unresolved = 0
    for interval in low_intervals:
        direct_here = roster[(*interval, 'ordered')].total()
        exchange_here = roster[(*interval, 'LH')].total()
        direct += direct_here
        exchange += exchange_here
        print(*interval, 'ordered-prefix', direct_here, exchange_here, 0, direct_here + exchange_here, file=stream)
    for interval in high_intervals:
        representative = roster[(*interval, 'HHrep')]
        diagonal = roster[(*interval, 'HHdiag')]
        both = 2 * representative.total() - diagonal.total()
        if interval in reports:
            shard, summary = reports[interval]
            terminal_hash.update(upper_receipt(shard, summary, representative, diagonal))
            direct_here = representative.total()
            exchange_here = both - direct_here
            direct += direct_here
            exchange += exchange_here
            print(*interval, 'HH-representative', direct_here, exchange_here, 0, both, file=stream)
        else:
            unresolved += both
            print(*interval, 'HH-unresolved', 0, 0, both, both, file=stream)
    demand(direct + exchange + unresolved == 157472001, 'coverage totals do not partition the original ordered inventory')
    demand(not require_full or len(reports) == len(high_intervals), 'HH representative partition incomplete')
    print(0, SIZE, 'full', direct, exchange, unresolved, direct + exchange + unresolved, file=stream)
    print(f'HH verified negative receipts: {len(reports)}/{len(high_intervals)}; aggregate terminal SHA256 {terminal_hash.hexdigest()}')
    print(f'direct={direct} by_exchange={exchange} unresolved_ordered={unresolved}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('exchange', type=Path)
    parser.add_argument('old_census', type=Path)
    parser.add_argument('old_full', type=Path)
    parser.add_argument('old_reports', type=Path)
    parser.add_argument('round13', type=Path)
    parser.add_argument('coverage', type=Path)
    parser.add_argument('--reports', type=Path)
    parser.add_argument('--require-full', action='store_true')
    args = parser.parse_args()
    low, high, count0, count1, digest = args.old_full.read_text().split()
    demand((int(low), int(high)) == (0, SIZE), 'wrong original full census range')
    original = load_census(args.old_census)
    rows, low_intervals, high_intervals, totals = load_exchange(args.exchange, original, Binding(int(count0), int(count1), digest))
    prefix_receipts(args.old_reports, low_intervals, original, args.round13)
    print(f'original negative coverage: {len(low_intervals)} ordered receipts')
    print('per-map census:', json.dumps(totals, sort_keys=True))
    reports = published_reports(args.reports) if args.reports else {}
    temporary = args.coverage.with_suffix(args.coverage.suffix + '.tmp')
    try:
        with temporary.open('w') as stream:
            coverage(rows, low_intervals, high_intervals, reports, stream, args.require_full)
        temporary.replace(args.coverage)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
