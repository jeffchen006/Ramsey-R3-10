"""Literal center-first check of the 2P3 Hall cut, independently of idjoin_r23."""

import argparse
from itertools import combinations
from pathlib import Path


def enumerate_rows(adjacency):
    full = set(range(21))
    answer = []
    for sites in combinations(range(21), 5):
        if any(second in adjacency[first] for first, second in combinations(sites, 2)):
            continue
        if set(sites).union(*(adjacency[site] for site in sites)) != full:
            continue
        answer.append(sum(1 << site for site in sites))
    return answer


def mask(sites):
    return sum(1 << site for site in sites)


def run(source):
    edges = [(first, second) for second in range(21) for first in range(second)]
    graphs = with_center = centers = survivors = 0
    for record in source.read_text().splitlines():
        graphs += 1
        assert len(record) == 36 and record[0] == 'T'
        words = [ord(char) - 63 for char in record[1:]]
        adjacency = [set() for _ in range(21)]
        for index, (first, second) in enumerate(edges):
            if words[index // 6] & (1 << (5 - index % 6)):
                adjacency[first].add(second)
                adjacency[second].add(first)
        degree = list(map(len, adjacency))
        candidates = []
        low = mask(site for site in range(21) if degree[site] <= 3)
        for center in range(21):
            if degree[center] != 6 or min(map(degree.__getitem__, adjacency[center])) < 5:
                continue
            required = set(adjacency[center])
            for site in adjacency[center]:
                if degree[site] == 5:
                    tail = adjacency[site] - {center}
                    if any(degree[other] == 6 for other in tail):
                        break
                    required.update(other for other in tail if degree[other] == 5)
            else:
                if len(required) <= 13:
                    candidates.append((center, mask(required)))
        if not candidates:
            continue
        with_center += 1
        centers += len(candidates)
        rows = enumerate_rows(adjacency)
        good = False
        for left, right in combinations(rows, 2):
            shared = left & right
            if shared.bit_count() != 1:
                continue
            first = left | right
            for third in rows:
                if third & first:
                    continue
                used = first | third
                if low & ~used:
                    continue
                singles = used ^ shared
                if any(not ((1 << center) & used) and not (required & ~singles)
                       for center, required in candidates):
                    good = True
                    break
            if good:
                break
        if good:
            survivors += 1
    print(f'{graphs} seeds; {with_center} with a possible center ({centers} marked); '
          f'{survivors} surviving literal joins')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    run(parser.parse_args().source)
