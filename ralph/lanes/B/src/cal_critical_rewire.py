"""Direct labelled comparison of critical rewires on order-eight controls."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess

from cal_mtf import parse_graph6, to_graph6
from cal_lateral import bits


def direct(rows, alpha, minimum, increment):
    vertices = range(len(rows))
    old_edges = bits(rows)
    triangles = [frozenset(combinations(triple, 2)) for triple in combinations(vertices, 3)]
    independent = [frozenset(combinations(group, 2)) for group in combinations(vertices, alpha+1)]
    for root in vertices:
        old = frozenset(edge for edge in old_edges if root in edge)
        unchanged = old_edges - old
        for attachments in combinations([vertex for vertex in vertices if vertex != root], len(old)+increment):
            new = frozenset(tuple(sorted((root, other))) for other in attachments)
            candidate = unchanged | new
            if new == old or any(triangle <= candidate for triangle in triangles):
                continue
            if min(sum(vertex in edge for edge in candidate) for vertex in vertices) < minimum:
                continue
            if not all(candidate & group for group in independent):
                continue
            if all(any(candidate & group == {edge} for group in independent) for edge in new):
                yield candidate


def main():
    controls = Path('../G/round4/excursion.control.g6').read_text().splitlines()
    counts = []
    for row in controls:
        graph = parse_graph6(row)
        assert len(graph) == 8
        for minimum in (0, 1, 2, 3):
            for increment in range(3):
                run = subprocess.run(['timeout', '5s', 'build/critical_rewire', '3', str(minimum), str(increment)],
                                     input=to_graph6(graph)+'\n', text=True, capture_output=True, check=True)
                actual = Counter(bits(parse_graph6(text)) for text in run.stdout.splitlines())
                expected = Counter(direct(graph, 3, minimum, increment))
                assert actual == expected
                counts.append(actual.total())
    assert len(counts) == 36 and sum(counts)
    print(f'{len(counts)} brute-force labelled comparisons PASS: {counts}')


if __name__ == '__main__':
    main()
