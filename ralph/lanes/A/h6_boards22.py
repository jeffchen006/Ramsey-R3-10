#!/usr/bin/env python3
"""Enumerate weak boards, crossing-preserving orbits and hole decorations."""
import argparse
from collections import Counter
import itertools as it
import json
from pathlib import Path

WIDTH = 5
PRIVATE = 4
COORDS = tuple(range(WIDTH))
PERMS = tuple((0, *tail) for tail in it.permutations(COORDS[1:]))
ACTIONS = [(swap, left, right) for left, right in it.product(PERMS, repeat=2) for swap in (False, True)]
PAIRS = tuple(map(sum, it.combinations((1 << coordinate for coordinate in COORDS), 2)))
HOLES = tuple(sorted(tuple(sorted(pair)) for pair in it.combinations(PAIRS, 2) if (pair[0] | pair[1]) & 1))


def row_allowance(entries, crossed):
    return sum(entries) <= PRIVATE and sum(value > 0 for value in entries[1:]) + PRIVATE - sum(entries) >= 3 + crossed


def board_set(total):
    rules = [[], []]
    for entries in it.product(range(3), repeat=WIDTH):
        for crossed in (False, True):
            if (not crossed or entries[0] == 0) and row_allowance(entries, crossed):
                rules[crossed].append((sum(entries), entries))

    def search(rows, remaining, columns):
        if len(rows) == WIDTH:
            if remaining == 0:
                yield ''.join(str(value) for row in rows for value in row)
            return
        for size, row in rules[not rows]:
            if not 0 <= remaining - size <= PRIVATE * (WIDTH - 1 - len(rows)):
                continue
            updated = tuple(column + (value,) for column, value in zip(columns, row, strict=True))
            if all(row_allowance(col, index == 0) for index, col in enumerate(updated)):
                yield from search(rows + (row,), remaining - size, updated)

    return set(search((), total, ((),) * WIDTH))


def transform(board, action):
    swapped, left, right = action
    moved = [''] * (WIDTH * WIDTH)
    for row, col in it.product(COORDS, repeat=2):
        first, second = (right[col], left[row]) if swapped else (left[row], right[col])
        moved[WIDTH * first + second] = board[WIDTH * row + col]
    return ''.join(moved)


def transpose(board):
    return ''.join(board[WIDTH * col + row] for row, col in it.product(COORDS, repeat=2))


def inverse(action):
    swap, left, right = action
    left_inverse, right_inverse = tuple(left.index(index) for index in COORDS), tuple(right.index(index) for index in COORDS)
    return (swap, right_inverse, left_inverse) if swap else (swap, left_inverse, right_inverse)


def decorate(stabilizer):
    def map_mask(mask, permutation):
        return sum(1 << new for old, new in enumerate(permutation) if mask >> old & 1)

    lookup = {permutation: {holes: tuple(sorted(map_mask(mask, permutation) for mask in holes)) for holes in HOLES}
              for permutation in PERMS}

    def act(decoration, action):
        swap, left, right = action
        mapped = lookup[left][decoration[0]], lookup[right][decoration[1]]
        return mapped[::-1] if swap else mapped

    unseen = set(it.product(HOLES, repeat=2))
    complete = []
    while unseen:
        seed = min(unseen)
        orbit = {act(seed, action) for action in stabilizer}
        assert seed in orbit and orbit <= unseen and len(stabilizer) % len(orbit) == 0
        unseen.difference_update(orbit)
        complete.append((*seed, len(orbit)))
    return complete


def deficits(board):
    return [PRIVATE - sum(map(int, board[WIDTH * row:WIDTH * (row + 1)])) for row in COORDS]


def census(total, out=None):
    raw = board_set(total)
    unvisited = set(raw)
    by_type = Counter()
    board_rows = []
    crosswalk = []
    contexts = []
    complete_contexts = 0
    type_labels = Counter()
    type_contexts = Counter()
    while unvisited:
        seed = min(unvisited)
        images = {}
        for action in ACTIONS:
            images.setdefault(transform(seed, action), action)
        assert images.keys() <= unvisited
        unvisited.difference_update(images)
        pure = {transform(seed, action) for action in ACTIONS if not action[0]}
        stabilizer = [action for action in ACTIONS if transform(seed, action) == seed]
        swap_stab = [action for action in stabilizer if action[0]]
        assert len(images) * len(stabilizer) == len(ACTIONS)
        assert len(images) == len(pure) * (1 if swap_stab else 2)
        assert bool(swap_stab) == (transpose(seed) in pure)
        decorated = decorate(stabilizer)
        complete_contexts += len(decorated)
        assert sum(amount for _, _, amount in decorated) == len(HOLES) ** 2
        left, right = deficits(seed), deficits(transpose(seed))
        tag = ''.join(sorted('R' if 2 in shore else 'S' for shore in (left, right)))
        by_type[tag] += 1
        type_labels[tag] += len(images)
        type_contexts[tag] += len(decorated)
        board_rows.append((seed, ''.join(map(str, left)), ''.join(map(str, right)), tag, len(images), len(pure),
                           len(stabilizer) - len(swap_stab), len(swap_stab), int(transpose(seed) == seed), len(decorated)))
        for image, action in sorted(images.items()):
            swap, left_move, right_move = inverse(action)
            assert transform(image, (swap, left_move, right_move)) == seed
            crosswalk.append((image, seed, int(swap), ''.join(map(str, left_move)), ''.join(map(str, right_move))))
        contexts.extend((seed, *lhs, *rhs, multiplicity, multiplicity * len(images))
                        for lhs, rhs, multiplicity in decorated)
    assert len(crosswalk) == len(raw) and sum(row[-1] for row in contexts) == len(raw) * len(HOLES) ** 2
    if out:
        assert all(sum(deficits(row[0])) == sum(deficits(transpose(row[0]))) == 2 for row in board_rows)
        tables = (
            ('h6.boards.tsv', 'board\tleft_deficit\tright_deficit\ttype\tlabelled\toriented_labelled\tstabilizer_plain\tstabilizer_swap\tbare_transpose\thole_contexts', board_rows),
            ('h6.labels.tsv', 'label\trepresentative\tswap\tleft_perm\tright_perm', sorted(crosswalk)),
            ('h6.holes.tsv', 'board\tleft_hole_0\tleft_hole_1\tright_hole_0\tright_hole_1\tfixed_board_labelled\tglobal_labelled', contexts),
        )
        for name, header, rows in tables:
            with (out / name).open('w') as stream:
                print(header, file=stream)
                for row in rows:
                    print(*row, sep='\t', file=stream)
    print('grid_sites', total, 'labelled', len(raw), 'orbits', len(board_rows), 'decorated_orbits', complete_contexts,
          'oriented_orbits', sum(1 + (row[7] == 0) for row in board_rows), 'swap_stabilized', sum(row[7] > 0 for row in board_rows),
          'bare_transpose', sum(row[8] for row in board_rows), flush=True)
    print('type board/label/context multiplicities', json.dumps({tag: [by_type[tag], type_labels[tag], type_contexts[tag]]
                                                               for tag in sorted(by_type)}, sort_keys=True), flush=True)
    return len(raw), len(board_rows), complete_contexts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert census(20) == (24, 1, 30)
    assert census(19) == (1296, 6, 1213)
    assert census(18, args.out) == (22408, 49, 19651)


if __name__ == '__main__':
    main()
