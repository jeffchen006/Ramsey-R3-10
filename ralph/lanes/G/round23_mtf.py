"""Add exterior-exterior saturation to the marked h5 relaxation."""

from itertools import combinations
from pathlib import Path
import json
import sys

from pysat.solvers import Solver

import round23_deficit as deficit
from round22_control import decode, unflatten
from round22_deep import projected_activity


def encode(top, grid_right, bins, edges, width):
    clauses = []

    def variable():
        nonlocal top
        top += 1
        return top

    locations = len(grid_right) + len(bins)
    end = len(grid_right)
    contact = {}
    for index, (_, group) in enumerate(bins, end):
        for anchor in range(width):
            hits = [gate for gate, mask in group if anchor in mask]
            if not hits:
                continue
            seen = variable()
            contact[index, anchor] = seen
            clauses.append((-seen, *hits))
            clauses.extend((-gate, seen) for gate in hits)

    def join(witnesses, first, second):
        link = variable()
        clauses.append((-link, first))
        clauses.append((-link, second))
        witnesses.append(link)

    def edge(first, second):
        return edges.get(tuple(sorted((first, second))))

    for (first, second), pair_edge in edges.items():
        witnesses = [pair_edge]
        for site in (first, second):
            if site >= end:
                witnesses.append(-bins[site - end][0])
        if first < end <= second:
            witnesses.extend(contact[second, anchor] for anchor in sorted(grid_right[first])
                             if (second, anchor) in contact)
        if first >= end:
            for anchor in range(width):
                lhs, rhs = contact.get((first, anchor)), contact.get((second, anchor))
                if lhs and rhs:
                    join(witnesses, lhs, rhs)
        for other in range(locations):
            if other not in (first, second) and (lhs := edge(first, other)) and (rhs := edge(second, other)):
                join(witnesses, lhs, rhs)
        clauses.append(tuple(witnesses))
    return top, clauses


def bind(fold):
    width = fold.width
    grid = [{anchor for anchor in range(width) if support >> (anchor + width) & 1} for support in fold.grid]
    bins = [(literal, [(gate, {anchor for anchor in range(width) if fold.slots[1][right] >> anchor & 1})
                       for (left, right), gate in fold.gates.items() if left == index])
            for index, literal in enumerate(fold.activity[0])]
    return grid, bins, fold.edges[0], width


def extended(board, prefix, budget=False, **kwargs):
    fold, physical = deficit.extended(board, prefix, budget, **kwargs)
    fold.variables, rows = encode(fold.variables, *bind(fold))
    for row in rows:
        fold.add(row, 'exterior-MTF')
    return fold, physical


def control(folder):
    cache = {}
    compared = []
    sat = 0
    saturated = 0
    try:
        for line in (folder / 'n17.d3.placements.jsonl').open():
            sample = json.loads(line)
            board = sample['board']
            if board not in cache:
                fold, physical = deficit.original(unflatten(board, 3), '', target=False, bound=7)
                _, rows = encode(fold.variables, *bind(fold))
                cache[board] = fold, physical, Solver(name='cadical195', bootstrap_with=rows)
            fold, physical, solver = cache[board]
            original = projected_activity(fold, sample)
            active = [option for option, gate in fold.gates.items() if gate in original]
            occupied = {site for site, _ in active}
            original.update(literal for site, literal in enumerate(fold.activity[0]) if site in occupied)
            graph = decode(sample['graph'])
            exterior = physical.boundary
            sites = [*range(len(fold.grid)), *(len(fold.grid) + site for site, _ in active)]
            check = [*fold.activity[0], *fold.gates.values(), *fold.edges[0].values()]

            def saturating(edges, positive, test):
                neighborhoods = [set() for _ in range(17)]
                for first, second in edges:
                    neighborhoods[first].add(second)
                    neighborhoods[second].add(first)
                status = True
                for first, second in combinations(range(exterior, 17), 2):
                    if second in neighborhoods[first] or neighborhoods[first] & neighborhoods[second]:
                        continue
                    status = False
                    if not test:
                        neighbors = fold.edge(0, sites[first - exterior], sites[second - exterior])
                        assert neighbors
                        positive.add(neighbors)
                        neighborhoods[first].add(second)
                        neighborhoods[second].add(first)
                assert solver.solve(assumptions=[literal if literal in positive else -literal for literal in check]) == (status or not test)
                return status

            sat += saturating(graph, original, True)
            saturating(graph, set(original), False)
            saturated += 1
            compared.append(board)
    finally:
        for _, _, solver in cache.values():
            solver.delete()
    assert saturated == 1960 and len(set(compared)) == 16 and 0 < sat < 1960
    print('literal exterior maximality:', sat, 'native positives;', saturated, 'greedily saturated positives;',
          1960 - sat, 'unsaturated negatives, 16 smaller boards')


if __name__ == '__main__':
    if sys.argv[1] == 'control-mtf':
        control(Path(sys.argv[2]))
    else:
        assert '--deficit' in sys.argv
        sys.argv.remove('--deficit')
        deficit.base.build = extended
        deficit.base.main()
