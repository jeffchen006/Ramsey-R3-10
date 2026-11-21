#!/usr/bin/env python3
"""Signature-cell edge projection, with exact replay of any cuts."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path

from check_root_cover import graph, vertices
from check_rows import saturated
from equality_template import template_counts
from etables import E, e3
from scan import solve, verify
from typed_lp import Model

LOCAL_TRIPLE_FLOORS = (9, 11, 15, 18)


def lower_edges(target_k, order):
    if target_k <= 1:
        return 0 if order == 0 else None
    if target_k == 2:
        return order * (order - 1) // 2 if order <= 2 else None
    if target_k > 9:
        return 0
    return e3(target_k, order) if order <= max(E[target_k]) else None


@lru_cache(maxsize=None)
def contact_bounds(private, size, signature_pairs, family):
    """Minimize over all counts of private vertices touched by the family."""
    pairs = list(combinations(range(size), 2))
    base = sum(private - 1 + (pair in signature_pairs) for pair in pairs)
    bounds = [range(private + 1) if any(index not in pair for pair in family) else (0,)
              for index in range(size)]
    feasible = []
    unused = set(range(size)).difference(*family)
    for removed in product(*bounds):
        if any(private - number >= private + size - len(family) for number in removed):
            continue
        contacts = sum(removed)
        remainder = lower_edges(private + size - len(family), private * size - contacts)
        if remainder is None:
            continue
        with_anchors = lower_edges(private + size - len(family), private * size - contacts + len(unused))
        if with_anchors is None:
            continue
        remainder = max(remainder, with_anchors - sum(private - removed[index] for index in unused))
        touching = sum(max(0, max(removed[left], removed[right]) - ((left, right) not in signature_pairs))
                       for left, right in pairs)
        even_cycles = private == 4 and size == 3 and len(signature_pairs) == 3
        extra = int(even_cycles and private * size - contacts > 2 * (private + size - len(family) - 1))
        feasible.append((contacts, max(base + extra, remainder + touching)))
    if not feasible:
        return None
    return tuple(min(edges + weight * contacts for contacts, edges in feasible) for weight in range(4)), min(
        contacts for contacts, _ in feasible)


def supports_model(signatures, anchors, private, counts, total, strengthen=True, target=False):
    model = Model()
    supports = [(index,) for index in range(anchors)] + list(signatures)
    masks = [sum(1 << index for index in support) for support in supports]
    sizes = [private] * anchors + [1] * len(signatures)
    alpha = anchors + private - 1
    root_anchors = Counter([anchors] + [1 + sum(size for size, support in zip(sizes, supports) if anchor in support)
                                        for anchor in range(anchors)])
    inner = total - anchors - sum(size * len(support) for size, support in zip(sizes, supports))
    edges = {(left, right): model.col(('edge', left, right), sizes[left] * sizes[right])
             for left, right in combinations(range(len(sizes)), 2) if not masks[left] & masks[right]}
    model.eq({column: 1 for column in edges.values()}, inner, 'interior_edges')
    population = {}
    for index, (size, support) in enumerate(zip(sizes, supports)):
        assignment = {degree: model.col(('count', index, degree), size) for degree in counts
                      if degree >= len(support) + (6 if target else 0)}
        population[index] = assignment
        model.eq({column: 1 for column in assignment.values()}, size, f'cell_size_{index}')
        coefficients = {column: 1 for pair, column in edges.items() if index in pair}
        coefficients.update({column: len(support) - degree for degree, column in assignment.items()})
        model.eq(coefficients, 0, f'cell_incidence_{index}')
        for anchor in range(anchors):
            if anchor in support:
                continue
            model.le({column: -1 for (left, right), column in edges.items() if
                      (left == index and anchor in supports[right]) or (right == index and anchor in supports[left])},
                     -size, f'column_domination_{index}_{anchor}')
    for degree, count in counts.items():
        model.eq({assignment[degree]: 1 for assignment in population.values() if degree in assignment},
                 count - root_anchors[degree], f'global_deg_{degree}')
    if target and counts[6] == 2:
        leaf = next(anchor for anchor in range(anchors) if sum(anchor in pair for pair in signatures) == 1)
        double = next(anchors + index for index, pair in enumerate(signatures) if leaf in pair)
        strip = {leaf, double}
        model.eq({column: 1 for pair, column in edges.items() if strip.intersection(pair)}, 36, 'companion_residue_edges')
        model.le({assignment[7]: 1 for index, assignment in population.items() if index in strip and 7 in assignment},
                 1, 'companion_profile_7')
        for index, size in enumerate(sizes):
            if index in strip:
                continue
            incidences = {column: 1 for pair, column in edges.items() if index in pair and strip.intersection(pair)}
            model.le({column: -value for column, value in incidences.items()}, -size, 'companion_support_min')
            model.le(incidences, 2 * size, 'companion_support_max')
        if counts[8] <= 2:
            model.eq({population[double][9]: 1}, 1, 'companion_leaf_anchor_9')
    for first, second in combinations(range(anchors), 2):
        model.le({edges[first, second]: -1}, -(private - 1 + ((first, second) in signatures)),
                 f'private_matching_{first}_{second}')
        cross = {column: -1 for (left, right), column in edges.items() if
                 (first in supports[left] and second in supports[right]) or
                 (second in supports[left] and first in supports[right])}
        union = sum(size for support, size in zip(supports, sizes) if first in support or second in support)
        model.le(cross, -(union - (alpha - 1)), f'full_column_matching_{first}_{second}')
    for count in range(2, anchors + 1):
        for subset in combinations(range(anchors), count):
            mask = sum(1 << index for index in subset)
            groups = {index for index, support in enumerate(masks) if not support & ~mask}
            size = sum(sizes[index] for index in groups)
            lower = lower_edges(private + count, size)
            with_anchors = lower_edges(private + count, size + count)
            if lower is None or with_anchors is None:
                model.le({}, -1, f'impossible_subset_{subset}')
                continue
            lower = max(lower, with_anchors - sum(sizes[index] * len(supports[index]) for index in groups))
            if strengthen and private == 4 and count == 3:
                lower = max(lower, LOCAL_TRIPLE_FLOORS[len(groups) - count])
            model.le({column: -1 for pair, column in edges.items() if groups.issuperset(pair)},
                     -lower, f'induced_subset_{subset}')
            if strengthen:
                add_contacts(model, private, subset, groups, supports, masks, anchors, edges)
    return model


def add_contacts(model, private, subset, groups, supports, masks, anchors, edges):
    doubles = sorted(index for index in groups if index >= anchors)
    remapped = {index: tuple(subset.index(anchor) for anchor in supports[index]) for index in doubles}
    signature_pairs = tuple(remapped.values())
    internal = {column: -1 for (left, right), column in edges.items() if left in subset and right in subset}
    for cardinality in range(1, min(max(len(subset) - 1, 3), len(doubles)) + 1):
        for family in combinations(doubles, cardinality):
            if any(not masks[first] & masks[second] for first, second in combinations(family, 2)):
                continue
            bounds = contact_bounds(private, len(subset), signature_pairs, tuple(remapped[index] for index in family))
            if bounds is None:
                model.le({}, -1, f'impossible_contacts_{subset}_{family}')
                continue
            weighted_bounds, contact_minimum = bounds
            links = {column: -1 for (left, right), column in edges.items() if left in subset and right in family}
            model.le(links, -contact_minimum, f'contact_minimum_{subset}_{family}')
            for weight, bound in enumerate(weighted_bounds):
                model.le(internal | {column: weight * value for column, value in links.items()}, -bound,
                         f'contact_edges_w{weight}_{subset}_{family}')


def maximum_matching(adj, left, right):
    matched = {}

    def augment(vertex, seen):
        for other in right:
            if not adj[vertex] >> other & 1 or other in seen:
                continue
            seen.add(other)
            if other not in matched or augment(matched[other], seen):
                matched[other] = vertex
                return True
        return False

    return sum(augment(vertex, set()) for vertex in left)


def controls(adj, alpha):
    assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
    order = len(adj)
    counts = Counter(map(int.bit_count, adj))
    results = Counter()
    for root, neighborhood in enumerate(adj):
        anchors = tuple(vertices(neighborhood))
        degree = len(anchors)
        private = alpha + 1 - degree
        exterior = ((1 << order) - 1) & ~(neighborhood | 1 << root)
        supports = {vertex: tuple(index for index, anchor in enumerate(anchors) if adj[vertex] >> anchor & 1)
                    for vertex in vertices(exterior)}
        cells = {signature: [vertex for vertex, value in supports.items() if value == signature]
                 for signature in set(supports.values())}
        for first, second in combinations(range(degree), 2):
            left = cells.get((first,), [])
            right = cells.get((second,), [])
            common = cells.get((first, second), [])
            lower = len(left) + len(right) + len(common) - (private + 1)
            assert maximum_matching(adj, left, right) >= lower
            results['nontrivial_general_private_match'] += lower > 0
            columns = [{vertex for vertex in supports if anchor in supports[vertex]} for anchor in (first, second)]
            assert maximum_matching(adj, columns[0] - columns[1], columns[1] - columns[0]) >= len(columns[0] | columns[1]) - (alpha - 1)
            results['checked_general_pairs'] += 1
        if sum(map(len, supports.values())) != 2 * len(supports) - degree * private:
            continue
        signatures = tuple(sorted(signature for signature in cells if len(signature) == 2))
        groups = [(index,) for index in range(degree)] + list(signatures)
        model = supports_model(signatures, degree, private, counts, sum(map(int.bit_count, adj)) // 2)
        assignment = {}
        for key in model.bounds:
            kind, left, right = key
            if kind == 'edge':
                assignment[key] = sum(bool(adj[vertex] >> other & 1) for vertex in cells[groups[left]] for other in cells[groups[right]])
            else:
                assignment[key] = sum(adj[vertex].bit_count() == right for vertex in cells[groups[left]])
        for coefficients, rhs, name in model.rows:
            assert sum(value * assignment[key] for key, value in coefficients.items()) <= rhs, (root, name)
        results['equality_substitutions'] += 1
        results['checked_equality_rows'] += len(model.rows)
    return dict(results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, nargs=2)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.control:
        c13_file, exoo_file = args.control
        adj = graph.parse_matrix(exoo_file.read_text().splitlines())
        exoo = saturated([neighbours ^ ((1 << 39) - 1) ^ (1 << index) for index, neighbours in enumerate(adj)])
        c35 = [sum(1 << ((index + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16)) for index in range(35)]
        triangle = ((0, 1), (0, 2), (1, 2))
        assert contact_bounds(4, 3, triangle, triangle) == ((12, 18, 23, 27), 4)
        for tag, adj, alpha in [('C13', graph.parse_graph6(c13_file.read_text().strip()), 4),
                                ('n9p3', graph.parse_graph6('H?bvbro'), 4), ('C35', c35, 8), ('Exoo39-MTF', exoo, 9)]:
            print(tag, controls(adj, alpha))
        return
    templates, _ = template_counts()
    counts_by_result = Counter()
    if args.verify:
        seen = set()
        for line in args.output.read_text().splitlines():
            item = json.loads(line)
            key = item['mask'], tuple(item['counts']), item['strengthen']
            assert key not in seen
            seen.add(key)
            signatures, cases = templates[item['mask']]
            assert tuple(item['counts']) in cases
            model = supports_model(signatures, 6, 4, dict(zip(range(6, 10), item['counts'])), 168, item['strengthen'], target=True)
            assert verify(model, {int(index): Fraction(value) for index, value in item['multiplier'].items()})
        print(f'Checked {len(seen)} exact template/case rational certificates')
        return
    with args.output.open('w') as stream:
        for mask, (signatures, cases) in sorted(templates.items()):
            for strengthen in (False, True):
                for counts in cases:
                    model = supports_model(signatures, 6, 4, dict(zip(range(6, 10), counts)), 168, strengthen, target=True)
                    status, multiplier = solve(model)
                    counts_by_result[strengthen, status] += 1
                    if status == 'cert':
                        print(json.dumps({'mask': mask, 'counts': counts, 'strengthen': strengthen,
                                          'multiplier': multiplier}), file=stream, flush=True)
                    print(mask, counts, strengthen, len(model.rows), status, flush=True)
    print(dict(counts_by_result))


if __name__ == '__main__':
    main()
