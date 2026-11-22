#!/usr/bin/env python3
"""Reconstruct four-window clauses independently and check narrow LRATs."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import process_time

from pysat.card import CardEnc, EncType

from batch_shared74 import limited
from involution_sat import from_graph6
from replay_shared74 import read


def dimacs(variables, clauses):
    return (f'p cnf {variables} {len(clauses)}\n' + ''.join(
        ' '.join(map(str, (*clause, 0))) + '\n' for clause in clauses)).encode('ascii')


def reconstruct(core, groups, bounds, degrees=None):
    starts = [len(core)]
    for group in groups:
        starts.append(starts[-1] + len(group))
    parts = tuple(tuple(range(first, last)) for first, last in zip(starts, starts[1:]))
    size = starts[-1]
    pinned = [set(vertex for vertex in range(len(core)) if row >> vertex & 1) for row in core]
    for group in groups:
        for support in group:
            contacts = {vertex for vertex in range(len(core)) if support >> vertex & 1}
            for vertex in contacts:
                pinned[vertex].add(len(pinned))
            pinned.append(contacts)
    edges = {}
    for first in range(len(parts)):
        for second in range(first + 1, len(parts)):
            for left in parts[first]:
                for right in parts[second]:
                    if pinned[left].isdisjoint(pinned[right]):
                        edges[left, right] = len(edges) + 1

    variables = len(edges)
    base = []

    def clamp(literals, bound):
        nonlocal variables
        if bound < 0:
            base.append(())
        elif bound < len(literals):
            row = CardEnc.atmost(lits=literals, bound=bound, top_id=variables, encoding=EncType.seqcounter)
            base.extend(tuple(clause) for clause in row.clauses)
            variables = max(variables, row.nv)

    for first, second, third in combinations(parts, 3):
        for left, middle, right in product(first, second, third):
            triangle = ((left, middle), (left, right), (middle, right))
            if all(pair in edges for pair in triangle):
                base.append(tuple(-literal for literal in sorted(edges[pair] for pair in triangle)))
    if degrees is not None:
        assert len(degrees) == size - len(core)
        for vertex, total in enumerate(degrees, len(core)):
            literals = [index for pair, index in edges.items() if vertex in pair]
            need = total - len(pinned[vertex])
            clamp(literals, need)
            clamp([-literal for literal in literals], len(literals) - need)

    windows = []
    for part, bound in zip(parts, bounds, strict=True):
        if bound is None:
            continue
        sites = set(range(size)).difference(part)
        windows.append((sites, bound + 1))
        for vertex in sorted(sites):
            remaining = bound - len(pinned[vertex] & sites)
            if remaining < 0:
                base.append(())
            clamp([index for pair, index in edges.items() if vertex in pair and
                   pair[0] in sites and pair[1] in sites], remaining)
    return variables, tuple(base), pinned, edges, windows


def narrow_clauses(pinned, edges, windows, width=3):
    """Pending vertices in bucket j have exactly j optional edges to the chosen set."""
    forced = [sum(1 << vertex for vertex in row) for row in pinned]
    optional = [0] * len(pinned)
    for left, right in edges:
        optional[left] |= 1 << right
        optional[right] |= 1 << left
    clauses = set()

    def walk(buckets, chosen, need, limit):
        pending = sum(buckets)
        if pending.bit_count() < need:
            return
        if not need:
            clauses.add(tuple(sorted(edges[pair] for pair in combinations(chosen, 2) if pair in edges)))
            return
        while pending.bit_count() >= need:
            bit = pending & -pending
            pending ^= bit
            vertex = bit.bit_length() - 1
            extra = next(cost for cost, layer in enumerate(buckets) if layer & bit)
            budget = limit - extra
            permitted = pending & ~forced[vertex]
            neighbors = optional[vertex]
            layers = [(buckets[0] & ~neighbors) & permitted]
            for cost in range(1, budget + 1):
                layers.append(((buckets[cost] & ~neighbors) | (buckets[cost - 1] & neighbors)) & permitted)
            walk(layers, (*chosen, vertex), need - 1, budget)

    for sites, need in windows:
        walk([sum(1 << vertex for vertex in sites)] + [0] * width, (), need, width)
    return tuple(sorted(clauses))


def parse_cnf(path):
    header, *rows = path.read_bytes().splitlines()
    prefix, fmt, variables, count = header.split()
    assert (prefix, fmt) == (b'p', b'cnf') and len(rows) == int(count)
    clauses = tuple(tuple(map(int, row.split())) for row in rows)
    assert all(row and row[-1] == 0 and all(0 < abs(literal) <= int(variables) for literal in row[:-1])
               for row in clauses)
    return int(variables), tuple(row[:-1] for row in clauses)


def binding(core, groups, bounds, degrees, wide, narrow):
    variables, base, pinned, edges, windows = reconstruct(core, groups, bounds, degrees)
    cuts = narrow_clauses(pinned, edges, windows)
    assert narrow.read_bytes() == dimacs(variables, (*base, *cuts)), narrow
    original_variables, original = parse_cnf(wide)
    assert original_variables == variables and original[:len(base)] == base, wide
    alpha = original[len(base):]
    assert tuple(sorted(set(alpha))) == alpha
    assert tuple(clause for clause in alpha if len(clause) <= 3) == cuts, wide
    return len(base), len(cuts)


def batch(cover, trace, wide, folder):
    wanted = [(index, lift) for index, lift, status, *_ in read(trace) if status == 'open']
    assert wanted and wanted == sorted(set(wanted))
    expected = {f'{index}_{lift}' for index, lift in wanted}
    for place, suffix in product((wide, folder), ('cnf', 'lrat')):
        assert {path.stem for path in place.glob(f'*.{suffix}')} == expected
    queue = iter(wanted)
    item = next(queue, None)
    stats = Counter()
    for index, (key, profile, parts, omitted) in enumerate(read(cover)):
        if item is None:
            break
        while item is not None and item[0] == index:
            _, lift = item
            stem = f'{index}_{lift}'
            groups = (*parts, omitted[lift])
            assert [sum(map(int.bit_count, group)) for group in groups] == profile == [10, 10, 11, 11]
            start = process_time()
            cnf = folder/f'{stem}.cnf'
            base, cuts = binding(from_graph6(key), groups, (7,)*4, (7,)*24, wide/cnf.name, cnf)
            elapsed = process_time() - start
            log = folder/f'{stem}.independent.log'
            assert limited('cake_lpr', 10, 30, (cnf, folder/f'{stem}.lrat'), log) == 0
            assert 's VERIFIED UNSAT' in log.read_text(encoding='ascii').splitlines()
            stats['ids'] += 1
            stats['base'] += base
            stats['cuts'] += cuts
            print(stem, base, cuts, f'bind_cpu={elapsed:.6f}', flush=True)
            item = next(queue, None)
    assert item is None and stats['ids'] == len(wanted)
    print('independent narrow inclusion and CakeLRAT:', dict(stats), flush=True)


def calibrate(folder, library):
    from m11_sat import FastCuts, encode

    folder.mkdir()
    fast = FastCuts(library)
    core, groups, bounds = (0,), ((1,), (0,), (0,), (0, 0)), (3,)*4
    cases = (('positive', (2, 1, 2, 1, 1), 5, 2), ('negative', (3, 1, 1, 1, 1), 5, 0))
    for name, degrees, expected_base, expected in cases:
        from pysat.solvers import Solver

        variables, base, pinned, edges, windows = reconstruct(core, groups, bounds, degrees)
        assert len(edges) == 9
        base_count = 0
        true = []
        for states in product((False, True), repeat=len(edges)):
            graph = [set(row) for row in pinned]
            for (left, right), present in zip(edges, states):
                if present:
                    graph[left].add(right)
                    graph[right].add(left)
            if any(right in graph[left] and graph[left] & graph[right] for left, right in combinations(range(len(graph)), 2)):
                continue
            if tuple(map(len, graph[len(core):])) != degrees:
                continue
            if any(len(graph[vertex] & sites) >= need for sites, need in windows for vertex in sites):
                continue
            base_count += 1
            if any(all(right not in graph[left] for left, right in combinations(pick, 2))
                   for sites, need in windows for pick in combinations(sorted(sites), need)):
                continue
            true.append(states)
        cuts = narrow_clauses(pinned, edges, windows)
        literal = set()
        for sites, need in windows:
            for selected in combinations(sorted(sites), need):
                pairs = tuple(combinations(selected, 2))
                if all(right not in pinned[left] for left, right in pairs):
                    clause = tuple(sorted(edges[pair] for pair in pairs if pair in edges))
                    if len(clause) <= 3:
                        literal.add(clause)
        assert cuts == tuple(sorted(literal)) and cuts and len(true) == expected and base_count == expected_base
        with Solver(bootstrap_with=list(base)) as solver:
            assert solver.solve()
        with Solver(bootstrap_with=[*base, *cuts]) as solver:
            allowed = {tuple(index if present else -index for index, present in enumerate(states, 1))
                       for states in true}
            for assignment in product(*((index, -index) for index in range(1, len(edges)+1))):
                assert solver.solve(assumptions=list(assignment)) == (assignment in allowed)
        narrow = folder/f'{name}.3.cnf'
        narrow.write_bytes(dimacs(variables, (*base, *cuts)))
        wide = folder/f'{name}.8.cnf'
        wide_variables, wide_clauses, _, wide_edges = encode(core, groups, bounds, degrees, cut_size=8, fast=fast)
        assert edges == wide_edges
        wide.write_bytes(dimacs(wide_variables, wide_clauses))
        binding(core, groups, bounds, degrees, wide, narrow)
        if not expected:
            proof = folder/f'{name}.lrat'
            bad_log = folder/f'{name}.solve.log'
            check = folder/f'{name}.check.log'
            assert limited('cadical', 5, 15, ('-q', '--lrat', narrow, proof), bad_log) == 20
            assert limited('cake_lpr', 5, 15, (narrow, proof), check) == 0
            assert 's VERIFIED UNSAT' in check.read_text(encoding='ascii').splitlines()
        for mutation in ((*base, *cuts[:-1]), (*base, *cuts, cuts[-1]), (*base, *cuts[:-1], tuple(-lit for lit in cuts[-1]))):
            changed = folder/f'{name}.mutated.cnf'
            changed.write_bytes(dimacs(variables, mutation))
            try:
                binding(core, groups, bounds, degrees, wide, changed)
            except AssertionError:
                pass
            else:
                raise AssertionError('accepted mutated narrow CNF')
        print(name, 'base completions', base_count, 'literal completions', len(true), 'width-three cuts', len(cuts), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='mode', required=True)
    control = commands.add_parser('calibrate')
    control.add_argument('folder', type=Path)
    control.add_argument('--library', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    bind = commands.add_parser('batch')
    for name in ('cover', 'trace', 'wide', 'folder'):
        bind.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibrate(args.folder, args.library)
    else:
        batch(args.cover, args.trace, args.wide, args.folder)
