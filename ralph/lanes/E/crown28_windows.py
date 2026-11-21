#!/usr/bin/env python3
"""Check the largest fixed-set windows of a six-pair crown."""
import argparse
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from crown30_windows import (alpha, brute_alpha, check_equal_triples, independent_multiplicity,
                             optimistic_groups, parse_graph6, triangle_free)


def first_packing(graph, choices, count, base_alpha):
    degree = tuple(row.bit_count() for row in graph)
    local_loads = [[sum(word >> vertex & 1 for word in group) for vertex in range(len(graph))]
                   for group in choices]
    nodes = 0

    @lru_cache(maxsize=200000)
    def compatible(indices):
        return alpha(optimistic_groups(graph, *(choices[index] for index in indices))) <= base_alpha + len(indices)

    def search(picked, start, load):
        nonlocal nodes
        nodes += 1
        if len(picked) == count:
            return picked
        for index in range(start, len(choices)):
            added = tuple(left + right for left, right in zip(load, local_loads[index]))
            if any(value > 9 for value in added):
                continue
            if any(not compatible(subset + (index,)) for size in range(1, len(picked) + 1)
                   for subset in combinations(picked, size)):
                continue
            hit = search(picked + (index,), index, added)
            if hit is not None:
                return hit
        return None

    found = search((), 0, degree)
    compatible.cache_clear()
    return found, nodes


def control():
    core = [0]
    choices = independent_multiplicity(core, 1, 2)
    assert (1,) in choices
    planted = optimistic_groups(core, (1,), (1,), (1,))
    assert planted == [14, 1, 1, 1] and triangle_free(planted) and brute_alpha(planted) == alpha(planted) == 3
    good = check_equal_triples(core, choices, 3, 4)
    assert good[0] and (choices.index((1,)),) * 3 in good[1]
    assert first_packing(core, [(1,)], 3, 1)[0] == (0, 0, 0)
    assert first_packing(core, [(1, 1)], 2, 1)[0] is None
    first, second = (3,), (3,)
    graph = optimistic_groups([0, 0, 0], first, second)
    assert triangle_free(graph) and brute_alpha(graph) == alpha(graph) == 3
    print('Control: Petersen fixed star retained; repeated profiles checked exactly.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('orders', type=int, nargs='+', choices=(4, 5, 6, 7, 8))
    args = parser.parse_args()
    control()
    expected = {4: 6, 5: 9, 6: 15, 7: 9, 8: 3}
    for order in args.orders:
        catalogue = []
        for line in (args.data / f'crown28.trianglefree{order}.g6').read_text().splitlines():
            graph = parse_graph6(line)
            assert len(graph) == order and triangle_free(graph)
            if brute_alpha(graph) <= 3:
                catalogue.append(graph)
        assert len(catalogue) == expected[order]
        for index, graph in enumerate(catalogue, 1):
            choices = independent_multiplicity(graph, 4, 4)
            if order >= 7:
                pairs, triples = check_equal_triples(graph, choices, 5, 6)
                print(f'W{order} index {index}: {len(choices)} size-four, {pairs} viable pairs, {len(triples)} triples.')
            else:
                found, nodes = first_packing(graph, choices, 10 - order, 3)
                status = 'EMPTY' if found is None else ['SURVIVES', [choices[value] for value in found]]
                print(f'W{order} index {index}: {len(choices)} size-four, {nodes} nodes, {status}.')


if __name__ == '__main__':
    main()
