#!/usr/bin/env python3
"""Time and bind the ordered core-1 pilot; no full receipt or proof queue."""

import argparse
from collections import Counter
import csv
from hashlib import sha256
from itertools import groupby
import json
from pathlib import Path
from time import process_time

import fast_trace74
import fuse_shared74
from hard_lifts74 import NAMES, read_band
import m11_prop
import order_shared74
from shared74_price import bands
import shared74_scan


def branch_label(row):
    return ','.join(map(str, row[2][0]))


def measured(rows, totals):
    for row in rows:
        branch = branch_label(row)
        started = process_time()
        yield row
        totals[branch] += process_time() - started


def timed(mode, cover, receipt, output):
    totals = Counter()
    reader = order_shared74.read
    def instrument(path):
        return measured(reader(path), totals) if path == cover else reader(path)

    order_shared74.read = instrument
    prover = m11_prop.Prover(Path('../r6_e11/m11_prop.so'))
    if mode != 'python':
        checker = fast_trace74.Checker(Path('check_trace74.so'))
        for module in (fuse_shared74, shared74_scan, order_shared74):
            assert module.proof_check is m11_prop.proof_check
            module.proof_check = checker
    if mode == 'scan':
        order_shared74.scan(cover, receipt, prover, ('fused', 'marked'))
    else:
        order_shared74.replay(cover, receipt, prover)
    with output.open('x', encoding='ascii') as stream:
        for branch, seconds in totals.items():
            print(branch, f'{seconds:.7f}', sep='\t', file=stream)


def offsets(size, width, band):
    if size >= 3 * width:
        start = (0, (size - width) // 2, size - width)[band]
        return range(start, start + width)
    return range(band * size // 3, (band + 1) * size // 3)


def choose(bands, cap):
    hit_groups = [iter(ids) for _, ids in sorted(bands.items())]
    selected = []
    while hit_groups and len(selected) < cap:
        remaining = []
        for group in hit_groups:
            chosen = next(group, None)
            if chosen is not None:
                selected.append(chosen)
                remaining.append(group)
                if len(selected) == cap:
                    break
        hit_groups = remaining
    assert len(selected) == len(set(selected))
    return sorted(selected)


def audit(prefix, width, output, queue, selected):
    with Path(f'{prefix}.branches.tsv').open(encoding='ascii') as stream:
        branches = list(csv.DictReader(stream, delimiter='\t'))
    open_groups = {}
    metadata = {}
    branch_limits = {}
    start = 0
    lifts_start = 0
    for branch in branches:
        label = branch['branch']
        rows, lifts = int(branch['projections']), int(branch['lifts'])
        assert label not in branch_limits
        branch_limits[label] = (start, start + rows, lifts_start, lifts_start + lifts)
        start += rows
        lifts_start += lifts
    all_ids = set()
    with output.open('x', encoding='ascii') as out:
        print('branch\trow_begin\trow_end\tlift_start\tlift_end\tband\trows\tlifts\thard_lifts\topen\t'
              'receipt_bytes\tscan_cpu\tnative_cpu\tpython_cpu', file=out)
        for band_index, band in enumerate(NAMES):
            cover, receipt = (Path(f'{prefix}.{band}{suffix}') for suffix in ('.jsonl', '.receipt.jsonl'))
            ids = list(map(int, Path(f'{prefix}.{band}.ids').read_text(encoding='ascii').splitlines()))
            assert len(ids) == len(set(ids)) and all_ids.isdisjoint(ids)
            all_ids.update(ids)
            want = []
            for branch in branches:
                begin, end, _, _ = branch_limits[branch['branch']]
                want.extend(begin + rel for rel in offsets(end - begin, width, band_index))
            assert want == ids
            times = [dict(line.split('\t') for line in Path(f'{prefix}.{band}.{mode}.tsv')
                          .read_text(encoding='ascii').splitlines()) for mode in ('scan', 'native', 'python')]
            receipt_sizes = Counter()
            with receipt.open('rb') as stream:
                for line in stream:
                    local, lift, status, *_ = json.loads(line)
                    receipt_sizes[local] += len(line)
                    if status == 'open':
                        global_id = (ids[local], lift)
                        assert global_id not in metadata
                        metadata[global_id] = (band, local)
            cursor = 0
            grouped = iter(groupby(enumerate(read_band(cover, receipt)), key=lambda item: item[1][0]))
            present = next(grouped, None)
            for branch in branches:
                label = branch['branch']
                rows, lifts = int(branch[band]), int(branch[f'{band}_lifts'])
                counts = Counter()
                if rows:
                    assert present is not None and present[0] == label
                    for local, (_, values) in present[1]:
                        assert local == cursor
                        counts.update(values)
                        counts['receipt_bytes'] += receipt_sizes.pop(local)
                        cursor += 1
                    present = next(grouped, None)
                assert (rows, lifts) == (counts['rows'], counts['lifts'])
                print(label, *branch_limits[label], band, rows, lifts, counts['hard_lifts'], counts['open'],
                      counts['receipt_bytes'], *(items.pop(label) if rows else '0' for items in times),
                      sep='\t', file=out)
            assert cursor == len(ids) and present is None and not receipt_sizes and all(not items for items in times)
    for global_id, (band, local) in sorted(metadata.items()):
        branch = next(label for label, (begin, end, _, _) in branch_limits.items() if begin <= global_id[0] < end)
        open_groups.setdefault((NAMES.index(band), branch), []).append(global_id)
    groups = {stratum: sorted(keys, key=lambda key: (abs(key[0] * 2 - keys[0][0] - keys[-1][0]), key))
              for stratum, keys in open_groups.items()}
    matched = choose(groups, 16)
    with queue.open('x', encoding='ascii') as out:
        print('projection\tlift\tband\tsample_projection\tselected', file=out)
        for key, (band, local) in sorted(metadata.items()):
            print(*key, band, local, int(key in matched), sep='\t', file=out)
    with selected.open('x', encoding='ascii') as out:
        for key in matched:
            print(json.dumps((*key, 'open'), separators=(',', ':')), file=out)
    print('exact band bindings:', len(branches), 'branches;', start, 'projections;', lifts_start, 'lifts;',
          len(all_ids), 'pilot projections;', len(metadata), 'pilot opens;', len(matched), 'matched rows;',
          'TSV sha256', sha256(output.read_bytes()).hexdigest(), flush=True)


def calibrate():
    for width in (1, 3, 24, 48):
        for size in range(320):
            assert tuple(offsets(size, width, band) for band in range(3)) == bands(size, width)
    assert choose({(0, 'a'): [(1, 0), (2, 1)], (1, 'b'): [(3, 1)]}, 2) == [(1, 0), (3, 1)]
    assert choose({(0, 'a'): [(1, 0)], (1, 'b'): [(3, 1)]}, 16) == [(1, 0), (3, 1)]
    sample = [['x', [], [[1]], []], ['x', [], [[2]], []], ['x', [], [[2]], []]]
    times = Counter()
    assert list(measured(sample, times)) == sample and times.keys() == {'1', '2'}
    print('1,280 band comparisons, timing passthrough and capped strata selection passed', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('calibrate')
    for mode in ('scan', 'native', 'python'):
        timing = commands.add_parser(mode)
        for name in ('cover', 'receipt', 'output'):
            timing.add_argument(name, type=Path)
    auditing = commands.add_parser('audit')
    auditing.add_argument('prefix')
    auditing.add_argument('width', type=int)
    for name in ('output', 'queue', 'selected'):
        auditing.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.command == 'calibrate':
        calibrate()
    elif args.command == 'audit':
        audit(args.prefix, args.width, args.output, args.queue, args.selected)
    else:
        timed(args.command, args.cover, args.receipt, args.output)


if __name__ == '__main__':
    main()
