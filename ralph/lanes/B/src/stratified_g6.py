"""Stable degree-histogram round-robin for small, disjoint graph pilots."""

import argparse
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from check_graph import parse_graph6


def digest(key, salt):
    return sha256(salt.encode('ascii') + key).digest()


def select(source, count, salt):
    groups = defaultdict(list)
    for line in source:
        key = line.rstrip(b'\n')
        degrees = tuple(sorted(row.bit_count() for row in parse_graph6(key.decode('ascii'))))
        groups[degrees].append(key)
    for group in groups.values():
        group.sort(key=lambda key: digest(key, salt))
    ordered = sorted(groups, key=lambda group: digest(groups[group][0], salt))
    index = 0
    selected = []
    while len(selected) < count and ordered:
        active = []
        for group in ordered:
            selected.append(groups[group][index])
            if len(selected) == count:
                break
            if index + 1 < len(groups[group]):
                active.append(group)
        index += 1
        ordered = active
    print(f'pool={sum(map(len, groups.values()))} histograms={len(groups)} selected={len(selected)}', file=sys.stderr)
    return selected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('count', type=int)
    parser.add_argument('salt')
    parser.add_argument('--hash-only', action='store_true')
    args = parser.parse_args()
    assert args.count > 0
    if args.hash_only:
        selected = sorted((line.rstrip(b'\n') for line in sys.stdin.buffer), key=lambda key: digest(key, args.salt))[:args.count]
    else:
        selected = select(sys.stdin.buffer, args.count, args.salt)
    sys.stdout.buffer.writelines(key + b'\n' for key in selected)
