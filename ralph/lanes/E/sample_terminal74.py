#!/usr/bin/env python3
"""Select deterministic spaced IDs from the exact ordered open receipt queue."""

import argparse
from pathlib import Path
import json


def sample(trace, queue, spaced, target):
    assert target >= 2
    with trace.open(encoding='ascii') as stream:
        keys = [tuple(row[:2]) for row in map(json.loads, stream) if row[2] == 'open']
    assert keys == sorted(set(keys)) and all(index >= 0 and lift >= 0 for index, lift in keys)
    count = min(target, len(keys))
    selected = sorted({offset * (len(keys)-1) // max(1, count-1) for offset in range(count)})
    assert len(selected) == count
    if count >= 2:
        assert selected[0] == 0 and selected[-1] == len(keys)-1
    with queue.open('x', encoding='ascii') as all_ids, spaced.open('x', encoding='ascii') as chosen:
        for index, lift in keys:
            print(json.dumps((index, lift, 'open'), separators=(',', ':')), file=all_ids)
        for offset in selected:
            print(json.dumps((*keys[offset], 'open'), separators=(',', ':')), file=chosen)
    print('exact ordered queue', len(keys), 'projections', len({index for index, _ in keys}),
          'dispersed sample', len(selected), 'ordinals', selected, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('trace', 'queue', 'spaced'):
        parser.add_argument(name, type=Path)
    parser.add_argument('target', type=int)
    args = parser.parse_args()
    sample(args.trace, args.queue, args.spaced, args.target)
