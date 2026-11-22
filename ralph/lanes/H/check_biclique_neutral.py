"""Small literal controls for the antineighborhood count, not a frame census."""

from itertools import combinations


def edge(first, second):
    return frozenset((first, second))


def independent(vertices, edges):
    return all(edge(*pair) not in edges for pair in combinations(vertices, 2))


def triangle_free(vertices, edges):
    return all(any(edge(*pair) not in edges for pair in combinations(triple, 2))
               for triple in combinations(vertices, 3))


def graph_subsets(optional_edges):
    optional_edges = list(optional_edges)
    for mask in range(1 << len(optional_edges)):
        yield {pair for index, pair in enumerate(optional_edges) if (mask >> index) & 1}


def window(vertices, edges, roots):
    return {vertex for vertex in vertices - roots
            if all(edge(vertex, root) not in edges for root in roots)}


def check(vertices, edges, left, right):
    exterior = vertices - left - right
    left_window = window(vertices, edges, left)
    right_window = window(vertices, edges, right)
    neutral = {vertex for vertex in exterior if not any(
        vertex in pair and pair & (left | right) for pair in edges)}
    assert left_window | right_window == exterior
    assert left_window & right_window == neutral
    assert len(left_window) + len(right_window) == len(exterior) + len(neutral)
    if any(independent(selection, edges) for selection in combinations(vertices, 5)):
        return None
    for roots, induced in ((left, left_window), (right, right_window)):
        assert all(independent(roots | set(selection), edges)
                   for selection in combinations(induced, 2) if independent(selection, edges))
        assert not any(independent(selection, edges) for selection in combinations(induced, 3))
        assert len(induced) <= 5
    limit = 10 - len(exterior)
    assert len(neutral) <= limit
    assert (len(neutral) == limit) == (len(left_window) == len(right_window) == 5)
    return len(left_window), len(right_window), len(neutral)


def main():
    for order, expected in ((5, 12), (6, 0)):
        vertices = set(range(order))
        survivors = sum(triangle_free(vertices, edges) and not any(
            independent(triple, edges) for triple in combinations(vertices, 3))
            for edges in graph_subsets(edge(*pair) for pair in combinations(vertices, 2)))
        assert survivors == expected
        print(f"R(3,3) control: order {order}, {survivors} labelled alpha<=2 survivors")

    left, right = {0, 1}, {2, 3}
    crossings = {edge(first, second) for first in left for second in right}
    vertices = set(range(7))
    optional = [edge(*pair) for pair in combinations(vertices, 2) if set(pair) & {4, 5, 6}]
    passed = triangle_count = cap_miss = 0
    for extension in graph_subsets(optional):
        edges = crossings | extension
        if not triangle_free(vertices, edges):
            triangle_count += 1
            continue
        if check(vertices, edges, left, right) is None:
            cap_miss += 1
        else:
            passed += 1
    assert passed > 0 and cap_miss > 0 and triangle_count > 0
    print(f"Order 7: {passed} cap-valid plants, {cap_miss} alpha misses, {triangle_count} triangle misses")

    vertices = set(range(9))
    edges = crossings | {edge(4 + index, 4 + (index + 1) % 5) for index in range(5)}
    assert triangle_free(vertices, edges)
    assert check(vertices, edges, left, right) == (5, 5, 5)
    perturbed = edges | {edge(0, 4)}
    assert triangle_free(vertices, perturbed)
    assert check(vertices, perturbed, left, right) == (4, 5, 4)
    triangle = perturbed | {edge(2, 4)}
    assert not triangle_free(vertices, triangle)
    assert 4 not in window(vertices, triangle, left) | window(vertices, triangle, right)
    print("Order 9: tight (5,5,5), asymmetric (4,5,4), and mixed-touch triangle mutation")


if __name__ == "__main__":
    main()
