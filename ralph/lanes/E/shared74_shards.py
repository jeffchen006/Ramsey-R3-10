#!/usr/bin/env python3
"""Split a shared74 cover into contiguous chunks and bind local receipts."""

import argparse
from collections import Counter
from itertools import groupby, zip_longest
import json
from pathlib import Path
from shutil import copyfile


def chunks(work, count):
    return (work / f'cover.{shard:02d}.jsonl' for shard in range(count))


def split(cover, work, stride):
    assert stride > 0
    work.mkdir()
    total = 0
    out = None
    with cover.open(encoding='ascii') as source:
        for index, line in enumerate(source):
            if index % stride == 0:
                if out is not None:
                    out.close()
                out = (work / f'cover.{index//stride:02d}.jsonl').open('x', encoding='ascii')
            out.write(line)
            total += 1
    assert out is not None
    out.close()
    print('projections', total, 'shards', (total + stride - 1) // stride, flush=True)


def groups(stream):
    return groupby(map(json.loads, stream), key=lambda row: row[0])


def merge(cover, work, count, mode, target):
    stats = Counter()
    with cover.open(encoding='ascii') as full, target.open('x', encoding='ascii') as out:
        for source in chunks(work, count):
            with source.open(encoding='ascii') as current, source.with_suffix(f'.{mode}.jsonl').open(encoding='ascii') as trace:
                for local_id, (line, batch) in enumerate(zip_longest(current, groups(trace))):
                    assert line is not None and batch is not None and line == next(full)
                    index, receipts = batch
                    assert index == local_id
                    lift_count = len(json.loads(line)[3])
                    rows = list(receipts)
                    assert lift_count and rows
                    if rows[0][1] == -1:
                        assert len(rows) == 1 and rows[0][2:4] == ['graph', 3]
                        stats['projection_graph'] += 1
                        stats['projection_graph_lifts'] += lift_count
                    else:
                        assert [row[1] for row in rows] == list(range(lift_count))
                        for row in rows:
                            assert row[2] in ('graph', 'incompatible', 'open')
                            stats[row[2]] += 1
                    for row in rows:
                        row[0] = stats['projections']
                        print(json.dumps(row, separators=(',', ':')), file=out)
                    stats['projections'] += 1
                    stats['lifts'] += lift_count
        assert next(full, None) is None
    assert stats['lifts'] == sum(stats[key] for key in ('projection_graph_lifts', 'graph', 'incompatible', 'open'))
    print(mode, dict(stats), flush=True)


def compare(filtered, baseline):
    stats = Counter()
    with filtered.open(encoding='ascii') as first, baseline.open(encoding='ascii') as second:
        for left, right in zip_longest(map(json.loads, first), map(json.loads, second)):
            assert left is not None and right is not None and left[:2] == right[:2]
            if left != right:
                assert len(left) == len(right) == 3 and left[2] == 'incompatible' and right[2] == 'open'
                stats['open to incompatible'] += 1
            else:
                stats[f'{left[2]} unchanged'] += 1
    print(dict(stats), flush=True)


def distribute_proofs(trace, proofs, work, count):
    assert count > 0
    with trace.open(encoding='ascii') as receipts:
        keys = [(index, lift) for index, lift, verdict, *_ in map(json.loads, receipts) if verdict == 'open']
    expected = {f'{index}_{lift}' for index, lift in keys}
    assert len(keys) == len(expected)
    for suffix in ('.cnf', '.lrat'):
        assert {path.stem for path in proofs.glob(f'*{suffix}')} == expected
    work.mkdir()
    totals = []
    for shard in range(count):
        folder = work/f'proofs.{shard:02d}'
        folder.mkdir()
        subset = keys[shard::count]
        totals.append(len(subset))
        with (work/f'trace.{shard:02d}.jsonl').open('x', encoding='ascii') as selected:
            for index, lift in subset:
                print(json.dumps((index, lift, 'open'), separators=(',', ':')), file=selected)
                for suffix in ('.cnf', '.lrat'):
                    path = proofs/f'{index}_{lift}{suffix}'
                    (folder/path.name).symlink_to(path.resolve(strict=True))
    assert sum(totals) == len(expected)
    print('proof replay partition sizes', totals, 'total', len(expected), flush=True)


def plan_fused(graph_first, fused, old_proofs, checked, new_proofs, todo):
    with graph_first.open(encoding='ascii') as stream:
        wanted = [row[:2] for row in map(json.loads, stream) if row[2] == 'open']
    with fused.open(encoding='ascii') as stream:
        results = list(map(json.loads, stream))
    assert [row[:2] for row in results] == wanted and len(set(map(tuple, wanted))) == len(wanted)
    assert all(row[2:] == ['open'] or (len(row) == 4 and row[2] == 'fused' and row[3] in (
        'degree conflict', 'global triangle', 'window conflict', 'cross-window edge conflict')) for row in results)
    with checked.open(encoding='ascii') as stream:
        reusable = {tuple(map(int, line.split())) for line in stream}
    assert reusable <= set(map(tuple, wanted))
    new_proofs.mkdir()
    remaining = reused = 0
    with todo.open('x', encoding='ascii') as out:
        for index, lift, status, *_ in results:
            if status != 'open':
                continue
            if (index, lift) in reusable:
                stem = f'{index}_{lift}'
                assert 's VERIFIED UNSAT' in (old_proofs / f'{stem}.lrat.log').read_text(encoding='ascii').splitlines()
                for suffix in ('.cnf', '.lrat', '.lrat.log', '.solve.log'):
                    copyfile(old_proofs / f'{stem}{suffix}', new_proofs / f'{stem}{suffix}')
                reused += 1
            else:
                print(json.dumps((index, lift, 'open'), separators=(',', ':')), file=out)
                remaining += 1
    print('coverage bound', len(wanted), 'open after fusion', remaining + reused,
          'reuse', reused, 'new proofs', remaining, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='action', required=True)
    splitter = modes.add_parser('split')
    splitter.add_argument('cover', type=Path)
    splitter.add_argument('work', type=Path)
    splitter.add_argument('stride', type=int)
    merger = modes.add_parser('merge')
    merger.add_argument('cover', type=Path)
    merger.add_argument('work', type=Path)
    merger.add_argument('count', type=int)
    merger.add_argument('mode', choices=('graphfirst', 'unfiltered'))
    merger.add_argument('target', type=Path)
    comparer = modes.add_parser('compare')
    comparer.add_argument('filtered', type=Path)
    comparer.add_argument('baseline', type=Path)
    distributor = modes.add_parser('distribute-proofs')
    distributor.add_argument('trace', type=Path)
    distributor.add_argument('proofs', type=Path)
    distributor.add_argument('work', type=Path)
    distributor.add_argument('count', type=int)
    planner = modes.add_parser('plan-fused')
    planner.add_argument('graph_first', type=Path)
    planner.add_argument('fused', type=Path)
    planner.add_argument('old_proofs', type=Path)
    planner.add_argument('checked', type=Path)
    planner.add_argument('new_proofs', type=Path)
    planner.add_argument('todo', type=Path)
    args = parser.parse_args()
    if args.action == 'split':
        split(args.cover, args.work, args.stride)
    elif args.action == 'merge':
        merge(args.cover, args.work, args.count, args.mode, args.target)
    elif args.action == 'compare':
        compare(args.filtered, args.baseline)
    elif args.action == 'distribute-proofs':
        distribute_proofs(args.trace, args.proofs, args.work, args.count)
    else:
        plan_fused(args.graph_first, args.fused, args.old_proofs, args.checked, args.new_proofs, args.todo)


if __name__ == '__main__':
    main()
