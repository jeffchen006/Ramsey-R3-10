#!/usr/bin/env python3
"""Join terminal producer receipts to a complete independent hash replay."""

import argparse
from hashlib import sha256
from pathlib import Path
import re

from audit_floor_covers import require


DIGEST = re.compile(r'[0-9a-f]{64}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipts', type=Path)
    parser.add_argument('expected', type=int)
    parser.add_argument('replays', type=Path, nargs='+')
    args = parser.parse_args()
    receipts = {}
    for row in args.receipts.read_text().splitlines():
        if '\t' not in row:
            continue
        key, checksum, size, file_name = row.split('\t')
        require(key not in receipts and DIGEST.fullmatch(checksum), 'duplicate or malformed receipt')
        receipts[key] = checksum, int(size), Path(file_name)
    require(len(receipts) == args.expected, f'expected {args.expected} terminal receipts')

    replayed = set()
    for log in args.replays:
        for row in log.read_text().splitlines():
            fields = row.split()
            if row.startswith(('continuation attempted', f'{args.expected} keys;')):
                continue
            require(len(fields) == 5 and all(DIGEST.fullmatch(field) for field in fields[3:]),
                    f'invalid replay row {row}')
            key, pins, eager, digest, proof_hash = fields
            require(key in receipts and key not in replayed, f'unknown or duplicate replay key {key}')
            require(0 < int(pins) <= 780 and 0 <= int(eager), 'invalid clause counts')
            expected, size, path = receipts[key]
            proof = path.read_bytes()
            require(digest == expected and len(proof) == size and sha256(proof).hexdigest() == proof_hash,
                    f'terminal binding mismatch {key}')
            replayed.add(key)
    require(replayed == set(receipts), f'missing {len(set(receipts) - replayed)} independent replay keys')
    print(f'{len(replayed)}/{len(receipts)} exact replay keys; independent CNF and proof SHA-256 matches')


if __name__ == '__main__':
    main()
