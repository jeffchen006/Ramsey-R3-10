#!/usr/bin/env python3
"""Factorized, row-word preflight for the two bmax15 / min10 profiles."""

import argparse
from collections import Counter
from functools import cache
from itertools import product
import json
from math import prod
from pathlib import Path
from random import Random
import sys
from time import process_time

from cubic32 import automorphisms
from involution_sat import from_graph6
from m11_support import Supports
from shape_deck24 import identify, options


PROFILES = ((2, 2, 5), (2, 3, 4))


def degree_rows(total):
    for degrees in product(range(3), repeat=8):
        if sum(degrees) == total and 2 <= sum(bool(count) for count in degrees) <= 4:
            yield degrees


def reorder(word, permutation):
    result = [0]*len(word)
    for vertex, target in enumerate(permutation):
        result[target] = word[vertex]
    return tuple(result)


def roster(core, profile):
    moves = tuple(automorphisms(core))
    by_sum = {total: tuple(degree_rows(total)) for total in set(profile)}
    supports = Supports(core, 6)

    @cache
    def instances(word):
        return supports.options(tuple(cnt+1 for cnt in word))

    @cache
    def shape(word):
        keep = sum(1 << vertex for vertex, entry in enumerate(word) if entry == 0)
        return identify(core, keep)

    for tripled_and_double in sorted(set(degree_rows(7))):
        assert sorted(tripled_and_double) == [0, 0, 0, 0, 1, 2, 2, 2]
        if tripled_and_double != min(reorder(tripled_and_double, perm) for perm in moves):
            continue
        if not instances(tripled_and_double):
            continue
        stable = tuple(perm for perm in moves if reorder(tripled_and_double, perm) == tripled_and_double)
        remainder = tuple(2-val for val in tripled_and_double)
        for first in by_sum[profile[0]]:
            if any(used > cap for used, cap in zip(first, remainder, strict=True)):
                continue
            for second in by_sum[profile[1]]:
                if profile[0] == profile[1] and first > second:
                    continue
                third = tuple(cap-left-right for cap, left, right in zip(remainder, first, second, strict=True))
                if min(third) < 0 or not 2 <= sum(bool(val) for val in third) <= 4:
                    continue
                assert sum(third) == profile[2]
                rows = first, second, third
                relevant = {shape(word) for word in rows if word.count(0) == 6}
                if len(relevant) != 1:
                    continue
                orbit = []
                for perm in stable:
                    moved = tuple(reorder(word, perm) for word in rows)
                    if profile[0] == profile[1]:
                        moved = (*sorted(moved[:2]), moved[2])
                    orbit.append(moved)
                if rows != min(orbit):
                    continue
                choices = tuple(instances(word) for word in rows)
                if all(choices):
                    yield tripled_and_double, rows, choices


def preflight(key, profile, sample_count, seed, ledger, sample, gate_log):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'C'))
    from audit_crown24_pinned import literal_pilot
    from crown24_pinned import analyze

    core = tuple(from_graph6(key))
    assert len(core) == 8 and all(row.bit_count() == 2 for row in core)
    rng = Random(seed)
    started = process_time()
    by_weight = []
    global_weight = 0
    for omitted, words, choices in roster(core, profile):
        arities = tuple(map(len, choices))
        volume = prod(arities)
        global_weight += volume
        by_weight.append((global_weight, omitted, words, choices))
        print(json.dumps((omitted, words, arities, volume), separators=(',', ':')), file=ledger)
    assert global_weight and by_weight
    print(key, profile, 'symbolic covers', len(by_weight), 'ordered column product upper', global_weight, flush=True)
    picked = sorted(rng.sample(range(global_weight), min(global_weight, sample_count)))
    index = 0
    alternatives = Counter()
    gate_counts = Counter()
    gate_cpu = 0.0
    for sample_index, rank in enumerate(picked):
        while rank >= by_weight[index][0]:
            index += 1
        peak, omitted, words, lists = by_weight[index]
        local = rank - (by_weight[index-1][0] if index else 0)
        reverse = []
        for folder in reversed(lists):
            local, entry = divmod(local, len(folder))
            reverse.append(folder[entry])
        assert local == 0
        groups = tuple(reversed(reverse))
        possible = options(core, groups, omitted, 6)
        assert possible is not None
        alternatives[len(possible)] += 1
        print(json.dumps((rank, key, profile, words, groups, omitted, possible), separators=(',', ':')), file=sample)
        if sample_index % 8 == 0:
            row = key, groups, omitted, 6
            before = process_time()
            primary = analyze(row, anchored=True)
            counts, literal = literal_pilot(row, anchored=True)
            gate_cpu += process_time()-before
            assert counts == primary['pairs']
            assert literal == json.loads(json.dumps(primary['retained']))
            gate_counts[bool(literal)] += 1
            print(json.dumps((rank, row, counts, literal), separators=(',', ':')), file=gate_log)
    print(key, profile, 'physically bound candidate-pair counts', dict(sorted(alternatives.items())),
          'CPU-s', process_time()-started, flush=True)
    print(key, profile, 'C all-anchor and literal', dict(gate_counts), 'CPU-s', gate_cpu, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key')
    parser.add_argument('profile', type=int, choices=(0, 1))
    parser.add_argument('output', type=Path)
    parser.add_argument('--sample', type=int, default=512)
    parser.add_argument('--seed', type=int, default=246358)
    args = parser.parse_args()
    with args.output.with_name(args.output.name+'.roster.jsonl').open('x', encoding='ascii') as ledger:
        with args.output.with_name(args.output.name+'.sample.jsonl').open('x', encoding='ascii') as sample:
            with args.output.with_name(args.output.name+'.gate.jsonl').open('x', encoding='ascii') as gate_log:
                preflight(args.key, PROFILES[args.profile], args.sample, args.seed, ledger, sample, gate_log)
