#!/usr/bin/env python3
"""Stage and audit the frozen core-1 cover; run unchanged receipt logic."""

import argparse
import csv
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import groupby, zip_longest
import json
from pathlib import Path
from time import process_time

import audit_routes74
from estimate_core1_74 import extrapolate, population, sample_size
import fast_trace74
import fuse_shared74
import m11_prop
import order_shared74 as ordered
import shared74_scan


PREV = Path('../r18_shared')
COVER = PREV/'cover.1.jsonl'
DIGEST = 'd9d3d68bd75ddc164498bc2948a02e7e98ea4101e7b5a6712acd6f6fe5b63c6c'
WORK = Path('branches')
PLAN = Path('branches.tsv')
MERGED = Path('cover.1.receipt.jsonl')
BANDS = ('front', 'interior', 'tail')
STAGING = 192 * 1024**2


def tsv(path):
    with path.open(encoding='ascii') as stream:
        yield from csv.DictReader(stream, delimiter='\t')


def branch_path(index):
    return WORK/f'cover.{index:02d}.jsonl'


def stage_bytes():
    return sum(path.stat().st_size for path in Path.cwd().rglob('*') if path.is_file())


def part_label(row):
    assert row[:2] == ['G?bFbo', [10, 10, 11, 11]]
    return ','.join(map(str, row[2][0]))


def bind_block(lines, label, rows, lifts):
    count = 0
    lift_count = 0
    for line in lines:
        value = json.loads(line)
        assert part_label(value) == label and value[3]
        count += 1
        lift_count += len(value[3])
    assert (count, lift_count) == (rows, lifts)


def prepare():
    assert sha256(COVER.read_bytes()).hexdigest() == DIGEST
    accepted = list(tsv(PREV/'pilot.1.branches.tsv'))
    metrics = defaultdict(list)
    for row in tsv(PREV/'metrics.1.tsv'):
        metrics[row['branch']].append(row)
    assert len(accepted) == len(metrics) == 24
    assert len({row['branch'] for row in accepted}) == 24
    WORK.mkdir()
    prices = []
    offset = lift_offset = 0
    with COVER.open('rb') as source:
        for index, row in enumerate(accepted):
            label = row['branch']
            rows, lifts = int(row['projections']), int(row['lifts'])
            lines = [next(source) for _ in range(rows)]
            bind_block(lines, label, rows, lifts)
            branch_path(index).write_bytes(b''.join(lines))
            assert [entry['band'] for entry in metrics[label]] == list(BANDS)
            budget = []
            for metric in ('scan_cpu', 'python_cpu', 'receipt_bytes'):
                for sample in metrics[label]:
                    assert population(sample) == (rows, lifts)
                    assert tuple(map(int, (sample['row_begin'], sample['lift_start']))) == (offset, lift_offset)
                budget.append(max(extrapolate(float(sample[metric]), sample_size([sample]), (rows, lifts))
                                  for sample in metrics[label]))
            prices.append((label, offset, rows, lift_offset, lifts, *budget))
            offset += rows
            lift_offset += lifts
        assert next(source, None) is None
    assert (offset, lift_offset) == (68323, 565531)
    work = {}
    for mode, column in (('scan', 5), ('replay', 6)):
        by_shard = [sum(prices[index][column] for index in (2*shard, 2*shard+1)) for shard in range(12)]
        loads = [0.0, 0.0]
        for shard in sorted(range(12), key=lambda index: (-by_shard[index], index)):
            worker = min(range(2), key=loads.__getitem__)
            work[mode, shard] = worker
            loads[worker] += by_shard[shard]
        print(mode, 'frozen branch-price loads', [round(value, 3) for value in loads], flush=True)
    with PLAN.open('x', encoding='ascii') as out:
        print('index\tshard\tbranch\trow_begin\trows\tlift_begin\tlifts\tscan_est\treplay_est\tbytes_est\t'
              'scan_worker\treplay_worker', file=out)
        for index, entry in enumerate(prices):
            print(index, index//2, *entry[:5], *(f'{value:.6f}' for value in entry[5:]),
                  work['scan', index//2], work['replay', index//2], sep='\t', file=out)
    receipt_estimate = sum(entry[-1] for entry in prices)
    print('ordered shards: 12; stage bytes now', stage_bytes(), 'projected receipt bytes',
          round(receipt_estimate), flush=True)
    assert stage_bytes() + 2*receipt_estimate < STAGING


def run(mode, worker):
    prover = m11_prop.Prover(Path('../r6_e11/m11_prop.so'))
    if mode == 'scan':
        proof = fast_trace74.Checker(PREV/'check_trace74.so')
        for module in (fuse_shared74, shared74_scan, ordered):
            assert module.proof_check is m11_prop.proof_check
            module.proof_check = proof
    else:
        assert all(module.proof_check is m11_prop.proof_check
                   for module in (fuse_shared74, shared74_scan, ordered))
    with Path(f'{mode}.{worker}.tsv').open('x', encoding='ascii') as times:
        print('index\tcpu\tbytes', file=times, flush=True)
        for row in tsv(PLAN):
            if int(row[f'{mode}_worker']) != worker:
                continue
            index = int(row['index'])
            cover = branch_path(index)
            receipt = cover.with_suffix('.receipt.jsonl')
            assert stage_bytes() < STAGING - 32 * 1024**2
            print('begin', mode, index, row['row_begin'], row['rows'], row['lift_begin'], row['lifts'], flush=True)
            started = process_time()
            if mode == 'scan':
                ordered.scan(cover, receipt, prover, ('fused', 'marked'))
            else:
                ordered.replay(cover, receipt, prover)
            print(index, f'{process_time() - started:.6f}', receipt.stat().st_size, sep='\t', file=times, flush=True)


def audit_pilot():
    wanted = {}
    prior_open = {}
    for band in BANDS:
        ids = list(map(int, (PREV/f'pilot.1.{band}.ids').read_text(encoding='ascii').splitlines()))
        assert not set(ids) & wanted.keys() and len(set(ids)) == len(ids)
        with (PREV/f'pilot.1.{band}.jsonl').open('rb') as cover, \
                (PREV/f'pilot.1.{band}.receipt.jsonl').open('rb') as receipts:
            for local, (global_id, line, block) in enumerate(zip_longest(ids, cover, groupby(
                    receipts, key=lambda raw: int(raw.split(b',', 1)[0][1:])))):
                assert global_id is not None and line is not None and block is not None and block[0] == local
                rows = []
                for raw in block[1]:
                    _, lift, verdict, *_ = json.loads(raw)
                    if verdict == 'open':
                        assert (global_id, lift) not in prior_open
                        prior_open[global_id, lift] = band, local
                    rows.append(b'[' + str(global_id).encode('ascii') + b',' + raw.split(b',', 1)[1])
                wanted[global_id] = line, rows
    checked_rows = checked_receipts = 0
    with COVER.open('rb') as source, MERGED.open('rb') as merged:
        for index, (line, block) in enumerate(zip_longest(source, groupby(
                merged, key=lambda raw: int(raw.split(b',', 1)[0][1:])))):
            assert line is not None and block is not None and block[0] == index
            if index in wanted:
                previous_line, receipts = wanted.pop(index)
                assert line == previous_line and list(block[1]) == receipts
                checked_rows += 1
                checked_receipts += len(receipts)
    declared = {(int(row['projection']), int(row['lift'])): (row['band'], int(row['sample_projection']))
                for row in tsv(PREV/'pilot_opens.1.tsv')}
    assert declared == prior_open and len(declared) == 24
    matched = [tuple(json.loads(line)[:2]) for line in (PREV/'matched.1.jsonl').read_bytes().splitlines()]
    assert matched == [(int(row['projection']), int(row['lift'])) for row in tsv(PREV/'pilot_opens.1.tsv')
                       if row['selected'] == '1'] and len(matched) == len(set(matched)) == 16
    stems = [f'{index}_{lift}' for index, lift in matched]
    for mode in ('wide', 'narrow'):
        prefix = PREV/f'matched.{mode}'
        audit_routes74.recheck(Path(f'{prefix}.log'), Path(f'{prefix}.rebind.log'), prefix, stems)
    assert not wanted and checked_rows == 3385
    print('byte-identical pilot overlap:', checked_rows, 'projections,', checked_receipts, 'receipts,',
          len(declared), 'terminal IDs,', len(matched), 'already proved', flush=True)
    return declared, set(matched)


def finish():
    plan = list(tsv(PLAN))
    assert [int(row['index']) for row in plan] == list(range(24))
    timings = {}
    for mode in ('scan', 'replay'):
        for worker in range(2):
            records = list(tsv(Path(f'{mode}.{worker}.tsv')))
            assert [int(row['index']) for row in records] == [int(row['index']) for row in plan
                                                              if int(row[f'{mode}_worker']) == worker]
            timings.update(((mode, int(row['index'])), (float(row['cpu']), int(row['bytes']))) for row in records)
    branch_bytes = sum(timings['scan', index][1] for index in range(24))
    assert stage_bytes() + branch_bytes + 4*565531 + 2*1024**2 < STAGING
    ordered.merge(COVER, WORK, 24, MERGED)
    prior, matched = audit_pilot()
    seen = set()
    previous = None
    stats = Counter()
    timing_keys = ('scan_cpu', 'replay_cpu', 'receipt_bytes', 'open', 'old_open', 'old_proved')
    with Path('terminal.1.jsonl').open('x', encoding='ascii') as terminal, \
            Path('pending.1.jsonl').open('x', encoding='ascii') as pending, \
            Path('branch_rates.tsv').open('x', encoding='ascii') as rates, MERGED.open('rb') as merged:
        for raw in merged:
            if not raw.endswith(b',"open"]\n'):
                continue
            index, lift, verdict = json.loads(raw)
            assert verdict == 'open' and lift >= 0 and (previous is None or previous < (index, lift))
            previous = (index, lift)
            seen.add(previous)
            branch, = (int(row['index']) for row in plan if
                       int(row['row_begin']) <= index < int(row['row_begin']) + int(row['rows']))
            stats[branch, 'open'] += 1
            stats[branch, 'old_open'] += previous in prior
            stats[branch, 'old_proved'] += previous in matched
            terminal.write(raw.decode('ascii'))
            if previous not in matched:
                pending.write(raw.decode('ascii'))
        print(*plan[0].keys(), *timing_keys, sep='\t', file=rates)
        for row in plan:
            index = int(row['index'])
            scan, size = timings['scan', index]
            replay, replay_size = timings['replay', index]
            assert size == replay_size == branch_path(index).with_suffix('.receipt.jsonl').stat().st_size
            print(*row.values(), scan, replay, size, *(stats[index, key] for key in timing_keys[3:]), sep='\t', file=rates)
    assert set(prior) <= seen and matched <= seen
    print('terminal IDs', len(seen), 'old overlap', len(prior), 'old proved', len(matched),
          'pending', len(seen - matched), 'staging bytes', stage_bytes(), flush=True)


def controls():
    root = Path('merge_control')
    root.mkdir()
    source = root/'frozen.jsonl'
    first = b'["G?bFbo",[10,10,11,11],[[1],[2],[3]],[[4],[5]]]\n'
    second = b'["G?bFbo",[10,10,11,11],[[2],[2],[3]],[[5]]]\n'
    source.write_bytes(first + second)
    (root/'cover.00.jsonl').write_bytes(first)
    (root/'cover.01.jsonl').write_bytes(second)
    bind_block([first], '1', 1, 2)
    try:
        bind_block([second], '1', 1, 1)
    except AssertionError:
        pass
    else:
        raise AssertionError('wrong first branch accepted')
    first_receipts = b'[0,0,"open"]\n', b'[0,1,"open"]\n'
    (root/'cover.01.receipt.jsonl').write_bytes(b'[0,0,"open"]\n')
    for number, (rows, valid) in enumerate(((first_receipts, True), (first_receipts[:1], False),
                                             ((*first_receipts, first_receipts[-1]), False),
                                             (first_receipts[::-1], False))):
        (root/'cover.00.receipt.jsonl').write_bytes(b''.join(rows))
        output = root/f'global.{number}.jsonl'
        try:
            ordered.merge(source, root, 2, output)
        except AssertionError:
            assert not valid
        else:
            assert valid and output.read_bytes() == b''.join(first_receipts) + b'[1,0,"open"]\n'
    print('exact ordered merge control accepted; wrong branch and dropped/duplicated/reordered lifts rejected', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='mode', required=True)
    for command in ('prepare', 'finish', 'controls'):
        actions.add_parser(command)
    for command in ('scan', 'replay'):
        actions.add_parser(command).add_argument('worker', type=int, choices=(0, 1))
    args = parser.parse_args()
    if args.mode in ('scan', 'replay'):
        run(args.mode, args.worker)
    else:
        globals()[args.mode]()
