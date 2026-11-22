#!/usr/bin/env python3
"""Literal slot-table oracle and physical controls for reroot_shell.cc."""

from argparse import ArgumentParser
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path
import subprocess

from check_root_cover import graph, induced, vertices
from reroot_shell_jobs import mask


def fixtures(adj, count):
    alpha = graph.alpha(adj)
    universe = (1 << len(adj)) - 1
    found = set()
    for first, second, pivot in ((first, second, pivot) for triple in combinations(range(len(adj)), 3)
                                 for pivot in triple for first, second in [tuple(v for v in triple if v != pivot)]):
        if any(adj[v] & mask((first, second, pivot)) for v in (first, second, pivot)):
            continue
        overlap = adj[first] & adj[second] & ~adj[pivot]
        roots = (None, *vertices(overlap))
        for root in roots:
            common = overlap if root is None else overlap ^ (1 << root)
            left = adj[first] & ~adj[second] & ~adj[pivot]
            right = adj[second] & ~adj[first] & ~adj[pivot]
            if not (left and right and common.bit_count() <= 1):
                continue
            if root is not None and (adj[root] & (left | right | common)):
                continue
            core = universe & ~(adj[first] | adj[second] | adj[pivot] | mask((first, second, pivot)))
            smaller = 0 if root is None else adj[root] & core
            if root is not None and not smaller:
                continue
            if common and any(adj[v] & smaller for v in vertices(common)):
                continue
            while (left | right | common).bit_count() > 4:
                if left.bit_count() >= right.bit_count():
                    left &= left - 1
                else:
                    right &= right - 1
            for group in (left, right):
                signatures = [adj[v] & smaller for v in vertices(group)]
                if any(sig.bit_count() > 1 for sig in signatures) or len({sig for sig in signatures if sig}) != sum(
                        bool(sig) for sig in signatures):
                    break
            else:
                shell = tuple(vertices(left | right | common))
                for width in range(1, min(4, (core & ~smaller).bit_count()) + 1):
                    for large in combinations(vertices(core & ~smaller), width):
                        larger = mask(large)
                        if not all(1 <= (adj[v] & larger).bit_count() <= 2 for v in shell):
                            continue
                        key = (root is not None, bool(common), left.bit_count(), right.bit_count())
                        if key in found:
                            continue
                        found.add(key)
                        remap = {label: index for index, label in enumerate(vertices(core))}
                        def mapped(bitmap):
                            return mask(remap[v] for v in vertices(bitmap))
                        old = induced(adj, core)
                        floors = []
                        for group, swapped in ((left, first), (right, second),
                                               (left | right | common, first)):
                            window = core | group | (1 << swapped)
                            if group == left | right | common:
                                window |= 1 << second
                                if root is not None:
                                    window |= 1 << root
                            rows = induced(adj, window)
                            floors.append((min(map(int.bit_count, rows)), sum(map(int.bit_count, rows)) // 2))
                        yield (old, alpha - 3, mapped(smaller), mapped(larger), left.bit_count(), right.bit_count(),
                               common.bit_count(), mapped(smaller), mapped(smaller),
                               [mapped(adj[v] & larger) for v in shell], floors, root is not None)
                        break
                    else:
                        continue
                    break
            if len(found) >= count:
                return


def literal(fixture):
    adj, alpha, small, large, first, second, common, one, two, slots, floors, rooted = fixture
    all_core = (1 << len(adj)) - 1
    free = all_core ^ small ^ large
    base = sum(map(int.bit_count, adj)) // 2

    @lru_cache(maxsize=None)
    def independent_size(allowed):
        return graph.alpha(induced(adj, allowed)) if allowed else 0

    @lru_cache(maxsize=None)
    def available(signature):
        shadow = 0
        for v in vertices(signature):
            shadow |= adj[v]
        return 0 if signature & shadow else signature | (free & ~shadow)

    def distance(signature):
        allowed = available(signature)
        return signature.bit_count() + independent_size(allowed ^ signature)

    def subsets(positions):
        return (q for size in range(1, len(positions) + 1) for q in combinations(positions, size))

    def miss(choices, remove):
        excluded = remove
        for signature in choices:
            excluded |= available(signature)
        return independent_size(all_core & ~excluded)

    stats = Counter()
    visited = set()
    domains = tuple((0, *(1 << v for v in vertices(mask_))) for mask_ in (one, two))
    for copies in set(permutations(slots)):
        for same_first, same_second in product(product(domains[0], repeat=first), product(domains[1], repeat=second)):
            if any(len(set(same) - {0}) != sum(bool(sig) for sig in same) or same.count(0) > 4
                   for same in (same_first, same_second)):
                continue
            groups = (tuple(sorted(opp | same for opp, same in zip(copies[:first], same_first, strict=True))),
                      tuple(sorted(opp | same for opp, same in zip(copies[first:first + second], same_second,
                                                                  strict=True))))
            center = copies[-1] if common else 0
            if (groups, center) in visited:
                continue
            visited.add((groups, center))
            if any(not available(signature) for group in groups for signature in group):
                continue
            if any(len(q) + miss(q, 0) > alpha + 1 for group in groups for q in subsets(group)):
                continue
            stats['open'] += 1
            edge_bounds = [sum(map(distance, group)) for group in groups]
            for group, edge_bound, (floor, edge_floor) in zip(groups, edge_bounds, floors[:2], strict=True):
                if base + len(group) + edge_bound < edge_floor or any(distance(sig) + 1 < floor for sig in group):
                    break
                for idx, row in enumerate(adj):
                    lower = row.bit_count() + sum(sig >> idx & 1 for sig in group)
                    upper = row.bit_count() + sum(available(sig) >> idx & 1 for sig in group)
                    if lower > alpha + 1 or upper < floor:
                        break
                else:
                    continue
                break
            else:
                stats['both'] += 1
                if common and not available(center):
                    continue
                edge_bound = base + sum(edge_bounds) + first + second + (small.bit_count() + 2 if rooted else 0)
                edge_bound += (2 + distance(center)) if common else 0
                edge_bound += sum(not (left & right) for left, right in product(*groups))
                if edge_bound < floors[2][1]:
                    continue
                for left, right in product(((), *subsets(groups[0])), ((), *subsets(groups[1]))):
                    if any(not (p & q) for p, q in product(left, right)):
                        continue
                    selected = left + right
                    for mid, use_root in product((0, 1) if common else (0,), (0, 1) if rooted else (0,)):
                        part = selected + ((center,) if mid else ())
                        if len(part) + use_root + miss(part, small if use_root else 0) > alpha + 2:
                            break
                    else:
                        continue
                    break
                else:
                    stats['joint'] += 1
    return tuple(stats[k] for k in ('open', 'both', 'joint'))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('known', type=Path)
    args = parser.parse_args()
    suite = []
    for row in args.known.read_text().splitlines():
        adj = graph.parse_graph6(row)
        selected = list(fixtures(adj, 3))
        print(f'n={len(adj)} physical positives {len(selected)}, rooted {sum(x[-1] for x in selected)}', flush=True)
        for fixture in selected:
            expect = literal(fixture)
            assert expect[-1] > 0
            suite.append((fixture, expect))
            impossible = (*fixture[:-2], (*fixture[-2][:2], (0, 1000)), fixture[-1])
            rejected = literal(impossible)
            assert rejected[-1] == 0
            suite.append((impossible, rejected))
    assert suite and any(fixture[-1] for fixture, _ in suite)
    rows = []
    for idx, (fixture, _) in enumerate(suite):
        adj, alpha, small, large, first, second, common, one, two, slots, floors, rooted = fixture
        rows += [f'{alpha} {idx} {small} {large} {graph.to_graph6(adj)} 1',
                 ' '.join(map(str, ('control', idx, 0, first, second, common, one, two, len(slots), floors[0][0],
                                     floors[1][0], floors[0][1], floors[1][1], floors[2][1], int(rooted),
                                     *sorted(slots))))]
    result = subprocess.run([args.binary.resolve(), '--all'], input='\n'.join(rows) + '\n',
                            capture_output=True, text=True, check=True, timeout=60)
    observed = [tuple(map(int, row.split()[3:6])) for row in result.stdout.splitlines()]
    assert observed == [expect for _, expect in suite], (observed, [expect for _, expect in suite])
    print(f'{len(suite)} exact literal slot-table controls match all three columns')


if __name__ == '__main__':
    main()
