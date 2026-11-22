#!/usr/bin/env python3
"""Profile supplied graphs or emit marked vertex antineighborhoods."""
import argparse
from collections import Counter
from pathlib import Path

from critical_witness import parse_graph6


def encode(rows):
    bits = [bool(rows[right] & (1 << left))
            for right in range(len(rows)) for left in range(right)]
    bits.extend([False] * (-len(bits) % 6))
    return chr(63+len(rows)) + ''.join(
        chr(63+sum(1 << (5-offset) for offset in range(6) if bits[start+offset]))
        for start in range(0, len(bits), 6))


def read_marks(path, degree):
    for line in path.open():
        graph = parse_graph6(line.strip())
        deg = [neighbors.bit_count() for neighbors in graph]
        size = sum(deg)//2
        for root, row in enumerate(graph):
            if deg[root] != degree:
                continue
            inside = [vertex for vertex in range(len(graph)) if vertex == root or row & (1 << vertex)]
            outside = [vertex for vertex in range(len(graph)) if vertex not in inside]
            count = size - sum(deg[vertex] for vertex in inside if vertex != root)
            yield line.strip(), graph, root, count, outside


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('degree', type=int)
    parser.add_argument('--edges', type=int)
    args = parser.parse_args()
    cards = Counter()
    graphs = set()
    for label, graph, root, count, outside in read_marks(args.source, args.degree):
        if args.edges is None:
            cards[count] += 1
            graphs.add((count, label))
        elif count == args.edges:
            induced = [sum(1 << index for index, other in enumerate(outside) if graph[vertex] & (1 << other))
                       for vertex in outside]
            assert sum(row.bit_count() for row in induced) == 2*count
            print(encode(induced), label, root, sep='\t')
    if args.edges is None:
        graph_counts = Counter(count for count, _ in graphs)
        for count in sorted(cards):
            print(count, cards[count], graph_counts[count], sep='\t')


if __name__ == '__main__':
    main()
