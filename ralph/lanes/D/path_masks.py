"""Complete residual 5x5 panel, then exact finite external attachment masks."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json

from path_growth import ROOT, bits, fixed_graph, pairs, path_lengths, read_profiles
from path_overlap import Library, optimistic
from path_panel import target_catalogue
from path_reroot import core_instances, decode, neighbors, placements, profile_key
from kernel_cnf import Cnf, neg


def split(profile, edges):
    graph = fixed_graph(profile)
    rows = [vertex for vertex in range(8, len(graph)) if graph[vertex] == 1]
    cols = [vertex for vertex in range(8, len(graph)) if graph[vertex] == 16]
    for ri, src in enumerate(rows):
        for ci, dst in enumerate(cols):
            if (ri, ci + len(rows)) in edges:
                graph[src] |= 1 << dst
                graph[dst] |= 1 << src
    return graph, rows + cols, [vertex for vertex in range(8, len(graph)) if vertex not in rows + cols]


def candidates(graph, wings, outside, pivot, degree, maximum, qmax, qflat, library=None):
    width = len(wings) // 2
    half = [list(bits(graph[anchor] & ~((1 << 8) - 1))) for anchor in (0, 4)]
    options = []
    for wing in half:
        if len(wing) != width:
            raise ValueError('not an isolated P6 component')
        root = 0 if wing == half[0] else 4
        old = (graph[root] & graph[pivot]).bit_count()
        group = []
        for count in range(max(0, (2 if qflat else 1) - old), 4 - old):
            for chosen in combinations(wing, count):
                if any(graph[vertex] & graph[pivot] for vertex in chosen):
                    continue
                group.append(sum(1 << vertex for vertex in chosen))
        options.append(group)
    out = []
    for left, right in product(*options):
        extra = left | right
        if any(graph[vertex] & right for vertex in bits(left)):
            continue
        work = list(graph)
        work[pivot] |= extra
        for vertex in bits(extra):
            work[vertex] |= 1 << pivot
        if any((work[pivot] & work[vertex]).bit_count() > 3 for vertex in range(len(graph)) if vertex != pivot):
            continue
        if any((work[first] & work[second]).bit_count() > 3 for first in bits(extra) for second in range(len(graph)) if second != first):
            continue
        if path_lengths(work) > maximum:
            continue
        if library is not None:
            upper = optimistic(work, degree)
            fixed_inner = ((1 << len(work)) - 1) ^ sum(1 << vertex for vertex in outside)
            for wing in wings:
                upper[wing] &= ~fixed_inner | work[wing]
                if not work[pivot] >> wing & 1:
                    upper[wing] &= ~(1 << pivot)
            upper[pivot] &= ~fixed_inner | work[pivot]
            if not all(library.supports(work, upper, core) for core in placements(work)):
                continue
        out.append(extra)
    return out


def build_table(profile, edges, degree, maximum, qmax, qflat, library=None):
    graph, wings, outside = split(profile, edges)
    order = len(graph)
    anchors = sorted(set(range(order)) - set(outside))
    fixed = {(src, dst): bool(graph[src] >> dst & 1) for src, dst in pairs(range(order))
             if src < 8 or src in anchors and dst in anchors or graph[src] & graph[dst]}
    form = Cnf(order, fixed)
    table = {}
    selects = {}
    for pivot in outside:
        mask = graph[pivot]
        if mask not in table:
            table[mask] = candidates(graph, wings, outside, pivot, degree, maximum, qmax, qflat, library)
        choices = []
        for extra in table[mask]:
            lit = form.new()
            choices.append(lit)
            for vertex in wings:
                arc = form.edge(pivot, vertex)
                form.add(-lit, arc if extra >> vertex & 1 else neg(arc))
        form.add(*choices)
        selects[pivot] = choices
    for anchor in anchors:
        form.cardinality([form.edge(anchor, other) for other in range(order) if other != anchor], degree, degree)
    for first, second in pairs(anchors):
        if form.edge(first, second) is True:
            continue
        common = [form.conjunction(form.edge(first, vertex), form.edge(second, vertex)) for vertex in range(order) if vertex not in (first, second)]
        form.cardinality(common, 2 if qflat else 1, 3)
    for root in (0, 4):
        side = list(bits(graph[root]))
        non = sorted(set(range(order)) - set(side) - {root})
        q = {vertex: [] for vertex in side}
        for first, second in pairs(side):
            common = [form.conjunction(form.edge(first, vertex), form.edge(second, vertex)) for vertex in non]
            flags = form.thresholds(common, 2)
            for vertex in (first, second):
                q[vertex].extend(flags)
        for terms in q.values():
            form.cardinality(terms, qmax if qflat else 0, qmax)
    for first, second in pairs(outside):
        form.cardinality([form.conjunction(form.edge(first, vertex), form.edge(second, vertex)) for vertex in anchors], 0, 3)
    return form, table


def calibration(use_library):
    from pysat.solvers import Cadical195
    seen = set()
    checks = 0
    profile_keys = set()
    if use_library:
        for line in (ROOT / 'duo/reg6_22.g6').read_text().splitlines():
            adj = neighbors(22, decode(line))
            if max(len(left & right) for left, right in pairs(adj)) > 3:
                continue
            for cycle, core in core_instances(adj):
                assert not cycle
                profile_keys.add(profile_key(Counter(sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
                                                     for vertex in set(range(22)) - set(core))))
    library = Library([dict(key) for key in profile_keys]) if use_library else None
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            assert not cycle
            mask = lambda vertex: sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (mask(vertex), vertex))
            order = core + outer
            wings = [vertex for sig in (1, 16) for vertex in outer if mask(vertex) == sig]
            if len(wings) != 4:
                continue
            edges = {(src, dst) for src, dst in pairs(range(4)) if wings[dst] in adj[wings[src]]}
            profile = Counter(map(mask, outer))
            key = profile_key(profile), tuple(sorted(edges))
            qmax = max(sum(len(adj[point] & adj[other]) - 1 for other in adj[root] - {point}) for root in (core[0], core[4]) for point in adj[root])
            if (key, qmax) in seen:
                continue
            seen.add((key, qmax))
            form, _ = build_table(profile, edges, 6, 8, qmax, False, library)
            with Cadical195(bootstrap_with=form.clauses) as solver:
                assert solver.solve(assumptions=[form.edge(src, dst, simplify=False) * (1 if order[dst] in adj[order[src]] else -1) for src, dst in pairs(range(22))])
            checks += 1
    print('PASS pinned C22 full-kernel tables', checks, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--index', type=int)
    parser.add_argument('--panel', type=int)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--overlaps', action='store_true')
    args = parser.parse_args()
    if args.index is None:
        calibration(args.overlaps)
    else:
        code, qmax, sizes = target_catalogue()[args.panel]
        profiles = list(read_profiles(args.source))
        library = Library([profiles[index] for index in ((2424, 2431) if qmax == 12 else (2298, 2386, 2424, 2431))]) if args.overlaps else None
        form, table = build_table(profiles[args.index], decode(code), 9, 6, qmax, qmax == 12, library)
        form.write(args.out)
        print(args.index, args.panel, 'variables', form.nvars, 'clauses', len(form.clauses), 'row options', {key: len(value) for key, value in table.items()}, flush=True)
