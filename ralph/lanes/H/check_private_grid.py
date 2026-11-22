"""Literal private-cell matching controls, with crossed anchor 0."""

from itertools import combinations, product


def matchings(supports):
    choices = [(-1, *(anchor for anchor in row if anchor != 0)) for row in supports]
    for assignment in product(*choices):
        used = [anchor for anchor in assignment if anchor != -1]
        if len(used) == len(set(used)):
            yield len(used)


def margin_and_occupancy(supports):
    singles = [support[0] for support in supports if len(support) == 1]
    return len(singles), len(set(singles) - {0})


def maximum(supports):
    return max(matchings(supports))


def check():
    anchors = range(3)
    types = tuple((anchor,) for anchor in anchors) + tuple(combinations(anchors, 2))
    controls = 0
    for supports in product(types, repeat=3):
        margin, occupancy = margin_and_occupancy(supports)
        capacity = occupancy + 3 - margin
        assert all(size <= capacity for size in matchings(supports))
        controls += 1
    assert controls == 216

    smaller = ((1,), (1, 2), (0,))
    assert (margin_and_occupancy(smaller), maximum(smaller)) == ((2, 1), 2)

    grid = ((1, 1), (1, 1), (1, 2), (2, 0), (3, 0), (4, 0))
    row = tuple((column,) for left, column in grid if left == 1) + ((3, 4),)
    column = tuple((left,) for left, right in grid if right == 0) + ((0, 1),)
    assert (margin_and_occupancy(row), maximum(row)) == ((3, 2), 3)
    assert (margin_and_occupancy(column), maximum(column)) == ((3, 3), 4)
    transposed = tuple((right, left) for left, right in grid)
    assert tuple((right,) for left, right in transposed if left == 0) + ((0, 1),) == column

    broken = ((1,), (1,), (1,), (3, 4))
    assert (margin_and_occupancy(broken), maximum(broken)) == ((3, 1), 2)
    candidates = [(site, anchor) for site, row in enumerate(broken) for anchor in row]
    mutant_witnesses = [edges for edges in combinations(candidates, 3)
                        if len({anchor for _, anchor in edges}) == 3]
    assert len(mutant_witnesses) == 3
    assert all(len({site for site, _ in edges}) == 2 for edges in mutant_witnesses)
    print("PASS: 216 three-site controls; 2/3/4 maxima for small/row/column examples")
    print("PASS: actual mutated row maximum 2, anchor-only mutant produces three false size-3 witnesses")


if __name__ == "__main__":
    check()
