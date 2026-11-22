"""Eight-anchor incidence profiles for an induced P6 in an edge kernel."""

import argparse
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path

from punctured import ROOT, decode, neighbors, pairs


def template(cycle):
    edges = {(src, dst) for src in range(4) for dst in range(4, 8)
             if src == 0 or dst == 4 or src != dst - 4}
    if not cycle:
        edges.remove((1, 6))
    return neighbors(8, edges)


def moves(adj, cap=3):
    pair_caps = {left: cap - len(adj[src] & adj[dst]) for src, dst in pairs(range(8))
                 if dst not in adj[src] and (left := (1 << src) | (1 << dst))}
    subsets = [[] for _ in range(9)]
    for size in range(2, 9):
        for subset in combinations(range(8), size):
            marks = [(1 << src) | (1 << dst) for src, dst in pairs(subset)]
            if all(pair_caps.get(mark, 0) > 0 for mark in marks):
                subsets[size].append((sum(1 << src for src in subset), marks))
    return {mask: room for mask, room in pair_caps.items() if room}, subsets


def symmetry(cycle):
    from itertools import permutations
    adj = template(cycle)
    perms = []
    for left in permutations(range(1, 4)):
        for right in permutations(range(5, 8)):
            ori = (0,) + left + (4,) + right
            for perm in (ori, tuple((vertex + 4) % 8 for vertex in ori)):
                if all((dst in adj[src]) == (perm[dst] in adj[perm[src]]) for src, dst in pairs(range(8))):
                    perms.append(perm)
    return perms


def profiles(order, degree, cycle):
    adj = template(cycle)
    caps, subsets = moves(adj)
    left = [degree - len(row) for row in adj]
    spare = order - 8 + sum(caps.values()) - sum(left)
    high = [item for size in range(3, 9) for item in subsets[size]]
    masks = sorted(caps)
    chosen = {}

    def pairs_at(index, slack):
        if index == len(masks):
            if sum(left) + sum(chosen.values()) + slack == order - 8:
                yield {**{mask: size for mask, size in chosen.items() if size},
                       **{1 << index: size for index, size in enumerate(left) if size}, **({0: slack} if slack else {})}
            return
        mask = masks[index]
        first, second = (index for index in range(8) if mask >> index & 1)
        for count in range(max(0, caps[mask] - slack), min(caps[mask], left[first], left[second]) + 1):
            left[first] -= count
            left[second] -= count
            chosen[mask] = count
            yield from pairs_at(index + 1, slack - caps[mask] + count)
            left[first] += count
            left[second] += count
        chosen.pop(mask, None)

    def high_at(index, slack):
        if index == len(high):
            yield from pairs_at(0, slack)
            return
        mask, marks = high[index]
        vertices = [vertex for vertex in range(8) if mask >> vertex & 1]
        cost = comb(len(vertices) - 1, 2)
        room = min(min(caps[mark] for mark in marks), min(left[vertex] for vertex in vertices), slack // cost)
        for count in range(room + 1):
            chosen[mask] = count
            for vertex in vertices:
                left[vertex] -= count
            for mark in marks:
                caps[mark] -= count
            yield from high_at(index + 1, slack - count * cost)
            for vertex in vertices:
                left[vertex] += count
            for mark in marks:
                caps[mark] += count
        chosen.pop(mask, None)

    yield from high_at(0, spare)


def core_instances(adj):
    for first, row in enumerate(adj):
        for second in sorted(row):
            if first >= second:
                continue
            left, right = adj[first] - {second}, adj[second] - {first}
            for start in left:
                paths = [(start,)]
                for step in range(5):
                    paths = [path + (other,) for path in paths
                             for other in adj[path[-1]] & (right if step % 2 == 0 else left) if other not in path]
                for path in paths:
                    cycle = path[-1] in adj[start]
                    # P6 on labels 1,7,2,5,3,6 in either direction; anchors 0,4.
                    outer = [path[index] for index in (0, 2, 4, 3, 5, 1)]
                    yield cycle, [second] + outer[:3] + [first] + outer[3:]


def profile_key(profile):
    return tuple(sorted(profile.items()))


def permuter(cycle):
    maps = [{mask: sum(1 << perm[vertex] for vertex in range(8) if mask >> vertex & 1)
             for mask in range(256)} for perm in symmetry(cycle)]
    return lambda profile: min(tuple(sorted((mapping[mask], size) for mask, size in profile.items())) for mapping in maps)


def calibration():
    expected, seen, totals = set(), set(), Counter()
    planted = set()
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        expected.add(line)
        for cycle, core in core_instances(adj):
            shape = template(cycle)
            assert all((core[dst] in adj[core[src]]) == (dst in shape[src]) for src, dst in pairs(range(8)))
            if cycle:
                totals['closed P6 in cycle'] += 1
                continue
            totals['induced P6'] += 1
            seen.add(line)
            profile = Counter(sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
                              for vertex in set(range(22)) - set(core))
            planted.add(profile_key(profile))
    assert seen == expected and len(seen) == 3 and totals['induced P6'] == 239
    for profile in profiles(22, 6, False):
        planted.discard(profile_key(profile))
        if not planted:
            break
    assert not planted
    print('PASS exact planted P6 profiles on all three classes;', totals, flush=True)


def p7_rescue(profile):
    adj = template(True)
    for mask, size in profile.items():
        for _ in range(size):
            addition = {vertex for vertex in range(8) if mask >> vertex & 1}
            for vertex in addition:
                adj[vertex].add(len(adj))
            adj.append(addition)
    for full, opp in [(0, 4), (4, 0)]:
        for extra in range(1, 4):
            second = opp + extra
            left, right = adj[full] - {second}, adj[second] - {full}
            for start in right - set(range(8)):
                paths = [(start,)]
                for step in range(6):
                    paths = [path + (other,) for path in paths for other in adj[path[-1]] & (left if step % 2 == 0 else right)
                             if other not in path and not adj[other].intersection(path[:-1])
                             and ((step == 5 and other >= 8) or (step < 5 and other < 8))]
                if paths:
                    # The two outside endpoints are both neighbors of second, hence no unknown chord.
                    return True
    return False


def census(out, cycle):
    canonical = permuter(cycle)
    orbits = set()
    labels = 0
    for profile in profiles(40, 9, cycle):
        if cycle:
            assert p7_rescue(profile)
        labels += 1
        orbits.add(canonical(profile))
    print('C6' if cycle else 'P6', 'profiles labelled/orbits', labels, len(orbits), 'group', len(symmetry(cycle)), flush=True)
    out.write_text(''.join(' '.join(f'{mask}:{size}' for mask, size in rep) + '\n' for rep in sorted(orbits)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    calibration()
    census(args.out / 'cycle.tsv', True)
    census(args.out / 'path.tsv', False)
