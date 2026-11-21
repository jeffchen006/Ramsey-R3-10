#!/usr/bin/env python3
"""Verify the finite signature and unit-weight arithmetic of the two hand cuts."""

from math import comb

from scan import verify
from scan_private_equality import signatures
from typed_lp import Model


def main():
    dictionary = {
        'A': (1, 1, 1, 3), 'B': (1, 0, 3, 2), 'C': (0, 3, 0, 3),
        'D': (0, 2, 2, 2), 'E': (0, 1, 4, 1), 'F': (0, 0, 6, 0),
    }
    assert set(dictionary.values()) == {tuple(row.count(degree) for degree in range(6, 10)) for row in signatures()[0]}
    for counts, expected, rhs in [((5, 0, 9, 26), ('B', 'F'), -1), ((6, 2, 2, 30), ('A', 'D'), -2)]:
        assert sum(counts) == 40 and sum(degree * count for degree, count in enumerate(counts, 6)) == 336
        allowed = tuple(name for name, spec in dictionary.items()
                        if spec[0] < counts[0] and all(r <= n for r, n in zip(spec[1:], counts[1:])))
        assert allowed == expected
        model = Model()
        for name in allowed:
            model.col(name, counts[0])
        if allowed == ('B', 'F'):
            assert counts[0] % 2 == 1 and dictionary['B'][0] == 1 and dictionary['F'][0] == 0
            size = dictionary['F'][2]
            assert 2 * size - counts[2] > 1 and dictionary['B'][2] - 1 == 2
            model.le({'B': 1}, comb(counts[2] - size, 2), 'outside-pair packing')
            model.le({'F': 1}, 1, 'six-set overlap')
        else:
            assert dictionary['D'][1:3] == counts[1:3] and counts[0] >= 2
            assert dictionary['A'][1:3] == (1, 1)
            model.le({'A': 1}, counts[1] * counts[2], 'mixed-type pair packing')
            model.le({'D': 1}, 0, 'overlap with any other root')
        model.le({name: -1 for name in allowed}, -counts[0], 'root mass')
        assert sum(row[1] for row in model.rows) == rhs and verify(model, {0: 1, 1: 1, 2: 1})
        print(f'{counts}: exact unit certificate 0 <= {rhs}')


if __name__ == '__main__':
    main()
