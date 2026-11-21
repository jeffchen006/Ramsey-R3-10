"""Exact small-case calibration of the biclique obstruction."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from kernel_projection import MAX_ORDER, bits, decode


def check(adj, alpha):
    order = len(adj)
    width = max(mask.bit_count() for mask in adj)
    counts = Counter()
    for minor in range(1, min(alpha, width) + 1):
        targets = [(major, minor + major + MAX_ORDER[alpha - minor] + MAX_ORDER[alpha - major])
                   for major in range(minor, min(alpha, width) + 1)]
        boundary = {major for major, maximum in targets if order >= maximum}
        if not boundary:
            continue
        possible = {group for neighbors in adj for group in combinations(bits(neighbors), minor)}
        for group in possible:
            common = adj[group[0]]
            for vertex in group[1:]:
                common &= adj[vertex]
                if common.bit_count() < min(boundary):
                    break
            for major, maximum in targets:
                if order >= maximum and common.bit_count() >= major:
                    assert order == maximum, (order, minor, major, group)
                    counts[minor, major] += 1
    return counts


def main():
    parse = argparse.ArgumentParser(description=__doc__)
    parse.add_argument('order22')
    args = parse.parse_args()
    control = [sum(1 << ((vertex + step) % 35) for step in (1,-1,7,-7,11,-11,16,-16))
               for vertex in range(35)]
    print('C35: all strict forbidden shapes absent; equality shapes:', sorted(check(control, 8).items()))
    tally = Counter()
    for line in Path(args.order22).read_text().splitlines():
        tally.update(check(decode(line), 6))
    print('order 22: all strict forbidden shapes absent; equality shapes over ten graphs:', sorted(tally.items()))
    for sides in ((3, 6), (4, 5)):
        first, second = sides
        upper = first + second + MAX_ORDER[9-first] + MAX_ORDER[9-second]
        assert upper == 39
        print('target: shape', sides, 'implies order <=', upper)


if __name__ == '__main__':
    main()
