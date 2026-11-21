"""Brute-force labelled critical-edge swap comparison on (3,4;8)."""

from itertools import combinations
from pathlib import Path
import subprocess

from cal_mtf import parse_graph6, to_graph6


def bits(graph):
    return frozenset(edge for edge in combinations(range(len(graph)), 2) if graph[edge[0]] >> edge[1] & 1)


def direct(rows, alpha, minimum):
    order = len(rows)
    universe = set(combinations(range(order), 2))
    edges = bits(rows)
    triangles = [frozenset(combinations(tips, 2)) for tips in combinations(range(order), 3)]
    forbidden = [frozenset(combinations(tips, 2)) for tips in combinations(range(order), alpha+1)]
    for removed in edges:
        punctured = edges - {removed}
        if all(mask & punctured for mask in forbidden):
            continue
        for added in universe - edges:
            result = punctured | {added}
            if any(mask <= result for mask in triangles) or not all(mask & result for mask in forbidden):
                continue
            degrees = [sum(vertex in edge for edge in result) for vertex in range(order)]
            if min(degrees) >= minimum:
                yield result


if __name__ == '__main__':
    controls = Path('../G/round4/excursion.control.g6').read_text().splitlines()
    counts = []
    for text in controls:
        graph = parse_graph6(text)
        assert len(graph) == 8
        for minimum in (0, 1, 2, 3):
            run = subprocess.run(['timeout', '5s', 'build/lateral_critical', '3', str(minimum)],
                                 input=to_graph6(graph) + '\n', text=True, capture_output=True, check=True)
            observed = [bits(parse_graph6(line)) for line in run.stdout.splitlines()]
            expected = list(direct(graph, 3, minimum))
            assert len(observed) == len(expected) and set(observed) == set(expected)
            counts.append(len(expected))
    assert len(controls) == 3 and sum(counts)
    print(f'{len(counts)} brute-force control comparisons: exact labelled counts {counts}')
