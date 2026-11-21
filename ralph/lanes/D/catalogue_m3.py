#!/usr/bin/env python3
"""Independent component cover for the bipartite R(3) edge kernel."""

import argparse
from collections import Counter
from pathlib import Path

from kernel_cnf import decode
from pin_controls import graph6


def types(side):
    for half in range(side):
        yield (half + 1, half, 'path')
        yield (half, half + 1, 'path')
    for half in range(1, side + 1):
        yield (half, half, 'path')
        if half >= 2:
            yield (half, half, 'cycle')


def covers(side, min_matching, max_edges):
    components = tuple(sorted(types(side)))

    def enumerate_components(start, left, right, matching, edges, signature):
        if not (left or right):
            if matching >= min_matching:
                yield tuple(signature)
            return
        if matching + min(left, right) < min_matching:
            return
        for index in range(start, len(components)):
            comp = components[index]
            count_left, count_right, kind = comp
            count_edges = count_left + count_right - (kind == 'path')
            if count_left <= left and count_right <= right and count_edges <= max_edges - edges:
                yield from enumerate_components(index, left - count_left, right - count_right,
                                                matching + min(count_left, count_right), edges + count_edges,
                                                signature + [comp])

    return set(enumerate_components(0, side, side, 0, 0, []))


def swap(signature):
    return tuple(sorted((right, left, kind) for left, right, kind in signature))


def signature_of(side, line):
    assert ord(line[0]) - 63 == 2 * side
    adjacency = [set() for _ in range(2 * side)]
    for left, right in decode(line):
        assert left < side <= right
        adjacency[left].add(right)
        adjacency[right].add(left)
    assert all(len(row) <= 2 for row in adjacency)
    remaining = set(range(2 * side))
    signature = []
    while remaining:
        stack = [remaining.pop()]
        component = set(stack)
        while stack:
            new = adjacency[stack.pop()] & remaining
            stack.extend(new)
            component.update(new)
            remaining.difference_update(new)
        left = sum(vertex < side for vertex in component)
        kind = 'cycle' if all(len(adjacency[vertex]) == 2 for vertex in component) else 'path'
        signature.append((left, len(component) - left, kind))
    return tuple(sorted(signature))


def representative(side, signature):
    next_left, next_right = 0, side
    edges = set()
    for count_left, count_right, kind in signature:
        left = list(range(next_left, next_left + count_left))
        right = list(range(next_right, next_right + count_right))
        if count_left < count_right:
            left, right = right, left
        vertices = [vertex for group in zip(left, right) for vertex in group] + left[len(right):]
        edges.update(tuple(sorted(pair)) for pair in zip(vertices, vertices[1:]))
        if kind == 'cycle':
            edges.add(tuple(sorted((vertices[-1], vertices[0]))))
        next_left += count_left
        next_right += count_right
    code = graph6(2 * side, edges)
    assert signature_of(side, code) == signature
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('side', type=int)
    parser.add_argument('min_matching', type=int)
    parser.add_argument('max_edges', type=int)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--write', type=Path)
    parser.add_argument('--orientation-orbits', action='store_true')
    args = parser.parse_args()
    signatures = covers(args.side, args.min_matching, args.max_edges)
    unoriented = {min(sig, swap(sig)) for sig in signatures}
    print(f'{len(signatures)} oriented classes; {len(unoriented)} up to side exchange')
    print('Counts by edge count:', sorted(Counter(sum(left + right - (kind == 'path') for left, right, kind in sig)
                                                  for sig in signatures).items()))
    if args.check:
        actual = Counter(signature_of(args.side, line) for line in args.check.read_text().splitlines())
        assert set(actual) == signatures and set(actual.values()) == {1}, (
            len(signatures - set(actual)), len(set(actual) - signatures), max(actual.values(), default=0))
        print('PASS: exactly one supplied graph6 for every oriented component signature')
    if args.write:
        args.write.write_text('\n'.join(representative(args.side, sig)
                                      for sig in sorted(unoriented if args.orientation_orbits else signatures)) + '\n')


if __name__ == '__main__':
    main()
