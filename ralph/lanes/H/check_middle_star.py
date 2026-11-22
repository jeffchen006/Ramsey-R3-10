"""Literal smaller controls for the middle-star edge and incidence identities."""

from itertools import combinations, product


def physical_controls():
    labels = tuple(map(frozenset, combinations(range(5), 2)))
    vertices = set(range(len(labels)))
    edges = {
        (first, second) for first, second in combinations(vertices, 2)
        if labels[first].isdisjoint(labels[second])
    }
    assert len(vertices) == 10 and len(edges) == 15
    neighbors = {
        vertex: {next(iter(set(edge) - {vertex})) for edge in edges if vertex in edge}
        for vertex in vertices
    }
    assert all(len(sites) == 3 for sites in neighbors.values())
    assert all(not (neighbors[first] & neighbors[second]) for first, second in edges)
    independent_count = lambda size: sum(
        all(edge not in edges for edge in combinations(group, 2))
        for group in combinations(sorted(vertices), size)
    )
    assert (independent_count(4), independent_count(5)) == (5, 0)

    def inside(sites):
        return sum(set(edge) <= sites for edge in edges)

    def between(left, right):
        assert left.isdisjoint(right)
        return sum(
            (first in left and second in right) or (first in right and second in left)
            for first, second in edges
        )

    paths = mutations = 0
    for left, right in product(vertices, repeat=2):
        if left == right or right in neighbors[left]:
            continue
        shared = neighbors[left] & neighbors[right]
        assert len(shared) == 1
        middle, = shared
        wing_left, wing_right = neighbors[left] - shared, neighbors[right] - shared
        star = neighbors[middle] - {left, right}
        book = {left, right, middle} | wing_left | wing_right
        untouched = vertices - ({left, right, middle} | neighbors[left] | neighbors[right] | neighbors[middle])
        assert untouched == vertices - book - star
        zones = ({left, right, middle}, wing_left, wing_right, star, untouched)
        assert tuple(map(len, zones)) == (3, 2, 2, 1, 2)
        assert len(set.union(*zones)) == sum(map(len, zones)) == 10
        petals = between(wing_left, wing_right)
        residue_edges = inside(untouched)
        rest = vertices - book
        assert (petals, residue_edges) == (2, 0)
        assert inside(book) == 2 * 3 + petals and inside(star) == 0
        assert 2 * (inside(rest) - inside(book)) == 3 * (len(rest) - len(book))
        assert between(star, untouched) == inside(rest) - residue_edges == 2
        for vertex in star:
            assert tuple(len(neighbors[vertex] & zone) for zone in zones[1:]) == (0, 0, 0, 2)
            assert len(neighbors[vertex] & neighbors[left]) == len(neighbors[vertex] & neighbors[right]) == 1
        for vertex in untouched:
            assert len(neighbors[middle] & neighbors[vertex]) == len(star & neighbors[vertex]) == 1

        changed = {vertex: set(sites) for vertex, sites in neighbors.items()}
        pole, = star
        hole = min(untouched)
        changed[pole].remove(hole)
        changed[hole].remove(pole)
        assert len(changed[pole]) < 3 and len(changed[hole] & changed[middle]) == 0
        assert sum(len(changed[vertex] & untouched) for vertex in star) == 1
        paths += 1
        mutations += 1
    assert (paths, mutations) == (60, 60)
    print("PASS Petersen KG(5,2): (n,e,alpha)=(10,15,4); 60 ordered deficient paths, 60 failed contact deletions")

    middle = min(vertices)
    clones = {(vertex, clone) for vertex in vertices for clone in range(1 if vertex == middle else 2)}
    blown = {clone: {target for target in clones if target[0] in neighbors[clone[0]]} for clone in clones}
    assert all(
        not (blown[first] & blown[second]) if first in blown[second] else blown[first] & blown[second]
        for first, second in combinations(sorted(clones), 2)
    )
    marker = (middle, 0)
    left, right = sorted(neighbors[middle])[:2]
    assert blown[left, 0] & blown[right, 0] == {marker}
    assert all(len(blown[marker] & blown[vertex]) >= 2 for vertex in clones - {marker} - blown[marker])
    untouched = clones - {marker, (left, 0), (right, 0)} - blown[marker] - blown[left, 0] - blown[right, 0]
    assert len(untouched) == 4 and all(len(blown[marker] & blown[vertex]) == 2 for vertex in untouched)
    print("PASS 19-site Petersen blow-up: MTF, marked unique witness, no deficient endpoint at the middle, all 4 untouched codegrees exactly 2")


def incidence_controls():
    rows = tuple(combinations(range(4), 2))
    tight = rejected = 0
    for left, right in product(rows, repeat=2):
        columns = [int(column in left) + int(column in right) for column in range(4)]
        assert sum(columns) == 4
        if min(columns) >= 1:
            assert columns == [1] * 4
            tight += 1
        else:
            assert 2 in columns and 0 in columns
            rejected += 1
    assert (tight, rejected) == (6, 30)
    print("PASS 36 tight-row literal incidences: 6 floor-preserving, 30 countercontrols if the column floor is dropped")


if __name__ == "__main__":
    physical_controls()
    incidence_controls()
