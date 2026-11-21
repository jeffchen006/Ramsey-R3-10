"""Test center deletion on known smaller catalogues and rejected mutations."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from check_graph import alpha, parse_graph6, triangle_free


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def edges(adj, keep):
    return sum((adj[vertex] & keep).bit_count() for vertex in vertices(keep)) // 2


def subgraph(adj, keep):
    order = tuple(vertices(keep))
    return [sum(1 << col for col, other in enumerate(order) if adj[vertex] >> other & 1)
            for vertex in order]


def support_valid(adj, strip, exterior, private):
    supports = Counter(adj[vertex] & strip for vertex in vertices(exterior))
    return all(supports[1 << vertex] == private for vertex in vertices(strip)) and all(
        key.bit_count() == 1 or (key.bit_count() == 2 and value == 1)
        for key, value in supports.items())


def check(adj, alpha_cap):
    full = (1 << len(adj)) - 1
    dmax = max(neighbors.bit_count() for neighbors in adj)
    counts = Counter()
    for root, neighbors in enumerate(adj):
        for peer in vertices(neighbors):
            degree = neighbors.bit_count()
            if adj[peer].bit_count() != degree:
                continue
            private = alpha_cap + 1 - degree
            if private < 1:
                continue
            opposite = adj[root] ^ (1 << peer)
            strip = adj[peer] ^ (1 << root)
            exterior = full & ~(opposite | strip | 1 << root | 1 << peer)
            if not (support_valid(adj, neighbors, full & ~(neighbors | 1 << root), private)
                    and support_valid(adj, adj[peer], full & ~(adj[peer] | 1 << peer), private)):
                continue
            missing = [(first, second) for first, second in combinations(vertices(strip), 2)
                       if not (adj[first] & adj[second] & exterior)]
            if len(missing) != 2 or len(set(missing[0]) & set(missing[1])) != 1:
                continue
            center = next(iter(set(missing[0]) & set(missing[1])))
            lower = strip | exterior
            deleted = adj[center] & lower
            window = lower & ~(deleted | 1 << center)
            retained = strip ^ (1 << center)
            assert (deleted & strip) == 0
            assert deleted.bit_count() == private + degree - 4
            assert window.bit_count() == lower.bit_count() - 1 - deleted.bit_count()
            assert alpha(subgraph(adj, lower)) <= alpha_cap - 1
            assert alpha(subgraph(adj, window)) <= alpha_cap - 2
            assert triangle_free(subgraph(adj, window))
            assert all((adj[vertex] & window).bit_count() == private + degree - 3
                       for vertex in vertices(retained))
            assert support_valid(adj, retained, window & ~retained, private)
            witnesses = [adj[first] & adj[second] & window
                         for first, second in combinations(vertices(retained), 2)]
            assert all(mask.bit_count() == 1 for mask in witnesses)
            assert len(set(witnesses)) == len(witnesses)
            losses = [(adj[vertex] & opposite).bit_count() for vertex in vertices(deleted)]
            assert all(loss in (1, 2) for loss in losses)
            extra = sum(loss - 1 for loss in losses)
            deficit = sum(dmax - adj[vertex].bit_count() for vertex in vertices(deleted))
            assert edges(adj, window) == edges(adj, lower) - (dmax - 1) * deleted.bit_count() + extra + deficit
            counts[window.bit_count(), edges(adj, window)] += 1

            if not witnesses:
                continue
            witness = next(vertices(witnesses[0]))
            modified = adj.copy()
            modified[center] |= 1 << witness
            modified[witness] |= 1 << center
            assert not support_valid(modified, strip, exterior, private)
            assert not (modified[center] & witnesses[0] == 0)
            counts["rejected triple"] += 1
    return counts


def check_double_deletion(adj):
    full = (1 << len(adj)) - 1
    original_edges = edges(adj, full)
    counts = Counter()
    for first, second in combinations(range(len(adj)), 2):
        first_nbrs, second_nbrs = adj[first], adj[second]
        if first_nbrs >> second & 1:
            continue
        shared = first_nbrs & second_nbrs
        first_only = first_nbrs & ~shared
        second_only = second_nbrs & ~shared
        window = full & ~(first_nbrs | second_nbrs | 1 << first | 1 << second)
        removed_degrees = sum(adj[vertex].bit_count() for vertex in vertices(first_nbrs | second_nbrs))
        crossing = sum((adj[vertex] & second_only).bit_count() for vertex in vertices(first_only))
        assert edges(adj, window) == original_edges - removed_degrees + crossing
        counts["pairs"] += 1
        counts["crossing term necessary"] += crossing > 0
        counts["shared term necessary"] += bool(shared)
    assert all(counts.values()) and len(counts) == 3
    return counts


def check_support_weights():
    states = [(degree, own, opposite) for degree in (7, 8, 9) for own in (1, 2) for opposite in (1, 2)
              if max(own, opposite) <= degree - 6]
    costs = {state: state[2] - 1 + 9 - state[0] for state in states}
    assert min(costs.values()) == 0
    assert max(costs.values()) == 2
    assert max(cost for state, cost in costs.items() if state[0] == 9) == 1

    def max_window(no_eight):
        return 72 + sum(multiplicity * max(cost for state, cost in costs.items()
                                           if state[1] == own and (not no_eight or state[0] != 8))
                        for own, multiplicity in ((1, 4), (2, 2)))

    assert (max_window(False), max_window(True)) == (84, 82)
    print(f"target scalar control: {len(states)} feasible support/degree triples, caps 84 and 82")


def main():
    for order, r, file_count in ((12, 5, 12), (22, 7, 191)):
        rows = (ROOT / "gluing" / "val" / f"r3_{r}_{order}.g6").read_text().splitlines()
        assert len(rows) == file_count
        total, pair_totals = Counter(), Counter()
        for row in rows:
            adj = parse_graph6(row)
            assert len(adj) == order and triangle_free(adj) and alpha(adj) == r - 1
            total.update(check(adj, r - 1))
            pair_totals.update(check_double_deletion(adj))
        print(f"(3,{r};{order}): {file_count} validated rows; {dict(total)}", flush=True)
        print(f"double-deletion identity: {dict(pair_totals)}", flush=True)
        if order == 12:
            assert total == {(5, 5): 18, "rejected triple": 18}
    check_support_weights()


if __name__ == "__main__":
    main()
