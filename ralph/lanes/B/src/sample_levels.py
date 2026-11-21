"""Reproducible uniform sampling without replacement within an e-level."""
import argparse
from pathlib import Path
import random
import sys


def sample(path, order, edges, count, seed):
    width = 2 + (order*(order-1)//2 + 5)//6
    length = path.stat().st_size
    if length % width:
        raise ValueError('partial records in input')
    rng = random.Random(seed)
    seen = set()
    population = length//width
    with path.open('rb') as source:
        while count and len(seen) < population:
            offset = rng.randrange(population)
            if offset in seen:
                continue
            seen.add(offset)
            source.seek(width*offset)
            line = source.read(width)
            if len(line) != width or line[0] != order+63 or line[-1] != 10:
                raise ValueError('malformed graph6 input')
            if sum((character-63).bit_count() for character in line[1:-1]) != edges:
                continue
            sys.stdout.buffer.write(line)
            count -= 1
    if count:
        raise ValueError('too few graphs at requested level')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=Path)
    parser.add_argument('order', type=int)
    parser.add_argument('edges', type=int)
    parser.add_argument('count', type=int)
    parser.add_argument('seed', type=int)
    args = parser.parse_args()
    sample(args.file, args.order, args.edges, args.count, args.seed)
