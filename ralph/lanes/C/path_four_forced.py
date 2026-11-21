"""Exact P4 window filter: degree, triangle, codegree and MTF propagation."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import time

from kernel_projection import bits, decode
from pair_packages import restrict


def bounds(seed, block):
    order = len(seed)
    total = order + 4 * block + 2
    fixed = list(seed) + [0] * (total - order)
    possible = list(fixed)
    root0, root3, root1, root2 = order - 2, order - 1, total - 2, total - 1
    groups = [range(order + group * block, order + (group + 1) * block) for group in range(4)]

    def permit(left, right):
        possible[left] |= 1 << right
        possible[right] |= 1 << left

    def force(left, right):
        permit(left, right)
        fixed[left] |= 1 << right
        fixed[right] |= 1 << left

    for group, vertices in enumerate(groups):
        endpoint = root0 if group < 2 else root3
        for vertex in vertices:
            force(endpoint, vertex)
            if group < 3:
                force(root1, vertex)
            if group > 0:
                force(root2, vertex)
            for target in range(order - 2):
                if not (seed[endpoint] >> target & 1):
                    permit(vertex, target)
    for left, right in product(groups[0], groups[3]):
        permit(left, right)
    return fixed, possible, tuple(product(groups[0], groups[3]))


class Conflict(Exception):
    pass


def propagate(fixed, possible, degree, cap):
    changed = True
    order = len(fixed)

    def assign(left, right, edge):
        nonlocal changed
        if edge:
            if not (possible[left] >> right & 1):
                raise Conflict('forbid/force conflict')
            if not (fixed[left] >> right & 1):
                fixed[left] |= 1 << right
                fixed[right] |= 1 << left
                changed = True
        else:
            if fixed[left] >> right & 1:
                raise Conflict('force/forbid conflict')
            if possible[left] >> right & 1:
                possible[left] ^= 1 << right
                possible[right] ^= 1 << left
                changed = True

    while changed:
        changed = False
        for vertex, present in enumerate(fixed):
            minimum, maximum = present.bit_count(), possible[vertex].bit_count()
            if not minimum <= degree <= maximum:
                raise Conflict('degree conflict')
            if degree in (minimum, maximum):
                for other in bits(possible[vertex] ^ present):
                    assign(vertex, other, degree == maximum)
        for left, right in combinations(range(order), 2):
            lo = fixed[left] & fixed[right]
            hi = possible[left] & possible[right]
            if lo:
                assign(left, right, False)
                common = lo.bit_count()
                if common > cap:
                    raise Conflict('codegree conflict')
                if common == cap:
                    for third in bits(hi ^ lo):
                        if fixed[left] >> third & 1:
                            assign(right, third, False)
                        if fixed[right] >> third & 1:
                            assign(left, third, False)
            if fixed[left] >> right & 1:
                for third in bits(hi):
                    if fixed[left] >> third & 1:
                        assign(right, third, False)
                    if fixed[right] >> third & 1:
                        assign(left, third, False)
            elif not hi:
                assign(left, right, True)
            elif not (possible[left] >> right & 1) and hi.bit_count() == 1:
                third = hi.bit_length() - 1
                assign(left, third, True)
                assign(right, third, True)


def scan(seed, degree, block, cap, count):
    fixed, possible, cross = bounds(seed, block)
    try:
        propagate(fixed, possible, degree, cap)
    except Conflict as exc:
        return 0, 0, str(exc)
    if not count:
        return 1, 1, 'initial-pass'
    cut = sum(map(int.bit_count, seed)) // 2 - degree * (len(fixed) - 8 * block) // 2
    need = cut - sum((fixed[left] >> right & 1) for left, right in cross)
    unknown = [(left, right) for left, right in cross if (possible[left] ^ fixed[left]) >> right & 1]
    if not 0 <= need <= len(unknown):
        return 0, 0, 'cross-count conflict'
    checked = survivors = 0
    for picked in combinations(range(len(unknown)), need):
        selected = set(picked)
        now, can = list(fixed), list(possible)
        for idx, (left, right) in enumerate(unknown):
            if idx in selected:
                now[left] |= 1 << right
                now[right] |= 1 << left
            else:
                can[left] ^= 1 << right
                can[right] ^= 1 << left
        checked += 1
        try:
            propagate(now, can, degree, cap)
        except Conflict:
            continue
        survivors += 1
    return checked, survivors, 'cross' if survivors else 'all-cross-conflict'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--cross', action='store_true')
    parser.add_argument('--sample', type=int, default=0)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    params = (6, 2, 4) if args.control else (9, 3, 6)
    rows = args.catalogue.read_text().splitlines()
    if args.sample:
        rows = [rows[idx * len(rows) // args.sample] for idx in range(min(len(rows), args.sample))]
    start = time.process_time()
    status = Counter()
    checked = branches = 0
    kept = []
    for row in rows:
        total, survivors, reason = scan(decode(row), *params, args.cross)
        status[reason] += 1
        checked += total
        branches += survivors
        if survivors:
            kept.append(row)
    print('sample' if args.sample else 'complete', dict(status), 'branch counts', checked, branches,
          'kept', len(kept), 'CPU-s', round(time.process_time() - start, 4), flush=True)
    if args.output:
        args.output.write_text(''.join(row + '\n' for row in kept))
    if args.control:
        graph = [sum(1 << ((vertex + step) % 21) for step in (1, -1, 4, -4, 6, -6)) for vertex in range(21)]
        for start, step in product(range(21), (5, -5)):
            verts = [(start + idx * step) % 21 for idx in range(4)]
            allowed = ((1 << 21) - 1) & ~(graph[verts[1]] | graph[verts[2]] | (1 << verts[1]) | (1 << verts[2]))
            root0, _, _, root3 = verts
            ys = list(bits(allowed & graph[root3] & ~(1 << root0)))
            zs = list(bits(allowed & graph[root0] & ~(1 << root3)))
            unmarked = allowed & ~(graph[root0] | graph[root3])
            marked = restrict(graph, list(bits(unmarked)) + ys + zs + [root0, root3])
            assert scan(marked, *params, args.cross)[1] > 0
        print('C21: all 42 explicitly labelled planted root spans retained', flush=True)
        endpoint0, endpoint3 = len(marked) - 2, len(marked) - 1
        marked[endpoint0] ^= 1 << endpoint3
        marked[endpoint3] ^= 1 << endpoint0
        assert scan(marked, *params, args.cross)[1] == 0
        print('C21: corrupted endpoint edge rejected', flush=True)


if __name__ == '__main__':
    main()
