"""Independent edge-witness replay on exact order-16 controls and target seed marks."""

from argparse import ArgumentParser
from pathlib import Path
from itertools import combinations

from cal_mtf import parse_graph6, to_graph6


def stem(graph, root):
    kept = [other for other in range(len(graph)) if other != root and not (graph[root] >> other & 1)]
    return [sum(((graph[left] >> right) & 1) << pos for pos, right in enumerate(kept))
            for left in kept]


def roots(source, degree, count, tagged):
    previous = set()
    for line in source.open():
        graph = parse_graph6(line)
        for root, neighbors in enumerate(graph):
            if neighbors.bit_count() != degree:
                continue
            base = stem(graph, root)
            if count is None or sum(row.bit_count() for row in base) == 2*count:
                row = to_graph6(base).strip()
                entry = f'{row}\t{line.rstrip()}' if tagged else row
                if entry not in previous:
                    previous.add(entry)
                    print(entry)


def check_star(source, forbidden):
    for line in source.open():
        graph = parse_graph6(line)
        root = len(graph)-1
        full = (1 << len(graph))-1
        for vertex in range(root):
            if not (graph[root] >> vertex & 1):
                continue
            remain = full & ~(graph[root] | graph[vertex])
            if not any(all(not (graph[left] >> right & 1) for left, right in combinations(group, 2))
                       for group in combinations([left for left in range(root) if remain >> left & 1], forbidden-2)):
                break
        else:
            print(line.rstrip())


if __name__ == '__main__':
    parser = ArgumentParser()
    modes = parser.add_subparsers(dest='mode', required=True)
    extraction = modes.add_parser('roots')
    extraction.add_argument('source', type=Path)
    extraction.add_argument('degree', type=int)
    extraction.add_argument('--edges', type=int)
    extraction.add_argument('--tagged', action='store_true')
    check = modes.add_parser('check-star')
    check.add_argument('source', type=Path)
    check.add_argument('forbidden', type=int)
    args = parser.parse_args()
    if args.mode == 'roots':
        roots(args.source, args.degree, args.edges, args.tagged)
    else:
        check_star(args.source, args.forbidden)
