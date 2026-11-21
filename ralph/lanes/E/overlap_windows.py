#!/usr/bin/env python3
"""Join the four order-17 windows of the remaining f=28 overlap cycle."""

import argparse
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, product
import json

import pynauty

from involution_cores import bits
from involution_sat import from_graph6, to_graph6, witnesses


def permute_mask(mask, image):
    return sum(1 << image[index] for index in bits(mask))


def induced(adj, vertices):
    return tuple(sum(1 << index for index, old in enumerate(vertices) if adj[vertex] & (1 << old))
                 for vertex in vertices)


def nauty(adj):
    return pynauty.Graph(len(adj), adjacency_dict={index: list(bits(row)) for index, row in enumerate(adj)})


@cache
def canon(adj):
    label = pynauty.canon_label(nauty(adj))
    core = induced(adj, label)
    return core, tuple(label.index(index) for index in range(len(adj)))


@cache
def automorphisms(core):
    generators = pynauty.autgrp(nauty(core))[0]
    identity = tuple(range(len(core)))
    seen = {identity}
    frontier = [identity]
    while frontier:
        perm = frontier.pop()
        for generator in generators:
            image = tuple(generator[index] for index in perm)
            if image not in seen:
                seen.add(image)
                frontier.append(image)
    return tuple(sorted(seen))


def projection(adj, left, right, root):
    universe = (1 << len(adj)) - 1
    vertices = tuple(bits(universe ^ (left | right | (1 << root))))
    core, perm = canon(induced(adj, vertices))
    masks = {vertex: sum(1 << perm[index] for index, other in enumerate(vertices)
                         if adj[vertex] & (1 << other)) for vertex in bits(left | right | (1 << root))}
    return core, tuple(masks[vertex] for vertex in bits(left)), tuple(masks[vertex] for vertex in bits(right)), masks[root]


def rows_from_anchors(path):
    rows = defaultdict(set)
    seen = set()
    for number, line in enumerate(open(path, encoding='ascii'), 1):
        adj = from_graph6(line.strip())
        assert len(adj) == 17
        assert not any(adj[left] & adj[right] for left in range(17) for right in bits(adj[left]))
        universe = (1 << len(adj)) - 1
        assert next(witnesses(adj, universe, 6), None) is None
        cert = pynauty.certificate(nauty(adj))
        assert cert not in seen
        seen.add(cert)
        indsets = tuple(witnesses(adj, universe, 4))
        count = 0
        for left, right in combinations(indsets, 2):
            if left & right:
                continue
            eligible = universe ^ (left | right)
            for vertex in bits(left | right):
                eligible &= ~adj[vertex]
            for root in bits(eligible):
                core, first, second, third = projection(adj, left, right, root)
                rows[core].add((tuple(sorted(first)), tuple(sorted(second)), third))
                count += 1
        print(f'ANCHOR {number} layouts={count}', flush=True)
    assert len(seen) == 7
    expanded = {}
    for core in sorted(rows):
        perms = automorphisms(core)
        expanded[core] = set()
        for first, second, third in rows[core]:
            for perm in perms:
                left = tuple(sorted(permute_mask(mask, perm) for mask in first))
                right = tuple(sorted(permute_mask(mask, perm) for mask in second))
                root = permute_mask(third, perm)
                expanded[core].add((left, right, root))
                expanded[core].add((right, left, root))
    print(f'WINDOWS cores={len(rows)} distinct_placements={sum(map(len, expanded.values()))}', flush=True)
    return expanded


def cycles(expanded, output):
    stats = Counter()
    for core, rows in expanded.items():
        links = defaultdict(lambda: defaultdict(set))
        for left, right, root in rows:
            links[left][right].add(root)
        collisions = Counter()
        for first in sorted(links):
            for second in sorted(links[first]):
                if first > second:
                    continue
                for third in sorted(links[second]):
                    if first > third:
                        continue
                    for fourth in sorted(links[third]):
                        if second > fourth or first > fourth or first not in links[fourth]:
                            continue
                        stats['mask_cycles'] += 1
                        ring = (first, second, third, fourth)
                        pinned = tuple(core[index].bit_count() + sum((mask >> index) & 1
                                                                      for part in ring for mask in part)
                                       for index in range(len(core)))
                        if max(pinned) > 9:
                            continue
                        roots = tuple(tuple(sorted(links[left][right])) for left, right in zip(ring, ring[1:] + ring[:1]))
                        collisions[(pinned, roots)] += 1
        passed = sum(collisions.values())
        if passed:
            print(f'CYCLES core={to_graph6(core)} rows={len(rows)} degree9_cycles={passed} root_patterns={len(collisions)}',
                  flush=True)
            stats['degree9_cycles'] += passed
            for (pinned, roots), count in sorted(collisions.items()):
                output.write(json.dumps([to_graph6(core), pinned, roots, count]) + '\n')
    print('JOIN', dict(stats), flush=True)


def partitions(core):
    independent = tuple(sorted(mask for size in range(1, 5) for mask in witnesses(core, 255, size)))
    all_independent = (0,) + tuple(mask for size in range(1, 6) for mask in witnesses(core, 255, size))
    seen = set()
    for left, right in combinations(independent, 2):
        sizes = tuple(sorted((left.bit_count(), right.bit_count())))
        if left & right or sizes not in {(1, 4), (2, 3), (2, 4), (3, 3), (3, 4), (4, 4)}:
            continue
        if (left, right) in seen:
            continue
        seen.update(tuple(sorted((permute_mask(left, perm), permute_mask(right, perm))))
                    for perm in automorphisms(core))
        free = 255 ^ (left | right)
        domains = ((free, 3), (free | left, 4), (free | right, 4), (255, 5))
        if any(mask.bit_count() > limit and not mask & ~domain
               for domain, limit in domains for mask in all_independent):
            continue
        return_rows = tuple((mask, limit + 1 - mask.bit_count()) for domain, limit in domains
                            for mask in all_independent if not mask & ~domain and limit < mask.bit_count() + 3)
        yield left, right, free, return_rows


def part_compatible(attachment, requirements):
    return all(sum(not (mask & support) for support in attachment) <= cap for mask, cap in requirements)


def joined_partitions(expanded, output):
    stats = Counter()
    by_sizes = Counter()
    for core, rows in expanded.items():
        core_stats = Counter()
        profiles = {part for first, second, _ in rows for part in (first, second)}
        for left, right, free, requirements in partitions(core):
            cap = tuple((9 if free & (1 << index) else 7) - core[index].bit_count() for index in range(8))
            links = defaultdict(lambda: defaultdict(set))
            admissible = {part for part in profiles if part_compatible(part, requirements)}
            for first, second, root in rows:
                if first in admissible and second in admissible:
                    links[first][second].add(root)
            if not links:
                continue
            core_stats['partitions'] += 1
            for first in sorted(links):
                for second in sorted(links[first]):
                    if first > second:
                        continue
                    for third in sorted(links[second]):
                        if first > third:
                            continue
                        for fourth in sorted(links[third]):
                            if second > fourth or first > fourth or first not in links[fourth]:
                                continue
                            ring = (first, second, third, fourth)
                            left_deg = tuple(cap[index] - sum((mask >> index) & 1 for part in ring for mask in part)
                                             for index in range(8))
                            if min(left_deg) < 0:
                                continue
                            core_stats['cycle_cap'] += 1
                            roots = [tuple(sorted(links[before][after])) for before, after in zip(ring, ring[1:] + ring[:1])]
                            possible = []
                            for root_pattern in product(*roots):
                                if any(sum((mask >> index) & 1 for mask in root_pattern) > left_deg[index]
                                       for index in range(8)):
                                    continue
                                possible.append(root_pattern)
                            if not possible:
                                continue
                            core_stats['root_cap'] += len(possible)
                            sizes = tuple(sorted((left.bit_count(), right.bit_count())))
                            by_sizes[sizes] += len(possible)
                            output.write(json.dumps([to_graph6(core), left, right, ring, possible]) + '\n')
        stats.update(core_stats)
        if core_stats['root_cap']:
            print(f'PJOIN {to_graph6(core)} {dict(core_stats)}', flush=True)
    print(f'PARTITIONS {dict(stats)} by_sizes={sorted(by_sizes.items())}', flush=True)


def calibrate():
    # Disconnected six-vertex core, including nontrivial automorphisms.
    original = (2, 1, 24, 4, 4, 0)
    representative, _ = canon(original)
    for perm in combinations(range(len(original)), 2):
        label = list(range(len(original)))
        first, second = perm
        label[first], label[second] = label[second], label[first]
        assert canon(induced(original, label))[0] == representative
    assert len(automorphisms(representative)) == 4
    print('Canonical label and automorphism controls pass', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--anchors')
    parser.add_argument('--output')
    parser.add_argument('--partitions', action='store_true')
    args = parser.parse_args()
    if args.control:
        calibrate()
    else:
        with open(args.output, 'w', encoding='ascii') as stream:
            (joined_partitions if args.partitions else cycles)(rows_from_anchors(args.anchors), stream)


if __name__ == '__main__':
    main()
