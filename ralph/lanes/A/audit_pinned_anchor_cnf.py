#!/usr/bin/env python3
"""Check the order-24 pinned-anchor role split and plant literal addbacks."""

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys

from pysat.solvers import Cadical195

from audit_path_leaf import vertices
from audit_short_anchor import capacity, marked, parse_graph6, support_counts
from audit_strip_extensions import ROOT, independent

sys.path.insert(0, str(ROOT / 'ralph/lanes/G'))
from pinned_anchor_window import fixed_shell, roles, weak_window


def oracle_roles(adj, short, long, degree):
    restored = len(adj)
    pivot = 27
    stars = marked(adj, short, long)
    assert stars is not None
    masks = (short | (1 << restored), long)
    exterior = ((1 << restored) - 1) ^ short ^ long
    for orientation in (0, 1):
        first, second = (tuple(vertices(masks[index])) for index in (orientation, 1-orientation))
        star = stars[1-orientation]
        occupied = {tuple(vertices(mask)) for mask in support_counts(adj, masks[1-orientation], exterior)
                    if mask.bit_count() == 2}
        permitted = sorted(set(combinations((*second, pivot), 2)) - occupied)
        for first_hole, second_hole in combinations(permitted, 2):
            multiplicity = Counter((*first_hole, *second_hole))
            if multiplicity[pivot] != 9-degree or not multiplicity[star]:
                continue
            if multiplicity[star] == 2:
                shape = 'middle'
            elif len(multiplicity) == 4:
                shape = 'matching'
            else:
                continue
            holes = tuple(sorted((first_hole, second_hole), key=lambda pair: (pivot in pair, pair)))
            yield (orientation, first, second, stars[orientation], star,
                   ('full-' if degree == 9 else '') + shape, *holes)


def oracle_pins(adj, degree, role, missing):
    short_index, group_a, group_b, _, _, _, first_hole, second_hole = role
    roots, pivots, restored = (24, 25), (26, 27), 21
    common = set(range(28, 21+degree))
    exclusive = (set(range(21+degree, 34)), set(range(34, 40)))
    groups = (set(group_a), set(group_b))
    destroyed = set.union(common, *exclusive)
    needed = short_index == 0 or tuple(vertices(missing)) not in (first_hole, second_hole)
    eligible = exclusive[1-short_index]
    slot = min(eligible) if needed else None
    shell = {}
    for left, right in combinations(range(40), 2):
        pair = (left, right)
        endpoints = set(pair)
        if right <= 20:
            shell[pair] = bool(adj[left] >> right & 1)
        elif endpoints & set(roots):
            root = min(endpoints & set(roots))
            other, = endpoints - {root}
            index = roots.index(root)
            shell[pair] = other in roots or other in groups[index] or other == pivots[index]
        elif endpoints & set(pivots):
            pivot = min(endpoints & set(pivots))
            other, = endpoints - {pivot}
            index = pivots.index(pivot)
            shell[pair] = other in common or other in exclusive[index]
        elif left in destroyed and right in destroyed:
            if not (left in exclusive[0] and right in exclusive[1]):
                shell[pair] = False
        elif right == restored or pair == (22, 23):
            shell[pair] = False
        elif left == restored and right in (22, 23):
            shell[pair] = True
        elif slot in endpoints and endpoints & groups[short_index]:
            anchor, = endpoints & groups[short_index]
            shell[pair] = bool(missing >> anchor & 1)
        elif left == restored and right in eligible:
            shell[pair] = right != slot
    return shell


def compare_roles(adj, short, long, counts):
    exterior = ((1 << len(adj)) - 1) ^ short ^ long
    missing, = (capacity(short) - support_counts(adj, short, exterior)).elements()
    for degree in (8, 9):
        candidates = list(roles(adj, tuple(vertices(short)), tuple(vertices(long)), degree))
        assert len(candidates) == len(set(candidates))
        assert set(candidates) == set(oracle_roles(adj, short, long, degree))
        for role in candidates:
            orientation, _, _, _, mixed_star, shape, first_hole, second_hole = role
            consumed = orientation == 1 and tuple(vertices(missing)) in (first_hole, second_hole)
            if missing.bit_count() == 1 and orientation == 1:
                assert degree == 8 and 21 in first_hole and 27 in second_hole
                if shape == 'middle':
                    assert set(first_hole) == {21, mixed_star}
                    assert set(second_hole) == {27, mixed_star}
            counts[(missing.bit_count(), degree, orientation, shape, consumed)] += 1
            pinned = fixed_shell(adj, tuple(vertices(short)), tuple(vertices(long)), degree, role)[0]
            expected = oracle_pins(adj, degree, role, missing)
            assert pinned == expected, (role, set(expected.items()) ^ set(pinned.items()))


def plant_window(control, limit):
    adj = tuple(parse_graph6(control['core']))
    target = tuple(parse_graph6(control['target']))
    short, long = tuple(vertices(control['short'])), tuple(vertices(control['long']))
    problem, extras = weak_window(adj, short, long, 4, limit)
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        for layout in (tuple(range(24)), (*range(22), 23, 22)):
            literals = [edge if target[layout[left]] >> layout[right] & 1 else -edge
                        for (left, right), edge in problem.edge.items()]
            assert solver.solve(assumptions=literals), (control['graft'], layout)
    assert extras == (22, 23)


def main():
    control_path, keys = map(Path, sys.argv[1:])
    controls = json.loads(control_path.read_text())
    actual = controls['positives'][0]
    plant_window(actual, 7)
    print('actual order24 addback SAT in both extra label orders; all induced edges pinned', flush=True)
    synthetic = Counter()
    for mutated in controls['mutations']:
        plant_window(mutated, 8)
        try:
            plant_window(mutated, 7)
        except AssertionError:
            core = parse_graph6(mutated['core'])
            assert next(independent(core, 7), None) == tuple(mutated['parent_I7'])
        else:
            raise AssertionError('non-Ramsey mutant accepted at cap 7')
        compare_roles(tuple(parse_graph6(mutated['core'])), mutated['short'], mutated['long'], synthetic)
    assert any(used for _, _, _, _, used in synthetic)
    assert any(not used for _, _, _, _, used in synthetic)
    print('double deficits: relaxed geometry SAT; rejected as Ramsey parents at cap 7; '
          'both consumed-as-hole and retained-slot branches', sorted(synthetic.items()), flush=True)
    counts = Counter()
    for row in keys.read_text().splitlines():
        _, short, long, encoded = row.split()
        compare_roles(tuple(parse_graph6(encoded)), int(short), int(long), counts)
    print('all catalogue orientation and hole roles plus every fixed shell', sum(counts.values()), sorted(counts.items()))


if __name__ == '__main__':
    main()
