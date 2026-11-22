"""Three-defect setup, reusing frozen physical edge and witness routines."""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

from pysat.solvers import Solver

from round22_control import ROOT, flatten, project, ref_key, unflatten
from round22_fold import Fold, deficit, masks


class ThreeDefect(Fold):
    def __init__(self, board, double_count, target, bound=None, peer=True):
        self.board = board
        self.width = width = len(board)
        self.target = target
        self.bound = bound if bound is not None else 2 * width
        self.double_count = double_count
        self.grid = tuple((1 << row) | (1 << (width + col))
                          for row, col in product(range(width), repeat=2) for _ in range(board[row][col]))
        self.pairs = masks(width)
        self.slots = tuple(self.pairs + tuple(1 << index for index, amount in enumerate(deficit(board, side))
                                             for _ in range(amount)) for side in range(2))
        assert not board[0][0] and all(len(shore) == len(self.pairs) + 3 for shore in self.slots)
        assert len(self.grid) == width * (width - 1) - 3
        self.variables = 0
        self.rows = {}
        self.counts = Counter()
        self.activity = tuple(tuple(self.var() for _ in shore) for shore in self.slots)
        self.gates = {(left, right): self.var() for left, lhs in enumerate(self.slots[0])
                      for right, rhs in enumerate(self.slots[1])
                      if not (lhs & rhs & 1) and lhs.bit_count() + rhs.bit_count() >= 3}
        self.options = tuple(self.gates)
        self.supports = self.grid + tuple(self.slots[0][left] | (self.slots[1][right] << width)
                                          for left, right in self.options)
        self.left_edges = self.shore_edges(0)
        self.edges = (self.left_edges, self.shore_edges(1))
        for side in range(2):
            incident = []
            for slot, active in enumerate(self.activity[side]):
                selectors = [gate for option, gate in self.gates.items() if option[side] == slot]
                self.add((-active, *selectors), 'mate')
                for gate in selectors:
                    self.add((-gate, active), 'mate')
                for one, two in combinations(selectors, 2):
                    self.add((-one, -two), 'injective')
                if slot >= len(self.pairs):
                    self.add((active,), 'singleton')
                elif self.slots[side][slot] & 1:
                    incident.append(active)
            doubles = self.activity[side][:len(self.pairs)]
            for selected in combinations(doubles, double_count + 1):
                self.add(tuple(-literal for literal in selected), 'population')
            for absent in combinations(doubles, len(doubles) - double_count + 1):
                self.add(absent, 'population')
            if target:
                self.add(tuple(-literal for literal in incident), 'cross-degree')
        self.channel_edges()
        self.triangles()
        self.hall()
        if peer:
            self.peer_hall()
        if target:
            self.mtf(None)
            self.degree()
        self.padded_blocks()

    def peer_hall(self):
        width = self.width
        shore_mask = (1 << width) - 1
        noncross = shore_mask ^ 1
        for side in range(2):
            for anchor in range(width):
                vertex = 1 << anchor
                singletons = tuple(slot for slot, support in enumerate(self.slots[side]) if support == vertex)
                matching = 3 * width - self.bound - 2 + (anchor == 0)
                for contacts in range(2, noncross + 1, 2):
                    grid_hits = sum((support >> (side * width) & shore_mask) == vertex and
                                    bool(support >> ((1 - side) * width) & contacts) for support in self.grid)
                    still_need = matching - (width - 1 - contacts.bit_count()) - grid_hits
                    if still_need <= 0:
                        continue
                    if still_need > len(singletons):
                        self.add((), 'peer-Hall')
                        continue
                    for failures in combinations(singletons, len(singletons) - still_need + 1):
                        self.add(tuple(selector for option, selector in self.gates.items()
                                       if option[side] in failures and
                                       self.slots[1 - side][option[1 - side]] & contacts), 'peer-Hall')


def controls(base):
    rows = [json.loads(line) for line in (base / 'n17.d3.placements.jsonl').open()]
    references = {}
    for row in rows:
        references.setdefault(row['board'], set()).add(ref_key(row))
    canonical = {(row['board'], row['canonical']) for row in rows}
    matched, strict = set(), 0
    for entries in product(range(3), repeat=8):
        if sum(entries) != 3:
            continue
        board = unflatten('0' + ''.join(map(str, entries)), 3)
        if min(*deficit(board, 0), *deficit(board, 1)) < 0:
            continue
        name = flatten(board)
        fold = ThreeDefect(board, 3, False, bound=6)
        with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
            assert not solver.solve(), (board, 6)
        strict += 1
        fold = ThreeDefect(board, 3, False, bound=7)
        projection = [*fold.gates.values(), *fold.edges[0].values()]
        placements = set()
        with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
            while solver.solve():
                signed = set(solver.get_model())
                placement = project(fold, signed)
                assert placement not in placements
                placements.add(placement)
                solver.add_clause([-lit if lit in signed else lit for lit in projection])
        assert placements == references.get(name, set()), (name, len(placements), len(references.get(name, ())))
        if placements:
            labels = subprocess.check_output([ROOT / 'opt/bin/labelg', '-q'], text=True,
                                             input=''.join(row[-1] + '\n' for row in sorted(placements))).splitlines()
            matched.update((name, label) for label in labels)
    assert canonical == matched
    print('strict/relaxed literal boards', strict, 'strict solutions 0; positive boards', len(references),
          'exact placements', sum(map(len, references.values())), 'distinct classes', len({label for _, label in matched}),
          'board/class incidences', len(matched))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    check = sub.add_parser('controls')
    check.add_argument('base', type=Path)
    emit = sub.add_parser('emit')
    emit.add_argument('manifest', type=Path)
    emit.add_argument('board', type=int)
    emit.add_argument('--strength', choices=('full',), default='full')
    args = parser.parse_args()
    if args.action == 'controls':
        controls(args.base)
    else:
        record = json.loads(args.manifest.read_text())[args.board]
        assert record['id'] == args.board
        fold = ThreeDefect(record['grid'], 8, True)
        fold.dump(sys.stdout)
        print(json.dumps(dict(board=args.board, grid=record['grid'], split=None, strength='full', counts=fold.counts,
                              variables=fold.variables, clauses=len(fold.rows),
                              manifest=hashlib.sha256(args.manifest.read_bytes()).hexdigest())), file=sys.stderr)
