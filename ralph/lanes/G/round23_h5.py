"""Compact physical witness rows for the marked three-defect h5 board."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from pysat.solvers import Solver

from round22_control import decode, graph6, unflatten
from round22_deep import projected_activity
from round22_three import ThreeDefect


class Physical:
    """Independent address/variable reconstruction; not based on Fold edges or selectors."""

    def __init__(self, board):
        self.width = width = len(board)
        self.boundary = 2 + 2 * width
        self.fixed_edges = {(0, 1), (2, 2 + width), *((0, 2 + ix) for ix in range(width)),
                            *((1, 2 + width + ix) for ix in range(width))}
        contacts = [(row, col) for row, col in product(range(width), repeat=2) for _ in range(board[row][col])]
        self.grid = tuple(frozenset((2 + row, 2 + width + col)) for row, col in contacts)
        self.slots = []
        for side in range(2):
            offset = 2 + side * width
            shore = [frozenset(pair) for pair in combinations(range(offset, offset + width), 2)]
            for ix in range(width):
                count = (width - 1) - sum(contact[side] == ix for contact in contacts)
                assert count >= 0
                shore.extend([frozenset((offset + ix,))] * count)
            self.slots.append(shore)
        self.gates = {}
        self.options = {}
        last = sum(map(len, self.slots))
        for left, right in product(*[range(len(shore)) for shore in self.slots]):
            support = self.slots[0][left] | self.slots[1][right]
            if {2, 2 + width} <= support or len(support) == 2:
                continue
            last += 1
            self.gates[left, right] = last
            self.options[left, right] = support
        locations = self.grid + tuple(self.slots[0])
        self.edges = {}
        for one, two in combinations(range(len(locations)), 2):
            if not locations[one].isdisjoint(locations[two]):
                continue
            last += 1
            self.edges[one, two] = last

    def row(self, record, forbidden):
        grids = tuple(record['grid'])
        pairs = tuple(map(tuple, record['options']))
        boundary = tuple(record['boundary'])
        assert grids == tuple(sorted(set(grids))) and all(0 <= ix < len(self.grid) for ix in grids)
        assert pairs == tuple(sorted(pairs)) and all(option in self.gates for option in pairs)
        assert all(len(set(coords)) == len(pairs) for coords in zip(*pairs))
        assert boundary == tuple(sorted(set(boundary))) and all(0 <= ix < self.boundary for ix in boundary)
        assert all(pair not in self.fixed_edges for pair in combinations(boundary, 2))
        assert len(grids) + len(pairs) + len(boundary) == forbidden
        sites = [(ix, self.grid[ix]) for ix in grids] + [(len(self.grid) + left, self.options[left, right])
                                                        for left, right in pairs]
        assert all(support.isdisjoint(boundary) for _, support in sites)
        clause = [-self.gates[pair] for pair in pairs]
        for (first, left), (second, right) in combinations(sites, 2):
            if left.isdisjoint(right):
                clause.append(self.edges[first, second])
        return tuple(sorted(clause))

    def model_witness(self, positive, forbidden):
        active = [option for option, gate in self.gates.items() if gate in positive]
        assert all(len(set(coords)) == len(active) for coords in zip(*active))
        physical = [(ix, support) for ix, support in enumerate(self.grid)]
        physical.extend((len(self.grid) + left, self.options[left, right]) for left, right in active)
        edges = set(self.fixed_edges)
        for ix, (_, support) in enumerate(physical, self.boundary):
            edges.update((anchor, ix) for anchor in support)
        for (idx, (first, left)), (jdx, (second, right)) in combinations(enumerate(physical, self.boundary), 2):
            if self.edges.get((first, second)) in positive:
                assert left.isdisjoint(right)
                edges.add((idx, jdx))
        order = self.boundary + len(physical)
        adjacent = [0] * order
        for one, two in edges:
            adjacent[one] |= 1 << two
            adjacent[two] |= 1 << one
        assert all(not adjacent[one] & adjacent[two] for one, two in edges)

        def visit(remaining, wanted, chosen):
            if not wanted:
                return chosen
            while remaining.bit_count() >= wanted:
                low = remaining & -remaining
                remaining ^= low
                ans = visit(remaining & ~adjacent[low.bit_length() - 1], wanted - 1, chosen | low)
                if ans is not None:
                    return ans
            return None

        found = visit((1 << order) - 1, forbidden, 0)
        if found is None:
            return None, graph6(order, edges)
        selected = [ix for ix in range(order) if found >> ix & 1]
        start = self.boundary + len(self.grid)
        result = dict(boundary=[ix for ix in selected if ix < self.boundary],
                      grid=[ix - self.boundary for ix in selected if self.boundary <= ix < start],
                      options=[active[ix - start] for ix in selected if ix >= start])
        assert not any(lit in positive if lit > 0 else -lit not in positive for lit in self.row(result, forbidden))
        return result, None


def optioncheck(fold, physical):
    assert physical.gates == fold.gates and physical.edges == fold.edges[0]


def build(board, prefix, budget=False, target=True, bound=None):
    fold = ThreeDefect(board, 8 if target else 3, target, bound=bound)
    physical = Physical(board)
    optioncheck(fold, physical)
    if budget is not False:
        budget = 86 if budget is True else budget
        edges = tuple(fold.edges[0].values())
        fold.cardinality(edges, budget, False, (), 'edge-budget')
        fold.cardinality(edges, budget, True, (), 'edge-budget')
    assert len(prefix) <= len(fold.pairs) and all(sign in '01' for sign in prefix)
    for index, sign in enumerate(prefix):
        fold.add(((1 if sign == '1' else -1) * fold.activity[0][index],), 'occupancy')
    return fold, physical


def load_models(seed):
    signed = [int(word) for line in seed.read_text().splitlines() if line.startswith('v ')
              for word in line.split()[1:] if word != '0']
    return {literal for literal in signed if literal > 0}


def model_loop(fold, physical, out, rounds, conflicts):
    reasons = Counter()
    with out.open('a', buffering=1) as output, Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
        for attempt in range(rounds):
            solver.conf_budget(conflicts)
            result = solver.solve_limited()
            if result is not True:
                print(json.dumps(dict(attempt=attempt, terminal=result, **reasons)), flush=True)
                return
            positive = {value for value in solver.get_model() if value > 0}
            record, graph = physical.model_witness(positive, fold.bound)
            if record is None:
                print(json.dumps(dict(attempt=attempt, graph=graph, **reasons)), flush=True)
                return
            row = physical.row(record, fold.bound)
            solver.add_clause(row)
            output.write(json.dumps(record) + '\n')
            reasons[f"outside_{len(record['grid']) + len(record['options'])}"] += 1
        print(json.dumps(dict(attempt=rounds, rows_limit=True, **reasons)), flush=True)


def controls(base):
    seen = Counter()
    folds = {}
    mutations = {}
    for line in (base / 'n17.d3.placements.jsonl').open():
        placement = json.loads(line)
        name = placement['board']
        if name not in folds:
            folds[name] = build(unflatten(name, 3), '', target=False, bound=7)
        fold, oracle = folds[name]
        positive = projected_activity(fold, placement)
        raw = decode(placement['graph'])
        witness, recovered = oracle.model_witness(positive, 7)
        assert witness is None and recovered == placement['graph']
        witness, recovered = oracle.model_witness(positive, 6)
        assert witness is not None and recovered is None
        present = [option for option, guard in oracle.gates.items() if guard in positive]
        vertices = [*witness['boundary'], *(oracle.boundary + ix for ix in witness['grid']),
                    *(oracle.boundary + len(oracle.grid) + present.index(option) for option in witness['options'])]
        assert len(set(vertices)) == 6 and not any(tuple(sorted(pair)) in raw for pair in combinations(vertices, 2))
        seen.update({'positive': 1, 'negative': 1, f"options_{len(witness['options'])}": 1})
        if witness['boundary'] and 'short' not in mutations:
            altered = dict(witness, boundary=witness['boundary'][:-1])
            try:
                oracle.row(altered, 6)
            except AssertionError:
                mutations['short'] = (name, altered)
            else:
                raise AssertionError('short padding accepted')
        if witness['options'] and 'unguarded' not in mutations:
            row = oracle.row(witness, 6)
            guard = -oracle.gates[witness['options'][0]]
            assert guard in row
            if len(witness['options']) >= 2:
                first, second, *rest = witness['options']
                altered = dict(witness, options=sorted([first, (first[0], second[1]), *rest]))
                try:
                    oracle.row(altered, 6)
                except AssertionError:
                    mutations['unguarded'] = (name, altered)
                else:
                    raise AssertionError('reused slot accepted')
    assert seen['positive'] == seen['negative'] == 1960 and len(folds) == 16 and len(mutations) == 2
    for name, (fold, oracle) in folds.items():
        first = next(json.loads(line) for line in (base / 'n17.d3.placements.jsonl').open()
                     if json.loads(line)['board'] == name)
        projection = [*oracle.gates.values(), *oracle.edges.values()]
        positive = projected_activity(fold, first)
        assumptions = [bit if bit in positive else -bit for bit in projection]
        physical_count = sum(1 for first, _ in decode(first['graph']) if first >= oracle.boundary)
        for delta in (-1, 0, 1):
            restricted, _ = build(fold.board, '', physical_count + delta, target=False, bound=7)
            with Solver(name='cadical195', bootstrap_with=restricted.rows) as solver:
                assert solver.solve(assumptions=assumptions) == (delta == 0)
    print(json.dumps(dict(boards=len(folds), exact_count_controls=16 * 3, **seen, mutations=mutations), sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('emit', 'learn', 'seed', 'control'))
    parser.add_argument('manifest', type=Path)
    parser.add_argument('board', nargs='?', type=int)
    parser.add_argument('prefix', nargs='?', default='-')
    parser.add_argument('--budget', action='store_true')
    parser.add_argument('--witnesses', type=Path)
    parser.add_argument('--seed-log', type=Path)
    parser.add_argument('--rounds', type=int, default=1000)
    parser.add_argument('--conflicts', type=int, default=20000)
    opts = parser.parse_args()
    if opts.action == 'control':
        return controls(opts.manifest)
    raw = opts.manifest.read_bytes()
    record = json.loads(raw)[opts.board]
    assert record['id'] == opts.board
    prefix = '' if opts.prefix == '-' else opts.prefix
    fold, physical = build(record['grid'], prefix, opts.budget)
    if opts.action == 'seed':
        rec, graph = physical.model_witness(load_models(opts.seed_log), 10)
        assert rec is not None and graph is None
        print(json.dumps(rec))
        return
    witness_hash = None
    if opts.witnesses and opts.witnesses.exists():
        witnesses = opts.witnesses.read_bytes()
        witness_hash = hashlib.sha256(witnesses).hexdigest()
        for line in witnesses.splitlines():
            fold.add(physical.row(json.loads(line), 10), 'physical-I10')
    if opts.action == 'learn':
        return model_loop(fold, physical, opts.witnesses, opts.rounds, opts.conflicts)
    fold.dump(sys.stdout)
    print(json.dumps(dict(board=opts.board, grid=record['grid'], prefix=prefix, budget=opts.budget,
                          counts=fold.counts, variables=fold.variables, clauses=len(fold.rows),
                          manifest=hashlib.sha256(raw).hexdigest(), witnesses=witness_hash)), file=sys.stderr)


if __name__ == '__main__':
    main()
