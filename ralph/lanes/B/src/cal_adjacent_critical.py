"""Match labelled outputs to an exact direct oracle before target sampling."""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
import subprocess

from cal_mtf import parse_graph6, to_graph6
from cal_lateral import bits


def direct(rows, alpha, minimum, target):
    size = len(rows)
    old = bits(rows)
    edge = (size, size + 1)
    vertex_sets = tuple(frozenset(combinations(vertices, 2))
                        for vertices in combinations(range(size + 2), alpha + 1))
    triangles = tuple(frozenset(combinations(vertices, 2))
                      for vertices in combinations(range(size + 2), 3))
    for assignments in product(range(3), repeat=size):
        left = sum(1 << vertex for vertex, value in enumerate(assignments) if value == 1)
        right = sum(1 << vertex for vertex, value in enumerate(assignments) if value == 2)
        if (left.bit_count(), left) > (right.bit_count(), right):
            continue
        candidate = old | {edge} | {(vertex, size + value - 1)
                                    for vertex, value in enumerate(assignments) if value}
        if len(candidate) != target or any(triple <= candidate for triple in triangles):
            continue
        if min(sum(vertex in pair for pair in candidate) for vertex in range(size + 2)) < minimum:
            continue
        witnesses = [candidate & group for group in vertex_sets]
        if all(witnesses) and candidate == set().union(*(w for w in witnesses if len(w) == 1)):
            yield candidate


def remove(rows, first, second):
    keep = [vertex for vertex in range(len(rows)) if vertex not in (first, second)]
    return [sum(((rows[vertex] >> other) & 1) << index for index, other in enumerate(keep))
            for vertex in keep]


def main():
    bases = subprocess.check_output(['../../opt/bin/geng', '-qt', '6'], text=True).splitlines()
    cases = outputs = 0
    for source in bases:
        rows = parse_graph6(source)
        for alpha, minimum in [(3, 0), (3, 2), (4, 1)]:
            if any(all(not (rows[first] >> second & 1) for first, second in combinations(group, 2))
                   for group in combinations(range(len(rows)), alpha + 1)):
                continue
            edges = len(bits(rows))
            for target in range(edges + 1, edges + 2*alpha):
                run = subprocess.run(['build/adjacent_critical', str(alpha), str(minimum), str(target)],
                                     input=source+'\n', capture_output=True, text=True, check=True)
                actual = Counter(bits(parse_graph6(line)) for line in run.stdout.splitlines())
                expected = Counter(direct(rows, alpha, minimum, target))
                assert actual == expected, (source, alpha, minimum, target, actual, expected)
                cases += 1
                outputs += sum(actual.values())
    path = Path('work/round4_tail_control/all21.g6')
    stems = subprocess.run(['build/adjacent_stems', '0', '6', '22'], input=path.read_text(),
                           capture_output=True, text=True, check=True)
    expected = Counter()
    for source in path.read_text().splitlines():
        rows = parse_graph6(source)
        for first, second in bits(rows):
            size = rows[first].bit_count() + rows[second].bit_count() - 1
            if size + 1 <= 11:
                expected[to_graph6(remove(rows, first, second)).strip()] += 1
    assert Counter(stems.stdout.splitlines()) == expected
    print(f'PASS exact order-8 labelled cases={cases}, outputs={outputs}; '
          f'order-16/e21 stem multiset={sum(expected.values())}')


if __name__ == '__main__':
    main()
