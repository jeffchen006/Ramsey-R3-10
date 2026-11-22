"""Derive the next weak-board manifest from A's independent coordinate cover."""

import json
from pathlib import Path
import sys

from round22_control import ROOT, unflatten
from round22_fold import deficit

sys.path.insert(0, str(ROOT / 'ralph/lanes/A'))
from h6_boards22 import ACTIONS, board_set, decorate, transform


def inventory(output):
    remaining = board_set(17)
    assert len(remaining) == 184488
    records = []
    while remaining:
        base = min(remaining)
        images = {transform(base, action) for action in ACTIONS}
        assert images <= remaining
        remaining -= images
        stabilizer = [action for action in ACTIONS if transform(base, action) == base]
        assert len(stabilizer) * len(images) == 1152
        keys = decorate(stabilizer)
        board = unflatten(base, 5)
        deficits = [deficit(board, side) for side in range(2)]
        assert all(sum(shore) == 3 for shore in deficits)
        records.append(dict(id=len(records), name=base, grid=board, orbit_size=len(images),
                            deficits=deficits, keys=[[left, right] for left, right, _ in keys]))
    assert len(records) == 286 and sum(len(record['keys']) for record in records) == 156112
    output.write_text(json.dumps(records, separators=(',', ':')) + '\n')
    print('matched prior Burnside counts:', len(records), 184488, 156112)


if __name__ == '__main__':
    inventory(Path(sys.argv[1]))
