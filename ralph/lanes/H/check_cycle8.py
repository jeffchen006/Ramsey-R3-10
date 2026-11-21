"""Rebuild the R(6) cycle-eight window relaxation from the order-22 census."""

from collections import defaultdict
from itertools import permutations
from pathlib import Path
import sys


def read_graph6(line):
    assert all(63 <= ord(char) <= 126 for char in line)
    order = ord(line[0]) - 63
    assert 0 <= order <= 62 and len(line) == 1 + (order * (order - 1) // 2 + 5) // 6
    bits = iter((ord(char) - 63) >> shift & 1 for char in line[1:] for shift in range(5, -1, -1))
    graph = [set() for _ in range(order)]
    for end in range(order):
        for start in range(end):
            if next(bits):
                graph[start].add(end)
                graph[end].add(start)
    assert not any(bits)
    return tuple(map(frozenset, graph))


def independent_sets(graph, size, available):
    if size == 0:
        yield ()
        return
    while len(available) >= size:
        first = min(available)
        available = available - {first}
        for suffix in independent_sets(graph, size - 1, available - graph[first]):
            yield (first, *suffix)


def invariant(graph):
    return tuple((len(neighbors), tuple(sorted(len(graph[index]) for index in neighbors)))
                 for neighbors in graph)


def isomorphisms(source, target, source_labels, target_labels):
    domains = [tuple(index for index, label in enumerate(target_labels) if label == source_label)
               for source_label in source_labels]
    available = set(range(len(source)))
    order = []
    while available:
        current = min(available, key=lambda i: (-len(source[i] - available), len(domains[i]), -len(source[i]), i))
        order.append(current)
        available.remove(current)
    assigned = {}
    seen = set()

    def extend(depth):
        if depth == len(source):
            yield tuple(assigned[index] for index in range(len(source)))
            return
        current = order[depth]
        for image in domains[current]:
            if image in seen or any((other in source[current]) != (mapped in target[image])
                                    for other, mapped in assigned.items()):
                continue
            assigned[current] = image
            seen.add(image)
            yield from extend(depth + 1)
            seen.remove(image)
            del assigned[current]

    yield from extend(0)


def ordered_matchings(remaining):
    if not remaining:
        yield ()
        return
    first, *others = remaining
    for second in others:
        for suffix in ordered_matchings(tuple(index for index in others if index != second)):
            yield ((first, second), *suffix)


def load(scores):
    return tuple(sum(column) for column in zip(*scores))


def split_loads(windows, target):
    extensions = defaultdict(set)
    loads = {}
    for first, second, third in windows:
        extensions[(first, second)].add(third)
        for pair in (first, second, third):
            if pair not in loads:
                loads[pair] = tuple(sum(mask >> index & 1 for mask in pair)
                                    for index in range(len(target)))
    profiles = set()
    words = 0
    for first, second, third in windows:
        subtotal = load(loads[pair] for pair in (first, second, third))
        for fourth in extensions[(second, third)]:
            words += 1
            profiles.add(load((subtotal, loads[fourth])))
    found = any(tuple(need - count for need, count in zip(target, profile)) in profiles
                for profile in profiles)
    return found, words


def verify(census):
    matchings = [order for matching in ordered_matchings(tuple(range(6)))
                 for order in permutations(matching)]
    assert len(matchings) == len(set(matchings)) == 90
    one = (1, 1)
    assert split_loads({(one, one, one)}, (16,)) == (True, 1)
    assert split_loads({(one, one, one)}, (15,)) == (False, 1)

    families = defaultdict(list)
    seeds = [read_graph6(line) for line in census.read_text().splitlines()]
    original_labels = defaultdict(list)
    surviving = 0
    for seed in seeds:
        assert len(seed) == 22 and all(len(neighbors) <= 6 for neighbors in seed)
        assert all(not (neighbors & seed[neighbor]) for neighbors in seed for neighbor in neighbors)
        available = frozenset(range(len(seed)))
        assert next(independent_sets(seed, 7, available), None) is None
        seed_labels = invariant(seed)
        key = tuple(sorted(seed_labels))
        for old, labels in original_labels[key]:
            assert next(isomorphisms(old, seed, labels, seed_labels), None) is None
        original_labels[key].append((seed, seed_labels))

        for omitted in independent_sets(seed, 6, available):
            kept = sorted(available.difference(omitted))
            residue = tuple(frozenset(index for index, vertex in enumerate(kept) if vertex in seed[root])
                            for root in kept)
            degrees = tuple(map(len, residue))
            twice_edges = sum(degrees)
            if max(degrees) > 4 or not 48 <= twice_edges <= 64:
                continue
            if sum(6 - len(seed[vertex]) for vertex in omitted) > twice_edges - 48:
                continue
            surviving += 1
            labels = invariant(residue)
            candidates = families[tuple(sorted(labels))]
            for representative, target_labels, triples in candidates:
                mapping = next(isomorphisms(residue, representative, labels, target_labels), None)
                if mapping is not None:
                    break
            else:
                representative, target_labels, triples = residue, labels, set()
                candidates.append((representative, target_labels, triples))

            neighborhoods = [tuple(index for index, vertex in enumerate(kept) if vertex in seed[root])
                             for root in omitted]
            window = set()
            for mapping in isomorphisms(residue, representative, labels, target_labels):
                masks = tuple(sum(1 << mapping[index] for index in adjacency) for adjacency in neighborhoods)
                if masks in window:
                    continue
                window.add(masks)
                overlap = tuple(tuple((first & second).bit_count() for second in masks) for first in masks)
                for pairs in matchings:
                    if any(overlap[first][second] > 3 for first, second in pairs):
                        continue
                    if any(overlap[first][second] > 3 + upper - lower
                           for lower, upper in ((0, 1), (0, 2), (1, 2))
                           for first in pairs[lower] for second in pairs[upper]):
                        continue
                    triples.add(tuple(tuple(sorted((masks[first], masks[second]))) for first, second in pairs))
            assert window

    graph_count = sum(map(len, families.values()))
    print(f'census={len(seeds)} admissible_sets={surviving} residue_families={graph_count}', flush=True)
    assert (len(seeds), surviving, graph_count) == (191, 270, 32)
    word_count = 0
    for candidates in families.values():
        for representative, _, triples in candidates:
            found, words = split_loads(triples, tuple(9 - len(neighbors) for neighbors in representative))
            assert not found, 'complementary half-load pair found; this relaxation is inconclusive'
            word_count += words
    print(f'four-type words={word_count} complementary_pairs=0', flush=True)
    assert word_count == 95984


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
