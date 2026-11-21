#!/usr/bin/env python3
"""Pair-footprint CSP for the pinned order-three a=4 reduction."""
import argparse
from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations, product
from functools import lru_cache
import sys

sys.dont_write_bytecode = True
from order3_a4_profiles import bits, block, brute_alpha, profile_data, shapes, triangle_free


def rotation(word, shift):
    return sum(1 << (3 * (vertex // 3) + ((vertex + shift) % 3)) for vertex in bits(word))


def neighborhoods(word):
    shifts = [rotation(word, phase) for phase in range(3)]
    return [(shifts[0] if colors & 1 else 0) | (shifts[1] if colors & 2 else 0) |
            (shifts[2] if colors & 4 else 0) for colors in range(8)]


def pair_offsets(left_neighbors, right_neighbors):
    return tuple(offset for offset in range(3) if not left_neighbors[1] & right_neighbors[1 << offset])


def pair_alpha(complement_alpha, universe, left_neighbors, right_neighbors, offsets):
    interact = [0] * 8
    for colors in range(8):
        for phase in bits(colors):
            for offset in offsets:
                interact[colors] |= 1 << ((phase + offset) % 3)
    return max(left_colors.bit_count() + right_colors.bit_count() + complement_alpha[
               universe & ~(left_neighbors[left_colors] | right_neighbors[right_colors])]
               for left_colors in range(8) for right_colors in range(8)
               if not interact[left_colors] & right_colors)


def root_neighbors(shape):
    return sum(1 << (3 * index) for index in range(4)) | (2 if shape.startswith('D') else 0)


def alpha_tables(graph, root_word):
    @lru_cache(None)
    def rank(mask):
        if not mask:
            return 0
        vertex = (mask & -mask).bit_length() - 1
        other = mask ^ (1 << vertex)
        return max(rank(other), 1 + rank(other & ~graph[vertex]))

    universe = (1 << len(graph)) - 1
    table = [rank(mask) for mask in range(universe + 1)]
    root = neighborhoods(root_word)
    rooted = [max(picked.bit_count() + table[mask & ~root[picked]] for picked in range(8))
              for mask in range(universe + 1)]
    return universe, table, rooted


def control():
    for first, second in product(range(1, 8), repeat=2):
        first_word = min(rotation(first, phase) for phase in range(3))
        second_word = min(rotation(second, phase) for phase in range(3))
        words = neighborhoods(first_word), neighborhoods(second_word)
        universe, table, with_root = alpha_tables([0, 0, 0], 1)
        offsets = pair_offsets(*words)
        for selected in ((), offsets):
            graph = [0] * 9
            block(graph, 1, 0, tuple(bits(first_word)))
            block(graph, 2, 0, tuple(bits(second_word)))
            block(graph, 1, 2, selected)
            assert triangle_free(graph)
            assert brute_alpha(graph) == pair_alpha(table, universe, *words, selected)
            rooted = graph + [0] * 3
            block(rooted, 3, 0, (0,))
            assert triangle_free(rooted)
            assert brute_alpha(rooted) == pair_alpha(with_root, universe, *words, selected)
        for offset in set(range(3)) - set(offsets):
            graph = [0] * 9
            block(graph, 1, 0, tuple(bits(first_word)))
            block(graph, 2, 0, tuple(bits(second_word)))
            block(graph, 1, 2, (offset,))
            assert not triangle_free(graph)
    print('Control: all 49 footprint pairs match direct (H,J,K[,O]) alpha and triangle checks.')


@lru_cache(None)
def fixed_layouts(count):
    changes = [[sum(1 << image[index] for index in bits(mask)) for mask in range(16)]
               for image in permutations(range(4))]
    found = []
    for masks in combinations_with_replacement(range(1, 16), count):
        if sum(mask.bit_count() for mask in masks) > 8:
            continue
        if any(sum((mask >> index) & 1 for mask in masks) > 2 for index in range(4)):
            continue
        if any(tuple(sorted(change[mask] for mask in masks)) < masks for change in changes):
            continue
        found.append(masks)
    return found


def compatibility(shape, graph, footprints):
    universe, table, rooted = alpha_tables(graph, root_neighbors(shape))
    neighbors = [neighborhoods(word) for word, _, _ in footprints]
    size = len(neighbors)
    relations = [[0] * size for _ in range(10)]
    for first in range(size):
        for second in range(first, size):
            words = neighbors[first], neighbors[second]
            for joined, offsets in [(0, ()), (1, pair_offsets(*words))]:
                required = max(0, pair_alpha(table, universe, *words, offsets) - 5)
                if required > 4 or pair_alpha(rooted, universe, *words, offsets) > 9:
                    continue
                for fixed_union in range(required, 5):
                    relation = relations[5 * joined + fixed_union]
                    relation[first] |= 1 << second
                    relation[second] |= 1 << first
    return relations


def solve(masks, footprints, capacity, relations):
    count = len(masks)
    loads = [load for _, _, load in footprints]
    needed = [maximum - 5 for _, maximum, _ in footprints]
    domain = [sum(1 << index for index, bound in enumerate(needed) if bound <= mask.bit_count())
              for mask in masks]
    relations_for = [[relations[5 * (not (left & right)) + (left | right).bit_count()]
                      for right in masks] for left in masks]
    less_masks = [(1 << index) - 1 for index in range(len(footprints))]
    nodes = 0

    def rec(domains, remain, witness):
        nonlocal nodes
        nodes += 1
        if not remain:
            return witness
        for site in remain:
            allowed = 0
            for candidate in bits(domains[site]):
                if all(left >= right for left, right in zip(witness[-1], loads[candidate])):
                    allowed |= 1 << candidate
            if not allowed:
                return None
            domains[site] = allowed
        site = min(remain, key=lambda index: domains[index].bit_count())
        others = [index for index in remain if index != site]
        for candidate in bits(domains[site]):
            next_domains = domains.copy()
            for other in others:
                allowed = next_domains[other] & relations_for[site][other][candidate]
                if masks[site] == masks[other]:
                    allowed &= (less_masks[candidate] | (1 << candidate)) if other < site else ~less_masks[candidate]
                if not allowed:
                    break
                next_domains[other] = allowed
            else:
                next_capacity = tuple(a - b for a, b in zip(witness[-1], loads[candidate]))
                result = rec(next_domains, others, [*witness[:-1], (site, candidate), next_capacity])
                if result is not None:
                    return result
        return None

    result = rec(domain, list(range(count)), [capacity])
    return result, nodes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('templates', nargs='*')
    args = parser.parse_args()
    control()
    for shape, graph, roots in shapes():
        if args.templates and shape not in args.templates:
            continue
        limit = tuple(9 - graph[3 * index].bit_count() - load for index, load in enumerate(roots))
        footprints = [row for row in profile_data(graph, keep_words=True)[2]
                      if row[1] <= 9 and all(first <= second for first, second in zip(row[2], limit))]
        relations = compatibility(shape, graph, footprints)
        for fixed in (7, 10):
            count = (40 - fixed) // 3 - 5
            layouts = fixed_layouts(count)
            sizes = Counter()
            nodes = 0
            first_example = None
            for masks in layouts:
                found, visits = solve(masks, footprints, limit, relations)
                nodes += visits
                if found is not None:
                    sizes[sum(mask.bit_count() for mask in masks)] += 1
                    if first_example is None:
                        first_example = (masks, sorted((site, footprints[index][0]) for site, index in found[:-1]))
            print(f'{shape} f={fixed} layouts={len(layouts)} surviving_by_load={sorted(sizes.items())} '
                  f'nodes={nodes} example={first_example}', flush=True)


if __name__ == '__main__':
    main()
