#!/usr/bin/env python3
import argparse
from collections import Counter
from contextlib import ExitStack
from hashlib import sha256
import json
from pathlib import Path
import resource
import struct
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
LANE = Path(__file__).resolve().parent
REFERENCE = ROOT / 'scratch/ideas/r012_R'
CATALOGUE = ROOT / 'gluing/val'
RECORD = struct.Struct('<HHHH')
FRAME_COUNT = 55055
HEADER_COUNT = 157472001
FIRST_COUNT = 4322749
FIRST_END = 2048
PILOT_COUNT = 1554349
PILOT_CPU = sum((5.85, 6.79, .35, 13.18))
BASE_CPU = 45
CPU_LIMIT = 7200
DISK_LIMIT = 1 << 30


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def cpu():
    readings = [resource.getrusage(scope) for scope in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)]
    return sum(reading.ru_utime + reading.ru_stime for reading in readings)


def merge(left, right, panels, low, high):
    stages, ids = sha256(), sha256()
    histogram = Counter()
    prior = None
    while True:
        row = left.read(1 << 20)
        other = right.read(1 << 20)
        if row != other:
            offsets = range(0, min(len(row), len(other)), RECORD.size)
            offset = next((offset for offset in offsets if row[offset:offset+8] != other[offset:offset+8]),
                          min(len(row), len(other)))
            raise RuntimeError(f'scanner mismatch: {row[offset:offset+8].hex()} != {other[offset:offset+8].hex()}')
        if not row:
            break
        check(len(row) % RECORD.size == 0, 'short stage record')
        first, last = RECORD.unpack_from(row), RECORD.unpack_from(row, len(row)-RECORD.size)
        check(low <= first[0] <= last[0] < high and (prior is None or prior < first[:3]), 'shard/chunk boundary')
        prior = last[:3]
        stages.update(row)
        depths, flips = row[6::8], row[4::8]
        per_depth = {depth: depths.count(depth) for depth in range(1, 6)}
        check(row[5::8].count(0) == len(depths) and row[7::8].count(0) == len(depths) and sum(per_depth.values()) == len(depths)
              and flips.count(0) + flips.count(1) == len(flips), 'invalid stage stream')
        histogram.update(per_depth)
        roster = bytearray(row)
        roster[6::8] = bytes(len(depths))
        ids.update(roster)
        offset = depths.find(b'\x05')
        while offset != -1:
            left_id, right_id, flip, _ = RECORD.unpack_from(row, offset * RECORD.size)
            panels.write(f'{left_id} {right_id} {flip}\n')
            offset = depths.find(b'\x05', offset + 1)
    return [sum(histogram[depth] for depth in range(first, 6)) for first in range(1, 6)], ids.hexdigest(), stages.hexdigest()


def read_terminal(path, panel_ids):
    data = []
    with path.open() as stream:
        for line in stream:
            values = line.split()
            check(len(values) == 9, f'invalid receipt in {path}')
            detail = tuple(int(item) for item in values[:8])
            elapsed = float(values[8])
            check(all(value >= 0 for value in detail) and 0 <= elapsed < float('inf'), 'invalid receipt values')
            data.append((detail, elapsed))
    check([row[:3] for row, _ in data] == panel_ids, f'{path}: wrong panel roster')
    return data


class Scan:
    def __init__(self, build, scope, baseline):
        self.build = build
        self.scope = scope
        self.baseline = baseline
        self.start = cpu()
        self.target = [str(CATALOGUE / 'r3_6_17.g6'), str(REFERENCE / 'liftrows.txt'),
                       str(REFERENCE / 'frames17-5-2.txt')]

    def used(self):
        return self.baseline + cpu() - self.start

    def launch(self, workdir, command, stdin, stdout, stderr):
        per_process = min(300, int((CPU_LIMIT - self.used() - 10) // 2))
        check(per_process >= 5, 'CPU hard limit: no room for another child pair')
        return subprocess.Popen(['nice', '-n', '5', 'timeout', '360', 'prlimit',
                                 '--as=17179869184', '--fsize=4194304', '--core=0',
                                 f'--cpu={per_process}:{per_process}', '--', *map(str, command)],
                                cwd=workdir, stdin=stdin, stdout=stdout, stderr=stderr)

    def run(self, low, high):
        check(sum(path.stat().st_size for path in self.build.rglob('*') if path.is_file()) < DISK_LIMIT - (64 << 20),
              'retained disk headroom exhausted')
        work = self.scope / f'{low:05d}-{high:05d}'
        work.mkdir()
        start = cpu()
        wall = time.monotonic()
        with ExitStack() as stack:
            log_c = stack.enter_context((work / 'C.screen.log').open('wb'))
            log_a = stack.enter_context((work / 'A.screen.log').open('wb'))
            panels = stack.enter_context((work / 'panels.ids').open('w'))
            scanner_c = stack.enter_context(self.launch(work, [self.build / 'scan_C', 'shard', *self.target, low, high],
                                                        subprocess.DEVNULL, subprocess.PIPE, log_c))
            scanner_a = stack.enter_context(self.launch(work, [self.build / 'scan_A', 'shard', CATALOGUE,
                                                                self.target[2], 'A.atlas', low, high],
                                                        subprocess.DEVNULL, subprocess.PIPE, log_a))
            counts, roster_hash, stage_hash = merge(scanner_c.stdout, scanner_a.stdout, panels, low, high)
            exits = (scanner_c.wait(), scanner_a.wait())
            check(exits == (0, 0), f'scanner exits {exits}')
        headers, forward, reverse, local, panel = counts
        check((work / 'A.atlas').read_bytes() == Path(self.target[1]).read_bytes(), 'A regenerated atlas mismatch')
        (work / 'A.atlas').unlink()
        expected_a = [0] * 6
        for line in (work / 'A.screen.log').read_text().splitlines():
            if line.startswith('flip='):
                for index, item in enumerate(line.split(':')[1].split()):
                    expected_a[index] += int(item)
        check(expected_a == [2 * FRAME_COUNT * (high-low), *counts], 'A internal counters disagree')
        if (low, high) == (0, FIRST_END):
            check(headers == FIRST_COUNT, f'wrong first header count: {headers}')
        screen_seconds = cpu() - start
        panel_ids = [tuple(map(int, line.split())) for line in (work / 'panels.ids').read_text().splitlines()]
        check(len(panel_ids) == panel and all(first < second for first, second in zip(panel_ids, panel_ids[1:])),
              'panel order/count')
        (work / 'screen.json').write_text(json.dumps(dict(low=low, high=high, counts=counts,
            roster_sha256=roster_hash, stage_sha256=stage_hash, screen_cpu_s=screen_seconds)) + '\n')
        C_file, A_file = (work / label for label in ('C.terminal', 'scout.terminal'))
        if panel:
            for name in ('frames17-5-2.txt', 'liftrows.txt'):
                (work / name).symlink_to(REFERENCE / name)
            check((CATALOGUE / 'r3_6_17.g6').is_file() and (work / 'frames17-5-2.txt').is_file()
                  and (work / 'liftrows.txt').is_file(), 'scout inputs missing')
            with ExitStack() as stack:
                terminals = []
                for out, cmd in ((C_file, [self.build / 'panel17', 'terminal', *self.target]),
                                 (A_file, [sys.executable, '-B', LANE / 'verify_panel17.py', 'scout', 'panels.ids'])):
                    log = stack.enter_context(out.with_suffix(out.suffix + '.log').open('wb'))
                    target = stack.enter_context(out.open('wb'))
                    source = stack.enter_context((work / 'panels.ids').open('rb'))
                    terminals.append(stack.enter_context(self.launch(work, cmd, source, target, log)))
                exits = [terminal.wait() for terminal in terminals]
                check(exits == [0, 0], f'terminal exits {exits}')
        else:
            C_file.touch()
            A_file.touch()
        first_result = read_terminal(C_file, panel_ids)
        second_result = read_terminal(A_file, panel_ids)
        keyed = [row for row, _ in first_result]
        opens = [row for row in keyed if row[7] > 0]
        with (work / 'unresolved.tsv').open('w') as unresolved:
            for row in opens:
                print(*row, file=unresolved)
        check(keyed == [row for row, _ in second_result], 'terminal reason-vector disagreement')
        receipts = ''.join(' '.join(map(str, row)) + '\n' for row in keyed)
        (work / 'terminal.keyed').write_text(receipts)
        joint = sum(any(row[3:]) for row in keyed)
        tails = [max((elapsed for _, elapsed in result), default=0) for result in (first_result, second_result)]
        total_fills = [sum(row[index] for row in keyed) for index in range(3, 8)]
        max_fill = max((sum(row[3:]) for row in keyed), default=0)
        total = cpu() - start
        report = dict(low=low, high=high, raw=2*FRAME_COUNT*(high-low), counts=counts,
                      joint=joint, unresolved=len(opens), fillings=total_fills, max_fill=max_fill,
                      roster_sha256=roster_hash, stage_sha256=stage_hash, terminal_sha256=sha256(receipts.encode()).hexdigest(),
                      cpu_s=round(total, 3), screen_cpu_s=round(screen_seconds, 3), tail_ms=tails,
                      wall_s=round(time.monotonic()-wall, 3))
        (work / 'result.json').write_text(json.dumps(report, sort_keys=True) + '\n')
        print(json.dumps(report, sort_keys=True), flush=True)
        return report


def gate(result):
    headers, _, _, local, panel = result['counts']
    check(panel == 0 or local >= 100 * panel, 'terminal call reduction below 100x')
    check(result['unresolved'] == 0, 'unresolved terminal ID; no new shards')
    check(result['tail_ms'][0] <= 100 and result['tail_ms'][1] <= 1000, 'new expensive terminal tail')
    check(result['cpu_s'] <= 300, 'new expensive shard tail')
    return result['cpu_s'] * HEADER_COUNT / headers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('work', type=Path)
    parser.add_argument('phase', choices=('first', 'rest'))
    parser.add_argument('--step', type=int, default=2048)
    args = parser.parse_args()
    build = args.work.resolve()
    if args.phase == 'first':
        scan = Scan(build, build, BASE_CPU)
        result = scan.run(0, FIRST_END)
        projection = gate(result)
        pilot_projection = PILOT_CPU * HEADER_COUNT / PILOT_COUNT
        print(json.dumps(dict(first_projection_cpu_s=projection, pilot_projection_cpu_s=pilot_projection)), flush=True)
        check(max(projection, pilot_projection) + BASE_CPU <= CPU_LIMIT, 'full scan projection exceeds two CPU-h')
        return
    first = json.loads((build / '00000-02048/result.json').read_text())
    check(first['low'] == 0 and first['high'] == FIRST_END and first['counts'][0] == FIRST_COUNT, 'first shard binding')
    check(1 <= args.step <= FIRST_END and max(gate(first), PILOT_CPU * HEADER_COUNT / PILOT_COUNT) +
          BASE_CPU <= CPU_LIMIT, 'full scan projection exceeds two CPU-h')
    scan = Scan(build, build, BASE_CPU + first['cpu_s'])
    for low in range(FIRST_END, FRAME_COUNT, args.step):
        result = scan.run(low, min(FRAME_COUNT, low + args.step))
        gate(result)
    print(json.dumps(dict(aggregate_charged_cpu_s=scan.used(), remaining_ceiling_cpu_s=CPU_LIMIT-scan.used())), flush=True)


if __name__ == '__main__':
    main()
