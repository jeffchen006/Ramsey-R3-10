#!/usr/bin/env python3
"""Exact support split and low-edge window CNFs for the cubic involution core."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path

from involution_cores import bits, graph
from involution_sat import from_graph6, witnesses


CORES = ('G?zTb_', 'GCrb`o')


def neighborhoods(core, double):
    size = len(core) - len(double)
    single = sorted(set(range(len(core))) - set(double))
    options = []
    for vert in double:
        options.append([((1 << left) | (1 << right)) for left, right in combinations(range(size), 2)
                        if not (core[vert] & ((1 << single[left]) | (1 << single[right])))
                        and (core[single[left]] >> single[right]) & 1])
    independent = [tuple(bits(subset)) for need in range(2, len(core) + 1)
                   for subset in witnesses(core, (1 << len(core)) - 1, need)]
    for extra in product(*options):
        rows = [0] * len(core)
        for index, vert in enumerate(single):
            rows[vert] = 1 << index
        for vert, row in zip(double, extra):
            rows[vert] = row
        for left, right in combinations(range(len(core)), 2):
            if (core[left] >> right) & 1 and rows[left] & rows[right]:
                break
        else:
            for subset in independent:
                union = 0
                for vert in subset:
                    union |= rows[vert]
                if union.bit_count() < len(subset):
                    break
            else:
                yield tuple(rows)


def small_oracle(core, double):
    single = sorted(set(range(len(core))) - set(double))
    width = len(single)
    core_edges = [(left, right) for left, right in combinations(range(len(core)), 2)
                  if core[left] >> right & 1]
    for extra in product(tuple(combinations(range(width), 2)), repeat=len(double)):
        incidences = [(vert, column) for column, vert in enumerate(single)]
        incidences.extend((vert, column) for vert, cols in zip(double, extra) for column in cols)
        edges = set(core_edges + [(vert, len(core) + column) for vert, column in incidences])
        verts = range(len(core) + width)
        if any(all(pair in edges for pair in combinations(triple, 2)) for triple in combinations(verts, 3)):
            continue
        if any(all(pair not in edges for pair in combinations(subset, 2)) for subset in combinations(verts, width + 1)):
            continue
        yield tuple(sum(1 << column for row, column in incidences if row == vert) for vert in range(len(core)))


def invert(rows):
    width = max(rows, default=0).bit_length()
    return tuple(sum(1 << vert for vert, row in enumerate(rows) if row >> col & 1) for col in range(width))


def mask_image(mask, perm):
    return sum(1 << perm[vertex] for vertex in bits(mask))


def automorphisms(core):
    for perm in permutations(range(len(core))):
        if all(mask_image(row, perm) == core[perm[vertex]] for vertex, row in enumerate(core)):
            yield perm


def verify_core_cover():
    cores = tuple(from_graph6(row) for row in CORES)
    assert all(len(core) == 8 and all(row.bit_count() == 3 for row in core) for core in cores)
    assert all(not any(core[left] & core[right] for left in range(8) for right in bits(core[left])) for core in cores)
    orbits = []
    for core in cores:
        orbit = set()
        for perm in permutations(range(8)):
            if mask_image(core[perm.index(0)], perm) != 14:
                continue
            rows = [0] * 8
            for vertex, row in enumerate(core):
                rows[perm[vertex]] = mask_image(row, perm)
            orbit.add(tuple(rows))
        orbits.append(orbit)
    assert not (orbits[0] & orbits[1])
    remaining = [(left, right) for left, right in combinations(range(1, 8), 2) if right > 3]
    fixed = [(0, vertex) for vertex in range(1, 4)]
    found = set()
    for more in combinations(remaining, 9):
        rows = graph(8, fixed + list(more))
        if all(row.bit_count() == 3 for row in rows) and not any(
                rows[left] & rows[right] for left in range(8) for right in bits(rows[left])):
            found.add(tuple(rows))
    assert found == orbits[0] | orbits[1]
    print('complete cubic core check:', len(found), [len(orbit) for orbit in orbits], flush=True)


def degree_profiles(core, allowed):
    needed = tuple(4 - row.bit_count() for row in core)
    assert len(core) == 8 and sum(needed) == 8 and min(needed) >= 0

    def walk(start, remain, parts):
        if not any(remain):
            yield parts
            return
        for index in range(start, len(allowed)):
            left, right = allowed[index]
            if remain[left] and remain[right]:
                next_remain = tuple(count - int(index in (left, right)) for index, count in enumerate(remain))
                yield from walk(index, next_remain, parts + (allowed[index],))

    return walk(0, needed, ())


def verify_saturated_cover(keys):
    verify_core_cover()
    assert len(keys) == len(set(keys)) and set(CORES) <= set(keys)
    union = set()
    for key in keys:
        if key in CORES:
            continue
        core = from_graph6(key)
        assert len(core) == 8 and min(row.bit_count() for row in core) == 2
        assert sum(row.bit_count() for row in core) == 24 and max(row.bit_count() for row in core) <= 4
        assert not any(core[left] & core[right] for left in range(8) for right in bits(core[left]))
        orbit = set()
        for perm in permutations(range(8)):
            if mask_image(core[perm.index(0)], perm) != 6:
                continue
            rows = [0] * 8
            for vertex, row in enumerate(core):
                rows[perm[vertex]] = mask_image(row, perm)
            orbit.add(tuple(rows))
        assert orbit and not union & orbit
        union.update(orbit)
    remaining = [(left, right) for left, right in combinations(range(1, 8), 2) if right > 2]
    found = set()
    for more in combinations(remaining, 10):
        rows = graph(8, [(0, 1), (0, 2), *more])
        if all(2 <= row.bit_count() <= 4 for row in rows) and not any(
                rows[left] & rows[right] for left in range(8) for right in bits(rows[left])):
            found.add(tuple(rows))
    assert found == union
    print('complete noncubic saturated core check:', len(keys) - 2, len(found), flush=True)


def windows(keys=CORES):
    for key in keys:
        core = from_graph6(key)
        autos = tuple(automorphisms(core))
        options = {pair: tuple(sorted({tuple(sorted(invert(rows))) for rows in neighborhoods(core, pair)}))
                   for pair in combinations(range(8), 2)}

        @lru_cache(None)
        def image(part, perm):
            return tuple(sorted(mask_image(column, perm) for column in part))

        raw = set()
        valid = tuple(part for part, supports in options.items() if supports)
        for partition in degree_profiles(core, valid):
            for idx in range(len(partition)):
                triple = partition[:idx] + partition[idx + 1:]
                raw.update(tuple(sorted(parts)) for parts in product(*(options[pair] for pair in triple)))
        pending = set(raw)
        reps = []
        while pending:
            smallest = min(pending)
            orbit = {tuple(sorted(image(part, perm) for part in smallest)) for perm in autos}
            assert orbit <= raw
            pending -= orbit
            reps.append(smallest)
        print(key, 'aut', len(autos), 'local', sum(map(len, options.values())), 'labeled_windows', len(raw),
              'orbit_reps', len(reps), flush=True)
        yield key, reps


def pin_graph(core, groups):
    edges = [(left, right) for left, right in combinations(range(len(core)), 2) if core[left] >> right & 1]
    parts = []
    size = len(core)
    for group in groups:
        parts.append(tuple(range(size, size + len(group))))
        edges.extend((vert, size + col) for col, support in enumerate(group) for vert in bits(support))
        size += len(group)
    return graph(size, edges), parts


def bounded_cuts(known, edges, domain, need, max_lits):
    masks = [[0] * len(known) for _ in known]
    for (left, right), index in edges.items():
        masks[left][right] = masks[right][left] = 1 << (index - 1)

    def walk(pending, picked, left, clause):
        if not left:
            yield tuple(index + 1 for index in bits(clause))
            return
        while pending.bit_count() >= left:
            vertex_bit = pending & -pending
            pending ^= vertex_bit
            vert = vertex_bit.bit_length() - 1
            delta = clause
            for other in picked:
                delta |= masks[vert][other]
            if delta.bit_count() <= max_lits:
                yield from walk(pending & ~known[vert], picked + (vert,), left - 1, delta)

    return walk(domain, (), need, 0)


def clauses_for(core, groups, alpha, max_edges, min_pair_alpha, include_alpha=True, omit_pair_cuts=False,
                max_lits=None):
    from pysat.card import CardEnc, EncType

    known, parts = pin_graph(core, groups)
    nv = len(known)
    edges = {(left, right): index for index, (left, right) in enumerate(
        ((left, right) for first, second in combinations(parts, 2) for left in first for right in second
         if not (known[left] & known[right])), 1)}
    nn = len(edges)
    clauses = []

    def atmost(row, bound):
        nonlocal nn
        if bound < 0:
            clauses.append(())
        elif len(row) > bound:
            encoded = CardEnc.atmost(lits=list(row), bound=bound, top_id=nn, encoding=EncType.seqcounter)
            nn = max(nn, encoded.nv)
            clauses.extend(encoded.clauses)

    def eset(vertices):
        return tuple(edges[edge] for edge in combinations(vertices, 2) if edge in edges)

    for triple in product(*parts) if len(parts) == 3 else ():
        row = eset(triple)
        if len(row) == 3:
            clauses.append(tuple(-literal for literal in row))

    atmost(tuple(edges.values()), max_edges - sum(row.bit_count() for row in known) // 2)
    for vert, row in enumerate(known):
        atmost(tuple(index for pair, index in edges.items() if vert in pair), alpha - row.bit_count())

    dom = (1 << nv) - 1
    windows = []
    for first, second in combinations(parts, 2):
        if omit_pair_cuts:
            continue
        pair_window = (1 << len(core)) - 1 | sum(1 << vert for vert in first + second)
        windows.append((pair_window, min_pair_alpha))
    if include_alpha:
        windows.append((dom, alpha))

    for root in range(len(core)):
        if known[root].bit_count() != alpha:
            continue
        for other in bits(dom & ~known[root] & ~(1 << root)):
            if not known[root] & known[other]:
                clauses.append(tuple(edges[edge] for nbr in bits(known[root])
                                     if (edge := tuple(sorted((nbr, other)))) in edges))

    ind = set()
    for domain, bound in windows:
        if max_lits is None:
            for pick in witnesses(known, domain, bound + 1):
                ind.add(eset(tuple(bits(pick))))
        else:
            ind.update(bounded_cuts(known, edges, domain, bound + 1, max_lits))
    clauses.extend(sorted(ind))
    return nn, clauses, known, edges


def calibration():
    from pysat.solvers import Solver

    for nv in (4, 5):
        for mask in range(1 << (nv - 1)):
            core = graph(nv, [(left, left + 1) for left in range(nv - 1) if mask >> left & 1])
            for count in (1, 2):
                for double in combinations(range(nv), count):
                    assert set(neighborhoods(core, double)) == set(small_oracle(core, double))
    core = graph(1, [])
    groups = ((1,), (0, 0), (0, 0))
    known, parts = pin_graph(core, groups)
    candidates = tuple((left, right) for first, second in combinations(parts, 2) for left in first for right in second)
    graphs = {}
    for mask in range(1 << len(candidates)):
        adj = list(known)
        for index, (left, right) in enumerate(candidates):
            if mask >> index & 1:
                adj[left] |= 1 << right
                adj[right] |= 1 << left
        graphs[mask] = adj
    matched = []
    for alpha, limit in ((2, 10), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, 6)):
        nn, clauses, pinned, variables = clauses_for(core, groups, alpha, limit, alpha)
        assert pinned == known
        for width in range(4):
            for window in [tuple(range(len(known))), *(tuple(range(len(core))) + first + second
                                                       for first, second in combinations(parts, 2))]:
                domain = sum(1 << vertex for vertex in window)
                direct = {tuple(variables[key] for key in combinations(bits(pick), 2) if key in variables)
                          for pick in witnesses(known, domain, alpha + 1)}
                assert set(bounded_cuts(known, variables, domain, alpha + 1, width)) == {
                    row for row in direct if len(row) <= width}
        expected = set()
        for mask, adj in graphs.items():
            if sum(row.bit_count() for row in adj) > 2 * limit:
                continue
            if any(all(adj[left] >> right & 1 for left, right in combinations(triple, 2))
                   for triple in combinations(range(len(adj)), 3)):
                continue
            if any(all(not (adj[left] >> right & 1) for left, right in combinations(subset, 2))
                   for subset in combinations(range(len(adj)), alpha + 1)):
                continue
            expected.add(mask)
        actual = set()
        with Solver(name='cadical195', bootstrap_with=clauses) as sat:
            while sat.solve():
                model = set(sat.get_model())
                mask = sum(1 << index for index, key in enumerate(candidates) if variables[key] in model)
                actual.add(mask)
                sat.add_clause([-var if var in model else var for var in variables.values()])
        assert expected == actual, (alpha, limit, expected, actual)
        matched.append(len(actual))
    print('matched smaller oracle completion counts:', matched, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    census = sub.add_parser('census')
    census.add_argument('manifest', type=Path)
    census.add_argument('--saturated', type=Path)
    emit = sub.add_parser('encode')
    emit.add_argument('manifest', type=Path)
    emit.add_argument('index', type=int)
    emit.add_argument('cnf', type=Path)
    emit.add_argument('--no-alpha', action='store_true')
    emit.add_argument('--no-pair', action='store_true')
    emit.add_argument('--max-edges', type=int, default=74)
    emit.add_argument('--cut-size', type=int)
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibration()
    elif args.mode == 'census':
        keys = CORES
        if args.saturated:
            expanded = tuple(args.saturated.read_text(encoding='ascii').splitlines())
            verify_saturated_cover(expanded)
            keys = tuple(key for key in expanded if key not in CORES)
        else:
            verify_core_cover()
        manifest = [(key, parts) for key, reps in windows(keys) for parts in reps]
        args.manifest.write_text(''.join(json.dumps(row, separators=(',', ':')) + '\n' for row in manifest), encoding='ascii')
    else:
        core, groups = json.loads(args.manifest.read_text(encoding='ascii').splitlines()[args.index])
        nn, clauses, _, variables = clauses_for(from_graph6(core), groups, 7, args.max_edges, 7,
                                                not args.no_alpha, args.no_pair, args.cut_size)
        with args.cnf.open('w', encoding='ascii') as out:
            print('p cnf', nn, len(clauses), file=out)
            for row in clauses:
                print(*row, 0, file=out)
        print('index', args.index, 'core', core, 'edge_vars', len(variables), 'vars', nn, 'clauses', len(clauses), flush=True)


if __name__ == '__main__':
    main()
