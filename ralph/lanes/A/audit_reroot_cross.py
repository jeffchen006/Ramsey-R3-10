#!/usr/bin/env python3
"""Necessary exact support pairing with all missing cross witnesses."""

from argparse import ArgumentParser
from collections import Counter
from functools import lru_cache
from itertools import permutations, product
from pathlib import Path
from random import Random

from audit_a_side_reroot import capacity, cross_edge, mask, parse_graph6, remnant, take, vertices


def cross_mask(left, right, width):
    return sum(right << (width * column) for column in vertices(left))


def solve(left, right, quotas, needed, width, cap=20000):
    left_types, right_types = (tuple(sorted(set(group))) for group in (left, right))
    left_counts = tuple(left.count(label) for label in left_types)
    right_counts = tuple(right.count(label) for label in right_types)
    status = tuple(label >> (width - 2) for label in left_types)
    binary = tuple(label >> (width - 1) for label in right_types)
    options = tuple((left_id, right_id, cross_mask(first, second, width))
                    for (left_id, first), (right_id, second) in product(enumerate(left_types), enumerate(right_types))
                    if not first & second & 1)
    nodes = 0

    @lru_cache(maxsize=None)
    def search(left_counts, right_counts, quotas, needed):
        nonlocal nodes
        nodes += 1
        if nodes > cap:
            raise OverflowError
        if not any(left_counts):
            return not (needed or any(right_counts) or any(quotas))
        remaining = [0] * 4
        for count, value in zip(left_counts, status, strict=True):
            remaining[value] += count
        if any(take_count > total for take_count, total in zip(quotas, remaining, strict=True)):
            return False
        allowed = tuple(row for row in options if left_counts[row[0]] and right_counts[row[1]] and
                        (quotas[status[row[0]]] > 0 if binary[row[1]] else
                         quotas[status[row[0]]] < remaining[status[row[0]]]))
        pivot = min((tuple(row for row in allowed if row[0] == left_id)
                     for left_id, count in enumerate(left_counts) if count), key=len)
        for edge in vertices(needed):
            here = tuple(row for row in allowed if row[2] >> edge & 1)
            if len(here) < len(pivot):
                pivot = here
        for left_id, right_id, witnessed in sorted(pivot, key=lambda row: -(row[2] & needed).bit_count()):
            first, second, next_quotas = map(list, (left_counts, right_counts, quotas))
            first[left_id] -= 1
            second[right_id] -= 1
            next_quotas[status[left_id]] -= binary[right_id]
            if search(tuple(first), tuple(second), tuple(next_quotas), needed & ~witnessed):
                return True
        return False

    try:
        return search(left_counts, right_counts, quotas, needed), nodes
    except OverflowError:
        return None, nodes


def literal(left, right, width):
    counts, covered = [0] * 4, 0
    for first, second in zip(left, right, strict=True):
        counts[first >> (width - 2)] += second >> (width - 1)
        covered |= cross_mask(first, second, width)
    return tuple(counts), covered


def control():
    rng = Random(314168)
    counts = Counter()
    for _ in range(1400):
        length = rng.randrange(1, 7)
        left, right = (rng.choices(range(1, 7), k=length) for _ in range(2))
        quotas, needed = literal(left, right, 3)
        needed = (needed | (1 << rng.randrange(1, 9) if rng.getrandbits(1) else 0)) & ~1
        expect = False
        for order in set(permutations(right)):
            if any(first & second & 1 for first, second in zip(left, order, strict=True)):
                continue
            counts0, covered = literal(left, order, 3)
            if counts0 == quotas and not needed & ~covered:
                expect = True
                break
        got, _ = solve(left, right, quotas, needed, 3)
        assert got == expect
        counts[got] += 1
    print('literal width3 controls', sorted(counts.items()), flush=True)


def task(adj, degree, arm_a, arm_b, centre, leaf, triple, holes_b):
    order = len(adj)
    cross_a, cross_b = cross_edge(adj, arm_a, arm_b)
    layout_a = (cross_a, *vertices(arm_a & ~mask((centre, cross_a))), centre, order)
    layout_b = (cross_b, *vertices(arm_b ^ (1 << cross_b)), order + 1)
    holes_a = (mask((centre, cross_a)), mask((centre, leaf)))
    outside = tuple(vertices(((1 << order) - 1) ^ arm_a ^ arm_b))
    rem_a = remnant(capacity(arm_a | 1 << order, holes_a), take(adj, outside, arm_a))
    rem_b = remnant(capacity(arm_b | 1 << (order + 1), holes_b), take(adj, outside, arm_b))
    assert rem_a is not None and rem_b is not None

    def project(row, labels):
        return mask(index for index, label in enumerate(labels) if row >> label & 1)

    seen = 0
    for vertex in outside:
        seen |= cross_mask(project(adj[vertex], layout_a), project(adj[vertex], layout_b), 5)
    assert not seen & 1
    left = [project(row, layout_a) for row in rem_a.elements()]
    right = [project(row, layout_b) for row in rem_b.elements()]
    assert len(left) == len(right) == 36 - order
    return left, right, (1, degree - 7 - triple, 5, triple), ((1 << 25) - 2) & ~seen, 5


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('maps', type=Path)
    parser.add_argument('windows', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    control()
    source, results, counts, kept = {}, {}, Counter(), set()
    for line in args.windows.read_text().splitlines():
        row, first, second, encoded = line.split()
        source[(row, *sorted(map(int, (first, second))))] = parse_graph6(encoded)
    with args.output.open('w') as output:
        for line in args.maps.read_text().splitlines()[:args.limit]:
            original, tag, triple, degree, row, first, second, centre, leaf, shape, hole, peer, _ = line.split()
            key = tuple(line.split()[1:-1])
            if key not in results:
                arm_a, arm_b = map(int, (first, second))
                proposal = task(source[(row, *sorted((arm_a, arm_b)))], int(degree), arm_a, arm_b, int(centre),
                                int(leaf), int(triple), tuple(map(int, (hole, peer))))
                results[key] = solve(*proposal)
                counts[degree, tag, str(results[key][0])] += 1
            status, nodes = results[key]
            if status is not False:
                kept.add((original, tag))
            print(status, nodes, line, sep='\t', file=output)
    print('rooted counts', sorted(counts.items()), 'nodes', sum(nodes for _, nodes in results.values()))
    print('remaining IDs', sorted(Counter((key.split('_')[3], tag) for key, tag in kept).items()),
          'union', len({key for key, _ in kept}))


if __name__ == '__main__':
    main()
