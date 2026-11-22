"""Literal finite geometry controls for the q5/q6 arguments."""

from itertools import combinations, product


def frame(mask):
    return {frozenset((row, col + 3)) for row, col in product(range(3), repeat=2)
            if mask & (1 << (3 * row + col))}


def neighbors(edges, vertex):
    return {other for pair in edges if vertex in pair for other in pair if other != vertex}


def sides(edges):
    return tuple([{other for other in neighbors(edges, vertex)} for vertex in shore]
                 for shore in (range(3), range(3, 6)))


def missing_double_pairs(edges):
    return tuple(tuple(pair for pair in combinations(neighborhoods, 2)
                       if not pair[0] & pair[1] and len(pair[0] | pair[1]) < 3)
                 for neighborhoods in sides(edges))


def main():
    cross = {frozenset(edge) for edge in ((0, 3), (1, 3), (1, 4), (2, 4), (2, 5))}
    assert missing_double_pairs(cross) == ((), ())
    nonedges = [(row, col) for row, col in product(range(3), range(3, 6))
                if frozenset((row, col)) not in cross]
    valid = []
    for values in product(range(4), repeat=len(nonedges)):
        quotas = [0] * 6
        for (row, col), value in zip(nonedges, values):
            quotas[row] += value
            quotas[col] += value
        if quotas == [3, 3, 2, 2, 3, 3]:
            valid.append(dict(zip(nonedges, values)))
    assert valid == [{(0, 4): 3, (0, 5): 0, (1, 5): 3, (2, 3): 2}]
    assert [list(map(len, missing_double_pairs(frame(code)))) for code in (78, 85)] == [[0, 0], [1, 1]]

    cube = {frozenset((left, right + 4)) for left, right in product(range(4), repeat=2) if left != right}
    assert len(cube) == 12
    opposite = {frozenset((index, index + 4)) for index in range(4)}
    for pair in opposite:
        first, second = sorted(pair)
        left, right = neighbors(cube, first), neighbors(cube, second)
        assert left | right == set(range(8)) - pair and not left & right
        cross_edges = {frozenset((row, col)) for row, col in product(left, right)}
        assert len(cube & cross_edges) == 6
        assert cross_edges - cube == opposite - {pair}
    print('q5: unique quota table; q4: 0/0 versus 1/1 extra double masks; q6: four literal re-roots')


if __name__ == '__main__':
    main()
