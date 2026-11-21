#!/usr/bin/env python3
import argparse
from collections import Counter
from math import factorial, prod
from pathlib import Path

from p2_cross_cert import bits, decode


def key_of(graph):
    root = len(graph) - 1
    common = graph[root]
    assert len(graph) == 19 and common.bit_count() == 6
    core = ((1 << root) - 1) & ~common
    degree_sum = sum((graph[vertex] & core).bit_count() for vertex in bits(core))
    assert degree_sum % 2 == 0
    sizes = sorted(graph[vertex].bit_count() - 1 for vertex in bits(common))
    return degree_sum // 2, *sizes


def read_lines(path):
    with path.open() as stream:
        for line in stream:
            yield line.rstrip('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('profiles', type=Path)
    parser.add_argument('canonical', type=Path)
    parser.add_argument('raw_profiled', type=Path)
    parser.add_argument('raw_unprofiled', type=Path)
    parser.add_argument('--stride', type=int, default=307)
    args = parser.parse_args()
    profiles = {}
    for line in read_lines(args.profiles):
        *key, weight = map(int, line.split())
        assert tuple(key) not in profiles
        profiles[tuple(key)] = weight
    raw_profiled = list(read_lines(args.raw_profiled))
    filtered = [line for line in read_lines(args.raw_unprofiled) if key_of(decode(line)) in profiles]
    assert filtered == raw_profiled
    hist = Counter()
    previous = None
    for line in read_lines(args.canonical):
        assert previous is None or previous < line
        previous = line
        key = key_of(decode(line))
        assert key in profiles
        hist[key] += 1
    raw_maps = sum(profiles[key] * hits * prod(factorial(count) for count in Counter(key[1:]).values())
                   for key, hits in hist.items())
    print(f'exact profile-subset control raw={len(filtered)}; rooted keys={sum(hist.values())}, '
          f'present profiles={len(hist)}, raw complementary wing-C maps >= {raw_maps}')
    print(f'linear sample projection (stride {args.stride}, not a bound) >= {args.stride * raw_maps} raw maps')
