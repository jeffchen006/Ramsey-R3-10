"""Check complementary unit splits against all labelled hole lists and parent bytes."""

from itertools import combinations, product
from pathlib import Path
import sys

from round22_fold import masks


def hypotheses(side, slot):
    pair_masks = masks(5)
    halves = {-1: set(), 1: set()}
    holes = [frozenset(pair) for pair in combinations(pair_masks, 2) if (pair[0] | pair[1]) & 1]
    original = set(product(holes, repeat=2))
    for board_holes in original:
        halves[-1 if pair_masks[slot] in board_holes[side] else 1].add(board_holes)
    assert len(original) == 900 and not halves[1] & halves[-1] and halves[1] | halves[-1] == original
    return len(halves[-1]), len(halves[1])


def cnf_data(path):
    head, *rows = path.read_bytes().splitlines()
    tokens = head.split()
    assert tokens[:2] == [b'p', b'cnf'] and int(tokens[-1]) == len(rows)
    assert len(set(rows)) == len(rows)
    return int(tokens[2]), set(rows)


def compare(base, board, side, slot, neg, pos):
    population = hypotheses(side, slot)
    unit = side * 12 + slot + 1
    number, original = cnf_data(base / 'work' / f'b{board:02d}' / 'grid.cnf')
    for name, polarity in ((neg, -1), (pos, 1)):
        size, child = cnf_data(base / 'work' / name / 'grid.cnf')
        assert size == number and original < child and child - original == {f'{polarity * unit} 0'.encode()}
    print(f'board {board}: exact {-unit}/{unit} CNF units, {population[0]}+{population[1]} labelled hole lists')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        print(hypotheses(*map(int, sys.argv[1:])))
    else:
        compare(Path(sys.argv[1]), *map(int, sys.argv[2:5]), *sys.argv[5:])
