"""Max-square roots among max-six edge kernels: graph-first remaining panels."""

import argparse
from collections import Counter
from pathlib import Path
import subprocess

from pysat.solvers import Cadical195

from path_growth import bits, fixed_graph, path_lengths, read_profiles
from path_links import make
from punct_path import ROOT, core_instances, decode, neighbors, pairs
from punctured import certificate, matching_size


def catalogue(width, degree, lower, upper, floor_order, cap):
    records = []
    rows = subprocess.run([ROOT / 'opt/bin/genbg', '-q', '-D2:2', str(width), str(width)],
                          check=True, timeout=15, capture_output=True, text=True).stdout.splitlines()
    for code in rows:
        edges = decode(code)
        if not lower <= 5 + len(edges) <= upper:
            continue
        adj = neighbors(2 * width, edges)
        if matching_size(adj, width) + 3 < degree - 2:
            continue
        remain = set(range(2 * width))
        sizes = []
        while remain:
            found = {min(remain)}
            search = list(found)
            while search:
                vertex = search.pop()
                for other in adj[vertex] - found:
                    found.add(other)
                    search.append(other)
            if all(len(adj[vertex]) == 2 for vertex in found):
                break
            sizes.append(len(found))
            remain -= found
        if remain or max(sizes) > cap or min(sizes) < floor_order:
            continue
        records.append((code, 5 + len(edges), sorted(sizes)))
    return records


def controls():
    controls = catalogue(2, 6, 5, 9, 1, 8)
    panels = {certificate(neighbors(4, decode(code)), [[0, 1], [2, 3]]): code for code, _, _ in controls}
    seen = set()
    counts = Counter()
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            assert not cycle
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex]), vertex))
            order = core + outer
            masks = [sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex]) for vertex in outer]
            panelset = [outer[index] for mask in (1, 16) for index, sig in enumerate(masks) if sig == mask]
            if len(panelset) != 4:
                continue
            edge_set = {(src, dst) for src, dst in pairs(range(4)) if panelset[dst] in adj[panelset[src]]}
            code = panels[certificate(neighbors(4, edge_set), [[0, 1], [2, 3]])]
            counts['placements'] += 1
            squares = [sum(len(adj[vertex] & adj[terminal]) - 1 for terminal in adj[anchor] - {vertex})
                       for anchor in core for vertex in adj[anchor]]
            key = tuple(masks), code, min(squares), max(squares)
            if key in seen:
                continue
            seen.add(key)
            pins = [(src, dst, 1 if order[dst] in adj[order[src]] else -1) for src, dst in pairs(range(22))]
            for high, expected in [(max(squares), True), (max(squares) - 1, False)]:
                formula = make(Counter(masks), 6, 8, panel=edge_set, square_range=(min(squares), high))
                with Cadical195(bootstrap_with=formula.clauses) as solver:
                    assert solver.solve(assumptions=[sign * formula.edge(src, dst, simplify=False) for src, dst, sign in pins]) == expected
                counts[expected] += 1
    assert counts[True] == counts[False] > 0
    print('PASS P6-component smaller panel membership and signed qmax:', dict(counts), flush=True)


def target_catalogue():
    return catalogue(5, 9, 12, 12, 2, 6) + catalogue(5, 9, 13, 13, 1, 6)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--index', type=int)
    parser.add_argument('--panel', type=int)
    parser.add_argument('--exact', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.index is None:
        controls()
        print('target catalogue', list(enumerate(target_catalogue())), flush=True)
    else:
        code, maximum, _ = target_catalogue()[args.panel]
        formula = make(list(read_profiles(args.source))[args.index], 9, 6, exact=args.exact, panel=decode(code),
                       square_range=(12 if maximum == 12 else 0, maximum))
        formula.write(args.out)
        print(args.index, args.panel, code, maximum, formula.nvars, len(formula.clauses), flush=True)
