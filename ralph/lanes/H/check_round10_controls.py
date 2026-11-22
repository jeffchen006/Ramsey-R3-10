"""Direct smaller-case checks, without the original join or LP code."""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from check_graph import alpha, parse_graph6, triangle_free


def reciprocal_control():
    catalogue = ROOT / "gluing/val/r3_7_22.g6"
    records = catalogue.read_text().splitlines()
    assert len(records) == len(set(records)) == 191
    window_counts = Counter()
    classes = Counter()
    checked_vertices = adverse = 0
    for record in records:
        graph = parse_graph6(record)
        if not all(mask.bit_count() == 6 for mask in graph):
            continue
        assert len(graph) == 22 and triangle_free(graph) and alpha(graph) == 6
        vertices = set(range(len(graph)))
        neighbours = [{other for other in vertices if mask >> other & 1} for mask in graph]
        for first, second in combinations(sorted(vertices), 2):
            opposite = neighbours[first] & neighbours[second]
            if len(opposite) != 2:
                continue
            third, fourth = sorted(opposite)
            codegree = len(neighbours[third] & neighbours[fourth])
            if codegree not in (2, 3):
                continue
            left = vertices - {first, second} - neighbours[first] - neighbours[second]
            right = vertices - opposite - neighbours[third] - neighbours[fourth]
            overlap = left & right
            assert len(left) == 10 and len(right) == 8 + codegree
            assert left | right == vertices - {first, second, third, fourth}
            assert len(overlap) == codegree
            for vertex in overlap:
                nbrs = neighbours[vertex]
                assert nbrs <= left | right
                lhs = len(nbrs & left) + len(nbrs & right)
                assert lhs == 6 + len(nbrs & overlap)
                for deleted in nbrs & left - right:
                    cut = left - {deleted}
                    assert not nbrs <= cut | right
                    assert len(nbrs & cut) + len(nbrs & right) == 5 + len(nbrs & (cut & right))
                    adverse += 1
                checked_vertices += 1
            window_counts[codegree] += 1
            classes[record] += 1
    assert len(classes) == 10 and window_counts == {2: 334, 3: 395}
    assert checked_vertices == 2 * 334 + 3 * 395 and adverse > 0
    print(f"reciprocal: 10 classes, 334 equal / 395 asymmetric marks, {checked_vertices} overlap slots, "
          f"{adverse} coverage-drop negatives")


def incidence_control():
    """Exhaust four size-two columns on six rows, then test a capacity witness."""
    row_count = 6
    options = list(combinations(range(row_count), 2))
    counts = Counter()
    for columns in product(options, repeat=4):
        histogram = Counter(sum(row in column for column in columns) for row in range(row_count))
        zeroes, singles, doubles, triples, quadruples = (histogram[degree] for degree in range(5))
        assert singles + 2 * doubles + 3 * triples + 4 * quadruples == 8
        total = singles + 2 * zeroes
        assert total == 4 + triples + 2 * quadruples
        if total <= 4:
            assert not triples and not quadruples
        if total <= 5:
            assert triples <= 1 and not quadruples
        counts[total - 4] += 1
    assert sum(counts.values()) == 15**4 and all(counts[margin] for margin in (0, 1, 2))

    multiplicity = (2, 1, 3)
    weights, bounds, scale = (1, 2), (5, 3), 3
    valid = ((2, 1, 0), (1, 1, 0))
    invalid = ((1, 0, 0), (0, 1, 0))
    for matrix, expected_cover in ((valid, True), (invalid, False)):
        assert all(sum(value * count for value, count in zip(row, multiplicity)) <= bound
                   for row, bound in zip(matrix, bounds))
        covers = all(sum(weight * row[index] for weight, row in zip(weights, matrix)) >= scale
                     for index in (0, 1))
        assert covers == expected_cover
        if covers:
            assert sum(multiplicity[:2]) <= sum(a * b for a, b in zip(weights, bounds)) // scale
    print(f"incidences: {sum(counts.values())} exact small matrices, margins {dict(sorted(counts.items()))}; "
          "valid weight witness and coverage mutation separated")


if __name__ == "__main__":
    reciprocal_control()
    incidence_control()
