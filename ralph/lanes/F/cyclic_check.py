"""Independent semantic trace, LRAT, and degree-nine cyclic-source verifier."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]


def read_base(text):
    size = ord(text[0]) - 65
    assert 1 <= size <= 20 and len(text) == 1 + size * (size + 1) // 2
    base = [[0] * size for _ in range(size)]
    weights = iter(map(int, text[1:]))
    for row in range(size):
        for column in range(row + 1):
            base[row][column] = base[column][row] = next(weights)
            assert 0 <= base[row][column] <= (1 if row == column else 2)
    return base


def source_check(inputs):
    remaining = set()
    raw = 0
    for vertical, antipode in product(range(2), range(3)):
        residual = 9 - vertical - antipode
        if residual % 2:
            continue
        for steps in combinations_with_replacement(range(1, 10), residual // 2):
            counts = Counter(steps)
            if max(counts.values()) > 2:
                continue
            raw += 1
            weights = [vertical] + [counts[step] for step in range(1, 10)] + [antipode]
            row = tuple(weights + weights[1:-1][::-1])
            graph = [set() for _ in range(40)]
            for left, right in combinations(range(40), 2):
                weight = row[(left // 2 - right // 2) % 20]
                if weight == 2 or (weight == 1 and (left ^ right) & 1):
                    graph[left].add(right)
                    graph[right].add(left)
            assert all(len(adjacent) == 9 for adjacent in graph)
            if all(not (graph[left] & graph[right]) for left in range(40) for right in graph[left]):
                remaining.add(row)
    total = len(remaining)
    for text in inputs:
        base = read_base(text)
        assert len(base) == 20 and all(base[left][right] == base[0][(right - left) % 20]
                                       for left in range(20) for right in range(20))
        images = {tuple(base[0][(step * unit) % 20] for step in range(20))
                  for unit in (1, 3, 7, 9, 11, 13, 17, 19)}
        assert images <= remaining
        remaining.difference_update(images)
    assert not remaining
    return raw, total


def rank(forms):
    basis = {}
    for form in forms:
        while form and form.bit_length() in basis:
            form ^= basis[form.bit_length()]
        if form:
            basis[form.bit_length()] = form
    return len(basis)


def clause_key(clause):
    return tuple(sorted(clause, key=lambda lit: (abs(lit), lit < 0)))


def forbidden(indices, predicate):
    return [tuple(-index if value else index for index, value in zip(indices, assignment))
            for assignment in product((False, True), repeat=len(indices)) if predicate(*assignment)]


def check(text, target, stem):
    base = read_base(text)
    size = len(base)
    edges = [(left, right) for left in range(size) for right in range(left + 1, size) if base[left][right] == 1]
    symbols = {index: 1 << (index - 1) for index in range(1, len(edges) + 1)}
    forest = []
    clauses = []
    support_count = 0
    boundary = [(1 << left) | (1 << right) for left, right in edges]
    for line in stem.with_suffix('.trace').read_text().splitlines():
        tag, *fields = line.split()
        numbers = list(map(int, fields))
        if tag == 'forest':
            [ident] = numbers
            assert 1 <= ident <= len(edges)
            forest.append(boundary[ident - 1])
            clauses.append((-ident,))
        elif tag == 'tri':
            assert len(numbers) == len(set(numbers)) == 3 and all(1 <= ident <= len(edges) for ident in numbers)
            endpoints = set(vertex for ident in numbers for vertex in edges[ident - 1])
            assert len(endpoints) == 3
            clauses.extend(forbidden(numbers, lambda first, second, third: first ^ second ^ third))
        elif tag == 'xor':
            result, left, right = numbers
            assert result == len(symbols) + 1 and symbols[left] is not None and symbols[right] is not None
            symbols[result] = symbols[left] ^ symbols[right]
            clauses.extend(forbidden(numbers, lambda out, first, second: out != (first ^ second)))
        else:
            assert tag in ('cut', 'forestcut')
            full, single, *rest = numbers
            assert 0 <= (full | single) < 1 << size and not (full & single)
            assert 2 * full.bit_count() + single.bit_count() == target
            for left in range(size):
                for right in range(left, size):
                    occupied = (1 << left) | (1 << right)
                    if occupied & full and not (occupied & ~(full | single)):
                        assert base[left][right] == 0
                    if left != right and not (occupied & ~single):
                        assert base[left][right] < 2
            active = [index for index, incident in enumerate(boundary) if not (incident & ~single)]
            dimension = len(active) - rank(boundary[index] for index in active)
            if tag == 'forestcut':
                [guard] = rest
                assert dimension == 0 and guard == len(symbols) + 1
                symbols[guard] = None
                clauses.extend(((guard,), (-guard,)))
            else:
                assert rest and all(index in symbols and symbols[index] is not None for index in rest)
                forms = [symbols[index] for index in rest]
                assert rank(forms) == dimension
                mask = sum(1 << index for index in active)
                for form in forms:
                    assert not (form & ~mask)
                    parity = 0
                    for index in active:
                        if (form >> index) & 1:
                            parity ^= boundary[index]
                    assert not parity
                clauses.append(tuple(rest))
            support_count += 1
    assert rank(forest) == len(forest)
    raw = stem.with_suffix('.cnf').read_text().splitlines()
    assert raw[0] == f'p cnf {len(symbols)} {len(clauses)}'
    actual = []
    for line in raw[1:]:
        *clause, zero = map(int, line.split())
        assert zero == 0 and all(0 < abs(literal) <= len(symbols) for literal in clause)
        actual.append(clause_key(clause))
    assert Counter(map(clause_key, clauses)) == Counter(actual)
    for name, flags, expect in [('lrat-check', [], b'c VERIFIED'),
                                ('cake_lpr', ['--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=32'], b's VERIFIED UNSAT')]:
        args = [ROOT / 'opt/bin' / name, *flags, stem.with_suffix('.cnf'), stem.with_suffix('.lrat')]
        run = subprocess.run(['timeout', '35', 'prlimit', '--cpu=25:27', '--', *args], capture_output=True)
        assert not run.returncode and expect in run.stdout.splitlines(), (stem, name, run.stdout)
    return support_count


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('small', 'target'))
    parser.add_argument('--data', type=Path, default=Path('.'))
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    with open(args.receipt or (args.mode + '.receipt.tsv'), 'w') as receipt:
        print('row\tsource_sha256\tpath\tsupports\tcnf_sha256\tlrat_sha256\ttrace_sha256', file=receipt)
        inputs = (args.data / (args.mode + '.q')).read_text().splitlines()
        if args.mode == 'target':
            raw, legal = source_check(inputs)
            print('source profiles before structural triangle filter', raw, 'legal', legal, 'representatives', len(inputs))
            assert inputs[:12] == (args.data / 'target.pilot.q').read_text().splitlines()
        scored = 0
        for index, text in enumerate(inputs):
            if args.mode == 'small':
                if int((args.data / 'small.expected').read_text().splitlines()[index]) == 0:
                    continue
                stem = Path('smallproof2') / f'{index:03}'
            else:
                stem = Path('pilotproof' if index < 12 else 'suffixproof') / f'{index:03}'
            count = check(text, 4 if args.mode == 'small' else 10, args.data / stem)
            hashes = [digest((args.data / stem).with_suffix(extension)) for extension in ('.cnf', '.lrat', '.trace')]
            print(index, sha256(text.encode()).hexdigest(), stem, count, *hashes, sep='\t', file=receipt, flush=True)
            scored += 1
    print('PASS', scored, 'semantic and dual-LRAT replays')


if __name__ == '__main__':
    main()
