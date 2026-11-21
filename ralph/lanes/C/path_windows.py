"""Exact P4 two-window join; output order is X, Y, Z, v0, v3."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import subprocess
import time

from cycle8_join import labelled_maps
from kernel_projection import bits, decode, encode
from pair_packages import restrict


def canonical(graphs, labelg):
    proc = subprocess.run([labelg, '-q'], input=''.join(graph + '\n' for graph in graphs),
                          text=True, capture_output=True, check=True)
    output = proc.stdout.splitlines()
    if len(output) != len(graphs):
        raise ValueError('wrong labelg output count')
    return output


def independence_oracle(adj):
    @lru_cache(maxsize=16000)
    def has_independent(mask, size):
        if size <= 1:
            return size <= 0 or bool(mask)
        if mask.bit_count() < size:
            return False
        vertex = max(bits(mask), key=lambda index: (adj[index] & mask).bit_count())
        rest = mask ^ (1 << vertex)
        return has_independent(rest & ~adj[vertex], size - 1) or has_independent(rest, size)

    return has_independent


def trianglefree(adj):
    return not any(adj[left] & adj[right] for left, mask in enumerate(adj) for right in bits(mask))


def census_records(census, labelg, mark_count, alpha_window, count_expected, cap, window_order, sample=0):
    graphs = list(map(decode, census))
    if len(graphs) != count_expected or len(set(canonical(census, labelg))) != count_expected:
        raise ValueError('wrong census count or duplicate isomorphism class')
    partials = []
    keys = []
    for adj in graphs:
        count = len(adj)
        full = (1 << count) - 1
        if count != window_order or not trianglefree(adj) or independence_oracle(adj)(full, alpha_window + 1):
            raise ValueError('bad census graph')
        for marked in combinations(range(count), mark_count):
            if any(adj[left] >> right & 1 for left, right in combinations(marked, 2)):
                continue
            if any((adj[left] & adj[right]).bit_count() + 1 > cap for left, right in combinations(marked, 2)):
                continue
            unmarked = [idx for idx in range(count) if idx not in marked]
            core = restrict(adj, unmarked)
            masks = tuple(sum(1 << idx for idx, value in enumerate(unmarked) if adj[vertex] >> value & 1)
                          for vertex in marked)
            keys.append(encode(core))
            partials.append((core, masks))
    classes = defaultdict(list)
    for key, partial in zip(canonical(keys, labelg), partials):
        classes[key].append(partial)
    print('input placements', len(partials), 'core families', len(classes), flush=True)
    if sample:
        ordered = sorted(classes)
        classes = {ordered[idx * len(ordered) // sample]: classes[ordered[idx * len(ordered) // sample]]
                   for idx in range(min(len(ordered), sample))}
    for key, group in sorted(classes.items()):
        core = decode(key)
        types = set()
        for original, masks in group:
            covered = False
            for mapping in labelled_maps(original, core):
                covered = True
                types.add(tuple(sorted(sum(1 << mapping[index] for index in bits(mask)) for mask in masks)))
            if not covered:
                raise ValueError('canonical label did not provide an isomorphism')
        yield core, tuple(sorted(types)), len(group)


def combine(core, left, right, cross):
    order = len(core)
    side = len(left)
    root0 = order + 2 * side
    root3 = root0 + 1
    adj = list(core) + [0] * (2 * side + 2)

    def add_edge(source, target):
        adj[source] |= 1 << target
        adj[target] |= 1 << source

    for index, mask in enumerate(left + right):
        vertex = order + index
        for neighbor in bits(mask):
            add_edge(vertex, neighbor)
        add_edge(vertex, root3 if index < side else root0)
    for index in bits(cross):
        left_index, right_index = divmod(index, side)
        add_edge(order + left_index, order + side + right_index)
    add_edge(root0, root3)
    return adj


def scan(census, labelg, order, degree, alpha, block, cap, count_expected, edge_floor, sample=0):
    mark_count = block - 1
    full = order - 2 - 4 * block
    window_order = full - block - 1
    base_edges = order * degree // 2 - 4 * block * degree
    min_edge = max(base_edges, edge_floor)
    max_edge = base_edges + block * block
    stats = Counter()
    results = set()
    for core, types, placements in census_records(census, labelg, mark_count, alpha - 3,
                                                  count_expected, cap, window_order, sample):
        stats['placements'] += placements
        stats['families'] += 1
        stats['types'] += len(types)
        core_edges = sum(mask.bit_count() for mask in core) // 2
        for left_index, left in enumerate(types):
            for right in types[left_index:]:
                stats['type_pairs'] += 1
                pairs = list(product(left, right))
                permitted = sum(1 << index for index, (first, second) in enumerate(pairs) if not first & second)
                used_edges = core_edges + 2 * mark_count + 1 + sum(mask.bit_count() for mask in left + right)
                if not (used_edges <= max_edge and used_edges + permitted.bit_count() >= min_edge):
                    continue
                stats['edge_range'] += 1
                cross = permitted
                while True:
                    if min_edge <= used_edges + cross.bit_count() <= max_edge:
                        adj = combine(core, left, right, cross)
                        degrees = [mask.bit_count() for mask in adj]
                        if min(degrees) >= full - 1 - window_order and max(degrees) <= alpha - 2:
                            stats['degree'] += 1
                            if not any((adj[first] & adj[second]).bit_count() > cap
                                       for first, second in combinations(range(full), 2)):
                                stats['codegree'] += 1
                                if not independence_oracle(adj)((1 << full) - 1, alpha - 1):
                                    stats['alpha'] += 1
                                    results.add(encode(adj))
                    if cross == 0:
                        break
                    cross = (cross - 1) & permitted
    return results, stats, (full - 2 * block, mark_count)


def verify_controls(results, stats, labelg):
    adj = [sum(1 << ((vertex + step) % 21) for step in (1, -1, 4, -4, 6, -6)) for vertex in range(21)]
    assert trianglefree(adj) and not independence_oracle(adj)((1 << 21) - 1, 7)
    cover = set(canonical(sorted(results), labelg))
    sources = set()
    for start, step in product(range(21), (5, -5)):
        root0, root1, root2, root3 = [(start + index * step) % 21 for index in range(4)]
        assert all((adj[left] & adj[right]).bit_count() == 4
                   for left, right in zip((root0, root1, root2), (root1, root2, root3)))
        allowed = ((1 << 21) - 1) & ~(adj[root1] | adj[root2] | (1 << root1) | (1 << root2))
        sources.add(encode(restrict(adj, list(bits(allowed)))))
    assert set(canonical(sorted(sources), labelg)) <= cover
    assert stats['alpha'] > 0
    print('positive: 42 oriented C21 paths recovered', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    parser.add_argument('labelg')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sample', type=int, default=0)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    params = (21, 6, 6, 2, 4, 3, 0) if args.control else (40, 9, 9, 3, 6, 191, 73)
    census = args.census.read_text().splitlines()
    start = time.process_time()
    results, stats, layout = scan(census, args.labelg, *params, sample=args.sample)
    print('sample' if args.sample else 'complete', 'census', len(census), 'layout', layout,
          'stats', dict(stats), 'unique rows', len(results), 'CPU-s', round(time.process_time() - start, 4), flush=True)
    if args.control and not args.sample:
        verify_controls(results, stats, args.labelg)
    if args.output:
        args.output.write_text(''.join(graph + '\n' for graph in sorted(results)))
    if args.verify:
        listed = args.verify.read_text().splitlines()
        if listed != sorted(results):
            raise ValueError('missing, malformed, duplicated, extraneous or out-of-order join row')
        print('join coverage exactly replayed', flush=True)


if __name__ == '__main__':
    main()
