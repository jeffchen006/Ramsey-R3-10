"""Literal smaller-graph and equal-mask controls for FoldedSlot.lean."""

from itertools import combinations, permutations, product


def neighbors(order, pairs):
    graph = [set() for site in range(order)]
    for first, second in pairs:
        assert first != second
        graph[first].add(second)
        graph[second].add(first)
    assert all(not (row & graph[other]) for row in graph for other in row)
    return graph


def board(graph, first_root, second_root):
    left = graph[first_root] - {second_root}
    right = graph[second_root] - {first_root}
    assert not left & right
    exterior = set(range(len(graph))) - left - right - {first_root, second_root}
    masks = {site: (graph[site] & left, graph[site] & right) for site in exterior}
    grid = tuple(sorted(site for site, pair in masks.items() if tuple(map(len, pair)) == (1, 1)))
    return masks, grid, tuple(sorted(exterior - set(grid)))


def is_partial_matching(selected):
    return all(len({pair[side] for pair in selected}) == len(selected) for side in range(2))


def check_board(graph, masks, grid, left, right):
    assert len(left) == len(right) == len(set(left)) == len(set(right))
    assert set(left) == set(right) and not set(left) & set(grid)
    inactive = len(left)
    slots = (left + (None,), right + (None,))
    selected = {(left.index(site), right.index(site)) for site in left}
    assert is_partial_matching(selected)
    assert len({left[left_slot] for left_slot, right_slot in selected}) == len(selected)
    assert len({right[right_slot] for left_slot, right_slot in selected}) == len(selected)
    edges = []
    for side in range(2):
        active = {pair[side] for pair in selected}
        edges.append({(slot, copy): (slot in active and not (masks[site][side] & masks[copy][side])
                                     and copy in graph[site])
                      for slot, site in enumerate(slots[side]) for copy in grid})
        assert not any(edges[side][inactive, copy] for copy in grid)
    stats = [0, 0, 0, 0]
    for left_slot, right_slot in product(range(inactive + 1), repeat=2):
        for copy in grid:
            left_bit, right_bit = edges[0][left_slot, copy], edges[1][right_slot, copy]
            if (left_slot, right_slot) not in selected:
                stats[3] += left_bit != right_bit
                continue
            assert left[left_slot] == right[right_slot]
            site = left[left_slot]
            assert left_bit == right_bit == (copy in graph[site])
            stats[0] += 1
            stats[1] += left_bit
            overlap = tuple(bool(masks[site][side] & masks[copy][side]) for side in range(2))
            stats[2] += overlap[0] != overlap[1]
    return tuple(stats)


def circulant_control():
    order = 13
    graph = neighbors(order, ((site, (site + step) % order) for site in range(order) for step in (1, 5)))
    assert all(len(row) == 4 for row in graph)

    def independent(sites):
        return all(second not in graph[first] for first, second in combinations(sites, 2))

    assert any(map(independent, combinations(range(order), 4)))
    assert not any(map(independent, combinations(range(order), 5)))
    totals = [0, 0, 0, 0]
    marks = 0
    for first, second in product(range(order), repeat=2):
        if second not in graph[first]:
            continue
        masks, grid, slots = board(graph, first, second)
        stats = check_board(graph, masks, grid, slots, tuple(reversed(slots)))
        totals = [total + value for total, value in zip(totals, stats)]
        marks += 1
    assert marks == 52 and all(totals)
    print(f"C13(1,5) alpha=4, oriented root marks={marks}: "
          f"selected/true/asymmetric/unguarded-differences={totals}")


def duplicate_control():
    first_slot, second_slot = 8, 9
    first_copy, second_copy, clash_copy = 10, 11, 12
    graph = neighbors(13, [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (1, 6), (1, 7),
                           *((site, anchor) for site in (first_slot, second_slot) for anchor in (2, 3, 5, 6)),
                           *((copy, anchor) for copy in (first_copy, second_copy) for anchor in (4, 7)),
                           (clash_copy, 2), (clash_copy, 7), (first_slot, first_copy), (second_slot, second_copy)])
    masks, grid, slots = board(graph, 0, 1)
    assert masks[first_slot] == masks[second_slot] and slots == (first_slot, second_slot)
    assert masks[first_copy] == masks[second_copy] and grid == (first_copy, second_copy, clash_copy)
    assert [copy in graph[first_slot] for copy in grid] == [True, False, False]
    assert [copy in graph[second_slot] for copy in grid] == [False, True, False]
    assert not is_partial_matching({(0, 0), (0, 1)})
    assert not is_partial_matching({(0, 0), (1, 0)})
    lifts = 0
    for left, right, copies in product(permutations(slots), permutations(slots), permutations(grid)):
        observed = check_board(graph, masks, copies, left, right)
        assert observed == (6, 2, 2, 8), observed
        lifts += 1
    print(f"duplicate masks: {lifts} labellings; equal full supports but different grid rows; "
          "shared-left-only clash, inactive guards and reused slots checked")


def slot_edge_control():
    graph = neighbors(13, [(0, 1), *((0, anchor) for anchor in range(2, 6)),
                           *((1, anchor) for anchor in range(6, 10)),
                           (10, 2), (10, 3), (10, 6), (11, 4), (11, 5), (11, 7),
                           (12, 2), (12, 5), (12, 8), (10, 11)])
    masks, grid, sites = board(graph, 0, 1)
    assert not grid and sites == (10, 11, 12)
    labels = 0
    for left, right in product(permutations(sites), repeat=2):
        selected = {(left.index(site), right.index(site)) for site in sites}
        assert is_partial_matching(selected)
        for first, second in combinations(sorted(selected), 2):
            site_pair = left[first[0]], left[second[0]]
            assert site_pair == (right[first[1]], right[second[1]])
            start, end = site_pair
            edge = end in graph[start]
            folded = [not (masks[start][side] & masks[end][side]) and edge for side in range(2)]
            assert folded == [edge, edge]
            assert ((not (masks[start][0] & masks[end][0])) == edge and
                    not (masks[start][1] & masks[end][1]))
        labels += 1
    print(f"slot/slot: {labels} labellings; one positive edge, two asymmetric clashes per labelling")


if __name__ == "__main__":
    circulant_control()
    duplicate_control()
    slot_edge_control()
