"""Check the P4 maximality bridge on small graphs, not on the P4 census."""

from collections import Counter
from itertools import combinations, product


def neighborhoods(order, edges):
    neighbors = [set() for _ in range(order)]
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return neighbors


def maximal_triangle_free(neighbors):
    return all(
        bool(neighbors[left] & neighbors[right]) == (right not in neighbors[left])
        for left, right in combinations(range(len(neighbors)), 2)
    )


def cross_window(neighbors, roots):
    first, mid_left, mid_right, last = roots
    assert last in neighbors[first]
    middle = set(range(len(neighbors))) - {mid_left, mid_right} - neighbors[mid_left] - neighbors[mid_right]
    y_wing = (middle & neighbors[last]) - {first}
    z_wing = (middle & neighbors[first]) - {last}
    overlap = middle - {first, last} - neighbors[first] - neighbors[last]
    covered = neighbors[mid_left] | neighbors[mid_right] <= neighbors[first] | neighbors[last]
    return covered, y_wing, z_wing, overlap


def check_side_rows(neighbors):
    roots = (0, 5, 10, 15)
    first, mid_left, mid_right, last = roots
    middle = set(range(len(neighbors))) - {mid_left, mid_right} - neighbors[mid_left] - neighbors[mid_right]
    _, y_wing, z_wing, overlap = cross_window(neighbors, roots)
    inner = neighbors[mid_left] & neighbors[mid_right]
    outside_left = neighbors[mid_left] - inner
    outside_right = neighbors[mid_right] - inner
    left_side = outside_left | (inner & neighbors[first])
    right_side = outside_right | (inner & neighbors[last])
    total = 0
    tight = 0
    for endpoint, root, side, outer, projected in (
        (first, mid_right, left_side, outside_left, overlap | y_wing),
        (last, mid_left, right_side, outside_right, overlap | z_wing),
    ):
        assert not (neighbors[root] & (outer | middle)) and (neighbors[root] & side)
        eligible = sorted(middle - {endpoint})
        for size in range(len(eligible) + 1):
            for base in combinations(eligible, size):
                if any(right in neighbors[left] for left, right in combinations(base, 2)):
                    continue
                available = {vertex for vertex in side if not neighbors[vertex].intersection(base)}
                assert available == {vertex for vertex in side if not neighbors[vertex] & (projected.intersection(base))}
                assert len(base) + len(available) <= 6
                strengthened = len(base) + len(available & outer) + 1
                assert strengthened <= 6
                tight += bool(available & outer) and strengthened == 6
                total += 1
    assert total > 0 and tight > 0
    print(f"PASS: C21 side rows on {total} independent subsets; {tight} tight outer rows with a nonempty available group")


def main():
    order = 21
    neighbors = neighborhoods(order, ((start, (start + step) % order)
                                      for start in range(order) for step in (1, 4, 6)))
    assert maximal_triangle_free(neighbors)
    check_side_rows(neighbors)
    counts = Counter()
    for start, step in product(range(order), (5, -5)):
        roots = tuple((start + step * offset) % order for offset in range(4))
        covered, y_wing, z_wing, overlap = cross_window(neighbors, roots)
        assert covered and (len(y_wing), len(z_wing), len(overlap)) == (1, 1, 7)
        for left, right in product(y_wing, z_wing):
            common = neighbors[left] & neighbors[right]
            edge = right in neighbors[left]
            assert common <= overlap and edge == (not common)
            counts[edge] += 1
    assert counts == {False: 42}

    neighbors = neighborhoods(10, ((start, (start + step) % 10)
                                      for start in range(10) for step in (1, 4)))
    roots, left, right = (0, 3, 8, 1), 5, 6
    covered, y_wing, z_wing, overlap = cross_window(neighbors, roots)
    assert maximal_triangle_free(neighbors) and covered
    assert left in y_wing and right in z_wing and right in neighbors[left]
    assert not (neighbors[left] & neighbors[right] & overlap)
    neighbors[left].remove(right)
    neighbors[right].remove(left)
    covered, y_wing, z_wing, overlap = cross_window(neighbors, roots)
    assert covered and left in y_wing and right in z_wing
    assert not maximal_triangle_free(neighbors) and not (neighbors[left] & neighbors[right] & overlap)

    extra = [(0, 5), (3, 5), (0, 6), (3, 6)]
    neighbors = neighborhoods(7, [(start, (start + 1) % 5) for start in range(5)] + extra)
    covered, y_wing, z_wing, overlap = cross_window(neighbors, (0, 5, 6, 1))
    assert maximal_triangle_free(neighbors) and not covered
    assert 2 in y_wing and 4 in z_wing and 4 not in neighbors[2]
    assert neighbors[2] & neighbors[4] == {3} and 3 not in overlap
    print("PASS: 42 oriented C21 P4 nonedges and one C10 cross edge")
    print("PASS: two countercontrols show the need for maximality and middle-neighborhood cover")


if __name__ == "__main__":
    main()
