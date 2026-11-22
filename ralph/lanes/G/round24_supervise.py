"""Lease one worker per slot and account for future writes before dispatch."""

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from round23_h5 import Physical, load_models


AUX = 8_000_000
STAGE_LIMIT = 4_350_000_000
WORKSPACE_LIMIT = 146_000_000_000


def moment():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def size(directory):
    for _ in range(3):
        measurement = subprocess.run(['du', '-sb', directory], text=True, capture_output=True, env={**os.environ, 'LC_ALL': 'C'})
        if measurement.returncode == 0:
            return int(measurement.stdout.split()[0])
        errors = measurement.stderr.splitlines()
        if not errors or not all('No such file or directory' in line for line in errors):
            raise RuntimeError(measurement.stderr)
        time.sleep(0.25)
    if measurement.stdout and Path(directory).is_dir():
        return int(measurement.stdout.split()[0]) + 250_000_000
    raise RuntimeError(measurement.stderr)


def append(path, record):
    with path.open('a') as outfile:
        outfile.write(json.dumps(record, sort_keys=True) + '\n')


def footprint(directory, identity):
    archive = directory / 'archive' / (identity + '.lrat.zst')
    temp = archive.with_suffix('.zst.tmp')
    return ((size(directory / 'work' / identity) if (directory / 'work' / identity).exists() else 0) +
            sum(item.stat().st_size for item in (archive, temp) if item.exists()))


def seed(stage, record, boards):
    result = stage / 'work' / record['id'] / 'solve.log'
    oracle = Physical(boards[record['board']]['grid'])
    try:
        witness, graph = oracle.model_witness(load_models(result), 10)
        if witness is None:
            append(stage / 'provisional-graphs.jsonl', dict(board=record['board'], id=record['id'], graph=graph))
            return False
        oracle.row(witness, 10)
    except (AssertionError, OSError, ValueError):
        return False
    folder = stage / 'seeds'
    folder.mkdir(exist_ok=True)
    path = folder / f"{record['board']}.jsonl"
    lines = set(path.read_text().splitlines()) if path.exists() else set()
    lines.add(json.dumps(witness, sort_keys=True))
    tmp = path.with_suffix('.tmp')
    tmp.write_text('\n'.join(sorted(lines)) + '\n')
    tmp.replace(path)
    return True


def supervise(stage, slots, wall, tag, qfile=None):
    assert 1 <= slots <= 16
    root = stage.parents[2]
    worker = root / 'ralph/lanes/G/round24_worker.sh'
    board_file = stage / '../round22/h5/manifest.json'
    boards = json.loads(board_file.read_text())
    qfile = qfile or stage / 'queue.json'
    eventlog = stage / f'{tag}.events.jsonl'
    samplelog = stage / f'{tag}.samples.jsonl'
    census = json.loads((stage / 'complement.json').read_text())
    with (stage / 'dispatch.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        queue = deque(json.loads(qfile.read_text()))
        running = {}
        observed = {}
        last_cpus = {}
        last_finished_cpu = 0.0
        wall_deadline = time.monotonic() + wall
        next_sample = 0
        external = size(stage.parents[1]) - size(stage)
        initial = json.loads((stage / 'incoming.json').read_text())
        checked = {int(board): set(prefixes) for board, prefixes in initial['proofs'].items()}
        explicit = set()
        costs = {}

        def classify(job, child_code=None):
            identity = job['id']
            if identity in observed:
                return
            work = stage / 'work' / identity
            result_file = work / 'result'
            state = result_file.read_text().strip() if result_file.exists() else f'OPEN wrapper exit {child_code}'
            timings = [item.split() for path in work.glob('*.time') for item in path.read_text().splitlines()]
            costs[identity] = sum(float(fields[0]) + float(fields[1]) for fields in timings if len(fields) == 5 and fields[0][0].isdigit())
            observed[identity] = state
            append(eventlog, dict(event='exit', at=moment(), **job, state=state, worker_rc=child_code,
                                  cpu_seconds=costs[identity]))
            if state.startswith('CHECKED '):
                if job['mode'] == 'DN':
                    scope = json.loads((work / 'scope.json').read_text())
                    explicit.update((job['board'], key) for key in scope['keys'])
                else:
                    checked.setdefault(job['board'], set()).add(job['prefix'])
                return
            learned = False
            if 'SAT relaxation' in state:
                learned = seed(stage, job, boards)
            if (job['mode'] in ('D', 'DM') and
                    (learned or any(token in state for token in ('raw cap', 'conversion/compression cap', 'solver exit 124', 'solver exit 137')))
                    and job.get('generation', 0) < 2 and len(job['prefix']) < 8):
                for sign in '01':
                    prefix = job['prefix'] + sign
                    queue.append(dict(board=job['board'], parent=job['prefix'], prefix=prefix,
                                      mode='DM' if learned or job['mode'] == 'DM' else 'D',
                                      keys=job['keys'], id=f'g{job["board"]:03}_{prefix}',
                                      generation=job.get('generation', 0) + 1))

        def sample(force=False):
            nonlocal next_sample, last_cpus, last_finished_cpu, external
            if not force and time.monotonic() < next_sample:
                return
            next_sample = time.monotonic() + 300
            live = {}
            proc = subprocess.check_output(['ps', '-eo', 'pid=,ppid=,stat=,cputimes=,args='], text=True).splitlines()
            children = {}
            for line in proc:
                fields = line.split(None, 4)
                if len(fields) != 5 or not all(fields[index].isdigit() for index in (0, 1, 3)):
                    continue
                pid, parent, state, cpu, command = fields
                children.setdefault(int(parent), []).append((int(pid), state, int(cpu), command))
            current_cpus = {}
            for identity, (child, job, reservation) in running.items():
                tree = list(children.get(child.pid, []))
                for descendant, _, _, _ in tree:
                    tree.extend(children.get(descendant, []))
                current_cpus.update({pid: value for pid, _, value, _ in tree})
                live[identity] = dict(pid=child.pid, reserve=reservation, actual=footprint(stage, identity), tree=tree)
            hits = 0
            for board, information in census.items():
                prefixes = checked.get(int(board), ())
                hits += sum((int(board), key) in explicit or
                            any(word.startswith(prefix) for words in coverage.values() for word in words for prefix in prefixes)
                            for key, coverage in information['residual'].items())
            stage_bytes = size(stage)
            external = size(stage.parents[1]) - stage_bytes
            finished = sum(costs.values())
            append(samplelog, dict(at=moment(), live=live, stage_bytes=stage_bytes, external_bytes=external,
                                   residual_keys_excluded=hits, stages_done=len(observed), queue=len(queue),
                                   finished_cpu_delta=round(finished - last_finished_cpu, 2),
                                   live_cpu_deltas={pid: cpu - last_cpus.get(pid, 0) for pid, cpu in current_cpus.items()},
                                   cumulative_cpu_lower_bound=round(finished + sum(current_cpus.values()), 2)))
            last_cpus = current_cpus
            last_finished_cpu = finished

        append(eventlog, dict(event='start', at=moment(), pid=os.getpid(), slots=slots,
                              queue_sha256=hashlib.sha256(qfile.read_bytes()).hexdigest(), wall_budget=wall))
        while queue or running:
            for identity, (child, job, _) in list(running.items()):
                if child.poll() is not None:
                    classify(job, child.returncode)
                    del running[identity]
            sample()
            while queue and len(running) < slots and time.monotonic() < wall_deadline - 1080:
                job = queue[0]
                identity = job['id']
                if (stage / 'work' / identity).exists():
                    queue.popleft()
                    classify(job)
                    continue
                generation = job.get('generation', 0)
                binary, archive, cpu, learn = (110_000_000, 55_000_000, 195, 75) if not generation else (125_000_000, 60_000_000, 215, 90)
                binary, archive, cpu, learn = job.get('budget', (binary, archive, cpu, learn))
                reservation = binary + archive + AUX
                predicted = size(stage) + sum(bound for _, _, bound in running.values()) + reservation
                if predicted > min(STAGE_LIMIT, WORKSPACE_LIMIT - external):
                    break
                queue.popleft()
                executable = {'DP': worker.with_name('round24_shore_worker.sh'), 'DN': worker.with_name('round24_occupancy_worker.sh')}.get(job['mode'], worker)
                args = ['timeout', '--kill-after=10', '1050', str(executable), str(job['board']),
                        job['prefix'] or '-', job['mode'], identity, str(binary), str(archive), str(cpu), str(learn)]
                with (stage / f'{identity}.log').open('wb') as log:
                    child = subprocess.Popen(args, cwd=stage, stdin=subprocess.DEVNULL, stdout=log,
                                             stderr=subprocess.STDOUT, start_new_session=True)
                running[identity] = (child, job, reservation)
                append(eventlog, dict(event='launch', at=moment(), pid=child.pid, cores=1, wall=1050,
                                      reservation=reservation, log=f'{identity}.log', args=args, **job))
            if not running:
                break
            time.sleep(2)
        sample(force=True)
        (stage / f'{tag}.deferred.json').write_text(json.dumps(list(queue), indent=2) + '\n')
        append(eventlog, dict(event='stop', at=moment(), remaining=len(queue), done=len(observed)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', type=Path)
    parser.add_argument('slots', type=int)
    parser.add_argument('wall_seconds', type=int)
    parser.add_argument('tag')
    parser.add_argument('--queue', type=Path)
    opts = parser.parse_args()
    supervise(opts.stage.resolve(), opts.slots, opts.wall_seconds, opts.tag, opts.queue)
