#!/usr/bin/env python3
"""Generate degree-preserving quotient paths with two vertical endpoint toggles."""

import argparse
from itertools import combinations, product
from pathlib import Path
from random import Random

from relift_audit import (decode, encode, explicit_lift, legal_support, one_graph,
                         quotient, switches, walk_score, write_lines)


def trades(matrix, max_length):
    size = len(matrix)
    candidates = [set() for _ in range(max_length + 1)]
    original_loops = [matrix[index][index] for index in range(size)]
    for start in range(size):
        first_change = 2 * original_loops[start] - 1

        def visit(last, change, seen, depth):
            for other, old in enumerate(matrix[last]):
                mask = 1 << other
                new = old + change
                if seen & mask or not 0 <= new <= 2:
                    continue
                matrix[last][other] = matrix[other][last] = new
                if other > start and change == 2 * original_loops[other] - 1:
                    matrix[start][start] ^= 1
                    matrix[other][other] ^= 1
                    if legal_support(matrix):
                        candidates[depth].add(encode(matrix))
                    matrix[start][start] ^= 1
                    matrix[other][other] ^= 1
                if depth < max_length:
                    visit(other, -change, seen | mask, depth + 1)
                matrix[last][other] = matrix[other][last] = old

        visit(start, first_change, 1 << start, 1)
    return candidates


def independent_oracle(matrix, max_length):
    size = len(matrix)
    edges = list(combinations(range(size), 2))
    old_degrees = list(map(sum, matrix))
    result = [set() for _ in range(max_length + 1)]
    for length in range(1, max_length + 1):
        for changed in combinations(edges, length):
            incident = [set() for _ in range(size)]
            for left, right in changed:
                incident[left].add(right)
                incident[right].add(left)
            ends = [index for index, adj in enumerate(incident) if len(adj) == 1]
            if len(ends) != 2 or any(len(adj) > 2 for adj in incident):
                continue
            seen = set()
            pending = ends[:1]
            while pending:
                index = pending.pop()
                if index in seen:
                    continue
                seen.add(index)
                pending.extend(incident[index])
            if len(seen) != length + 1:
                continue
            for changes in product((-1, 1), repeat=length):
                child = [row[:] for row in matrix]
                for (left, right), change in zip(changed, changes, strict=True):
                    child[left][right] += change
                    child[right][left] += change
                if any(not 0 <= child[left][right] <= 2 for left, right in changed):
                    continue
                for end in ends:
                    child[end][end] ^= 1
                if list(map(sum, child)) != old_degrees:
                    continue
                single_count = sum(child[left][right] == 1 for left, right in edges)
                graph = explicit_lift(child, iter([1] * single_count))
                if not any(graph[left] & graph[right] for left, right in combinations(range(2 * size), 2)
                           if graph[left] >> right & 1):
                    result[length].add(encode(child))
    return result


def oracle():
    rng = Random(770438)
    count, depths = 0, [0] * 5
    while count < 64:
        size = rng.randrange(2, 6)
        matrix = [[0] * size for _ in range(size)]
        for left in range(size):
            matrix[left][left] = rng.randrange(2)
        for left, right in combinations(range(size), 2):
            matrix[left][right] = matrix[right][left] = rng.choices(range(3), [5, 3, 1])[0]
        if not legal_support(matrix):
            continue
        generated = trades(matrix, 4)
        assert generated == independent_oracle(matrix, 4), matrix
        count += 1
        for depth, rows in enumerate(generated):
            depths[depth] += len(rows)
    print(f'PASS trade oracle: {count} legal quotients; outputs by length {depths[1:]}')


def calibration(sources):
    rng = Random(566231)
    for number, path in enumerate(sources):
        graph = one_graph(path)
        assert len(graph) == 38 and walk_score(graph, 10) == 0
        matrix = quotient(graph)
        parent = encode(matrix)
        forward = trades(matrix, 4)
        for length, neighbors in enumerate(forward[1:], 1):
            if not neighbors:
                continue
            mutant = rng.choice(sorted(neighbors))
            changed = decode(mutant)
            reverse = trades(changed, length)[length]
            baseline = set(switches(changed))
            assert parent in reverse and parent not in baseline and mutant not in reverse | baseline
            assert not (reverse & baseline)
            prefix = f'ctl{number}_{length}'
            write_lines(Path(prefix + '.q'), [mutant] + sorted(reverse) + sorted(baseline))
            write_lines(Path(prefix + '.expected'), [parent])
            print(f'{prefix} n38 parent={path} trade={len(reverse)} switches={len(baseline)} planted_index={1 + sorted(reverse).index(parent)}')


def target(sources, exclusions, depth, pilot):
    prior = {row for path in exclusions for row in path.read_text().splitlines()}
    prior |= {encode(quotient(one_graph(path))) for path in sources}
    rng = Random(638013)
    for number, path in enumerate(sources):
        graph = one_graph(path)
        assert len(graph) == 40 and walk_score(graph, 10) == 24
        matrix = quotient(graph)
        assert all(6 <= sum(row) <= 9 for row in matrix)
        for length, neighbors in enumerate(trades(matrix, depth)[1:], 1):
            new = sorted(neighbors - prior)
            for row in new:
                assert list(map(sum, decode(row))) == list(map(sum, matrix))
            rng.shuffle(new)
            prefix = f'target{number}_{length}'
            write_lines(Path(prefix + '.q'), new)
            write_lines(Path(prefix + '.pilot.q'), new[:pilot])
            print(f'{prefix} parent={path} total={len(neighbors)} new={len(new)} pilot={len(new[:pilot])}')
            prior.update(new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='what', required=True)
    sub.add_parser('oracle')
    ctl = sub.add_parser('calibration')
    ctl.add_argument('sources', nargs='+', type=Path)
    tgt = sub.add_parser('target')
    tgt.add_argument('sources', nargs='+', type=Path)
    tgt.add_argument('--exclude', nargs='+', type=Path, default=[])
    tgt.add_argument('--depth', type=int, default=4)
    tgt.add_argument('--pilot', type=int, default=32)
    args = parser.parse_args()
    if args.what == 'oracle':
        oracle()
    elif args.what == 'calibration':
        calibration(args.sources)
    else:
        target(args.sources, args.exclude, args.depth, args.pilot)


if __name__ == '__main__':
    main()
