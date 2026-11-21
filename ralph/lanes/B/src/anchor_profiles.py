"""Relax the e63/e88 anchor cover to counts of local neighbor-degree profiles."""

import argparse
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


def read_profiles(line):
    order = line[0] - 63
    rows = [set() for _ in range(order)]
    for right in range(1, order):
        for left in range(right):
            bit = right * (right - 1) // 2 + left
            if (line[1 + bit // 6] - 63) & (32 >> (bit % 6)):
                rows[left].add(right)
                rows[right].add(left)
    return Counter((len(row), tuple(sorted(len(rows[index]) for index in row))) for row in rows)


def matrix(degrees, ceilings):
    profiles = [(degree, neighbors) for degree in degrees
                for neighbors in combinations_with_replacement(degrees, degree)
                if sum(neighbors) <= ceilings[degree]]
    pairs = [(degree, other) for degree in degrees for other in degrees if degree < other]
    columns = [
        [1, degree, *(neighbors.count(high) if degree == low else
                      -neighbors.count(low) if degree == high else 0
                      for low, high in pairs)]
        for degree, neighbors in profiles
    ]
    return profiles, np.asarray(columns, dtype=np.int64).T


def minimum(profiles, equations, target, match, name):
    objective = [int(match(degree, neighbors)) for degree, neighbors in profiles]
    result = linprog(objective, A_eq=equations, b_eq=target, method='highs')
    if not result.success:
        raise RuntimeError(result.message)
    print(f'{name}: fractional min {result.fun:.6f}', flush=True)
    if result.fun < 1:
        active = [(round(value, 5), degree, neighbors) for (degree, neighbors), value in zip(profiles, result.x)
                  if value > 1e-6]
        print(f'{name}: feasible relaxation {active}', flush=True)


def calibrate(small):
    profiles, equations = matrix(range(4, 7), {4: 23, 5: 31, 6: 38})
    target = np.array([22, 126, 0, 0, 0])
    actual = 0
    for line in small.read_bytes().splitlines():
        counts = read_profiles(line)
        position = [counts.pop(profile, 0) for profile in profiles]
        if counts or np.any(equations @ position != target):
            raise ValueError(f'e63 control {actual} fails')
        actual += 1
    if actual != 60:
        raise ValueError(f'wrong control census: {actual}')
    print('control: all 60 exact e63 graphs obey the incidence equations')


def run(small):
    calibrate(small)
    profiles, equations = matrix(range(3, 9), {3: 15, 4: 23, 5: 29, 6: 36, 7: 44, 8: 53})
    target = np.array([30, 176, *([0] * 15)])

    def anchor(degree, neighbors):
        return (degree, sum(neighbors)) in ((6, 36), (7, 44)) and neighbors[0] >= 5

    print(f'{len(profiles)} local profiles')
    minimum(profiles, equations, target, anchor, 'all anchors')
    for degrees in (6, 7):
        minimum(profiles, equations, target, lambda degree, neighbors: degree == degrees and anchor(degree, neighbors),
                f'only d{degrees}')
    for high_limit in (0, 1, 2):
        minimum(profiles, equations, target,
                lambda degree, neighbors: anchor(degree, neighbors) and
                (degree == 7 or sum(neighbor > 6 for neighbor in neighbors) <= high_limit),
                f'with d7 and <= {high_limit} high neighbors at d6')
    for allowed in (6, 7):
        minimum(profiles, equations, target,
                lambda degree, neighbors: anchor(degree, neighbors) and
                (degree == 7 or neighbors[-1] <= allowed),
                f'with d7 and <= {allowed} maximum neighbor at d6')


if __name__ == '__main__':
    arguments = argparse.ArgumentParser()
    arguments.add_argument('small', type=Path)
    run(arguments.parse_args().small)
