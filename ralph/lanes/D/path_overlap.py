"""Overlap support for forced P6 marks after tentatively adding one exterior edge."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import json
import sys

from path_growth import bits, fixed_graph, pairs, path_lengths, read_profiles
from path_reroot import ROOT, core_instances, decode, fingerprint, neighbors, orientations, placements, profile_key


def optimistic(graph, degree):
    order = len(graph)
    possible = list(graph)
    for src, dst in pairs(range(8, order)):
        if not graph[src] & graph[dst] and graph[src].bit_count() < degree and graph[dst].bit_count() < degree:
            possible[src] |= 1 << dst
            possible[dst] |= 1 << src
    return possible


def upper_masks(graph, upper, core):
    n = len(graph)
    low, high = [], []
    for external in range(n):
        if external not in core:
            low.append(sum(1 << idx for idx, anchor in enumerate(core) if graph[external] >> anchor & 1))
            high.append(sum(1 << idx for idx, anchor in enumerate(core) if upper[external] >> anchor & 1))
    return low, high


def compatible(key, low, high):
    slots = [mask for mask, size in key for _ in range(size)]
    options = [[index for index, cand in enumerate(slots) if (need & ~cand) == (cand & ~allow) == 0]
               for need, allow in zip(low, high)]
    if not all(options):
        return False
    options.sort(key=len)
    mate = {}
    def extend(left, seen):
        for right in options[left]:
            if right not in seen:
                seen.add(right)
                if right not in mate or extend(mate[right], seen):
                    mate[right] = left
                    return True
        return False
    return all(extend(left, set()) for left in range(len(slots)))


class Library:
    def __init__(self, profiles):
        self.keys = sorted({profile_key(oriented) for profile in profiles for oriented in orientations(profile)})
        self.index = {}

    def candidates(self, keep, code):
        if keep not in self.index:
            records = defaultdict(list)
            for key in self.keys:
                records[fingerprint(key, keep)].append(key)
            self.index[keep] = records
        return self.index[keep].get(code, ())

    def supports(self, graph, upper, core, extra=-1):
        keep = sum(1 << index for index, vertex in enumerate(core) if vertex < 8 or vertex == extra)
        low, high = upper_masks(graph, upper, core)
        code = tuple(sorted(Counter(mask & keep for mask in low).items()))
        return any(compatible(key, low, high) for key in self.candidates(keep, code))


def arc_round(profile, library, degree, path_cap, upper=None, planted=None):
    graph = fixed_graph(profile)
    if upper is None:
        upper = optimistic(graph, degree)
    base = set(placements(graph))
    for core in sorted(base):
        if not library.supports(graph, upper, core):
            return 'base-overlap', upper, []
    rejects = []
    checked = 0
    for src, dst in pairs(range(8, len(graph))):
        if not upper[src] >> dst & 1 or (planted is not None and not planted[src] >> dst & 1):
            continue
        graph[src] ^= 1 << dst
        graph[dst] ^= 1 << src
        if any((graph[pivot] & graph[vertex]).bit_count() > 3 for pivot in (src, dst) for vertex in range(len(graph)) if pivot != vertex):
            reason = 'cap'
        elif path_lengths(graph) > path_cap:
            reason = 'path'
        else:
            reason = ''
            for core in placements(graph):
                if core in base and src not in core and dst not in core:
                    continue
                if not library.supports(graph, upper, core):
                    reason = 'overlap'
                    break
        graph[src] ^= 1 << dst
        graph[dst] ^= 1 << src
        if reason:
            upper[src] ^= 1 << dst
            upper[dst] ^= 1 << src
            rejects.append([src, dst, reason])
            if planted is not None:
                raise AssertionError((src, dst, reason))
            if min(upper[src].bit_count(), upper[dst].bit_count()) < degree:
                return 'degree', upper, rejects
        checked += 1
    if planted is not None:
        assert checked == sum((row >> 8).bit_count() for row in planted[8:]) // 2
    for src, dst in pairs(range(len(graph))):
        if not upper[src] >> dst & 1 and not upper[src] & upper[dst]:
            return 'undominated', upper, rejects
    return 'open', upper, rejects


def controls():
    marked = {}
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            assert not cycle
            mask = lambda vertex: sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (mask(vertex), vertex))
            order = core + outer
            marked.setdefault(profile_key(Counter(map(mask, outer))), [sum(1 << index for index, other in enumerate(order) if other in adj[vertex]) for vertex in order])
    library = Library([dict(key) for key in marked])
    count = 0
    for key, graph in marked.items():
        result, _, rejects = arc_round(dict(key), library, 6, 8, planted=graph)
        assert result == 'open' and not rejects
        count += sum((row >> 8).bit_count() for row in graph[8:]) // 2
    print('PASS marked C22 profiles', len(marked), 'planted exterior arc overlays', count, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('receipt', type=Path)
    parser.add_argument('indices', type=int, nargs='*')
    args = parser.parse_args()
    if not args.indices:
        controls()
        sys.exit()
    all_profiles = list(read_profiles(args.source))
    upper = {}
    active = set(args.indices)
    with args.receipt.open('w') as receipt:
        while active:
            library = Library([all_profiles[index] for index in sorted(active)])
            changed = False
            for index in sorted(active.copy()):
                result, allowed, rejects = arc_round(all_profiles[index], library, 9, 6, upper.get(index))
                upper[index] = allowed
                print(index, result, len(rejects), flush=True)
                print(json.dumps([index, result, rejects, allowed]), file=receipt, flush=True)
                changed |= bool(rejects) or result != 'open'
                if result != 'open':
                    active.remove(index)
            if not changed:
                break
    print('survivors', sorted(active), flush=True)
