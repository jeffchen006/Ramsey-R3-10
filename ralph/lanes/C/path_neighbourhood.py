"""Exact independent attachment packing for a five-root residue."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import time

from kernel_projection import bits, decode, encode
from path_windows import canonical, independence_oracle, trianglefree


def independent_size(adj, allowed, size):
    if size == 0:
        yield 0
        return
    while allowed.bit_count() >= size:
        low = allowed & -allowed
        allowed ^= low
        for rest in independent_size(adj, allowed & ~adj[low.bit_length() - 1], size - 1):
            yield rest | low


def attach(adj, masks):
    order = len(adj)
    graph = list(adj) + list(masks) + [0]
    for index, mask in enumerate(masks, order):
        for vertex in bits(mask):
            graph[vertex] |= 1 << index
        graph[index] |= 1 << (len(graph) - 1)
        graph[-1] |= 1 << index
    return graph


def search(adj, degree, alpha, block, cap, limit, emit_all=False, extend=False, audit=None, trace=None):
    order = len(adj)
    full = (1 << order) - 1
    roots = tuple(range(order - 4, order))
    rootmask = sum(1 << root for root in roots)
    need = tuple(degree - mask.bit_count() for mask in adj)
    eligible = []
    for kind, pair in enumerate(zip(roots, roots[1:])):
        mandatory = sum(1 << vertex for vertex in pair)
        permitted = full & ~(rootmask | adj[pair[0]] | adj[pair[1]])
        for free in independent_size(adj, permitted, degree - 3):
            mask = free | mandatory
            if any((neighbors & mask).bit_count() > cap for neighbors in adj):
                continue
            eligible.append((kind, mask))

    num_colours = len(eligible)
    full_colours = (1 << num_colours) - 1
    with_vertex = [0] * order
    with_kind = [0] * 3
    for idx, (kind, mask) in enumerate(eligible):
        with_kind[kind] |= 1 << idx
        for vertex in bits(mask):
            with_vertex[vertex] |= 1 << idx

    initial_empty = []
    for vertex, amount in enumerate(need):
        bound = sum(min(block, (with_vertex[vertex] & source).bit_count()) for source in with_kind)
        if bound < amount:
            initial_empty.append(vertex)
    if initial_empty:
        return 'load', num_colours, 0, (min(initial_empty),), ()

    extension_support = 0
    if extend:
        side = block - 1
        boundary_size = 4 * side
        base = order - 4 - boundary_size
        right_mask = sum(1 << idx for idx in range(base, base + side)) | sum(
            1 << idx for idx in range(base + 2 * side, base + 3 * side))
        left_mask = right_mask << side
        extension_support = sum(1 << idx for idx, (kind, mask) in enumerate(eligible)
                                if ((kind == 0 and mask & right_mask == right_mask) or
                                    (kind == 2 and mask & left_mask == left_mask)))
        if not extension_support:
            return 'cannot-extend-span', num_colours, 0, (), ()

    unreachable = [(left, right) for left, right in combinations(range(order), 2)
                   if not (adj[left] >> right & 1 or adj[left] & adj[right])]
    support = [(with_vertex[left] & with_vertex[right], left, right) for left, right in unreachable]
    for options, left, right in support:
        if not options:
            return 'mtf', num_colours, 0, (left, right), ()
    if extend:
        support.append((extension_support, -1, -1))

    compatible = [0] * num_colours
    independent_large = list(independent_size(adj, full, alpha - 1))
    bytes_independent = (len(independent_large) + 7) // 8
    contains = [bytearray(bytes_independent) for _ in range(order)]
    for idx, mask in enumerate(independent_large):
        byte, bit = divmod(idx, 8)
        for vertex in bits(mask):
            contains[vertex][byte] |= 1 << bit
    index_by_vertex = list(map(lambda row: int.from_bytes(row, 'little'), contains))
    misses = []
    for _, mask in eligible:
        hits = 0
        for vertex in bits(mask):
            hits |= index_by_vertex[vertex]
        misses.append(((1 << len(independent_large)) - 1) ^ hits)
    for idx, (_, mask) in enumerate(eligible):
        for other in range(idx + 1, num_colours):
            right = eligible[other][1]
            if (mask & right).bit_count() < cap and not (misses[idx] & misses[other]):
                compatible[idx] |= 1 << other
                compatible[other] |= 1 << idx

    nodes = 0
    chosen = []
    solutions = []
    remaining = list(need)
    group_count = [block] * 3

    def visit(todo, seen_support):
        nonlocal nodes
        nodes += 1
        if limit and nodes > limit:
            raise OverflowError('node limit')
        if len(chosen) == degree:
            assert not any(remaining) and not any(group_count)
            if audit is not None:
                audit['complete_packs'] += 1
            graph = attach(adj, [eligible[idx][1] for idx in chosen])
            if not independence_oracle(graph)((1 << len(graph)) - 1, alpha + 1):
                solutions.append(encode(graph))
                return not emit_all
            return False

        minimum = num_colours + 1
        pivot = 0
        pivot_id = -1

        def check(domain, quota, row_id):
            nonlocal minimum, pivot, pivot_id
            candidates = domain & todo
            count = candidates.bit_count()
            if count < quota:
                if trace is not None:
                    trace.append(-row_id - 1)
                return False
            if count < minimum:
                minimum, pivot, pivot_id = count, candidates, row_id
            return True

        for row_id, (row, quota) in enumerate(zip(with_kind, group_count)):
            if quota and not check(row, quota, row_id):
                return False
        for row_id, (row, quota) in enumerate(zip(with_vertex, remaining), 3):
            if quota and not check(row, quota, row_id):
                return False
        for flag, (row, _, _) in enumerate(support):
            if not (seen_support >> flag & 1) and not check(row, 1, order + 3 + flag):
                return False

        if trace is not None:
            trace.append(pivot_id)
        for idx in bits(pivot):
            todo ^= 1 << idx
            kind, mask = eligible[idx]
            chosen.append(idx)
            group_count[kind] -= 1
            new = todo & compatible[idx]
            if group_count[kind] == 0:
                new &= ~with_kind[kind]
            for vertex in bits(mask):
                remaining[vertex] -= 1
                if remaining[vertex] == 0:
                    new &= ~with_vertex[vertex]
            flags = seen_support
            for flag, (row, _, _) in enumerate(support):
                if row >> idx & 1:
                    flags |= 1 << flag
            if visit(new, flags):
                return True
            for vertex in bits(mask):
                remaining[vertex] += 1
            group_count[kind] += 1
            chosen.pop()
        return False

    try:
        visit(full_colours, 0)
    except OverflowError:
        return 'limit', num_colours, nodes, (), tuple(solutions)
    return 'found' if solutions else 'tree', num_colours, nodes, (), tuple(solutions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('p5', type=Path)
    parser.add_argument('labelg')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sample', type=int, default=0)
    parser.add_argument('--node-limit', type=int, default=1000000)
    parser.add_argument('--extend', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--trace', type=Path)
    args = parser.parse_args()
    if args.trace and (args.control or args.extend or args.sample or args.node_limit):
        parser.error('--trace requires the full uncapped standard order-40 scan')
    params = (6, 6, 2, 4) if args.control else (9, 9, 3, 6)
    lines = args.p5.read_text().splitlines()
    if args.sample:
        indices = [idx * len(lines) // args.sample for idx in range(min(len(lines), args.sample))]
    else:
        indices = range(len(lines))
    stats = Counter()
    histogram = Counter()
    audit = Counter()
    detail = []
    solutions = set()
    records = []
    start = time.process_time()
    for idx in indices:
        row_trace = [] if args.trace else None
        status, count, nodes, witness, extensions = search(decode(lines[idx]), *params, args.node_limit,
                                                            emit_all=args.control, extend=args.extend,
                                                            audit=audit, trace=row_trace)
        stats[status] += 1
        histogram.update({'sum_colours': count, 'sum_nodes': nodes})
        histogram['max_colours'] = max(histogram['max_colours'], count)
        histogram['max_nodes'] = max(histogram['max_nodes'], nodes)
        detail.append(f'{idx}\t{sha256(lines[idx].encode()).hexdigest()}\t{status}\t{count}\t{nodes}\t{witness}')
        solutions.update(extensions)
        if args.trace:
            records.append([sha256(lines[idx].encode()).hexdigest(), status, witness, row_trace])
    print('sample' if args.sample else 'complete', dict(stats), dict(histogram),
          'complete_packs', audit['complete_packs'], 'CPU-s',
          round(time.process_time() - start, 4), flush=True)
    if args.control and not args.sample:
        control = [sum(1 << ((vertex + step) % 21) for step in (1, -1, 4, -4, 6, -6)) for vertex in range(21)]
        assert trianglefree(control)
        assert canonical([encode(control)], args.labelg)[0] in canonical(sorted(solutions), args.labelg)
        print('positive: C21 recovered as a full regular extension', flush=True)
    if solutions and not args.control:
        for graph in sorted(solutions):
            print('UNVERIFIED CANDIDATE', graph)
    if args.output:
        args.output.write_text(''.join(line + '\n' for line in detail))
    if args.trace:
        if audit['complete_packs'] or stats['limit'] or solutions:
            raise ValueError('scan does not establish no packing')
        args.trace.write_text(''.join(json.dumps(record, separators=(',', ':')) + '\n' for record in records))
    if args.verify:
        if args.verify.read_text().splitlines() != detail:
            raise ValueError('attachment replay mismatch')
        print('attachment replay matches')


if __name__ == '__main__':
    main()
