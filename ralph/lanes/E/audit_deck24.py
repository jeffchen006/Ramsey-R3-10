#!/usr/bin/env python3
"""Exact covers and receipt anti-joins for the two e8/bmax16 cores."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import chain
import json
from pathlib import Path
from time import process_time


def lines(path):
    contents = path.read_bytes()
    records = contents.splitlines()
    if contents and not contents.endswith(b'\n'):
        records.pop()
    return records


def compare():
    for folder, name, total in (('cover2', '../r23_deck/e8ext.first.plan', 15_350), ('cover8', 'C8.plan', 243_162)):
        parts = [lines(Path(folder)/f'{index}.jsonl') for index in range(7)]
        expected = lines(Path(name))
        observed = set(chain.from_iterable(parts))
        assert len(expected) == total and len(set(expected)) == total and observed == set(expected)
        tuple_order = lambda raw: json.loads(raw)[1:3]
        assert expected == sorted(observed, key=tuple_order)
        print(folder, 'exact column-first labelled-to-orbit join', sum(map(len, parts)), total,
              sha256(Path(name).read_bytes()).hexdigest(), flush=True)


def statuses(files, proof_directory=False):
    by_id = {}
    sample_cpu = 0.0
    proof_bytes = 0
    for path in files:
        records = lines(path)
        offset = 0
        for record in records:
            values = record.split(b'\t')
            index = int(values[0]); status = values[1].decode('ascii')
            assert index not in by_id
            by_id[index] = status
            sample_cpu += float(values[6])
            if proof_directory and status == 'CHECKED':
                assert offset == int(values[4]) and len(values[2]) == len(values[3]) == 64
                counted = int(values[5]); assert counted > 0
                offset += counted
        if proof_directory:
            assert path.with_suffix('.bin').stat().st_size >= offset
            proof_bytes += offset
    return by_id, sample_cpu, proof_bytes


def audit(prefix):
    old, cpu_old, _ = statuses(sorted(Path('oldreplay').glob('*.tsv')))
    assert not old.keys() - set(range(15_350))
    print('2C4 distinct', len(old), dict(Counter(old.values())), f'{cpu_old:.2f} replay CPU-s', flush=True)
    pilot, cpu_pilot, bytes_pilot = statuses(sorted(Path('pilot').glob('*.tsv')), True)
    prod, cpu_prod, bytes_prod = statuses(sorted(Path('C8.prod').glob('*.tsv')), True)
    assert pilot.keys().isdisjoint(prod) and len(pilot) == 224
    seen = pilot | prod
    target = set(range(243_162))
    assert not seen.keys() - target
    for path in Path('C8.prod').glob('*.tsv'):
        shard = int(path.stem)
        assert all(int(row.split(b'\t', 1)[0]) % 22 == shard for row in lines(path))
    counter = Counter(seen.values())
    print('C8 distinct', len(seen), dict(counter), 'not attempted', len(target-seen.keys()),
          f'{cpu_pilot+cpu_prod:.2f} completed CPU-s', 'proof bytes', bytes_pilot+bytes_prod, flush=True)
    for name, table, total in (('2c4', old, 15_350), ('C8', seen, 243_162)):
        with Path(f'{prefix}.{name}.open.tsv').open('x', encoding='ascii') as output:
            for index in range(total):
                condition = table.get(index, 'NO_TERMINAL')
                if condition != 'CHECKED':
                    print(index, condition, sep='\t', file=output)
    print('audit CPU-s', process_time(), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare', action='store_true')
    parser.add_argument('--prefix')
    args = parser.parse_args()
    if args.compare:
        compare()
    if args.prefix is not None:
        audit(args.prefix)
