from itertools import combinations, product
from math import comb


def adjacency(vertices, edges):
    neighbors = {vertex: set() for vertex in vertices}
    for first, second in edges:
        assert first != second
        neighbors[first].add(second)
        neighbors[second].add(first)
    return neighbors


def literal_check(name, neighbors, degree, alpha, common_cap, saturated):
    assert {len(row) for row in neighbors.values()} == {degree}
    pairs = list(combinations(neighbors, 2))
    nonedges = [(first, second) for first, second in pairs if second not in neighbors[first]]
    assert all(not neighbors[first] & neighbors[second] for first, second in pairs if second in neighbors[first])
    common = [len(neighbors[first] & neighbors[second]) for first, second in nonedges]
    assert max(common) == common_cap
    assert (min(common) > 0) == saturated
    assert sum(common) == sum(comb(len(row), 2) for row in neighbors.values())

    def independent(sites):
        return all(second not in neighbors[first] for first, second in combinations(sites, 2))

    assert any(independent(sites) for sites in combinations(neighbors, alpha))
    assert not any(independent(sites) for sites in combinations(neighbors, alpha + 1))
    print(f"{name}: n={len(neighbors)} degree={degree} alpha={alpha} "
          f"nonedges={len(nonedges)} codegree={min(common)}..{max(common)} "
          f"wedges={sum(common)} cap2_budget={2 * len(nonedges)}")


def circulant(order, steps):
    return adjacency(range(order), ((site, (site + step) % order)
                                    for site, step in product(range(order), steps)))


def main():
    literal_check("C5", circulant(5, (1,)), 2, 2, 1, True)
    literal_check("C13(1,5)", circulant(13, (1, 5)), 4, 4, 2, True)
    clebsch = adjacency(range(16), ((site, site ^ step)
                                    for site, step in product(range(16), (1, 2, 4, 8, 15))))
    literal_check("Clebsch", clebsch, 5, 5, 2, True)
    literal_check("K4,4 (adverse)", adjacency(range(8), product(range(4), range(4, 8))),
                  4, 4, 4, True)

    rows = ("a", "b", "c", "d")
    columns = ("ac", "ad", "bc", "bd", "cd", "x", "y")
    low_edges = [("root", row) for row in rows]
    low_edges += [(row, column) for row, column in product(rows, columns[:5]) if row in column]
    low_edges += [("a", "x"), ("b", "y"), ("ac", "bd"), ("ad", "bc"),
                  ("cd", "x"), ("cd", "y"), ("x", "bc"), ("x", "bd"),
                  ("y", "ac"), ("y", "ad")]
    low = adjacency(("root", *rows, *columns), low_edges)
    literal_check("forced 12-vertex low layer", low, 4, 4, 2, True)
    triples = (("root", "x", "y"), ("a", "b", "cd"), ("c", "ad", "bd"), ("d", "ac", "bc"))
    one = {frozenset((first, second)) for first, second in combinations(low, 2)
           if len(low[first] & low[second]) == 1}
    assert one == {frozenset(pair) for triple in triples for pair in combinations(triple, 2)}
    print(f"codegree-one graph: four triangles, {len(one)} edges")

    allowable = {}
    for count_low in range(8, 21):
        count_seven = 40 - 2 * count_low
        allowable[count_low] = []
        for type_two_seven in range(count_low + 1):
            low_degree_sum = 5 * count_low - type_two_seven
            if low_degree_sum % 2:
                continue
            low_mid = 6 * type_two_seven + 10 * (count_low - type_two_seven)
            seven_mid = max(0, 2 * type_two_seven - count_seven)
            cap = 2 * (comb(count_low, 2) - low_degree_sum // 2)
            if low_mid + seven_mid <= cap:
                allowable[count_low].append(type_two_seven)
    assert [allowable[count_low] for count_low in range(8, 13)] == [[], [], [], [], [12]]
    print("wedge bound (parity included): n6=8..11 impossible; n6=12 forces all 12 type two-seven")


if __name__ == "__main__":
    main()
