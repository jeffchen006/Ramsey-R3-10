#!/usr/bin/env python3
import hashlib
import itertools
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

import networkx as nx


PACKED = struct.Struct('<4H')
ROOTS = range(2)
PRIVATE = range(2, 10)
NEUTRAL = range(10, 12)


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def edge_set(edges):
    return {tuple(sorted(edge)) for edge in edges}


def frame(graph, labels):
    result = nx.relabel_nodes(graph.subgraph(labels), {site: index for index, site in enumerate(labels)}, copy=True)
    for role, group in enumerate((ROOTS, PRIVATE, NEUTRAL)):
        for site in group:
            result.nodes[site]['role'] = role
    return result


def gluing(left, right, flip, crossings):
    label_left = dict(zip(range(12), (*range(10), 20, 21)))
    label_right = dict(zip(range(12), (*range(10, 20), 20 + flip, 21 - flip)))
    return edge_set(itertools.chain(
        ((label_left[one], label_left[two]) for one, two in left.edges),
        ((label_right[one], label_right[two]) for one, two in right.edges),
        ((label_left[one], label_right[two]) for one in ROOTS for two in ROOTS),
        ((label_left[one], label_right[two]) for one, two in crossings),
    ))


def plant(graph, left, right, flip):
    demand(left[10] == right[10 + flip] and left[11] == right[11 - flip], 'wrong physical neutral map')
    locations = {site: index for index, site in enumerate((*left[:10], *right[:10], *left[10:]))}
    demand(len(locations) == 22, 'collapsed separate physical frame copies')
    first = frame(graph, left)
    second = frame(graph, right)
    crossings = {(one, two) for one in PRIVATE for two in PRIVATE if graph.has_edge(left[one], right[two])}
    expected = edge_set((locations[one], locations[two]) for one, two in graph.edges)
    actual = gluing(first, second, flip, crossings)
    demand(actual == expected, 'forward reconstruction differs from source graph')
    relabel = (*range(10, 20), *range(10), 20 + flip, 21 - flip)
    reverse = gluing(second, first, flip, {(two, one) for one, two in crossings})
    demand(reverse == edge_set((relabel[one], relabel[two]) for one, two in expected), 'reverse physical mismatch')
    demand(all(relabel[relabel[site]] == site for site in range(22)), 'non-involutory physical label map')
    return first, second, crossings


def check_plants(path):
    graphs = [nx.from_graph6_bytes(line) for line in Path(path).read_bytes().splitlines()]
    demand(len(graphs) == 191, 'wrong source catalog count')
    regular = [graph for graph in graphs if graph.number_of_nodes() == 22 and set(dict(graph.degree).values()) == {6}]
    squares, placements = 0, 0
    diagonal = Counter()
    nonsymmetric = Counter()
    wrong_neutral_failures = 0
    for graph in regular:
        for low, high in itertools.combinations(range(22), 2):
            common = sorted(set(graph[low]) & set(graph[high]))
            for one, two in itertools.combinations(common, 2):
                roots = {low, high, one, two}
                left = (set(graph[low]) | set(graph[high])) - roots
                right = (set(graph[one]) | set(graph[two])) - roots
                neutral = sorted(set(graph) - roots - left - right)
                if len(left) != 8 or len(right) != 8 or left & right or len(neutral) != 2:
                    continue
                squares += 1
                source = [low, high, *sorted(left), *neutral]
                target = [one, two, *sorted(right), *neutral]
                for order_left, order_right in itertools.product(range(2), repeat=2):
                    source_order = [*source[:10], source[10 + order_left], source[11 - order_left]]
                    target_order = [*target[:10], target[10 + order_right], target[11 - order_right]]
                    first, second, crossings = plant(graph, source_order, target_order, order_left ^ order_right)
                    demand(bool(crossings), 'empty private-crossing plant')
                    placements += 1
                    if gluing(second, first, 1 ^ order_left ^ order_right, {(two, one) for one, two in crossings}) != gluing(
                        second, first, order_left ^ order_right, {(two, one) for one, two in crossings}
                    ):
                        wrong_neutral_failures += 1
                same_roles = nx.algorithms.isomorphism.categorical_node_match('role', -1)
                for mapping in nx.algorithms.isomorphism.GraphMatcher(first, second, node_match=same_roles).isomorphisms_iter():
                    target_copy = [target_order[mapping[index]] for index in range(12)]
                    flip = mapping[10] - 10
                    frame_left, frame_right, crossings = plant(graph, source_order, target_copy, flip)
                    demand(edge_set(frame_left.edges) == edge_set(frame_right.edges), 'diagonal frames not literally equal')
                    diagonal[flip] += 1
                    nonsymmetric[flip] += crossings != {(two, one) for one, two in crossings}
    demand((len(regular), squares, placements) == (10, 334, 1336), 'wrong planted inventory')
    demand(all(diagonal[flip] > 0 and nonsymmetric[flip] > 0 for flip in range(2)) and wrong_neutral_failures == placements,
           'missing physical equal-frame, asymmetric crossing or wrong-neutral control')
    print(f'physical regular={len(regular)}, squares={squares}, orientations={2*placements}, '
          f'fixed_forward={[diagonal[flip] for flip in range(2)]}, '
          f'fixed_asymmetric={[nonsymmetric[flip] for flip in range(2)]}, wrong_bit_changes={wrong_neutral_failures}')


def pack(ids):
    return b''.join(PACKED.pack(*record, 0) for record in sorted(ids))


def check_stream(executable):
    ordered = {(0, 0, 0), (2, 0, 0), (0, 2, 0), (1, 2, 1), (2, 1, 1),
               (2, 2, 0), (2, 2, 1), (2, 3, 0), (3, 2, 0), (2, 3, 1), (3, 2, 1)}
    expected = {
        (0, 2, 'LH'): {(0, 2, 0), (1, 2, 1)},
        (2, 3, 'HL'): {(2, 0, 0), (2, 1, 1)},
        (2, 3, 'HHrep'): {(2, 2, 0), (2, 2, 1), (2, 3, 0), (2, 3, 1)},
        (2, 3, 'HHdiag'): {(2, 2, 0), (2, 2, 1)},
        (3, 4, 'HHlower'): {(3, 2, 0), (3, 2, 1)},
        (0, 4, 'full'): ordered,
    }

    def run(ids):
        return subprocess.run([executable, 'full', '4', '2', '1'], input=pack(ids), capture_output=True, check=False)

    def rows_match(run_result):
        if run_result.returncode != 0:
            return False
        rows = {}
        for line in run_result.stdout.decode().splitlines():
            low, high, kind, flip0, flip1, digest = line.split()
            rows[int(low), int(high), kind] = int(flip0), int(flip1), digest
        return all(rows[key] == (sum(record[2] == 0 for record in ids), sum(record[2] == 1 for record in ids),
                                 hashlib.sha256(pack(ids)).hexdigest()) for key, ids in expected.items())

    demand(rows_match(run(ordered)), 'small packed roster mismatch')
    missing_diag = run(ordered - {(2, 2, 1)})
    demand(missing_diag.returncode == 0 and not rows_match(missing_diag), 'missing diagonal not rejected by bound inventory')
    for name, mutant in (
        ('wrong-bit', ordered - {(2, 0, 0)} | {(2, 0, 1)}),
        ('dropped-prefix-reference', ordered - {(1, 2, 1)}),
    ):
        result = run(mutant)
        demand(result.returncode == 2 and b'transposed reference' in result.stderr, f'{name} passed membership')
        print(f'{name}: rejected by exact transposed membership')
    print('missing-diagonal: rejected by bound inventory despite matching off-diagonal memberships')


if __name__ == '__main__':
    check_plants(sys.argv[1])
    check_stream(sys.argv[2])
