#!/usr/bin/env python3
"""Exact orbit-neighborhood profiles for a root with four fixed neighbors."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, triangle_free


def bits(mask):
    while mask:
        unit = mask & -mask
        yield unit.bit_length() - 1
        mask ^= unit


def edge(graph, left, right):
    graph[left] |= 1 << right
    graph[right] |= 1 << left


def block(graph, left, right, differences):
    for phase, difference in product(range(3), differences):
        edge(graph, left * 3 + phase, right * 3 + ((phase + difference) % 3))


def shapes():
    for doubled, compositions in [(False, ((1, 1, 1, 1), (2, 1, 1), (1, 2, 1),
                                          (1, 1, 2), (2, 2))),
                                   (True, ((1, 1, 1), (2, 1), (1, 2)))]:
        for composition in compositions:
            groups = tuple(index for index, size in enumerate(composition) for _ in range(size))
            order = len(groups) + doubled
            graph = [0] * (3 * order)
            if doubled:
                for other in range(1, order):
                    block(graph, 0, other, (1,))
            for left, right in combinations(range(len(groups)), 2):
                offsets = (1, 2) if groups[left] == groups[right] else (1,)
                block(graph, left + doubled, right + doubled, offsets)
            root_load = (1 + doubled,) + (1,) * (order - 1)
            yield ('D:' if doubled else 'S:') + ''.join(map(str, composition)), graph, root_load


def profile_data(graph, keep_words=False):
    order = len(graph) // 3
    universe = (1 << len(graph)) - 1

    @lru_cache(None)
    def alpha(mask):
        if not mask:
            return 0
        root = (mask & -mask).bit_length() - 1
        other = mask ^ (1 << root)
        return max(alpha(other), 1 + alpha(other & ~graph[root]))

    profiles = set()
    words = []
    word_count = 0
    for picked in range(1 << len(graph)):
        if any(graph[vertex] & picked for vertex in bits(picked)):
            continue
        shifts = [sum(1 << (3 * (vertex // 3) + ((vertex + phase) % 3)) for vertex in bits(picked))
                  for phase in range(3)]
        if picked != min(shifts):
            continue
        word_count += 1
        max_alpha = alpha(universe)
        for colors in range(1, 8):
            blocked = 0
            for phase in bits(colors):
                blocked |= shifts[phase]
            max_alpha = max(max_alpha, colors.bit_count() + alpha(universe & ~blocked))
        load = tuple(((picked >> (3 * index)) & 7).bit_count() for index in range(order))
        profiles.add((max_alpha, load))
        if keep_words:
            words.append((picked, max_alpha, load))
    return word_count, profiles, words


def control():
    graph = [0] * 3
    count, profiles, _ = profile_data(graph)
    oracle = set()
    for mask in range(8):
        whole = graph + [0] * 3
        block(whole, 1, 0, tuple(bits(mask)))
        assert triangle_free(whole)
        oracle.add((brute_alpha(whole), (mask.bit_count(),)))
    assert count == 4 and oracle == profiles
    print('Control: one-orbit profiles match exact (3,4,6) matching/6-cycle and non-Ramsey cases.')
    graph = [0] * 15
    for left, right in combinations(range(5), 2):
        block(graph, left, right, (1, 2) if (left, right) in ((0, 1), (3, 4)) else (1,))
    independent = (1, 4, 6, 7, 9, 12)
    assert triangle_free(graph) and brute_alpha(graph) == 6
    assert all(not (graph[left] >> right & 1) for left, right in combinations(independent, 2))
    print('Control: 2,1,2 on five orbits contains the middle-singleton independent 6-set.')


def pack(profiles, capacity, count, r_budget, max_alpha_in_h):
    template = [(max(0, maximum - max_alpha_in_h), load) for maximum, load in sorted(profiles)
                if max(0, maximum - max_alpha_in_h) <= 4 and all(a <= b for a, b in zip(load, capacity))]
    states = {(0,) * (len(capacity) + 1)}
    for _ in range(count):
        new = set()
        for state in states:
            for minimum, load in template:
                attach = state[0] + minimum
                if attach > r_budget:
                    continue
                added = tuple(left + right for left, right in zip(state[1:], load))
                if all(left <= right for left, right in zip(added, capacity)):
                    new.add((attach,) + added)
        states = new
    return states


def main():
    control()
    for shape, graph, roots in shapes():
        limit = tuple(9 - graph[3 * index].bit_count() - load for index, load in enumerate(roots))
        assert triangle_free(graph) and brute_alpha(graph) <= 5
        word_count, profiles, _ = profile_data(graph)
        mins = []
        for fixed in range(5):
            feasible = [sum(load) for maximum, load in profiles if maximum <= 5 + fixed]
            mins.append(min(feasible, default=-1))
        for fixed in (7, 10):
            orbits = (40 - fixed) // 3 - 1 - len(roots)
            result = pack(profiles, limit, orbits, 8, 5)
            levels = sorted(Counter(state[0] for state in result).items())
            print(f'{shape} f={fixed} capacity={limit}, J={orbits}, words={word_count}, '
                  f'profiles={len(profiles)}, minimum loads={mins}, states={levels}')


if __name__ == '__main__':
    main()
