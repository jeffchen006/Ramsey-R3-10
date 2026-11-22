"""Exact overlap requirement between induced eight-anchor P6 occurrences."""

import argparse
import json
from collections import Counter
from pathlib import Path

from path_growth import bits, check, fixed_graph, read_profiles
from punct_path import ROOT, core_instances, decode, neighbors, pairs, permuter, profile_key, symmetry, template


def placements(graph):
    return sorted({tuple(core) for cycle, core in core_instances([set(bits(row)) for row in graph]) if not cycle})


def signature(graph, pins, omitted):
    return tuple(sorted(Counter(sum(1 << index for index, pin in enumerate(pins) if pin >= 0 and graph[vertex] >> pin & 1)
                                for vertex in range(len(graph)) if vertex not in omitted).items()))


def orientations(profile):
    for perm in symmetry(False):
        yield {sum(1 << perm[vertex] for vertex in bits(mask)): size for mask, size in profile.items()}


def fingerprint(key, keep):
    counts = Counter()
    for mask, size in key:
        counts[mask & keep] += size
    return tuple(sorted(counts.items()))


def demands(profile):
    graph = fixed_graph(profile)
    out = []
    for core in placements(graph):
        pins = [vertex if vertex < 8 else -1 for vertex in core]
        keep = sum(1 << index for index, vertex in enumerate(pins) if vertex >= 0)
        if keep == 255:
            continue
        out.append((keep, signature(graph, pins, set(core)), core))
    return out


def fixed_point(profiles, receipt):
    records = {index: demands(profile) for index, profile in profiles.items()}
    oriented = {index: [profile_key(other) for other in orientations(profile)] for index, profile in profiles.items()}
    keeps = {keep for rows in records.values() for keep, _, _ in rows}
    active = set(profiles)
    generations = []
    while active:
        library = {(keep, fingerprint(key, keep)) for keep in keeps for index in active for key in oriented[index]}
        failed = {}
        for index in sorted(active):
            for keep, code, core in records[index]:
                if (keep, code) not in library:
                    failed[index] = (index, keep, core, code)
                    break
        if not failed:
            break
        generations.append(len(failed))
        print('deletions', generations, file=receipt)
        for row in failed.values():
            print(json.dumps(row), file=receipt)
        active -= set(failed)
    return generations, active


def controls(receipt):
    canonical = permuter(False)
    planted = set()
    total = 0
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            assert not cycle
            planted.add(canonical(Counter(sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
                                          for vertex in set(range(22)) - set(core))))
            total += 1
    controls = {index: dict(key) for index, key in enumerate(sorted(planted))}
    generations, left = fixed_point(controls, receipt)
    assert not generations and left == set(controls) and total == 239
    print('PASS planted C22 closure across all', total, 'P6s,', len(planted), 'distinct profile orbits', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('filter', type=Path)
    parser.add_argument('receipt', type=Path)
    args = parser.parse_args()
    all_profiles = list(read_profiles(args.source))
    with args.receipt.open('w') as receipt:
        controls(receipt)
        survivors = {index: all_profiles[index] for index, result, _ in map(json.loads, args.filter.read_text().splitlines()) if result == 'open'}
        generations, left = fixed_point(survivors, receipt)
        print('max6', len(survivors), 'waves', generations, 'survive', sorted(left), flush=True)
