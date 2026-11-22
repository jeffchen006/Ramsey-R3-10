#!/usr/bin/env python3
"""Direct planted-graph controls and a deficit oracle for pure opposite pivots."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from audit_strip_extensions import mark, validate_graph
from residue_bundle import triangle_free
from pysat.solvers import Cadical195

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'G'))
from joint_pivot_caps import impose, pure_caps
from strip_completion import Completion


def fixed_graph(adj):
    return Completion(len(adj), {(left, right): bool(adj[left] >> right & 1)
                                 for left, right in combinations(range(len(adj)), 2)})


def accepts(problem):
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        return solver.solve()


def c5_control():
    cycle = [sum(1 << ((vertex + displacement) % 5) for displacement in (-1, 1))
             for vertex in range(5)]
    assert triangle_free(cycle)
    visits = 0
    for first, second in combinations(range(5), 2):
        if cycle[first] >> second & 1:
            continue
        common = (cycle[first] & cycle[second]).bit_count()
        assert common == 1
        for allow, cap in ((True, 1), (False, 2), (False, 1), (True, 0)):
            problem = fixed_graph(cycle)
            impose(problem, first, second, tuple(set(range(5)) - {first, second}), cap, 1 if allow else -1)
            assert accepts(problem) == (common + int(not allow) <= cap)
            visits += 1
    print('C5 legal and wrong-cap controls:', visits, flush=True)


def deficits(sides, seen):
    return tuple(sorted((Counter({(anchor,): 4 for anchor in side}) + Counter(combinations(side, 2))
                         - support).elements()) for side, support in zip(sides, seen, strict=True))


def plant(adj, sides, stars, missing, leaves, move_full_into_common=None):
    order = len(adj)
    pivots = (order+2, order+3)
    common = tuple(range(order+4, 2*order-20))
    exclusive = (tuple(range(2*order-20, order+10)), tuple(range(order+10, 40)))
    assert len(common) + len(exclusive[0]) == len(common) + len(exclusive[1]) == 6
    planted = list(adj) + [0] * (40-order)

    def edge(first, second):
        planted[first] |= 1 << second
        planted[second] |= 1 << first

    edge(order, order+1)
    for index, (side, centre, leaf, star) in enumerate(zip(sides, pivots, leaves, stars, strict=True)):
        for anchor in (*side, centre):
            edge(order+index, anchor)
        for exterior in (*common, *exclusive[index]):
            edge(centre, exterior)
        fulls = sorted(set(side) - {leaf, star})
        double_vertices = list(exclusive[index][:2])
        if move_full_into_common is not None and move_full_into_common[0] == index:
            double_vertices[fulls.index(move_full_into_common[1])] = common[0]
        for anchor, exterior in zip(fulls, double_vertices, strict=True):
            edge(anchor, exterior)
        for exterior, support in zip(exclusive[1-index], missing[index], strict=True):
            for anchor in support:
                edge(anchor, exterior)
    assert triangle_free(planted)
    assert (planted[pivots[0]] & planted[pivots[1]]).bit_count() == len(common)
    assert all(planted[pivot].bit_count() == 7 for pivot in pivots)
    assert all(planted[anchor].bit_count() == (8 if anchor in leaves else 9)
               for side in sides for anchor in side)
    return planted


def direct(adj, sides, stars, leaves, order, index):
    return {(anchor, (adj[order+3-index] & adj[anchor]).bit_count(), 3 if anchor == leaves[index] else 4)
            for anchor in sides[index] if anchor != stars[index]}


def planted_control(row):
    row_id, first, second, encoded = row.split()
    masks = int(first), int(second)
    adj = validate_graph(encoded)
    order = len(adj)
    sides, stars, support = mark(adj, *masks)
    missing = deficits(sides, support)
    histograms = [Counter(anchor for signature in gaps for anchor in signature) for gaps in missing]
    crowded, = [(index, anchor) for index in (0, 1) for anchor in sides[index]
                if anchor != stars[index] and histograms[index][anchor] == 4]
    index, anchor = crowded
    leaves = [next(other for other in side if other != star and other != anchor)
              for side, star in zip(sides, stars, strict=True)]
    bad_leaves = list(leaves)
    bad_leaves[index] = anchor
    for tag, current, promote in (('positive', leaves, None), ('leaf_overflow', bad_leaves, None),
                                  ('full_overflow', leaves, crowded)):
        planted = plant(adj, sides, stars, missing, current, promote)
        for direction in ('0', '1', 'both'):
            problem = fixed_graph(planted)
            pure_caps(problem, order, *masks, direction=direction)
            actual = accepts(problem)
            counts = set().union(*(direct(planted, sides, stars, current, order, side)
                                   for side in (0, 1) if direction in ('both', str(side))))
            assert actual == all(shared <= cap for _, shared, cap in counts)
            assert actual == (tag == 'positive' or direction == str(1-index))
            print('planted', row_id, tag, direction, actual, sorted(counts), flush=True)


def pilot(path):
    passing = 0
    histogram = Counter()
    rows = path.read_text().splitlines()
    for row in rows:
        _, first, second, encoded = row.split()
        sides, stars, seen = mark(validate_graph(encoded), int(first), int(second))
        permitted = []
        for side, star, missing in zip(sides, stars, deficits(sides, seen), strict=True):
            values = [sum(anchor in contact for contact in missing) for anchor in side if anchor != star]
            histogram.update(values)
            permitted.append(max(values) <= 4 and min(values) <= 3)
        passing += all(permitted)
    print('standalone cap oracle', path.name, 'passing', passing, 'of', len(rows),
          'missing contact histogram', sorted(histogram.items()), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('witnesses', type=Path)
    parser.add_argument('samples', type=Path, nargs='+')
    args = parser.parse_args()
    c5_control()
    planted_control(next(line for line in args.witnesses.read_text().splitlines()
                         if line.startswith('179581 4204548 8388657 ')))
    for sample in args.samples:
        pilot(sample)


if __name__ == '__main__':
    main()
