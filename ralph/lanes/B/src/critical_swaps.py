"""Bounded exact-neighbor search at fixed edge count, removing only critical edges."""
import argparse
from collections import deque
import json
from pathlib import Path
import sys

from critical_witness import check, edges, independent, parse_graph6, witness
from check_graph import to_graph6
from profile_filter import keep


def swaps(adjacency, forbidden, brute=False):
    order = len(adjacency)
    vertex_mask = (1 << order) - 1
    result = set()
    for left, right in edges(adjacency):
        remaining = vertex_mask & ~(adjacency[left] | adjacency[right])
        first = independent(adjacency, remaining, forbidden - 2)
        if first is None:
            continue
        if brute:
            allowed = list(range(order))
        else:
            allowed = [left, right]
            for vertex in range(order):
                if first & (1 << vertex) and independent(adjacency, remaining & ~(1 << vertex), forbidden - 2) is None:
                    allowed.append(vertex)
        changed = adjacency.copy()
        changed[left] ^= 1 << right
        changed[right] ^= 1 << left
        for idx, first_endpoint in enumerate(allowed):
            for second_endpoint in allowed[idx+1:]:
                if {first_endpoint, second_endpoint} == {left, right}:
                    continue
                if changed[first_endpoint] & ((1 << second_endpoint)) or changed[first_endpoint] & changed[second_endpoint]:
                    continue
                changed[first_endpoint] ^= 1 << second_endpoint
                changed[second_endpoint] ^= 1 << first_endpoint
                if not brute or independent(changed, vertex_mask, forbidden) is None:
                    result.add(to_graph6(changed))
                changed[first_endpoint] ^= 1 << second_endpoint
                changed[second_endpoint] ^= 1 << first_endpoint
    return result


def walk(input_file, cap):
    seed = json.loads(input_file.read_text())
    if check(seed) != (30, 88) or seed['forbidden'] != 9:
        raise ValueError('walk needs a verified edge-critical order-30 e88 seed')
    visited = {seed['g6']}
    queue = deque([seed['g6']])
    expanded = new_outside_prefix = 0
    while queue and expanded < cap:
        graph = queue.popleft()
        outside = keep((graph + '\n').encode(), 88, {5:58, 6:51, 7:42})
        if outside:
            new_outside_prefix += 1
            result = witness(graph, 9)
            if result is not None:
                check(result)
                print(json.dumps(result))
                break
        for candidate in sorted(swaps(parse_graph6(graph), 9) - visited):
            visited.add(candidate)
            queue.append(candidate)
        expanded += 1
    print(f'labelled graph counts: expanded={expanded}, reached={len(visited)}, '
          f'frontier={len(queue)}, outside_prefix_tested={new_outside_prefix}', file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('calibrate', 'walk'))
    parser.add_argument('input', type=Path)
    parser.add_argument('--forbidden', type=int, default=7)
    parser.add_argument('--cap', type=int, default=256)
    args = parser.parse_args()
    if args.mode == 'walk':
        walk(args.input, args.cap)
    else:
        for line in args.input.open():
            adjacency = parse_graph6(line)
            fast = swaps(adjacency, args.forbidden)
            direct = swaps(adjacency, args.forbidden, brute=True)
            if fast != direct:
                raise ValueError(f'mismatch: {len(fast)} intersection and {len(direct)} direct outputs')
            print(f'calibrated {len(fast)} exact labelled neighbors')
