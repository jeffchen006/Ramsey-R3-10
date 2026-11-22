#!/usr/bin/env python3
"""Run and independently rebind only the frozen round-19 comparison queue."""

import argparse
from collections import Counter
import csv
from hashlib import sha256
from itertools import chain
import json
from pathlib import Path
from resource import RUSAGE_CHILDREN, RUSAGE_SELF, getrusage
import subprocess

from bind_width74 import binding
from involution_sat import from_graph6
from m11_sat import FastCuts
from price_width74 import formula


OLD = Path('../r18_shared')
FULL = Path('../r19_shared')
TOOLS = Path('../../../opt/bin').resolve()
FASTCUTS = Path('../r6_e11/m11_fastcuts.so')
PROFILE = [10, 10, 11, 11]
FILE_CAP = 8 * 1024**2
SOFT_STAGE_CAP = 94 * 1024**2
INCOMPLETE = {124, 137, 152, 153, -24, -25}
CHECKERS = (
    ('cake_lpr', ('--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=64'), 's VERIFIED UNSAT'),
    ('lrat-check', (), 'c VERIFIED'),
)


def cpu():
    return sum(usage.ru_utime + usage.ru_stime
               for usage in map(getrusage, (RUSAGE_SELF, RUSAGE_CHILDREN)))


def disk(root):
    return sum(path.stat().st_size for path in root.rglob('*') if path.is_file())


def room(storage=0):
    assert disk(Path('.')) + storage < SOFT_STAGE_CAP, 'aggregate staging stop'


def digest(content):
    return sha256(content).hexdigest()


def write(path, content):
    room(len(content))
    with path.open('xb') as stream:
        stream.write(content)


def timed(tool, args, log, cpu_limit, wall):
    output_cap = FILE_CAP
    room(2 * output_cap if tool == 'cadical' else output_cap)
    with log.open('x', encoding='ascii') as stream:
        return subprocess.run([
            'nice', '-n', '5', '/usr/bin/time', '-f', 'wall=%e cpu=%U+%S RSS=%M',
            'timeout', '--foreground', '-k', '1s', f'{wall}s',
            'prlimit', f'--cpu={cpu_limit}:{cpu_limit + 1}',
            f'--fsize={output_cap}:{output_cap}', '--', str(TOOLS / tool), *map(str, args),
        ], stdout=stream, stderr=subprocess.STDOUT).returncode


def log_ok(log, marker):
    return marker in log.read_text(encoding='ascii').splitlines()


def solve(cnf):
    log = cnf.with_suffix('.solve.log')
    code = timed('cadical', ('-q', '--lrat', '--no-binary', cnf, cnf.with_suffix('.lrat')), log, 7, 15)
    if code == 20:
        assert log_ok(log, 's UNSATISFIABLE'), cnf
        return 'UNSAT'
    if code == 10:
        assert log_ok(log, 's SATISFIABLE'), cnf
        return 'SAT'
    assert code in INCOMPLETE, (cnf, code)
    return f'INCOMPLETE_{code}'


def check(cnf):
    proof = cnf.with_suffix('.lrat')
    assert proof.stat().st_size > 0, proof
    start = cpu()
    for tool, options, marker in CHECKERS:
        log = cnf.with_suffix(f'.{tool}.log')
        code = timed(tool, (*options, cnf, proof), log, 10, 30)
        assert code == 0 and log_ok(log, marker), (cnf, tool, code)
    return cpu() - start


def ids(path):
    result = []
    for index, ordinal, status in map(json.loads, path.read_text(encoding='ascii').splitlines()):
        assert status == 'open'
        result.append((index, ordinal))
    assert result == sorted(set(result))
    return result


def roster():
    chosen, pending, terminal, old = (
        ids(path) for path in (FULL/'proposed_pilot.1.jsonl', FULL/'pending.1.jsonl',
                               FULL/'terminal.1.jsonl', OLD/'matched.1.jsonl'))
    assert len(chosen) == len(old) == 16 and len(pending) == 131 and len(terminal) == 147
    assert sorted([*old, *pending]) == terminal and set(chosen) <= set(pending)
    receipts = []
    with (FULL/'cover.1.receipt.jsonl').open('rb') as stream:
        for row in stream:
            index, ordinal, verdict, *_ = json.loads(row)
            if verdict == 'open':
                receipts.append((index, ordinal))
    assert receipts == terminal
    with (FULL/'branch_rates.tsv').open(encoding='ascii') as stream:
        branches = [(int(row['index']), int(row['row_begin']), int(row['rows']), row['branch'])
                    for row in csv.DictReader(stream, delimiter='\t')]
    assert len(branches) == 24
    chosen_projections = {key[0] for key in chosen}
    with (OLD/'cover.1.jsonl').open('rb') as stream:
        original = {index: row for index, row in enumerate(stream) if index in chosen_projections}
    split = {}
    for index, begin, size, mark in branches:
        local = {projection-begin for projection in original if begin <= projection < begin + size}
        if not local:
            continue
        with (FULL/f'branches/cover.{index:02d}.jsonl').open('rb') as stream:
            for offset, row in enumerate(stream):
                if offset in local:
                    split[begin+offset] = (row, index, min(2, 3*offset//size), mark)
    assert set(split) == set(original) == chosen_projections
    for projection, (row, _, _, mark) in split.items():
        assert row == original[projection]
        assert json.loads(row)[2][0] == list(map(int, mark.split(',')))
    return chosen, pending, original, split


def physical(row, ordinal):
    key, profile, parts, omitted = json.loads(row)
    assert key == 'G?bFbo' and profile == PROFILE and 0 <= ordinal < len(omitted)
    groups = (*parts, omitted[ordinal])
    assert [sum(map(int.bit_count, group)) for group in groups] == profile
    return from_graph6(key), groups, (7,)*4, (7,)*24


def narrow_attempt(root, phys, rebound, fast):
    start = cpu()
    base, cnf = root/'reference8.cnf', root/'width3.cnf'
    write(base, formula(*phys, 8, fast))
    write(cnf, formula(*phys, 3, fast))
    assert cnf.read_bytes() == formula(*rebound, 3, fast), cnf
    binding(*rebound, base, cnf)
    prep = cpu() - start
    start = cpu()
    status = solve(cnf)
    solve_cpu = cpu() - start
    verify = check(cnf) if status == 'UNSAT' else 0.0
    return dict(status=status, prepare=prep, solve=solve_cpu, verify=verify, bytes=disk(root),
                cnf=digest(cnf.read_bytes()),
                proof=digest(cnf.with_suffix('.lrat').read_bytes()) if status == 'UNSAT' else None)


def wide_attempt(root, phys, rebound, fast, reference, positive=False):
    start = cpu()
    cnf = root/'width8.cnf'
    write(cnf, formula(*phys, 8, fast))
    prep = cpu() - start
    start = cpu()
    status = solve(cnf)
    solve_cpu = cpu() - start
    assert status == ('SAT' if positive else 'UNSAT'), (cnf, status)
    start = cpu()
    assert cnf.read_bytes() == formula(*rebound, 8, fast) == reference.read_bytes(), cnf
    prep += cpu() - start
    verify = 0.0 if positive else check(cnf)
    return dict(status=status, prepare=prep, solve=solve_cpu, verify=verify, bytes=disk(root),
                cnf=digest(cnf.read_bytes()),
                proof=digest(cnf.with_suffix('.lrat').read_bytes()) if not positive else None)


def pair(root, phys, rebound, fast, positive=False):
    narrow, wide = root/'narrow', root/'wide'
    narrow.mkdir(parents=True)
    wide.mkdir()
    result = narrow_attempt(narrow, phys, rebound, fast)
    assert not positive or result['status'] == 'SAT'
    wide_result = wide_attempt(wide, phys, rebound, fast, narrow/'reference8.cnf', positive=positive)
    return result, wide_result


def controls(fast):
    core, groups, bounds = (0,), ((1,), (0,), (0,), (0, 0)), (3,)*4
    positive = (core, groups, bounds, (2, 1, 2, 1, 1))
    negative = (core, groups, bounds, (3, 1, 1, 1, 1))
    for label, case in (('positive', positive), ('negative', negative)):
        result = pair(Path('controls')/label, case, case, fast, positive=(label == 'positive'))
        assert {item['status'] for item in result} == {'SAT' if label == 'positive' else 'UNSAT'}
        print(label, result, flush=True)
    good = Path('controls/positive/narrow/reference8.cnf')
    bad = Path('controls/negative/narrow/width3.cnf')
    try:
        binding(*positive, good, bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted wrong degree formula')
    bad_lift = (core, ((1,), (0,), (0,), (0, 1)), bounds, positive[-1])
    try:
        binding(*bad_lift, good, good.with_name('width3.cnf'))
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted wrong physical lift')
    print('wrong lift and wrong formula rejected; SAT control fell through to width eight', flush=True)


def target(fast):
    start = cpu()
    chosen, _, original, split = roster()
    jobs = Counter()
    print(f'frozen_roster_cpu={cpu()-start:.6f}', flush=True)
    with Path('paired.jsonl').open('x', encoding='ascii') as out:
        for projection, ordinal in chosen:
            case = Path('target')/f'{projection}_{ordinal}'
            row, branch, third, _ = split[projection]
            start = cpu()
            narrow, wide = pair(case, physical(original[projection], ordinal), physical(row, ordinal), fast)
            choice = 'narrow' if narrow['status'] == 'UNSAT' else 'wide-fallback'
            jobs[choice] += 1
            data = dict(id=[projection, ordinal], branch=branch, third=third, choice=choice,
                        row=digest(row), cpu=cpu()-start, narrow=narrow, wide=wide)
            print(json.dumps(data, sort_keys=True), file=out, flush=True)
            print(projection, ordinal, branch, third, choice, f'{data["cpu"]:.6f}s', flush=True)
    print('paired dual checked:', dict(jobs), 'unique physical IDs:', sum(jobs.values()), flush=True)


def audit():
    chosen, pending, _, split = roster()
    checked = []
    for record in map(json.loads, Path('paired.jsonl').read_text(encoding='ascii').splitlines()):
        key = tuple(record['id'])
        projection, ordinal = key
        row, branch, third, _ = split[projection]
        assert (branch, third, digest(row)) == (record['branch'], record['third'], record['row'])
        root = Path('target')/f'{projection}_{ordinal}'
        for mode, width in (('narrow', 3), ('wide', 8)):
            stats = record[mode]
            cnf = root/mode/f'width{width}.cnf'
            assert stats['bytes'] == disk(cnf.parent) and stats['cnf'] == digest(cnf.read_bytes())
            if stats['status'] == 'UNSAT':
                assert stats['proof'] == digest(cnf.with_suffix('.lrat').read_bytes())
                for tool, _, marker in CHECKERS:
                    assert log_ok(cnf.with_suffix(f'.{tool}.log'), marker)
            else:
                assert mode == 'narrow' and stats['proof'] is None
        assert record['wide']['status'] == 'UNSAT'
        assert record['choice'] == ('narrow' if record['narrow']['status'] == 'UNSAT' else 'wide-fallback')
        checked.append(key)
    assert checked == chosen[:len(checked)] and len(checked) == len(set(checked))
    with Path('residual.jsonl').open('x', encoding='ascii') as out:
        left = sorted(set(pending) - set(checked))
        for key in left:
            print(json.dumps((*key, 'open'), separators=(',', ':')), file=out)
    assert sorted(chain(checked, left)) == pending
    print('exact paired prefix', len(checked), 'residual', len(left), 'staged bytes', disk(Path('.')), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('controls', 'target', 'audit'))
    mode = parser.parse_args().mode
    if mode == 'audit':
        audit()
    else:
        (controls if mode == 'controls' else target)(FastCuts(FASTCUTS))
