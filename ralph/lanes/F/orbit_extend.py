#!/usr/bin/env python3
"""Extend by a single orbit of 2–5 vertices, preserving a specified automorphism."""

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
from check_graph import parse_graph6, to_graph6


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def perm_for(cycles):
    permutation = []
    for length in cycles:
        start = len(permutation)
        permutation.extend(start + (index + 1) % length for index in range(length))
    return permutation


def image(mask, permutation):
    return sum(1 << permutation[index] for index in vertices(mask))


def independent(mask, neighbors):
    return all(not (neighbors[index] & mask) for index in vertices(mask))


def independent_sets(neighbors, candidates, size, chosen=0):
    if not size:
        yield chosen
    else:
        while candidates.bit_count() >= size:
            bit = candidates & -candidates
            candidates ^= bit
            yield from independent_sets(neighbors, candidates & ~neighbors[bit.bit_length() - 1],
                                        size - 1, chosen | bit)


def orbit_patterns(length):
    for steps in range(1 << (length // 2)):
        neighbors = [0] * length
        for offset in range(1, length // 2 + 1):
            if steps & (1 << (offset - 1)):
                for index in range(length):
                    neighbors[index] |= (1 << ((index + offset) % length)) | (1 << ((index - offset) % length))
        if all(independent(mask, neighbors) for mask in neighbors):
            yield steps, neighbors


def make_cnf(base, inverse, pattern, indsets):
    clauses = set()
    for left, neighbors in enumerate(base):
        for right in vertices(neighbors & ((1 << left) - 1)):
            clauses.add((-left - 1, -right - 1))
    for offset in vertices(pattern[0]):
        for vertex in range(len(base)):
            clauses.add(tuple(sorted(set((-vertex - 1, -inverse[offset][vertex] - 1)))))
    for subset in range(1, 1 << len(pattern)):
        if not independent(subset, pattern):
            continue
        rotations = [sum(1 << ((index + shift) % len(pattern)) for index in vertices(subset))
                     for shift in range(len(pattern))]
        if subset != min(rotations):
            continue
        for mask in indsets[subset.bit_count()]:
            covering = 0
            for new_index in vertices(subset):
                covering |= image(mask, inverse[new_index])
            clauses.add(tuple(vertex + 1 for vertex in vertices(covering)))
    return clauses


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('graph', type=Path)
    arg.add_argument('cycles', help='comma-separated lengths of base vertex cycles, in order')
    arg.add_argument('orbit', type=int, choices=range(2, 6))
    arg.add_argument('k', type=int)
    arg.add_argument('prefix', type=Path)
    args = arg.parse_args()
    cycles = list(map(int, args.cycles.split(',')))
    [line] = args.graph.read_text().strip().splitlines()
    base = parse_graph6(line)
    total = len(base) + args.orbit
    if any(length <= 0 or args.orbit % length for length in cycles) or sum(cycles) != len(base):
        arg.error('cycles must cover the base and their lengths must divide orbit length')
    if not args.orbit < args.k <= total < 63:
        arg.error('require orbit length < k <= total order < 63')
    all_base = (1 << len(base)) - 1
    permutation = perm_for(cycles)
    if any(image(base[index], permutation) != base[permutation[index]] for index in range(len(base))):
        arg.error('input graph does not have the requested symmetry')
    if any(not independent(mask, base) for mask in base) or next(independent_sets(base, all_base, args.k), None) is not None:
        arg.error('base is not a valid Ramsey graph')
    forward = [list(range(len(base)))]
    for _ in range(1, args.orbit):
        forward.append([permutation[index] for index in forward[-1]])
    inverse = [forward[-offset % args.orbit] for offset in range(args.orbit)]
    indsets = {count: list(independent_sets(base, all_base, args.k - count))
               for count in range(1, args.orbit + 1)}
    unresolved = False
    for steps, pattern in orbit_patterns(args.orbit):
        clauses = make_cnf(base, inverse, pattern, indsets)
        cnf = Path(f'{args.prefix}.pattern{steps}.cnf')
        with cnf.open('w') as stream:
            stream.write(f'p cnf {len(base)} {len(clauses)}\n')
            for clause in sorted(clauses):
                stream.write(' '.join(map(str, clause)) + ' 0\n')
        result = subprocess.run([str(ROOT / 'opt/bin/cadical'), str(cnf)],
                                capture_output=True, text=True, check=False)
        Path(f'{args.prefix}.pattern{steps}.satlog').write_text(result.stdout + result.stderr)
        print(f'pattern={steps} rc={result.returncode} clauses={len(clauses)}', flush=True)
        if result.returncode == 20:
            continue
        if result.returncode != 10:
            unresolved = True
            continue
        chosen = [int(lit) - 1 for row in result.stdout.splitlines() if row.startswith('v ')
                  for lit in row.split()[1:] if int(lit) > 0]
        neighbors = base + [mask << len(base) for mask in pattern]
        seed = sum(1 << vertex for vertex in chosen)
        for offset in range(args.orbit):
            new_index = len(base) + offset
            mask = image(seed, forward[offset])
            neighbors[new_index] |= mask
            for vertex in vertices(mask):
                neighbors[vertex] |= 1 << new_index
        if (any(not independent(mask, neighbors) for mask in neighbors) or
                next(independent_sets(neighbors, (1 << total) - 1, args.k), None) is not None):
            raise ValueError('SAT model fails independent graph check')
        with Path(f'{args.prefix}.found.g6').open('a') as stream:
            stream.write(to_graph6(neighbors) + '\n')
    return int(unresolved)


if __name__ == '__main__':
    raise SystemExit(main())
