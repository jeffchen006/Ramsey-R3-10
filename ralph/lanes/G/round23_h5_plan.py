"""Freeze the unique first-wave assignments from the reconciled h5 frontier."""

import json
import sys
from itertools import product, zip_longest
from pathlib import Path


def plan(base):
    baseline = json.loads((base / 'baseline.json').read_text())
    models = {item['board'] for item in map(json.loads, (base / 'baseline.models.jsonl').open())}
    assert len(models) == 45 and 52 in models
    queue_models = [(board, '-', 'BM', f'c{board:03}_bm') for board in sorted(models - {52} | {285})]
    caps = set(baseline['boards_open']) - models - {285}
    assert len(caps) == 16 and 271 in caps
    queue_caps = [(board, prefix, 'S', f'c{board:03}_{prefix}') for board in sorted(caps)
                  for prefix in ('10', '11') if board == 271]
    queue_caps += [(board, ''.join(bit), 'S', f'c{board:03}_{"".join(bit)}')
                   for bit in product('01', repeat=2) for board in sorted(caps - {271})]
    assert len(queue_caps) == 62 and len(queue_models) == 45
    ordered = [entry for pair in zip_longest(queue_caps, queue_models) for entry in pair if entry]
    assert len(set(entry[-1] for entry in ordered)) == len(ordered)
    for idx, (board, prefix, mode, key) in enumerate(ordered):
        print(idx % 22, board, prefix, mode, key)


if __name__ == '__main__':
    plan(Path(sys.argv[1]))
