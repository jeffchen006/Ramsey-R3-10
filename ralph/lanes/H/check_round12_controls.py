"""Check the witness and triple-window interfaces on physical smaller graphs."""

from collections import Counter
from itertools import combinations

from check_round11_controls import ROOT, graph6_small, indices


def graph(order, edges):
    neighbors = [set() for _ in range(order)]
    for left, right in edges:
        assert left != right
        neighbors[left].add(right)
        neighbors[right].add(left)
    return neighbors


def witness_controls(neighbors, counts):
    pairs = list(combinations(range(len(neighbors)), 2))
    marked = [(frozenset((left, right)), next(iter(common))) for left, right in pairs
              if right not in neighbors[left] and len(common := neighbors[left] & neighbors[right]) == 1]
    witnesses = {witness for _, witness in marked}
    distinct_disjoint = [(first, left, second, right)
                         for (first, left), (second, right) in combinations(marked, 2)
                         if not first & second and left != right]
    counts['different_colour_marks'] += len(distinct_disjoint)
    counts['internal_witness_marks'] += sum(bool(({left} | first) & ({right} | second))
                                            for first, left, second, right in distinct_disjoint)
    for (first, left), (second, right) in combinations(marked, 2):
        if first & second:
            continue
        if len(witnesses) > 1:
            assert distinct_disjoint
        if left != right:
            continue
        for other, witness in marked:
            if witness == left:
                continue
            assert not first & other or not second & other
            counts['bridge_marks'] += 1


def triple_controls(neighbors, counts):
    order = len(neighbors)
    universe = set(range(order))
    for roots in combinations(universe, 3):
        if any(second in neighbors[first] for first, second in combinations(roots, 2)):
            continue
        first, second, third = (neighbors[root] for root in roots)
        window = universe.difference(roots, first, second, third)
        common = first & second & third
        pair_counts = [len(first & second), len(first & third), len(second & third)]
        assert len(window) + 3 + len(first) + len(second) + len(third) + len(common) == order + sum(pair_counts)
        counts['independent_triple_marks'] += 1
        counts['opposite_triples_available'] += len(common) >= 3


def planted_controls():
    paths = graph(5, [(vertex, (vertex + 1) % 5) for vertex in range(5)])
    counts = Counter()
    witness_controls(paths, counts)
    assert counts['different_colour_marks'] == counts['internal_witness_marks'] == 5
    leaves = [(vertex, 4) for vertex in range(4)]
    wedge = graph(7, leaves + [(0, 6), (5, 6)])
    counts = Counter()
    witness_controls(wedge, counts)
    assert counts['bridge_marks'] > 0
    assert wedge[0] & wedge[1] == wedge[0] & wedge[2] == {4} and wedge[0] & wedge[5] == {6}
    mutant = graph(7, leaves + [(0, 6), (2, 6), (5, 6)])
    assert mutant[0] & mutant[2] == {4, 6}
    print(f'planted P3/C5 controls: bridge={counts["bridge_marks"]}; removing uniqueness or disjointness changes applicability')

    for triple, pair_counts, expected in [(3, (5, 5, 5), 22), (5, (5, 5, 5), 20),
                                           (4, (5, 5, 5), 21), (3, (4, 5, 5), 21)]:
        masks = [(0, 1, 2)] * triple
        for pair, count in zip(combinations(range(3), 2), pair_counts, strict=True):
            masks += [pair] * (count - triple)
        for root in range(3):
            masks += [(root,)] * (9 - sum(root in mask for mask in masks))
        neighbors = graph(40, [(root, vertex) for vertex, mask in enumerate(masks, 3) for root in mask])
        first, second, third = neighbors[:3]
        assert list(map(len, (first, second, third))) == [9, 9, 9]
        assert len(first & second & third) == triple
        assert tuple(map(len, (first & second, first & third, second & third))) == pair_counts
        assert 37 - len(first | second | third) == expected
        triple_controls(neighbors, Counter())
    print('four planted local cap-five controls: window orders 22,20,21,21; both 21 patterns need external exclusion')


def main():
    planted_controls()
    for name, order, size in [('r35_13', 13, 1), ('r36_17', 17, 7), ('r37_22', 22, 191)]:
        records = (ROOT / f'scratch/H/lit/r11-{name}.g6').read_bytes().splitlines()
        assert len(set(records)) == size
        counts = Counter()
        for record in records:
            neighbors = [set(indices(mask)) for mask in graph6_small(record)]
            assert len(neighbors) == order
            assert all(not (neighbors[vertex] & neighbors[other])
                       for vertex in range(order) for other in neighbors[vertex])
            witness_controls(neighbors, counts)
            triple_controls(neighbors, counts)
        assert counts['independent_triple_marks'] and counts['different_colour_marks']
        print(f'{name}: hosts={size} {dict(counts)}')


if __name__ == '__main__':
    main()
