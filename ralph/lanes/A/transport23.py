"""Version 1 of the h=6 raw-label to representative fixture."""

from collections import Counter
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'scratch/A/r22'


def read_table(path):
    with path.open() as source:
        return list(csv.DictReader(source, delimiter='\t'))


def transport(row):
    left, right = (tuple(map(int, row[key])) for key in ('left_perm', 'right_perm'))
    assert sorted(left) == sorted(right) == list(range(5))
    assert left[0] == right[0] == 0
    assert row['swap'] in ('0', '1')
    return left, right, row['swap'] == '1'


def move_board(label, action):
    left, right, swap = action
    moved = [''] * 25
    for index, entry in enumerate(label):
        src_left, src_right = divmod(index, 5)
        dst_left, dst_right = left[src_left], right[src_right]
        if swap:
            dst_left, dst_right = dst_right, dst_left
        moved[5 * dst_left + dst_right] = entry
    return ''.join(moved)


def move_holes(holes, action):
    left, right, swap = action
    moved = tuple(tuple(sorted(sum(1 << dest for src, dest in enumerate(perm) if mask & (1 << src))
                               for mask in shore)) for shore, perm in zip(holes, (left, right)))
    return moved[::-1] if swap else moved


def inverse(action):
    left, right, swap = action
    first, second = (tuple(perm.index(dest) for dest in range(5)) for perm in (left, right))
    return (second, first, swap) if swap else (first, second, swap)


def main():
    boards = read_table(SOURCE / 'h6.boards.tsv')
    holes = read_table(SOURCE / 'h6.holes.tsv')
    known = {(row['board'], tuple((int(row[f'{shore}_hole_0']), int(row[f'{shore}_hole_1']))
                                  for shore in ('left', 'right'))) for row in holes}
    assert len(known) == len(holes) == 19651
    assert Counter(key[0] for key in known) == {row['board']: int(row['hole_contexts']) for row in boards}
    assert sum(int(row['global_labelled']) for row in holes) == 22408 * 900
    examples, seen, masses = {}, set(), Counter()
    reverse_fails = 0
    for row in read_table(SOURCE / 'h6.labels.tsv'):
        raw, rep = row['label'], row['representative']
        action = transport(row)
        assert raw not in seen
        seen.add(raw)
        masses[rep] += 1
        assert move_board(raw, action) == rep
        assert move_board(rep, inverse(action)) == raw
        backwards = move_board(rep, action)
        if backwards != raw:
            reverse_fails += 1
            if action[-1] not in examples:
                rep_holes = min(pair for board, pair in known if rep == board and pair[0] != pair[1])
                raw_holes = move_holes(rep_holes, inverse(action))
                assert move_holes(raw_holes, action) == rep_holes
                examples[action[-1]] = dict(row, wrongly_forward_from_rep=backwards,
                                            raw_holes=raw_holes, representative_holes=rep_holes)
    assert masses == {row['board']: int(row['labelled']) for row in boards}
    assert set(examples) == {False, True} and reverse_fails == 19908
    print(json.dumps(dict(schema='h6.label-to-representative.v1', source='scratch/A/r22/h6.labels.tsv',
                          raw_labels=len(seen), representatives=len(masses), hole_keys=len(known),
                          reversed_action_failures=reverse_fails, rejection_cases=list(examples.values())),
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
