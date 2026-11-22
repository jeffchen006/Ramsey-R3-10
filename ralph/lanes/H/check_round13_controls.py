"""Physical controls for the edge-split, parity and window-balance interfaces."""

from collections import Counter
from itertools import combinations

from check_round12_controls import ROOT, graph6_small, indices


def inside(neighbors, sites):
    return sum(len(neighbors[vertex] & sites) for vertex in sites) // 2


def balance(neighbors, left, right, degree):
    universe = set(range(len(neighbors)))
    window = universe.difference(left, *(neighbors[vertex] for vertex in left))
    private = universe - window - set(left) - set(right)
    return (2 * inside(neighbors, window) + degree * len(private),
            2 * inside(neighbors, private) + degree * len(window), window)


def records(name):
    for record in (ROOT / f'scratch/H/lit/r11-{name}.g6').read_bytes().splitlines():
        yield [set(indices(mask)) for mask in graph6_small(record)]


def main():
    tally = Counter()
    for name, order, classes, regular_count in [('r35_13', 13, 1, 1), ('r37_22', 22, 191, 10)]:
        graphs = list(records(name))
        regular = [neighbors for neighbors in graphs if len({len(row) for row in neighbors}) == 1]
        assert len(graphs) == classes and len(regular) == regular_count
        for neighbors in graphs:
            assert len(neighbors) == order
            universe = set(range(order))
            for root, row in enumerate(neighbors):
                assert all(not row & neighbors[peer] for peer in row)
                remainder = universe - row - {root}
                z_value = sum(len(neighbors[peer]) for peer in row)
                assert inside(neighbors, remainder) + z_value == inside(neighbors, universe)
                for peer in row:
                    rest = {vertex for vertex in row - {peer} if len(neighbors[vertex]) % 2}
                    if rest:
                        assert sum(len(neighbors[vertex]) for vertex in rest) % 2 == len(rest) % 2
                        tally['physical odd arrays'] += 1
                tally['root edge splits'] += 1
        for neighbors in regular:
            universe = set(range(order))
            degree = len(neighbors[0])
            for width in (1, 2, 3):
                for left in combinations(range(order), width):
                    shared = set.intersection(*(neighbors[vertex] for vertex in left))
                    for right in combinations(sorted(shared), width):
                        lhs, rhs, window = balance(neighbors, left, right, degree)
                        assert lhs == rhs
                        tally[order, width] += 1
                        if order == 13 and width == 1:
                            assert len(window) == 8 and inside(neighbors, window) == 10
                            edge = next((vertex, other) for vertex, other in combinations(sorted(window), 2)
                                        if other in neighbors[vertex])
                            mutant = [row.copy() for row in neighbors]
                            vertex, other = edge
                            mutant[vertex].remove(other)
                            mutant[other].remove(vertex)
                            assert len({len(row) for row in mutant}) > 1
                            first, second, same = balance(mutant, left, right, degree)
                            assert same == window and first == second - 2
                            tally['irregular negative'] += 1
    assert tally[13, 1] == tally['irregular negative'] == 52
    assert tally[22, 1] == 1320
    assert tally['root edge splits'] == 13 + 191 * 22
    assert tally['physical odd arrays'] > 0
    print('PASS smaller Ramsey host controls:', dict(tally))
    blown_up_pentagon = [{other for other in range(15) if (other // 3 - vertex // 3) % 5 in (1, 4)}
                         for vertex in range(15)]
    first, second, window = balance(blown_up_pentagon, (0, 1, 2), (3, 4, 5), 6)
    assert first == second == 36 and window == set(range(6, 12))
    print('PASS planted K3,3 in 6-regular blown-up pentagon (two windows both order six)')


if __name__ == '__main__':
    main()
