#!/usr/bin/env python3
"""Dispersed mixed-core pilot, reordered filters, and coverage replay."""

import argparse
from collections import Counter
from itertools import groupby, zip_longest
from pathlib import Path
from time import process_time
import json

from fuse_shared74 import calibration as calibrate_fusion, fuse
from involution_sat import from_graph6
from m11_prop import Prover, proof_check, targets
from m11_support import Supports, automorphisms, group_image, image
from replay_shared74 import compatible, read
from shared74 import MIXED, calibration as calibrate_marked, surviving_counts
from shared74_scan import prove


def spread(key, output, per_branch, tail):
    core = tuple(from_graph6(key))
    autos = tuple(automorphisms(core))
    cap = tuple(4 - row.bit_count() for row in core)
    support = Supports(core, 6)
    small, large = (support.catalog(size, cap) for size in (10, 11))
    reps = tuple(first for first in small if all(first <= image(first, perm) for perm in autos))
    second_options = small[::-1] if tail else small
    third_options = large[::-1] if tail else large
    stats = Counter()
    with output.open('x', encoding='ascii') as out:
        for first in reps:
            count = 0
            for second in second_options:
                pair = (first, second)
                if second < first or any(tuple(sorted((image(first, perm), image(second, perm)))) < pair
                                         for perm in autos):
                    continue
                remain = tuple(bound - left - right for bound, left, right in
                               zip(cap, support.info(first)[0], support.info(second)[0]))
                if min(remain) < 0:
                    continue
                for third in third_options:
                    residue = tuple(bound - need for bound, need in zip(remain, support.info(third)[0]))
                    if min(residue) < 0:
                        continue
                    parts = (*pair, third)
                    lifts = tuple(fourth for fourth in support.options(tuple(1 + left for left in residue))
                                  if support.admissible((*parts, fourth)) and
                                  all(group_image((*parts, fourth), MIXED, perm) >= (*parts, fourth)
                                      for perm in autos))
                    if not lifts:
                        continue
                    print(json.dumps((key, MIXED, parts, lifts), separators=(',', ':')), file=out)
                    stats['projections'] += 1
                    stats['lifts'] += len(lifts)
                    count += 1
                    if count >= per_branch:
                        break
                if count >= per_branch:
                    break
            stats['nonempty sampled branches'] += bool(count)
    assert stats['projections']
    print(key, 'local counts', len(small), len(large), 'automorphisms', len(autos),
          'first-support representatives', len(reps), dict(stats), flush=True)


OMISSIONS = tuple(tuple(range(8 + 6 * group, 14 + 6 * group)) for group in range(4))


def fused_status(prover, core, groups):
    lower, upper = targets(core, groups)
    verdict, _, _, _ = fuse(lower, upper, OMISSIONS, (8,) * 8 + (7,) * 24, 7, 74, prover)
    return verdict


def decode(row):
    key, profile, parts, omitted = row
    assert tuple(profile) == MIXED
    return tuple(from_graph6(key)), tuple(map(tuple, parts)), tuple(map(tuple, omitted))


def scan(cover, output, prover, order):
    stats = Counter()
    start = process_time()
    with output.open('x', encoding='ascii') as out:
        def emit(*record):
            print(json.dumps(record, separators=(',', ':')), file=out)

        for index, row in enumerate(read(cover)):
            core, parts, omitted = decode(row)
            stats['projections'] += 1
            stats['lifts'] += len(omitted)
            witness = prove(prover, core, parts)
            if witness:
                stats['projection_graph_lifts'] += len(omitted)
                emit(index, -1, 'graph', 3, witness)
                continue
            for lift, option in enumerate(omitted):
                groups = (*parts, option)
                for dropped in range(3):
                    witness = prove(prover, core, groups[:dropped] + groups[dropped + 1:])
                    if witness:
                        stats['graph'] += 1
                        emit(index, lift, 'graph', dropped, witness)
                        break
                else:
                    for test in order:
                        stats[test + '_calls'] += 1
                        if test == 'marked':
                            if not any(surviving_counts(core, groups, marked=True)):
                                stats['incompatible'] += 1
                                emit(index, lift, 'incompatible')
                                break
                        else:
                            status = fused_status(prover, core, groups)
                            if status != 'open':
                                stats[status] += 1
                                emit(index, lift, 'fused', status)
                                break
                    else:
                        stats['open'] += 1
                        emit(index, lift, 'open')
    print('order', order, dict(stats), f'cpu={process_time()-start:.3f}', flush=True)


def replay(cover, trace, prover):
    receipts = iter(read(trace))
    stats = Counter()

    def check_graph(receipt, core, parts, dropped):
        assert len(receipt) == 5 and receipt[2:4] == ['graph', dropped]
        witness = receipt[4]
        assert 1 <= witness[0] <= 5
        proof_check(*targets(core, parts), 7, 74, *witness)

    for index, row in enumerate(read(cover)):
        core, parts, omitted = decode(row)
        assert omitted
        stats['projections'] += 1
        stats['lifts'] += len(omitted)
        first = next(receipts)
        assert first[0] == index
        if first[1] == -1:
            check_graph(first, core, parts, 3)
            stats['projection_graph_lifts'] += len(omitted)
            continue
        for lift, option in enumerate(omitted):
            receipt = first if lift == 0 else next(receipts)
            assert receipt[:2] == [index, lift]
            groups = (*parts, option)
            status = receipt[2]
            if status == 'graph':
                dropped = receipt[3]
                assert 0 <= dropped < 3
                check_graph(receipt, core, groups[:dropped] + groups[dropped + 1:], dropped)
            elif status == 'incompatible':
                assert len(receipt) == 3 and not compatible(core, groups), (index, lift)
            elif status == 'fused':
                assert len(receipt) == 4 and receipt[3] != 'open'
                assert fused_status(prover, core, groups) == receipt[3], (index, lift)
            else:
                assert status == 'open' and len(receipt) == 3
            stats[status] += 1
    assert next(receipts, None) is None
    assert stats['lifts'] == sum(stats[status] for status in
                                 ('projection_graph_lifts', 'graph', 'incompatible', 'fused', 'open'))
    print('receipt replay:', dict(stats), flush=True)


def compare(left, right, output):
    def opens(path):
        return [row for row in read(path) if row[2] == 'open']

    residual = opens(left)
    assert residual == opens(right)
    with output.open('x', encoding='ascii') as out:
        out.writelines(json.dumps(row, separators=(',', ':')) + '\n' for row in residual)
    print('identical ordered residual IDs:', len(residual), flush=True)


def merge(cover, directory, count, target):
    stats = Counter()
    with cover.open(encoding='ascii') as full, target.open('x', encoding='ascii') as out:
        for shard in range(count):
            base = directory / f'cover.{shard:02d}.jsonl'
            with base.open(encoding='ascii') as source:
                batches = groupby(read(base.with_suffix('.receipt.jsonl')), key=lambda row: row[0])
                for local, (line, batch) in enumerate(zip_longest(source, batches)):
                    assert line is not None and batch is not None and line == next(full)
                    index, receipts = batch
                    assert index == local
                    lifts = len(json.loads(line)[3])
                    rows = list(receipts)
                    if rows[0][1] == -1:
                        assert len(rows) == 1 and rows[0][2:4] == ['graph', 3]
                        stats['projection_graph_lifts'] += lifts
                    else:
                        assert [row[1] for row in rows] == list(range(lifts))
                        for row in rows:
                            assert row[2] in ('graph', 'fused', 'incompatible', 'open')
                            stats[row[2]] += 1
                    for row in rows:
                        row[0] = stats['projections']
                        print(json.dumps(row, separators=(',', ':')), file=out)
                    stats['projections'] += 1
                    stats['lifts'] += lifts
        assert next(full, None) is None
    assert stats['lifts'] == sum(stats[status] for status in
                                 ('projection_graph_lifts', 'graph', 'incompatible', 'fused', 'open'))
    print('merged receipts:', dict(stats), flush=True)


def bind_samples(cover, samples):
    sampled = [set(path.read_text(encoding='ascii').splitlines()) for path in samples]
    for path, lines in zip(samples, sampled):
        assert len(lines) == sum(1 for _ in read(path))
    with cover.open(encoding='ascii') as full:
        seen = {line.strip() for line in full}
    for path, lines in zip(samples, sampled):
        assert lines <= seen
        print('all sample projections and lifts byte-bound:', path, len(lines), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', type=Path, default=Path('../r6_e11/m11_prop.so'))
    commands = parser.add_subparsers(dest='mode', required=True)
    sample = commands.add_parser('spread')
    sample.add_argument('key')
    sample.add_argument('output', type=Path)
    sample.add_argument('--per-branch', type=int, default=24)
    sample.add_argument('--tail', action='store_true')
    benchmark = commands.add_parser('scan')
    benchmark.add_argument('order', choices=('marked-first', 'fused-first', 'graph-only'))
    benchmark.add_argument('cover', type=Path)
    benchmark.add_argument('output', type=Path)
    auditor = commands.add_parser('replay')
    auditor.add_argument('cover', type=Path)
    auditor.add_argument('trace', type=Path)
    equal = commands.add_parser('compare')
    equal.add_argument('left', type=Path)
    equal.add_argument('right', type=Path)
    equal.add_argument('output', type=Path)
    merger = commands.add_parser('merge')
    merger.add_argument('cover', type=Path)
    merger.add_argument('directory', type=Path)
    merger.add_argument('count', type=int)
    merger.add_argument('target', type=Path)
    binder = commands.add_parser('bind-samples')
    binder.add_argument('cover', type=Path)
    binder.add_argument('samples', type=Path, nargs='+')
    commands.add_parser('calibrate')
    args = parser.parse_args()
    if args.mode == 'spread':
        assert args.per_branch > 0
        spread(args.key, args.output, args.per_branch, args.tail)
    elif args.mode == 'compare':
        compare(args.left, args.right, args.output)
    elif args.mode == 'merge':
        merge(args.cover, args.directory, args.count, args.target)
    elif args.mode == 'bind-samples':
        bind_samples(args.cover, args.samples)
    else:
        prover = Prover(args.lib)
        if args.mode == 'scan':
            order = {'marked-first': ('marked', 'fused'), 'fused-first': ('fused', 'marked'), 'graph-only': ()}
            scan(args.cover, args.output, prover, order[args.order])
        elif args.mode == 'replay':
            replay(args.cover, args.trace, prover)
        else:
            calibrate_marked()
            calibrate_fusion(prover)


if __name__ == '__main__':
    main()
