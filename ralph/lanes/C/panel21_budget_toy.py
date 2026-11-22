#!/usr/bin/env python3
"""Exact enumeration of two order-13 fixtures; no inputs or dependencies."""

from collections import Counter
from itertools import chain, combinations


VERTICES = frozenset(range(13))
CORE = (6, 11, 9, 4)
POLES = (0, 2)
GROUPS = ((5, 8, 12), (3, 7, 10))


def edge(first, second):
    return tuple(sorted((first, second)))


def incident(edges, vertex):
    return {second if vertex == first else first
            for first, second in edges if vertex in (first, second)}


def pair_test(vertices, edges, order, adjacent):
    return any(all((edge(*pair) in edges) == adjacent
                   for pair in combinations(subset, 2))
               for subset in combinations(sorted(vertices), order))


SCAFFOLD = {(1, 6), (1, 9), (6, 11), (4, 9), (0, 1), (1, 2)} | {
    edge(pole, singleton)
    for pole, group in zip(POLES, GROUPS) for singleton in group
}
PRESCRIBED = SCAFFOLD | {(5, 6), (11, 12)}
POSITIVE_FORBIDDEN = {(9, 12)}
NEGATIVE_FORBIDDEN = POSITIVE_FORBIDDEN | {(4, 12)}
CAPACITY = tuple(4 - len(incident(PRESCRIBED, vertex)) for vertex in CORE)


def rows_to_edges(rows):
    return {edge(vertex, site) for vertex, row in zip(CORE, rows) for site in row}


def graph_control(edges, forbidden, max_independence):
    assert PRESCRIBED <= edges and not (forbidden & edges)
    assert [len(incident(edges, site)) for site in sorted(VERTICES)] == [4] * 13
    assert not pair_test(VERTICES, edges, 3, True)
    assert pair_test(VERTICES, edges, max_independence, False)
    assert not pair_test(VERTICES, edges, max_independence + 1, False)
    assert incident(edges, 1) == {0, 2, 6, 9}
    for pole, group in zip(POLES, GROUPS):
        assert incident(edges, pole) == set(group) | {1}


def card_profiles(pole, group, forbidden):
    vertices = set(CORE) | {pole} | set(group)
    fixed = {pair for pair in PRESCRIBED if set(pair) <= vertices}
    possible = tuple(sorted({edge(site, singleton)
                             for site in CORE for singleton in group}))
    required = fixed & set(possible)
    skeleton = fixed - required
    bound = Counter()
    balanced = Counter()
    literal_balanced_crosses = set()
    for chosen in chain.from_iterable(combinations(possible, size)
                                     for size in range(len(possible) + 1)):
        crosses = frozenset(chosen)
        if not required <= crosses or forbidden & crosses:
            continue
        restored = skeleton | crosses
        added = crosses - required
        degrees = tuple(len(incident(added, site)) for site in CORE)
        if any(degree > capacity for degree, capacity in zip(degrees, CAPACITY)):
            continue
        if any(len(incident(restored, site)) > 4 for site in group):
            continue
        literal = (not pair_test(vertices, restored, 3, True)
                   and not pair_test(vertices, restored, 4, False))
        rows = {site: incident(crosses, site) for site in CORE}
        shortcut = all(rows.values()) and all(
            not (rows[first] & rows[second]) if edge(first, second) in SCAFFOLD
            else len(rows[first] | rows[second]) >= 2
            for first, second in combinations(CORE, 2)
        )
        assert literal == shortcut
        if literal:
            bound[degrees] += 1
            if len(crosses) == 5:
                balanced[degrees] += 1
                literal_balanced_crosses.add(crosses)
    return bound, balanced, literal_balanced_crosses


def compare(label, forbidden, controls):
    print(f"{label}: core={CORE} residual={CAPACITY}")
    added_minima = []
    for pole, group, control in zip(POLES, GROUPS, controls):
        bound, balanced, crosses = card_profiles(pole, group, forbidden)
        assert frozenset(control) in crosses
        minimum = tuple(map(min, zip(*balanced)))
        assert minimum == tuple(map(min, zip(*bound)))
        added_minima.append(minimum)
        print(f"  pole={pole} masks=4096 local={sum(bound.values())} "
              f"exact-five={sum(balanced.values())} profiles={len(balanced)} "
              f"min={minimum}")
    total = tuple(map(sum, zip(*added_minima)))
    overloads = tuple(site for site, amount, capacity in zip(CORE, total, CAPACITY)
                      if amount > capacity)
    print(f"  sum minima={total} overloads={overloads}")
    return total, overloads


def main():
    planted = {edge(site, (site + offset) % 13)
               for site in VERTICES for offset in (1, 5)}
    graph_control(planted, POSITIVE_FORBIDDEN, 4)
    assert planted & NEGATIVE_FORBIDDEN == {(4, 12)}
    planted_rows = [rows_to_edges([incident(planted, site) & set(group) for site in CORE])
                    for group in GROUPS]
    added = (planted_rows[0] | planted_rows[1]) - PRESCRIBED
    assert tuple(len(incident(added, site)) for site in CORE) == CAPACITY
    positive_minima, positive_overloads = compare(
        "plant", POSITIVE_FORBIDDEN, planted_rows,
    )
    assert not positive_overloads
    assert positive_minima[0] == CAPACITY[0] == 1
    assert positive_minima[0] + 1 > CAPACITY[0]
    print("  mutant counting prescribed 5-6 again would reject the plant")

    degree_only = PRESCRIBED | rows_to_edges(((5, 10), (8, 12, 7), (5, 3), (8, 7, 10))) | {
        (3, 8), (3, 12), (10, 12), (5, 7),
    }
    graph_control(degree_only, NEGATIVE_FORBIDDEN, 5)
    assert not any(edge(*pair) in degree_only for pair in combinations((2, 6, 8, 9, 12), 2))
    witnesses = [rows_to_edges(((5, 8), (12,), (5,), (8,))),
                 rows_to_edges(((3,), (7,), (3, 7), (10,)))]
    negative_minima, negative_overloads = compare("strict", NEGATIVE_FORBIDDEN, witnesses)
    assert negative_overloads == (6,)
    assert negative_minima[0] == 2 > CAPACITY[0]
    print("PASS: strict card degree coupling, degree-only witness, and one-pin plant")


if __name__ == "__main__":
    main()
