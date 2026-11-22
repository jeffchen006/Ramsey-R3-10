"""Endpoint-cell joins with pair capacity pruning on the induced P8 root."""

import argparse
import csv
import random
import time
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

from induced_join_cost import PINS, SHARED
from long_root import reverse
from path_growth import ROOT, read_profiles
from punct_path import decode, neighbors, pairs, profile_key


def mapping(order, size):
    return [sum(1 << point for idx, point in enumerate(order) if mask >> idx & 1) for mask in range(size)]


MAPS = [mapping(order, 512) for order in PINS]
FLIP = mapping((1, 0, 9, 8, 7, 6, 5, 4, 3, 2), 1024)


def flip(key):
    return tuple(sorted((FLIP[mask], size) for mask, size in key))


def catalog(source):
    tables = [defaultdict(list), defaultdict(list)]
    directed = 0
    for idx, row in enumerate(read_profiles(source)):
        base = profile_key(row)
        for orientation, key in enumerate(sorted({base, reverse(base)})):
            if (258, 1) not in key:
                continue
            directed += 1
            for side, transform in enumerate(MAPS):
                total, hit = Counter(), Counter()
                for mask, size in key:
                    if mask != 258:
                        fixed = transform[mask] & SHARED
                        total[fixed] += size
                        if mask & 4:
                            hit[fixed] += size
                common = profile_key(total)
                tables[side][common].append((2 * idx + orientation, bytes(hit[mask] for mask, _ in common)))
    return tables, directed


def children(common, left, right, stats):
    low = [max(0, first + second - total) for (_, total), first, second in zip(common, left, right)]
    high = [min(first, second) for first, second in zip(left, right)]
    compulsory = sum(low)
    if compulsory > 3 or not sum(high):
        return
    stats['index_pairs'] += 1
    opts = [idx for idx in range(len(common)) if high[idx] > low[idx]]
    for extras in product(*(range(min(3 - compulsory, high[idx] - low[idx]) + 1) for idx in opts)):
        codegree = compulsory + sum(extras)
        if not 1 <= codegree <= 3:
            continue
        overlap = low.copy()
        for idx, add in zip(opts, extras):
            overlap[idx] += add
        stats['by_c' + str(codegree)] += 1
        both = [mask for (mask, _), size in zip(common, overlap) for _ in range(size)]
        if any((first & second).bit_count() > 1 for first, second in pairs(both)):
            continue
        key = []
        for (mask, total), first, second, together in zip(common, left, right, overlap):
            for extra, number in ((0, total-first-second+together), (4, first-together), (512, second-together), (516, together)):
                if number:
                    key.append((mask | extra, number))
        yield tuple(sorted(key))


def line(key):
    return ' '.join(f'{mask}:{number}' for mask, number in key)


def planted():
    for code in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph = neighbors(22, decode(code))
        if {len(row) for row in graph} != {6} or max(len(left & right) for left, right in pairs(graph)) > 3:
            continue
        for root in range(22):
            for other in graph[root]:
                if other <= root:
                    continue
                block = (graph[root] | graph[other]) - {root, other}
                walks = [(point,) for point in graph[root]-{other}]
                for _ in range(7):
                    walks = [walk+(point,) for walk in walks for point in (graph[walk[-1]] & block)-set(walk)]
                for walk in walks:
                    if walk[-1] not in graph[walk[0]]:
                        yield graph, (root, other)+walk


def graph_key(graph, pins):
    return profile_key(Counter(sum(1 << idx for idx, point in enumerate(pins) if vertex in graph[point]) for vertex in range(len(graph)) if vertex not in pins))


def control(source, dest):
    tables, _ = catalog(source)
    seen = set()
    planted_keys = set()
    for common in tables[0].keys() & tables[1].keys():
        for (_, left), (_, right) in product(tables[0][common], tables[1][common]):
            for key in children(common, left, right, Counter()):
                assert key not in seen
                seen.add(key)
    assert {flip(key) for key in seen} == seen
    counts = Counter()
    for graph, core in planted():
        for pins in (core, (core[1], core[0])+tuple(reversed(core[2:]))):
            key = graph_key(graph, pins)
            assert key in seen
            planted_keys.add(min(key, flip(key)))
            overlaps = Counter()
            for vertex in graph[pins[2]] & graph[pins[9]]:
                assert vertex not in pins
                cell = sum(1 << idx for idx, point in enumerate(pins) if vertex in graph[point]) & SHARED
                overlaps[cell] += 1
            assert dict(overlaps) == {mask & SHARED:size for mask, size in key if mask & 516 == 516}
            counts[sum(overlaps.values())] += 1
    assert sum(counts.values()) == 62
    (dest/'control.tsv').write_text(''.join(line(key)+'\n' for key in sorted(planted_keys)))
    (dest/'control-join.tsv').write_text(''.join(line(key)+'\n' for key in sorted({min(key, flip(key)) for key in seen})))
    print('PASS 31 C22 occurrences, both orientations, direct cell overlaps', dict(counts), 'real orbits', len(planted_keys), 'join labelled', len(seen), 'join orbits', len({min(key, flip(key)) for key in seen}))


COLUMNS = 'bucket left_n right_n population sample index_pairs by_c1 by_c2 by_c3 labelled canonical bytes maxkids survivors elapsed'.split()


def sample(source, dest, per_bucket, seed):
    start = time.process_time()
    tables, directed = catalog(source)
    groups = sorted(tables[0].keys() & tables[1].keys())
    print('catalog CPU-s', time.process_time()-start, 'oriented', directed, 'fingerprints', len(groups), flush=True)
    rng = random.Random(seed)
    with (dest/'buckets.tsv').open('w') as hist, (dest/'sample.tsv').open('w') as output, (dest/'cases.tsv').open('w') as cases:
        writer = csv.DictWriter(hist, COLUMNS, delimiter='\t', extrasaction='ignore'); writer.writeheader()
        print('bucket pair left right children representatives', file=cases)
        for idx, common in enumerate(groups):
            before = time.process_time()
            lefts, rights = [table[common] for table in tables]
            population = len(lefts)*len(rights)
            sample_size = min(population, per_bucket)
            stats = Counter({key:0 for key in COLUMNS})
            stats.update(dict(bucket=idx, left_n=len(lefts), right_n=len(rights), population=population, sample=sample_size))
            for rank in sorted(rng.sample(range(population), sample_size)):
                first, second = divmod(rank, len(rights))
                left_id, left = lefts[first]; right_id, right = rights[second]
                joined = kept = 0
                for key in children(common, left, right, stats):
                    joined += 1
                    if left_id < right_id or (left_id == right_id and key <= flip(key)):
                        kept += 1
                        text = line(key)+'\n'; output.write(text); stats['bytes'] += len(text)
                print(idx, rank, left_id, right_id, joined, kept, file=cases)
                stats.update(dict(labelled=joined, canonical=kept, survivors=int(bool(joined))))
                stats['maxkids'] = max(stats['maxkids'], joined)
            stats['elapsed'] = time.process_time()-before
            writer.writerow(stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path); parser.add_argument('dest', type=Path)
    parser.add_argument('--sample', type=int, default=0); parser.add_argument('--seed', type=int, default=181013)
    args = parser.parse_args()
    if args.sample:
        sample(args.source, args.dest, args.sample, args.seed)
    else:
        control(args.source, args.dest)
