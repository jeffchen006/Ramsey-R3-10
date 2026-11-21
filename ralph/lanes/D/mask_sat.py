#!/usr/bin/env python3
"""Boolean projection of fixed-edge mask choices with codegree cap at most 3."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from pysat.solvers import Cadical195, Minicard

from kernel_cnf import Cnf, ROOT

sys.path.insert(0, str(ROOT / 'ralph/lanes/C'))
from kernel_projection import Projection, bits, by_edge, decode, independent_masks


def projected(order, degree, maximum, kernel, min_edge, lazy_rows, native):
    projection = Projection(kernel, order, degree, maximum, strong=True, min_edge=min_edge)
    cnf = Cnf(0, {})
    cnf.nvars = len(projection.masks)
    for column, mask in enumerate(projection.masks):
        if mask.bit_count() > degree:
            cnf.add(-column - 1)
    limits = {}
    residuals = {}
    native_rows = []

    def at_most(literals, bound):
        if bound < 0:
            cnf.add()
        elif bound < len(literals):
            if native:
                native_rows.append((literals, bound))
            else:
                cnf.cardinality(literals, 0, bound)

    for row, bound, name in projection.rows:
        if lazy_rows and name.startswith(('ramsey:', 'star:', 'shared:')) and bound >= 0:
            assert all(coefficient == 1 for _, coefficient in row)
            if len(row) > bound:
                support = sum(1 << column for column, coefficient in row)
                residuals[support] = min(bound, residuals.get(support, bound))
            continue
        literals = []
        for column, coefficient in row:
            if coefficient > 0:
                literals.extend([column + 1] * coefficient)
            else:
                literals.extend([-column - 1] * (-coefficient))
                bound -= coefficient
        literals = tuple(sorted(literals))
        if bound < len(literals):
            limits[literals] = min(bound, limits.get(literals, bound))
    for literals, bound in limits.items():
        at_most(literals, bound)
    if min_edge and maximum == 3:
        width = degree - 1
        left = (1 << width) - 1
        right = left << width
        count = sum(mask.bit_count() for mask in kernel) // 2
        floor = max(0, (degree * count + 1) // 2 - (2 * degree * (degree - 1) - 3 * (order - degree - 1)))
        for own, opposite in ((left, right), (right, left)):
            base = sum(not kernel[index] for index in bits(opposite))
            literals = [index + 1 for index, mask in enumerate(projection.masks) if (own & mask).bit_count() == 1]
            at_most([-literal for literal in literals], len(literals) - max(0, floor - base))
    return projection, cnf, residuals, native_rows


def residue_cuts(selected, residuals):
    chosen = sum(1 << column for column in selected)
    result = set()
    for support, bound in residuals.items():
        witness = support & chosen
        if witness.bit_count() > bound:
            result.add(tuple(-column - 1 for column in list(bits(witness))[:bound + 1]))
    return [('residue', list(clause)) for clause in sorted(result)]


def relation_tables(kernel, masks, degree, maximum):
    width = len(kernel)
    allcols = (1 << len(masks)) - 1
    contains = [sum(1 << col for col, mask in enumerate(masks) if mask >> vertex & 1)
                for vertex in range(width)]
    vetoes = [sum(1 << vertex for vertex, adjacency in enumerate(kernel)
                  if (mask & adjacency).bit_count() == maximum) for mask in masks]
    vetoed_by = [sum(1 << col for col, veto in enumerate(vetoes) if veto >> vertex & 1)
                 for vertex in range(width)]
    allowed = []
    common_holes = []
    for mask, veto in zip(masks, vetoes):
        excluded = 0
        for vertex in bits(mask | veto):
            excluded |= contains[vertex]
        for vertex in bits(mask):
            excluded |= vetoed_by[vertex]
        allowed.append(allcols ^ excluded)
        common_holes.append([vertex for vertex, adjacency in enumerate(kernel)
                             if not (mask >> vertex & 1 or mask & adjacency)])
    left = (1 << (degree - 1)) - 1
    right = left << (degree - 1)
    inner = [mask | (1 << (width + (vertex >= degree - 1))) for vertex, mask in enumerate(kernel)]
    inner += [left | (1 << (width + 1)), right | (1 << width)]
    required = [0] * len(masks)
    for seed in independent_masks(inner, (1 << (width + 2)) - 1):
        if seed.bit_count() != degree - 1:
            continue
        avoiding = allcols
        for vertex in bits(seed & (left | right)):
            avoiding &= ~contains[vertex]
        for col in bits(avoiding):
            required[col] |= avoiding ^ (1 << col)
    return allowed, required, common_holes, contains


def cuts(masks, degree, maximum, selected, tables):
    allowed, required, common_holes, contains = tables
    chosen = sum(1 << col for col in selected)
    for col in selected:
        residual_degree = degree - masks[col].bit_count()
        possible = allowed[col] & chosen
        forced = required[col] & chosen
        if possible.bit_count() < residual_degree:
            yield 'outside-degree', [-col - 1] + [other + 1 for other in bits(allowed[col] & ~possible)]
        if forced.bit_count() > residual_degree:
            yield 'forced-degree', [-col - 1] + [-other - 1 for other in list(bits(forced))[:residual_degree + 1]]
        for other in bits(forced & ~allowed[col]):
            if col < other:
                yield 'impossible-forced-edge', [-col - 1, -other - 1]
        for vertex in common_holes[col]:
            options = allowed[col] & contains[vertex]
            if not options & chosen:
                yield 'inner-outer-MTF', [-col - 1] + [other + 1 for other in bits(options)]
    for left, right in combinations(selected, 2):
        shared = (masks[left] & masks[right]).bit_count()
        forced_common = required[left] & required[right] & chosen
        if forced_common and required[left] >> right & 1:
            third = next(bits(forced_common))
            yield 'forced-triangle', [-left - 1, -right - 1, -third - 1]
        if shared + forced_common.bit_count() > maximum:
            yield 'outer-codegree', ([-left - 1, -right - 1] +
                                     [-third - 1 for third in list(bits(forced_common))[:max(0, maximum + 1 - shared)]])
        if not shared and not (allowed[left] >> right & 1):
            options = allowed[left] & allowed[right]
            if not options & chosen:
                yield 'outer-outer-MTF', [-left - 1, -right - 1] + [third + 1 for third in bits(options)]


def independent_witness(nonedge, needed):
    def search(candidates, depth, selected):
        if not depth:
            return selected
        while candidates.bit_count() >= depth:
            leading = candidates & -candidates
            candidates ^= leading
            vertex = leading.bit_length() - 1
            witness = search(candidates & nonedge[vertex], depth - 1, selected | leading)
            if witness:
                return witness
        return 0

    return search((1 << len(nonedge)) - 1, needed, 0)


def supergraph_cut(kernel, degree, masks, chosen, allowed):
    width = len(kernel)
    kernel_size = width + 2
    left = (1 << (degree - 1)) - 1
    right = left << (degree - 1)
    adjacency = [row | (1 << (width + (vertex >= degree - 1))) for vertex, row in enumerate(kernel)]
    adjacency += [left | (1 << (width + 1)), right | (1 << width)]
    for index, column in enumerate(chosen):
        vertex = kernel_size + index
        for neighbor in bits(masks[column]):
            adjacency[neighbor] |= 1 << vertex
        possible_edges = sum(1 << (kernel_size + other_index) for other_index, other in enumerate(chosen)
                             if allowed[column] >> other & 1)
        adjacency.append(masks[column] | possible_edges)
    full = (1 << len(adjacency)) - 1
    nonedge = [full & ~(row | 1 << index) for index, row in enumerate(adjacency)]
    witness = independent_witness(nonedge, degree + 1)
    if not witness:
        return []
    return [('supergraph-independent', [-chosen[vertex - kernel_size] - 1
                                        for vertex in bits(witness) if vertex >= kernel_size])]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('cap', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('idx', type=int)
    parser.add_argument('--models', type=int, default=10_000)
    parser.add_argument('--min-edge', action='store_true')
    parser.add_argument('--extra-cuts', action='store_true')
    parser.add_argument('--lazy-rows', action='store_true')
    parser.add_argument('--supergraph-cut', action='store_true')
    parser.add_argument('--native', action='store_true', help='use MiniCard for eager cardinalities')
    parser.add_argument('--pin-graph', type=Path)
    parser.add_argument('--proof-output', type=Path)
    args = parser.parse_args()
    assert 1 <= args.cap <= 3 and args.models > 0
    assert not args.supergraph_cut or args.extra_cuts
    assert not args.native or not args.proof_output
    line = args.catalogue.read_text().splitlines()[args.idx]
    kernel = decode(line)
    pinned = None
    if args.pin_graph:
        graph = decode(args.pin_graph.read_text().splitlines()[0])
        assert len(graph) == args.order
        edges = ((left, right) for left in range(len(graph)) for right in bits(graph[left]) if left < right)
        _, kernel, pinned = min((sum(mask.bit_count() for mask in part) // 2, part, sorted(counts.items()))
                                for left, right in edges for part, counts in [by_edge(graph, left, right)])
        assert all(mult == 1 for _, mult in pinned)
        line = None
    wall_start, cpu_start = time.monotonic(), time.process_time()
    projection, cnf, residuals, native_rows = projected(args.order, args.degree, args.cap, kernel,
                                                       args.min_edge, args.lazy_rows, args.native)
    if pinned is not None:
        chosen = {mask for mask, _ in pinned}
        assert chosen <= set(projection.masks)
        for index, mask in enumerate(projection.masks):
            cnf.add((index + 1) if mask in chosen else -(index + 1))
    tables = relation_tables(kernel, projection.masks, args.degree, args.cap) if args.extra_cuts else None
    print(json.dumps({'kernel': line, 'columns': len(projection.masks), 'variables': cnf.nvars,
                      'clauses': len(cnf.clauses), 'lazy_rows': len(residuals),
                      'native_rows': len(native_rows),
                      'encode_cpu_s': round(time.process_time() - cpu_start, 3)}), flush=True)
    tally = Counter()
    cut_log = []
    backend = Minicard if args.native else Cadical195
    with backend(bootstrap_with=cnf.clauses) as solver:
        for literals, bound in native_rows:
            solver.add_atmost(literals, bound)
        for iteration in range(1, args.models + 1):
            if not solver.solve():
                verdict = 'UNSAT-RELAXATION'
                break
            selected = sorted(lit - 1 for lit in solver.get_model() if 0 < lit <= len(projection.masks))
            assert len(selected) == args.order - 2 * args.degree
            learned = residue_cuts(selected, residuals)
            if tables:
                learned.extend(cuts(projection.masks, args.degree, args.cap, selected, tables))
                if args.supergraph_cut:
                    learned.extend(supergraph_cut(kernel, args.degree, projection.masks, selected, tables[0]))
            if not learned:
                verdict = 'SAT-RELAXATION'
                break
            for name, clause in learned:
                solver.add_clause(clause)
                if args.proof_output:
                    cut_log.append((name, clause, selected))
                tally[name] += 1
            if iteration in (10, 100, 1000):
                print(json.dumps({'iteration': iteration, 'cuts': tally,
                                  'cpu_s': round(time.process_time() - cpu_start, 3)}), flush=True)
        else:
            verdict = 'MODEL-LIMIT'
    if args.proof_output and verdict == 'UNSAT-RELAXATION':
        args.proof_output.mkdir()
        cnf.clauses += [clause for _, clause, _ in cut_log]
        cnf.write(args.proof_output / 'problem.cnf')
        (args.proof_output / 'cuts.json').write_text(json.dumps(cut_log))
        with Cadical195(bootstrap_with=cnf.clauses, with_proof=True) as proof_solver:
            assert not proof_solver.solve()
            (args.proof_output / 'trace.drat').write_text('\n'.join(proof_solver.get_proof()) + '\n')
    print(json.dumps({'verdict': verdict, 'iterations': iteration, 'cuts': tally,
                      'cpu_s': round(time.process_time() - cpu_start, 3), 'wall_s': round(time.monotonic() - wall_start, 3)}),
          flush=True)


if __name__ == '__main__':
    main()
