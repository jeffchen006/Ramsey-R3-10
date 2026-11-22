#!/usr/bin/env python3
"""Pilot: share forced and forbidden edges across saturated deletion windows."""

import argparse
from collections import Counter
from contextlib import nullcontext
from itertools import combinations
import json
from pathlib import Path
from time import process_time

from involution_cores import bits, graph
from involution_sat import from_graph6
from m11_prop import Prover, proof_check, targets
from replay_shared74 import read


def restrict(rows, relabel):
    return [sum(1 << new for new, old in enumerate(relabel) if rows[vertex] >> old & 1)
            for vertex in relabel]


def writeback(rows, result, relabel, forced):
    mask = sum(1 << vertex for vertex in relabel)
    for vertex, row in zip(relabel, result):
        original = sum(1 << relabel[neighbor] for neighbor in bits(row))
        if forced:
            rows[vertex] |= original
        else:
            rows[vertex] &= original | ~mask


def degree_pass(lower, upper, degrees):
    def change(rows, left, right, use):
        if use:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
        else:
            rows[left] &= ~(1 << right)
            rows[right] &= ~(1 << left)

    for vertex, target in enumerate(degrees):
        if lower[vertex] & ~upper[vertex]:
            return 'cross-window edge conflict'
        if not lower[vertex].bit_count() <= target <= upper[vertex].bit_count():
            return 'degree conflict'
        if any(lower[vertex] & lower[neighbor] for neighbor in bits(lower[vertex])):
            return 'global triangle'
        optional = upper[vertex] & ~lower[vertex]
        if lower[vertex].bit_count() == target:
            for neighbor in bits(optional):
                change(upper, vertex, neighbor, False)
        elif upper[vertex].bit_count() == target:
            for neighbor in bits(optional):
                change(lower, vertex, neighbor, True)
        else:
            for neighbor in bits(optional):
                if lower[vertex] & lower[neighbor]:
                    change(upper, vertex, neighbor, False)
    return None


def fuse(lower, upper, omissions, degrees, alpha, edges, prover):
    lower, upper = list(lower), list(upper)
    active = [tuple(vertex for vertex in range(len(lower)) if vertex not in omitted) for omitted in omissions]
    for turns in range(1, 1 + 2*len(lower)**2):
        before = (tuple(lower), tuple(upper))
        failure = degree_pass(lower, upper, degrees)
        if failure:
            return failure, lower, upper, turns
        for label in active:
            pinned, eligible = restrict(lower, label), restrict(upper, label)
            trace = prover.prove(pinned, eligible, alpha, edges)
            low, high = proof_check(pinned, eligible, alpha, edges, *trace)
            if trace[0]:
                return 'window conflict', lower, upper, turns
            writeback(lower, low, label, True)
            writeback(upper, high, label, False)
        if before == (tuple(lower), tuple(upper)):
            return 'open', lower, upper, turns
    raise AssertionError('propagation is monotone and should reach a fixed point')


def calibration(prover):
    omissions = ((0, 1), (2, 3), (4, 5))
    possible = [(left, right) for left, right in combinations(range(6), 2) if left//2 != right//2]
    upper = graph(6, possible)
    base = graph(6, [])
    good = []
    for selected in combinations(possible, 6):
        trial = graph(6, selected)
        if any(row.bit_count() != 2 for row in trial):
            continue
        if any(trial[left] & trial[right] for left, right in selected):
            continue
        for omitted in omissions:
            label = tuple(vertex for vertex in range(6) if vertex not in omitted)
            window = restrict(trial, label)
            if any(all(not window[left] >> right & 1 for left, right in combinations(pick, 2))
                   for pick in combinations(range(4), 3)):
                break
        else:
            good.append(trial)
    counts = Counter()
    for forbidden in ((), *((edge,) for edge in possible), *combinations(possible, 2)):
        available = graph(6, [edge for edge in possible if edge not in forbidden])
        true = [trial for trial in good if all(not (row & ~bound) for row, bound in zip(trial, available))]
        status, lower, high, _ = fuse(base, available, omissions, (2,)*6, 2, 2, prover)
        assert status == 'open' or not true
        for trial in true:
            assert all(not (low & ~actual or actual & ~bound)
                       for low, actual, bound in zip(lower, trial, high))
        counts['positive' if true else 'negative'] += 1
        counts['detected negative'] += status != 'open'
    assert good and counts['positive']
    print('six-vertex exhaustive completion control:', len(good), 'valid', dict(counts), flush=True)


def pilot(cover, trace, prover, output=None):
    wanted = {}
    for index, lift, result, *_ in read(trace):
        if result == 'open':
            wanted.setdefault(index, []).append(lift)
    counts = Counter()
    started = process_time()
    with output.open('x', encoding='ascii') if output else nullcontext() as receipts:
        for index, (key, profile, parts, omitted) in enumerate(read(cover)):
            if index not in wanted:
                continue
            assert profile == [10, 10, 11, 11]
            core = from_graph6(key)
            for lift in wanted.pop(index):
                lower, upper = targets(core, (*parts, omitted[lift]))
                omissions = tuple(tuple(range(8 + 6*group, 14 + 6*group)) for group in range(4))
                result, low, high, turns = fuse(lower, upper, omissions, (8,)*8+(7,)*24, 7, 74, prover)
                counts[result] += 1
                counts['turns'] += turns
                counts['forced edges'] += (sum(map(int.bit_count, low))-sum(map(int.bit_count, lower)))//2
                counts['removed edges'] += (sum(map(int.bit_count, upper))-sum(map(int.bit_count, high)))//2
                if receipts is not None:
                    verdict = (index, lift, result) if result == 'open' else (index, lift, 'fused', result)
                    print(json.dumps(verdict, separators=(',', ':')), file=receipts)
    assert not wanted
    print('fused-window checks:', dict(counts), f'cpu={process_time()-started:.3f}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cover', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--lib', type=Path, default=Path('../r6_e11/m11_prop.so'))
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    propagator = Prover(args.lib)
    calibration(propagator)
    pilot(args.cover, args.trace, propagator, args.out)
