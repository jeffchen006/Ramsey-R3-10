"""Bounded calibration and a four-row frozen channel audit; no SAT calls."""

from itertools import combinations
import json
from pathlib import Path
import sys


def held(row, positive):
    return any((literal > 0) == (abs(literal) in positive) for literal in row)


def graph6(text):
    order = ord(text[0]) - 63
    assert 0 < order < 63
    bits = ''.join(f'{ord(char) - 63:06b}' for char in text[1:])
    endpoint_order = [(first, second) for second in range(order) for first in range(second)]
    assert len(bits) >= len(endpoint_order) and '1' not in bits[len(endpoint_order):]
    return order, {pair for pair, indicator in zip(endpoint_order, bits) if indicator == '1'}


def independent(sites, edges):
    return all(pair not in edges for pair in combinations(sorted(sites), 2))


def exact_small_calibration():
    vertices = range(13)
    pairs = list(combinations(vertices, 2))
    edges = {pair for pair in pairs if (pair[1] - pair[0]) % 13 in (1, 5, 8, 12)}
    adjacent = {site: {other for other in vertices if tuple(sorted((site, other))) in edges}
                for site in vertices}
    assert all(not (adjacent[first] & adjacent[second]) for first, second in edges)
    tiny = sum(independent(subset, edges) for subset in combinations(vertices, 4))
    assert tiny and not any(independent(subset, edges) for subset in combinations(vertices, 5))
    left_guard, right_guard = 1, 2
    activity = [set(), {left_guard}, {right_guard}, {left_guard, right_guard}]
    variable = {pair: index for index, pair in enumerate(pairs, 3)}
    selected_projections, dropped_occurrences = 0, 0
    fails_missing_pair = 0
    for sites in combinations(vertices, 5):
        pairs_here = tuple(combinations(sites, 2))
        guards = [-left_guard, -right_guard]
        keep = {pair for pair in pairs_here if not adjacent[pair[0]] & adjacent[pair[1]]}
        projected = {variable[pair] for pair in pairs_here if pair in edges}
        full = guards + [variable[pair] for pair in pairs_here]
        compact = guards + [variable[pair] for pair in sorted(keep)]
        for enabled in activity:
            valuation = enabled | projected
            assert held(full, valuation) and held(compact, valuation)
            selected_projections += 1
        dropped_occurrences += len(full) - len(compact)
        if len(projected) == 1:
            sole = next(iter(projected))
            assert not held([literal for literal in compact if literal != sole], activity[-1] | projected)
            fails_missing_pair += 1
    assert fails_missing_pair
    print(f'C13: alpha=4, independent fours={tiny}, valuation rows={selected_projections}, '
          f'false edge occurrences removed={dropped_occurrences}, missing true pair fails={fails_missing_pair}')


def graph_controls(controls):
    for name, fixture in controls.items():
        order, edges = graph6(fixture['plant']['graph'])
        assert order == 17 and fixture['alpha'] == 6
        assert any(independent(sites, edges) for sites in combinations(range(order), 6))
        assert not any(independent(sites, edges) for sites in combinations(range(order), 7))
        if name == 'short_padding':
            assert len(fixture['positions']) == 6 and independent(fixture['positions'], edges)
            values = {-guard for guard in fixture['guards']}
            assert not held(fixture['compact'], values)
        elif name == 'missing_option_edge':
            assert len(fixture['positions']) == 7
            physical = set(combinations(sorted(fixture['positions']), 2)) & edges
            assert len(physical) == 1
            sole = fixture['omitted_literal']
            assert [pair['positions'] for pair in fixture['pairs'] if pair['left'] == sole] == [list(next(iter(physical)))]
            values = {-guard for guard in fixture['guards']} | {sole}
            assert held(fixture['compact'], values) and not held(fixture['mutant'], values)
        else:
            assert name == 'missing_guard' and fixture['position_index'] == 'counterfactual list, not plant graph6'
            repair_order, repair_edges = graph6(fixture['positive_completion_graph'])
            assert repair_order == order
            assert not any(independent(sites, repair_edges) for sites in combinations(range(order), 7))
            disabled = fixture['omitted_guard']
            enabled = {-guard for guard in fixture['guards'] if guard != disabled} | {
                pair['left'] for pair in fixture['pairs'] if pair['left_value']}
            assert disabled < 0 and held(fixture['compact'], enabled) and not held(fixture['mutant'], enabled)
            assert held(fixture['compact'], {-guard for guard in fixture['guards']} |
                        set(fixture['completion_satisfying_edges']))
    print('width-three plants: three alpha=6 controls; short row, dropped pair, and dropped guard mutations detected')


def channel_receipts(artifact, source):
    reports = {obj['board']: obj for obj in map(json.loads, (source / 'final-model.jsonl').read_text().splitlines())}
    total_rows, channel_occurrences = 0, 0
    for target in artifact['targets']:
        board = target['board']
        order, edges = graph6(reports[board]['graph'])
        assert order == 40 and len(edges) == target['physical_edges']
        folder = source / 'work' / f'b{board:03d}'
        assert (folder / 'solve.status').read_text().strip() == '10'
        with (folder / 'grid.cnf').open() as formula:
            problem, kind, num_vars, num_rows = next(formula).split()
            assert (problem, kind) == ('p', 'cnf')
            raw_rows = [list(map(int, raw.split())) for raw in formula]
        assert int(num_rows) == len(raw_rows) == target['checked_cnf_rows']
        assert all(row[-1] == 0 and all(0 < abs(lit) <= int(num_vars) for lit in row[:-1]) for row in raw_rows)
        clauses = {tuple(sorted(row[:-1])) for row in raw_rows}
        positive = {word for raw in (folder / 'solve.log').read_text().splitlines() if raw.startswith('v ')
                    for word in map(int, raw.split()[1:]) if word > 0}
        assert all(held(row[:-1], positive) for row in raw_rows)
        for key in ('witness', 'repeated_witness'):
            fixture = target[key]
            positions, sites, guards = fixture['positions'], fixture['sites'], fixture['guards']
            assert len(positions) == len(set(positions)) == len(sites) == 10 and independent(positions, edges)
            assert len({tuple(site) if isinstance(site, list) else site for site in sites}) == 10
            assert all(len({site[side] for site in sites if isinstance(site, list)}) ==
                       sum(isinstance(site, list) for site in sites) for side in (0, 1))
            assert [tuple(pair['positions']) for pair in fixture['pairs']] == list(combinations(positions, 2))
            assert all(guard < 0 and -guard in positive for guard in guards)
            full, compact = list(guards), list(guards)
            for pair in fixture['pairs']:
                left, right = pair['left'], pair['right']
                assert pair['left_value'] == (left in positive) == 0
                assert pair['right_value'] == (right in positive) == 0
                if left:
                    full.append(left)
                if pair['kind'] == 'free':
                    assert left and right
                    compact.append(left)
                elif left:
                    assert pair['kind'] == 'common-anchor-nonedge' and right == 0
                    row = pair['conditional_false_row']
                    assert -left in row and all(lit < 0 and (lit == -left or lit in guards) for lit in row)
                    assert tuple(sorted(row)) in clauses
                    channel_occurrences += 1
            assert sorted(full) == fixture['full'] and sorted(compact) == fixture['compact']
            if key == 'witness':
                assert sorted(reports[board]['exact_block']) == sorted(full)
            assert not held(full, positive) and not held(compact, positive)
            total_rows += 1
            print(f'b{board} {key}: size=10, full={len(full)}, compact={len(compact)}, guards={len(guards)}')
    assert total_rows == 4 and channel_occurrences == 21
    print(f'Four rows match literal physical pairs; {channel_occurrences} omission-to-base-clause bindings')


if __name__ == '__main__':
    directory = Path(sys.argv[1])
    data = json.loads((directory / 'physical.v2.json').read_text())
    assert data['schema'] == 'h5.physical-blocker.v1'
    exact_small_calibration()
    graph_controls(data['controls'])
    channel_receipts(data, directory / 'h5-source')
