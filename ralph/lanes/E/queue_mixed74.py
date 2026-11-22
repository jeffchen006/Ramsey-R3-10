#!/usr/bin/env python3
"""Ordered mixed E-021 cover, calibrated pilots, and bounded end-to-end shards."""

import argparse
from ast import literal_eval
from collections import Counter
from contextlib import contextmanager
from fcntl import LOCK_EX, LOCK_UN, flock
from hashlib import sha256
from itertools import groupby, zip_longest
from pathlib import Path
from resource import RLIMIT_FSIZE, getrlimit, setrlimit
import gzip
import json
import os

import fast_trace74
import fuse_shared74
import m11_prop
import order_shared74 as ordered
import paired_core1_74 as paired
import shared74_scan
from bind_width74 import binding, dimacs, narrow_clauses, reconstruct
from involution_sat import from_graph6


KEYS = {6: 'G?bav_', 9: 'G?q`v_', 18: 'GCpb`o'}
PROFILE = [10, 10, 11, 11]
MIB = 1024**2
STAGE = 280 * MIB
PROOF_LIVE = 80 * MIB
SCAN_LIVE = 40 * MIB
CPU_LIMIT = 3000
STRIDE_LIFTS = 12000
STRIDE_ROWS = 1500
WIDTH = 8
ORIGIN = Path.cwd().resolve()
SLOW = m11_prop.proof_check
NATIVE = ORIGIN/'../r18_shared/check_trace74.so'
PROVER = ORIGIN/'../r6_e11/m11_prop.so'
FAST = ORIGIN/'../r6_e11/m11_fastcuts.so'


def encode_json(value):
    return (json.dumps(value, separators=(',', ':'), sort_keys=True) + '\n').encode('ascii')


def read_lines(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as stream:
        yield from stream


def records(path):
    for line in read_lines(path):
        yield json.loads(line)


def atomic(path, data):
    assert not path.exists(), path
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes(data)
    temporary.rename(path)


def append(path, value):
    with path.open('ab') as stream:
        stream.write(encode_json(value))


def file_sha(path):
    with path.open('rb') as stream:
        return sha256_file(stream)


def logical_bytes(folder):
    total = 0
    for path in folder.rglob('*'):
        try:
            if path.is_file():
                total += path.stat().st_size
        except FileNotFoundError:
            continue
    return total


def sha256_file(stream):
    digest = sha256()
    for block in iter(lambda: stream.read(MIB), b''):
        digest.update(block)
    return digest.hexdigest()


def folders(core):
    return ORIGIN/f'core.{core}', ORIGIN/f'cover.{core}.jsonl', ORIGIN/f'independent.{core}.jsonl'


def check_line(line, key):
    found, profile, parts, omitted = json.loads(line)
    assert found == key and profile == PROFILE and len(parts) == 3 and omitted
    assert all(len(group) == 6 for group in (*parts, *omitted))
    assert parts[0] <= parts[1] and parts[2] <= omitted[0]
    assert all(left < right for left, right in zip(omitted, omitted[1:]))
    return parts, omitted


def prepare(core):
    start = paired.cpu()
    folder, cover, independent = folders(core)
    assert all('exit=0' in (ORIGIN/f'{mode}.{core}.log').read_text() for mode in ('census', 'independent'))
    assert 'COMPLETE' in (ORIGIN/f'census.{core}.log').read_text()
    first = [list(literal_eval(line)) for line in (ORIGIN/f'first.{core}.txt').read_text().splitlines()]
    assert first == [list(branch) for branch in sorted(set(map(tuple, first)))]
    folder.mkdir()
    shards, branches = [], []
    rows = lifts = position = 0
    previous_parts = []
    digest = sha256()
    limit = 0
    block = None
    with cover.open('rb') as primary, independent.open('rb') as secondary:
        for found, wanted in zip_longest(primary, secondary):
            assert found == wanted and found is not None, (core, rows)
            parts, options = check_line(found, KEYS[core])
            assert previous_parts < parts, (core, rows)
            new_branch = not previous_parts or previous_parts[0] != parts[0]
            if new_branch:
                while first[limit] != parts[0]:
                    assert first[limit] < parts[0]
                    branches.append(dict(branch=first[limit], first=rows, stop=rows, first_lift=lifts, stop_lift=lifts))
                    limit += 1
                branch = dict(branch=first[limit], first=rows, stop=rows, first_lift=lifts, stop_lift=lifts)
                branches.append(branch)
                limit += 1
            previous_parts = parts
            if (new_branch or rows - block['first'] >= STRIDE_ROWS or
                    lifts - block['first_lift'] + len(options) > STRIDE_LIFTS):
                if block is not None:
                    block['sha'] = block_digest.hexdigest()
                block = dict(shard=len(shards), branch=parts[0], first=rows, stop=rows, first_lift=lifts,
                             stop_lift=lifts, start_byte=position, end_byte=position)
                shards.append(block)
                block_digest = sha256()
            digest.update(found)
            block_digest.update(found)
            rows += 1
            lifts += len(options)
            position += len(found)
            block.update(stop=rows, stop_lift=lifts, end_byte=position)
            branch.update(stop=rows, stop_lift=lifts)
    assert block is not None
    block['sha'] = block_digest.hexdigest()
    branches.extend(dict(branch=branch, first=rows, stop=rows, first_lift=lifts, stop_lift=lifts)
                    for branch in first[limit:])
    assert [branch['branch'] for branch in branches] == first
    source = dict(core=core, key=KEYS[core], rows=rows, lifts=lifts, bytes=position, sha=digest.hexdigest(),
                  shards=len(shards), branches=len(branches), empty=sum(b['first'] == b['stop'] for b in branches))
    atomic(folder/'shards.jsonl', b''.join(map(encode_json, shards)))
    atomic(folder/'branches.jsonl', b''.join(map(encode_json, branches)))
    atomic(folder/'parent.json', encode_json(source))
    verify_manifest(core)
    print('bound parent', source, f'cpu={paired.cpu()-start:.3f}', flush=True)


def verify_manifest(core):
    folder, cover, independent = folders(core)
    parent = json.loads((folder/'parent.json').read_bytes())
    assert parent['core'] == core and parent['key'] == KEYS[core]
    assert cover.stat().st_size == independent.stat().st_size == parent['bytes']
    assert all(file_sha(path) == parent['sha'] for path in (cover, independent))
    shards = list(records(folder/'shards.jsonl'))
    branches = list(records(folder/'branches.jsonl'))
    assert len(shards) == parent['shards'] and len(branches) == parent['branches']
    assert [tuple(branch['branch']) for branch in branches] == sorted({tuple(branch['branch']) for branch in branches})
    by_branch = {tuple(key): list(group) for key, group in groupby(shards, key=lambda shard: shard['branch'])}
    rows = lifts = 0
    for branch in branches:
        assert (branch['first'], branch['first_lift']) == (rows, lifts)
        for block in by_branch.pop(tuple(branch['branch']), ()):
            assert (block['first'], block['first_lift']) == (rows, lifts)
            rows, lifts = block['stop'], block['stop_lift']
        assert (branch['stop'], branch['stop_lift']) == (rows, lifts)
    assert not by_branch and (rows, lifts) == (parent['rows'], parent['lifts'])
    assert [block['shard'] for block in shards] == list(range(len(shards)))
    assert [block['start_byte'] for block in shards] == [0] + [block['end_byte'] for block in shards[:-1]]
    assert shards[-1]['end_byte'] == parent['bytes']
    return parent, shards, branches


def slice_source(cover, independent, block, core):
    size = block['end_byte'] - block['start_byte']
    payloads = []
    for path in (cover, independent):
        with path.open('rb') as stream:
            stream.seek(block['start_byte'])
            payloads.append(stream.read(size))
    assert payloads[0] == payloads[1] and sha256(payloads[0]).hexdigest() == block['sha']
    rows, direct = (payload.splitlines(keepends=True) for payload in payloads)
    assert len(rows) == block['stop'] - block['first']
    lifts = 0
    for row in rows:
        parts, options = check_line(row, KEYS[core])
        assert parts[0] == block['branch']
        lifts += len(options)
    assert lifts == block['stop_lift'] - block['first_lift']
    return rows, direct


def physical(row, key, ordinal):
    parts, omitted = check_line(row, key)
    assert 0 <= ordinal < len(omitted)
    groups = (*parts, omitted[ordinal])
    assert [sum(map(int.bit_count, group)) for group in groups] == PROFILE
    return from_graph6(key), groups, (7,) * 4, (7,) * 24


def bind_lift(row, direct, key, ordinal, independent_ordinal):
    primary = physical(row, key, ordinal)
    bound = physical(direct, key, independent_ordinal)
    assert ordinal == independent_ordinal and primary == bound
    return primary, bound


@contextmanager
def native_trace():
    fast = fast_trace74.Checker(NATIVE)
    modules = (fuse_shared74, shared74_scan, ordered)
    assert all(module.proof_check is SLOW for module in modules)
    for module in modules:
        module.proof_check = fast
    try:
        yield
    finally:
        for module in modules:
            module.proof_check = SLOW


def scan_replay(root, rows, prover):
    cover, receipt = root/'slice.jsonl', root/'receipt.raw'
    assert not cover.exists()
    cover.write_bytes(b''.join(rows))
    began = paired.cpu()
    soft, hard = getrlimit(RLIMIT_FSIZE)
    setrlimit(RLIMIT_FSIZE, (16 * MIB, hard))
    try:
        with native_trace():
            ordered.scan(cover, receipt, prover, ('fused', 'marked'))
    finally:
        setrlimit(RLIMIT_FSIZE, (soft, hard))
    scanned = paired.cpu() - began
    began = paired.cpu()
    ordered.replay(cover, receipt, prover)
    replayed = paired.cpu() - began
    data = receipt.read_bytes()
    output = root/'receipt.jsonl.gz'
    atomic(output, gzip.compress(data, compresslevel=1, mtime=0))
    assert gzip.decompress(output.read_bytes()) == data
    cover.unlink()
    receipt.unlink()
    return scanned, replayed, output, sha256(data).hexdigest()


def verify_wide(bound, reference):
    variables, base, pinned, edges, windows = reconstruct(*bound)
    cuts = narrow_clauses(pinned, edges, windows, width=8)
    assert reference.read_bytes() == dimacs(variables, (*base, *cuts)), reference


def attempt(root, row, direct, key, ordinal, fast, wide_only=False):
    primary, bound = bind_lift(row, direct, key, ordinal, ordinal)
    stages = dict(narrow='NOT_RUN', wide='NOT_RUN')
    reference, narrow = root/'reference8.cnf', root/'width3.cnf'
    chosen = reference if wide_only else narrow
    began = paired.cpu()
    try:
        for target, width, instance in ((reference, 8, bound), (narrow, 3, primary)):
            data = paired.formula(*instance, width, fast)
            assert len(data) <= paired.FILE_CAP, ('formula file limit', target)
            paired.write(target, data)
        base, cuts = binding(*bound, reference, narrow)
        stages.update(prepare=paired.cpu()-began, base=base, cuts=cuts)
        if not wide_only:
            stages['narrow'] = paired.solve(narrow)
        if stages['narrow'] != 'UNSAT':
            chosen = reference
            verify_wide(bound, reference)
            stages['wide'] = paired.solve(reference)
        if stages['narrow'] != 'UNSAT' and stages['wide'] != 'UNSAT':
            return dict(stages, status='open', reason=stages['wide'], cpu=paired.cpu()-began)
        stages['check_cpu'] = paired.check(chosen)
        proof = chosen.with_suffix('.lrat')
        raw = proof.read_bytes()
        archive = root/'proof.lrat.gz'
        atomic(archive, gzip.compress(raw, compresslevel=1, mtime=0))
        assert gzip.decompress(archive.read_bytes()) == raw
        result = dict(stages, status='checked', width=3 if chosen == narrow else 8,
                      proof=sha256(raw).hexdigest(), archive=file_sha(archive),
                      proof_bytes=archive.stat().st_size, formula=file_sha(chosen), reference=file_sha(reference),
                      cpu=paired.cpu()-began)
    except (AssertionError, OSError) as error:
        return dict(stages, status='open', reason=f'{type(error).__name__}: {error}', cpu=paired.cpu()-began)
    for file in root.iterdir():
        if file.suffix in ('.cnf', '.lrat'):
            file.unlink()
    return result


def controls(core, samples):
    prover = m11_prop.Prover(PROVER)
    fast = paired.FastCuts(FAST)
    paired.controls(fast)
    fast_trace74.check_controls(fast_trace74.Checker(NATIVE), prover)
    for index, row, direct in samples:
        if len(json.loads(row)[3]) > 1:
            for bad_key, bad_ordinal in ((KEYS[core], 1), ('G?bFbo' if core != 6 else KEYS[9], 0)):
                try:
                    bind_lift(row, direct, bad_key, 0, bad_ordinal)
                except AssertionError:
                    pass
                else:
                    raise AssertionError(f'accepted wrong core or omitted ordinal at {index}')
            print('rejected core substitution and alternate valid omitted ordinal', index, flush=True)
            return prover, fast
    raise AssertionError('no multi-lift calibration row')


def sampled_rows(core, branches, width):
    _, cover, independent = folders(core)
    boundaries = {}
    per_branch = {}
    for number, branch in enumerate(branches):
        count = branch['stop'] - branch['first']
        take = min(width, count//3)
        offsets = {'front': range(take), 'interior': range((count-take)//2, (count-take)//2+take),
                   'tail': range(count-take, count)}
        if 0 < count < 3:
            offsets = {'front': range(count), 'interior': (), 'tail': ()}
        for band, indices in offsets.items():
            for index in indices:
                absolute = branch['first'] + index
                assert absolute not in boundaries
                boundaries[absolute] = (number, band)
            if indices:
                per_branch[number, band] = []
    with cover.open('rb') as primary, independent.open('rb') as secondary:
        for index, (row, direct) in enumerate(zip(primary, secondary, strict=True)):
            if index in boundaries:
                assert row == direct
                per_branch[boundaries[index]].append((index, row, direct))
    assert sum(map(len, per_branch.values())) == len(boundaries)
    return per_branch


def pilot(core):
    began = paired.cpu()
    parent, _, branches = verify_manifest(core)
    folder = folders(core)[0]/'pilot'
    folder.mkdir()
    samples = sampled_rows(core, branches, WIDTH)
    os.chdir(folder)
    prover, fast = controls(core, (item for batch in samples.values() for item in batch))
    metrics, terminals, groups = [], [], []
    for (number, band), sample in samples.items():
        root = Path(f'{number:03}_{band}')
        root.mkdir()
        rows = [row for _, row, _ in sample]
        scanned, replayed, receipt, receipt_sha = scan_replay(root, rows, prover)
        ids = [(sample[index][0], ordinal, sample[index][1], sample[index][2])
               for index, ordinal, result, *_ in records(receipt) if result == 'open']
        entry = dict(branch=number, band=band, row_ids=[index for index, _, _ in sample],
                     rows=len(sample), lifts=sum(len(json.loads(row)[3]) for row in rows),
                     terminal=len(ids), scan=scanned, replay=replayed, archive=receipt.stat().st_size,
                     receipt=receipt_sha)
        metrics.append(entry)
        append(Path('bands.jsonl'), entry)
        terminals.extend(ids)
        if ids:
            groups.append(ids)
    selected = []
    for offset in range(2):
        for group in groups:
            if len(group) > offset and len(selected) < 8:
                selected.append(group[offset])
    proof_seconds, proof_bytes = [], []
    for index, ordinal, row, direct in selected:
        pair = []
        for mode in ('narrow_first', 'wide_only'):
            root = Path(f'proof_{index}_{ordinal}_{mode}')
            root.mkdir()
            result = attempt(root, row, direct, KEYS[core], ordinal, fast, wide_only=(mode == 'wide_only'))
            append(Path('matched.jsonl'), dict(result, index=index, ordinal=ordinal, mode=mode))
            assert result['status'] == 'checked', (index, ordinal, mode, result)
            pair.append(result)
        proof_seconds.append(sum(result['cpu'] for result in pair))
        proof_bytes.append(max(paired.disk(Path(f'proof_{index}_{ordinal}_{mode}'))
                               for mode in ('narrow_first', 'wide_only')))
    assert selected, 'no target proof price; use wider pilot before launch'
    estimate = Counter()
    for number, branch in enumerate(branches):
        lifts = branch['stop_lift'] - branch['first_lift']
        rows = branch['stop'] - branch['first']
        if not rows:
            continue
        bands = [item for item in metrics if item['branch'] == number]
        for name in ('scan', 'replay', 'archive', 'terminal'):
            estimate[name] += max(item[name] * max(lifts/item['lifts'], rows/item['rows']) for item in bands)
    terminal_rate = max(len(terminals) / sum(value['lifts'] for value in metrics), 1 / parent['lifts'])
    projected_terminals = max(estimate['terminal'], terminal_rate * parent['lifts'])
    summary = dict(core=core, cover_sha=parent['sha'], rows=sum(item['rows'] for item in metrics),
                   lifts=sum(item['lifts'] for item in metrics), terminals=len(terminals), matched=len(selected),
                   scan_s=sum(item['scan'] for item in metrics), replay_s=sum(item['replay'] for item in metrics),
                   proof_combined_max_s=max(proof_seconds), proof_max_bytes=max(proof_bytes),
                   scan_est_s=estimate['scan'], replay_est_s=estimate['replay'],
                   terminal_est=projected_terminals,
                   total_plan_s=estimate['scan']+estimate['replay']+3*projected_terminals*max(proof_seconds),
                   archive_plan_bytes=2*estimate['archive']+3*projected_terminals*max(proof_bytes),
                   cpu=paired.cpu()-began)
    atomic(Path('price.json'), encode_json(summary))
    print('pilot price', summary, flush=True)


@contextmanager
def stage_lease(folder, limit, size):
    token = folder/f'lease.{os.getpid()}'
    with (folder/'staging.lock').open('ab') as mutex:
        flock(mutex, LOCK_EX)
        reservations = sum(int(path.read_text()) for path in folder.glob('lease.*'))
        granted = logical_bytes(folder) + reservations + size < limit
        if granted:
            assert not token.exists()
            token.write_text(str(size))
        flock(mutex, LOCK_UN)
        try:
            yield granted
        finally:
            if granted:
                flock(mutex, LOCK_EX)
                token.unlink()
                flock(mutex, LOCK_UN)


def do_shard(core, block, work, prover, fast, archive_limit):
    target = folders(core)[0]/'shards'/f'{block["shard"]:05}'
    root = target
    began = paired.cpu()
    try:
        folder = target.parent.parent
        _, cover, independent = folders(core)
        rows, direct = slice_source(cover, independent, block, core)
        with stage_lease(folder, archive_limit, SCAN_LIVE) as granted:
            assert granted, 'scan staging guard'
            scan, replay, receipt, trace_sha = scan_replay(root, rows, prover)
        stats = Counter()
        accepted = 0
        internal_error = False
        for local, ordinal, verdict, *_ in records(receipt):
            stats[verdict] += len(json.loads(rows[local])[3]) if ordinal == -1 else 1
            if verdict != 'open':
                continue
            index = block['first'] + local
            dest = target/f'{index}_{ordinal}'
            if internal_error or paired.cpu() >= CPU_LIMIT or paired.disk(work) + PROOF_LIVE >= STAGE:
                result = dict(status='open', reason=('BIND_OR_CHECK_FAILURE' if internal_error else 'STAGE_OR_CPU_GUARD'))
            else:
                with stage_lease(folder, archive_limit, PROOF_LIVE) as granted:
                    if granted:
                        dest.mkdir()
                        result = attempt(dest, rows[local], direct[local], KEYS[core], ordinal, fast)
                    else:
                        result = dict(status='open', reason='STAGE_OR_CPU_GUARD')
                if result['status'] == 'open' and not (result['reason'] == 'SAT' or result['reason'].startswith('INCOMPLETE_')):
                    internal_error = True
            if result['status'] == 'checked':
                accepted += 1
            append(target/'terminal.jsonl', dict(result, index=index, ordinal=ordinal, row=sha256(rows[local]).hexdigest(),
                                                omitted=json.loads(rows[local])[3][ordinal]))
        assert sum(stats.values()) == block['stop_lift'] - block['first_lift']
        atomic(target/'complete.json', encode_json(dict(block, counts=dict(stats), accepted=accepted,
                                                       open=stats['open']-accepted, scan=scan, replay=replay,
                                                       cpu=paired.cpu()-began, trace_sha=trace_sha,
                                                       trace_archive=file_sha(receipt))))
        print('finished', core, block['shard'], dict(stats), 'accepted', accepted,
              f'cpu={paired.cpu()-began:.3f}', flush=True)
    finally:
        (root/'slice.jsonl').unlink(missing_ok=True)


def worker(core, worker_id):
    folder, _, _ = folders(core)
    parent = json.loads((folder/'parent.json').read_bytes())
    price = json.loads((folder/'pilot/price.json').read_bytes())
    gate = json.loads((folder/'gate.json').read_bytes())
    assert gate['core'] == core and parent['sha'] == price['cover_sha'] == gate['cover_sha']
    assert price['cpu'] < 360 and price['archive_plan_bytes'] < gate['archive_limit']
    assert gate['shards'] == file_sha(folder/'shards.jsonl')
    work = folder/'work'/str(worker_id)
    work.mkdir(parents=True)
    os.chdir(work)
    paired.SOFT_STAGE_CAP = STAGE
    prover, fast = m11_prop.Prover(PROVER), paired.FastCuts(FAST)
    shards = list(records(folder/'shards.jsonl'))
    shards.sort(key=lambda block: (-(block['stop_lift']-block['first_lift']), block['shard']))
    for block in shards:
        if paired.cpu() >= CPU_LIMIT or logical_bytes(folder) + STAGE >= gate['archive_limit']:
            print('queue stopped at CPU/staging guard', core, worker_id, flush=True)
            return
        target = folder/'shards'/f'{block["shard"]:05}'
        try:
            target.mkdir()
        except FileExistsError:
            continue
        atomic(target/'owner.json', encode_json(dict(pid=os.getpid(), worker=worker_id)))
        try:
            do_shard(core, block, work, prover, fast, gate['archive_limit'])
        except (AssertionError, OSError, StopIteration) as error:
            atomic(target/'failed.json', encode_json(dict(reason=repr(error))))
            print('shard failure (open)', core, block['shard'], repr(error), flush=True)
    print('worker exit', core, worker_id, f'cpu={paired.cpu():.3f}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'pilot', 'worker'))
    parser.add_argument('core', type=int, choices=KEYS)
    parser.add_argument('worker', type=int, nargs='?')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.core)
    elif args.command == 'pilot':
        pilot(args.core)
    else:
        assert args.worker is not None
        worker(args.core, args.worker)


if __name__ == '__main__':
    main()
