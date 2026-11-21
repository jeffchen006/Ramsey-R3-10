#!/usr/bin/env python3
"""Short rerooting obstructions if every edge kernel is a forest."""

from itertools import combinations

from max_root import catalogue
from kernel_projection import bits, decode


def blocked_triples(kernel):
    for center, row in enumerate(kernel):
        if row.bit_count() != 2:
            continue
        opposite = tuple(bits(row))
        if not all(kernel[vertex].bit_count() == 2 for vertex in opposite):
            continue
        endpoints = tuple(next(bits(kernel[vertex] ^ (1 << center))) for vertex in opposite)
        assert endpoints[0] != endpoints[1]
        yield (1 << center) | (1 << endpoints[0]) | (1 << endpoints[1])


def blocked_arcs(kernel):
    for center, row in enumerate(kernel):
        if row.bit_count() != 2:
            continue
        for partner in bits(row):
            if partner <= center or kernel[partner].bit_count() != 2:
                continue
            third = kernel[partner] ^ (1 << center)
            fourth = row ^ (1 << partner)
            yield ((1 << center) | third, (1 << partner) | fourth)


def arc_bad(mask, other, forbidden):
    return any((mask & first == first and other & second == second) or
               (mask & second == second and other & first == first) for first, second in forbidden)


def check():
    from outer_star import Star

    def with_masks(star, masks, connected):
        adj = list(star.adj)
        for mask in masks:
            vertex = len(adj)
            for coord in bits(mask):
                adj[coord] |= 1 << vertex
            adj.append(mask)
        if connected:
            adj[-1] |= 1 << (len(adj) - 2)
            adj[-2] |= 1 << (len(adj) - 1)
        assert all(not (adj[first] & adj[second]) for first in range(len(adj)) for second in bits(adj[first]))
        for first, row in enumerate(adj):
            for second in bits(row):
                if second <= first:
                    continue
                kernel = (row ^ (1 << second)) | (adj[second] ^ (1 << first))
                remaining = kernel
                while remaining:
                    peeled = sum(1 << coord for coord in bits(remaining) if (adj[coord] & remaining).bit_count() <= 1)
                    if not peeled:
                        return True
                    remaining ^= peeled
        return False

    keys = list(catalogue(40, 9))
    checks = [0, 0]
    for index in (21, 33, 34):
        kernel = decode(keys[index])
        star = Star(kernel, 40, 9)
        assert not with_masks(star, [], False)
        for blocked in blocked_triples(kernel):
            choices = [mask for mask in star.masks if mask & blocked == blocked]
            if choices:
                assert with_masks(star, [choices[0]], False)
                checks[0] += 1
        for pair in blocked_arcs(kernel):
            witnesses = ((mask, other) for mask, other in combinations(star.masks, 2)
                         if not mask & other and arc_bad(mask, other, [pair]))
            witness = next(witnesses, None)
            if witness:
                assert with_masks(star, witness, True)
                checks[1] += 1
    assert all(checks)
    print(f'PASS explicit partial graph reroots: {checks[0]} triples and {checks[1]} arcs create a cycle')


if __name__ == '__main__':
    check()
