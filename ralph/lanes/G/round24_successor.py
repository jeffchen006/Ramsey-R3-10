"""Sequence disjoint h5 replacements after every first-wave child exits."""

import fcntl
import json
import os
import subprocess
import sys
from pathlib import Path

from round24_plan import complement
from round24_representatives import plan
from round24_status import scan
from round24_supervise import size, supervise


def h4_checks(stage, source):
    for identity, amount, arguments in [
            ('h4-controls', 55, ['round24_h4.py', 'controls']),
            ('h4-h5-inventory-control', 95, ['round24_h4_inventory.py', '17', 'h5-regression.json']),
            ('h4-inventory', 120, ['round24_h4_inventory.py', '16', 'h4-manifest.json'])]:
        command = ['timeout', '--kill-after=10', str(3 * amount + 20), 'prlimit',
                   f'--cpu={amount}:{amount}', '--as=5368709120:5368709120', '--', sys.executable,
                   '-B', str(source / arguments[0]), *arguments[1:]]
        with (stage / (identity + '.log')).open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, cwd=stage)
            print('launch', child.pid, identity, command, flush=True)
            result = child.wait()
        print('exit', child.pid, identity, result, flush=True)
        if result:
            break


def main(stage):
    workspace = stage.parents[2]
    source = workspace / 'ralph/lanes/G'
    os.environ.update(PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', LC_ALL='C')
    # Continuation is serialized behind the dispatch lock of the original worker.
    with (stage / 'dispatch.lock').open('a') as guard:
        fcntl.flock(guard, fcntl.LOCK_EX)
    initial = stage / 'after-live.json'
    scan(workspace, stage, initial, hash_archive=False)
    after = json.loads(initial.read_text())
    shore = {int(path.stem) for path in (stage / 'shore-seeds').glob('*.jsonl')}
    cover = json.loads((stage / 'complement.json').read_text())
    follow = []
    for board in after['boards_open']:
        if board not in shore:
            continue
        prefixes = list(after['proofs'].get(str(board), {}))
        for prefix in complement(prefixes):
            footprint = 0
            for labels in cover[str(board)]['residual'].values():
                all_labels = [word for items in labels.values() for word in items]
                if any(word.startswith(scope) for word in all_labels for scope in prefixes):
                    continue
                footprint += any(word.startswith(prefix) for word in all_labels)
            if footprint:
                follow.append(dict(id=f'p{board:03}_{prefix or "all"}', board=board, prefix=prefix, parent=prefix,
                                   mode='DP', keys=footprint, budget=[95_000_000, 47_000_000, 130, 75]))
    representatives = plan(stage, initial, omit=shore)
    # Two contrasting same-scope SAT replacements, plus two already-small cap controls.
    name = stage / 'successor-pilot.json'
    pilot = follow[:2] + representatives[:2]
    for item in pilot:
        item['budget'] = [85_000_000, 42_000_000, 50, 30]
    name.write_text(json.dumps(pilot, indent=2) + '\n')
    if pilot:
        supervise(stage, 4, 1800, 'successor-pilot', name)
    eligible = set()
    for item in pilot:
        directory = stage / 'work' / item['id']
        result = directory / 'result'
        if result.exists() and result.read_text().startswith('CHECKED '):
            eligible.add(item['mode'])
    completed = {item['id'] for item in pilot}
    roster = [row for row in follow + representatives if row['id'] not in completed and row['mode'] in eligible]
    for row in roster:
        row.setdefault('budget', [100_000_000, 48_000_000, 145, 60])
    later = stage / 'successor-queue.json'
    later.write_text(json.dumps(roster, indent=2) + '\n')
    print('modes following calibrated target proof:', sorted(eligible), 'queue:', len(roster), 'stage bytes:', size(stage), flush=True)
    if roster:
        supervise(stage, 16, 5400, 'successor', later)
    if not (stage / 'inventory-16.json').exists():
        h4_checks(stage, source)


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
