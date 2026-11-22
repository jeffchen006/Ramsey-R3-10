#!/usr/bin/env python3
"""Reconcile the ordered shard ledger and optionally recheck archived LRATs."""

import argparse
from bisect import bisect_right
from collections import Counter
from hashlib import sha256
from itertools import groupby, zip_longest
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import json

import paired_core1_74 as paired
from queue_mixed74 import (FAST, KEYS, ORIGIN, bind_lift, check_line, file_sha, folders, read_lines,
                           records, slice_source, verify_manifest, verify_wide)


def target_ids(rows, trace, begin):
    totals = Counter()
    targets = []
    groups = groupby(trace, key=lambda row: row[0])
    for local, (row, group) in enumerate(zip_longest(rows, groups)):
        assert row and group and group[0] == local
        options = json.loads(row)[3]
        batch = list(group[1])
        if batch[0][1] == -1:
            assert len(batch) == 1 and batch[0][2:4] == ['graph', 3]
            totals['projection_graph'] += len(options)
            continue
        assert [receipt[1] for receipt in batch] == list(range(len(options)))
        for receipt in batch:
            index, ordinal, verdict, *_ = receipt
            assert index == local and verdict in ('open', 'graph', 'fused', 'incompatible')
            totals[verdict] += 1
            if verdict == 'open':
                targets.append((begin+index, ordinal))
    return totals, targets


def inspect_proof(entry, directory):
    assert entry['width'] in (3, 8)
    path = directory/'proof.lrat.gz'
    assert file_sha(path) == entry['archive'] and path.stat().st_size == entry['proof_bytes']
    raw = gzip.decompress(path.read_bytes())
    assert raw and sha256(raw).hexdigest() == entry['proof']
    stem = 'width3' if entry['width'] == 3 else 'reference8'
    assert entry['narrow' if entry['width'] == 3 else 'wide'] == 'UNSAT'
    for tool, _, marker in paired.CHECKERS:
        assert paired.log_ok(directory/f'{stem}.{tool}.log', marker)
    return raw


def replay_proof(row, direct, key, ordinal, entry, proof, fast, root):
    physical, independent = bind_lift(row, direct, key, ordinal, ordinal)
    with TemporaryDirectory(dir=root, prefix='proof.') as name:
        tmp = Path(name)
        reference = tmp/'reference8.cnf'
        narrow = tmp/'width3.cnf'
        reference.write_bytes(paired.formula(*physical, 8, fast))
        narrow.write_bytes(paired.formula(*independent, 3, fast))
        counts = paired.binding(*independent, reference, narrow)
        assert counts == (entry['base'], entry['cuts']) and file_sha(reference) == entry['reference']
        selected = narrow if entry['width'] == 3 else reference
        if selected == reference:
            verify_wide(independent, reference)
        assert file_sha(selected) == entry['formula']
        selected.with_suffix('.lrat').write_bytes(proof)
        paired.check(selected)


def audit(core, out, reproof_stride, reproof_offset):
    parent, blocks, branches = verify_manifest(core)
    folder, cover, independent = folders(core)
    totals = Counter()
    accepted = []
    residual = []
    missing = []
    recognized = set()
    if reproof_stride:
        fast = paired.FastCuts(FAST)
        paired.room = lambda storage=0: None
        (out/'recheck').mkdir()
    for block in blocks:
        target = folder/'shards'/f'{block["shard"]:05}'
        recognized.add(target.name)
        finished = target/'complete.json'
        if not finished.exists():
            missing.append(dict(block, failure=(target/'failed.json').is_file(), claimed=target.is_dir()))
            continue
        totals['complete_shards'] += 1
        totals['rows'] += block['stop'] - block['first']
        certificate = json.loads(finished.read_bytes())
        assert all(certificate[key] == value for key, value in block.items())
        rows, direct = slice_source(cover, independent, block, core)
        archive = target/'receipt.jsonl.gz'
        assert file_sha(archive) == certificate['trace_archive']
        trace_hash = sha256()

        def trace_rows():
            for line in read_lines(archive):
                trace_hash.update(line)
                yield json.loads(line)

        counts, terminals = target_ids(rows, trace_rows(), block['first'])
        assert trace_hash.hexdigest() == certificate['trace_sha']
        assert certificate['counts'].get('graph', 0) == counts['projection_graph'] + counts['graph']
        assert all(counts[route] == certificate['counts'].get(route, 0) for route in ('fused', 'incompatible', 'open'))
        assert sum(counts.values()) == block['stop_lift'] - block['first_lift']
        totals.update(counts)
        ledger_path = target/'terminal.jsonl'
        ledger = records(ledger_path) if ledger_path.is_file() else iter(())
        local_checked = 0
        for identity, entry in zip_longest(terminals, ledger):
            assert identity == (entry['index'], entry['ordinal'])
            index, ordinal = identity
            local = index - block['first']
            parts, options = check_line(rows[local], KEYS[core])
            assert parts[0] == block['branch'] and options[ordinal] == entry['omitted']
            assert entry['row'] == sha256(rows[local]).hexdigest()
            if entry['status'] != 'checked':
                assert entry['status'] == 'open' and entry.get('reason')
                residual.append([index, ordinal, entry['reason']])
                totals['open_ids'] += 1
                continue
            directory = target/f'{index}_{ordinal}'
            raw = inspect_proof(entry, directory)
            if reproof_stride and len(accepted) % reproof_stride == reproof_offset:
                replay_proof(rows[local], direct[local], KEYS[core], ordinal, entry, raw, fast, out/'recheck')
                totals['fresh_rechecks'] += 1
            totals[f'checked_width{entry["width"]}'] += 1
            accepted.append([index, ordinal, entry['width'], entry['archive']])
            local_checked += 1
        assert certificate['accepted'] == local_checked and certificate['open'] == len(terminals)-local_checked
    assert all(path.name in recognized for path in (folder/'shards').iterdir())
    assert totals['open'] == len(accepted) + len(residual)
    totals['unscanned_lifts'] = sum(block['stop_lift'] - block['first_lift'] for block in missing)
    totals['unscanned_rows'] = sum(block['stop'] - block['first'] for block in missing)
    totals['unscanned_shards'] = len(missing)
    assert totals['rows'] + totals['unscanned_rows'] == parent['rows']
    assert (sum(totals[name] for name in ('projection_graph', 'graph', 'fused', 'incompatible', 'open')) +
            totals['unscanned_lifts'] == parent['lifts'])
    for name, rows in (('checked', accepted), ('residual', residual), ('unfinished-shards', missing)):
        with (out/f'{name}.jsonl').open('x', encoding='ascii') as stream:
            for row in rows:
                print(json.dumps(row, separators=(',', ':')), file=stream)
    print('AUDIT', core, len(branches), parent['rows'], parent['lifts'], dict(totals), flush=True)


def recheck_listed(core, ledger, pieces, offset, out):
    folder, cover, independent = folders(core)
    blocks = list(records(folder/'shards.jsonl'))
    starts = [block['first'] for block in blocks]
    assert 0 <= offset < pieces
    goal = list(records(ledger))[offset::pieces]
    check_time = paired.cpu()
    paired.room = lambda storage=0: None
    fast = paired.FastCuts(FAST)
    for shard, items in groupby(goal, key=lambda item: bisect_right(starts, item[0])-1):
        block = blocks[shard]
        target = folder/'shards'/f'{shard:05}'
        rows, direct = slice_source(cover, independent, block, core)
        known = {(item['index'], item['ordinal']): item for item in records(target/'terminal.jsonl')}
        for index, ordinal, width, archive in items:
            local = index - block['first']
            entry = known[index, ordinal]
            assert entry['status'] == 'checked' and (entry['width'], entry['archive']) == (width, archive)
            assert sha256(rows[local]).hexdigest() == entry['row']
            raw = inspect_proof(entry, target/f'{index}_{ordinal}')
            replay_proof(rows[local], direct[local], KEYS[core], ordinal, entry, raw, fast, out)
            print('DUAL_RECHECK', core, index, ordinal, width, archive, flush=True)
    print('complete recheck partition', core, offset, pieces, len(goal), f'cpu={paired.cpu()-check_time:.3f}', flush=True)


def control():
    real_rows = [b'["toy",[10,10,11,11],[[0],[1],[2]],[[3],[4]]]\n']
    receipts = [[0, 0, 'graph', 0], [0, 1, 'open']]
    assert target_ids(real_rows, iter(receipts), 173) == (Counter(graph=1, open=1), [(173, 1)])
    for bad in (receipts[::-1], receipts[:1], [[0, 0, 'open'], [0, 0, 'open']], [[1, -1, 'graph', 3]]):
        try:
            target_ids(real_rows, iter(bad), 173)
        except AssertionError:
            pass
        else:
            raise AssertionError('accepted wrong projection/ordinal cover')
    print('auditor accepts toy receipt and rejects four coverage mutations', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('core', type=int, choices=KEYS)
    parser.add_argument('output', type=Path)
    parser.add_argument('--recheck-stride', type=int, default=0)
    parser.add_argument('--recheck-offset', type=int, default=0)
    parser.add_argument('--ledger', type=Path)
    args = parser.parse_args()
    assert 0 <= args.recheck_offset < max(1, args.recheck_stride)
    control()
    args.output.mkdir()
    if args.ledger:
        assert args.recheck_stride
        recheck_listed(args.core, args.ledger, args.recheck_stride, args.recheck_offset, args.output.resolve())
    else:
        audit(args.core, args.output.resolve(), args.recheck_stride, args.recheck_offset)
