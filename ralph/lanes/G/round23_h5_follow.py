"""Turn completed wave-one failures into disjoint deficit slices."""

import argparse
import json
from pathlib import Path

from round23_h5_status import covered


def plan(base, snapshot, count):
    current = json.loads(snapshot.read_text())
    prepared = {}
    for manifest in base.glob('queue*.tsv'):
        for line in manifest.read_text().splitlines():
            _, board, prefix, _, name = line.split()
            prepared[int(board), '' if prefix == '-' else prefix, name] = None
    for manifest in base.glob('*.pids'):
        for line in manifest.read_text().splitlines():
            fields = line.split()
            if len(fields) != 6:
                continue
            _, board, prefix, _, name, _ = fields
            prepared[int(board), '' if prefix == '-' else prefix, name] = None
    open_boards = set(current['boards_open'])
    terminal = current['terminal']
    proofs = {int(board): prefixes for board, prefixes in current['proofs'].items()}
    jobs = []
    for name, previous in sorted(terminal.items()):
        ident, prefix, tactic = previous['board'], previous['prefix'], previous['mode']
        if ident not in open_boards or not name.startswith('c') or not previous['result'].startswith('OPEN '):
            continue
        if previous['result'].startswith('OPEN archive'):
            continue
        for digit in '01':
            branch = prefix + digit
            closed = proofs.get(ident, {})
            if any(branch.startswith(proof) for proof in closed) or covered(closed, branch):
                continue
            if any(other == ident and (branch.startswith(other_prefix) or other_prefix.startswith(branch)) and
                   job != name and job not in terminal for other, other_prefix, job in prepared):
                continue
            job = f'd{ident:03}_{branch}'
            if (ident, branch, job) in prepared or (base / 'work' / job).exists():
                continue
            strategy = 'DM' if tactic == 'BM' else 'D'
            jobs.append((ident, branch, strategy, job))
    assert len(jobs) == len({item[-1] for item in jobs})
    for index, (ident, prefix, strategy, name) in enumerate(jobs):
        print(index % count, ident, prefix, strategy, name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=Path)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('slots', type=int)
    options = parser.parse_args()
    assert 0 < options.slots <= 22
    plan(options.base, options.snapshot, options.slots)
