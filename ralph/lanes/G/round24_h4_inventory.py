"""Inventory h4 boards, with h5 as a fixed regression of the quotient."""

import argparse
import json
import sys
from functools import cache
from pathlib import Path

from round22_control import ROOT, unflatten

sys.path.insert(0, str(ROOT / 'ralph/lanes/A'))
from h6_boards22 import ACTIONS, board_set, decorate, transform


@cache
def decoration(stabilizer):
    return tuple(decorate(stabilizer))


def inventory(total):
    remaining = board_set(total)
    labelled = len(remaining)
    records = []
    for board in sorted(remaining):
        if board not in remaining:
            continue
        transport = {transform(board, action) for action in ACTIONS}
        assert transport <= remaining
        remaining -= transport
        stabilizer = tuple(action for action in ACTIONS if transform(board, action) == board)
        assert len(stabilizer) * len(transport) == 1152
        contexts = decoration(stabilizer)
        assert sum(size for _, _, size in contexts) == 900
        records.append(dict(id=len(records), name=board, grid=unflatten(board, 5),
                            orbit_size=len(transport), keys=[[left, right] for left, right, _ in contexts]))
    assert sum(row['orbit_size'] for row in records) == labelled
    keys = sum(len(row['keys']) for row in records)
    if total == 17:
        assert (labelled, len(records), keys) == (184488, 286, 156112)
    if total == 16:
        assert (labelled, len(records), keys) == (864087, 1099, 712734)
    return records, dict(grid=total, boards=len(records), labelled=labelled, keys=keys)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('total', type=int, choices=(16, 17))
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data, summary = inventory(args.total)
    args.output.write_text(json.dumps(data, separators=(',', ':')) + '\n')
    print(json.dumps(summary))
