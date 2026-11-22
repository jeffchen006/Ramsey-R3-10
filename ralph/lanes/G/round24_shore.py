"""Add two physical shore projections of an I10 without pinning its mates."""

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

from pysat.solvers import Solver

import round23_deficit


def row(fold, physical, witness):
    side, boundary, coords = witness['side'], witness['boundary'], witness['coords']
    grids = len(physical.grid)
    assert side in (0, 1) and len(boundary) + len(coords) == fold.bound
    assert boundary == sorted(set(boundary)) and coords == sorted(set(coords))
    assert all(0 <= vertex < physical.boundary for vertex in boundary)
    assert all(0 <= coord < grids + len(physical.slots[side]) for coord in coords)
    assert not any(pair in physical.fixed_edges for pair in combinations(boundary, 2))
    selected = set(boundary)
    clause = []
    for coord in coords:
        if coord < grids:
            assert physical.grid[coord].isdisjoint(selected)
            continue
        slot = coord - grids
        assert physical.slots[side][slot].isdisjoint(selected)
        clause.append(-fold.activity[side][slot])
        for pair, gate in physical.gates.items():
            if pair[side] == slot and not physical.slots[1 - side][pair[1 - side]].isdisjoint(selected):
                clause.append(gate)
    clause.extend(fold.edges[side][pair] for pair in combinations(coords, 2) if pair in fold.edges[side])
    assert len(clause) == len(set(clause))
    return tuple(sorted(clause))


def projected(physical, exact):
    for side in (0, 1):
        yield dict(side=side, boundary=exact['boundary'],
                   coords=sorted([*exact['grid'], *(len(physical.grid) + pair[side] for pair in exact['options'])]))


def learn(fold, physical, destination, rounds, conflicts):
    count = 0
    with destination.open('a', buffering=1) as output, Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
        for attempt in range(rounds):
            solver.conf_budget(conflicts)
            state = solver.solve_limited()
            if state is not True:
                print(json.dumps(dict(attempt=attempt, terminal=state, clauses=count)), flush=True)
                return
            signed = set(solver.get_model())
            record, graph = physical.model_witness({value for value in signed if value > 0}, fold.bound)
            if record is None:
                print(json.dumps(dict(attempt=attempt, graph=graph, clauses=count)), flush=True)
                return
            cuts = {row(fold, physical, fixture): fixture for fixture in projected(physical, record)}
            for clause, fixture in cuts.items():
                assert all(-literal in signed for literal in clause)
                solver.add_clause(clause)
                output.write(json.dumps(fixture, sort_keys=True) + '\n')
                count += 1
    print(json.dumps(dict(attempt=rounds, rows_limit=True, clauses=count)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('emit', 'learn'))
    parser.add_argument('manifest', type=Path)
    parser.add_argument('board', type=int)
    parser.add_argument('prefix')
    parser.add_argument('--witnesses', type=Path)
    parser.add_argument('--shore', type=Path, required=True)
    parser.add_argument('--rounds', type=int, default=600)
    parser.add_argument('--conflicts', type=int, default=250000)
    options = parser.parse_args()
    raw = options.manifest.read_bytes()
    board = json.loads(raw)[options.board]
    assert board['id'] == options.board
    prefix = '' if options.prefix == '-' else options.prefix
    fold, physical = round23_deficit.extended(board['grid'], prefix)
    witnesses = options.witnesses.read_bytes() if options.witnesses is not None else None
    if witnesses is not None:
        for line in witnesses.splitlines():
            fold.add(physical.row(json.loads(line), 10), 'physical-I10')
    shore = options.shore.read_bytes()
    for line in shore.splitlines():
        fold.add(row(fold, physical, json.loads(line)), 'shore-I10')
    if options.action == 'learn':
        learn(fold, physical, options.shore, options.rounds, options.conflicts)
    else:
        fold.dump(sys.stdout)
        print(json.dumps(dict(board=options.board, grid=board['grid'], prefix=prefix, budget=False,
                              counts=fold.counts, variables=fold.variables, clauses=len(fold.rows),
                              manifest=hashlib.sha256(raw).hexdigest(), shore=hashlib.sha256(shore).hexdigest(),
                              witnesses=None if witnesses is None else hashlib.sha256(witnesses).hexdigest())), file=sys.stderr)


if __name__ == '__main__':
    main()
