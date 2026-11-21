#!/usr/bin/env python3
"""Require one checked proof per marked key; record proof and CNF hashes."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import re


def key_of(line):
    *fields, graph6 = line.split()
    return '_'.join(fields), int(fields[0]), graph6


def checked_index(keys, source, evidences):
    wanted = {}
    for line in keys.read_text().splitlines():
        key, row, graph6 = key_of(line)
        if key in wanted or row < 1 or source[row-1] != graph6:
            raise ValueError(f'duplicate key or wrong source row: {key}')
        wanted[key] = row
    checked = {}
    for directory, log in evidences:
        for line in log.read_text().splitlines():
            key, status, *tail = line.split()
            if status != 'CERT':
                continue
            if key not in wanted or key in checked:
                raise ValueError(f'duplicate or unexpected certificate: {key}')
            cnf_hash, size, _ = tail
            if not re.fullmatch('[0-9a-f]{64}', cnf_hash):
                raise ValueError(f'bad DIMACS hash for {key}')
            path = directory / (key + '.lrat.gz')
            if path.stat().st_size != int(size):
                raise ValueError(f'wrong proof length: {key}')
            digest = sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1 << 20), b''):
                    digest.update(block)
            checked[key] = (cnf_hash, digest.hexdigest(), path, size)
    if set(checked) != set(wanted):
        raise ValueError(f'{len(wanted)-len(checked)} missing certificates')
    return checked


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('--proofs', nargs=2, action='append', type=Path, required=True, metavar=('DIR', 'LOG'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    checked = checked_index(args.keys, args.source.read_text().splitlines(), args.proofs)
    with args.output.open('w') as output:
        for key, values in checked.items():
            print(key, *values, sep='\t', file=output)
    print(f'{len(checked)} distinct source-bound dual-checked certificates')


if __name__ == '__main__':
    main()
