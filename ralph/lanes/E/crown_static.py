#!/usr/bin/env python3
"""Static CNF and independent smaller calibration for a projected crown."""
import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys

from calibrate_crown_exact import brute_alpha, edge, oracle, parse_graph6, to_graph6


def subsets(group, size):
    for vertices in combinations(group, size):
        yield vertices


def formula(core, sizes, threshold, pair_threshold=None, cap=False, sort=False,
            min_degree=None, trace=None, w_cap=9, clean=0, anchor_sort=False):
    w = len(core)
    vertices = list(range(w + sum(sizes)))
    offsets = [w]
    for size in sizes:
        offsets.append(offsets[-1] + size)
    groups = [tuple(range(left, right)) for left, right in zip(offsets, offsets[1:])]
    forbidden = {pair for group in groups for pair in combinations(group, 2)}
    pinned = {pair for pair in combinations(range(w), 2) if (core[pair[0]] >> pair[1]) & 1}
    fixed_pairs = set(combinations(range(w), 2))
    ids = {pair: index for index, pair in enumerate((pair for pair in combinations(vertices, 2)
                           if pair not in forbidden and pair not in fixed_pairs), 1)}
    next_id = len(ids)
    clauses = set()
    assert 0 <= clean <= len(groups) and all(len(group) == w for group in groups[:clean])
    for group in groups[:clean]:
        for column, vertex in enumerate(group):
            for fixed in range(w):
                clauses.add(((1 if column + fixed == w - 1 else -1) * ids[(fixed, vertex)],))

    for triple in combinations(vertices, 3):
        pairs = set(combinations(triple, 2)) - pinned
        if pairs <= ids.keys():
            clauses.add(tuple(sorted(-ids[pair] for pair in pairs)))

    def forbid(selected):
        pairs = list(combinations(selected, 2))
        if not pinned.intersection(pairs):
            clauses.add(tuple(sorted(ids[pair] for pair in pairs if pair in ids)))

    def cover(index, remaining, selected):
        if index == len(group_options):
            if not remaining:
                forbid(selected)
            return
        for weight, choices in enumerate(group_options[index]):
            if weight > remaining:
                break
            for choice in choices:
                cover(index + 1, remaining - weight, selected + choice)

    if trace is None:
        options = [list(subsets(range(w), size)) for size in range(min(w, threshold) + 1)]
        group_options = [[list(subsets(group, size + 1)) if size else [()]
                          for size in range(min(threshold, len(group) - 1) + 1)] for group in groups]
        for weight, choices in enumerate(options):
            for choice in choices:
                if not pinned.intersection(combinations(choice, 2)):
                    cover(0, threshold - weight, choice)

        if pair_threshold is not None:
            for group in groups:
                for selected in combinations([vertex for vertex in vertices if vertex not in group], pair_threshold):
                    forbid(selected)
    else:
        for line in trace:
            match = line.split()
            if len(match) != 2 or match[0] != 'CUT':
                raise ValueError('malformed witness row')
            encoded = int(match[1])
            if not 0 < encoded < (1 << len(vertices)):
                raise ValueError('witness mask out of range')
            selected = tuple(vertex for vertex in vertices if (encoded >> vertex) & 1)
            occupied = [any(vertex in group for vertex in selected) for group in groups]
            if not (len(selected) - sum(occupied) >= threshold or
                    (pair_threshold is not None and len(selected) >= pair_threshold and not all(occupied))):
                raise ValueError(f'not an independence violation: {selected}')
            if pinned.intersection(combinations(selected, 2)):
                raise ValueError('witness contains a pinned edge')
            forbid(selected)

    def lex(words):
        nonlocal next_id
        prefix = ()
        for left, right in words:
            next_id += 1
            clauses.add((*prefix, -left, right))
            clauses.add((*prefix, left, right, next_id))
            clauses.add((*prefix, -left, -right, next_id))
            prefix = (-next_id,)

    def at_most(row, limit):
        nonlocal next_id
        if limit >= len(row):
            return
        if limit < 0:
            clauses.add(())
            return
        if not limit:
            for value in row:
                clauses.add((-value,))
            return
        previous = []
        for value in row:
            current = list(range(next_id + 1, next_id + limit + 1))
            next_id += limit
            clauses.add((-value, current[0]))
            for old, new in zip(previous, current):
                clauses.add((-old, new))
            for old, new in zip(previous, current[1:]):
                clauses.add((-value, -old, new))
            if previous:
                clauses.add((-value, -previous[-1]))
            previous = current

    if cap or min_degree is not None:
        for vertex in vertices:
            row = [value for pair, value in ids.items() if vertex in pair]
            pinned_degree = core[vertex].bit_count() if vertex < w else 2
            if cap:
                at_most(row, (w_cap if vertex < w else 9) - pinned_degree)
            if min_degree is not None:
                at_most([-value for value in row], len(row) - (min_degree - pinned_degree))

    if sort:
        for group in groups:
            for left, right in zip(group, group[1:]):
                lex([(ids[(fixed, left)], ids[(fixed, right)]) for fixed in range(w)])
        for index, (left, right) in enumerate(zip(groups, groups[1:]), 1):
            if index != clean and len(left) == len(right):
                words = [(ids[(fixed, first)], ids[(fixed, second)]) for first, second in zip(left, right)
                         for fixed in range(w)]
                if anchor_sort and index >= 2 and clean:
                    words.extend((ids[(fixed, first)], ids[(fixed, second)]) for fixed in groups[0]
                                 for first, second in zip(left, right))
                lex(words)

    return next_id, sorted(clauses, key=lambda clause: (len(clause), clause)), ids


def control():
    for core, sizes, bound in [([0], (1, 1, 1), 4), ([0], (1, 1, 1), 3),
                               ([0, 0], (2, 1), 5), ([2, 1], (2, 1), 4)]:
        k = len(sizes)
        _, valid = oracle(core, sizes, bound)
        nv, cnf, ids = formula(core, sizes, bound + 1 - k, bound - 1)
        assert nv == len(ids)
        checked = set()
        order = len(core) + sum(sizes)
        for bits in product((False, True), repeat=nv):
            if not all(any(bits[abs(literal) - 1] == (literal > 0) for literal in row) for row in cnf):
                continue
            graph = core + [0] * (order + 2 * k - len(core))
            for pair, number in ids.items():
                if bits[number - 1]:
                    edge(graph, *pair)
            start = len(core)
            for index, size in enumerate(sizes):
                for vertex in range(start, start + size):
                    edge(graph, vertex, order + index)
                    edge(graph, vertex, order + k + index)
                start += size
                for other in range(k):
                    if other != index:
                        edge(graph, order + index, order + k + other)
            checked.add(to_graph6(graph))
        assert checked == valid
        print(f'{to_graph6(core)} {sizes} alpha<={bound}: {2**nv} direct assignments, exact {len(valid)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--pair-threshold', type=int)
    parser.add_argument('--degree-cap', action='store_true')
    parser.add_argument('--min-degree', type=int)
    parser.add_argument('--w-cap', type=int, default=9)
    parser.add_argument('--clean', type=int, default=0)
    parser.add_argument('--anchor-sort', action='store_true')
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--sort', action='store_true')
    parser.add_argument('core', nargs='?')
    parser.add_argument('threshold', nargs='?', type=int)
    parser.add_argument('output', nargs='?', type=Path)
    parser.add_argument('sizes', nargs='*', type=int)
    args = parser.parse_args()
    if args.control:
        control()
        return
    assert args.core and args.threshold > 0 and args.sizes and all(size > 0 for size in args.sizes)
    trace = args.trace.read_text().splitlines() if args.trace else None
    nv, cnf, _ = formula(parse_graph6(args.core), args.sizes, args.threshold,
                         args.pair_threshold, args.degree_cap, args.sort, args.min_degree, trace,
                         args.w_cap, args.clean, args.anchor_sort)
    with args.output.open('w') as handle:
        handle.write(f'p cnf {nv} {len(cnf)}\n')
        for clause in cnf:
            handle.write(' '.join(map(str, (*clause, 0))) + '\n')
    print(f'{args.core} {args.sizes}: {nv} vars {len(cnf)} rows by width {sorted(Counter(map(len, cnf)).items())}')


if __name__ == '__main__':
    main()
