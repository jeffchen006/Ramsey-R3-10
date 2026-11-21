"""Necessary two-degree incidence LP for an MTF root with a specified residue."""

import csv
from collections import Counter
from itertools import combinations_with_replacement, product
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from signature_probe import decode, members


def equations(distribution, attachments, root, edges, residual_edges, floors, ceilings):
    outside = {degree: count - attachments.get(degree, 0) - int(degree == root)
               for degree, count in distribution.items()}
    outside = {degree: count for degree, count in outside.items() if count}
    types = [(degree, inner) for degree in sorted(outside) for inner in sorted(ceilings)
             if 1 <= degree - inner <= root]
    pair_slots = list(combinations_with_replacement(types, 2))
    columns = ([('n', item) for item in types] + [('p', *pair) for pair in pair_slots] +
               [('b', item, degree) for item in types for degree in sorted(attachments)])
    equalities, inequalities = [], []
    for degree, count in outside.items():
        equalities.append(({('n', item): 1 for item in types if item[0] == degree}, count))
    equalities.append(({('n', item): item[1] for item in types}, 2*residual_edges))
    for item in types:
        degree, inner = item
        incidence, inner_sum, outer_sum = {}, {}, {}
        for left, right in pair_slots:
            if item not in (left, right):
                continue
            other = right if item == left else left
            factor = 2 if left == right else 1
            key = ('p', left, right)
            incidence[key] = factor
            inner_sum[key] = factor * other[1]
            outer_sum[key] = factor * other[0]
        equalities.append(({**incidence, ('n', item): -inner}, 0))
        equalities.append(({**{('b', item, neighbor): 1 for neighbor in attachments},
                            ('n', item): inner-degree}, 0))
        inequalities.append(({**inner_sum, ('n', item): -ceilings[inner]}, 0))
        inequalities.append(({**outer_sum, **{('b', item, neighbor): neighbor for neighbor in attachments},
                              ('n', item): floors[degree]-edges}, 0))
    for degree, count in attachments.items():
        equalities.append(({('b', item, degree): 1 for item in types}, count*(degree-1)))
        inequalities.append(({('b', item, degree): item[0] for item in types},
                             count*(edges-floors[degree]-root)))
        for item in types:
            inequalities.append(({('b', item, degree): 1, ('n', item): -count}, 0))
        inequalities.append(({('b', item, degree): 1 for item in types if item[0]-item[1] == 1}, count))
    return columns, equalities, inequalities


def reduce_rows(columns, rows):
    return np.asarray([[terms.get(key, 0) for key in columns] for terms, _ in rows]), np.asarray([rhs for _, rhs in rows])


def solve(columns, equalities, inequalities):
    equality, equality_rhs = reduce_rows(columns, equalities)
    inequality, inequality_rhs = reduce_rows(columns, inequalities)
    return linprog(np.zeros(len(columns)), A_eq=equality, b_eq=equality_rhs,
                   A_ub=inequality, b_ub=inequality_rhs, method='highs')


def calibrate(path):
    rows = decode(path.read_bytes().splitlines()[0])
    assert len(rows) == 35 and all(row.bit_count() == 8 for row in rows)
    base = ((1 << 35)-1) & ~(rows[0] | 1)
    degree = [(row.bit_count(), (row & base).bit_count()) for row in rows]
    actual = Counter(('n', degree[vertex]) for vertex in members(base))
    for vertex in members(base):
        for neighbor in members(rows[vertex] & base & ((1 << vertex)-1)):
            actual[('p', *sorted((degree[vertex], degree[neighbor])))] += 1
        actual[('b', degree[vertex], 8)] += (rows[vertex] & rows[0]).bit_count()
    columns, equalities, inequalities = equations({8:35}, {8:8}, 8, 140, 76, {8:76}, {inner:7*inner for inner in range(8)})
    assert set(actual) <= set(columns)
    assert all(sum(value*actual[key] for key, value in terms.items()) == rhs for terms, rhs in equalities)
    assert all(sum(value*actual[key] for key, value in terms.items()) <= rhs for terms, rhs in inequalities)
    assert solve(columns, equalities, inequalities).success
    print('C35 rooted control: actual incidence vector passes every exact row and LP is feasible', flush=True)


def main(small, census):
    calibrate(small)
    floors = {6:120, 7:107, 8:97, 9:88}
    ceilings = {3:15, 4:23, 5:29, 6:36, 7:44, 8:53}
    tested = feasible = 0
    with census.open() as source:
        for case in csv.DictReader(line for line in source if not line.startswith('#')):
            if case['round3_cut'] or case['t9_after'] != '88':
                continue
            edges = int(case['e'])
            distribution = {degree: int(case[f'n{degree}']) for degree in floors}
            outcomes = []
            choices = [range(min(count-(degree == 9), 9)+1) for degree, count in distribution.items()]
            for histogram in product(*choices):
                if sum(histogram) != 9 or sum(degree*count for degree, count in zip(distribution, histogram)) != edges-88:
                    continue
                attachments = {degree: count for degree, count in zip(distribution, histogram) if count}
                result = solve(*equations(distribution, attachments, 9, edges, 88, floors, ceilings))
                if result.status not in (0, 2):
                    raise ValueError(result.message)
                outcomes.append((histogram, result.status))
                tested += 1
                feasible += result.success
            print(edges, tuple(distribution.values()), outcomes, flush=True)
    print(f'{tested} rooted profiles tested; {feasible} feasible; floating LP diagnostic only')


if __name__ == '__main__':
    from sys import argv

    main(Path(argv[1]), Path(argv[2]))
