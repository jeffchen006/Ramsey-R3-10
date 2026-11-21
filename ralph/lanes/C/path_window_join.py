"""Join two P4 rows across their common triple window to cover P5."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
import time

from cycle8_join import labelled_maps
from kernel_projection import bits, decode, encode
from pair_packages import restrict
from path_windows import canonical, independence_oracle, trianglefree


def ports(lines, labelg, block, sample):
    side = block - 1
    local = defaultdict(set)
    for adj in map(decode, lines):
        core_size = len(adj) - 2 * block
        ys = list(range(core_size, core_size + side))
        zs = list(range(core_size + side, core_size + 2 * side))
        for marked, outside in ((zs, ys), (ys, zs)):
            window_order = list(range(core_size)) + marked
            window = encode(restrict(adj, window_order))
            outside_masks = tuple(sorted(sum(1 << idx for idx, v in enumerate(window_order)
                                             if adj[vertex] >> v & 1) for vertex in outside))
            local[window].add(outside_masks)
    keys = sorted(local)
    families = defaultdict(list)
    for key, representative in zip(keys, canonical(keys, labelg)):
        families[representative].append(key)
    print('input ports', sum(map(len, local.values())), 'window families', len(families), flush=True)
    if sample:
        ordered = sorted(families)
        families = {ordered[idx * len(ordered) // sample]: families[ordered[idx * len(ordered) // sample]]
                    for idx in range(min(len(ordered), sample))}
    for representative, windows in sorted(families.items()):
        window = decode(representative)
        core_size = len(window) - side
        entries = set()
        for labelled in windows:
            aligned = False
            for mapping in labelled_maps(decode(labelled), window):
                aligned = True
                mark = sum(1 << mapping[idx] for idx in range(core_size, len(window)))
                for masks in local[labelled]:
                    masks_in_rep = tuple(sorted(sum(1 << mapping[idx] for idx in bits(mask)) for mask in masks))
                    entries.add((mark, masks_in_rep))
            if not aligned:
                raise ValueError('unmatched canonical window')
        yield window, sorted(entries)


def combine(window, left, right, cross):
    left_mark, left_outer = left
    right_mark, right_outer = right
    window_size = len(window)
    side = len(left_outer)
    root0 = window_size + 2 * side
    root1, root3, root4 = root0 + 1, root0 + 2, root0 + 3
    adj = list(window) + [0] * (2 * side + 4)

    def add_edge(source, target):
        adj[source] |= 1 << target
        adj[target] |= 1 << source

    for index, mask in enumerate(left_outer + right_outer):
        vertex = window_size + index
        for neighbor in bits(mask):
            add_edge(vertex, neighbor)
        if index < side:
            add_edge(vertex, root3)
            add_edge(vertex, root4)
        else:
            add_edge(vertex, root1)
            add_edge(vertex, root0)
    for vertex in bits(left_mark):
        add_edge(vertex, root0)
    for vertex in bits(right_mark):
        add_edge(vertex, root4)
    for index in bits(cross):
        left_index, right_index = divmod(index, side)
        add_edge(window_size + left_index, window_size + side + right_index)
    add_edge(root0, root3)
    add_edge(root1, root4)
    add_edge(root0, root4)
    permutation = (list(bits(((1 << window_size) - 1) ^ (left_mark | right_mark))) +
                   list(bits(right_mark)) + list(bits(left_mark)) + list(range(window_size, len(adj))))
    return restrict(adj, permutation)


def scan(lines, labelg, order, degree, alpha, block, cap, sample=0):
    stats = Counter()
    results = set()
    side = block - 1
    target = order * degree // 2 - degree * degree
    for window, entries in ports(lines, labelg, block, sample):
        stats['families'] += 1
        stats['ports'] += len(entries)
        window_edges = sum(mask.bit_count() for mask in window) // 2
        for left, right in combinations(entries, 2):
            stats['pairs'] += 1
            left_mark, left_outer = left
            right_mark, right_outer = right
            if left_mark & right_mark or any(mask & right_mark for mask in left_outer) or any(mask & left_mark for mask in right_outer):
                continue
            stats['disjoint'] += 1
            used = window_edges + 6 * side + 3 + sum(mask.bit_count() for mask in left_outer + right_outer)
            pairs = list(product(left_outer, right_outer))
            permitted = sum(1 << idx for idx, (first, second) in enumerate(pairs) if not first & second)
            if not 0 <= target - used <= permitted.bit_count():
                continue
            stats['edge_range'] += 1
            for selected in combinations(bits(permitted), target - used):
                adj = combine(window, left, right, sum(1 << idx for idx in selected))
                degrees = [mask.bit_count() for mask in adj]
                assert sum(degrees) == 2 * target
                if min(degrees) < degree - cap or max(degrees) > alpha - 1:
                    continue
                if not trianglefree(adj):
                    continue
                stats['degree_tf'] += 1
                if any((adj[first] & adj[second]).bit_count() > cap for first, second in combinations(range(len(adj)), 2)):
                    continue
                stats['codegree'] += 1
                if not independence_oracle(adj)((1 << len(adj)) - 1, alpha):
                    stats['alpha'] += 1
                    results.add(encode(adj))
    return results, stats


def control(results, labelg):
    adj = [sum(1 << ((vertex + step) % 21) for step in (1, -1, 4, -4, 6, -6)) for vertex in range(21)]
    cover = set(canonical(sorted(results), labelg))
    residues = set()
    for start, step in product(range(21), (5, -5)):
        root = (start + 2 * step) % 21
        allowed = ((1 << 21) - 1) & ~(adj[root] | (1 << root))
        residues.add(encode(restrict(adj, list(bits(allowed)))))
    if not set(canonical(sorted(residues), labelg)) <= cover:
        raise ValueError('lost a positive C21 P5 control')
    print('positive: 42 C21 five-root spans recovered', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('p4', type=Path)
    parser.add_argument('labelg')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sample', type=int, default=0)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    start = time.process_time()
    params = (21, 6, 6, 2, 4) if args.control else (40, 9, 9, 3, 6)
    results, stats = scan(args.p4.read_text().splitlines(), args.labelg, *params, sample=args.sample)
    print('sample' if args.sample else 'complete', 'P5 join:', dict(stats), 'unique rows', len(results),
          'CPU-s', round(time.process_time() - start, 4), flush=True)
    if args.control and not args.sample:
        control(results, args.labelg)
    if args.output:
        args.output.write_text(''.join(graph + '\n' for graph in sorted(results)))
    if args.verify:
        listed = args.verify.read_text().splitlines()
        if listed != sorted(results):
            raise ValueError('missing, malformed, duplicated, extraneous or out-of-order P5 row')
        print('join coverage exactly replayed', flush=True)


if __name__ == '__main__':
    main()
