"""Apply checked prefixes directly to every weak hole key and its label orbit."""

import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path


def cover(stage, snapshot):
    status = json.loads(snapshot.read_text())
    original = json.loads((stage / 'baseline.json').read_text())
    boards = json.loads((stage / '../round22/h5/manifest.json').read_text())
    slots = tuple((1 << first) + (1 << second) for first, second in combinations(range(5), 2))
    holes = set(tuple(sorted(pair)) for pair in combinations(slots, 2) if (pair[0] | pair[1]) & 1)
    assert len(holes) == 30
    order = [(0, 0), (0, 1), (1, 0), (1, 1)] + [(side, slot) for slot in range(2, 10) for side in (0, 1)]

    def word(pair):
        return ''.join('0' if slots[slot] in pair[side] else '1' for side, slot in order)

    raw = dict((pair, word(pair)) for pair in product(holes, repeat=2))
    groups = [(0, *tail) for tail in permutations(range(1, 5))]

    def remapped(mask, perm):
        return sum(1 << index for index, original in enumerate(perm) if mask & (1 << original))

    moves = {perm: {pair: tuple(sorted(remapped(mask, perm) for mask in pair)) for pair in holes}
             for perm in groups}
    result = {}
    whole = []
    exact_keys = 0
    for board in boards:
        ident = str(board['id'])
        if ident in original['reviewed'] or board['id'] in status['added']:
            whole.append(board['id'])
            exact_keys += len(board['keys'])
            prefixes = ('',) if ident in original['reviewed'] else tuple(status['proofs'][ident])
            assert all(any(bits.startswith(prefix) for prefix in prefixes) for bits in raw.values())
            continue
        prefixes = tuple(status['proofs'].get(ident, {}))
        if not prefixes:
            continue
        grid = tuple(map(tuple, board['grid']))
        stabilizer = []
        for left, right in product(groups, repeat=2):
            moved = tuple(tuple(grid[row][col] for col in right) for row in left)
            if moved == grid:
                stabilizer.append((left, right, False))
            if tuple(zip(*moved)) == grid:
                stabilizer.append((left, right, True))
        assert len(stabilizer) * board['orbit_size'] == len(groups) ** 2 * 2
        reviewed = {}
        checked = {pair for pair, bits in raw.items() if any(bits.startswith(prefix) for prefix in prefixes)}
        seen = set()
        for key, item in enumerate(board['keys']):
            lhs, rhs = map(tuple, item)
            orbit = set()
            for left, right, transpose in stabilizer:
                pair = (moves[left][lhs], moves[right][rhs])
                orbit.add(pair[::-1] if transpose else pair)
            assert (lhs, rhs) == min(orbit) and not seen & orbit
            seen |= orbit
            if good := checked & orbit:
                representative = min(good)
                reviewed[key] = [representative, sorted(prefix for prefix in prefixes
                                                        if raw[representative].startswith(prefix))]
        assert seen == set(raw)
        exact_keys += len(reviewed)
        result[ident] = reviewed
        if len(reviewed) == len(board['keys']):
            whole.append(board['id'])
    assert len(whole) >= status['board_count'] and exact_keys >= status['key_count']
    print(json.dumps(dict(board_count=len(whole), whole=sorted(whole), key_count=exact_keys,
                          partial_keys=result, baseline_board_count=status['board_count'],
                          baseline_key_count=status['key_count']), separators=(',', ':')))


if __name__ == '__main__':
    cover(*map(Path, sys.argv[1:]))
