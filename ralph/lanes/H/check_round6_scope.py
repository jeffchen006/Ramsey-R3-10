#!/usr/bin/env python3
"""Check the frozen case-key merge and the marked two-addition degree profiles."""

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'G'
FIELDS = ('e', 'n6', 'n7', 'n8', 'n9')


def csv_keys(name):
    with (SOURCE / name).open() as stream:
        rows = list(csv.DictReader(line for line in stream if not line.startswith('#')))
    data = {tuple(int(row[field]) for field in FIELDS): row for row in rows}
    assert len(data) == len(rows)
    for edges, *counts in data:
        assert sum(counts) == 40
        assert sum(degree * count for degree, count in zip(range(6, 10), counts)) == 2 * edges
    return data


def key_scope():
    prior = {key: int(row['t9_new']) for key, row in csv_keys('round4_cases.csv').items() if not row['round4_cut']}
    accepted = csv_keys('round5_cases.csv')
    assert prior == {key: int(row['t9_before']) for key, row in accepted.items()}
    after_six = {key: int(row['t9_after']) for key, row in accepted.items() if not row['round5_cut']}
    records = [json.loads(line) for line in (SOURCE / 'floor108_overlap.jsonl').read_text().splitlines()]
    change = defaultdict(list)
    for record in records:
        key = (record['e'], *record['n'])
        assert key in after_six and record['floor7'] == 108
        change[key].append(record)
    floor_cuts = {key for key, rows in change.items() if any(row['kind'] != 't9' for row in rows)}
    after_both = after_six.copy()
    for key in floor_cuts:
        assert len(change[key]) == 1
        del after_both[key]
    for key in change.keys() - floor_cuts:
        threshold = min(row['floor9'] - 1 for row in change[key])
        assert threshold < after_both[key]
        after_both[key] = threshold
    frozen = csv_keys('round6_baseline.csv')
    assert after_both == {key: int(row['t9']) for key, row in frozen.items() if not row['cut']}
    assert floor_cuts == {key for key, row in frozen.items() if row['cut']}
    assert (len(prior), len(after_six), len(after_both)) == (368, 283, 278)
    assert len(floor_cuts) == 5 and (162, 0, 2, 32, 6) in floor_cuts
    assert len(change.keys() - floor_cuts) == 39
    old_tail = {key for key, threshold in after_six.items() if threshold == 88}
    tail = sorted(key for key, threshold in after_both.items() if threshold == 88)
    assert (len(set(tail) - old_tail), len(old_tail - set(tail))) == (4, 4)
    remaining_six = sorted(key for key in after_both if key[0] == 168 and key[1])
    assert len(tail) == 10 and not set(tail).intersection(remaining_six)
    assert Counter(key[1] for key in remaining_six) == {1: 11, 2: 9}
    print('PASS 368 -> 283 -> 278; 39 tightened; 4 out / 4 in U88; e162 counted once')
    print('U88', *tail, sep='\n')
    print('e168 with n6>0', *remaining_six, sep='\n')


def marked_additions():
    vertices = tuple(range(5))
    edges = tuple(combinations(vertices, 2))
    allowed = Counter()
    admissible_profiles = set()
    for special in vertices:
        for degrees in product((7, 8, 9), repeat=5):
            if sum(degrees) != 42 or degrees[special] < 8:
                continue
            profile = tuple(degrees.count(degree) for degree in (7, 8, 9))
            admissible_profiles.add(profile)
            for additions in combinations(edges, 2):
                if any(degrees[vertex] - 1 - (vertex == special) +
                       sum(vertex in edge for edge in additions) != 8 for vertex in vertices):
                    continue
                shared = set(additions[0]).intersection(additions[1])
                allowed[(profile, degrees[special], bool(shared))] += 1
                if shared:
                    center, = shared
                    if profile[0] == 0:
                        assert center == special
                    else:
                        assert degrees[center] == 7
    assert admissible_profiles == {(0, 3, 2), (1, 1, 3)}
    assert set(allowed) == {((0, 3, 2), 8, True), ((0, 3, 2), 9, False), ((1, 1, 3), 9, True)}
    print('PASS marked addition degree identity:', dict(sorted(allowed.items())))


def circulant_control():
    vertices = set(range(13))
    adjacency = {vertex: {(vertex + step) % 13 for step in (-5, -1, 1, 5)} for vertex in vertices}
    assert not any(adjacency[first] & adjacency[second] for first in vertices for second in adjacency[first])
    assert all(adjacency[first] & adjacency[second] for first, second in combinations(vertices, 2)
               if second not in adjacency[first])
    assert not any(all(second not in adjacency[first] for first, second in combinations(candidate, 2))
                   for candidate in combinations(vertices, 5))
    checked = 0
    for root in vertices:
        residue = vertices - {root} - adjacency[root]
        for peer in adjacency[root]:
            boundary = adjacency[peer] - {root}
            exterior = residue - boundary
            assert len(boundary) == 3 and boundary <= residue
            signatures = [adjacency[vertex] & boundary for vertex in exterior]
            doubles = [tuple(sorted(signature)) for signature in signatures if len(signature) == 2]
            assert all(len(signature) in (1, 2) for signature in signatures)
            assert len(doubles) == len(set(doubles)) == 2
            additions = set(combinations(sorted(boundary), 2)) - set(doubles)
            legal = {pair for pair in combinations(sorted(boundary), 2)
                     if not (adjacency[pair[0]] & adjacency[pair[1]] & residue)}
            assert legal == additions and len(legal) == 1
            assert {len(adjacency[vertex] & residue) + sum(vertex in edge for edge in legal)
                    for vertex in boundary} == {3}
            checked += 1
    assert checked == 52
    print('PASS C13(1,5), 52 ordered adjacent-root controls: 2 blocked, 1 legal marked pair each')


if __name__ == '__main__':
    key_scope()
    marked_additions()
    circulant_control()
