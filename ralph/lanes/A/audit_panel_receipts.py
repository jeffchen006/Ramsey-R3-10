#!/usr/bin/env python3
import argparse
from collections import Counter
import gzip
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
import re
from struct import Struct


SIZE = 55055
FIRST = 2048
RECORD = Struct('<HHHH')
INTERVAL_NAME = re.compile(r'[0-9]{5}-[0-9]{5}')
HEXHASH = re.compile(r'[a-f0-9]{64}')


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def valid_id(item, low, high):
    return low <= item[0] < high and 0 <= item[1] < SIZE and item[2] in (0, 1)


def ordered(item, prior, low, high):
    if not valid_id(item, low, high):
        raise ValueError(f'ID outside shard or bad map bit: {item}')
    if prior is not None and prior >= item:
        raise ValueError(f'duplicate or unordered ID: {item}')


def check_partition(intervals, end=None):
    cursor = 0
    for low, high in intervals:
        demand(low == cursor and low < high <= SIZE, f'gap or shared left IDs at shard {(low, high)}; expected {cursor}')
        cursor = high
    demand(cursor > 0 and (end is None or cursor == end), f'incomplete partition ends at {cursor}')
    return cursor


def text_rows(path, width):
    with path.open() as stream:
        for line in stream:
            values = line.split()
            demand(len(values) == width, f'{path}: malformed record')
            yield tuple(map(int, values))


def terminal_rows(path):
    with path.open() as stream:
        for line in stream:
            values = line.split()
            demand(len(values) == 9, f'{path}: malformed terminal')
            counts = tuple(map(int, values[:8]))
            elapsed = float(values[8])
            demand(all(value >= 0 for value in counts) and math.isfinite(elapsed) and elapsed >= 0,
                   f'{path}: invalid terminal value')
            yield counts, elapsed


def load_census(path):
    lines = path.read_text().splitlines()
    demand(lines[0] == 'low high flip0 flip1 sha256_canonical_packed', 'unexpected census header')
    result = {}
    for line in lines[1:]:
        low, high, zero, one, digest = line.split()
        interval = int(low), int(high)
        demand(interval not in result and HEXHASH.fullmatch(digest), f'invalid expected census row {line}')
        result[interval] = int(zero), int(one), digest
    check_partition(result, SIZE)
    demand(sum(zero + one for zero, one, _ in result.values()) == 157472001, 'wrong full census total')
    return result


def published_reports(path):
    reports = {}
    for shard in sorted(path.iterdir()):
        if not INTERVAL_NAME.fullmatch(shard.name) or not (shard / 'result.json').is_file():
            continue
        summary = json.loads((shard / 'result.json').read_text())
        interval = tuple(map(int, shard.name.split('-')))
        demand((summary['low'], summary['high']) == interval, f'interval mismatch: {shard}')
        reports[interval] = shard, summary
    return reports


def audit_terminal(shard, summary, pilot):
    low, high = summary['low'], summary['high']
    panel = list(text_rows(shard / 'panels.ids', 3))
    previous = None
    for item in panel:
        ordered(item, previous, low, high)
        previous = item
    demand(len(panel) == summary['counts'][4], f'{shard}: wrong panel count')
    producer = list(terminal_rows(shard / 'C.terminal'))
    scout = list(terminal_rows(shard / 'scout.terminal'))
    keyed = list(text_rows(shard / 'terminal.keyed', 8))
    demand([row[:3] for row in keyed] == panel, f'{shard}: terminal has missing/extra/misordered IDs')
    demand([row for row, _ in producer] == [row for row, _ in scout] == keyed,
           f'{shard}: terminal reason vectors disagree')
    canonical = ''.join(' '.join(map(str, row)) + '\n' for row in keyed).encode()
    demand(sha256(canonical).hexdigest() == summary['terminal_sha256'] and
           canonical == (shard / 'terminal.keyed').read_bytes(), f'{shard}: terminal digest mismatch')
    unresolved = [row for row in keyed if row[7] > 0]
    demand(list(text_rows(shard / 'unresolved.tsv', 8)) == unresolved, f'{shard}: unresolved ID roster')
    fills = [sum(row[column] for row in keyed) for column in range(3, 8)]
    joint = sum(sum(row[3:]) > 0 for row in keyed)
    maximum = max((sum(row[3:]) for row in keyed), default=0)
    tails = [max((elapsed for _, elapsed in scanner), default=0.0) for scanner in (producer, scout)]
    demand((fills, joint, maximum, len(unresolved), tails) ==
           (summary['fillings'], summary['joint'], summary['max_fill'], summary['unresolved'], summary['tail_ms']),
           f'{shard}: terminal summary does not reconstruct')
    seen = {}
    for row in keyed:
        item = row[:3]
        if item in pilot:
            demand(pilot[item] == row, f'{shard}: former pilot terminal changed at {item}')
            seen[item] = row
    demand(pilot == seen, f'{shard}: former pilot terminal ID missing')
    return panel, fills, canonical


def audit_metadata(shard, summary, expected):
    low, high = summary['low'], summary['high']
    count0, count1, digest = expected
    counts = summary['counts']
    demand(len(counts) == 5 and counts == sorted(counts, reverse=True) and counts[-1] >= 0,
           f'{shard}: malformed stage totals')
    demand(counts[0] == count0 + count1 and summary['roster_sha256'] == digest,
           f'{shard}: independently generated header identity differs')
    demand(summary['raw'] == (high-low) * SIZE * 2, f'{shard}: wrong raw domain')
    screen = json.loads((shard / 'screen.json').read_text())
    for key in ('low', 'high', 'counts', 'roster_sha256', 'stage_sha256'):
        demand(screen[key] == summary[key], f'{shard}: screen/result mismatch: {key}')
    demand(HEXHASH.fullmatch(summary['stage_sha256']), f'{shard}: malformed stage digest')
    depth_counts = {}
    for line in (shard / 'A.screen.log').read_text().splitlines():
        match = re.fullmatch(r'flip=([01]) raw/header/fwd/rev/local/panel: (.*)', line)
        if match:
            flip = int(match[1])
            demand(flip not in depth_counts, f'{shard}: duplicate scanner count vector')
            depth_counts[flip] = tuple(map(int, match[2].split()))
    demand(set(depth_counts) == {0, 1} and all(len(row) == 6 for row in depth_counts.values()),
           f'{shard}: malformed scanner count vectors')
    for flip, expected_count in enumerate((count0, count1)):
        demand(depth_counts[flip][:2] == ((high-low) * SIZE, expected_count),
               f'{shard}: map bit {flip} census differs')
    demand(list(map(sum, zip(depth_counts[0], depth_counts[1])))[1:] == counts,
           f'{shard}: per-map counts do not reconstruct')


def archive_depths(path):
    entries = {}
    for left, right, flip, depth in text_rows(path, 4):
        if not 0 <= left < FIRST:
            continue
        item = left, right, flip
        demand(valid_id(item, 0, FIRST) and item not in entries and 1 <= depth <= 5,
               f'{path}: malformed round-13 control: {item}')
        entries[item] = depth
    demand(entries, f'{path}: empty historical control intersection')
    return entries


def audit_stream(stream, interval, control_left, control_pilot):
    low, high = interval
    raw, ids = sha256(), sha256()
    by_flip, at_depth = [0, 0], [0] * 6
    prior = witness = None
    panel, seen_left, seen_pilot = [], {}, {}
    while chunk := stream.read(1 << 20):
        demand(len(chunk) % RECORD.size == 0, 'partial packed stage record')
        raw.update(chunk)
        for left, right, flip, depth in RECORD.iter_unpack(chunk):
            item = left, right, flip
            ordered(item, prior, low, high)
            if not 1 <= depth <= 5:
                raise ValueError(f'invalid depth for {item}: {depth}')
            if prior is not None and prior[:2] == item[:2] and witness is None:
                witness = item[:2]
            prior = item
            by_flip[flip] += 1
            at_depth[depth] += 1
            if depth == 5:
                panel.append(item)
            if item in control_left:
                seen_left[item] = depth
            if item in control_pilot:
                seen_pilot[item] = depth
        normalized = bytearray(chunk)
        normalized[6::8] = bytes(len(chunk) // RECORD.size)
        ids.update(normalized)
    demand(seen_left == control_left, 'left-triple stage control missing or changed')
    demand(seen_pilot == control_pilot, 'former-pilot stage control missing or changed')
    return by_flip, [sum(at_depth[index:]) for index in range(1, 6)], ids.hexdigest(), raw.hexdigest(), panel, witness


def negative_controls(witness):
    left, right = witness
    zero = RECORD.pack(left, right, 0, 1)
    one = RECORD.pack(left, right, 1, 1)

    def certify_pair(data):
        by_flip, _, _, digest, _, _ = audit_stream(BytesIO(data), (0, FIRST), {}, {})
        demand(by_flip == [1, 1] and digest == sha256(zero + one).hexdigest(), 'map roster altered')

    certify_pair(zero + one)
    for label, test in (
        ('dropped-map-row', lambda: certify_pair(zero)),
        ('constant-count-overwritten-map-bit', lambda: certify_pair(zero + zero)),
        ('shared-boundary-interval', lambda: check_partition(((0, FIRST), (FIRST-1, SIZE)), SIZE)),
        ('shared-boundary-ID', lambda: audit_stream(BytesIO(RECORD.pack(FIRST, right, 0, 1)), (0, FIRST), {}, {})),
        ('dropped-terminal-input', lambda: list(terminal_rows(Path('/dev/null/no-terminal-record')))),
    ):
        try:
            test()
        except (ValueError, OSError) as error:
            print(f'adverse {label}: rejected ({error})')
        else:
            raise ValueError(f'adverse {label} passed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('census', type=Path)
    parser.add_argument('reports', type=Path)
    parser.add_argument('round13', type=Path)
    parser.add_argument('--first-stream', type=Path)
    parser.add_argument('--require-full', action='store_true')
    args = parser.parse_args()
    census = load_census(args.census)
    reports = published_reports(args.reports)
    end = check_partition(reports, SIZE if args.require_full else None)
    demand(next(iter(reports)) == (0, FIRST), 'missing complete first shard')
    pilot = {row[:3]: row for row, _ in terminal_rows(args.round13 / 'C.terminal.tsv') if row[0] < FIRST}
    demand(pilot, 'empty historical pilot terminal intersection')
    totals = [0] * 5
    fillings = [0] * 5
    joint = unresolved = 0
    first_panel = None
    terminal_stream = sha256()
    for interval, (shard, summary) in reports.items():
        audit_metadata(shard, summary, census[interval])
        panel, fills, canonical = audit_terminal(shard, summary, pilot if interval == (0, FIRST) else {})
        terminal_stream.update(canonical)
        if interval == (0, FIRST):
            first_panel = panel
        totals = list(map(sum, zip(totals, summary['counts'])))
        fillings = list(map(sum, zip(fillings, fills)))
        joint += summary['joint']
        unresolved += summary['unresolved']
        print(f'shard {interval[0]} {interval[1]} header/terminal PASS', *summary['counts'], summary['joint'], summary['unresolved'])
    print(f'partition [0,{end}) {len(reports)} shards: stages={totals} joint={joint} unresolved={unresolved} fillings={fillings}')
    print(f'partition terminal stream SHA256 {terminal_stream.hexdigest()}')
    print(f'first terminal former-pilot positive coverage: {len(pilot)} complete reason vectors')

    if args.first_stream:
        triple = archive_depths(args.round13 / 'A.triple.stages')
        archived_pilot = archive_depths(args.round13 / 'A.pilot.stages')
        demand(not triple.keys() & archived_pilot.keys() and not any(depth == 5 for depth in triple.values()),
               'bad triple/pilot controls')
        wanted = {item for item, depth in archived_pilot.items() if depth == 5}
        demand(wanted == pilot.keys(), 'historical pilot stages and terminal roster disagree')
        opener = (args.first_stream.open('rb') if args.first_stream.suffix != '.gz'
                  else gzip.open(args.first_stream, 'rb'))
        with opener as stream:
            by_flip, stage_counts, ids, stages, panel, witness = audit_stream(stream, (0, FIRST), triple, archived_pilot)
        _, summary = reports[(0, FIRST)]
        demand((*by_flip, ids) == census[(0, FIRST)] and stage_counts == summary['counts'] and
               stages == summary['stage_sha256'] and panel == first_panel, 'packed merged stage stream not bound')
        demand(witness is not None, 'no control with same frame pair and both map bits')
        print(f'first packed stream PASS: flips={by_flip} stages={stage_counts}, exact panel IDs={len(panel)}')
        print(f'first depth controls PASS: left-triple={len(triple)} former-pilot={len(archived_pilot)}, both-map witness={witness}')
        negative_controls(witness)
    else:
        print('packed first stream not supplied: full first depth/ID audit still pending')


if __name__ == '__main__':
    main()
