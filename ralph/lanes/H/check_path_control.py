"""Check the window identities at all 42 oriented J-paths in C21(1,4,6)."""

from itertools import combinations, product


def check_path(neighbors, roots, block_size):
    vertices = set(neighbors)
    first, mid_left, mid_right, last = roots[:4]
    assert all(len(neighbors[left] & neighbors[right]) == 2 * block_size
               for left, right in zip(roots, roots[1:]))

    def remove(window, root):
        return window - neighbors[root] - {root}

    middle = remove(remove(vertices, mid_left), mid_right)
    left, right = middle & neighbors[last], middle & neighbors[first]
    assert len(left) == len(right) == block_size
    assert first in left and last in right and not (left & right)
    left_wing, right_wing = left - {first}, right - {last}
    overlap = middle - left - right
    assert len(overlap) == len(middle) - 2 * block_size
    assert remove(middle, first) == overlap | left_wing
    assert remove(middle, last) == overlap | right_wing

    if len(roots) == 5:
        extra = roots[4]
        second_middle = remove(remove(vertices, mid_right), last)
        triple = remove(middle, last)
        assert middle & second_middle == triple
        assert middle | second_middle == remove(vertices, mid_right)
        outer_left, outer_right = middle - triple, second_middle - triple
        assert outer_left == left_wing | {first, last}
        second_right_wing = (neighbors[mid_left] & second_middle) - {extra}
        assert outer_right == second_right_wing | {mid_left, extra}
        cross_edges = {(left_vertex, right_vertex)
                       for left_vertex, right_vertex in product(outer_left, outer_right)
                       if right_vertex in neighbors[left_vertex]}
        forced = ({(first, extra)} | {(first, right_vertex) for right_vertex in second_right_wing}
                  | {(left_vertex, extra) for left_vertex in left_wing})
        assert forced <= cross_edges <= forced | set(product(left_wing, second_right_wing))


def main():
    neighbors = {vertex: {(vertex + step) % 21 for step in (1, -1, 4, -4, 6, -6)}
                 for vertex in range(21)}
    assert all(not (neighbors[left] & neighbors[right]) for left, right in combinations(neighbors, 2)
               if right in neighbors[left])
    assert not any(all(right not in neighbors[left] for left, right in combinations(subset, 2))
                   for subset in combinations(neighbors, 7))
    for start, step in product(neighbors, (5, -5)):
        roots = tuple((start + step * index) % 21 for index in range(5))
        check_path(neighbors, roots[:4], 2)
        check_path(neighbors, roots, 2)
    try:
        check_path(neighbors, (0, 5, 10, 16), 2)
    except AssertionError:
        print("PASS: 42 P4 and 42 P5 controls; corrupted path rejected")
    else:
        raise AssertionError("corrupted path accepted")


if __name__ == "__main__":
    main()
