"""Four-defect folded-board encoding and independently pinned controls."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path

from pysat.solvers import Solver

from round22_fold import deficit, masks
from round22_three import ThreeDefect
from round23_deficit import encode, places
from round23_h5 import Physical, optioncheck


class FourDefect(ThreeDefect):
    def __init__(self, board, double_count, target, bound=None):
        self.board = board
        self.width = width = len(board)
        self.target = target
        self.bound = 2 * width if bound is None else bound
        self.double_count = double_count
        self.grid = tuple(1 << row | 1 << (width + col) for row, col in product(range(width), repeat=2)
                          for _ in range(board[row][col]))
        self.pairs = masks(width)
        self.slots = tuple(self.pairs + tuple(1 << anchor for anchor, count in enumerate(deficit(board, side))
                                             for _ in range(count)) for side in (0, 1))
        assert not board[0][0] and all(len(shore) == len(self.pairs) + 4 for shore in self.slots)
        assert len(self.grid) == width * (width - 1) - 4
        self.variables = 0
        self.rows = {}
        self.counts = Counter()
        self.activity = tuple(tuple(self.var() for _ in shore) for shore in self.slots)
        self.gates = {(left, right): self.var() for left, lhs in enumerate(self.slots[0])
                      for right, rhs in enumerate(self.slots[1])
                      if not (lhs & rhs & 1) and lhs.bit_count() + rhs.bit_count() >= 3}
        self.options = tuple(self.gates)
        self.supports = self.grid + tuple(self.slots[0][left] | self.slots[1][right] << width
                                          for left, right in self.options)
        self.left_edges = self.shore_edges(0)
        self.edges = (self.left_edges, self.shore_edges(1))
        for side in (0, 1):
            crossed = []
            for slot, active in enumerate(self.activity[side]):
                selectors = [gate for pair, gate in self.gates.items() if pair[side] == slot]
                self.add((-active, *selectors), 'mate')
                for gate in selectors:
                    self.add((-gate, active), 'mate')
                for first, second in combinations(selectors, 2):
                    self.add((-first, -second), 'injective')
                if slot >= len(self.pairs):
                    self.add((active,), 'singleton')
                elif self.slots[side][slot] & 1:
                    crossed.append(active)
            doubles = self.activity[side][:len(self.pairs)]
            for selected in combinations(doubles, double_count + 1):
                self.add(tuple(-value for value in selected), 'population')
            for missing in combinations(doubles, len(doubles) - double_count + 1):
                self.add(missing, 'population')
            if target:
                self.add(tuple(-literal for literal in crossed), 'cross-degree')
        self.channel_edges()
        self.triangles()
        self.hall()
        self.peer_hall()
        if target:
            self.mtf(None)
            self.degree()
        if self.bound <= 2 + 2 * width + len(self.grid) + double_count + 4:
            self.padded_blocks()


def controls():
    checked = 0
    for cells in combinations(range(1, 9), 2):
        board = tuple(tuple(3 * row + col in cells for col in range(3)) for row in range(3))
        if min(*deficit(board, 0), *deficit(board, 1)) < 0:
            continue
        fold = FourDefect(board, 3, False, bound=18)
        with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
            assert not solver.solve()
        checked += 1
    assert checked == 28
    board = tuple(tuple(int(row != col and col - row != 1) for col in range(4)) for row in range(4))
    assert sum(map(sum, board)) == 9
    board = tuple(tuple(int(value and (i, j) != (3, 0)) for j, value in enumerate(row))
                  for i, row in enumerate(board))
    fold = FourDefect(board, 4, False, bound=27)
    physical = Physical(board)
    optioncheck(fold, physical)
    counted = Counter()
    candidates = range(len(fold.pairs))
    trials = [((0, 1, 2, 3), (0, 2, 3, 5)), ((0, 3, 4, 5), (1, 2, 4, 5)),
              ((1, 2, 3, 4), (0, 1, 2, 3)), ((0, 1, 4, 5), (0, 1, 4, 5))]
    for left, right in trials:
        own = tuple(range(len(fold.pairs), len(fold.slots[0])))
        for left_perm, right_perm in product(permutations(left), permutations(right)):
            sites = tuple(zip(left_perm, own)) + tuple(zip(own, right_perm))
            if any({2, 2 + fold.width} <= (physical.slots[0][lhs] | physical.slots[1][rhs]) for lhs, rhs in sites):
                continue
            counted[left, right] += 1
    all_gates = set(fold.gates.values())
    matched = Counter()
    for scope in trials:
        with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
            assumed = [-edge for edge in fold.edges[0].values()]
            assumed += [fold.activity[side][slot] * (1 if slot in occupied else -1)
                        for side, occupied in enumerate(scope) for slot in candidates]
            while solver.solve(assumptions=assumed):
                gates = set(solver.get_model()) & all_gates
                observed = [pair for pair, literal in fold.gates.items() if literal in gates]
                left = tuple(sorted(lhs for lhs, _ in observed if lhs in candidates))
                right = tuple(sorted(rhs for _, rhs in observed if rhs in candidates))
                assert (left, right) == scope
                matched[scope] += 1
                solver.add_clause([-value for value in gates])
    assert matched == counted and sum(counted.values()) > 0
    print('4-defect controls:', checked, 'width-3 impossible boards (pigeonhole);',
          len(counted), 'width-4 labelled occupancy pairs and', sum(counted.values()),
          'independent triangle-free edgeless-exterior placements at bound 27')


def emit(manifest, number, prefix):
    raw = manifest.read_bytes()
    record = json.loads(raw)[number]
    assert record['id'] == number
    fold = FourDefect(record['grid'], 8, True)
    optioncheck(fold, Physical(record['grid']))
    order = [(0, 0), (0, 1), (1, 0), (1, 1)] + [(side, slot) for slot in range(2, 10) for side in (0, 1)]
    assert len(prefix) <= len(order) and set(prefix) <= {'0', '1'}
    for (side, slot), value in zip(order, prefix):
        fold.add((fold.activity[side][slot] * (1 if value == '1' else -1),), 'occupancy')
    fold.variables, delta = encode(fold.variables, places(fold), 8)
    for extra in delta:
        fold.add(extra, 'deficit-budget')
    fold.dump(sys.stdout)
    print(json.dumps(dict(board=number, prefix=prefix, grid=record['grid'], variables=fold.variables,
                          clauses=len(fold.rows), counts=fold.counts, manifest=hashlib.sha256(raw).hexdigest())),
          file=sys.stderr)


if __name__ == '__main__':
    cli = argparse.ArgumentParser()
    cli.add_argument('operation', choices=('controls', 'emit'))
    cli.add_argument('manifest', type=Path, nargs='?')
    cli.add_argument('board', type=int, nargs='?')
    cli.add_argument('prefix', nargs='?', default='-')
    args = cli.parse_args()
    if args.operation == 'controls':
        controls()
    else:
        emit(args.manifest, args.board, '' if args.prefix == '-' else args.prefix)
