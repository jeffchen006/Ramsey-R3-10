from collections import Counter
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from round19_shared import (
    BOARD, CATALOG, LEAF, MIDDLE, OLD, PAIRS, PERMS, SCOUT,
    audit_formula, bind, calibration, check_matrix, dump, generate, move_mask,
    move_shape, support_layout,
)


MATCHING = (3, 5, 6, 9, 10, 18, 20, 24)
EXPECTED = {f'matching+matching.{index}': count for index, count in
            enumerate((2942, 3072, 3553, 3901, 3790, 3867))}
R19 = OLD.parent / 'round19'


def audit():
    audit_formula('matching.cnf', MATCHING)
    coords, slots, _, edges = support_layout(BOARD, MATCHING, PAIRS)
    assert all(start < len(coords) for start, _ in edges)
    data, _, _ = check_matrix('matching.cnf', MATCHING)
    cycle = sorted(coords.index(cell) for cell in ((0, 1), (1, 2), (2, 0)))
    forged = {edges[pair] for pair in combinations(cycle, 2)}
    assert max(forged) > len(slots)
    assert not any(set(map(int, row.split()[:-1])) == forged for row in data[1:])
    with NamedTemporaryFile(mode='w', dir='.', suffix='.cnf') as temporary:
        header = data[0].split()
        header[-1] = str(int(header[-1]) + 1)
        temporary.write(' '.join(header) + '\n' + '\n'.join(data[1:]) + '\n')
        temporary.write(' '.join(map(str, (*sorted(forged), 0))) + '\n')
        temporary.flush()
        try:
            bind(temporary.name, BOARD, MATCHING, PAIRS, Counter(), weak_right=True)
        except AssertionError as error:
            assert error.args == (('no padded independent ten', sorted(forged)),)
        else:
            raise AssertionError('accepted an all-grid blocker with insufficient padding')
    print('rejected forged all-grid blocker (complete edge list but insufficient padding)', flush=True)


def legal_groups(left, right):
    groups = []
    for partner in permutations(right):
        sites = tuple(zip(left, partner))
        both = tuple(first & second for first, second in sites)
        if not any(mask & 1 for mask in both) and all(any(mask & (1 << diag) for mask in both)
                                                      for diag in range(1, 5)):
            groups.append(tuple(sorted(first | (second << 5) for first, second in sites)))
    groups.sort()
    assert len(set(groups)) == len(groups)
    return groups


def hole_shape(supports):
    first, second = sorted(set(PAIRS) - set(supports))
    assert (first | second) & 1
    return 'matching' if not first & second else 'middle' if first & second & 1 else 'leaf'


def crosswalk():
    prior = json.loads((OLD / 'coverage.json').read_text())
    round19 = json.loads((R19 / 'outstanding-if-verified.json').read_text())
    direct = {name: set() for name in CATALOG}
    for line in (OLD / 'pilot/price.jsonl').read_text().splitlines():
        record = json.loads(line)
        assert 'sat' not in record and record['rank'] not in direct[record['tag']]
        direct[record['tag']].add(record['rank'])
    assert sum(map(len, direct.values())) == 96
    staged = json.loads((OLD.parent / 'round18/reconciliation.json').read_text())
    assert not any(staged[field] for field in ('open_ids', 'open_reps', 'staged_only'))
    leaf_maps = json.loads((SCOUT / 'h8.crosswalk.json').read_text())
    actions = tuple(product((0, 1), PERMS))
    shapes = {tuple(sorted(set(PAIRS) - set(holes))) for holes in combinations(PAIRS, 2)
              if (holes[0] | holes[1]) & 1}
    unused = set(product(shapes, repeat=2))
    assert len(unused) == 900 and len(CATALOG) == 30
    coords, slots, _, _ = support_layout(BOARD, MATCHING, PAIRS)
    _, checked_slots, mtf = check_matrix('matching.cnf', MATCHING)
    assert slots == checked_slots
    slot_of = {(MATCHING[left], PAIRS[right]): ident for ident, (left, right) in enumerate(slots, 1)}
    diagonals = [{ident for (left, right), ident in slot_of.items() if left & right & (1 << diag)}
                 for diag in range(1, 5)]
    assert {tuple(sorted(row)) for row in diagonals} == mtf
    records = {}
    outstanding = {}
    matching_union = {}
    used_selectors = set()
    with Path('matching-physical.tsv').open('w') as output:
        print('scheme\trank\tround19_open\tphysical_supports\tmatching_selectors', file=output)
        for name, (_, pair) in sorted(CATALOG.items()):
            left, right = tuple(pair[0]), tuple(pair[1])
            assert name.split('.')[0].split('+') == [hole_shape(left), hole_shape(right)]
            orbit = {tuple(move_shape(pair[index ^ swap], perm) for index in (0, 1))
                     for swap, perm in actions}
            assert orbit <= unused
            unused -= orbit
            maps = {target: [(swap, perm) for swap, perm in actions
                             if move_shape(pair[swap], perm) == target]
                    for target in (LEAF, MIDDLE, MATCHING)}
            assert bool(maps[LEAF]) == (name in leaf_maps)
            if maps[LEAF]:
                shore, perm = leaf_maps[name]
                assert (shore, tuple(perm)) in maps[LEAF]
            groups = legal_groups(left, right)
            assert len(groups) == prior[name]['total']
            r17 = set(prior[name]['uncovered'])
            assert direct[name] <= r17 <= set(range(len(groups)))
            remaining = r17 - direct[name]
            if name == 'middle+middle.2':
                assert set(map(int, staged['checked'])) == set(range(len(groups)))
            if maps[LEAF] or maps[MIDDLE]:
                remaining.clear()
            if remaining:
                outstanding[name] = sorted(remaining)
            if not maps[MATCHING]:
                assert not remaining
                continue
            swap, perm = maps[MATCHING][0]
            transform_grid = lambda row, col: (perm[col], perm[row]) if swap else (perm[row], perm[col])
            assert perm[0] == 0 and transform_grid(0, 0) == (0, 0)
            assert {transform_grid(row, col) for row, col in coords} == set(coords)
            assert {transform_grid(diag, diag) for diag in range(1, 5)} == {(diag, diag) for diag in range(1, 5)}
            move = {mask: move_mask(mask, perm) for mask in PAIRS}
            right_target = set(move_shape(pair[1 - swap], perm))
            assert right_target <= set(PAIRS)
            assert move_shape(pair[swap], perm) == MATCHING
            for rank, group in enumerate(groups):
                raw = tuple((support & 31, support >> 5) for support in group)
                pairs = tuple((move[site[swap]], move[site[1 - swap]]) for site in raw)
                assert {first for first, _ in pairs} == set(MATCHING)
                assert {second for _, second in pairs} == right_target
                assert all(not first & second & 1 for first, second in pairs)
                selected = tuple(sorted(slot_of[site] for site in pairs))
                assert len(set(selected)) == 8 and selected not in used_selectors
                used_selectors.add(selected)
                assert all(row.intersection(selected) for row in diagonals)
                print(name, rank, int(rank in remaining), ','.join(map(str, group)),
                      ','.join(map(str, selected)), sep='\t', file=output)
            matching_union[name] = list(range(len(groups)))
            records[name] = {'orientations': len(maps[MATCHING]), 'swap': swap, 'perm': perm,
                             'total': len(groups), 'fresh': len(remaining),
                             'overlap': len(groups) - len(remaining)}
    assert not unused
    assert outstanding == round19 and {name: len(ranks) for name, ranks in outstanding.items()} == EXPECTED
    coverage = {name: sorted(set(ranks).intersection(matching_union[name])) for name, ranks in outstanding.items()}
    residual = {name: sorted(set(ranks) - set(coverage[name])) for name, ranks in outstanding.items()
                if set(ranks) - set(coverage[name])}
    assert coverage == outstanding and not residual
    dump('matching-crosswalk.json', records)
    dump('matching-debit-if-verified.json', coverage)
    dump('outstanding-if-verified.json', residual)
    print('matching union', {field: sum(record[field] for record in records.values())
                             for field in ('total', 'fresh', 'overlap')}, 'schemes', len(records), flush=True)


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'emit':
        sys.stdout.buffer.write(generate(BOARD, MATCHING, PAIRS))
    else:
        {'control': calibration, 'audit': audit, 'crosswalk': crosswalk}[command]()
