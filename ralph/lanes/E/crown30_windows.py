#!/usr/bin/env python3
"""Check extreme W windows in a crown on five moved pairs."""
import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import alpha, brute_alpha, parse_graph6, triangle_free


def masks(available):
    while available:
        low = available & -available
        yield low.bit_length() - 1
        available ^= low


def induced(graph, members):
    vertices = list(masks(members))
    return [sum(1 << index for index, other in enumerate(vertices) if graph[vertex] >> other & 1)
            for vertex in vertices]


def independent_multiplicity(graph, add, alpha_limit):
    full = (1 << len(graph)) - 1
    ranks = [0] * (full + 1)
    for members in range(1, full + 1):
        low = members & -members
        vertex = low.bit_length() - 1
        other = members ^ low
        ranks[members] = max(ranks[other], 1 + ranks[other & ~graph[vertex]])
    assert ranks[full] == alpha(graph)
    if ranks[full] > alpha_limit:
        return []
    neighbors = [members for members in range(full + 1)
                 if ranks[members] == members.bit_count() and ranks[full ^ members] < alpha_limit]

    def extend(start, picked, subgroups):
        if len(picked) == add:
            yield picked
            return
        for index in range(start, len(neighbors)):
            word = neighbors[index]
            next_subgroups = [(union | word, count + 1) for union, count in subgroups]
            if all(ranks[full ^ union] + count <= alpha_limit for union, count in next_subgroups):
                yield from extend(index, picked + (word,), subgroups + next_subgroups)

    return list(extend(0, (), [(0, 0)]))


def materialize(graph, words):
    result = graph.copy() + list(words)
    for index, word in enumerate(words, len(graph)):
        for vertex in masks(word):
            result[vertex] |= 1 << index
    return result


def optimistic_groups(graph, *groups):
    combined = materialize(graph, sum(groups, ()))
    previous = []
    start = len(graph)
    for group in groups:
        for index, left in enumerate(group, start):
            for neighbor, right in previous:
                if not left & right:
                    combined[index] |= 1 << neighbor
                    combined[neighbor] |= 1 << index
        previous.extend(enumerate(group, start))
        start += len(group)
    return combined


def pair_ranks(graph, first, second):
    return alpha(optimistic_groups(graph, first, second))


def check_equal_triples(graph, choices, pair_limit, triple_limit):
    compatible = [{other for other in range(index, len(choices))
                   if pair_ranks(graph, first, choices[other]) <= pair_limit}
                  for index, first in enumerate(choices)]
    triples = []
    for index, first in enumerate(choices):
        for second in sorted(compatible[index]):
            for third in sorted(compatible[index] & compatible[second]):
                groups = (first, choices[second], choices[third])
                if any(row.bit_count() + sum(word >> vertex & 1 for word in sum(groups, ())) > 9
                       for vertex, row in enumerate(graph)):
                    continue
                if alpha(optimistic_groups(graph, *groups)) <= triple_limit:
                    triples.append((index, second, third))
    return sum(map(len, compatible)), triples


def inputs(path, order, bound):
    found = []
    for line in path.read_text().splitlines():
        graph = parse_graph6(line)
        assert len(graph) == order and triangle_free(graph) and alpha(graph) <= bound
        found.append(graph)
    return found


def control(graph13):
    full = (1 << 13) - 1
    for vertices in combinations(range(13), 4):
        group = sum(1 << vertex for vertex in vertices)
        if all(not graph13[vertex] & group for vertex in vertices):
            rest = full ^ group
            base = induced(graph13, rest)
            words = [sum(1 << index for index, other in enumerate(masks(rest)) if graph13[vertex] >> other & 1)
                     for vertex in vertices]
            choices = independent_multiplicity(base, 4, 4)
            assert tuple(sorted(words)) in choices and choices
            for choice in choices:
                witness = materialize(base, choice)
                assert triangle_free(witness) and brute_alpha(witness) == 4
            break
    else:
        raise AssertionError('expected independent 4-set in the planted order-13 control')
    assert independent_multiplicity(graph13, 1, 4) == []
    for first, second, expected in (((1, 2), (2, 4), 4), ((0, 0), (0, 0), 5)):
        graph = optimistic_groups([0, 0, 0], first, second)
        assert triangle_free(graph) and brute_alpha(graph) == alpha(graph) == expected
    print(f'Control: {len(choices)} checked order-13 extensions including the planted one; order 14 empty.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue_dir', type=Path)
    parser.add_argument('--probe11', action='store_true')
    parser.add_argument('--a4-w12', action='store_true')
    args = parser.parse_args()
    path = args.catalogue_dir
    graphs13 = inputs(path / 'r35_13.g6', 13, 4)
    graphs12 = inputs(path / 'r35_12.g6', 12, 4)
    graphs17 = inputs(path / 'r36_17.g6', 17, 5)
    assert (len(graphs12), len(graphs13), len(graphs17)) == (12, 1, 7)
    control(graphs13[0])
    for add in (4, 5):
        placements = 0
        for graph in graphs17:
            full = (1 << len(graph)) - 1
            for vertices in combinations(range(len(graph)), add):
                group = sum(1 << vertex for vertex in vertices)
                if all(not graph[vertex] & group for vertex in vertices) and alpha(induced(graph, full ^ group)) <= 4:
                    placements += 1
        print(f'7 order-17 anchors, delete I{add}: {placements} complements with alpha at most 4.')
        assert not placements
    for order, catalogue in ((12, graphs12), (13, graphs13)):
        counts = [len(independent_multiplicity(graph, 17 - order, 5)) for graph in catalogue]
        print(f'W-first order {order}: {len(catalogue)} roots, extension counts {counts}.')
        assert not any(counts)
    if args.a4_w12:
        for index, graph in enumerate(graphs12, 1):
            choices = independent_multiplicity(graph, 4, 5)
            pairs, triples = check_equal_triples(graph, choices, 6, 7)
            print(f'W12 index {index}: {len(choices)} size-four, {pairs} viable pairs, '
                  f'{len(triples)} viable triples.')
    if args.probe11:
        graphs11 = inputs(path / 'r35_11.g6', 11, 4)
        assert len(graphs11) == 105
        counts = []
        totals = Counter()
        for index, graph in enumerate(graphs11, 1):
            choices = independent_multiplicity(graph, 5, 5)
            counts.append(len(choices))
            if not choices:
                continue
            fifths = sum(pair_ranks(graph, first, second) <= 6
                         for position, first in enumerate(choices) for second in choices[position:])
            fourths = independent_multiplicity(graph, 4, 5)
            paired, triples = 0, 0
            for major in choices:
                candidates = [minor for minor in fourths if pair_ranks(graph, major, minor) <= 6]
                paired += len(candidates)
                for position, first in enumerate(candidates):
                    for second in candidates[position:]:
                        if any(row.bit_count() + sum(word >> vertex & 1 for word in major + first + second) > 9
                               for vertex, row in enumerate(graph)):
                            continue
                        if pair_ranks(graph, first, second) <= 6 and alpha(optimistic_groups(graph, major, first, second)) <= 7:
                            triples += 1
                            print(f'W11 triple {index}: {major} | {first} | {second}')
            totals.update(pairs55=fifths, pairs54=paired, triples544=triples)
            print(f'W11 index {index}: {len(choices)} size-five, {len(fourths)} size-four, '
                  f'{fifths} viable (5,5), {paired} viable (5,4), {triples} viable (5,4,4).')
        print('W-first order 11, size-five attachment:', dict(sorted(Counter(counts).items())))
        print('W11 pair totals:', dict(totals))


if __name__ == '__main__':
    main()
