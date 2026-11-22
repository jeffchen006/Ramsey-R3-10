"""Punctured six-vertex cover, one oriented singleton panel, two tip windows."""

import argparse
import ast
import itertools
import json
import resource
import subprocess
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

import pynauty

from kernel_cnf import Cnf, ROOT, decode, neg
from pin_controls import graph6


pairs = lambda values: itertools.combinations(values, 2)
KEYS = [(left, right, shared) for left in range(3) for right in range(left, 3)
        for shared in range(1, 4) if left + right + shared >= 4]


def neighbors(order, edges):
    return [{other for other in range(order) if tuple(sorted((vertex, other))) in edges}
            for vertex in range(order)]


def layout(order, degree, key):
    left, right, shared = key
    masks = Counter({36: shared})
    for full in list(range(left)) + list(range(3, 3 + right)):
        masks[(1 << full) | (4 if full < 3 else 32)] = 1
    core = {(src, dst) for src in range(3) for dst in range(3, 6) if (src, dst) != (2, 5)}
    for point, row in enumerate(neighbors(6, core)):
        masks[1 << point] = degree - len(row) - sum(size for mask, size in masks.items() if mask >> point & 1)
    masks[0] = order - 6 - sum(masks.values())
    if min(masks.values()) < 0:
        return None
    cells = {}
    start = 6
    for mask, size in sorted(masks.items()):
        cells[mask] = list(range(start, start + size))
        start += size
    assert start == order
    sig = {vertex: mask for mask, vertices in cells.items() for vertex in vertices}
    fixed = {}
    for src, dst in pairs(range(order)):
        if dst < 6:
            fixed[src, dst] = (src, dst) in core
        elif src < 6:
            fixed[src, dst] = bool(sig[dst] >> src & 1)
        elif sig[src] & sig[dst]:
            fixed[src, dst] = False
    return cells, fixed


def certificate(adj, blocks=()):
    return pynauty.certificate(pynauty.Graph(len(adj), adjacency_dict=dict(enumerate(adj)),
                                             vertex_coloring=list(map(set, blocks)))).hex()


def extract():
    expected = {key: set() for key in KEYS}
    classes, physical = set(), Counter()
    lines = (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines()
    assert len(lines) == 191
    regular = 0
    for line in lines:
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6}:
            continue
        regular += 1
        if max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        classes.add(certificate(adj))
        for tip, end in pairs(range(22)):
            if end in adj[tip]:
                continue
            for left in pairs(sorted(adj[end] - adj[tip])):
                other = sorted(adj[tip].intersection(*(adj[full] for full in left)))
                if len(other) != 2:
                    continue
                right = tuple(other)
                for first, last, tip1, tip2 in [(left, right, tip, end), (right, left, end, tip)]:
                    for side1, side2 in itertools.product(itertools.permutations(first), itertools.permutations(last)):
                        core = list(side1) + [tip1] + list(side2) + [tip2]
                        outer = sorted(set(range(22)) - set(core))
                        cells = {}
                        for vertex in outer:
                            mask = sum(1 << pos for pos, anchor in enumerate(core) if anchor in adj[vertex])
                            cells.setdefault(mask, []).append(vertex)
                        key = (sum(len(cells.get(mask, [])) for mask in (5, 6)),
                               sum(len(cells.get(mask, [])) for mask in (40, 48)), len(cells.get(36, [])))
                        if key not in expected:
                            assert key[0] > key[1]
                            continue
                        template, fixed = layout(22, 6, key)
                        if {mask: len(cell) for mask, cell in template.items() if cell} != {mask: len(cell) for mask, cell in cells.items()}:
                            continue
                        order = core + [vertex for mask in sorted(cells) for vertex in cells[mask]]
                        assert all((order[dst] in adj[order[src]]) == val for (src, dst), val in fixed.items())
                        marks = [[anchor] for anchor in core] + [cells[mask] for mask in sorted(cells)]
                        expected[key].add(certificate(adj, marks))
                physical[line] += 1
    assert (regular, len(classes), sum(physical.values())) == (10, 3, 136)
    print('census', len(lines), regular, len(classes), 'physical tip-root counts', dict(physical), flush=True)
    print('marked expectations', [(key, len(value)) for key, value in expected.items()], flush=True)
    return expected, classes


def matching_size(adj, left):
    mate = {}
    def augment(vertex, seen):
        for other in sorted(adj[vertex] - seen):
            if other in seen:
                continue
            seen.add(other)
            if other not in mate or augment(mate[other], seen):
                mate[other] = vertex
                return True
        return False
    return sum(augment(vertex, set()) for vertex in range(left))


@lru_cache(None)
def panels(rows, cols, degree):
    out = subprocess.run([ROOT / 'opt/bin/genbg', '-q', '-D2:2', str(rows), str(cols)],
                         capture_output=True, check=True, text=True, timeout=12)
    retained = []
    counts = Counter()
    for line in out.stdout.splitlines():
        edges = decode(line)
        adj = neighbors(rows + cols, edges)
        assert all(src < rows <= dst for src, dst in edges)
        if matching_size(adj, rows) < rows + cols + 2 - degree:
            continue
        counts['matching'] += 1
        if any(len(adj[src] & adj[dst]) > 1 for src, dst in pairs(range(rows))):
            continue
        retained.append(line)
    print('panels', rows, cols, 'all/match/no-C4', len(out.stdout.splitlines()), counts['matching'], len(retained), flush=True)
    return retained


def tip_windows(formula, cells):
    for tip in (2, 5):
        seed = {vertex for mask, cell in cells.items() if mask >> tip & 1 for vertex in cell}
        pool = sorted(set(range(formula.n)) - seed)
        avoids = {}
        for vertex in pool:
            edges = [formula.edge(vertex, member) for member in sorted(seed)]
            if True in [edge is True for edge in edges]:
                continue
            free = [edge for edge in edges if edge is not False]
            if free:
                lit = formula.new()
                formula.add(lit, *free)
                for edge in free:
                    formula.add(-lit, -edge)
                avoids[vertex] = lit
            else:
                avoids[vertex] = True
        formula.cardinality(list(avoids.values()), 0, 5)
        for triple in itertools.combinations(avoids, 3):
            formula.add(*(neg(avoids[vertex]) for vertex in triple), *(formula.edge(*edge) for edge in pairs(triple)))


def build(order, degree, key, mode, index=None):
    cells, fixed = layout(order, degree, key)
    blocks = [[vertex] for vertex in range(6)] + [cell for cell in cells.values() if cell]
    rows, cols = cells[1], cells[8]
    reps = None if mode == 'base' else panels(len(rows), len(cols), degree)
    if index is not None:
        edges = decode(reps[index])
        for ri, src in enumerate(rows):
            for ci, dst in enumerate(cols):
                fixed[src, dst] = (ri, ci + len(rows)) in edges
    if reps is not None:
        blocks = [part for cell in blocks for part in ([[vertex] for vertex in cell] if cell in (rows, cols) else [cell])]
    formula = Cnf(order, fixed)
    for vertex in range(order):
        formula.cardinality([formula.edge(vertex, other) for other in range(order) if other != vertex], degree, degree)
    for triple in itertools.combinations(range(order), 3):
        formula.add(*(neg(formula.edge(*edge)) for edge in pairs(triple)))
    for src, dst in pairs(range(order)):
        if formula.edge(src, dst) is True:
            continue
        paths = [formula.conjunction(formula.edge(src, vertex), formula.edge(dst, vertex))
                 for vertex in range(order) if vertex not in (src, dst)]
        formula.cardinality(paths, 0, 3)
    if reps is not None:
        tip_windows(formula, cells)
        if index is None:
            selectors = []
            for line in reps:
                select = formula.new()
                selectors.append(select)
                edges = decode(line)
                for ri, src in enumerate(rows):
                    for ci, dst in enumerate(cols):
                        lit = formula.edge(src, dst)
                        formula.add(-select, lit if (ri, ci + len(rows)) in edges else neg(lit))
            formula.add(*selectors)
    return formula, blocks


def solve(out, order, degree, key, mode, seconds, index=None):
    tag = ''.join(map(str, key)) + '-' + mode + ('' if index is None else f'-{index}')
    formula, blocks = build(order, degree, key, mode, index)
    cnf = out / (tag + '.cnf')
    formula.write(cnf)
    command = ['nice', '-n', '5', 'timeout', str(3 * seconds + 5), 'prlimit', f'--cpu={seconds}:{seconds+1}',
               '--as=17179869184', ROOT / 'opt/bin/smsg', '-v', str(order), '--dimacs', cnf,
               '--forbid-independent-set', str(degree + 1), '--cutoff', '0', '--initial-partition', *map(lambda cell: str(len(cell)), blocks)]
    if order == 22:
        command += ['-a']
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    with (out / (tag + '.out')).open('w') as stream:
        run = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    elapsed = time.monotonic() - start
    seconds_used = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    output = (out / (tag + '.out')).read_text()
    done = run.returncode == 20 and 'Result: 20' in output
    models = [set(ast.literal_eval(line)) for line in output.splitlines() if line.startswith('[(')]
    print(tag, json.dumps(dict(code=run.returncode, exhausted=done, models=len(models), variables=formula.nvars,
                               clauses=len(formula.clauses), cpu=round(seconds_used, 3), wall=round(elapsed, 3))), flush=True)
    if order == 40 and models:
        for number, edges in enumerate(models):
            (ROOT / 'ralph/found' / f'D_punct{tag}_{number}.g6').write_text(graph6(order, edges) + '\n')
    return done, [neighbors(order, edges) for edges in models]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    parser.add_argument('--key')
    parser.add_argument('--mode', choices=('base', 'panel'), default='panel')
    parser.add_argument('--index', type=int)
    parser.add_argument('--cpu', type=int, default=18)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.key:
        key = tuple(map(int, args.key))
        assert key in KEYS
        solve(args.out, 40, 9, key, args.mode, args.cpu, args.index)
        return
    expected, classes = extract()
    recovered = set()
    for key in KEYS:
        instance = layout(22, 6, key)
        if instance is None:
            assert not expected[key]
            continue
        cells, _ = instance
        colors = [[vertex] for vertex in range(6)] + [cell for cell in cells.values() if cell]
        done, models = solve(args.out, 22, 6, key, args.mode, args.cpu)
        assert done and {certificate(adj, colors) for adj in models} == expected[key], key
        recovered.update(certificate(adj) for adj in models)
    assert recovered == classes
    print('PASS every marked profile and all three unrooted classes', flush=True)


if __name__ == '__main__':
    main()
