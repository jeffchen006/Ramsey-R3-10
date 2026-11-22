from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path
from subprocess import run
import sys

from round19_shared import ROOT, SCOUT, generate, support_layout


FROZEN = ROOT / 'scratch/G/round19/h7-prereg.json'
BOARDS = json.loads((SCOUT / 'grid.5.1.json').read_text())


def pairs(width):
    return tuple((1 << first) | (1 << second)
                 for first, second in combinations(range(width), 2))


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=1, sort_keys=True) + '\n')


def pilot_input(pilot):
    plan = json.loads(FROZEN.read_text())['pilots'][pilot - 1]
    assert plan['pilot'] == pilot
    data = BOARDS[plan['board']]
    left = tuple(plan['shape']) + (1 << data['left'],)
    right = pairs(5) + (1 << data['right'],)
    assert (len(left), len(right), left[-1]) == (9, 11, plan['singleton'])
    return data['grid'], left, right


def verify_board_orbits():
    plans = json.loads(FROZEN.read_text())
    all_pairs = frozenset(pairs(5))
    holes = tuple(sorted(tuple(sorted(two)) for two in combinations(all_pairs, 2)
                         if any(mask & 1 for mask in two)))
    assert len(holes) == 30
    frozen_schemes = json.loads((SCOUT.parent / 'r015_N/schemes.json').read_text())
    old_left, old_right = (tuple(sorted(all_pairs.difference(side)))
                           for side in frozen_schemes['leaf+matching.0'][1])
    baseline, all_keys = set(), set()
    per_pilot = {}
    stabilizers = []
    perms = tuple((0, *perm) for perm in permutations(range(1, 5)))
    mask_move = {(perm, mask): sum(1 << perm[vertex] for vertex in range(5)
                                   if mask & (1 << vertex))
                 for perm in perms for mask in all_pairs}

    for board, data in enumerate(BOARDS):
        grid = data['grid']
        cells = tuple((row, col, repeat) for row, counts in enumerate(grid)
                      for col, size in enumerate(counts) for repeat in range(size))
        assert len(cells) == 19 and not grid[0][0]
        assert [sum(row) for row in grid] == [4 - (idx == data['left']) for idx in range(5)]
        assert [sum(col) for col in zip(*grid)] == [4 - (idx == data['right']) for idx in range(5)]
        target = frozenset(cells)
        actions = []
        for lhs, rhs in product(perms, repeat=2):
            forward = frozenset((lhs[row], rhs[col], repeat) for row, col, repeat in cells)
            if forward == target:
                assert lhs[data['left']] == data['left'] and rhs[data['right']] == data['right']
                actions.append((False, lhs, rhs))
            if frozenset((col, row, repeat) for row, col, repeat in forward) == target:
                assert lhs[data['left']] == data['right'] and rhs[data['right']] == data['left']
                actions.append((True, lhs, rhs))
        stabilizers.append(sorted(actions))
        flip_count = sum(flip for flip, _, _ in actions)
        assert (flip_count == 0) == (board in (2, 3))
        move = {(perm, hole): tuple(sorted(mask_move[perm, mask] for mask in hole))
                for perm in perms for hole in holes}

        def key(lhs, rhs):
            orbit = []
            for flip, left_perm, right_perm in actions:
                left = tuple(sorted(all_pairs.difference(move[left_perm, lhs])))
                right = tuple(sorted(all_pairs.difference(move[right_perm, rhs])))
                orbit.append((board, right, left) if flip else (board, left, right))
            return min(orbit)

        keys = {key(lhs, rhs) for lhs, rhs in product(holes, repeat=2)}
        known = ({key(old_left, rhs) for rhs in holes} if board in (0, 5) else
                 {key(old_left, old_right)})
        all_keys |= keys
        baseline |= known
        for plan in plans['pilots']:
            if plan['board'] != board:
                continue
            left = tuple(plan['holes'])
            assert left in holes
            assert sorted(all_pairs.difference(left)) == plan['shape']
            profiles = {key(left, right) for right in holes}
            assert [(num, list(lhs), list(rhs)) for num, lhs, rhs in sorted(profiles)] == [
                tuple(item) for item in plan['right_orbits']]
            assert (plan['preserves'], plan['flips']) == (len(actions) - flip_count, flip_count)
            assert len(profiles - known) == plan['baseline_fresh']
            per_pilot[plan['pilot']] = profiles
        print('board', board, len(actions) - flip_count, flip_count, len(keys), len(known), flush=True)

    assert [(num, list(lhs), list(rhs)) for num, lhs, rhs in sorted(baseline)] == [
        tuple(key) for key in plans['known']]
    assert len(all_keys) == plans['total'] == 1213 and len(baseline) == 51
    accounted = baseline.copy()
    exhibit = []
    for plan in plans['pilots']:
        scope = per_pilot[plan['pilot']]
        new = scope - accounted
        assert len(new) == plan['incremental_if_all_earlier_pass']
        exhibit.append(dict(pilot=plan['pilot'], board=plan['board'], scope=sorted(scope),
                            baseline_overlap=sorted(scope & baseline),
                            prior_pilot_overlap=sorted((scope & accounted) - baseline),
                            incremental=sorted(new)))
        accounted |= scope
    assert len(accounted - baseline) == plans['potential_if_all_pass'] == 184
    dump('presolve-sets.json', dict(baseline=sorted(baseline), pilots=exhibit,
                                  total=len(all_keys), stabilizers=stabilizers))
    print('51 baseline, 184 prospective fresh, 1213 total', flush=True)


@lru_cache(None)
def pad_table(width):
    left_pole, right_pole = 2 * width, 2 * width + 1
    boundary_edges = [(0, width), (left_pole, right_pole)]
    boundary_edges += [(anchor, left_pole) for anchor in range(width)]
    boundary_edges += [(anchor, right_pole) for anchor in range(width, 2 * width)]
    independent = [mask for mask in range(1 << (2 * width + 2))
                   if all(not (mask >> first & mask >> second & 1) for first, second in boundary_edges)]
    return tuple(max(mask.bit_count() for mask in independent if not mask & blocked)
                 for blocked in range(1 << (2 * width)))


class Binder:
    def __init__(self, grid, left, right, mtf):
        width = len(grid)
        self.width, self.pad = width, pad_table(width)
        private = tuple((1 << row) | (1 << (width + column)) for row in range(width)
                        for column in range(width) for _copy in range(grid[row][column]))
        self.grid_size = len(private)
        self.slots = {ident: slot for ident, slot in enumerate(
            ((lhs, rhs) for lhs in left for rhs in right
             if (lhs.bit_count(), rhs.bit_count()) != (1, 1) and not lhs & rhs & 1), 1)}
        self.gate_count = len(self.slots)
        self.site_of = {gate: self.grid_size + gate - 1 for gate in self.slots}
        self.support = private + tuple(lhs | (rhs << width) for lhs, rhs in self.slots.values())
        self.edges = {ident: (first, second) for ident, (first, second) in enumerate(
            ((first, second) for second, mask in enumerate(self.support)
             for first in range(min(second, self.grid_size)) if not mask & self.support[first]),
            self.gate_count + 1)}
        self.edge_of = {endpoints: ident for ident, endpoints in self.edges.items()}
        self.variables = self.gate_count + len(self.edges)
        self.rows = {}
        self.want = Counter()

        def structural(literals, kind):
            row = tuple(sorted(literals))
            assert not mtf or (row and self.rows.get(row, {kind}) == {kind})
            self.rows.setdefault(row, set()).add(kind)
            self.want[row] += 1

        for side, shape in enumerate((left, right)):
            for mask in shape:
                lits = [gate for gate, slot in self.slots.items() if slot[side] == mask]
                singleton = mask.bit_count() == 1
                if not side or singleton:
                    structural(lits, ('left' if not side else 'right') + ('-single' if singleton else '-double'))
                for first, second in combinations(lits, 2):
                    structural((-first, -second), 'slot-mutex')
        self.mtf = {}
        if mtf:
            for row, col in product(range(width), repeat=2):
                if (row or col) and not grid[row][col]:
                    lits = tuple(gate for gate, (lhs, rhs) in self.slots.items()
                                 if lhs & 1 << row and rhs & 1 << col)
                    structural(lits, 'mtf')
                    self.mtf[row, col] = lits
        for last in range(len(self.support)):
            for first, second in combinations(range(min(last, self.grid_size)), 2):
                required = [(first, second), (first, last), (second, last)]
                if all(edge in self.edge_of for edge in required):
                    structural((-self.edge_of[edge] for edge in required), 'triangle')
        self.common = tuple(sum(1 << other for other, other_mask in enumerate(private)
                                if other != site and mask & other_mask)
                            for site, mask in enumerate(self.support))

    def extend(self, blocked, size, available):
        pad = self.pad[blocked]
        if size + pad >= 2 * self.width:
            return True
        while size + pad + available.bit_count() >= 2 * self.width:
            bit = available & -available
            available ^= bit
            site = bit.bit_length() - 1
            if self.extend(blocked | self.support[site], size + 1, available & self.common[site]):
                return True
        return False

    def verify(self, row):
        canonical = tuple(sorted(row))
        if canonical in self.rows:
            return '+'.join(sorted(self.rows[canonical]))
        assert row and len(set(row)) == len(row), ('bad row', row)
        guards = [-lit for lit in row if -lit in self.slots]
        assert len(guards) <= 1, ('not a mutex', row)
        active_edges = {lit for lit in row if lit in self.edges}
        assert len(active_edges) + len(guards) == len(row), ('unknown structural row', row)
        present = {self.site_of[gate] for gate in guards}
        sites = present | {site for edge in active_edges for site in self.edges[edge]}
        assert all(site < self.grid_size or site in present for site in sites), ('unguarded option', row)
        for first, second in combinations(sorted(sites), 2):
            assert self.support[first] & self.support[second] or self.edge_of.get((first, second)) in active_edges, (
                'missing pair edge', row)
        blocked, available = 0, (1 << self.grid_size) - 1
        for site in sites:
            blocked |= self.support[site]
            available &= self.common[site]
        assert self.extend(blocked, len(sites), available), ('inadequate padding', row)
        return ('padded', 'padded-option')[bool(guards)]

    def all_rows(self, source):
        lines = source.decode('ascii').splitlines()
        tag, kind, variables, clauses = lines[0].split()
        assert (tag, kind) == ('p', 'cnf') and int(variables) == self.variables
        assert int(clauses) == len(lines) - 1
        counts, structural, rows = Counter(), Counter(), []
        for line in lines[1:]:
            *row, end = map(int, line.split())
            assert end == 0 and all(0 < abs(lit) <= self.variables for lit in row)
            clause = tuple(row)
            label = self.verify(clause)
            if not label.startswith('padded'):
                structural[tuple(sorted(clause))] += 1
            counts[label] += 1
            rows.append(clause)
        assert structural == self.want
        return counts, rows

    def mutations(self, rows, grid):
        short_mtf = next(row[1:] for row in self.mtf.values()
                         if len(row) > 1 and tuple(sorted(row[1:])) not in self.rows)
        option = next(tuple(lit for lit in row if lit > 0) for row in rows
                      if any(-lit in self.slots for lit in row) and all(
                          lit > 0 or -lit in self.slots for lit in row)
                      and any(lit in self.edges and self.edges[lit][1] >= self.grid_size for lit in row))
        private = [(row_idx, col) for row_idx in range(self.width) for col in range(self.width)
                   for _copy in range(grid[row_idx][col])]
        first, second, third = next(indices for indices in combinations(range(self.grid_size), 3)
                                    if all(len({private[site][side] for site in indices}) == 3
                                           for side in (0, 1)))
        short_pad = tuple(self.edge_of[edge] for edge in ((first, second), (first, third), (second, third)))
        for bad, reason in ((short_mtf, 'unknown structural row'), (option, 'unguarded option'),
                            (short_pad, 'inadequate padding')):
            try:
                self.verify(bad)
            except AssertionError as err:
                assert err.args[0][0] == reason, (reason, err)
            else:
                raise AssertionError(('accepted mutation', reason, bad))
        return ['short MTF', 'unguarded option', 'inadequate padding']


def calibrate():
    import networkx as nx
    from pysat.formula import CNF
    from pysat.solvers import Solver

    boards = json.loads((SCOUT / 'grid.3.1.json').read_text())
    for order in (15, 16):
        records, shapes = [], Counter()
        for idx, data in enumerate(boards):
            grid = data['grid']
            assert sum(map(sum, grid)) == 5
            assert [sum(row) for row in grid] == [2 - (i == data['left']) for i in range(3)]
            assert [sum(col) for col in zip(*grid)] == [2 - (i == data['right']) for i in range(3)]
            for double_left in combinations(pairs(3), order - 14):
                left = double_left + (1 << data['left'],)
                right = pairs(3) + (1 << data['right'],)
                binder = Binder(grid, left, right, mtf=False)
                _, projected = binder.all_rows(generate(grid, left, right))
                cells, slots, supports, edges = support_layout(grid, left, right, full=True)
                assert len(cells) == binder.grid_size and supports == binder.support
                assert [(left[lhs], right[rhs]) for lhs, rhs in slots] == list(binder.slots.values())
                exact = CNF(from_string=generate(grid, left, right, full=True).decode())
                with Solver(name='cadical195', bootstrap_with=exact.clauses) as oracle:
                    while oracle.solve():
                        true = set(oracle.get_model())
                        gates = [gate for gate in binder.slots if gate in true]
                        sites = list(range(binder.grid_size)) + [binder.site_of[gate] for gate in gates]
                        assert len(sites) == order - 8
                        number = {site: label for label, site in enumerate(sites, 8)}
                        graph = nx.Graph()
                        graph.add_nodes_from(range(order))
                        graph.add_edges_from([(0, 1), (2, 5), *((0, anchor) for anchor in range(2, 5)),
                                              *((1, anchor) for anchor in range(5, 8))])
                        graph.add_edges_from((number[site], anchor + 2) for site in sites
                                             for anchor in range(6) if supports[site] & 1 << anchor)
                        used = gates.copy()
                        for (first, second), var in edges.items():
                            if first in number and second in number:
                                used.append(var)
                                if var in true:
                                    graph.add_edge(number[first], number[second])
                        assert not any(nx.triangles(graph).values())
                        assert all(any(graph.has_edge(lhs, rhs) for lhs, rhs in combinations(six, 2))
                                   for six in combinations(graph, 6))
                        recovered = {site: (sum(1 << (anchor - 2) for anchor in graph[number[site]] if 2 <= anchor < 5),
                                            sum(1 << (anchor - 5) for anchor in graph[number[site]] if 5 <= anchor < 8))
                                     for site in sites}
                        assert all(lhs | (rhs << 3) == supports[site] for site, (lhs, rhs) in recovered.items())
                        optional = [recovered[binder.site_of[gate]] for gate in gates]
                        assert [lhs for lhs, _ in optional].count(left[-1]) == 1
                        assert [rhs for _, rhs in optional].count(right[-1]) == 1
                        assert set(lhs for lhs, _ in optional) == set(left)
                        assert all(not (lhs.bit_count() == rhs.bit_count() == 1) for lhs, rhs in optional)
                        shapes['double/double'] += sum(lhs.bit_count() == rhs.bit_count() == 2 for lhs, rhs in optional)
                        shapes['changed-right'] += {rhs for _, rhs in optional if rhs.bit_count() == 2} != set(double_left)
                        plant = set(gates) | {ident for ident, (first, second) in binder.edges.items()
                                              if first in number and second in number
                                              and graph.has_edge(number[first], number[second])}
                        assert all(any((lit > 0) == (abs(lit) in plant) for lit in row) for row in projected)
                        records.append(nx.to_graph6_bytes(graph, header=False).strip())
                        shapes[f'grid-{idx}'] += 1
                        oracle.add_clause([-var if var in true else var for var in used])
        canonical = run([str(ROOT / 'opt/bin/labelg'), '-q'], input=b'\n'.join(records) + b'\n',
                        capture_output=True, check=True).stdout.splitlines()
        classes = set(canonical)
        known = set((SCOUT / f'ref.{order}.set').read_bytes().splitlines())
        assert classes == known and len(classes) == {15: 129, 16: 11}[order]
        assert len(records) == {15: 247, 16: 22}[order] and shapes['changed-right']
        print('one-defect', order, len(classes), 'classes', len(records), 'plants; each with both singleton incidences;',
              dict(shapes), flush=True)


def debit():
    audited = json.loads(Path('presolve-sets.json').read_text())
    known = {(board, tuple(lhs), tuple(rhs)) for board, lhs, rhs in audited['baseline']}
    accounted = known.copy()
    rows = []
    for pilot in audited['pilots']:
        folder = Path(f"p{pilot['pilot']}")
        if not (folder / 'checked').is_file():
            break
        scope = {(board, tuple(lhs), tuple(rhs)) for board, lhs, rhs in pilot['scope']}
        fresh = sorted(scope - accounted)
        assert fresh == [(board, tuple(lhs), tuple(rhs)) for board, lhs, rhs in pilot['incremental']]
        rows.append(dict(pilot=pilot['pilot'], board=pilot['board'], fresh=fresh))
        accounted |= scope
    dump('checked-union.json', dict(checked_pilots=rows, newly_checked=len(accounted - known),
                                   total_checked=len(accounted), remaining=audited['total'] - len(accounted)))


if __name__ == '__main__':
    command = sys.argv[1]
    if command in ('emit', 'audit'):
        grid, lhs, rhs = pilot_input(int(sys.argv[2]))
        if command == 'emit':
            sys.stdout.buffer.write(generate(grid, lhs, rhs))
        else:
            binder = Binder(grid, lhs, rhs, mtf=True)
            counts, clauses = binder.all_rows(Path(sys.argv[3]).read_bytes())
            assert (counts['left-single'], counts['left-double'], counts['right-single']) == (1, 8, 1)
            assert counts['mtf'] == len(binder.mtf) == sum(cell == 0 for row in grid for cell in row) - 1
            rejected = binder.mutations(clauses, grid)
            print('variables', binder.variables, 'clauses', len(clauses), dict(counts), 'rejected', rejected)
    else:
        {'orbits': verify_board_orbits, 'control': calibrate, 'debit': debit}[command]()
