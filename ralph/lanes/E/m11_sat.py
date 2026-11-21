#!/usr/bin/env python3
"""Proof CNFs for four pinned cross-attachment graphs, with all alpha windows."""

import argparse
import ctypes
from itertools import combinations, product
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from cubic32 import bounded_cuts, pin_graph
from involution_cores import bits, graph
from involution_sat import from_graph6, witnesses


class FastCuts:
    def __init__(self, path):
        self.library = ctypes.CDLL(str(path.resolve()))
        self.func = self.library.m11_fast_cuts
        pointer = ctypes.POINTER(ctypes.c_uint64)
        self.func.argtypes = [pointer, ctypes.POINTER(ctypes.c_uint16), ctypes.c_uint64, ctypes.c_int,
                              ctypes.c_int, pointer, ctypes.c_uint]
        self.func.restype = ctypes.c_int
        self.capacity = 1 << 16
        self.output = (ctypes.c_uint64*(4*self.capacity))()

    def __call__(self, known, edges, domain, need, width):
        if len(known) > 32 or len(edges) > 256:
            return bounded_cuts(known, edges, domain, need, width)
        rows = (ctypes.c_uint64*len(known))(*known)
        lookup = (ctypes.c_uint16*1024)()
        for (left, right), variable in edges.items():
            lookup[left*32+right] = lookup[right*32+left] = variable
        count = self.func(rows, lookup, domain, need, width, self.output, self.capacity)
        if count < 0:
            return bounded_cuts(known, edges, domain, need, width)
        unique = {tuple(self.output[index:index+4]) for index in range(0, 4*count, 4)}
        return (tuple(1+bit+64*word for word, mask in enumerate(row) for bit in bits(mask)) for row in unique)


def encode(core, groups, bounds, attachment_degrees=None, edge_target=None, cut_size=None, fast=bounded_cuts):
    known, parts = pin_graph(core, groups)
    vertices = len(known)
    edges = {pair: index for index, pair in enumerate(
        ((left, right) for first, second in combinations(parts, 2) for left in first for right in second
         if not known[left] & known[right]), 1)}
    variables = len(edges)
    clauses = []

    def atmost(row, target):
        nonlocal variables
        if target < 0:
            clauses.append(())
        elif target < len(row):
            encoding = CardEnc.atmost(lits=list(row), bound=target, top_id=variables, encoding=EncType.seqcounter)
            clauses.extend(encoding.clauses)
            variables = max(variables, encoding.nv)

    def exact(row, target):
        atmost(row, target)
        atmost(tuple(-literal for literal in row), len(row)-target)

    def eset(vertices):
        return tuple(sorted(edges[edge] for edge in combinations(vertices, 2) if edge in edges))

    for selected in combinations(parts, 3):
        for triple in product(*selected):
            row = eset(triple)
            if len(row) == 3:
                clauses.append(tuple(-literal for literal in row))

    if attachment_degrees is not None:
        for vert in range(len(core), vertices):
            exact(tuple(index for pair, index in edges.items() if vert in pair),
                  attachment_degrees[vert-len(core)]-known[vert].bit_count())
    if edge_target is not None:
        exact(tuple(edges.values()), edge_target-sum(row.bit_count() for row in known)//2)

    independent = set()
    for omitted, order in enumerate(bounds):
        if order is None:
            continue
        domain = ((1 << vertices)-1) & ~sum(1 << vert for vert in parts[omitted])
        for vert in bits(domain):
            if (known[vert] & domain).bit_count() > order:
                clauses.append(())
            atmost(tuple(index for pair, index in edges.items() if vert in pair and all(domain >> end & 1 for end in pair)),
                   order-(known[vert] & domain).bit_count())
        if cut_size is not None:
            independent.update(fast(known, edges, domain, order+1, cut_size))
        else:
            independent.update(eset(tuple(bits(pick))) for pick in witnesses(known, domain, order+1))
    if len(parts) == 3 and not any(bound is not None for bound in bounds):
        domain = (1 << vertices)-1
        if cut_size is None:
            independent.update(eset(tuple(bits(pick))) for pick in witnesses(known, domain, 8))
        else:
            independent.update(fast(known, edges, domain, 8, cut_size))
        for vert in bits(domain):
            atmost(tuple(index for pair, index in edges.items() if vert in pair), 7-known[vert].bit_count())
    clauses.extend(sorted(independent))
    return variables, clauses, known, edges


def calibration(fast):
    from pysat.solvers import Solver

    totals = []
    for groups in (((1,), (0,), (0,), (0,)), ((1, 0), (0,), (1,), (0,))):
        core = graph(1, [])
        pinned, parts = pin_graph(core, groups)
        vertices = len(pinned)
        possible = tuple((left, right) for first, second in combinations(parts, 2) for left in first for right in second)
        domains = tuple(tuple(v for v in range(vertices) if v not in part) for part in parts)
        attach = len(pinned)-1
        for bounds, degrees, target in (((2, 2, 2, 2), None, None), ((2, 3, 3, 2), None, 4),
                                         ((3, 3, 3, 3), None, 5), ((3, 3, 3, 3), (2,)*attach, None),
                                         ((2, None, 2, None), None, None)):
            nn, clauses, known, variables = encode(core, groups, bounds, degrees, target)
            assert known == pinned
            expected = set()
            for picked in product((False, True), repeat=len(possible)):
                edges = {(left, right) for left, right in combinations(range(vertices), 2) if pinned[left] >> right & 1}
                edges.update(pair for pair, use in zip(possible, picked) if use)
                if target is not None and len(edges) != target:
                    continue
                if degrees is not None and tuple(sum(vert in pair for pair in edges) for vert in range(1, vertices)) != degrees:
                    continue
                if any(all(pair in edges for pair in combinations(subset, 2))
                       for subset in combinations(range(vertices), 3)):
                    continue
                if any(all(pair not in edges for pair in combinations(subset, 2))
                       for domain, order in zip(domains, bounds) if order is not None
                       for subset in combinations(domain, order+1)):
                    continue
                expected.add(picked)
            actual = set()
            with Solver(name='cadical195', bootstrap_with=clauses) as solver:
                while solver.solve():
                    model = set(solver.get_model())
                    picked = tuple(variables.get(pair) in model for pair in possible)
                    actual.add(picked)
                    solver.add_clause([-var if var in model else var for var in variables.values()])
            assert actual == expected, (bounds, degrees, target, len(actual), len(expected))
            relaxed = encode(core, groups, bounds, degrees, target, 20)[1]
            assert sorted(map(tuple, clauses)) == sorted(map(tuple, relaxed))
            for width in (0, 1, 2, 3, 8):
                assert encode(core, groups, bounds, degrees, target, width, fast)[1] == encode(
                    core, groups, bounds, degrees, target, width)[1]
            totals.append(len(actual))
    assert 0 in totals and max(totals) > 0
    print('smaller exact labelled completion counts:', totals, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fast', type=Path)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    emit = sub.add_parser('encode')
    emit.add_argument('manifest', type=Path)
    emit.add_argument('index', type=int)
    emit.add_argument('lift', type=int)
    emit.add_argument('cnf', type=Path)
    emit.add_argument('--one-window', action='store_true')
    emit.add_argument('--omit-small', action='store_true')
    emit.add_argument('--cut-size', type=int, default=8)
    args = parser.parse_args()
    fast = bounded_cuts if args.fast is None else FastCuts(args.fast)
    if args.mode == 'calibrate':
        calibration(fast)
        return
    key, profile, parts, viable = json.loads(args.manifest.read_text(encoding='ascii').splitlines()[args.index])
    core = from_graph6(key)
    if args.omit_small:
        nn, clauses, _, variables = encode(core, [*parts[1:], viable[args.lift]], (None,)*3, edge_target=74,
                                            cut_size=args.cut_size, fast=fast)
    elif args.one_window:
        nn, clauses, _, variables = encode(core, parts, (None,)*3, edge_target=74, cut_size=args.cut_size, fast=fast)
    else:
        groups = [*parts, viable[args.lift]]
        assert [sum(map(int.bit_count, group)) for group in groups] == profile
        nn, clauses, _, variables = encode(core, groups, (7,)*4, (7,)*24, cut_size=args.cut_size, fast=fast)
    with args.cnf.open('w', encoding='ascii') as out:
        print('p cnf', nn, len(clauses), file=out)
        for clause in clauses:
            print(*clause, 0, file=out)
    print(f'core={key} profile={profile} index={args.index} lift={args.lift} edge_vars={len(variables)} '
          f'vars={nn} clauses={len(clauses)}', flush=True)


if __name__ == '__main__':
    main()
