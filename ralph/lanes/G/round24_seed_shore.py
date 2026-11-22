"""Lift physical witnesses harvested from completed relaxations to two shores."""

import json
import sys
from collections import Counter
from pathlib import Path

from round23_h5 import Physical
from round24_shore import projected

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'ralph/lanes/A'))
from physical_blocker23 import Layout
from shore_blocker24 import projected as independent


def update(stage, boards):
    counts = Counter()
    for path in sorted((stage / 'seeds').glob('*.jsonl')):
        identity = int(path.stem)
        physical = Physical(boards[identity]['grid'])
        layout = Layout(boards[identity]['grid'])
        destination = stage / 'shore-seeds' / path.name
        result = {line for line in destination.read_text().splitlines()} if destination.exists() else set()
        before = len(result)
        for line in path.read_text().splitlines():
            record = json.loads(line)
            physical.row(record, 10)
            for candidate in projected(physical, record):
                assert independent(layout, candidate['side'], tuple(candidate['boundary']), tuple(candidate['coords']), 10) is not None
                result.add(json.dumps(candidate, sort_keys=True))
        if len(result) > before:
            temporary = destination.with_suffix('.tmp')
            temporary.write_text('\n'.join(sorted(result)) + '\n')
            temporary.replace(destination)
            counts[identity] += len(result) - before
    return counts


if __name__ == '__main__':
    stage = Path(sys.argv[1])
    manifest = json.loads((stage / '../round22/h5/manifest.json').read_text())
    print(json.dumps(update(stage, manifest), sort_keys=True))
