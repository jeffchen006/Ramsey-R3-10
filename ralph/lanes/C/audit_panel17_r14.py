#!/usr/bin/env python3
import argparse
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import Path

from panel17_round14 import FRAME_COUNT, HEADER_COUNT, RECORD, check, merge, read_terminal


def controls():
    rows = [(0, 0, 0, 1), (0, 0, 1, 5), (0, 1, 0, 4)]
    stream = b''.join(RECORD.pack(*row) for row in rows)
    roster = b''.join(RECORD.pack(*row[:3], 0) for row in rows)
    panels = StringIO()
    counts, ids, stages = merge(BytesIO(stream), BytesIO(stream), panels, 0, 1)
    check(counts == [3, 2, 2, 2, 1] and panels.getvalue() == '0 0 1\n' and
          (ids, stages) == (sha256(roster).hexdigest(), sha256(stream).hexdigest()), 'positive stream fixture')
    for invalid in (stream[:-8], stream[:8] + stream[:8] + stream[16:], stream[:14] + b'\x04' + stream[15:]):
        try:
            merge(BytesIO(stream), BytesIO(invalid), StringIO(), 0, 1)
        except RuntimeError:
            continue
        raise RuntimeError('accepted missing map, duplicate or altered stage')
    print('binary merge: 1 exact fixture and 3 adverse controls PASS')


def audit(work, reference):
    expected = {}
    with reference.open() as table:
        check(next(table).split() == ['low', 'high', 'flip0', 'flip1', 'sha256_canonical_packed'], 'A table format')
        last = 0
        for line in table:
            low, high, flip0, flip1, digest = line.split()
            low, high = int(low), int(high)
            check(low == last and high > low, 'A table partition')
            expected[(low, high)] = (int(flip0), int(flip1), digest)
            last = high
        check(last == FRAME_COUNT and sum(flip0 + flip1 for flip0, flip1, _ in expected.values()) == HEADER_COUNT,
              'A table scope')
    last = 0
    summed = [0] * 5
    fills = [0] * 5
    maximum = joint = total_cpu = screen_cpu = 0
    tail = [0, 0]
    terminal_stream = sha256()
    stage_tree = sha256()
    terminal_opens = []
    pending_panels = []
    coverage_rows = ['low\thigh\tflip0\tflip1\theader\tforward\treverse\tlocal\tpanel\tjoint\topen\t'
                     'ID_SHA256\tstage_SHA256\tterminal_SHA256']
    for path in sorted(work.glob('[0-9]*-[0-9]*')):
        result_path = path / 'result.json'
        if not result_path.exists():
            if (path / 'unresolved.tsv').exists():
                terminal_opens += (path / 'unresolved.tsv').read_text().splitlines()
            if (path / 'panels.ids').exists():
                pending_panels += (path / 'panels.ids').read_text().splitlines()
            break
        record = json.loads(result_path.read_text())
        low, high = record['low'], record['high']
        check(low == last and high > low and path.name == f'{low:05d}-{high:05d}', 'production partition')
        last = high
        flip0, flip1, digest = expected[(low, high)]
        check(record['counts'][0] == flip0 + flip1 and record['roster_sha256'] == digest, f'{path}: A header mismatch')
        observed = [tuple(map(int, line.split(':')[1].split())) for line in (path / 'A.screen.log').read_text().splitlines()
                    if line.startswith('flip=')]
        check(len(observed) == 2 and [stage[1] for stage in observed] == [flip0, flip1], 'flip counts')
        check(all(stage[0] == FRAME_COUNT * (high - low) for stage in observed) and
              [sum(pair) for pair in zip(*observed)][1:] == record['counts'], 'A stage counts')
        check(all(earlier >= later for earlier, later in zip(record['counts'], record['counts'][1:])), 'stage monotonicity')
        panel_ids = [tuple(map(int, line.split())) for line in (path / 'panels.ids').read_text().splitlines()]
        check(len(panel_ids) == record['counts'][4] and all(low <= left < high and 0 <= right < FRAME_COUNT and flip in (0, 1)
              for left, right, flip in panel_ids) and all(first < second for first, second in zip(panel_ids, panel_ids[1:])),
              'panel roster range/order')
        details = [row for row, _ in read_terminal(path / 'C.terminal', panel_ids)]
        independently = [row for row, _ in read_terminal(path / 'scout.terminal', panel_ids)]
        canonical = ''.join(' '.join(map(str, row)) + '\n' for row in details).encode()
        check(details == independently and canonical == (path / 'terminal.keyed').read_bytes() and
              sha256(canonical).hexdigest() == record['terminal_sha256'], 'terminal binding')
        terminal_stream.update(canonical)
        stage_tree.update(f"{low} {high} {record['stage_sha256']}\n".encode())
        openings = [' '.join(map(str, row)) for row in details if row[-1] > 0]
        these_fills = [sum(row[index] for row in details) for index in range(3, 8)]
        these_joint = sum(any(row[3:]) for row in details)
        these_maximum = max((sum(row[3:]) for row in details), default=0)
        check(len(openings) == record['unresolved'] and openings == (path / 'unresolved.tsv').read_text().splitlines()
              and these_fills == record['fillings'] and these_joint == record['joint'] and
              these_maximum == record['max_fill'], 'terminal counts')
        terminal_opens.extend(openings)
        summed = [sum(pair) for pair in zip(summed, record['counts'])]
        fills = [sum(pair) for pair in zip(fills, record['fillings'])]
        joint += these_joint
        maximum = max(maximum, these_maximum)
        total_cpu += record['cpu_s']
        screen_cpu += record['screen_cpu_s']
        tail = [max(pair) for pair in zip(tail, record['tail_ms'])]
        coverage_rows.append('\t'.join(map(str, [low, high, flip0, flip1, *record['counts'], these_joint, len(openings),
                             digest, record['stage_sha256'], record['terminal_sha256']])))
    complete = last == FRAME_COUNT
    if complete:
        check(len(coverage_rows) == len(expected) + 1 and summed[0] == HEADER_COUNT, 'full partition sum')
    (work / 'coverage.tsv').write_text('\n'.join(coverage_rows) + '\n')
    (work / 'unresolved.tsv').write_text(''.join(line + '\n' for line in terminal_opens))
    (work / 'unchecked_panels.tsv').write_text(''.join(line + '\n' for line in pending_panels))
    output = dict(verified_prefix=last, complete=complete, counts=summed, joint=joint, unresolved=len(terminal_opens),
                  fills=fills, max_fills=maximum, terminal_sha256=terminal_stream.hexdigest(), stage_tree_sha256=stage_tree.hexdigest(),
                  shard_cpu_s=round(total_cpu, 3), screen_cpu_s=round(screen_cpu, 3), terminal_tail_ms=tail,
                  unchecked_panels=len(pending_panels))
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('work', type=Path, nargs='?')
    parser.add_argument('reference', type=Path, nargs='?')
    args = parser.parse_args()
    if args.work is None:
        controls()
    else:
        audit(args.work, args.reference)
