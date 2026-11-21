#!/usr/bin/env python3
"""Construct the actual integer coordinates of controls and check every row."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from typed_lp import PRESENT, build, e3

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import check_graph as graph


def members(mask):
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def saturated(adj):
    adj = adj.copy()
    for first, second in combinations(range(len(adj)), 2):
        if not (adj[first] & (1 << second) or adj[first] & adj[second]):
            adj[first] |= 1 << second
            adj[second] |= 1 << first
    return adj


def check_rows(adj, order, alpha):
    assert len(adj) == order and graph.triangle_free(adj) and graph.alpha(adj) == alpha
    degrees = list(map(int.bit_count, adj))
    counts = dict(Counter(degrees))
    lower = {degree: e3(alpha, order - 1 - degree) for degree in counts}
    mtf = all(adj[first] & adj[second] or adj[first] & (1 << second)
              for first, second in combinations(range(order), 2))
    values = Counter()
    weighted = []
    multisets = []
    for vertex, degree in enumerate(degrees):
        multiset = tuple(sorted(degrees[other] for other in members(adj[vertex])))
        multisets.append(multiset)
        weighted.append(sum(multiset))
        values["x", degree, multiset] += 1
    for first, second in combinations(range(order), 2):
        deg_first, deg_second = sorted((degrees[first], degrees[second]))
        if adj[first] & (1 << second):
            values["m", deg_first, deg_second] += 1
            continue
        common_mask = adj[first] & adj[second]
        common = common_mask.bit_count()
        pair_type = (deg_first, deg_second, common)
        values[("p", *pair_type)] += 1
        values["q", degrees[first], multisets[first], degrees[second], common] += 1
        values["q", degrees[second], multisets[second], degrees[first], common] += 1
        for shared in members(common_mask):
            values[("w", *pair_type, degrees[shared])] += 1
        values[("z", *pair_type, degrees[first])] += weighted[first]
        values[("z", *pair_type, degrees[second])] += weighted[second]
        values[("f", *pair_type)] += sum((adj[vertex] & (adj[second] ^ common_mask)).bit_count()
                                         for vertex in members(adj[first] ^ common_mask))
    model = build(counts, lower, order, alpha, mtf, PRESENT["packing"])
    for key, value in values.items():
        assert not value or 0 <= value <= model.bounds[key], (key, value)
    for coefficients, rhs, name in model.rows:
        lhs = sum(value * values[key] for key, value in coefficients.items())
        assert lhs <= rhs, (name, lhs, rhs)
    return sum(degrees) // 2, counts, mtf, len(model.rows)


if __name__ == "__main__":
    complement = graph.parse_matrix(Path(sys.argv[1]).read_text().splitlines())
    exoo = [neighbors ^ ((1 << 39) - 1) ^ (1 << vertex)
            for vertex, neighbors in enumerate(complement)]
    c35 = [sum(1 << ((vertex + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16))
           for vertex in range(35)]
    print("C35:", check_rows(c35, 35, 8))
    print("Exoo39:", check_rows(exoo, 39, 9))
    print("Exoo39, saturated:", check_rows(saturated(exoo), 39, 9))
    assert e3(8, 28) is None
    impossible = build({8: 36}, {8: e3(8, 27)}, 36, 8, True, PRESENT["all"])
    assert ({}, -36, "profile_mass_8-") in impossible.rows
    print("(3,9,36): all degrees 8 by R(3,8)=28; exact empty-row contradiction 0 <= -36")
    checked = 0
    regular = 0
    for line in (ROOT / "gluing/val/r3_7_22.g6").read_text().splitlines():
        if not line.strip() or line.startswith(">>"):
            continue
        _, degrees, _, _ = check_rows(graph.parse_graph6(line), 22, 6)
        checked += 1
        regular += int(degrees == {6: 22})
    assert (checked, regular) == (191, 10)
    print(f"(3,7,22): all {checked} repository catalogue graphs passed, including all {regular} regular")
