#!/usr/bin/env python3
"""Compare every small fixed-side completion against explicit full graphs."""
from itertools import combinations
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, parse_graph6, to_graph6, triangle_free


def edge(graph, left, right):
    graph[left] |= 1 << right
    graph[right] |= 1 << left


def oracle(core, sizes, bound):
    pairs = len(sizes)
    owners = [-1] * len(core) + [index for index, size in enumerate(sizes) for _ in range(size)]
    fixed = len(owners)
    template = core + [0] * (fixed + 2 * pairs - len(core))
    for vertex, owner in enumerate(owners):
        if owner != -1:
            edge(template, vertex, fixed + owner)
            edge(template, vertex, fixed + pairs + owner)
    for left in range(pairs):
        for right in range(pairs):
            if left != right:
                edge(template, fixed + left, fixed + pairs + right)
    options = [(left, right) for left, right in combinations(range(fixed), 2)
               if owners[left] != owners[right]]
    accepted = set()
    for mask in range(1 << len(options)):
        graph = template.copy()
        for index, (left, right) in enumerate(options):
            if mask >> index & 1:
                edge(graph, left, right)
        if triangle_free(graph) and brute_alpha(graph) <= bound:
            accepted.add(to_graph6(graph))
    return len(options), accepted


def main():
    for core, sizes, bound, expected in [([0], (1, 1, 1), 4, 22), ([0], (1, 1, 1), 3, 0),
                                         ([0, 0], (2, 1), 5, None), ([2, 1], (2, 1), 4, None)]:
        count, accepted = oracle(core, sizes, bound)
        if expected is not None:
            assert len(accepted) == expected
        test_cases = ((0, 0), (6, 0), (6, 1))
        for seed, sym in test_cases:
            run = subprocess.check_output([sys.argv[1], to_graph6(core), str(bound), str(len(sizes)),
                                           'enum', str(seed), '0', str(sym), *map(str, sizes)], text=True)
            models = [line.split()[1] for line in run.splitlines() if line.startswith('MODEL ')]
            checked = {to_graph6(parse_graph6(line)) for line in models}
            assert len(checked) == len(models)
            assert checked <= accepted and bool(checked) == bool(accepted)
            assert 'EXHAUSTED' in run
            if not sym:
                assert checked == accepted
            print(f'core={to_graph6(core)} sizes={sizes} alpha<={bound} seed={seed} sym={sym}: '
                  f'checked {1 << count} direct assignments, {len(accepted)} valid, SAT returned {len(checked)}')


if __name__ == '__main__':
    main()
