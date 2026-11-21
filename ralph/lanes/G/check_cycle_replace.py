#!/usr/bin/env python3
"""Exact independent labelled control modulo the marked square's symmetry."""

from collections import defaultdict
from itertools import combinations, permutations, product
from pathlib import Path
import sys

from check_root_cover import graph


def key(rows, marks):
    mask = sum(1 << vertex for vertex in marks)
    sides = tuple(tuple(sorted(rows[vertex] & ~mask for vertex in side))
                  for side in (marks[:2], marks[2:]))
    return tuple(sorted(sides))


def main():
    src, tagged = map(Path, sys.argv[1:3])
    seeds = [graph.parse_graph6(row) for row in src.read_text().splitlines()]
    actual = defaultdict(set)
    for line in tagged.read_text().splitlines():
        seed, first, second, third, fourth, enc = line.split('\t')
        tag = tuple(map(int, (first, second, third, fourth)))
        rows = graph.parse_graph6(enc)
        original = seeds[int(seed) - 1]
        marked = sum(1 << vertex for vertex in tag)
        assert all(not ((original[vertex] ^ rows[vertex]) & (marked if vertex in tag else ~marked))
                   for vertex in range(len(rows)))
        assert graph.alpha(rows) <= 3 and graph.triangle_free(rows)
        assert 10 <= sum(map(int.bit_count, rows)) // 2 <= 12 and min(map(int.bit_count, rows)) >= 2
        sig = key(rows, tag)
        assert sig not in actual[int(seed), tag]
        actual[int(seed), tag].add(sig)
    tags = 0
    for seed, rows in enumerate(seeds, 1):
        for mark_set in combinations(range(len(rows)), 4):
            marks = next((tag for tag in permutations(mark_set) if tag[0] == min(mark_set)
                          and tag[2] < tag[3] and all(rows[left] >> right & 1
                                                     for left in tag[:2] for right in tag[2:])), None)
            if marks is None:
                continue
            tags += 1
            outside = tuple(vertex for vertex in range(len(rows)) if vertex not in marks)
            base = [sum(1 << partner for partner in range(len(rows)) if rows[vertex] >> partner & 1
                        and (vertex in outside) == (partner in outside)) for vertex in range(len(rows))]
            possible = [()] + [(vertex,) for vertex in outside]
            expected = set()
            for attachments in product(possible, repeat=4):
                out = base.copy()
                for left, neighbours in zip(marks, attachments):
                    for right in neighbours:
                        out[left] |= 1 << right
                        out[right] |= 1 << left
                if not 10 <= sum(map(int.bit_count, out)) // 2 <= 12 or min(map(int.bit_count, out)) < 2:
                    continue
                if graph.triangle_free(out) and graph.alpha(out) <= 3:
                    expected.add(key(out, marks))
            assert expected == actual.pop((seed, marks), set()), (seed, marks)
    assert not actual
    print(f'Exact equality at {tags} marked squares')


if __name__ == '__main__':
    main()
