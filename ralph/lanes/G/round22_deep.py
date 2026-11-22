"""Complete the observed depth gaps without changing the base edge encoding."""

from collections import Counter
from functools import reduce
from itertools import combinations
from operator import or_
from pathlib import Path
import argparse
import hashlib
import json
import sys

from round22_control import decode, unflatten
from round22_fold import padding
from round22_three import ThreeDefect


def completion_rows(fold, plan):
    grid = len(fold.grid)
    pad = padding(fold.width)
    for option_count, size in plan:
        remainder = fold.bound - size
        assert remainder >= 0
        for indices in combinations(range(grid), size - option_count):
            support = reduce(or_, (fold.grid[index] for index in indices), 0)
            if pad[support] < remainder:
                continue
            positives = tuple(edge for first, second in combinations(indices, 2)
                              if (edge := fold.edge(0, first, second)))
            if option_count == 0:
                yield positives
            else:
                assert option_count == 1
                for (left, right), selector in fold.gates.items():
                    option = fold.slots[0][left] | fold.slots[1][right] << fold.width
                    if pad[support | option] >= remainder:
                        attached = tuple(edge for index in indices if (edge := fold.edge(0, index, grid + left)))
                        yield (-selector, *positives, *attached)


def projected_activity(fold, placement):
    size = len(fold.grid)
    coordinates = []
    for side, name in enumerate(('left', 'right')):
        wanted = list(placement[name])
        active = []
        for slot, support in enumerate(fold.slots[side]):
            if support in wanted:
                wanted.remove(support)
                active.append(slot)
        assert not wanted
        coordinates.append(active)
    positive = {fold.gates[coordinates[0][index], coordinates[1][mate]]
                for index, mate in enumerate(placement['mates'])}
    coords = list(range(size)) + [size + slot for slot in coordinates[0]]
    for first, second in decode(placement['graph']):
        if first >= 8:
            edge = fold.edge(0, coords[first - 8], coords[second - 8])
            assert edge
            positive.add(edge)
    return positive


def small(base):
    prepared = {}
    count = Counter()
    hits = 0
    for line in (base / 'n17.d3.placements.jsonl').open():
        placement = json.loads(line)
        name = placement['board']
        if name not in prepared:
            fold = ThreeDefect(unflatten(name, 3), 3, False, bound=7)
            strict = ThreeDefect(unflatten(name, 3), 3, False, bound=6)
            prepared[name] = fold, tuple(completion_rows(fold, ((0, 3), (1, 4)))), tuple(
                completion_rows(strict, ((0, 3), (1, 4))))
        fold, rows, strict_rows = prepared[name]
        positive = projected_activity(fold, placement)
        assert all(any((lit in positive if lit > 0 else -lit not in positive) for lit in row)
                   for row in rows)
        actual = decode(placement['graph'])
        for row in strict_rows:
            if not any((lit in positive if lit > 0 else -lit not in positive) for lit in row):
                assert any(not any(pair in actual for pair in combinations(chosen, 2))
                           for chosen in combinations(range(17), 6))
                hits += 1
        count[name] += 1
    assert len(count) == 16 and sum(count.values()) == 1960
    assert hits > 0
    print('deeper physical clauses preserve all', sum(count.values()), 'smaller placements in', len(count),
          'boards; stricter rows reject with independently found I6 in', hits, 'placement/row incidences')


def emit(manifest, board, other):
    record = json.loads(manifest.read_text())[board]
    assert record['id'] == board
    fold = ThreeDefect(record['grid'], 8, True)
    if other:
        signed = [int(word) for line in other.read_text().splitlines() if line.startswith('v ')
                  for word in line.split()[1:] if word != '0']
        assert len(signed) == fold.variables
        assignment = set(signed)
    missed = 0
    for row in completion_rows(fold, ((0, 7), (0, 8), (1, 7))):
        fold.add(row, 'depth-extension')
        if other:
            missed += not any(literal in assignment for literal in row)
    if other:
        assert missed > 0
    fold.dump(sys.stdout)
    print(json.dumps(dict(board=board, grid=record['grid'], split=None, strength='full+depth', counts=fold.counts,
                          variables=fold.variables, clauses=len(fold.rows), prior_model_cuts=missed,
                          manifest=hashlib.sha256(manifest.read_bytes()).hexdigest())), file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    controls = sub.add_parser('small')
    controls.add_argument('base', type=Path)
    target = sub.add_parser('emit')
    target.add_argument('manifest', type=Path)
    target.add_argument('board', type=int)
    target.add_argument('--strength', choices=('full+depth',))
    target.add_argument('--old-model', type=Path)
    args = parser.parse_args()
    if args.action == 'small':
        small(args.base)
    else:
        emit(args.manifest, args.board, args.old_model)
