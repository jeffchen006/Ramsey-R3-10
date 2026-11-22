"""Independent witness oracle for the folded h=5 physical site projection."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
H5 = ROOT / 'scratch/A/r23/h5-source'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
from check_graph import alpha, parse_graph6, to_graph6, triangle_free


class Layout:
    def __init__(self, board):
        width = self.width = len(board)
        self.boundary = 2 + 2 * width
        axis = range(width)
        self.grid = [(1 << left, 1 << right) for left, right in product(axis, repeat=2)
                     for _ in range(board[left][right])]
        doubles = [(1 << left) + (1 << right) for left, right in combinations(axis, 2)]
        margins = (list(map(sum, board)), list(map(sum, zip(*board))))
        self.slots = [doubles + [1 << anchor for anchor in axis for _ in range(width - 1 - margin[anchor])]
                      for margin in margins]
        assert all(len(shore) == len(doubles) + 3 for shore in self.slots)
        number = sum(map(len, self.slots))
        self.gates = {}
        for left, right in product(range(len(self.slots[0])), range(len(self.slots[1]))):
            lhs, rhs = self.slots[0][left], self.slots[1][right]
            if not (lhs & rhs & 1) and lhs.bit_count() + rhs.bit_count() >= 3:
                number += 1
                self.gates[left, right] = number
        self.edges = [{}, {}]
        for side in (0, 1):
            size = len(self.grid)
            coords = [pair[side] for pair in self.grid] + self.slots[side]
            for first, second in combinations(range(len(coords)), 2):
                if second < size:
                    if any(mask & other for mask, other in zip(self.grid[first], self.grid[second])):
                        continue
                    if side == 1:
                        self.edges[side][first, second] = self.edges[0][first, second]
                        continue
                elif coords[first] & coords[second]:
                    continue
                number += 1
                self.edges[side][first, second] = number
        self.variables = number

    def sites(self, selected):
        assert len({left for left, _ in selected}) == len({right for _, right in selected}) == len(selected)
        size = len(self.grid)
        return list(range(self.boundary)) + [(index, index) for index in range(size)] + [
            (size + left, size + right) for left, right in sorted(selected)]

    def mask(self, site, side):
        coord = site[side]
        return self.grid[coord][side] if coord < len(self.grid) else self.slots[side][coord - len(self.grid)]

    def gate(self, site):
        if isinstance(site, tuple) and site[0] >= len(self.grid):
            return self.gates[tuple(coord - len(self.grid) for coord in site)]
        return 0

    def pair(self, first, second):
        if isinstance(first, int) and isinstance(second, int):
            width = self.width
            fixed = (first, second) in [(0, 1), (2, 2 + width)] + [
                (side, 2 + side * width + anchor) for side in (0, 1) for anchor in range(width)]
            return ('boundary-edge' if fixed else 'boundary-nonedge', 0, 0)
        if isinstance(first, int):
            if first in (0, 1):
                return 'root-exterior-nonedge', 0, 0
            side, anchor = divmod(first - 2, self.width)
            return ('contact-edge' if self.mask(second, side) & (1 << anchor) else 'contact-nonedge', 0, 0)
        left, right = (self.edges[side].get(tuple(sorted((first[side], second[side]))), 0) for side in (0, 1))
        common = [self.mask(first, side) & self.mask(second, side) for side in (0, 1)]
        if any(common):
            return 'common-anchor-nonedge', left, right
        assert left and right
        return 'free', left, right

    def blocker(self, sites):
        boundary = [site for site in sites if isinstance(site, int)]
        exterior = [site for site in sites if isinstance(site, tuple)]
        assert len(boundary) == len(set(boundary))
        assert all(len({site[side] for site in exterior}) == len(exterior) for side in (0, 1))
        guards = [-self.gate(site) for site in sites if self.gate(site)]
        pairs = [self.pair(first, second) for first, second in combinations(sites, 2)]
        if any(kind in ('boundary-edge', 'contact-edge') for kind, *_ in pairs):
            return None
        full = sorted(guards + [left for _, left, _ in pairs if left])
        compact = sorted(guards + [left for kind, left, _ in pairs if kind == 'free'])
        assert len(full) == len(set(full)) and len(compact) == len(set(compact))
        return dict(guards=sorted(guards), full=full, compact=compact)

    def decode(self, sites, positive):
        adj = [0] * len(sites)
        for first, second in combinations(range(len(adj)), 2):
            kind, left, right = self.pair(sites[first], sites[second])
            if kind == 'free':
                assert (left in positive) == (right in positive)
            elif kind == 'common-anchor-nonedge':
                assert left not in positive and right not in positive
            if kind in ('boundary-edge', 'contact-edge') or left in positive:
                adj[first] |= 1 << second
                adj[second] |= 1 << first
        for side in (0, 1):
            active = {site[side] for site in sites if isinstance(site, tuple)}
            assert all(one in active and two in active for (one, two), lit in self.edges[side].items() if lit in positive)
        return adj


def find_independent(adj, vertices, count):
    if count == 0:
        return ()
    while vertices.bit_count() >= count:
        low = vertices & -vertices
        vertices ^= low
        vertex = low.bit_length() - 1
        rest = find_independent(adj, vertices & ~adj[vertex], count - 1)
        if rest is not None:
            return (vertex, *rest)
    return None


def with_required(adj, required, exclude, count):
    available = ((1 << len(adj)) - 1) ^ sum(1 << vertex for vertex in exclude)
    for vertex in required:
        available &= ~(adj[vertex] | (1 << vertex))
    rest = find_independent(adj, available, count - len(required))
    return None if rest is None else tuple(sorted((*rest, *required)))


def true_clause(clause, positive):
    return any((literal > 0) == (abs(literal) in positive) for literal in clause)


def physical_fixture(layout, sites, positions, positive):
    named = [sites[position] for position in positions]
    blocker = layout.blocker(named)
    assert blocker is not None
    pairs = []
    for first, second in combinations(range(len(named)), 2):
        kind, left, right = layout.pair(named[first], named[second])
        pairs.append(dict(positions=[positions[first], positions[second]], kind=kind, left=left, right=right,
                          left_value=int(left in positive), right_value=int(right in positive)))
    return dict(**blocker, positions=positions, sites=named, pairs=pairs)


def target(layout, ident, reported):
    folder = H5 / 'work' / f'b{ident:03d}'
    assert int((folder / 'solve.status').read_text()) == 10
    signed = [int(word) for line in (folder / 'solve.log').read_text().splitlines() if line.startswith('v ')
              for word in line.split()[1:] if word != '0']
    positive = {literal for literal in signed if literal > 0}
    with (folder / 'grid.cnf').open() as stream:
        tag, dimacs, count, rows = next(stream).split()
        assert (tag, dimacs) == ('p', 'cnf') and sorted(map(abs, signed)) == list(range(1, int(count) + 1))
        count_rows, cnf_rows = 0, set()
        for line in stream:
            row = tuple(map(int, line.split()))
            assert row[-1] == 0 and true_clause(row[:-1], positive)
            cnf_rows.add(tuple(sorted(row[:-1])))
            count_rows += 1
        assert count_rows == int(rows)
    selected = [pair for pair, literal in layout.gates.items() if literal in positive]
    sites = layout.sites(selected)
    adj = layout.decode(sites, positive)
    assert len(adj) == 40 and triangle_free(adj) and to_graph6(adj) == reported['graph']
    def check_witness(witness):
        assert len(witness) == len(set(witness)) == 10
        assert all(not (adj[first] & (1 << second)) for first, second in combinations(witness, 2))
        fixture = physical_fixture(layout, sites, witness, positive)
        for form in ('full', 'compact'):
            assert not true_clause(fixture[form], positive) and tuple(fixture[form]) not in cnf_rows
        for pair in fixture['pairs']:
            if pair['left'] and pair['kind'] == 'common-anchor-nonedge':
                assert not pair['right']
                channel = tuple(sorted([-pair['left'], *(-layout.gate(sites[position])
                                       for position in pair['positions'] if layout.gate(sites[position]))]))
                assert channel in cnf_rows
                pair['conditional_false_row'] = channel
        return fixture

    witness = reported['I10']
    fixture = check_witness(witness)
    assert fixture['full'] == reported['exact_block']
    options = [site for site in witness if layout.gate(sites[site])]
    assert len(options) == 2
    assert not any(with_required(adj, (site,), [other for other in range(len(adj))
                   if other != site and layout.gate(sites[other])], 10) is not None for site in range(len(adj))
                   if layout.gate(sites[site]))
    assert with_required(adj, (), [site for site in range(len(adj)) if layout.gate(sites[site])], 10) is None
    repeated = []
    potential = [site for site in range(len(adj)) if layout.gate(sites[site])]
    for first, second in combinations(potential, 2):
        equal = [side for side in (0, 1) if layout.mask(sites[first], side) == layout.mask(sites[second], side)]
        if not equal:
            continue
        repeated.extend(dict(first=first, second=second, side=side, mask=layout.mask(sites[first], side)) for side in equal)
    repeated_witness = next((extension for pair in repeated if (extension := with_required(
        adj, (pair['first'], pair['second']), (), 10)) is not None), None)
    assert repeated_witness is not None
    repeated_fixture = check_witness(repeated_witness)
    return dict(board=ident, selected=selected, witness=fixture, repeated_contacts=repeated,
                repeated_witness=repeated_fixture,
                equal_contacts_in_repeated_witness=[pair for pair in repeated
                                                    if {pair['first'], pair['second']} <= set(repeated_witness)],
                physical_edges=sum(mask.bit_count() for mask in adj) // 2, checked_cnf_rows=count_rows)


def toy(row):
    flat = row['board']
    layout = Layout([list(map(int, flat[start:start + 3])) for start in (0, 3, 6)])
    assert row['left'] == layout.slots[0] and row['right'] == layout.slots[1]
    selected = list(enumerate(row['mates']))
    sites = layout.sites(selected)
    adj = parse_graph6(row['graph'])
    positive = {layout.gates[pair] for pair in selected}
    for first, second in combinations(range(len(adj)), 2):
        if adj[first] & (1 << second):
            kind, left, right = layout.pair(sites[first], sites[second])
            assert kind in ('free', 'boundary-edge', 'contact-edge')
            if kind == 'free':
                positive.update((left, right))
    assert layout.decode(sites, positive) == adj
    return layout, sites, adj, positive


def guard_mutation(layout, sites, positive, completions):
    size = len(layout.grid)
    occupied = {site[0]: site for site in sites if layout.gate(site)}
    for (left, right), gate in layout.gates.items():
        if gate in positive or size + left not in occupied:
            continue
        hypothetical = (size + left, size + right)
        allowed = [site for site in sites if not layout.gate(site) or
                   (site[0] != hypothetical[0] and site[1] != hypothetical[1])]
        allowed.append(hypothetical)
        conflict = [0] * len(allowed)
        for first, second in combinations(range(len(allowed)), 2):
            kind, lhs, _ = layout.pair(allowed[first], allowed[second])
            if kind in ('boundary-edge', 'contact-edge') or lhs in positive:
                conflict[first] |= 1 << second
                conflict[second] |= 1 << first
        slot = len(allowed) - 1
        positions = with_required(conflict, (slot,), (), 7)
        if positions is None:
            continue
        fixture = physical_fixture(layout, allowed, positions, positive)
        assert [-gate] == [literal for literal in fixture['full'] if true_clause([literal], positive)]
        expected_slots = frozenset((option_left - size, option_right - size) for chosen in fixture['sites']
                                   if layout.gate(chosen) for option_left, option_right in (chosen,))
        completion = next((graph for matching, graph in completions.items() if expected_slots <= matching), None)
        if completion is None:
            continue
        mutant = [literal for literal in fixture['full'] if literal != -gate]
        assert not true_clause(mutant, positive) and not true_clause(
            [literal for literal in fixture['compact'] if literal != -gate], positive)
        return dict(**fixture, position_index='counterfactual list, not plant graph6', omitted_guard=-gate,
                    mutant=mutant, actual_site=occupied[size + left], hypothetical_site=hypothetical,
                    positive_completion_graph=completion)
    return None


def plants(rows):
    tests = {}
    completions = {}
    for row in rows:
        completions.setdefault(row['board'], {}).setdefault(frozenset(enumerate(row['mates'])), row['graph'])
    for row in rows:
        layout, sites, adj, positive = toy(row)
        assert triangle_free(adj) and alpha(adj) == 6
        if len(tests) == 3:
            continue
        if 'missing_guard' not in tests:
            if (mutation := guard_mutation(layout, sites, positive, completions[row['board']])) is not None:
                tests['missing_guard'] = dict(plant=row, alpha=6, **mutation)
        options = [site for site in range(len(adj)) if layout.gate(sites[site])]
        for first, second in combinations(options, 2):
            edge = bool(adj[first] & (1 << second))
            key = 'missing_option_edge' if edge else 'short_padding'
            if key in tests:
                continue
            excluded = () if edge else set(options) - {first, second}
            positions = with_required(adj, (first, second), excluded, 7 if edge else 6)
            if positions is None:
                continue
            receipt = physical_fixture(layout, sites, positions, positive)
            assert len(receipt['guards']) >= 2
            truths = [literal for literal in receipt['compact'] if true_clause([literal], positive)]
            assert len(truths) == int(edge)
            if edge:
                kind, left, _ = layout.pair(sites[first], sites[second])
                assert kind == 'free' and truths == [left]
                mutant = [literal for literal in receipt['compact'] if literal != left]
                assert not true_clause(mutant, positive)
                receipt.update(omitted_literal=left, mutant=mutant)
            tests[key] = dict(plant=row, alpha=6, **receipt)
    assert set(tests) == {'short_padding', 'missing_option_edge', 'missing_guard'}, set(tests)
    guarded = tests['missing_guard']
    completion = next(row for row in rows if row['board'] == guarded['plant']['board'] and
                      row['graph'] == guarded['positive_completion_graph'])
    _, _, _, completed_bits = toy(completion)
    assert all(-guard in completed_bits for guard in guarded['guards'])
    guarded['completion_satisfying_edges'] = [literal for literal in guarded['compact'] if literal in completed_bits]
    assert guarded['completion_satisfying_edges']
    return tests


def main():
    positives = [json.loads(line) for line in (H5 / 'n17.d3.placements.jsonl').open()]
    assert len(positives) == 1960 and len({plant['canonical'] for plant in positives}) == 218
    tests = plants(positives)
    manifest_text = (H5 / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_text)
    reported = {row['board']: row for row in map(json.loads, (H5 / 'final-model.jsonl').open())}
    for ident in (201, 202):
        binding = json.loads((H5 / 'work' / f'b{ident:03d}' / 'binding.json').read_text())
        assert binding['manifest'] == sha256(manifest_text).hexdigest()
        assert binding['board'] == ident and binding['grid'] == manifest[ident]['grid']
    targets = [target(Layout(manifest[ident]['grid']), ident, reported[ident]) for ident in (201, 202)]
    assert all(item['equal_contacts_in_repeated_witness'] for item in targets)
    print(json.dumps(dict(schema='h5.physical-blocker.v1', toy_plants=len(positives),
                          toy_classes=218, controls=tests, targets=targets), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
