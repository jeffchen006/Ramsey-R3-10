#!/usr/bin/env python3
"""Recover the omitted size-twelve incidence group only for surviving windows."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path

from audit_m11 import read_json, verify_trace
from batch_a11 import control_args, digest
from involution_sat import from_graph6
from m11_prop import Prover, targets
from m11_sat import FastCuts, encode
from m11_support import Supports
import subprocess


def direct_options(core, degree, parts):
    singles = tuple(vertex for vertex, count in enumerate(degree) if count == 1)
    if len(singles) > 6 or max(degree) > 6:
        return set()
    double = tuple(vertex for vertex in range(len(core)) if vertex not in singles)
    edges = tuple((left, right) for left, right in combinations(range(len(core)), 2) if core[left] >> right & 1)
    tests = tuple(actors for count in range(2, len(core)+1) for actors in combinations(range(len(core)), count)
                  if not any(core[left] >> right & 1 for left, right in combinations(actors, 2)))
    domains = [tuple(sum(1 << slot for slot in choice) for choice in combinations(range(6), degree[vertex]))
               for vertex in double]
    rows = [0]*len(core)
    for slot, vertex in enumerate(singles):
        rows[vertex] = 1 << slot
    valid = set()
    for assigned in product(*domains):
        for vertex, row in zip(double, assigned):
            rows[vertex] = row
        if any(rows[left] & rows[right] for left, right in edges):
            continue
        for test in tests:
            union = 0
            for actor in test:
                union |= rows[actor]
            if union.bit_count() < len(test):
                break
        else:
            group = tuple(sorted(sum(1 << vertex for vertex, row in enumerate(rows) if row >> slot & 1)
                                 for slot in range(6)))
            all_groups = (*parts, group)
            for omitted in range(4):
                retained = all_groups[:omitted] + all_groups[omitted+1:]
                lower, _ = targets(core, retained)
                if any(lower[left].bit_count() == 7 and not (lower[left] >> right & 1) and
                       not (lower[left] & lower[right])
                       for left in range(len(core)) for right in range(len(core)) if left != right):
                    break
            else:
                valid.add(group)
    return valid


def options(key, parts, independent=False):
    core = from_graph6(key)
    support = Supports(core, 6)
    cap = tuple(4-row.bit_count() for row in core)
    used = [support.info(tuple(group))[0] for group in parts]
    missing = tuple(1 + upper - sum(cost[actor] for cost in used) for actor, upper in enumerate(cap))
    assert sum(missing) == 12 and min(missing) >= 1
    viable = tuple(group for group in support.options(missing) if support.admissible((*map(tuple, parts), group)))
    if independent:
        assert direct_options(core, missing, tuple(map(tuple, parts))) == set(viable)
    Supports.options.cache_clear()
    Supports.info.cache_clear()
    return core, viable


def cnf_for(core, groups, omitted, fast, width):
    if omitted == -1:
        variables, rows, _, _ = encode(core, groups, (7,)*4, (7,)*24, cut_size=width, fast=fast)
    else:
        window = groups[:omitted] + groups[omitted+1:]
        variables, rows, _, _ = encode(core, window, (None,)*3, edge_target=74, cut_size=width, fast=fast)
    return (f'p cnf {variables} {len(rows)}\n' + ''.join(' '.join(map(str, row)) + (' ' if row else '') + '0\n'
                                                       for row in rows)).encode('ascii')


def local_proof(core, groups, fast, args, stub, record=None):
    proof = stub.with_suffix('.lrat')
    artifact = stub.with_suffix('.cnf')
    candidates = ((0, 8), (1, 8), (2, 8), (-1, 8), (-1, 28)) if record is None else (tuple(record[:2]),)
    for omitted, width in candidates:
        cnf = cnf_for(core, groups, omitted, fast, width)
        if record is None:
            artifact.write_bytes(cnf)
            solve = subprocess.run(control_args(args, 'cadical', artifact, proof), capture_output=True, check=False)
            if solve.returncode != 20:
                continue
        else:
            assert cnf == artifact.read_bytes() and digest(cnf) == record[2]
            assert digest(proof.read_bytes()) == record[3]
        checker = subprocess.run(control_args(args, 'cake_lpr', artifact, proof), capture_output=True, check=False)
        if checker.returncode or b's VERIFIED UNSAT' not in checker.stdout.splitlines():
            continue
        return True, (omitted, width, digest(cnf), digest(proof.read_bytes()))
    return False, None


def cover_file(keys, output, verify=False, args=None):
    stats = Counter()
    prover = None if verify else Prover(Path('m11_prop.so'))
    plans = sorted(tuple(map(int, line.split()[:2])) for line in keys.read_text(encoding='ascii').splitlines())
    assert len(plans) == len(set(plans))
    traces = iter(read_json(output)) if verify else None
    stream = None if verify else output.open('w', encoding='ascii')
    manifests = {}
    fast = FastCuts(Path('m11_fastcuts.so')) if args and args.prove else None
    if fast is not None:
        args.prove.mkdir(parents=True, exist_ok=True)
    for core_id, index in plans:
        if core_id not in manifests:
            manifests[core_id] = Path(f'cover.a{core_id}.jsonl').read_text(encoding='ascii').splitlines()
        key, profile, parts, empty = json.loads(manifests[core_id][index])
        assert profile == [10, 10, 10, 12] and not empty
        core, viable = options(key, parts, verify)
        stats['projections'] += 1
        stats['omitted_supports'] += len(viable)
        if not viable:
            stats['no_omitted_support'] += 1
        if verify:
            info = next(traces)
            assert info[:2] == [core_id, index]
            recorded = info[2]
            assert len(recorded) == len(viable)
        cases = []
        for serial, group in enumerate(viable):
            all_groups = (*parts, group)
            stub = args.prove/f'{core_id}_{index}_{serial}' if fast is not None else None
            if verify:
                saved, omitted, trace = recorded[serial]
                assert tuple(saved) == group
                if omitted == 4:
                    assert fast is not None and trace is not None
                    status, _ = local_proof(core, all_groups, fast, args, stub, trace)
                    assert status
                    stats['lrat_checked'] += 1
                else:
                    assert 0 <= omitted < 3
                    window = all_groups[:omitted] + all_groups[omitted+1:]
                    verify_trace(core, window, trace)
                    stats['checked'] += 1
                continue
            for omitted in range(3):
                window = all_groups[:omitted] + all_groups[omitted+1:]
                lower, upper = targets(core, window)
                trace = prover.prove(lower, upper, 7, 74)
                if trace[0]:
                    verify_trace(core, window, trace)
                    cases.append((group, omitted, trace))
                    stats['checked'] += 1
                    break
            else:
                if fast is not None:
                    result, binding = local_proof(core, all_groups, fast, args, stub)
                    if result:
                        cases.append((group, 4, binding))
                        stats['lrat_checked'] += 1
                        continue
                cases.append((group, -1, None))
                stats['open'] += 1
        if not verify:
            print(json.dumps((core_id, index, cases), separators=(',', ':')), file=stream)
    if verify:
        assert next(traces, None) is None
    else:
        stream.close()
    print('verified' if verify else 'production', dict(stats), flush=True)
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('scan', 'verify'))
    parser.add_argument('keys', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--prove', type=Path)
    parser.add_argument('--cap', type=int, default=12)
    args = parser.parse_args()
    cover_file(args.keys, args.output, args.mode == 'verify', args)


if __name__ == '__main__':
    main()
