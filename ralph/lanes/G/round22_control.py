"""Independent physical controls and board-map crosscheck for round 22."""

import csv
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys

from pysat.solvers import Solver

from round22_fold import Fold, deficit


ROOT = Path(__file__).resolve().parents[3]
REF = ROOT / 'scratch/A/r22'


def flatten(board):
    return ''.join(str(value) for row in board for value in row)


def unflatten(name, width):
    return tuple(tuple(int(cell) for cell in name[start:start + width]) for start in range(0, len(name), width))


def compare_inventory(path):
    local = {flatten(board['grid']): board for board in json.load(open(path))}
    seen = Counter()
    for row in csv.DictReader(open(REF / 'h6.labels.tsv'), delimiter='\t'):
        grid = unflatten(row['representative'], 5)
        left, right = row['left_perm'], row['right_perm']
        mapped = [[0] * 5 for _ in range(5)]
        for first, second in product(range(5), repeat=2):
            a, b = int(left[first]), int(right[second])
            if row['swap'] == '1':
                a, b = b, a
            mapped[a][b] = grid[first][second]
        assert flatten(mapped) == row['label'], row
        seen[row['representative']] += 1
    assert seen == {key: board['orbit_size'] for key, board in local.items()}
    known = {(key, *left, *right) for key, board in local.items() for left, right in board['keys']}
    ref = {(row['board'], *(int(row[key]) for key in ('left_hole_0', 'left_hole_1', 'right_hole_0', 'right_hole_1')))
           for row in csv.DictReader(open(REF / 'h6.holes.tsv'), delimiter='\t')}
    assert known == ref
    print('board transporters, board masses and literal keys: agree', len(local), sum(seen.values()), len(known))


def graph6(order, edges):
    bits = [(first, second) in edges for second in range(1, order) for first in range(second)]
    bits.extend([False] * (-len(bits) % 6))
    return chr(order + 63) + ''.join(chr(63 + sum(value << (5 - idx) for idx, value in enumerate(bits[start:start+6])))
                                    for start in range(0, len(bits), 6))


def decode(text):
    order = ord(text[0]) - 63
    bits = [((ord(char) - 63) >> pos) & 1 for char in text[1:] for pos in reversed(range(6))]
    return {(first, second) for (first, second), bit in zip(
        ((first, second) for second in range(1, order) for first in range(second)), bits) if bit}


def project(fold, model):
    selected = [option for option, variable in fold.gates.items() if variable in model]
    size = len(fold.grid)
    left = [first for first, _ in selected]
    right = sorted(second for _, second in selected)
    mates = tuple(right.index(second) for _, second in selected)
    lhs = tuple(fold.slots[0][first] for first in left)
    rhs = tuple(fold.slots[1][second] for second in right)
    edges = {(0, 1), (2, 5), *((0, anchor) for anchor in range(2, 5)), *((1, anchor) for anchor in range(5, 8))}
    supports = fold.grid + tuple(lhs[index] | rhs[mate] << 3 for index, mate in enumerate(mates))
    for vertex, support in enumerate(supports, 8):
        edges.update((anchor + 2, vertex) for anchor in range(6) if support >> anchor & 1)
    coords = list(range(size)) + [size + slot for slot in left]
    edges.update((first + 8, second + 8) for first, second in combinations(range(len(coords)), 2)
                 if fold.edge(0, coords[first], coords[second]) in model)
    return lhs, rhs, mates, graph6(len(coords) + 8, edges)


def tiny_boards():
    for values in product(range(3), repeat=8):
        if sum(values) != 4:
            continue
        board = unflatten('0' + ''.join(map(str, values)), 3)
        if min((*deficit(board, 0), *deficit(board, 1))) >= 0:
            yield board


def tiny_strict():
    for count in (2, 3):
        seen = 0
        for board in tiny_boards():
            fold = Fold(board, count, False)
            with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
                assert not solver.solve(), (board, count)
            seen += 1
        ref = REF / f'n{14 + count}.d2.classes.tsv'
        assert not list(csv.DictReader(open(ref), delimiter='\t'))
        print('strict alpha<=5', 14 + count, 'boards', seen, 'classes', 0)


def ref_key(row):
    return tuple(row['left']), tuple(row['right']), tuple(row['mates']), row['graph']


def tiny_positive():
    chosen = ('001001110', '001001200', '002000200', '002000110')
    raw = {name: set() for name in chosen}
    canonical = {name: set() for name in chosen}
    for line in open(REF / 'positive/n16.d2.placements.jsonl'):
        row = json.loads(line)
        if row['board'] in raw:
            raw[row['board']].add(ref_key(row))
            canonical[row['board']].add(row['canonical'])
    for name in chosen:
        fold = Fold(unflatten(name, 3), 2, False, bound=7)
        projection = [*fold.gates.values(), *fold.edges[0].values()]
        got = set()
        with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
            while solver.solve():
                signed = set(solver.get_model())
                placement = project(fold, signed)
                assert placement not in got
                got.add(placement)
                solver.add_clause([-literal if literal in signed else literal for literal in projection])
        assert raw[name] == got, (name, len(raw[name]), len(got), next(iter(raw[name] - got), None),
                                  next(iter(got - raw[name]), None))
        labels = subprocess.check_output([ROOT / 'opt/bin/labelg', '-q'], text=True,
                                         input=''.join(row[-1] + '\n' for row in sorted(got))).splitlines()
        assert canonical[name] == set(labels)
        print('positive alpha<=6', name, 'placements', len(got), 'classes', len(set(labels)))


def plant(row):
    fold = Fold(unflatten(row['board'], 3), 2, False, bound=7)
    size = len(fold.grid)
    indices = []
    for side, label in enumerate(('left', 'right')):
        desired = list(row[label])
        active = []
        for slot, mask in enumerate(fold.slots[side]):
            if mask in desired:
                desired.remove(mask)
                active.append(slot)
        assert not desired
        indices.append(active)
    select = {(indices[0][idx], indices[1][pos]) for idx, pos in enumerate(row['mates'])}
    bits = [literal if pair in select else -literal for pair, literal in fold.gates.items()]
    edges = decode(row['graph'])
    coord = {**{idx: 8 + idx for idx in range(size)},
             **{size + slot: 8 + size + idx for idx, slot in enumerate(indices[0])}}
    bits.extend(literal if first in coord and second in coord and (coord[first], coord[second]) in edges else -literal
                for (first, second), literal in fold.edges[0].items())
    return fold, bits


def mutations():
    controls = json.load(open(REF / 'positive/n16.mutations.json'))
    alias = controls['alias']
    fold, bits = plant(alias)
    repeated = next(mask for mask in fold.slots[0] if fold.slots[0].count(mask) > 1)
    twins = [fold.activity[0][idx] for idx, mask in enumerate(fold.slots[0]) if mask == repeated]
    with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
        assert len(twins) == 2 and solver.solve(assumptions=bits)
        solver.add_clause([-literal for literal in twins])
        assert not solver.solve(assumptions=bits)
    short = controls['short_witness']
    fold, bits = plant(short)
    witness = [idx - 8 for idx in short['independent_exterior']]
    clause = [edge for first, second in combinations(witness, 2) if (edge := fold.edge(0, first, second))]
    assert clause
    with Solver(name='cadical195', bootstrap_with=fold.rows) as solver:
        assert solver.solve(assumptions=bits)
        solver.add_clause(clause)
        assert not solver.solve(assumptions=bits)
    print('alias and short padded rows reject their respective physical plants')


if __name__ == '__main__':
    compare_inventory(sys.argv[1])
    tiny_strict()
    tiny_positive()
    mutations()
