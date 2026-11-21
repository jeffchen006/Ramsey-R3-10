"""Boundary-only exact cover and filters for lower diagonal-five strata."""

import argparse
from collections import Counter
from itertools import combinations_with_replacement, product

from p3_e63 import reflect
from verify_p3_boundary import boundary_graph, boundary_test, matches, orbit_key


def keys_at(target):
    choices = set()
    labelled = 0
    boundary_slots = [(left, right, left.bit_count() + right.bit_count())
                      for left, right in product(range(1, 8), repeat=2)]
    for pattern in range(512):
        rows = [(pattern >> (3 * index)) & 7 for index in range(3)]
        mixed = [(left, right, count) for left, right, count in boundary_slots
                 if all(not row & right for index, row in enumerate(rows) if left >> index & 1)]
        if any(count >= 5 for _, _, count in mixed):
            continue
        for (left_a, right_a, a_count), (left_b, right_b, b_count) in combinations_with_replacement(mixed, 2):
            need = target - pattern.bit_count() - a_count - b_count
            if not 2 <= need <= 6:
                continue
            for left, right, count in boundary_slots:
                if count == need and matches((left, left_a, left_b)) and matches((right, right_a, right_b)):
                    labelled += 1
                    choices.add(orbit_key(rows, left, right, ((left_a, right_a), (left_b, right_b))))
    return labelled, sorted(choices)


def filter_boundary(key):
    graph = boundary_graph(key)
    for root in range(15, 18):
        for outer in range(15):
            if outer in graph[root]:
                continue
            common = len(graph[root] & graph[outer])
            if not 1 <= common <= 5:
                return 'root-maximality-or-cap'
    if any(len(row) < 3 for row in graph):
        return 'deficit-above-6'
    return boundary_test(key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edges', type=int, nargs='+', default=[63, 62, 61, 60])
    parser.add_argument('--dump', action='store_true')
    args = parser.parse_args()
    for edges in args.edges:
        labelled, keys = keys_at(edges - 45)
        once = [key for key in keys if key <= reflect(key)]
        assert all(reflect(key) in keys and reflect(reflect(key)) == key for key in keys)
        statuses = Counter(filter_boundary(key) for key in once)
        if edges == 63:
            assert (labelled, len(keys), len(once)) == (234, 13, 8)
        print('edges', edges, 'labelled', labelled, 'ordered-orbits', len(keys),
              'unoriented-orbits', len(once), 'filters', dict(statuses))
        if args.dump:
            for key_id, key in enumerate(once):
                print('key', edges, key_id, filter_boundary(key), key)


if __name__ == '__main__':
    main()
