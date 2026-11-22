#!/usr/bin/env python3
import argparse
from contextlib import ExitStack
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

from panel17_round14 import (CATALOGUE, CPU_LIMIT, DISK_LIMIT, FRAME_COUNT, LANE,
                             REFERENCE, Scan, check, cpu, merge, read_terminal)

CUT, STEP = 24576, 1024
BASE_CPU = 120
C_GATE_MS, PY_GATE_MS, SHARD_GATE_SECONDS = 180, 7000, 300
HEADER_TOTALS = (27198813, 40218398, 40218398, 49836392, 24924719, 13046)
KEYS = ('LL', 'LH', 'HL', 'HH', 'HHrep', 'HHdiag')
PREFIX = LANE.parents[2] / 'scratch/C/r14'


def intervals(start, stop, step):
    return [(low, min(low + step, stop)) for low in range(start, stop, step)]


LOW = intervals(0, CUT, STEP * 2)
HIGH = intervals(CUT, FRAME_COUNT, STEP)


def expected(path):
    rows = {}
    for line in path.read_text().splitlines():
        if not line:
            continue
        low, high, label, bit0, bit1, digest = line.split()
        key = (int(low), int(high), label)
        check(key not in rows and len(bytes.fromhex(digest)) == 32, 'invalid A coverage row')
        rows[key] = (int(bit0), int(bit1), digest)
        check(min(rows[key][:2]) >= 0, 'negative A count')
    for low, high in LOW:
        data = json.loads((PREFIX / f'{low:05d}-{high:05d}/result.json').read_text())
        left, right, digest = rows[low, high, 'ordered']
        check(digest == data['roster_sha256'] and left + right == data['counts'][0]
              and data['unresolved'] == 0, 'round-14 ordered receipt mismatch')
    for bit in range(2):
        check(sum(rows[low, high, 'LH'][bit] for low, high in LOW) ==
              sum(rows[low, high, 'HL'][bit] for low, high in HIGH), 'prefix exchange bit multiplicity')
        total = lambda key: sum(rows[low, high, key][bit] for low, high in HIGH)
        check(total('HH') == 2 * total('HHrep') - total('HHdiag'), 'HH exchange bit multiplicity')
    totals = [sum(sum(rows[low, high, key][:2]) for low, high in LOW + HIGH) for key in KEYS]
    check(tuple(totals) == HEADER_TOTALS, f'A totals {totals}')
    return rows


def check_receipt(result, coverage):
    low, high = result['low'], result['high']
    bit0, bit1, digest = coverage[low, high, 'HHrep']
    diag = sum(coverage[low, high, 'HHdiag'][:2])
    check(result['roster_sha256'] == digest and result['counts'][0] == bit0 + bit1
          and result['diagonal'] == diag and result['by_exchange'] == bit0 + bit1 - diag,
          f'A representative roster mismatch {low}:{high}')


class Triangle(Scan):
    def run(self, low, high, coverage):
        check(sum(path.lstat().st_size for path in self.scope.rglob('*') if path.is_file()) < DISK_LIMIT - (32 << 20),
              'retained disk headroom exhausted')
        raw = (high - low) * (2 * FRAME_COUNT - low - high + 1)
        work = self.scope / f'{low:05d}-{high:05d}'
        work.mkdir()
        start, wall = cpu(), time.monotonic()
        with ExitStack() as stack:
            def logger(name):
                return stack.enter_context((work / name).open('wb'))

            scan_c = stack.enter_context(self.launch(work, [self.build / 'scan_C', 'shard', *self.target, low, high],
                                                       subprocess.DEVNULL, subprocess.PIPE, logger('C.screen.log')))
            scan_a = stack.enter_context(self.launch(work, [self.build / 'scan_A', 'shard', CATALOGUE,
                                                            self.target[2], 'A.atlas', low, high],
                                                       subprocess.DEVNULL, subprocess.PIPE, logger('A.screen.log')))
            panels = stack.enter_context((work / 'panels.ids').open('w'))
            counts, roster_hash, stage_hash = merge(scan_c.stdout, scan_a.stdout, panels, low, high)
            check((scan_c.wait(), scan_a.wait()) == (0, 0), 'scanner child exit')
        check((work / 'A.atlas').read_bytes() == Path(self.target[1]).read_bytes(), 'A atlas mismatch')
        (work / 'A.atlas').unlink()
        columns = [list(map(int, line.split(':')[1].split())) for line in
                   (work / 'A.screen.log').read_text().splitlines() if line.startswith('flip=')]
        check(len(columns) == 2 and [sum(pair) for pair in zip(*columns)] == [raw, *counts],
              'A scanner internal counters')
        check([row[1] for row in columns] == list(coverage[low, high, 'HHrep'][:2]), 'header bit census')
        diag = sum(coverage[low, high, 'HHdiag'][:2])
        report = dict(low=low, high=high, counts=counts, diagonal=diag,
                      by_exchange=counts[0] - diag, roster_sha256=roster_hash, stage_sha256=stage_hash,
                      screen_cpu_s=round(cpu()-start, 3), raw=raw)
        check_receipt(report, coverage)
        check(counts[4] * 100 <= counts[3] or counts[4] == 0, 'terminal-call saving below 100x')
        (work / 'screen.json').write_text(json.dumps(report, sort_keys=True) + '\n')
        panels = [tuple(map(int, line.split())) for line in (work / 'panels.ids').read_text().splitlines()]
        check(len(panels) == counts[-1] and all(low <= left < high and left <= right < FRAME_COUNT and bit in (0, 1)
              for left, right, bit in panels) and panels == sorted(set(panels)), 'invalid panel roster')
        terminals = [work / name for name in ('C.terminal', 'scout.terminal')]
        if panels:
            for name in ('frames17-5-2.txt', 'liftrows.txt'):
                (work / name).symlink_to(REFERENCE / name)
            commands = [[self.build / 'panel17', 'terminal', *self.target],
                        [sys.executable, '-B', LANE / 'panel17_fast_r15.py', 'audit', 'panels.ids', PY_GATE_MS]]
            with ExitStack() as stack:
                processes = []
                for path, command in zip(terminals, commands):
                    args = (stack.enter_context((work / 'panels.ids').open('rb')),
                            stack.enter_context(path.open('wb')),
                            stack.enter_context(path.with_suffix(path.suffix + '.log').open('wb')))
                    processes.append(stack.enter_context(self.launch(work, command, *args)))
                exits = [process.wait() for process in processes]
                check(exits == [0, 0], f'terminal exit {exits}, shard remains unresolved')
        else:
            for path in terminals:
                path.touch()
        first, second = [read_terminal(path, panels) for path in terminals]
        details = [row for row, _ in first]
        check(details == [row for row, _ in second], 'terminal disposition mismatch')
        check(not any(row[-1] for row in details), 'live filling')
        tails = [max((ms for _, ms in data), default=0) for data in (first, second)]
        (work / 'terminal.keyed').write_text(''.join(' '.join(map(str, row)) + '\n' for row in details))
        report.update(unresolved=0, joint=sum(any(row[3:]) for row in details), tail_ms=tails,
                      max_fill=max((sum(row[3:]) for row in details), default=0),
                      fillings=[sum(row[index] for row in details) for index in range(3, 8)],
                      terminal_sha256=sha256((work / 'terminal.keyed').read_bytes()).hexdigest(),
                      cpu_s=round(cpu()-start, 3), wall_s=round(time.monotonic()-wall, 3))
        check(tails[0] <= C_GATE_MS and tails[1] <= PY_GATE_MS, 'per-ID tail stop, shard uncertified')
        check(report['cpu_s'] <= SHARD_GATE_SECONDS, 'shard CPU tail stop')
        (work / 'result.json').write_text(json.dumps(report, sort_keys=True) + '\n')
        print(json.dumps(report, sort_keys=True), flush=True)
        return report


def plan(used, remaining, results):
    prefix_tail = json.loads((PREFIX / '22528-24576/result.json').read_text())
    rate = max(row['cpu_s'] / row['counts'][0] for row in [prefix_tail, *results] if row['counts'][0])
    projection = used + 3 * remaining * rate + 3 * len(HIGH)
    print(json.dumps(dict(remaining_representatives=remaining, charged_cpu_s=round(used, 3),
                          projected_end_cpu_s=round(projection, 3))), flush=True)
    check(projection <= CPU_LIMIT, 'projected total independent work exceeds two CPU-h')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('work', type=Path)
    parser.add_argument('expected', type=Path)
    parser.add_argument('phase', choices=('first', 'rest'))
    args = parser.parse_args()
    work = args.work.resolve()
    coverage = expected(args.expected)
    results = []
    remaining = HEADER_TOTALS[-2]
    if args.phase == 'rest':
        for low, high in HIGH:
            directory = work / f'{low:05d}-{high:05d}'
            if not directory.exists():
                break
            report = json.loads((directory / 'result.json').read_text())
            check_receipt(report, coverage)
            check(report['unresolved'] == 0 and report['low'] == low and report['high'] == high, 'prior shard invalid')
            results.append(report)
            remaining -= report['counts'][0]
        check(results, 'first shard not priced')
    scan = Triangle(work, work, BASE_CPU + sum(row['cpu_s'] for row in results))
    plan(scan.used(), remaining, results)
    next_count = 1 if args.phase == 'first' else len(HIGH)
    upcoming = HIGH[len(results):len(results)+next_count]
    check(not upcoming or not (work / f'{upcoming[0][0]:05d}-{upcoming[0][1]:05d}').exists(), 'overlapping shard')
    for low, high in upcoming:
        report = scan.run(low, high, coverage)
        results.append(report)
        remaining -= report['counts'][0]
        plan(scan.used(), remaining, results)


if __name__ == '__main__':
    main()
