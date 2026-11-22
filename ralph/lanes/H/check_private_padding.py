"""Direct adjacency and subset checks for the physical two-anchor padding."""

from itertools import combinations


def edge(first, second):
    return frozenset((first, second))


def independent(edges, sites):
    return all(edge(first, second) not in edges for first, second in combinations(sites, 2))


def alpha(edges, sites):
    for size in range(len(sites), -1, -1):
        if any(independent(edges, subset) for subset in combinations(sites, size)):
            return size
    raise AssertionError("the empty set is independent")


def neighbors(edges, site):
    return {next(iter(pair - {site})) for pair in edges if site in pair}


def matching(edges, left, right):
    if not left:
        return 0
    site, remaining = left[0], left[1:]
    return max(
        [matching(edges, remaining, right)]
        + [1 + matching(edges, remaining, right - {anchor}) for anchor in right
           if edge(site, anchor) in edges]
    )


def physical_row(degree, width, matches, crossed, mutate=False):
    root, row, peer = 0, 1, 2
    anchors = set(range(1, degree + 1))
    left = tuple(range(degree + 1, degree + width + 1))
    right = tuple(range(degree + width + 1, degree + 2 * width + 1))
    cross = degree + 2 * width + 1
    all_sites = set(left + right) | {cross}
    edges = {edge(root, anchor) for anchor in anchors}
    edges |= {edge(row, site) for site in left} | {edge(peer, site) for site in right}
    edges |= {edge(left[index], right[index]) for index in range(matches)}
    edges |= {edge(peer, cross), edge(row if crossed else 3, cross)}
    if not crossed:
        edges.add(edge(cross, left[-1]))
    if mutate:
        edges.add(edge(3, left[-1]))

    vertices = anchors | all_sites | {root}
    assert not any(all(edge(first, second) in edges for first, second in combinations(triple, 2))
                   for triple in combinations(vertices, 3))
    actual_anchors = neighbors(edges, root)
    opposite_anchors = neighbors(edges, peer) - {root}
    assert actual_anchors == anchors and opposite_anchors - {cross} == set(right)
    assert {(anchor, site) for anchor in anchors - {peer} for site in opposite_anchors
            if edge(anchor, site) in edges} == {(row if crossed else 3, cross)}
    contacts = {site: neighbors(edges, site) & actual_anchors for site in all_sites}
    assert {site for site in all_sites if contacts[site] == {row}} == (
        set(left) - {left[-1]} if mutate else set(left))
    assert {site for site in all_sites if contacts[site] == {peer}} == set(right)
    isolated = {site for site in all_sites if contacts[site] == {row, peer}}
    assert isolated == ({cross} if crossed else set())

    local = set(left + right) | isolated
    unused = actual_anchors - {row, peer}
    assert len(unused) == degree - 2 and not unused & local
    assert independent(edges, unused) and independent(edges, left) and independent(edges, right)
    assert not any(edge(site, other) in edges for site in isolated for other in local)
    assert {site for site in local if neighbors(edges, site) & unused} == (
        {left[-1]} if mutate else set())
    global_value = alpha(edges, vertices)
    local_value = alpha(edges, local)
    match_value = matching(edges, left, set(right))
    assert global_value == width + degree - 1
    assert local_value == width + 1 + int(mutate)
    assert match_value == width - 1 + int(crossed) - int(mutate)
    if not mutate:
        labels = [neighbors(edges, site) & neighbors(edges, peer) for site in left]
        assert all(len(label) == 1 for label in labels)
        occupied_noncross = set.union(*labels) - {cross}
        assert len(left) - len(occupied_noncross) == 1 - int(crossed)
        padded = 0
        for size in range(len(local) + 1):
            for subset in combinations(local, size):
                if independent(edges, subset):
                    assert independent(edges, set(subset) | unused)
                    padded += 1
        assert local_value + len(unused) == global_value
    else:
        witness = {left[-1], *right, *isolated}
        assert len(witness) == local_value and independent(edges, witness)
        assert not independent(edges, witness | unused)
        padded = 0
    print(f"degree={degree} cross={int(crossed)} extra_contact={int(mutate)}: "
          f"global={global_value} local={local_value} matching={match_value} padded={padded}")


def c13_controls():
    vertices = set(range(13))
    edges = {edge(site, (site + step) % 13) for site in vertices for step in (1, 5)}
    assert alpha(edges, vertices) == 4
    assert all(independent(edges, neighbors(edges, site)) for site in vertices)
    pairs = 0
    tight = 0
    for root in vertices:
        anchors = neighbors(edges, root)
        exterior = vertices - {root} - anchors
        for first, second in combinations(anchors, 2):
            local = {site for site in exterior if neighbors(edges, site) & anchors <= {first, second}}
            unused = anchors - {first, second}
            for size in range(len(local) + 1):
                for positions in combinations(local, size):
                    if independent(edges, positions):
                        assert independent(edges, set(positions) | unused)
                        assert size + len(unused) <= 4
            tight += alpha(edges, local) + len(unused) == 4
            pairs += 1
    assert pairs == 78 and tight > 0
    print(f"C13(1,5): alpha=4; {pairs} pairs, {tight} tight")


if __name__ == "__main__":
    c13_controls()
    for degree, width in ((4, 2), (6, 4)):
        physical_row(degree, width, width - 1, crossed=False)
        physical_row(degree, width, width, crossed=True)
        physical_row(degree, width, width - 1, crossed=True, mutate=True)
