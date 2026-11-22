#!/usr/bin/env python3
"""Check the exact round-21 core-1 queue with narrow-first LRATs."""

from collections import Counter
import csv
from itertools import groupby, zip_longest
import json
from pathlib import Path
import subprocess

from bind_width74 import binding
import paired_core1_74 as paired


PRIOR = Path('../r20_shared')
STAGE = 222 * 1024**2
paired.SOFT_STAGE_CAP = STAGE
START_CPU_LIMIT = 194
POPULATION = dict(projections=68323, lifts=565531, projection_graph_lifts=340949,
                  graph=202928, fused=19090, incompatible=2417, open=147)


def pin_inputs():
    for path in (paired.OLD, paired.FULL, PRIOR):
        subprocess.run(['sha256sum', '--quiet', '-c', 'freeze.1.sha256'], cwd=path, check=True)
    print('R18/R19/R20 freezes verified', flush=True)


def physical_queue():
    full, old = paired.FULL, paired.OLD
    terminal = paired.ids(full/'terminal.1.jsonl')
    proved18 = paired.ids(old/'matched.1.jsonl')
    proved20 = [tuple(record['id']) for record in map(json.loads, (PRIOR/'paired.jsonl').read_bytes().splitlines())]
    pending = paired.ids(PRIOR/'residual.jsonl')
    assert (len(proved18), len(proved20), len(pending)) == (16, 16, 115)
    assert proved20 == paired.ids(full/'proposed_pilot.1.jsonl')
    assert sorted([*pending, *proved20]) == paired.ids(full/'pending.1.jsonl')
    assert sorted([*proved18, *proved20, *pending]) == terminal
    with (full/'branch_rates.tsv').open(encoding='ascii') as stream:
        branches = list(csv.DictReader(stream, delimiter='\t'))
    assert len(branches) == 24

    wanted = {index for index, _ in pending}
    physical_rows, seen = {}, []
    counts = Counter()
    with (old/'cover.1.jsonl').open('rb') as whole, (full/'cover.1.receipt.jsonl').open('rb') as ledger:
        receipt_rows = groupby(map(json.loads, ledger), key=lambda row: row[0])
        for branch, meta in enumerate(branches):
            begin, size, first_lift, lifts = map(int, (meta['row_begin'], meta['rows'], meta['lift_begin'], meta['lifts']))
            mark = list(map(int, meta['branch'].split(',')))
            assert branch == int(meta['index']) and begin == counts['projections'] and first_lift == counts['lifts']
            with (full/f'branches/cover.{branch:02d}.jsonl').open('rb') as shard:
                for offset, local in zip_longest(range(size), shard):
                    assert offset is not None and local is not None
                    original = next(whole)
                    index = begin + offset
                    assert original == local
                    key, profile, groups, omitted = json.loads(original)
                    assert key == 'G?bFbo' and profile == paired.PROFILE and groups[0] == mark and omitted
                    receipt_index, receipts = next(receipt_rows)
                    assert receipt_index == index
                    records = list(receipts)
                    if records[0][1] == -1:
                        assert len(records) == 1 and records[0][2:4] == ['graph', 3]
                        counts['projection_graph_lifts'] += len(omitted)
                    else:
                        assert [row[1] for row in records] == list(range(len(omitted)))
                        for _, ordinal, verdict, *witness in records:
                            assert verdict in ('graph', 'fused', 'incompatible', 'open')
                            counts[verdict] += 1
                            if verdict == 'open':
                                assert not witness
                                seen.append((index, ordinal))
                    counts['projections'] += 1
                    counts['lifts'] += len(omitted)
                    if index in wanted:
                        physical_rows[index] = (original, local, branch)
            assert counts['lifts'] == first_lift + lifts
        assert next(whole, None) is None and next(receipt_rows, None) is None
    assert counts == POPULATION and seen == terminal and physical_rows.keys() == wanted
    assert sum(counts[category] for category in ('projection_graph_lifts', 'graph', 'fused', 'incompatible', 'open')) == counts['lifts']
    print('reconciled frozen receipts:', dict(counts), 'terminal partition 16 + 16 + 115', flush=True)
    return terminal, proved18, proved20, pending, physical_rows


def attempt(root, original, independent, ordinal, fast):
    initial = paired.cpu()
    base, narrow = root/'reference8.cnf', root/'width3.cnf'
    physical = paired.physical(original, ordinal)
    rebound = paired.physical(independent, ordinal)
    paired.write(base, paired.formula(*rebound, 8, fast))
    paired.write(narrow, paired.formula(*physical, 3, fast))
    base_count, cut_count = binding(*rebound, base, narrow)
    prepared = paired.cpu() - initial

    initial = paired.cpu()
    narrow_status = paired.solve(narrow)
    narrow_cpu = paired.cpu() - initial
    selected = narrow
    wide_status, wide_cpu = 'NOT_RUN', 0.0
    if narrow_status != 'UNSAT':
        selected = base
        assert base.read_bytes() == paired.formula(*physical, 8, fast)
        initial = paired.cpu()
        wide_status = paired.solve(base)
        wide_cpu = paired.cpu() - initial
        print(root.name, 'narrow', narrow_status, 'wide', wide_status, flush=True)
        if wide_status != 'UNSAT':
            raise StopIteration(f'wide {wide_status}')
    verified = paired.check(selected)
    return dict(prepared=prepared, narrow=narrow_status, wide=wide_status,
                narrow_cpu=narrow_cpu, wide_cpu=wide_cpu, checked_cpu=verified,
                base_clauses=base_count, cuts=cut_count,
                omitted=list(physical[1][-1]), directory=str(root), width=3 if selected == narrow else 8,
                ref_sha=paired.digest(base.read_bytes()), formula_sha=paired.digest(selected.read_bytes()),
                proof_sha=paired.digest(selected.with_suffix('.lrat').read_bytes()))


def reconcile(records, terminal, proved18, proved20, pending):
    accepted = []
    routes = Counter()
    for record in map(json.loads, records.read_bytes().splitlines()):
        key = tuple(record['id'])
        root = Path('target')/f'{key[0]}_{key[1]}'
        assert record['directory'] == str(root)
        reference = root/'reference8.cnf'
        assert paired.digest(reference.read_bytes()) == record['ref_sha']
        if record['width'] == 3:
            assert (record['narrow'], record['wide']) == ('UNSAT', 'NOT_RUN')
            cnf = root/'width3.cnf'
        else:
            assert record['width'] == 8 and record['wide'] == 'UNSAT'
            assert record['narrow'] == 'SAT' or record['narrow'].startswith('INCOMPLETE_')
            cnf = reference
        assert paired.digest(cnf.read_bytes()) == record['formula_sha']
        assert paired.digest(cnf.with_suffix('.lrat').read_bytes()) == record['proof_sha']
        assert all(paired.log_ok(cnf.with_suffix(f'.{tool}.log'), marker) for tool, _, marker in paired.CHECKERS)
        accepted.append(key)
        routes[record['width']] += 1
    assert accepted == pending[:len(accepted)]
    remaining = pending[len(accepted):]
    assert sorted([*proved18, *proved20, *accepted, *remaining]) == terminal
    for name, roster in (('accepted', accepted), ('remaining', remaining)):
        paired.write(Path(f'{name}.1.jsonl'), ''.join(json.dumps(key) + '\n' for key in roster).encode('ascii'))
    ruled_out = POPULATION['lifts'] - POPULATION['open'] + len(proved18) + len(proved20) + len(accepted)
    assert ruled_out + len(remaining) == POPULATION['lifts']
    print(f'final accepted={len(accepted)} remaining={len(remaining)} routes={dict(routes)} '
          f'reconciled={ruled_out}+{len(remaining)}={POPULATION["lifts"]} CPU={paired.cpu():.3f}s '
          f'stage={paired.disk(Path("."))} bytes', flush=True)


def main():
    pin_inputs()
    fast = paired.FastCuts(paired.FASTCUTS)
    paired.controls(fast)
    terminal, proved18, proved20, pending, rows = physical_queue()
    records = Path('checked.1.jsonl')
    try:
        with records.open('x', encoding='ascii') as stream:
            for index, ordinal in pending:
                if paired.cpu() >= START_CPU_LIMIT or paired.disk(Path('.')) + 32 * 1024**2 >= STAGE:
                    print('stopped before next lift: cumulative CPU/staging guard', flush=True)
                    break
                root = Path('target')/f'{index}_{ordinal}'
                root.mkdir(parents=True)
                original, independent, branch = rows[index]
                print('start', index, ordinal, 'branch', branch, flush=True)
                record = attempt(root, original, independent, ordinal, fast)
                record.update(id=[index, ordinal], branch=branch, row=paired.digest(original))
                print(json.dumps(record, sort_keys=True), file=stream, flush=True)
                print('checked', index, ordinal, record['width'], f'CPU={paired.cpu():.3f}s', flush=True)
    finally:
        reconcile(records, terminal, proved18, proved20, pending)


if __name__ == '__main__':
    main()
