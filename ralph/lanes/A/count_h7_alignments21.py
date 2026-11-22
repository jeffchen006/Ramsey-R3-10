"""Count fixed-slot alignments for the eight frozen h=7 comparisons."""

import argparse
import json
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path
from time import process_time


ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT / 'scratch/ideas/r018_N'
FROZEN = ROOT / 'scratch/G/round19/h7-prereg.json'
SCHEMES = ROOT / 'scratch/ideas/r015_N/schemes.json'


def load(path):
    return json.loads(path.read_text())


def board_and_slots(data, left_doubles, right_doubles, defect=True):
    matrix = tuple(map(tuple, data['grid']))
    width = len(matrix)
    assert all(len(row) == width and min(row) >= 0 for row in matrix)
    assert matrix[0][0] == 0
    slots = []
    for side, orientation, doubles in (
        ('left', matrix, left_doubles), ('right', tuple(zip(*matrix)), right_doubles)
    ):
        assert len(set(doubles)) == len(doubles)
        assert all(mask.bit_count() == 2 and 0 < mask < (1 << width) for mask in doubles)
        deficits = tuple(width - 1 - sum(row) for row in orientation)
        expected = tuple(int(defect and anchor == data[side]) for anchor in range(width))
        assert deficits == expected
        singletons = tuple(1 << anchor for anchor, deficit in enumerate(deficits) if deficit)
        slots.append(singletons + tuple(doubles))
    assert len(slots[0]) == len(slots[1])
    return matrix, *slots


@cache
def permanent(choices):
    """Number of perfect matchings when each row has these eligible columns."""
    column_limit = (1 << len(choices)) - 1
    ways = {0: 1}
    for available in choices:
        after = defaultdict(int)
        for used, count in ways.items():
            options = available & (column_limit ^ used)
            while options:
                column = options & -options
                options ^= column
                after[used | column] += count
        ways = after
        if not ways:
            return 0
    return ways.get(column_limit, 0)


def inclusion_exclusion(matrix, left, right):
    required = [(row, col) for row, entries in enumerate(matrix)
                for col, copies in enumerate(entries) if not copies and (row or col)]
    permitted = tuple(sum(1 << index for index, right_mask in enumerate(right)
                          if not left_mask & right_mask & 1
                          and (left_mask.bit_count() == 2 or right_mask.bit_count() == 2))
                      for left_mask in left)
    covers = [tuple(sum(1 << index for index, right_mask in enumerate(right) if right_mask >> col & 1)
                    if left_mask >> row & 1 else 0 for left_mask in left)
              for row, col in required]
    subtotal = 0
    conflict_masks = {(0,) * len(left): 1}
    for covering in covers:
        updated = defaultdict(int, conflict_masks)
        for current, weight in conflict_masks.items():
            union = tuple(old | new for old, new in zip(current, covering))
            updated[union] -= weight
        conflict_masks = {mask: weight for mask, weight in updated.items() if weight}
    for forbidden, weight in conflict_masks.items():
        remaining = tuple(sorted((ok & ~bad for ok, bad in zip(permitted, forbidden)),
                                 key=lambda columns: (columns.bit_count(), columns)))
        subtotal += weight * permanent(remaining)
    assert subtotal >= 0
    return subtotal


def literal(matrix, left, right, *, drop_witness=None, omit_singletons=False,
            allow_double_triangle=False, allow_two_singletons=False):
    """Visit every slot permutation; evaluate actual projected anchor pairs."""
    occupied_cells = {(row, col) for row, entries in enumerate(matrix)
                      for col, copies in enumerate(entries) if copies}
    boundary = set(product(range(len(matrix)), repeat=2)) - {(0, 0)}
    required = boundary - occupied_cells
    if drop_witness is not None:
        required.remove(drop_witness)
    if omit_singletons:
        left = tuple(mask for mask in left if mask.bit_count() != 1)
        right = tuple(mask for mask in right if mask.bit_count() != 1)
    anchors = lambda mask: tuple(index for index in range(len(matrix)) if 1 << index & mask)
    bits = {cell: 1 << index for index, cell in enumerate(sorted(required))}
    complete = sum(bits.values())
    impact = []
    for left_anchor in map(anchors, left):
        impacts = []
        for right_anchor in map(anchors, right):
            projection = set(product(left_anchor, right_anchor))
            if (0, 0) in projection and not allow_double_triangle:
                impacts.append(-1)
            elif len(projection) == 1 and not allow_two_singletons:
                impacts.append(-1)
            else:
                impacts.append(sum(bits[cell] for cell in projection & required))
        impact.append(tuple(impacts))
    total = 0
    for order in permutations(range(len(right))):
        seen = 0
        for row_choices, col in zip(impact, order):
            effect = row_choices[col]
            if effect == -1:
                break
            seen |= effect
        else:
            total += seen == complete
    return total


def historical_controls(boards, leaf, cold):
    rows = [row.split() for row in (SCOUT / 'mass.log').read_text().splitlines()]
    recorded = {(int(row[-4]), int(row[-3])): int(row[-2]) for row in rows}
    assert set(recorded) == {(8, 0)} | {(7, index) for index in range(6)}
    for (overlap, index), expected in sorted(recorded.items()):
        data = (boards if overlap == 7 else load(SCOUT / 'grid.5.0.json'))[index]
        args = board_and_slots(data, leaf, cold, defect=overlap == 7)
        exact = inclusion_exclusion(*args)
        oracle = literal(*args)
        assert exact == oracle == expected, (overlap, index, exact, oracle, expected)
        print('historical', overlap, index, exact, oracle, expected)
    return recorded


def calibrate(boards, leaf, cold):
    for overlap, basename in ((8, 'grid.3.0.json'), (7, 'grid.3.1.json')):
        small = []
        for data in load(SCOUT / basename):
            for doubles in (1, 2):
                shapes = tuple(combinations((3, 5, 6), doubles))
                for left_shape, right_shape in product(shapes, repeat=2):
                    args = board_and_slots(data, left_shape, right_shape, defect=overlap == 7)
                    exact = inclusion_exclusion(*args)
                    assert exact == literal(*args)
                    small.append(exact)
        assert any(small) and 0 in small
        print('small', overlap, 'supports/legal/zero', len(small), sum(small), small.count(0))
    recorded = historical_controls(boards, leaf, cold)
    mutation_board = 0
    args = board_and_slots(boards[mutation_board], leaf, cold)
    correct = recorded[7, mutation_board]
    mutant = literal(*args, drop_witness=(4, 4))
    assert mutant == 9072 > correct
    print('mutant omitted witness (4,4)', mutation_board, correct, mutant)
    mutant = literal(*args, omit_singletons=True)
    assert mutant == 2443 > 0
    print('mutant omitted both compulsory singletons', mutation_board, correct, mutant,
          'extra partial matchings if made optional')
    for flag, index, expected in (('allow_double_triangle', 0, 114857),
                                  ('allow_two_singletons', 2, 10946)):
        correct = recorded[7, index]
        mutant = literal(*board_and_slots(boards[index], leaf, cold), **{flag: True})
        assert mutant == expected > correct, (flag, correct, mutant)
        print('mutant', flag, index, correct, mutant)


@cache
def actions(matrix):
    width = len(matrix)
    permutations_fixing_zero = [(0, *tail) for tail in permutations(range(1, width))]
    occupied = Counter({(row, col): copies for row, entries in enumerate(matrix)
                        for col, copies in enumerate(entries) if copies})
    result = []
    for left, right in product(permutations_fixing_zero, repeat=2):
        mapped = {(left[row], right[col]): copies for (row, col), copies in occupied.items()}
        if mapped == occupied:
            result.append((False, left, right))
        if {(col, row): copies for (row, col), copies in mapped.items()} == occupied:
            result.append((True, left, right))
    return tuple(result)


@cache
def image(shape, permutation):
    return tuple(sorted(sum(1 << new for old, new in enumerate(permutation) if mask >> old & 1)
                        for mask in shape))


def freeze_key(row):
    board, left, right = row
    return board, tuple(left), tuple(right)


def bound_scope(boards, leaf, cold):
    all_pairs = {1 << first | 1 << second for first, second in combinations(range(5), 2)}
    shapes = {tuple(sorted(all_pairs - set(holes))) for holes in combinations(all_pairs, 2)
              if any(mask & 1 for mask in holes)}
    assert len(shapes) == 30
    frozen = load(FROZEN)
    assert len(boards) == 6 and len(frozen['pilots']) == 8
    board_actions = [actions(board_and_slots(data, leaf, cold)[0]) for data in boards]

    def key(board, left, right):
        assert left in shapes and right in shapes
        images = []
        for swap, left_action, right_action in board_actions[board]:
            lhs = image(left, left_action)
            rhs = image(right, right_action)
            images.append((rhs, lhs) if swap else (lhs, rhs))
        return board, *min(images)

    baseline = {key(board, leaf, right) for board in range(6)
                for right in (shapes if board in (0, 5) else (cold,))}
    assert len(baseline) == len(frozen['known']) == 51
    assert baseline == set(map(freeze_key, frozen['known']))
    seen = baseline.copy()
    membership = defaultdict(list)
    for pilot_num, pilot in enumerate(frozen['pilots'], 1):
        board = pilot['board']
        left = tuple(pilot['shape'])
        assert pilot_num == pilot['pilot']
        assert pilot['holes'] == sorted(all_pairs - set(left))
        assert pilot['singleton'] == 1 << boards[board]['left']
        assert pilot['preserves'] == sum(not act[0] for act in board_actions[board])
        assert pilot['flips'] == sum(act[0] for act in board_actions[board])
        scope = {key(board, left, right) for right in shapes}
        assert scope == set(map(freeze_key, pilot['right_orbits']))
        assert len(scope) == len(pilot['right_orbits'])
        assert len(scope - baseline) == pilot['baseline_fresh']
        assert len(scope - seen) == pilot['incremental_if_all_earlier_pass']
        seen.update(scope)
        for entry in scope - baseline:
            assert key(*entry) == entry
            membership[entry].append(pilot_num)
    assert set(membership) == seen - baseline
    assert len(membership) == frozen['potential_if_all_pass'] == 184
    print('scope rebind baseline/pilots/fresh', len(baseline), len(frozen['pilots']), len(membership))
    return membership


def counted(boards, key, verify):
    board, left, right = key
    args = board_and_slots(boards[board], left, right)
    exact = inclusion_exclusion(*args)
    if verify:
        assert exact == literal(*args), (key, exact)
    return exact


def pilot_sample(boards, membership):
    for board in range(len(boards)):
        candidates = sorted(key for key in membership if key[0] == board)
        for key in (candidates[0], candidates[-1]):
            start = process_time()
            count = counted(boards, key, True)
            print('price', *key, count, f'{process_time() - start:.6f}', flush=True)


def full(boards, membership, verify):
    counts = {key: counted(boards, key, verify) for key in sorted(membership)}
    assert counts.keys() == membership.keys()
    for filename, header in (
        ('alignments.tsv', ('board', 'left_pairs', 'right_pairs', 'left_singleton', 'right_singleton',
                            'fixed_labelled_alignments', 'pilots_after_baseline', 'first_pilot')),
        ('prefix.tsv', ('pilot', 'board', 'potential_keys_minus_baseline', 'potential_labelled_alignments',
                        'incremental_keys', 'incremental_labelled_alignments', 'prefix_keys',
                        'prefix_labelled_alignments')),
    ):
        with Path(filename).open('x') as out:
            print(*header, sep='\t', file=out)
            if filename == 'alignments.tsv':
                for key, count in counts.items():
                    board, left, right = key
                    csv = lambda values: ','.join(map(str, values))
                    print(board, csv(left), csv(right), 1 << boards[board]['left'],
                          1 << boards[board]['right'], count, csv(membership[key]),
                          membership[key][0], sep='\t', file=out)
            else:
                for pilot in range(1, 9):
                    scope = {key for key in counts if pilot in membership[key]}
                    increment = {key for key in scope if membership[key][0] == pilot}
                    prefix = {key for key in counts if membership[key][0] <= pilot}
                    assert len({key[0] for key in scope}) == 1
                    print(pilot, next(iter(scope))[0], len(scope), sum(counts[key] for key in scope),
                          len(increment), sum(counts[key] for key in increment), len(prefix),
                          sum(counts[key] for key in prefix), sep='\t', file=out)
    print('full distinct keys/alignments/zero keys', len(counts), sum(counts.values()),
          sum(value == 0 for value in counts.values()), 'literal check', verify)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['control', 'sample', 'full', 'replay'])
    phase = parser.parse_args().phase
    boards = load(SCOUT / 'grid.5.1.json')
    leaf, cold = map(tuple, load(SCHEMES)['leaf+matching.0'][1])
    if phase == 'control':
        calibrate(boards, leaf, cold)
        return
    members = bound_scope(boards, leaf, cold)
    if phase == 'sample':
        pilot_sample(boards, members)
    else:
        full(boards, members, verify=phase == 'full')


if __name__ == '__main__':
    main()
