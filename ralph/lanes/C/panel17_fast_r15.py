#!/usr/bin/env python3
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
import time

SCOUT = Path(__file__).resolve().parents[3] / 'scratch/ideas/r012_R'
sys.path.insert(0, str(SCOUT))
import terminal as reference

REASONS = ('degree', 'triangle', 'codegree', 'I10', 'still-live')
FULL = (1 << 40) - 1


def witness(candidates, need, graph):
    while candidates.bit_count() >= need:
        first = candidates & -candidates
        candidates ^= first
        if need == 1:
            return first
        rest = witness(candidates & ~graph[first.bit_length() - 1], need - 1, graph)
        if rest:
            return first | rest
    return 0


def allows(graph, sites):
    return all(not graph[site] & sites for site in reference.bits(sites))


def possible_upper(upper, domains):
    universe = (1 << len(upper)) - 1
    allowances = [universe] * len(upper)
    for packages in domains:
        site_order = [site for site, _ in packages[0]]
        unions = [0] * len(site_order)
        for package in packages:
            for index, (site, row) in enumerate(package):
                if site != site_order[index]:
                    raise RuntimeError('package has inconsistent owners')
                unions[index] |= row
        for site, row in zip(site_order, unions):
            allowances[site] &= row
    possible = [row & allowance for row, allowance in zip(upper, allowances)]
    for left, row in enumerate(possible):
        bit = 1 << left
        for right in reference.bits(upper[left] & ~row):
            possible[right] &= ~bit
    return possible


def assign(lower, upper, chosen):
    lower, upper = lower[:], upper[:]
    for site, row in chosen:
        bit = 1 << site
        for other in reference.bits(row & ~lower[site]):
            lower[other] |= bit
        for other in reference.bits(upper[site] & ~row):
            upper[other] &= ~bit
        lower[site] = upper[site] = row
    return lower, upper


class Classifier:
    def __init__(self, order, degree, cap, upper_witness=0):
        self.universe = (1 << order) - 1
        self.degree = degree
        self.cap = cap
        self.upper_witness = upper_witness
        self.cache = []
        self.profile = Counter()

    def run(self, lower, upper):
        degree, cap = self.degree, self.cap
        while True:
            if any(lo & ~hi or lo.bit_count() > degree or hi.bit_count() < degree for lo, hi in zip(lower, upper)):
                return 'degree'
            if any(row & lower[other] for row in lower for other in reference.bits(row)):
                return 'triangle'
            if any((first & second).bit_count() > cap for first, second in combinations(lower, 2)):
                return 'codegree'
            if self.upper_witness:
                if not allows(upper, self.upper_witness):
                    raise RuntimeError('upper-domination witness invariant failed')
                self.profile['upper'] += 1
                return 'I10'
            for sites in self.cache:
                if allows(upper, sites):
                    self.profile['hit'] += 1
                    return 'I10'
            sites = witness(self.universe, degree + 1, upper)
            self.profile['search'] += 1
            if sites:
                self.cache.insert(0, sites)
                del self.cache[8:]
                return 'I10'
            forced, forbidden = [], []
            for site, (lo, hi) in enumerate(zip(lower, upper)):
                for other in reference.bits(hi & ~lo):
                    if lo.bit_count() == degree or lo & lower[other]:
                        forbidden.append((site, other))
                    if hi.bit_count() == degree:
                        forced.append((site, other))
            if not forced and not forbidden:
                return 'still-live'
            for first, second in forced:
                lower[first] |= 1 << second
                lower[second] |= 1 << first
            for first, second in forbidden:
                upper[first] &= ~(1 << second)
                upper[second] &= ~(1 << first)


def setup():
    reference.hosts = list(map(reference.graph6, reference.source(5, 17).read_text().splitlines()))
    reference.frames = []
    for line in Path('frames17-5-2.txt').open():
        host, *parts = map(int, line.split())
        reference.frames.append((host, parts))
    reference.atlas = reference.defaultdict(set)
    for line in Path('liftrows.txt').open():
        host, *rows = map(int, line.split())
        reference.atlas[host].add(tuple(rows))


def audit(left_id, right_id, flip):
    left = reference.frame(*reference.frames[left_id], False)
    right = reference.frame(*reference.frames[right_id], flip)
    lower, upper, maps, _ = reference.thegraph(left, right)
    domains = [reference.domain(left, right, group, 0, lower, upper, maps) for group in left[2]]
    domains += [reference.domain(right, left, group, 1, lower, upper, maps) for group in right[2]]
    detail = Counter()
    if not all(domains):
        return detail, Counter(), 0
    possible = possible_upper(upper, domains)
    common_witness = witness(FULL, 10, possible)
    classifier = Classifier(40, 9, 5, common_witness)
    for chosen in reference.combine(domains, lower):
        detail[classifier.run(*assign(lower, upper, chosen))] += 1
    return detail, classifier.profile, common_witness


def controls(file):
    unaltered, completions, mutations = 0, 0, 0
    for line in Path(file).open():
        degree, cap, order, *rows = map(int, line.split())
        lower, upper = rows[:order], rows[order:]
        expected = reference.propagate(lower, upper, degree, cap)
        if expected != 'still-live' or Classifier(order, degree, cap).run(lower[:], upper[:]) != expected:
            raise RuntimeError('planted positive rejected')
        unaltered += 1
        for physical in (lower, upper):
            avalid = all(row.bit_count() == degree for row in physical)
            if not avalid:
                continue
            exact = reference.propagate(physical, physical, degree, cap)
            if exact == 'still-live':
                if Classifier(order, degree, cap).run(physical[:], physical[:]) != exact:
                    raise RuntimeError('smaller full completion rejected')
                completions += 1
        done = False
        for site, row in enumerate(lower):
            for other in reference.bits(row):
                changed = upper[:]
                changed[site] &= ~(1 << other)
                changed[other] &= ~(1 << site)
                if Classifier(order, degree, cap).run(lower[:], changed) != 'degree':
                    raise RuntimeError('corrupted fixed crossing accepted')
                mutations += 1
                done = True
                break
            if done:
                break
    if not (unaltered == mutations == 2118 and completions > 0):
        raise RuntimeError('wrong smaller-control denominator')
    print(unaltered, completions, mutations, 'small positive / exact / corrupted completions')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'controls':
        controls(sys.argv[2])
    elif len(sys.argv) in (3, 4) and sys.argv[1] == 'audit':
        setup()
        limit_ms = float(sys.argv[3]) if len(sys.argv) == 4 else float('inf')
        for line in Path(sys.argv[2]).open():
            identity = tuple(map(int, line.split()))
            started = time.process_time_ns()
            details, stats, found = audit(*identity)
            elapsed = (time.process_time_ns() - started) / 1e6
            print(*identity, *(details[reason] for reason in REASONS), f'{elapsed:.3f}')
            print(*identity, hex(found), *(stats[event] for event in ('upper', 'hit', 'search')), file=sys.stderr)
            if details['still-live'] or elapsed > limit_ms:
                raise SystemExit(f'new live or costly terminal ID: {identity}, {elapsed:.3f} ms')
    else:
        raise SystemExit('usage: panel17_fast_r15.py (audit IDS | controls PLANTED)')
