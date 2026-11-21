#!/usr/bin/env python3
"""Small witnessed case-splits, with independent replay of both edge branches."""

import argparse
from collections import Counter
import ctypes
from itertools import combinations
import json
from pathlib import Path

from involution_cores import bits
from involution_sat import from_graph6
from m11_prop import Prover, proof_check, targets


def edges_in(mask, graph):
    return [(left, right) for left, right in combinations(bits(mask), 2) if graph[left] >> right & 1]


def forced(pinned, edge):
    left, right = edge
    lower = list(pinned)
    lower[left] |= 1 << right
    lower[right] |= 1 << left
    return lower


class Splits:
    def __init__(self, library):
        self.prover = Prover(library)
        self.splitter = self.prover.lib.m11_two_edge_set
        pointer = ctypes.POINTER(ctypes.c_uint64)
        self.splitter.argtypes = [ctypes.c_int, ctypes.c_int, pointer, pointer]
        self.splitter.restype = ctypes.c_uint64

    def prove(self, pinned, eligible, alpha, target, depth):
        trace = self.prover.prove(pinned, eligible, alpha, target)
        if trace[0]:
            return trace, None, None
        if not depth:
            return None
        lower, upper = proof_check(pinned, eligible, alpha, target, *trace)
        order = len(lower)
        array = ctypes.c_uint64 * order
        witness = self.splitter(order, alpha, array(*lower), array(*upper))
        if not witness:
            return None
        branches = []
        for edge in edges_in(witness, upper):
            branch = self.prove(forced(lower, edge), upper, alpha, target, depth-1)
            if branch is None:
                return None
            branches.append(branch)
        assert len(branches) == 2
        return trace, witness, tuple(branches)


def validate(pinned, eligible, alpha, target, proof):
    trace, witness, branches = proof
    lower, upper = proof_check(pinned, eligible, alpha, target, *trace)
    if witness is None:
        assert branches is None and trace[0]
        return 1
    assert not trace[0] and witness.bit_count() == alpha+1 and 0 < witness < 1 << len(lower)
    assert not edges_in(witness, lower)
    optional = edges_in(witness, upper)
    assert len(optional) == len(branches) == 2
    return sum(validate(forced(lower, edge), upper, alpha, target, child) for edge, child in zip(optional, branches))


def calibrate(searcher):
    from cubic32 import pin_graph
    from involution_cores import graph
    from itertools import product
    totals = Counter()
    for groups in (((0,), (0,), (0,)), ((1,), (0,), (0,)), ((1, 0), (0,), (0, 0)),
                   ((1, 0), (1,), (0, 0)), ((0,), (0, 0), (0, 0, 0))):
        core = graph(1, [])
        pinned, eligible = targets(core, groups)
        raw, parts = pin_graph(core, groups)
        assert raw == pinned and parts
        order = len(pinned)
        span = (1 << order)-1
        optional = set(edges_in(span, eligible)) - set(edges_in(span, pinned))
        triangles = [set(combinations(subset, 2)) for subset in combinations(range(order), 3)]
        for alpha in (2, 3, 4):
            independent = [set(combinations(subset, 2)) for subset in combinations(range(order), alpha+1)]
            known = set(edges_in(span, pinned))
            possible = set()
            for picked in product((False, True), repeat=len(optional)):
                edges = known | {edge for edge, chosen in zip(optional, picked) if chosen}
                if not any(triangle <= edges for triangle in triangles) and all(edges & subset for subset in independent):
                    possible.add(len(edges))
            for target in range(1, 10):
                proof = searcher.prove(pinned, eligible, alpha, target, 3)
                totals['cases'] += 1
                if proof is None:
                    totals['positive'] += target in possible
                    continue
                assert target not in possible
                leaves = validate(pinned, eligible, alpha, target, proof)
                totals['checked'] += 1
                totals['split'] += leaves > 1
    assert totals['split'] and totals['positive']
    print('small exact split controls:', dict(totals), flush=True)


def pilot(args, searcher):
    todos = [int(line.split()[0]) for line in args.todo.read_text(encoding='ascii').splitlines()]
    rows = args.manifest.read_text(encoding='ascii').splitlines()
    stats = Counter()
    with args.output.open('w', encoding='ascii') as out:
        for index in todos:
            key, profile, parts, _ = json.loads(rows[index])
            lower, upper = targets(from_graph6(key), parts)
            proof = searcher.prove(lower, upper, 7, 74, args.depth)
            stats[str(profile), 'cases'] += 1
            if proof is None:
                stats[str(profile), 'open'] += 1
            else:
                leaves = validate(lower, upper, 7, 74, proof)
                stats[str(profile), f'leaves={leaves}'] += 1
                print(json.dumps((index, proof), separators=(',', ':')), file=out)
    print('pilot split outcomes:', sorted(stats.items()), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    command = sub.add_parser('pilot')
    command.add_argument('manifest', type=Path)
    command.add_argument('todo', type=Path)
    command.add_argument('output', type=Path)
    command.add_argument('--depth', type=int, default=2)
    args = parser.parse_args()
    searcher = Splits(args.library)
    if args.mode == 'calibrate':
        calibrate(searcher)
    else:
        pilot(args, searcher)


if __name__ == '__main__':
    main()
