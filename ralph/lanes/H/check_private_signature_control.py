"""Small exact controls for the independent-family and signature-equality bridges."""

from itertools import combinations


def subsets(vertices):
    return (frozenset(choice) for size in range(len(vertices) + 1)
            for choice in combinations(sorted(vertices), size))


def independent(neighbors, vertices):
    return all(not (vertices & neighbors[vertex]) for vertex in vertices)


def test_c13():
    vertices = frozenset(range(13))
    neighbors = [{(vertex + offset) % 13 for offset in (1, -1, 5, -5)} for vertex in vertices]
    alpha = max(len(choice) for choice in subsets(vertices) if independent(neighbors, choice))
    assert alpha == 4
    assert all(not (neighbors[first] & neighbors[second]) for first in vertices
               for second in neighbors[first])
    assert all(neighbors[first] & neighbors[second] for first, second in combinations(vertices, 2)
               if second not in neighbors[first])
    roots = pairs = inequalities = tight = 0
    for root in vertices:
        boundary = neighbors[root]
        exterior = vertices - boundary - {root}
        signature = {vertex: frozenset(neighbors[vertex] & boundary) for vertex in exterior}
        cells = {anchor: sum(value == {anchor} for value in signature.values()) for anchor in boundary}
        doubles = [value for value in signature.values() if len(value) == 2]
        degree = len(boundary)
        bound = alpha + 1 - degree
        degree_sum = sum(len(neighbors[anchor]) for anchor in boundary)
        assert degree_sum == degree + 2 * len(exterior) - degree * bound
        assert all(size == bound for size in cells.values())
        assert len(doubles) == len(exterior) - sum(cells.values())
        assert len(doubles) == len(set(doubles)) == 4
        roots += 1
        pairs += len(doubles)
        for block in subsets(boundary):
            for anchor in block:
                available = {vertex for vertex in exterior
                             if anchor in signature[vertex] and signature[vertex] <= block}
                for family in subsets(available):
                    assert independent(neighbors, family | (boundary - block))
                    lhs, rhs = len(family) + degree, alpha + len(block)
                    assert lhs <= rhs
                    inequalities += 1
                    tight += lhs == rhs
    print(f"PASS C13(1,5): alpha={alpha}, equality roots={roots}, doubles={pairs}, "
          f"family checks={inequalities}, tight={tight}")


def test_without_full_cell():
    vertices = frozenset(range(5))
    left, right = frozenset((0, 1)), frozenset((2, 3, 4))
    neighbors = [right if vertex in left else left for vertex in vertices]
    root = 2
    boundary = neighbors[root]
    exterior = vertices - {root} - boundary
    alpha = max(len(choice) for choice in subsets(vertices) if independent(neighbors, choice))
    signatures = [neighbors[vertex] & boundary for vertex in exterior]
    assert alpha == 3 and len(boundary) == 2 and len(exterior) == 2
    assert signatures[0] == signatures[1] == boundary
    assert not any(value == {0} for value in signatures)
    print("PASS K2,3 negative: distinct exterior vertices repeat a double signature with no full cell")


if __name__ == "__main__":
    test_c13()
    test_without_full_cell()
