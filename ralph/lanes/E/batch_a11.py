#!/usr/bin/env python3
"""Batch prover and byte-bound LRAT replay for profile A window projections."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from involution_sat import from_graph6
from m11_sat import FastCuts, encode


LANE = Path(__file__).resolve().parent
TOOLS = LANE.parents[2] / 'opt' / 'bin'
LIMIT = LANE / 'limited.sh'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_cnf(record, fast, width):
    core, profile, parts, ignored = record
    assert profile == [10, 10, 10, 12] and not ignored
    nn, rules, _, _ = encode(from_graph6(core), parts, (None,)*3, edge_target=74, cut_size=width, fast=fast)
    return (f'p cnf {nn} {len(rules)}\n' + ''.join(' '.join(map(str, row)) + (' ' if row else '') + '0\n'
                                                 for row in rules)).encode('ascii')


def control_args(args, action, cnf, proof):
    budget = str(args.cap)
    return ['timeout', str(25+args.cap), 'bash', str(LIMIT), budget, str(TOOLS/action),
            *(['-q', '--lrat'] if action == 'cadical' else []), str(cnf), str(proof)]


def run(args, chunk, checking=False):
    fast = FastCuts(Path('m11_fastcuts.so'))
    todo = [tuple(map(int, row.split())) for row in args.plan.read_text(encoding='ascii').splitlines()]
    assert len(todo) == len(set(todo)) and sorted(todo) == todo
    local = todo[args.offset::args.stride]
    if args.pilot:
        local = local[:args.pilot]
    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    artifact = root / f'temp.{args.offset}.cnf'
    checks = []
    if checking:
        checks = [json.loads(row) for row in (root/f'bind.{args.offset}.jsonl').read_text(encoding='ascii').splitlines()]
        assert [(entry[0], entry[1]) for entry in checks] == local
    stats = Counter()
    report = (root/f'{"replay" if checking else "bind"}.{args.offset}.jsonl').open('w', encoding='ascii', buffering=1)
    pointer = 0
    try:
        for core in sorted({row[0] for row in local}):
            seek = {row[1] for row in local if row[0] == core}
            for index, row in enumerate(Path(f'cover.a{core}.jsonl').open(encoding='ascii')):
                if index not in seek:
                    continue
                now = time.monotonic()
                assert local[pointer] == (core, index)
                record = json.loads(row)
                prefix = root / str(core) / str(index)
                prefix.parent.mkdir(exist_ok=True)
                proof = prefix.with_suffix('.lrat')
                cnf = local_cnf(record, fast, args.width)
                sha = digest(cnf)
                artifact.write_bytes(cnf)
                if checking:
                    expected = checks[pointer]
                    if expected[2] != 'CHECKED':
                        assert expected[3] == sha
                        stats['SKIP_'+expected[2]] += 1
                        print(json.dumps((core, index, 'SKIP_'+expected[2])), file=report)
                        pointer += 1
                        continue
                    assert expected[3] == sha and expected[4] == digest(proof.read_bytes())
                    solver_rc = 20
                else:
                    solve = subprocess.run(control_args(args, 'cadical', artifact, proof),
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
                    solver_rc = solve.returncode
                if solver_rc == 20:
                    check = subprocess.run(control_args(args, 'cake_lpr', artifact, proof),
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
                    verdict = 'CHECKED' if check.returncode == 0 and b's VERIFIED UNSAT' in check.stdout.splitlines() else f'CHECK_FAIL_{check.returncode}'
                    proof_sha = digest(proof.read_bytes())
                elif solver_rc == 10:
                    verdict, proof_sha = 'SAT_RELAXATION', None
                else:
                    verdict, proof_sha = f'SOLVE_INCOMPLETE_{solver_rc}', None
                if verdict not in ('CHECKED', 'SAT_RELAXATION'):
                    error = check.stdout if solver_rc == 20 else solve.stdout
                    prefix.with_suffix('.error').write_bytes(error)
                if checking:
                    assert verdict == 'CHECKED'
                stats[verdict] += 1
                print(json.dumps((core, index, verdict, sha, proof_sha, round(time.monotonic()-now, 4)),
                                 separators=(',', ':')), file=report)
                pointer += 1
    finally:
        artifact.unlink(missing_ok=True)
        report.close()
    assert pointer == len(local)
    print('batch', chunk, dict(stats), flush=True)


def prepare(out):
    total, unresolved = 0, 0
    with out.open('w', encoding='ascii') as manifest:
        for core in range(19):
            rows = Path(f'checked.a{core}.jsonl').read_text(encoding='ascii').splitlines()
            assert len(rows) == sum(1 for _ in Path(f'cover.a{core}.jsonl').open(encoding='ascii'))
            for index, raw in enumerate(rows):
                item, dropped, omitted, proof = json.loads(raw)
                assert (item, dropped, omitted) == (index, -1, -1)
                if proof is None:
                    unresolved += 1
                    print(core, index, file=manifest)
                total += 1
    print('cover', total, 'remaining projections', unresolved, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'solve', 'replay'))
    parser.add_argument('plan', type=Path)
    parser.add_argument('--output', type=Path, default=Path('proof.a11'))
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    parser.add_argument('--pilot', type=int, default=0)
    parser.add_argument('--width', type=int, default=8)
    parser.add_argument('--cap', type=int, default=12)
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare(args.plan)
    else:
        run(args, (args.offset, args.stride), args.mode == 'replay')


if __name__ == '__main__':
    main()
