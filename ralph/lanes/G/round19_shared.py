from collections import Counter
from itertools import combinations, permutations, product
import json
from pathlib import Path
from subprocess import run
import sys
from tempfile import NamedTemporaryFile


ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT / 'scratch/ideas/r018_N'
OLD = ROOT / 'scratch/G/round17'
sys.path.insert(0, str(SCOUT))
from bind import bind


PAIRS = tuple((1 << first) | (1 << second) for first, second in combinations(range(5), 2))
CATALOG = json.loads((SCOUT.parent / 'r015_N/schemes.json').read_text())
MIDDLE = tuple(CATALOG['middle+middle.2'][1][0])
LEAF = tuple(CATALOG['leaf+matching.0'][1][0])
PERMS = tuple((0,) + tail for tail in permutations(range(1, 5)))
BOARD = tuple(tuple(int(row != col) for col in range(5)) for row in range(5))


def dump(file, value):
    Path(file).write_text(json.dumps(value, indent=1, sort_keys=True) + '\n')


def move_mask(mask, perm):
    return sum(1 << perm[pos] for pos in range(len(perm)) if mask & (1 << pos))


def move_shape(shape, perm):
    return tuple(sorted(move_mask(mask, perm) for mask in shape))


def support_layout(matrix, left, right, full=False):
    width = len(matrix)
    coords = tuple((row, col) for row in range(width) for col in range(width)
                   for _ in range(matrix[row][col]))
    slots = tuple((lidx, ridx) for lidx, lhs in enumerate(left) for ridx, rhs in enumerate(right)
                  if not (lhs & rhs & 1) and lhs.bit_count() + rhs.bit_count() >= 3)
    left_right = tuple((1 << row, 1 << col) for row, col in coords) + tuple(
        (left[lidx], right[ridx]) for lidx, ridx in slots)
    supports = tuple(lhs | (rhs << width) for lhs, rhs in left_right)
    edges = {}
    for end in range(len(supports)):
        for start in range(end if full else min(end, len(coords))):
            if not supports[start] & supports[end]:
                edges[start, end] = len(slots) + len(edges) + 1
    return coords, slots, supports, edges


def generate(matrix, left, right, full=False):
    cmd = ['./ghost', str(len(matrix)), '6', '6' if full else '1', '33' if full else '32',
           ','.join(map(str, left)), ','.join(map(str, right)), '0',
           ''.join(str(cell) for row in matrix for cell in row)]
    return run(cmd, check=True, capture_output=True).stdout


def calibration():
    import networkx as nx
    from pysat.formula import CNF
    from pysat.solvers import Solver

    aligned = {'grid': [[int(row != col) for col in range(3)] for row in range(3)]}
    defects = json.loads((SCOUT / 'grid.3.1.json').read_text())
    for order, defect in product((15, 16), (False, True)):
        records = []
        counts = Counter()
        for data in defects if defect else [aligned]:
            matrix = data['grid']
            for shape in combinations((3, 5, 6), order - 14):
                left = shape + ((1 << data['left'],) if defect else ())
                right = (3, 5, 6) + ((1 << data['right'],) if defect else ())
                grid, slots, supports, edges = support_layout(matrix, left, right, True)
                _, _, _, projected_edges = support_layout(matrix, left, right)
                exact = CNF(from_string=generate(matrix, left, right, True).decode())
                projected = CNF(from_string=generate(matrix, left, right).decode())
                with Solver(name='cadical195', bootstrap_with=exact.clauses) as oracle:
                    while oracle.solve():
                        true = set(oracle.get_model())
                        gates = sorted(gate for gate in range(1, len(slots) + 1) if gate in true)
                        indices = list(range(len(grid))) + [len(grid) + gate - 1 for gate in gates]
                        labels = {site: index + 8 for index, site in enumerate(indices)}
                        assert len(indices) == order - 8
                        graph = nx.Graph()
                        graph.add_nodes_from(range(order))
                        graph.add_edges_from([(0, 1), (2, 5)] + [(0, vertex) for vertex in range(2, 5)]
                                             + [(1, vertex) for vertex in range(5, 8)])
                        used = list(gates)
                        for site in indices:
                            graph.add_edges_from((labels[site], 2 + anchor) for anchor in range(6)
                                                 if supports[site] & 1 << anchor)
                        for (start, end), var in edges.items():
                            if start in labels and end in labels:
                                used.append(var)
                                if var in true:
                                    graph.add_edge(labels[start], labels[end])
                        assert not any(nx.triangles(graph).values())
                        assert not any(not any(graph.has_edge(*edge) for edge in combinations(sites, 2))
                                       for sites in combinations(graph, 6))
                        recovered = {vertex: sum(1 << (anchor - 2) for anchor in graph[vertex]
                                                 if 2 <= anchor < 8) for vertex in range(8, order)}
                        assert all(recovered[labels[site]] == supports[site] for site in indices)
                        plant = set(gates) | {var for (start, end), var in projected_edges.items()
                                              if start in labels and end in labels
                                              and graph.has_edge(labels[start], labels[end])}
                        assert all(any((lit > 0) == (abs(lit) in plant) for lit in row)
                                   for row in projected.clauses)
                        used_pairs = {right[slots[gate - 1][1]] for gate in gates
                                      if right[slots[gate - 1][1]].bit_count() == 2}
                        counts['plants'] += 1
                        counts['changed_right'] += used_pairs != set(shape)
                        records.append(nx.to_graph6_bytes(graph, header=False).strip())
                        oracle.add_clause([-var if var in true else var for var in used])
        raw = b'\n'.join(records) + (b'\n' if records else b'')
        actual = set(run([str(ROOT / 'opt/bin/labelg'), '-q'], input=raw,
                         capture_output=True, check=True).stdout.splitlines())
        ref = (SCOUT / f'ref.{order}.set' if defect else
               ROOT / f'scratch/G/round16/small.{order}.scan.set')
        assert actual == set(ref.read_bytes().splitlines())
        if actual:
            assert counts['changed_right'] > 0
        print('control', order, 'one-defect' if defect else 'aligned', len(actual), dict(counts), flush=True)


def check_matrix(formula, left):
    coords, slots, _, _ = support_layout(BOARD, left, PAIRS)
    expected_slots = {tuple(ident for ident, pair in enumerate(slots, 1) if pair[0] == idx)
                      for idx in range(8)}
    expected_mtf = {tuple(ident for ident, (lidx, ridx) in enumerate(slots, 1)
                          if left[lidx] & (1 << diag) and PAIRS[ridx] & (1 << diag))
                    for diag in range(1, 5)}
    expected_mutex = {(-first, -second) for (first, lhs), (second, rhs) in
                      combinations(enumerate(slots, 1), 2) if lhs[0] == rhs[0] or lhs[1] == rhs[1]}
    data = Path(formula).read_text().splitlines()
    rows = [tuple(map(int, line.split()[:-1])) for line in data[1:]]
    positive = [tuple(sorted(row)) for row in rows if all(1 <= lit <= len(slots) for lit in row)]
    binary = [tuple(sorted(row, reverse=True)) for row in rows if len(row) == 2 and
              all(1 <= -lit <= len(slots) for lit in row)]
    assert len(coords) == 20 and len(expected_slots) == 8 and len(expected_mtf) == 4
    assert not expected_slots & expected_mtf
    assert Counter(positive) == Counter(expected_slots | expected_mtf)
    assert Counter(binary) == Counter(expected_mutex)
    return data, slots, expected_mtf


def audit_formula(formula, left):
    data, slots, mtf = check_matrix(formula, left)
    counts = bind(formula, BOARD, left, PAIRS, Counter(), weak_right=True, adverse=True)
    rows = [tuple(map(int, line.split()[:-1])) for line in data[1:]]
    guard = next(row for row in rows if len(row) >= 3 and -len(slots) <= row[0] < 0
                 and all(lit > len(slots) for lit in row[1:]))
    distinct = next((-first, -second) for (first, lhs), (second, rhs) in
                    combinations(enumerate(slots, 1), 2) if lhs[0] != rhs[0] and lhs[1] != rhs[1])
    altered = [guard[1:], distinct, min(mtf)[1:]]
    assert not set(altered) & set(rows)
    for fake in altered:
        with NamedTemporaryFile(mode='w', dir='.', suffix='.cnf') as temporary:
            temporary.write(' '.join(data[0].split()[:-1] + [str(len(rows) + 1)]) + '\n')
            temporary.write('\n'.join(data[1:]) + '\n')
            temporary.write(' '.join(map(str, (*fake, 0))) + '\n')
            temporary.flush()
            try:
                bind(temporary.name, BOARD, left, PAIRS, Counter(), weak_right=True)
            except AssertionError:
                pass
            else:
                raise AssertionError(('accepted forged row', fake))
    print(formula, dict(counts), 'rejected unit, unguarded optional, fake mutex, shrunk MTF', flush=True)


def crosswalk():
    prior = json.loads((OLD / 'coverage.json').read_text())
    direct = {name: set() for name in CATALOG}
    for line in (OLD / 'pilot/price.jsonl').read_text().splitlines():
        row = json.loads(line)
        assert 'sat' not in row and row['rank'] not in direct[row['tag']]
        direct[row['tag']].add(row['rank'])
    assert sum(map(len, direct.values())) == 96
    scheme2 = 'middle+middle.2'
    reconciliation = json.loads((OLD.parent / 'round18/reconciliation.json').read_text())
    assert not reconciliation['open_ids'] and not reconciliation['open_reps'] and not reconciliation['staged_only']
    restored = set(map(int, reconciliation['checked']))
    assert restored == set(range(16350))
    leaf_moves = json.loads((SCOUT / 'h8.crosswalk.json').read_text())
    _, slots, mtf = check_matrix('middle.cnf', MIDDLE)
    _, leaf_slots, leaf_mtf = check_matrix(SCOUT / 'broad.8.cnf', LEAF)
    middle_gates = {(MIDDLE[lidx], PAIRS[ridx]): number for number, (lidx, ridx) in enumerate(slots, 1)}
    leaf_gates = {(LEAF[lidx], PAIRS[ridx]): number for number, (lidx, ridx) in enumerate(leaf_slots, 1)}
    all_shape = {tuple(sorted(set(PAIRS) - set(holes))) for holes in combinations(PAIRS, 2)
                 if (holes[0] | holes[1]) & 1}
    remaining_shapes = set(product(all_shape, repeat=2))
    inventory = {}
    with Path('physical.tsv').open('w') as table:
        print('scheme\trank\tr17_open\tr18_owner\tmiddle_gates\tleaf_gates', file=table)
        for name, (_, sides) in sorted(CATALOG.items()):
            orbit = {tuple(move_shape(sides[idx ^ shore], perm) for idx in range(2))
                     for shore, perm in product(range(2), PERMS)}
            assert orbit <= remaining_shapes
            remaining_shapes -= orbit
            maps = {label: [(shore, perm) for shore, perm in product(range(2), PERMS)
                            if move_shape(sides[shore], perm) == target]
                    for label, target in [('leaf', LEAF), ('middle', MIDDLE)]}
            assert bool(maps['leaf']) == (name in leaf_moves)
            if maps['leaf']:
                assert tuple([leaf_moves[name][0], tuple(leaf_moves[name][1])]) in maps['leaf']
                maps['leaf'] = [tuple([leaf_moves[name][0], tuple(leaf_moves[name][1])])]
            lhs, rhs = tuple(sides[0]), tuple(sides[1])
            groups = []
            for pairing in permutations(rhs):
                if any(first & second & 1 for first, second in zip(lhs, pairing)):
                    continue
                cover = 0
                for first, second in zip(lhs, pairing):
                    cover |= first & second
                if cover == 30:
                    groups.append(tuple(sorted(first | (second << 5) for first, second in zip(lhs, pairing))))
            groups.sort()
            assert len(set(groups)) == len(groups) == prior[name]['total']
            old_open = set(prior[name]['uncovered'])
            assert old_open <= set(range(len(groups))) and direct[name] <= old_open
            r17_open = old_open - direct[name]
            owner = 'middle.2' if name == scheme2 else 'leaf' if maps['leaf'] else 'open'
            if owner == 'middle.2':
                assert not maps['leaf'] and restored == set(range(len(groups)))
            seen = {'middle': set(), 'leaf': set()}
            shadows = {}
            for label, (target, gates, required) in {'middle': (MIDDLE, middle_gates, mtf),
                                                      'leaf': (LEAF, leaf_gates, leaf_mtf)}.items():
                if not maps[label]:
                    continue
                shore, perm = maps[label][0]
                mapped_grid = {(perm[col], perm[row]) if shore else (perm[row], perm[col])
                               for row in range(5) for col in range(5) if BOARD[row][col]}
                assert perm[0] == 0 and mapped_grid == {(row, col) for row in range(5) for col in range(5)
                                                          if BOARD[row][col]}
                mapped = {mask: move_mask(mask, perm) for mask in PAIRS}
                r_shape = set(move_shape(sides[1 - shore], perm))
                assert move_shape(sides[shore], perm) == target and r_shape <= set(PAIRS)
                shadows[label] = shore, mapped, r_shape, gates, tuple(map(set, required)), target
            for rank, group in enumerate(groups):
                present = {}
                for label, (shore, mapped, r_shape, gates, required, target) in shadows.items():
                    raw = [(mask & 31, mask >> 5) for mask in group]
                    matches = [(mapped[pair[shore]], mapped[pair[1 - shore]]) for pair in raw]
                    ids = tuple(sorted(gates[pair] for pair in matches))
                    assert {first for first, _ in matches} == set(target)
                    assert {second for _, second in matches} == r_shape
                    assert len(ids) == 8 and ids not in seen[label]
                    seen[label].add(ids)
                    assert all(requirement.intersection(ids) for requirement in required)
                    present[label] = ','.join(map(str, ids))
                print(name, rank, int(rank in r17_open), owner,
                      present.get('middle', '-'), present.get('leaf', '-'), sep='\t', file=table)
            inventory[name] = dict(total=len(groups), r17=len(r17_open), prior_owner=owner,
                                   middle_map=maps['middle'][0] if maps['middle'] else None,
                                   leaf_map=maps['leaf'][0] if maps['leaf'] else None,
                                   fresh_middle=len(r17_open) if owner == 'open' and maps['middle'] else 0,
                                   residual_ids=sorted(r17_open) if owner == 'open' else [])
    assert not remaining_shapes
    count = lambda field: sum(row[field] for row in inventory.values())
    assert count('total') == 169635 and count('r17') == 155746
    assert sum(row['r17'] for row in inventory.values() if row['prior_owner'] == 'leaf') == 60990
    assert inventory[scheme2]['r17'] == 15684
    assert sum(len(row['residual_ids']) for row in inventory.values()) == 79072
    assert count('fresh_middle') == 57947
    remainder = {name: row['residual_ids'] for name, row in inventory.items()
                 if row['residual_ids'] and not row['middle_map']}
    assert sum(map(len, remainder.values())) == 21125
    dump('crosswalk.json', inventory)
    dump('outstanding-if-verified.json', remainder)
    print('middle schemes overlap/fresh/remaining:',
          {name: (row['prior_owner'], row['total'], row['r17'], row['fresh_middle'], row['middle_map'])
           for name, row in inventory.items() if row['middle_map']}, flush=True)
    print('remaining if verified:', {name: len(ids) for name, ids in remainder.items()}, flush=True)


def preregister():
    shapes = sorted(tuple(sorted(set(PAIRS) - set(holes))) for holes in combinations(PAIRS, 2)
                    if (holes[0] | holes[1]) & 1)
    boards = json.loads((SCOUT / 'grid.5.1.json').read_text())
    cold = tuple(CATALOG['leaf+matching.0'][1][1])
    inventory = []
    initial = set()
    potential = set()
    for number, data in enumerate(boards):
        grid = tuple(map(tuple, data['grid']))
        actions = []
        for swap, lhs, rhs in product(range(2), PERMS, PERMS):
            if all(grid[row][col] == (grid[rhs[col]][lhs[row]] if swap else grid[lhs[row]][rhs[col]])
                   for row, col in product(range(5), repeat=2)):
                actions.append((swap, lhs, rhs))
        one = {min(move_shape(shape, lhs) for swap, lhs, _ in actions if not swap) for shape in shapes}
        assert sorted(one) == [tuple(shape) for shape in json.loads((SCOUT / f'left.7.{number}.json').read_text())]
        transform = {(shape, perm): move_shape(shape, perm) for shape, perm in product(shapes, PERMS)}
        classes = {}
        for pair in product(shapes, repeat=2):
            images = []
            for swap, lhs, rhs in actions:
                image = transform[pair[0], lhs], transform[pair[1], rhs]
                images.append(image[::-1] if swap else image)
            classes[pair] = (number, *min(images))
        known = ({classes[LEAF, right] for right in shapes} if number in (0, 5) else
                 {classes[LEAF, cold]})
        assert classes[LEAF, cold] in known
        initial |= known
        potential |= set(classes.values())
        by_left = {shape: {classes[shape, rhs] for rhs in shapes} for shape in sorted(one)}
        assert set().union(*by_left.values()) == set(classes.values())
        inventory.append((data, actions, by_left))
        print('h7 board', number, 'preserve/flip', Counter(swap for swap, _, _ in actions),
              'fixed-left', len(one), 'two-sided', len(set(classes.values())), 'checked', len(known))
    assert sum(len(group) for _, _, group in inventory) == 81
    assert len(potential) == 1213 and len(initial) == 51
    selected = {}
    credited = initial.copy()
    plan = []
    for pilot, (board, quantile) in enumerate(((0, 0.), (1, .5), (2, 1.), (3, 0.), (4, .5), (5, 1.),
                                               (2, 0.), (5, .5)), 1):
        data, actions, contexts = inventory[board]
        options = [shape for shape, right in contexts.items() if (board, shape) not in selected
                   and right - credited]
        assert options
        left = options[round((len(options) - 1) * quantile)]
        selected[board, left] = True
        scope = contexts[left]
        fresh = scope - credited
        first_fresh = scope - initial
        credited.update(fresh)
        restore = sorted(set(PAIRS) - set(left))
        plan.append(dict(pilot=pilot, board=board, shape=left, holes=restore, singleton=1 << data['left'],
                         tested_initially=False, preserves=sum(not swap for swap, _, _ in actions),
                         flips=sum(swap for swap, _, _ in actions), quantile=quantile,
                         right_orbits=sorted(scope), baseline_fresh=len(first_fresh),
                         incremental_if_all_earlier_pass=len(fresh)))
    dump('h7-prereg.json', dict(known=sorted(initial), total=len(potential), pilots=plan,
                               potential_if_all_pass=len(credited - initial)))
    print('h7 pilots (potential only):', [(row['board'], row['holes'], len(row['right_orbits']),
                                             row['baseline_fresh'], row['incremental_if_all_earlier_pass'])
                                            for row in plan], 'fresh union', len(credited - initial), flush=True)


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'emit':
        sys.stdout.buffer.write(generate(BOARD, MIDDLE, PAIRS))
    else:
        {'control': calibration, 'audit': lambda: audit_formula('middle.cnf', MIDDLE),
         'leaf': lambda: audit_formula(SCOUT / 'broad.8.cnf', LEAF),
         'crosswalk': crosswalk, 'preregister': preregister}[command]()
