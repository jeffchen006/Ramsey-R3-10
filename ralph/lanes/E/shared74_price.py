#!/usr/bin/env python3
"""Sample each canonical first branch at both ends and in its interior."""

import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
from pathlib import Path
import json

from order_shared74 import decode, read
from involution_sat import from_graph6
from m11_support import Supports, automorphisms, image


def bands(size, width):
    if size < 3 * width:
        return tuple(range(band * size // 3, (band + 1) * size // 3) for band in range(3))
    middle = (size - width) // 2
    return (range(width), range(middle, middle + width), range(size - width, size))


def sample(source, prefix, width):
    assert width > 0
    branch_rows = defaultdict(list)
    key = None
    with source.open(encoding='ascii') as stream:
        for index, line in enumerate(stream):
            row = json.loads(line)
            if key is None:
                key = row[0]
            assert row[0] == key and row[1] == [10, 10, 11, 11] and row[3]
            branch_rows[tuple(row[2][0])].append((index, line, len(row[3])))
    core = tuple(from_graph6(key))
    support = Supports(core, 6)
    autos = tuple(automorphisms(core))
    small = support.catalog(10, tuple(4 - row.bit_count() for row in core))
    representatives = tuple(first for first in small if all(first <= image(first, perm) for perm in autos))
    assert set(branch_rows) <= set(representatives)
    with ExitStack() as stack:
        branch_table = stack.enter_context(Path(f'{prefix}.branches.tsv').open('x', encoding='ascii'))
        samples = tuple(stack.enter_context(Path(f'{prefix}.{name}.jsonl').open('x', encoding='ascii'))
                        for name in ('front', 'interior', 'tail'))
        indices = tuple(stack.enter_context(Path(f'{prefix}.{name}.ids').open('x', encoding='ascii'))
                        for name in ('front', 'interior', 'tail'))
        print('branch\tprojections\tlifts\tfront\tfront_lifts\tinterior\tinterior_lifts\ttail\ttail_lifts',
              file=branch_table)
        for first in representatives:
            rows = branch_rows[first]
            stats = [','.join(map(str, first)), len(rows), sum(row[2] for row in rows)]
            for band, out, ids in zip(bands(len(rows), width), samples, indices):
                for offset in band:
                    index, line, _ = rows[offset]
                    out.write(line)
                    print(index, file=ids)
                stats.extend((len(band), sum(rows[offset][2] for offset in band)))
            print(*stats, sep='\t', file=branch_table)
    print(key, 'canonical branches', len(representatives), 'nonempty', sum(map(bool, branch_rows.values())),
          'projections', sum(len(rows) for rows in branch_rows.values()), flush=True)


def bind(source, prefix):
    full = source.read_bytes().splitlines()
    seen = set()
    for name in ('front', 'interior', 'tail'):
        path = Path(f'{prefix}.{name}.jsonl')
        rows = path.read_bytes().splitlines()
        indices = list(map(int, Path(f'{prefix}.{name}.ids').read_text(encoding='ascii').splitlines()))
        assert len(rows) == len(indices) == len(set(indices)) and not seen.intersection(indices)
        assert all(0 <= index < len(full) and row == full[index] for index, row in zip(indices, rows))
        seen.update(indices)
        count = Counter(parts[0] for _, parts, _ in map(decode, read(path)))
        print(name, 'byte-bound projections', len(rows), 'nonempty branches', len(count), flush=True)


def calibrate():
    for width in (1, 3, 48):
        for size in range(400):
            front, interior, tail = bands(size, width)
            groups = (front, interior, tail)
            assert all(len(group) <= width for group in groups)
            assert all(end <= start for end, start in ((front.stop, interior.start), (interior.stop, tail.start)))
            assert len(set().union(*groups)) == min(size, 3 * width)
            assert set().union(*groups) <= set(range(size))
    print('1,200 exhaustive sample-band size controls passed', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('calibrate')
    for action in ('sample', 'bind'):
        command = commands.add_parser(action)
        command.add_argument('source', type=Path)
        command.add_argument('prefix', type=Path)
        if action == 'sample':
            command.add_argument('--width', type=int, default=48)
    args = parser.parse_args()
    if args.command == 'calibrate':
        calibrate()
    elif args.command == 'sample':
        sample(args.source, args.prefix, args.width)
    else:
        bind(args.source, args.prefix)
