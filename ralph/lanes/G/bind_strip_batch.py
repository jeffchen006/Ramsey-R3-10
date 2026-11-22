#!/usr/bin/env python3
"""Bind completed and missing keys, including terminated partial shards."""

from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from os import fstat
from pathlib import Path
from re import fullmatch

from index_strip_proofs import key_of


def proof_digest(item):
    key, cnf_hash, size, path = item
    with path.open('rb') as stream:
        if fstat(stream.fileno()).st_size != size:
            raise ValueError(f'wrong proof length: {key}')
        digest = sha256()
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return key, cnf_hash, digest.hexdigest(), path, size


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--batch', nargs=4, required=True, action='append',
                        metavar=('KEY_SUBSET', 'PROOF_DIR', 'SHARD_COUNT', 'LOG_PREFIX'))
    parser.add_argument('--retry', nargs=4, action='append', default=[],
                        metavar=('KEY_SUBSET', 'PROOF_DIR', 'SHARD_COUNT', 'LOG_PREFIX'))
    parser.add_argument('--io-workers', type=int, choices=range(1, 5), default=1)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    all_rows = args.keys.read_text().splitlines()
    expected = {key_of(row)[0]: row for row in all_rows}
    if len(expected) != len(all_rows):
        raise ValueError('duplicate source keys')
    partition = set()
    receipts = {}
    checked = {}
    for batch_number, (subset, directory, count, prefix) in enumerate(args.batch + args.retry):
        retry = batch_number >= len(args.batch)
        if retry and partition != set(expected):
            raise ValueError('initial batch subsets do not partition the source')
        rows = Path(subset).read_text().splitlines()
        count = int(count)
        subset_keys = set()
        for row in rows:
            key = key_of(row)[0]
            if expected.get(key) != row or key in subset_keys or (not retry and key in partition):
                raise ValueError(f'overlap, bad source row or alien key: {key}')
            if retry and receipts.get(key) == 'CERT':
                raise ValueError(f'retry overlaps existing certificate: {key}')
            subset_keys.add(key)
            partition.add(key)
        for shard in range(count):
            log = Path(f'{prefix}.{shard}.log')
            wanted = [key_of(row)[0] for row in rows[shard::count]]
            found = log.read_text().splitlines()
            if len(found) > len(wanted):
                raise ValueError(f'extra receipts in {log}')
            for key, line in zip(wanted, found):
                actual, status, *tail = line.split()
                if actual != key or receipts.get(key) == 'CERT' or (not retry and key in receipts):
                    raise ValueError(f'wrong receipt position in {log}: {line}')
                receipts[key] = status
                if status == 'CERT':
                    cnf_hash, size, _ = tail
                    if not fullmatch('[0-9a-f]{64}', cnf_hash):
                        raise ValueError(f'bad DIMACS hash for {key}')
                    checked[key] = key, cnf_hash, int(size), Path(directory) / (key + '.lrat.gz')
            print(log, f'{len(found)}/{len(wanted)}', *sorted(Counter(line.split()[1] for line in found).items()))
    if partition != set(expected):
        raise ValueError('batch subsets do not partition the source')
    certified = args.output / 'cert.keys'
    certified.write_text(''.join(f'{row}\n' for key, row in expected.items() if receipts.get(key) == 'CERT'))
    unclosed = args.output / 'unclosed.keys'
    unclosed.write_text(''.join(f'{row}\n' for key, row in expected.items() if receipts.get(key) != 'CERT'))
    graph6_rows = {}
    for row in all_rows:
        _, line_number, encoded = key_of(row)
        if graph6_rows.setdefault(line_number, encoded) != encoded:
            raise ValueError(f'conflicting graph6 references at line {line_number}')
    with args.source.open() as source:
        for line_number, line in enumerate(source, 1):
            if line_number in graph6_rows and graph6_rows.pop(line_number) != line.rstrip('\n'):
                raise ValueError(f'wrong graph6 source at line {line_number}')
            if not graph6_rows:
                break
    if graph6_rows:
        raise ValueError(f'{len(graph6_rows)} source rows missing')
    staging = args.output / '.certificates.staging'
    with ThreadPoolExecutor(max_workers=args.io_workers) as pool, staging.open('w') as index:
        for result in pool.map(proof_digest, (checked[key] for key in sorted(checked))):
            print(*result, sep='\t', file=index)
    staging.replace(args.output / 'certificates.tsv')
    print(f'SOURCE {len(expected)} RECEIPTS {len(receipts)} CHECKED {len(checked)}',
          f'MISSING {len(expected)-len(receipts)}', sorted(Counter(receipts.values()).items()))


if __name__ == '__main__':
    main()
