"""Weighted cyclic quotients; the relift solver does not impose a cyclic signing."""

import argparse
import csv
from itertools import combinations, product
from math import gcd
from pathlib import Path
import sys

from pole_audit import to_graph6, write_lines, independent
from relift_audit import encode, explicit_lift, pairs, quotient, walk_score


def dist(size, offset):
    return min(offset % size, -offset % size)


def matrix(size, profile):
    return [[profile[dist(size, right - left)] for left in range(size)] for right in range(size)]


def profiles(size, low, high):
    for weights in product(range(3), repeat=size // 2):
        for vert in range(2):
            profile = (vert,) + weights
            if not low <= sum(profile[dist(size, step)] for step in range(size)) <= high:
                continue
            orbit = {tuple(profile[dist(size, step * unit)] for step in range(len(profile)))
                     for unit in range(1, size) if gcd(unit, size) == 1}
            if profile != min(orbit):
                continue
            occupied = {step for step in range(1, size) if profile[dist(size, step)]}
            if any(profile[dist(size, step)] == 2 and
                   (vert or any((other - step) % size in occupied for other in occupied))
                   for step in occupied):
                continue
            yield profile, len(orbit)


def cayley(size, steps, split):
    def shift(left, right):
        if split:
            return (left + right) % size + size * ((left // size) ^ (right // size))
        return (left + right) % (2 * size)
    return [sum(1 << shift(start, step) for step in steps) for start in range(2 * size)]


def baselines(size, profile, split):
    def inverse(step):
        return (-step) % size + size * (step // size) if split else (-step) % (2 * size)
    choices = []
    for offset, weight in enumerate(profile[1:], 1):
        blocks = []
        for chosen in combinations((offset, offset + size), weight):
            reflected = {inverse(step) for step in chosen}
            if 2 * offset == size and reflected != set(chosen):
                continue
            blocks.append(set(chosen) | reflected)
        choices.append(blocks)
    for blocks in product(*choices):
        steps = set.union({size} if profile[0] else set(), *blocks)
        graph = cayley(size, steps, split)
        if independent(graph[0], graph):
            yield steps, graph


def small():
    size = 4
    cells = pairs(size)
    positions = [(left, right, side) for left, right in cells
                 for side in range(1 if left == right else 2)]
    direct = {}
    for value in range(1 << len(positions)):
        graph = [0] * (2 * size)
        for index, (left, right, side) in enumerate(positions):
            if (value >> index) & 1:
                for layer in range(2):
                    other = 2 * right + (1 - layer if left == right else layer ^ side)
                    graph[2 * left + layer] |= 1 << other
                    graph[other] |= 1 << (2 * left + layer)
        if not all(independent(row, graph) for row in graph):
            continue
        base = quotient(graph)
        if any(base[left][right] != base[(left + 1) % size][(right + 1) % size] for left, right in cells):
            continue
        text = encode(base)
        score = walk_score(graph, 4)
        direct[text] = min(score, direct.get(text, score))
    source = [encode(matrix(size, profile)) for profile, orbit in profiles(size, 0, 7)]
    assert len(source) == len(set(source)) and set(source) == direct.keys()
    write_lines(Path('small.q'), source)
    write_lines(Path('small.expected'), (str(direct[text]) for text in source))
    print('small explicit labelled graphs', 1 << len(positions), 'legal cyclic quotients', len(direct),
          'thresholds', sorted(set(direct.values())))


def prepare(size):
    sys.path.insert(0, str(Path.cwd()))
    import ev
    controls = size == 19
    ksize = 10
    metadata = []
    positives = []
    planted = []
    baseline_witness = {}
    for profile, orbit in profiles(size, 6 if controls else 9, 9):
        base = encode(matrix(size, profile))
        best = None
        counts = []
        for split in (False, True):
            legal = zero = 0
            for steps, graph in baselines(size, profile, split):
                legal += 1
                score = ev.indep(graph, ksize, 1 if controls else 1 << 60)
                if not score:
                    zero += 1
                if best is None or score < best:
                    best = score
                    baseline_witness[base] = to_graph6(graph)
            counts.extend((legal, zero))
        if controls and counts[1]:
            positives.append((profile, orbit, counts[1]))
            planted.append(base)
        metadata.append((best, profile, orbit, *counts, base))
    metadata.sort(key=lambda rec: (rec[0] is None, rec[0], rec[1]))
    name = 'ctl' if controls else 'target'
    with open(name + '.meta.tsv', 'w') as handle:
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(('baseline', 'profile', 'unit_orbit', 'cyclic', 'cyclic_zero', 'split', 'split_zero', 'quotient'))
        for score, profile, *rest in metadata:
            writer.writerow((score, ''.join(map(str, profile)), *rest))
    write_lines(Path(name + '.q'), (rec[-1] for rec in metadata))
    write_lines(Path(name + '.baseline.g6'), (baseline_witness.get(rec[-1], '-') for rec in metadata))
    print(name, 'legal reps', len(metadata), 'distance profiles', sum(row[2] for row in metadata),
          'with abelian baseline', sum(row[0] is not None for row in metadata))
    if controls:
        assert sum(orbit * zero for _, orbit, zero in positives) == 9
        print('cyclic positives (profile, orbit, count):', positives)
        write_lines(Path('ctl.planted.q'), planted)
    else:
        print('best restricted baselines', [rec[0] for rec in metadata[:12]])
        write_lines(Path('target.pilot.q'), (rec[-1] for rec in metadata[:12]))


if __name__ == '__main__':
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('mode', choices=('small', 'ctl', 'target'))
    mode = args.parse_args().mode
    if mode == 'small':
        small()
    else:
        prepare(19 if mode == 'ctl' else 20)
