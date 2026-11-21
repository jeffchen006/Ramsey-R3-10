#!/usr/bin/env python3
"""Reconstruct P5 by overlapping whole P4 rows; check labels modulo reversal."""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

from check_path_cover import (all_maps, alpha, bits, canonical, induced,
                              parse_graph6, to_graph6, triangle_free)


@dataclass(frozen=True)
class Parameters:
    window: int
    side: int
    edges: int
    min_degree: int
    max_degree: int
    independence: int
    codegree: int

    @property
    def order(self):
        return self.window + 2 * self.side + 4


CONTROL = Parameters(8, 1, 27, 2, 5, 5, 4)
TARGET = Parameters(22, 2, 99, 3, 8, 8, 6)


def reverse(adj, params):
    start = params.window - 2 * params.side
    groups = [range(start + index * params.side, start + (index + 1) * params.side)
              for index in range(4)]
    order = (list(range(start)) + list(groups[1]) + list(groups[0])
             + list(groups[3]) + list(groups[2])
             + list(reversed(range(params.order - 4, params.order))))
    return induced(adj, order)


def key(adj, params):
    if len(adj) != params.order:
        raise ValueError('incorrect P5 order')
    return min(to_graph6(adj), to_graph6(reverse(adj, params)))


def p4_rows(lines, labelg, params):
    core_size = params.window - params.side
    side_y = tuple(range(core_size, params.window))
    side_z = tuple(range(params.window, params.window + params.side))
    first_root = params.window + params.side
    records = defaultdict(list)
    for line in lines:
        adj = tuple(parse_graph6(line))
        if to_graph6(adj) != line or len(adj) != first_root + 2:
            raise ValueError('malformed P4 row')
        for mark, outer, root_first, root_last in (
                (side_z, side_y, first_root, first_root + 1),
                (side_y, side_z, first_root + 1, first_root)):
            shared = tuple(range(core_size)) + mark
            records[to_graph6(induced(adj, shared))].append(
                (adj, shared, outer, root_first, root_last))
    windows = sorted(records)
    by_label = defaultdict(set)
    for window, label in zip(windows, canonical(windows, labelg), strict=True):
        window_adj = tuple(parse_graph6(window))
        carrier = tuple(parse_graph6(label))
        maps = tuple(all_maps(window_adj, carrier))
        if not maps:
            raise ValueError('failed to align shared window')
        for image in maps:
            mapped_mark = tuple(sorted(image[core_size:]))
            for adj, shared, outer, root_first, root_last in records[window]:
                outer_order = sorted(outer, key=lambda v: sum(1 << target for source, target
                                     in zip(shared, image) if adj[v] >> source & 1))
                placements = sorted((target, source) for source, target in zip(shared, image))
                source_order = [source for _, source in placements] + outer_order + [root_first, root_last]
                by_label[label].add((mapped_mark, induced(adj, source_order)))
    return by_label


def add_edge(adj, left, right):
    adj[left] |= 1 << right
    adj[right] |= 1 << left


def complete_pair(left, right, params):
    left_mark, left_adj = left
    right_mark, right_adj = right
    if set(left_mark) & set(right_mark):
        return
    width, side = params.window, params.side
    root0, root1, root3, root4 = range(params.order - 4, params.order)
    p4 = list(range(width, width + side))
    p0 = list(range(width + side, width + 2 * side))
    if any(left_adj[index] >> vertex & 1 for index in p4 for vertex in right_mark):
        return
    if any(right_adj[index] >> vertex & 1 for index in p4 for vertex in left_mark):
        return
    shared = list(range(width))
    base = [0] * params.order
    for row, positions in ((left_adj, shared + p4 + [root0, root3]),
                           (right_adj, shared + p0 + [root4, root1])):
        for source, mask in enumerate(row):
            for target in bits(mask & ((1 << source) - 1)):
                add_edge(base, positions[source], positions[target])
    add_edge(base, root0, root4)
    for vertex in p4:
        add_edge(base, vertex, root4)
    for vertex in p0:
        add_edge(base, vertex, root0)
    missing = params.edges - sum(row.bit_count() for row in base) // 2
    allowed = [(first, second) for first, second in product(p4, p0)
               if not base[first] & base[second]]
    if missing < 0 or missing > len(allowed):
        return
    order = (sorted(set(shared) - set(left_mark) - set(right_mark)) + list(right_mark)
             + list(left_mark) + p4 + p0 + [root0, root1, root3, root4])
    for edges in combinations(allowed, missing):
        adj = base.copy()
        for first, second in edges:
            add_edge(adj, first, second)
        if (all(params.min_degree <= row.bit_count() <= params.max_degree for row in adj)
                and triangle_free(adj)
                and all((adj[first] & adj[second]).bit_count() <= params.codegree
                        for first, second in combinations(range(params.order), 2))
                and alpha(adj) <= params.independence):
            yield key(induced(adj, order), params)


def planted(results, labelg):
    adj = tuple(sum(1 << ((vertex + offset) % 21) for offset in (-6, -4, -1, 1, 4, 6))
                for vertex in range(21))
    if alpha(adj) != 6 or not triangle_free(adj):
        raise ValueError('wrong C21 control')
    records = []
    for start, step in product(range(21), (-5, 5)):
        roots = [(start + step * index) % 21 for index in range(5)]
        root0, root1, root2, root3, root4 = roots
        if any((adj[first] & adj[second]).bit_count() != CONTROL.codegree
               for first, second in zip(roots, roots[1:])):
            raise ValueError('wrong planted path')
        excluded = [adj[vertex] | (1 << vertex) for vertex in roots]
        residue = ((1 << 21) - 1) & ~excluded[2]
        shared = residue & ~excluded[1] & ~excluded[3]
        p5, pm1 = shared & adj[root4], shared & adj[root0]
        outer = residue & ~shared & ~sum(1 << root for root in roots)
        p4, p0 = outer & adj[root3], outer & adj[root1]
        inner = shared & ~p5 & ~pm1
        groups = [inner, p5, pm1, p4, p0]
        if [group.bit_count() for group in groups] != [6, 1, 1, 1, 1]:
            raise ValueError('wrong planted marking')
        shared_order = list(bits(shared))
        records.append((to_graph6(induced(adj, shared_order)), shared_order, groups,
                        [root0, root1, root3, root4]))
    alignment_count = 0
    for (line, shared_order, groups, roots), label in zip(
            records, canonical([row[0] for row in records], labelg), strict=True):
        maps = tuple(all_maps(tuple(parse_graph6(line)), tuple(parse_graph6(label))))
        if not maps:
            raise ValueError('missing planted alignment')
        for image in maps:
            position = dict(zip(shared_order, image))
            order = (sorted(bits(groups[0]), key=position.__getitem__)
                     + [vertex for group in groups[1:] for vertex in bits(group)] + roots)
            if key(induced(adj, order), CONTROL) not in results:
                raise ValueError('missing marked planted P5 residue')
            alignment_count += 1
    print(f'PASS {len(records)} oriented C21 spans, {alignment_count} exact marked alignments')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('p4', type=Path)
    parser.add_argument('p5', type=Path)
    parser.add_argument('--labelg', required=True)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    params = CONTROL if args.control else TARGET
    p4_lines = args.p4.read_text().splitlines()
    if len(p4_lines) != len(set(p4_lines)):
        raise ValueError('duplicate P4 inputs')
    banks = p4_rows(p4_lines, args.labelg, params)
    results = set()
    tries = 0
    for rows in banks.values():
        for left, right in combinations(sorted(rows), 2):
            tries += 1
            results.update(complete_pair(left, right, params))
    print(f'{len(p4_lines)} P4 rows, {len(banks)} middle-window classes, {tries} pairs, '
          f'{len(results)} computed rows modulo reversal', flush=True)
    if args.control:
        planted(results, args.labelg)
    if args.write:
        args.write.write_text(''.join(row + '\n' for row in sorted(results)))
    supplied = args.p5.read_text().splitlines()
    observed = set()
    for line in supplied:
        adj = tuple(parse_graph6(line))
        if to_graph6(adj) != line:
            raise ValueError('malformed P5 graph6 row')
        observed.add(key(adj, params))
    if len(observed) != len(supplied):
        raise ValueError('duplicate P5 rows modulo reversal')
    if observed != results:
        raise ValueError(f'P5 labelled cover mismatch: missing={len(results - observed)} '
                         f'extra={len(observed - results)}')
    print('PASS exact P5 set modulo reversal; P4/P5 SHA-256:',
          sha256(args.p4.read_bytes()).hexdigest(), sha256(args.p5.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
