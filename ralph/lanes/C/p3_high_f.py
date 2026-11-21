"""Small fixed boundary cover for both incident P3 pair counts high."""

import argparse
from collections import Counter
from itertools import combinations, permutations, product

from kernel_projection import bits
from p3_flexible import parts
from p3_round4_index import has_independent
from pair_packages import restrict
from path_three_top import connect, plant


NO_HOLE = (-1, -1)


def canonical(matrix, left, right, width):
    def mark(hole, order):
        return hole if hole == NO_HOLE else (order[hole[0]], hole[1])

    possibilities = []
    for rows, columns in product(permutations(range(width)), repeat=2):
        edges = [(rows[pos // width], columns[pos % width]) for pos in bits(matrix)]
        normal = sum(1 << (width * first + second) for first, second in edges)
        transpose = sum(1 << (width * second + first) for first, second in edges)
        if normal <= transpose:
            possibilities.append((normal, mark(left, rows), mark(right, columns)))
        if transpose <= normal:
            possibilities.append((transpose, mark(right, columns), mark(left, rows)))
    return min(possibilities)


def classify(degree, overlap, diagonal, key):
    left, right, common, only_left, only_right, only_middle, [root_left], [root_mid], [root_right] = parts(degree, overlap, diagonal)
    width = len(left)
    matrix, hole_left, hole_right = key
    graph = [0] * (root_right + 1)
    for root, neighbours in [(root_left, left+common+only_left), (root_mid, common+only_left+only_right+only_middle),
                              (root_right, right+common+only_right)]:
        for vertex in neighbours:
            connect(graph, root, vertex)
    for position in bits(matrix):
        connect(graph, left[position // width], right[position % width])
    for wing, ordinary, hole in [(left, only_right, hole_left), (right, only_left, hole_right)]:
        for index, vertex in enumerate(wing):
            for column, outer in enumerate(ordinary + only_middle):
                missing_column = 0 if hole[1] == 0 else len(ordinary)
                if hole == NO_HOLE or (index, column) != (hole[0], missing_column):
                    connect(graph, vertex, outer)
    return graph


def filter_target(graph):
    order = len(graph)
    if any(mask.bit_count() < 3 for mask in graph):
        return 'deficit'
    last_two = {(order - 3, order - 2), (order - 2, order - 1)}
    for first, second in combinations(range(order), 2):
        common = (graph[first] & graph[second]).bit_count()
        if common and graph[first] >> second & 1:
            return 'triangle'
        if common > 6:
            return 'codegree'
        if second >= order - 3 and not graph[first] >> second & 1:
            if common == 0 or (common == 6 and (first, second) not in last_two):
                return 'root-cap-Maximality'
    for size, limit in ((3, 6), (4, 5)):
        for side in combinations(range(order), size):
            common = (1 << order) - 1
            for vertex in side:
                common &= graph[vertex]
            if common.bit_count() >= limit:
                return 'biclique'
    if has_independent(graph, (1 << order) - 1, 10):
        return 'alpha'
    return 'pass'


def layouts(degree, overlap, diagonal, min_f, min_boundary, max_boundary):
    width = degree - overlap
    maximum = width * width
    assert min_f in (maximum - 1, maximum)
    central_private = degree - 2 * overlap + diagonal
    assert central_private <= 1
    marks = [NO_HOLE]
    if min_f < maximum:
        marks += list(product(range(width), range(central_private + 1)))
    result = set()
    for left, right in product(marks, repeat=2):
        arm_count = 2 * maximum - (left != NO_HOLE) - (right != NO_HOLE)
        for matrix in range(1 << maximum):
            size = arm_count + matrix.bit_count()
            if min_boundary <= size <= max_boundary:
                result.add((size, canonical(matrix, left, right, width)))
    return sorted(result)


def control():
    core, _, graph = plant()
    outside = list(range(len(core), len(graph)))
    roots = outside[-3:]
    groups = [[], [], [], [], [], [], [roots[0]], [roots[1]], [roots[2]]]
    features = {1: 0, 4: 1, 7: 2, 3: 3, 6: 4, 2: 5}
    for vertex in outside[:-3]:
        pattern = sum(1 << index for index, root in enumerate(roots) if graph[root] >> vertex & 1)
        groups[features[pattern]].append(vertex)
    assert list(map(len, groups)) == list(map(len, parts(6, 4, 2)))
    observed = None
    key_set = {key: classify(6, 4, 2, key) for _, key in layouts(6, 4, 2, 3, 9, 9)}
    for oriented in range(2):
        for left, right, left_centre, right_centre in product(*(permutations(groups[index]) for index in (0, 1, 3, 4))):
            first, middle, last = roots
            order = (list(left) + list(right) + groups[2] + list(left_centre) + list(right_centre) + [first, middle, last]
                     if not oriented else list(right) + list(left) + groups[2] + list(right_centre) + list(left_centre) + [last, middle, first])
            boundary = restrict(graph, order)
            if boundary in key_set.values():
                observed = boundary
    assert observed is not None
    print('PASS planted C21 actual boundary lies in the cover at arm counts 3/3 and total 9')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump', action='store_true')
    args = parser.parse_args()
    control()
    for minimum, diagonal in product((9, 8), (3, 4)):
        occurrences = Counter()
        for total, key in layouts(9, 6, diagonal, minimum, 15, 19):
            status = filter_target(classify(9, 6, diagonal, key))
            occurrences[(total + 45, status)] += 1
            if args.dump:
                print('key', minimum, diagonal, total + 45, status, key)
        print('COVER min-f', minimum, 'diag', diagonal, sorted(occurrences.items()))


if __name__ == '__main__':
    main()
