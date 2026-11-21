"""Independent small-case star replacement oracle; use only for calibration."""
import argparse
from itertools import combinations
from pathlib import Path
import sys

from critical_witness import independent, parse_graph6


def graph6(adjacency):
    bits = ''.join('1' if neighbors & (1 << left) else '0'
                   for right, neighbors in enumerate(adjacency) for left in range(right))
    bits += '0' * (-len(bits) % 6)
    return chr(63 + len(adjacency)) + ''.join(chr(63 + int(bits[pos:pos + 6], 2))
                                              for pos in range(0, len(bits), 6))


def star_replacements(adjacency, bound, change):
    vertices = (1 << len(adjacency)) - 1
    for root, old in enumerate(adjacency):
        room = vertices ^ (1 << root)
        target = old.bit_count() + change
        if not 0 <= target <= bound:
            continue
        for subset in combinations((i for i in range(len(adjacency)) if i != root), target):
            star = sum(1 << vertex for vertex in subset)
            if any(adjacency[vertex] & star for vertex in subset):
                continue
            if independent(adjacency, room ^ star, bound) is not None:
                continue
            output = [ns ^ (((ns >> root ^ star >> vertex) & 1) << root)
                      for vertex, ns in enumerate(adjacency)]
            output[root] = star
            yield graph6(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--alpha', type=int, required=True)
    parser.add_argument('--shift', type=int, choices=(-1, 1), default=1)
    parser.add_argument('--first', action='store_true')
    args = parser.parse_args()
    for line in args.input.read_text().splitlines():
        for graph in star_replacements(parse_graph6(line), args.alpha, args.shift):
            print(graph)
            if args.first:
                break
