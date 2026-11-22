#!/usr/bin/env python3
"""Independent edge-subset oracle for the Hall propagation controls."""

from itertools import combinations
from pathlib import Path
from subprocess import run
from sys import argv

from check_root_cover import graph as checker


def members(mask):
    return tuple(index for index in range(mask.bit_length()) if mask >> index & 1)


def union(masks):
    result = 0
    for mask in masks:
        result |= mask
    return result


def oracle(support, palettes, alpha):
    order = len(support)
    pairs = list(combinations(range(order), 2))
    forbidden = {pair for pair in pairs if support[pair[0]] & support[pair[1]]}
    forced = set()
    unclear = set(pairs) - forbidden
    independent = [members(mask) for mask in range(1 << order)]
    bad = []
    for vertices in independent:
        neighbourhood = union(support[vertex] for vertex in vertices)
        if any(len(vertices) + (palette & ~neighbourhood).bit_count() > alpha for palette in palettes):
            bad.append(set(combinations(vertices, 2)))
    while True:
        if any(pattern <= forbidden for pattern in bad):
            return (0,)
        next_on = {next(iter(pattern - forbidden)) for pattern in bad if len(pattern - forbidden) == 1}
        if next_on & forbidden:
            return (0,)
        forced |= next_on
        next_off = set()
        for vertex in range(order):
            peers = {peer for edge in forced if vertex in edge for peer in edge if peer != vertex}
            next_off.update(combinations(sorted(peers), 2))
        if next_off & forced:
            return (0,)
        if (forced | next_off) & unclear == set():
            return (1, *bitmap(forced, order), *bitmap(forbidden, order))
        forbidden |= next_off
        unclear -= forced | next_off


def bitmap(pairs, order):
    masks = [0] * order
    for left, right in pairs:
        masks[left] |= 1 << right
        masks[right] |= 1 << left
    return masks


def maximum_anchor_sets(adj, anchors):
    masks = [sum(1 << index for index, peer in enumerate(anchors) if adj[vertex] >> peer & 1) for vertex in anchors]
    for mask in range(1 << len(anchors)):
        present = members(mask)
        if any(masks[index] & mask for index in present):
            continue
        if all(masks[index] & mask or mask >> index & 1 for index in range(len(anchors))):
            yield mask


def instance(adj, left, right, alpha, exact):
    anchors = (*members(adj[left] & ~(1 << right)), *members(adj[right] & ~(1 << left)))
    assert len(anchors) == len(set(anchors))
    exterior = tuple(vertex for vertex in range(len(adj)) if vertex not in {left, right, *anchors})
    supports = [sum(1 << index for index, anchor in enumerate(anchors) if adj[vertex] >> anchor & 1) for vertex in exterior]
    palettes = list(maximum_anchor_sets(adj, anchors))
    actual = [sum(1 << index for index, peer in enumerate(exterior) if adj[vertex] >> peer & 1) for vertex in exterior]
    return supports, palettes, alpha, actual, exact


def control(binary, catalogue):
    c13, c35, exoo = (checker.parse_graph6(row) for row in catalogue.read_text().splitlines())
    cases = [instance(c13, left, right, 4, True) for left in range(len(c13)) for right in members(c13[left])]
    cases += [instance(graph, 0, right, alpha, False) for graph, alpha in ((c35, 8), (exoo, 9)) for right in members(graph[0])]
    cases += [([1, 2, 3], [3], 2, [2, 1, 0], True), ([1, 1], [3], 2, None, True)]
    rows = ''.join(' '.join(map(str, [len(support), alpha, len(palettes), *support, *palettes])) + '\n'
                   for support, palettes, alpha, _, _ in cases)
    results = run([binary, 'control'], input=rows, text=True, capture_output=True, check=True)
    total_forced = total_forbidden = 0
    for (support, palettes, alpha, actual, exact), output in zip(cases, results.stdout.splitlines(), strict=True):
        result = tuple(map(int, output.split()))
        if exact:
            assert result == oracle(support, palettes, alpha), (support, result)
        if actual is None:
            assert result == (0,)
            continue
        assert result[0] == 1
        order = len(actual)
        for known, forced, forbidden in zip(actual, result[1:1 + order], result[1 + order:], strict=True):
            assert not (forced & ~known or forbidden & known)
            total_forced += forced.bit_count()
            total_forbidden += forbidden.bit_count()
    print(f'{len(cases)} controls, {sum(item[4] for item in cases)} exact independent oracles, '
          f'{total_forced//2} true forced edges and {total_forbidden//2} true forbidden edges')


if __name__ == '__main__':
    control(str(Path(argv[1]).resolve()), Path(argv[2]))
