"""Independent boundary-mask and receipt audit for two diagonal-four P3 layouts."""

from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
CATALOGUE_HASH = '228d886ee01b3003d90c768af57804954f7adccbca901a3eeb3c69ccc020e8c5'


def independent(group, graph):
    return all(not (graph[point] & group) for point in group)


def check_c21():
    graph = {point: {(point + step) % 21 for step in (1, 4, 6, -1, -4, -6)}
             for point in range(21)}
    roots = (0, 5, 10)
    assert independent(set(roots), graph)
    assert all(independent(neighbours, graph) for neighbours in graph.values())
    assert next((group for group in combinations(graph, 7) if independent(set(group), graph)), None) is None
    assert any(independent(set(group), graph) for group in combinations(graph, 6))
    common = set.intersection(*(graph[root] for root in roots))
    nonroots = set.union(*(graph[root] for root in roots))
    boundary = nonroots | set(roots)
    residue = set(graph) - boundary
    masks = [graph[point] & boundary for point in residue]
    boundary_sixes = [set(group) for group in combinations(sorted(boundary), 6)
                      if independent(set(group), graph)]
    assert all(mask <= nonroots and independent(mask, graph) and
               all(mask & witness for witness in boundary_sixes) and
               all(len(mask & graph[root]) <= 4 for root in roots) for mask in masks)
    counts = Counter(len(mask & common) for mask in masks)
    incidence = sum(len(graph[point] & residue) for point in common)
    assert (len(residue), len(common), counts, incidence) == (8, 2, {0: 2, 1: 6}, 6)
    assert sum(2 - len(mask & common) for mask in masks) == 2 * len(residue) - incidence
    print('C21: correct order, triangle/alpha and actual attachment rows; zero=2 singleton=6')


def boundary_for(matrix):
    first_wing, second_wing = set(range(3)), set(range(3, 6))
    common, left_block, right_block = set(range(6, 10)), {10, 11}, {12, 13}
    roots = {15: first_wing | common | left_block,
             16: common | left_block | right_block | {14},
             17: second_wing | common | right_block}
    first_to_right = {(point, tag) for point in first_wing for tag in right_block}
    second_to_left = {(point, tag) for point in second_wing for tag in left_block}
    wing_edges = {(0, 3)} | ({(0, 4)} if matrix == 3 else set())
    edges = first_to_right | second_to_left | wing_edges | {(1, 14), (2, 14), (4, 14), (5, 14)}
    edges |= {(point, root) for root, neighbours in roots.items() for point in neighbours}
    graph = {point: set() for point in range(18)}
    for first, second in edges:
        graph[first].add(second)
        graph[second].add(first)
    assert all(independent(neighbours, graph) for neighbours in graph.values())
    assert [len(graph[first] & graph[second]) for first, second in ((15, 16), (16, 17), (15, 17))] == [6, 6, 4]
    assert all(graph[tag] == set(roots) for tag in common)
    blockers = [first_wing | left_block, second_wing | right_block, left_block | right_block | {14},
                {0, 1, 2, 4, 5} if matrix == 1 else {1, 2, 3, 4, 5}]
    nines = [set(group) for group in combinations(graph, 9) if independent(set(group), graph)]
    assert nines
    masks = [set(group) for width in (3, 4, 5) for group in combinations(range(15), width)
             if independent(set(group), graph) and all(set(group) & witness for witness in nines)
             and all(len(set(group) & neighbours) <= 5 for neighbours in roots.values())]
    assert all(mask & common for mask in masks)
    for tag in sorted(common):
        padded = [blocker | (common - {tag}) for blocker in blockers]
        assert all(len(blocker) == 8 and independent(blocker, graph) for blocker in padded)
        singles = [mask for mask in masks if mask & common == {tag}]
        assert len(singles) == {1: 112, 3: 105}[matrix]
        assert not any(all(mask & blocker for blocker in padded) for mask in singles)
        assert sum(all(mask & blocker for blocker in padded[:3]) for mask in singles) == 17
    edges_residue = 180 - 18 * 9 + len(edges)
    deficit = 2 * 22 - len(common) * (9 - len(roots))
    assert deficit == 20 > len(common) * len(blockers) == 16
    adj_masks = [sum(1 << tag for tag in graph[point]) for point in graph]
    boundary_hash = sha256(','.join(map(str, adj_masks)).encode()).hexdigest()
    print(f'matrix={matrix} residue_edges={edges_residue} zero=0 singleton/tag={len(singles)} '
          f'uncovered=0 omit_fourth=17 boundary={boundary_hash}')
    return edges_residue, boundary_hash


def check_bindings(bindings_path):
    catalogue = (ROOT / 'gluing/val/r3_7_22.g6').read_bytes()
    assert sha256(catalogue).hexdigest() == CATALOGUE_HASH
    lines = catalogue.splitlines()
    assert len(lines) == len(set(lines)) == 191
    expected = set()
    for matrix in (1, 3):
        edge_count, boundary_hash = boundary_for(matrix)
        for row, line in enumerate(lines):
            assert line[0] == 85 and len(line) == 40 and (line[-1] - 63) % 8 == 0
            if sum((char - 63).bit_count() for char in line[1:]) == edge_count:
                expected.add(f'4\t{edge_count}\t{matrix}:0:1:0:1\t{boundary_hash}\t{row}\t{sha256(line).hexdigest()}')
    header, *rows = bindings_path.read_text().splitlines()
    assert header == 'diagonal\tedges\tlayout\tboundary_sha256\trow\tg6_sha256'
    assert Counter(row.split('\t')[1] for row in expected) == {'62': 30, '63': 60}

    def matches(actual):
        return len(actual) == len(expected) and set(actual) == expected

    assert matches(rows)
    assert not matches(rows[1:]) and not matches([rows[1], *rows[1:]])
    fields = rows[0].split('\t')
    fields[3] = rows[-1].split('\t')[3]
    assert not matches(['\t'.join(fields), *rows[1:]])
    print('exact bindings: e62=30 e63=60; missing, duplicate and crossed-boundary controls rejected')


if __name__ == '__main__':
    check_c21()
    check_bindings(Path(sys.argv[1]))
