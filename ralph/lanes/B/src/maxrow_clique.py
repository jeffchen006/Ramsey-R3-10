"""Replay demand cliques whose incompatibilities use maximal attachment rows."""

import argparse
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from check_graph import parse_graph6


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def compatible(rows, minimum, maximum):
    """Independent, maximal sets of the requested sizes (complement BK)."""
    full = (1 << len(rows)) - 1
    available = [full ^ ((1 << index) | outside) for index, outside in enumerate(rows)]

    def visit(picked, count, frontier, excluded):
        if not (frontier | excluded):
            if count >= minimum:
                yield picked
            return
        if count == maximum or count + frontier.bit_count() < minimum:
            return
        pivot = max(bits(frontier | excluded), key=lambda index: (frontier & available[index]).bit_count())
        for index in bits(frontier & ~available[pivot]):
            bit = 1 << index
            yield from visit(picked | bit, count + 1, frontier & available[index], excluded & available[index])
            frontier ^= bit
            excluded |= bit

    yield from visit(0, 0, full, 0)


def check(rows, demands, degree, minimum, maximum):
    if len(demands) != degree + 1 or len(set(demands)) != len(demands):
        raise ValueError('bad clique size or duplicate demand')
    for demand in demands:
        if not 0 < demand < 1 << len(rows) or demand.bit_count() not in (1, 2):
            raise ValueError('invalid demand mask')
        if demand.bit_count() == 2:
            first, second = bits(demand)
            if rows[first] & (rows[second] | (1 << second)):
                raise ValueError('demand pair is not at distance at least three')
    unions = {first | second for first, second in combinations(demands, 2)}
    open_unions = [union for union in unions if not any(rows[index] & union for index in bits(union))]
    if open_unions:
        for row in compatible(rows, minimum, maximum):
            if any(row & union == union for union in open_unions):
                raise ValueError('a maximal attachment row meets two demands')


def load_rows(source, trace, degree, minimum, maximum, remainder):
    with source.open() as inputs, trace.open() as proofs, remainder.open('w') as missing:
        def index_proof():
            entry = proofs.readline().split()
            if not entry:
                return None, ()
            index = int(entry[0])
            if index < 1:
                raise ValueError('nonpositive proof index')
            return index, tuple(int(word, 16) for word in entry[1:])

        index, demands = index_proof()
        read = checked = 0
        for read, line in enumerate(inputs, 1):
            if read == index:
                check(parse_graph6(line.rstrip('\n')), demands, degree, minimum, maximum)
                checked += 1
                index, demands = index_proof()
            else:
                print(f'{read}\t{line}', end='', file=missing)
        if index is not None or proofs.read(1):
            raise ValueError('duplicate, unsorted or out-of-range proof index')
    print(f'maxrow verifier: {checked}/{read}, {read-checked} remain')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('remainder', type=Path)
    parser.add_argument('--degree', type=int, required=True)
    parser.add_argument('--minimum', type=int, required=True)
    parser.add_argument('--maximum', type=int, required=True)
    options = parser.parse_args()
    if not 1 <= options.minimum <= options.maximum:
        parser.error('invalid row bounds')
    load_rows(options.source, options.trace, options.degree, options.minimum, options.maximum, options.remainder)


if __name__ == '__main__':
    main()
