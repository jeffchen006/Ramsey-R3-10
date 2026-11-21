"""Direct 3x3 enumeration of the P3 diagonal-five high-edge boundary."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, permutations, product


def matches(neighbourhoods):
    return any(all(neighbourhoods[slot] >> vertex & 1 for slot, vertex in enumerate(order))
               for order in permutations(range(3)))


def move(mask, order):
    return sum(1 << new for old, new in enumerate(order) if mask >> old & 1)


def orbit_key(rows, left_full, right_full, private):
    return min((sum(move(row, right) << (3 * left[index]) for index, row in enumerate(rows)),
                move(left_full, left), move(right_full, right),
                tuple(sorted((move(left_mask, left), move(right_mask, right))
                             for left_mask, right_mask in private)))
               for left, right in product(permutations(range(3)), repeat=2))


def boundary_graph(key):
    pattern, left_mask, right_mask, private = key
    neighbours = [set() for _ in range(18)]

    def edge(left, right):
        neighbours[left].add(right)
        neighbours[right].add(left)

    for root, adjacent in ((15, [0, 1, 2, *range(6, 12)]), (16, range(6, 15)),
                           (17, [3, 4, 5, *range(6, 11), 12])):
        for other in adjacent:
            edge(root, other)
    for left, right in product(range(3), repeat=2):
        if pattern >> (3 * left + right) & 1:
            edge(left, 3 + right)
    for outside, pair in [(11, (0, right_mask)), (12, (left_mask, 0)),
                          (13, private[0]), (14, private[1])]:
        for side, mask in enumerate(pair):
            for wing in range(3):
                if mask >> wing & 1:
                    edge(outside, side * 3 + wing)
    return neighbours


def independent_of_size(graph, available, count):
    if not count:
        return True
    while len(available) >= count:
        vertex = min(available)
        available.remove(vertex)
        if independent_of_size(graph, available - graph[vertex], count - 1):
            return True
    return False


def boundary_test(key):
    graph = boundary_graph(key)
    if any(len(graph[left] & graph[right]) > 6 for left, right in combinations(range(18), 2)):
        return 'codegree'
    for left_count, right_count in ((3, 6), (4, 5)):
        if any(len(set.intersection(*(graph[vertex] for vertex in part))) >= right_count
               for part in combinations(range(18), left_count)):
            return 'biclique'
    if independent_of_size(graph, set(range(18)), 10):
        return 'alpha'
    return 'pass'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--min-f', type=int, choices=[18, 19], default=19)
    args = parser.parse_args()
    counts = Counter()
    orbits = defaultdict(set)
    for pattern in range(1 << 9):
        rows = [(pattern >> (3 * index)) & 7 for index in range(3)]
        valid_mixed = [(first, second) for first, second in product(range(1, 8), repeat=2)
                       if all(not (second & row) for index, row in enumerate(rows) if first >> index & 1)]
        size = pattern.bit_count()
        if not valid_mixed or size + 6 + 2 * max(first.bit_count() + second.bit_count()
                                                  for first, second in valid_mixed) < args.min_f:
            continue
        for (left_first, right_first), (left_second, right_second) in combinations_with_replacement(valid_mixed, 2):
            used = size + sum(mask.bit_count() for mask in (left_first, right_first, left_second, right_second))
            if used + 6 < args.min_f:
                continue
            for left_full, right_full in product(range(1, 8), repeat=2):
                total = used + left_full.bit_count() + right_full.bit_count()
                if total < args.min_f or not matches([left_full, left_first, left_second]) or not matches([right_full, right_first, right_second]):
                    continue
                if any(first.bit_count() + second.bit_count() >= 5 for first, second in valid_mixed):
                    continue
                counts[total] += 1
                orbits[total].add(orbit_key(rows, left_full, right_full,
                                          ((left_first, right_first), (left_second, right_second))))
                if total == 18:
                    continue
                assert total == 19 and left_full == right_full == 7
                assert left_first == left_second and right_first == right_second
                assert left_first.bit_count() == right_first.bit_count() == 2
                assert all(((mask & right_first) == 0 and mask | right_first == 7) if left_first >> index & 1
                           else mask == 7 for index, mask in enumerate(rows))
    assert {total: count for total, count in counts.items() if total >= 19} == {19: 9}
    assert len(orbits[19]) == 1
    print('PASS all 512 wing patterns with both Hall matchings and no independent wing five-set:', dict(counts))
    for total, keys in sorted(orbits.items()):
        print('f', total, 'orbits', len(keys), 'keys', sorted(keys))
        print('fixed boundary tests', dict(Counter(boundary_test(key) for key in keys)),
              'kept', sorted(key for key in keys if boundary_test(key) == 'pass'))


if __name__ == '__main__':
    main()
