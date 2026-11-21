"""Small positive-root and exact maximal-domain controls for the row clique."""

import argparse
from itertools import combinations
from pathlib import Path

from maxrow_clique import bits, check, compatible, parse_graph6
from check_graph import to_graph6


def residue(rows, root):
    selected = tuple(index for index in range(len(rows)) if not (rows[root] | (1 << root)) >> index & 1)
    return [sum(((rows[index] >> other) & 1) << label for label, other in enumerate(selected)) for index in selected]


def direct(rows, minimum, maximum):
    full = (1 << len(rows)) - 1
    for size in range(minimum, maximum + 1):
        for row in combinations(range(len(rows)), size):
            picked = sum(1 << index for index in row)
            dominated = 0
            for index in row:
                dominated |= rows[index]
            if not (dominated & picked) and dominated | picked == full:
                yield picked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('control', type=Path)
    parser.add_argument('residues', type=Path)
    args = parser.parse_args()
    rooted = []
    for text in args.control.read_text().splitlines():
        rows = parse_graph6(text)
        if all(neighbors.bit_count() == 6 for neighbors in rows):
            rooted.extend(residue(rows, root) for root in range(len(rows)))
    assert len(rooted) == 220
    for rows in rooted[::22]:
        for low, high in ((1, 5), (5, 5), (3, 4)):
            actual = list(compatible(rows, low, high))
            assert sorted(actual) == sorted(direct(rows, low, high))
    rows = rooted[0]
    first = next(compatible(rows, 5, 5))
    seed = tuple(1 << index for index in bits(first))[:2]
    try:
        check(rows, seed, 1, 5, 5)
    except ValueError as error:
        assert str(error) == 'a maximal attachment row meets two demands'
    else:
        raise AssertionError('forged clique passed')
    args.residues.write_text(''.join(to_graph6(rows) + '\n' for rows in rooted))
    print('exact maximal domains on 30 small cases; forged clique rejected; 220 actual residues exported')


if __name__ == '__main__':
    main()
