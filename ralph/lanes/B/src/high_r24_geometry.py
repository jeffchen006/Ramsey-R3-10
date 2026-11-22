"""Literal enumeration of marked Y degree profiles for the two high partners."""

from collections import Counter, defaultdict
from itertools import combinations, product


def top_d8_board():
    eligible = set()
    columns = ((0,), (1,), (2,), (0, 1), (0, 2), (1, 2))
    for board in product(columns, repeat=5):
        if sum(map(len, board)) != 8 or len({column for column in board if len(column) == 2}) != 3:
            continue
        for high in range(5):
            low_counts = [sum(row in column for index, column in enumerate(board) if index != high)
                          for row in range(3)]
            if any(count > 2 for count in low_counts):
                continue
            assert low_counts == [2, 2, 2]
            assert len(board[high]) == 2
            assert sorted(column[0] for column in board if len(column) == 1) == list(board[high])
            eligible.add((board, high))
    assert len(eligible) == 360
    for board, high in eligible:
        for high_private in (None, 0, 1, 2):
            bad_low = [row for row in range(3) if row != high_private and row in board[high]
                       and sum(row in column for column in board) == 3]
            assert bad_low
    print(f'd8 e46: {len(eligible)} labelled boards satisfy the low-common cap; all hit a low 667 re-root')


def main():
    sites = tuple(range(4))
    pairs = tuple(combinations(sites, 2))
    expected = {7: {(2, 2, 2, 2): {(6, 6, 7, 7)},
                    (1, 2, 2, 3): {(6, 6, 7, 7), (6, 6, 6, 8)}},
                8: {(0, 2, 2, 2): set(),
                    (1, 1, 1, 3): {(6, 6, 6, 7)},
                    (1, 1, 2, 2): {(6, 6, 6, 7)}}}
    for partner in (7, 8):
        counts = defaultdict(Counter)
        for edges in combinations(pairs, 11 - partner):
            double_degrees = [sum(site in edge for edge in edges) for site in sites]
            shape = tuple(sorted(double_degrees))
            tally = counts[shape]
            for shared in sites:
                for other in combinations([site for site in sites if site != shared], partner - 6):
                    full_degrees = tuple(sorted(4 + degree + int(site == shared or site in other)
                                                for site, degree in enumerate(double_degrees)))
                    if all(6 <= degree <= 8 for degree in full_degrees):
                        tally[full_degrees] += 1
        assert {shape: set(tally) for shape, tally in counts.items()} == expected[partner]
        for shape, tally in sorted(counts.items()):
            print(partner, shape, dict(sorted(tally.items())))
    top_d8_board()


if __name__ == '__main__':
    main()
