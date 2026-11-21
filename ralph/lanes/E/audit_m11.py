#!/usr/bin/env python3
"""Replay support-projection traces and bind selected checked SAT proofs."""

import argparse
from collections import Counter
from itertools import groupby
import json
from pathlib import Path
import subprocess

from batch_a11 import LIMIT, TOOLS
from involution_sat import from_graph6
from m11_prop import proof_check, targets
from m11_sat import FastCuts, encode


def verify_trace(core, groups, trace):
    assert trace is not None and 1 <= trace[0] <= 5
    lower, upper = targets(core, groups)
    proof_check(lower, upper, 7, 74, *trace)


def audit(rows, traces, projected):
    trace_groups = iter(groupby(traces, key=lambda row: row[0]))
    open_rows = []
    stats = Counter()
    for index, (key, profile, parts, lifts) in enumerate(rows):
        at, records = next(trace_groups)
        assert at == index
        records = list(records)
        core = from_graph6(key)
        if records[0][1] == -1:
            assert len(records) == 1 and records[0][2] == -1
            if records[0][3] is None:
                assert projected
                open_rows.append(index)
            else:
                verify_trace(core, parts, records[0][3])
                stats['projection_witness'] += 1
        else:
            assert not projected and len(records) == len(lifts)
            hits = 0
            for lift, (_at, serial, omitted, trace) in enumerate(records):
                assert lift == serial
                if trace is None:
                    assert omitted == -1
                    hits += 1
                else:
                    assert 0 <= omitted < 3
                    combined = (*parts, lifts[lift])
                    verify_trace(core, combined[:omitted]+combined[omitted+1:], trace)
                    stats['lift_witness'] += 1
            stats['lift_sat_residual'] += hits
            if hits:
                open_rows.append(index)
        stats['rows'] += 1
        stats[f'chosen_{profile}'] += 1
    assert next(trace_groups, None) is None
    stats['projection_sat_residual'] = len(open_rows)
    return open_rows, stats


def read_json(path):
    with path.open(encoding='ascii') as stream:
        yield from map(json.loads, stream)


def replay_core(core_index, replay_stride):
    manifest = list(read_json(Path(f'cover.{core_index}.jsonl')))
    rows, stats = audit(manifest, read_json(Path(f'checked.{core_index}.jsonl')), False)
    folder = Path(f'pins.{core_index}')
    bindings = {}
    for report in sorted(folder.glob('worker.*.tsv')):
        for text in report.read_text(encoding='ascii').splitlines():
            index, lift, verdict = text.split()
            index = int(index)
            assert verdict == 'CHECKED' and index not in bindings and 0 <= int(lift) < len(manifest[index][3])
            bindings[index] = int(lift)
    assert sorted(bindings) == rows
    fast = FastCuts(Path('m11_fastcuts.so'))
    for serial, index in enumerate(rows):
        if serial % replay_stride:
            continue
        key, _, parts, _ = manifest[index]
        nn, rules, _, _ = encode(from_graph6(key), parts, (None,)*3, edge_target=74, cut_size=8, fast=fast)
        candidate = (f'p cnf {nn} {len(rules)}\n' + ''.join(' '.join(map(str, clause)) + (' ' if clause else '') + '0\n'
                                                          for clause in rules)).encode('ascii')
        prefix = folder/f'{index}.single'
        if Path(f'{prefix}.cnf').read_bytes() != candidate:
            raise ValueError(f'CNF generation mismatch at {index}')
        checked = subprocess.run(['timeout', '35', 'bash', str(LIMIT), '12', str(TOOLS/'cake_lpr'),
                                  f'{prefix}.cnf', f'{prefix}.lrat'], capture_output=True, check=True)
        assert b's VERIFIED UNSAT' in checked.stdout.splitlines()
        stats['lrat_replay'] += 1
    print('core', core_index, dict(stats), flush=True)


def replay_projection(core_index):
    cases = read_json(Path(f'cover.a{core_index}.jsonl'))
    rows, stats = audit(cases, read_json(Path(f'checked.a{core_index}.jsonl')), True)
    print('profile-a', core_index, dict(stats), flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('core', 'profile-a'))
    parser.add_argument('core', type=int)
    parser.add_argument('--replay-stride', type=int, default=1)
    args = parser.parse_args()
    assert args.replay_stride > 0
    if args.mode == 'core':
        replay_core(args.core, args.replay_stride)
    else:
        replay_projection(args.core)


if __name__ == '__main__':
    main()
