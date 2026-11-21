#!/usr/bin/env python3
"""Measure the necessary two-retained-group independent-set screen."""

from collections import Counter
import ctypes
from itertools import combinations_with_replacement
from pathlib import Path
import sys

from involution_cores import bits, graph
from involution_sat import from_graph6, witnesses
from m11_prop import targets
from m11_support import Supports


class UpperWitness:
    def __init__(self, library):
        self.lib = ctypes.CDLL(str(library.resolve()))
        self.func = self.lib.m11_upper_witness
        self.func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)]
        self.func.restype = ctypes.c_uint64

    def __call__(self, graph_rows, alpha):
        order = len(graph_rows)
        result = self.func(order, alpha, (ctypes.c_uint64*order)(*graph_rows))
        if result:
            assert result.bit_count() == alpha+1 and 0 < result < 1 << order
            assert all(not graph_rows[actor] & result for actor in bits(result))
        return result


def calibrate(witness):
    positives = 0
    for mask in range(1 << 6):
        edges = [(actor, actor+1) for actor in range(6) if mask >> actor & 1]
        core = graph(7, edges)
        for alpha in (2, 3, 4, 5, 6):
            direct = next(witnesses(core, 127, alpha+1), None) is not None
            assert bool(witness(core, alpha)) == direct
            positives += direct
    assert positives
    print('320 matched independent-set controls:', positives, 'witnesses', flush=True)


def pilot(witness, key):
    core = from_graph6(key)
    support = Supports(core, 6)
    caps = tuple(4-row.bit_count() for row in core)
    local = support.catalog(10, caps)
    stats = Counter()
    for first, second in combinations_with_replacement(local, 2):
        if any(left+right > cap for cap, left, right in zip(caps, support.info(first)[0], support.info(second)[0])):
            continue
        _, upper = targets(core, (first, second))
        stats['pairs'] += 1
        stats['witnesses'] += bool(witness(upper, 7))
    print(key, dict(stats), flush=True)
    Supports.options.cache_clear()
    Supports.info.cache_clear()


if __name__ == '__main__':
    finder = UpperWitness(Path('m11_prop2.so'))
    calibrate(finder)
    keys = Path(sys.argv[1]).read_text(encoding='ascii').splitlines()
    for index in map(int, sys.argv[2:]):
        pilot(finder, keys[index])
