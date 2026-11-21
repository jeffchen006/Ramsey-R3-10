"""Make or check the edge-deletion witnesses for one Ramsey graph."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from check_graph import parse_graph6, triangle_free, alpha


def independent(adjacency, available, needed):
    if not needed:
        return 0
    while available.bit_count() >= needed:
        first = available & -available
        available ^= first
        result = independent(adjacency, available & ~adjacency[first.bit_length() - 1], needed - 1)
        if result is not None:
            return result | first
    return None


def edges(adjacency):
    return [(left, right) for right, neighbors in enumerate(adjacency)
            for left in range(right) if neighbors & (1 << left)]


def witness(graph, forbidden):
    adjacency = parse_graph6(graph)
    universe = (1 << len(adjacency)) - 1
    witnesses = []
    for left, right in edges(adjacency):
        remaining = universe & ~(adjacency[left] | adjacency[right])
        extra = independent(adjacency, remaining, forbidden - 2)
        if extra is None:
            return None
        witnesses.append(extra | (1 << left) | (1 << right))
    return {'g6': graph, 'forbidden': forbidden, 'after_deletion': witnesses}


def check(result):
    if set(result) != {'g6', 'forbidden', 'after_deletion'}:
        raise ValueError('unexpected certificate fields')
    adjacency = parse_graph6(result['g6'])
    forbidden = result['forbidden']
    if not triangle_free(adjacency) or alpha(adjacency) >= forbidden:
        raise ValueError('input is not a Ramsey graph for the stated independence bound')
    for (left, right), mask in zip(edges(adjacency), result['after_deletion'], strict=True):
        if mask.bit_count() != forbidden or not (0 < mask < (1 << len(adjacency))):
            raise ValueError(f'wrong witness size or vertex for edge {(left, right)}')
        if not (mask & (1 << left) and mask & (1 << right)):
            raise ValueError(f'witness misses endpoint of {(left, right)}')
        for vertex, neighbors in enumerate(adjacency):
            if mask & (1 << vertex):
                others = (1 << right) if vertex == left else (1 << left) if vertex == right else 0
                if neighbors & mask & ~others:
                    raise ValueError(f'witness is not independent after deleting {(left, right)}')
    return len(adjacency), len(edges(adjacency))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('find', 'check', 'count'))
    parser.add_argument('input', type=Path)
    parser.add_argument('--forbidden', type=int, default=9)
    args = parser.parse_args()
    if args.mode == 'check':
        order, size = check(json.loads(args.input.read_text()))
        print(f'checked edge-deletion witnesses: n={order}, e={size}')
    else:
        number = 0
        for line in args.input.open():
            result = witness(line.strip(), args.forbidden)
            if result is not None:
                check(result)
                number += 1
                if args.mode == 'find':
                    print(json.dumps(result))
                    break
        else:
            if args.mode == 'find':
                raise SystemExit('no edge-critical graph in input')
        if args.mode == 'count':
            print(number)
