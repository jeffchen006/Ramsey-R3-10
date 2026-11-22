"""Physical folded two-defect board CNF and exact target board crosswalk."""

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import argparse
import hashlib
import json
import sys

from pysat.card import CardEnc, EncType


def masks(width):
    return tuple((1 << first) | (1 << second) for first, second in combinations(range(width), 2))


def margin(board, side, anchor):
    return sum(board[anchor]) if not side else sum(row[anchor] for row in board)


def deficit(board, side):
    return tuple(len(board) - 1 - margin(board, side, anchor) for anchor in range(len(board)))


@lru_cache(None)
def padding(width):
    def independent(boundary):
        return all(not (boundary >> first & 1 and boundary >> second & 1)
                   for first, second in ((0, 1), (2, 2 + width),
                                         *((0, 2 + pos) for pos in range(width)),
                                         *((1, 2 + width + pos) for pos in range(width))))
    pad = [0] * (1 << (2 * width))
    for mark in range(1 << (2 + 2 * width)):
        if independent(mark):
            for support in range(len(pad)):
                if not (mark >> 2) & support:
                    pad[support] = max(pad[support], mark.bit_count())
    return tuple(pad)


def board_inventory():
    width = 5
    row_options = [tuple(row for row in product(range(3), repeat=width)
                         if sum(row) <= 4 and (anchor != 0 or row[0] == 0)
                         and sum(row) - sum(bool(cell) for cell in row[1:]) <= bool(anchor))
                   for anchor in range(width)]

    def generate(rows, cols, col_costs, missing):
        if len(rows) == width:
            if not missing:
                yield rows
            return
        for row in row_options[len(rows)]:
            rest = missing - sum(row)
            if not 0 <= rest <= 4 * (width - 1 - len(rows)):
                continue
            updated = tuple(a + b for a, b in zip(cols, row))
            costs = tuple(a + b - (len(rows) != 0 and b != 0) for a, b in zip(col_costs, row))
            if all(used <= 4 and cost <= bool(index)
                   for index, (used, cost) in enumerate(zip(updated, costs))):
                yield from generate((*rows, row), updated, costs, rest)

    raw = set(generate((), (0,) * width, (0,) * width, 18))
    assert len(raw) == 22408
    actions = []
    holes = tuple(tuple(sorted(pair)) for pair in combinations(masks(width), 2) if (pair[0] | pair[1]) & 1)
    for tail in permutations(range(1, width)):
        perm = (0, *tail)
        act_mask = {mask: sum(1 << index for index, src in enumerate(perm) if mask >> src & 1)
                    for mask in masks(width)}
        actions.append((perm, {hole: tuple(sorted(act_mask[mask] for mask in hole)) for hole in holes}))
    assert len(holes) == 30
    records = []
    while raw:
        board = min(raw)
        orbit = set()
        stabilizers = []
        for (left, lhs), (right, rhs) in product(actions, repeat=2):
            transformed = tuple(tuple(board[row][col] for col in right) for row in left)
            for flip, moved in enumerate((transformed, tuple(zip(*transformed)))):
                orbit.add(moved)
                if moved == board:
                    stabilizers.append((flip, lhs, rhs))
        assert orbit <= raw and len(orbit) * len(stabilizers) == 1152
        raw -= orbit
        pairs = set(product(holes, repeat=2))
        keys = []
        while pairs:
            left, right = min(pairs)
            mates = {(rhs[right], lhs[left]) if flip else (lhs[left], rhs[right])
                     for flip, lhs, rhs in stabilizers}
            assert mates <= pairs
            pairs -= mates
            keys.append((left, right))
        records.append(dict(id=len(records), grid=board, orbit_size=len(orbit),
                            stabilizer=len(stabilizers), deficits=[deficit(board, side) for side in range(2)],
                            keys=keys))
    assert len(records) == 49 and sum(len(item['keys']) for item in records) == 19651
    return records


class Fold:
    def __init__(self, board, double_count, target, split=None, strength='full', mutation=None, bound=None):
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
        assert not board[0][0] and all(len(shore) == len(self.pairs) + 2 for shore in self.slots)
        assert len(self.grid) == 4 if width == 3 else len(self.grid) == 18
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
        if target:
            self.mtf(mutation)
            if strength == 'full':
                self.degree()
            if strength == 'budget':
                self.degree()
                self.cardinality(tuple(self.edges[0].values()), 86, True, (), 'edge-budget')
                self.cardinality(tuple(self.edges[0].values()), 86, False, (), 'edge-budget')
        if split is not None:
            side, slot, sign = split
            assert slot < len(self.pairs) and sign in (-1, 1)
            self.add((sign * self.activity[side][slot],), 'split')
        self.padded_blocks()

    def var(self):
        self.variables += 1
        return self.variables

    def add(self, row, tag):
        ordered = tuple(sorted(set(row)))
        if ordered not in self.rows:
            self.rows[ordered] = tag
            self.counts[tag] += 1

    def shore_edges(self, side):
        size = len(self.grid)
        shore = self.slots[side]
        mask = (1 << self.width) - 1
        supports = tuple(site >> (side * self.width) & mask for site in self.grid) + shore
        edges = {}
        for first, second in combinations(range(len(supports)), 2):
            if (self.grid[first] & self.grid[second] if second < size else supports[first] & supports[second]):
                continue
            edge = self.left_edges[first, second] if side and second < size else self.var()
            edges[first, second] = edge
            for vertex in (first, second):
                if vertex >= size:
                    self.add((-edge, self.activity[side][vertex - size]), 'edge-endpoint')
        return edges

    def edge(self, side, one, two):
        return self.edges[side].get(tuple(sorted((one, two))), 0)

    def channel(self, guards, left, right):
        if left == right:
            return
        if left:
            self.add((*guards, -left, *((right,) if right else ())), 'edge-channel')
        if right:
            self.add((*guards, -right, *((left,) if left else ())), 'edge-channel')

    def channel_edges(self):
        size = len(self.grid)
        for (left, right), gate in self.gates.items():
            for grid in range(size):
                self.channel((-gate,), self.edge(0, grid, size + left), self.edge(1, grid, size + right))
        for first, second in combinations(self.options, 2):
            if first[0] == second[0] or first[1] == second[1]:
                continue
            self.channel((-self.gates[first], -self.gates[second]),
                         self.edge(0, size + first[0], size + second[0]),
                         self.edge(1, size + first[1], size + second[1]))

    def triangles(self):
        for vertices in combinations(range(len(self.grid) + len(self.slots[0])), 3):
            edges = tuple(self.edge(0, first, second) for first, second in combinations(vertices, 2))
            if all(edges):
                self.add(tuple(-edge for edge in edges), 'triangle')

    def hall(self):
        width = self.width
        size = len(self.grid)
        for side in range(2):
            cells = [tuple(i for i, support in enumerate(self.grid) if support >> (side * width + anchor) & 1)
                     + tuple(size + slot for slot, mask in enumerate(self.slots[side]) if mask == 1 << anchor)
                     for anchor in range(width)]
            assert all(len(cell) == width - 1 for cell in cells)
            for idx, (row, col) in enumerate(combinations(range(width), 2)):
                count_at_double = self.bound - width
                for guard, count in ((-self.activity[side][idx], count_at_double), (0, count_at_double + 1)):
                    for rows in range(1, width):
                        for left, right in product(combinations(cells[row], rows),
                                                   combinations(cells[col], count - rows)):
                            row_edges = tuple(edge for one, two in product(left, right)
                                              if (edge := self.edge(side, one, two)))
                            self.add(((guard,) if guard else ()) + row_edges, 'private-margin')

    def mtf(self, mutation):
        width = self.width
        size = len(self.grid)
        for row, col in product(range(width), repeat=2):
            if (row or col) and not self.board[row][col]:
                witnesses = tuple(gate for (left, right), gate in self.gates.items()
                                  if self.slots[0][left] >> row & self.slots[1][right] >> col & 1)
                if mutation == 'short' and len(witnesses) > 1:
                    witnesses = witnesses[:-1]
                    mutation = None
                self.add(witnesses, 'anchor-MTF')

        def obligations(side, site, mask):
            for anchor in range(width):
                if mask >> anchor & 1:
                    continue
                supports = tuple(support >> (side * width) & ((1 << width) - 1) for support in self.grid)
                supports += self.slots[side]
                row = tuple(edge for other, support in enumerate(supports) if other != site and support >> anchor & 1
                            if (edge := self.edge(side, site, other)))
                yield anchor, row

        for side in range(2):
            for site, support in enumerate(self.grid):
                for anchor, row in obligations(side, site, support >> (side * width)):
                    if anchor or not support >> ((1 - side) * width) & 1:
                        self.add(row, 'grid-MTF')
            for (left, right), gate in self.gates.items():
                slot, opposite = (left, right) if not side else (right, left)
                for anchor, row in obligations(side, size + slot, self.slots[side][slot]):
                    if anchor or not self.slots[1 - side][opposite] & 1:
                        self.add((-gate, *row), 'slot-MTF')

    def cardinality(self, literals, bound, lower, guards, tag):
        if len(literals) < bound and lower:
            self.add(guards, tag)
            return
        encode = CardEnc.atleast if lower else CardEnc.atmost
        cnf = encode(lits=list(literals), bound=bound, top_id=self.variables, encoding=EncType.seqcounter)
        self.variables = max(self.variables, cnf.nv)
        for row in cnf.clauses:
            self.add((*guards, *row), tag)

    def degree(self):
        size = len(self.grid)
        incident = [tuple(edge for endpoints, edge in self.edges[0].items() if site in endpoints)
                    for site in range(size + len(self.slots[0]))]
        for site in range(size):
            self.cardinality(incident[site], 5, True, (), 'degree')
            self.cardinality(incident[site], 7, False, (), 'degree')
        slot_bounds = {}
        for (left, right), gate in self.gates.items():
            ctrl = self.slots[0][left].bit_count(), self.slots[1][right].bit_count()
            slot_bounds.setdefault((left, ctrl), []).append(gate)
        for (left, (lhs, rhs)), gates in slot_bounds.items():
            held = self.var()
            self.add((-held, *gates), 'degree-guard')
            for gate in gates:
                self.add((-gate, held), 'degree-guard')
            self.cardinality(incident[size + left], 6 - min(lhs, rhs), True, (-held,), 'degree')
            self.cardinality(incident[size + left], 9 - lhs - rhs, False, (-held,), 'degree')

    def padded_blocks(self):
        size = len(self.grid)
        limit = 6 if self.target else size + self.double_count + 2
        pad = padding(self.width)
        common = [sum(1 << other for other, grid in enumerate(self.grid) if site != other and support & grid)
                  for site, support in enumerate(self.supports)]

        def witness(sites, edges, supports):
            if self.target:
                choices = (1 << size) - 1
                for site in sites:
                    choices &= common[site]
                if not padded(supports, len(sites), choices):
                    return False
            elif len(sites) + pad[supports] < self.bound:
                return False
            self.add(edges, 'padded-I')
            return True

        def padded(supports, count, choices):
            if count + pad[supports] >= self.bound:
                return True
            while count + choices.bit_count() + pad[supports] >= self.bound:
                low = choices & -choices
                choices -= low
                site = low.bit_length() - 1
                if padded(supports | self.grid[site], count + 1, choices & common[site]):
                    return True
            return False

        def extend(sites, physical, edges, support, start, stop):
            if witness(sites, edges, support):
                return
            if len(sites) >= limit:
                return
            if not self.target and len(sites) + (stop - start) + pad[support] < self.bound:
                return
            for site in range(start, stop):
                if site < size:
                    physical_site = site
                    selector = ()
                else:
                    first, second = self.options[site - size]
                    if any(prev >= size and (first == self.options[prev - size][0]
                                             or second == self.options[prev - size][1]) for prev in sites):
                        continue
                    physical_site = size + first
                    selector = (-self.gates[first, second],)
                more = tuple(edge for prev in physical if (edge := self.edge(0, prev, physical_site)))
                extend((*sites, site), (*physical, physical_site), (*edges, *selector, *more),
                       support | self.supports[site], site + 1, stop)

        if self.target:
            extend((), (), (), 0, 0, size)
            for (left, right), gate in self.gates.items():
                site = size + self.options.index((left, right))
                extend((site,), (size + left,), (-gate,), self.supports[site], 0, size)
        else:
            extend((), (), (), 0, 0, len(self.supports))

    def dump(self, stream):
        print('p cnf', self.variables, len(self.rows), file=stream)
        for row in self.rows:
            print(*row, 0, file=stream)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('inventory')
    emit = sub.add_parser('emit')
    emit.add_argument('manifest')
    emit.add_argument('board', type=int)
    emit.add_argument('--split', nargs=3, type=int)
    emit.add_argument('--strength', choices=('full', 'light', 'budget'), default='full')
    args = parser.parse_args()
    if args.action == 'inventory':
        print(json.dumps(board_inventory(), separators=(',', ':')))
    else:
        record = json.load(open(args.manifest))[args.board]
        assert record['id'] == args.board
        fold = Fold(record['grid'], 8, True, args.split, args.strength)
        fold.dump(sys.stdout)
        print(json.dumps(dict(board=args.board, grid=record['grid'], split=args.split, strength=args.strength,
                              counts=fold.counts, variables=fold.variables, clauses=len(fold.rows),
                              manifest=hashlib.sha256(open(args.manifest, 'rb').read()).hexdigest())), file=sys.stderr)


if __name__ == '__main__':
    main()
