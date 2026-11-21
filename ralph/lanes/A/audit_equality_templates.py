#!/usr/bin/env python3
"""Check the canonical equality-template cover using an independent generator."""

from ast import literal_eval
from collections import Counter
import csv
from itertools import combinations, permutations
from math import factorial
from pathlib import Path
import re
import subprocess
import sys

from audit_floor_covers import BIN, require
from audit_residue_moves import expect_rejection, unique_labels
from residue_bundle import parse_graph6, to_graph6


def graph6(order, pairs):
    graph = [0] * order
    for first, second in pairs:
        require(0 <= first < second < order and not graph[first] >> second & 1, 'invalid pair')
        graph[first] |= 1 << second
        graph[second] |= 1 << first
    return to_graph6(graph).encode('ascii')


def geng(order, edges, min_degree, max_degree):
    return subprocess.run([str(BIN / 'geng'), '-q', f'-d{min_degree}', f'-D{max_degree}',
                           str(order), f'{edges}:{edges}'], capture_output=True,
                          check=True, timeout=15).stdout.splitlines()


def orbit_size(graph):
    def fixes(premap):
        return all((graph[left] >> right & 1) == (graph[premap[left]] >> premap[right] & 1)
                   for left, right in combinations(range(len(graph)), 2))

    return factorial(len(graph)) // sum(map(fixes, permutations(range(len(graph)))))


def target_distributions(baseline):
    with baseline.open() as stream:
        tracked = [tuple(int(row[f'n{degree}']) for degree in range(6, 10))
                   for row in csv.DictReader(stream)
                   if row['e'] == '168' and row['n6'] != '0' and not row['cut']]
    require(len(set(tracked)) == len(tracked) == 20, 'expected exactly 20 distinct input keys')
    require(all(1 <= key[0] <= 2 and sum(key) == 40 and
                sum(degree * count for degree, count in enumerate(key, 6)) == 336 for key in tracked),
            'bad e168 ledger row')
    return set(tracked)


def expected(distributions):
    structured = []
    raw_count = pinned_count = 0
    for row in geng(6, 9, 1, 4):
        graph = parse_graph6(row.decode('ascii'))
        degrees = [nbrs.bit_count() for nbrs in graph]
        if any(graph[left] >> right & 1 and degrees[left] == degrees[right] == 1
               for left, right in combinations(range(6), 2)):
            continue
        orbit = orbit_size(graph)
        raw_count += orbit
        anchored = (1 + degrees.count(1), *(degrees.count(degree) for degree in (2, 3, 4)))
        compatible = {key for key in distributions if key[0] == anchored[0]
                      and all(count >= used for count, used in zip(key, anchored))}
        if compatible:
            pinned_count += orbit
            structured.append((row, compatible))
    return structured, {'raw': raw_count, 'pinned': pinned_count}


def reported(cover):
    header, *lines = cover.read_text().splitlines()
    claimed = re.fullmatch(r'templates (\d+) (\{.*\})', header)
    require(claimed and int(claimed[1]) == len(lines), 'bad template header')
    result = []
    ids_seen = set()
    positions = dict(zip(combinations(range(6), 2), range(15)))
    for line in lines:
        match = re.fullmatch(r'(\d+) (\(.*\)) (\d+) (\(.*\))', line)
        require(match is not None, 'malformed template line')
        template, pairs, count, keys = int(match[1]), literal_eval(match[2]), int(match[3]), literal_eval(match[4])
        require(template not in ids_seen, 'duplicate template ID')
        ids_seen.add(template)
        require(len(pairs) == 9 and count == len(keys) == len(set(keys))
                and template == sum(1 << positions[pair] for pair in pairs), 'bad mask, keys or counts')
        result.append((graph6(6, pairs), set(keys)))
    return result, literal_eval(claimed[2])


def compare(actual, other):
    def keyed(rows):
        return dict(zip(unique_labels([row for row, _ in rows]), (keys for _, keys in rows)))

    reference, candidate = keyed(actual), keyed(other)
    require(reference.keys() == candidate.keys(), 'omitted or unexpected canonical template')
    require(reference == candidate, 'omitted or unexpected distribution pin')


def main(cover, baseline):
    smaller = geng(4, 4, 2, 2)
    require(len(smaller) == 1 and orbit_size(parse_graph6(smaller[0].decode('ascii'))) == 3,
            'incorrect C4 small template generation')
    print('PASS smaller C4 signature: one orbit, three labelled keys')
    roster = target_distributions(baseline)
    official, counts = expected(roster)
    producer, claimed = reported(cover)
    require(len(official) == 14 and counts == claimed == {'raw': 3700, 'pinned': 3700},
            'template attrition differs')
    compare(official, producer)
    expect_rejection(lambda: compare(official, producer[:-1]), 'omitted or unexpected canonical')
    original, keys = producer[0]
    view = parse_graph6(original.decode('ascii'))
    relabelled = next(row for row in (graph6(6, [(left, right) for left, right in combinations(range(6), 2)
                                               if view[order[left]] >> order[right] & 1])
                                      for order in permutations(range(6))) if row != original)
    expect_rejection(lambda: compare(official, [*producer, (relabelled, keys)]), 'duplicate isomorphism')
    expect_rejection(lambda: compare(official, [(original, keys - {min(keys)}), *producer[1:]]), 'distribution pin')
    require(set.union(*(keys for _, keys in official)) == roster, 'not every e168 key represented')
    by_root_count = Counter(next(iter(keys))[0] for _, keys in producer)
    print(f'PASS same {len(official)} canonical templates ({dict(by_root_count)} by n6), {counts}, '
          f'{sum(len(keys) for _, keys in official)} template/distribution pairs, {len(roster)} distributions')
    print('Cover only: no formula, construction or UNSAT verdict audited here')


if __name__ == '__main__':
    main(*(Path(arg) for arg in sys.argv[1:]))
