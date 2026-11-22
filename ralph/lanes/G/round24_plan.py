"""Independently map exact h5 prefixes to admissible physical occupancy orbits."""

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path


def complement(prefixes, prefix=''):
    if prefix in prefixes:
        return []
    if not any(other.startswith(prefix) for other in prefixes):
        return [prefix]
    return complement(prefixes, prefix + '0') + complement(prefixes, prefix + '1')


def cylinder_rows(manifest, status, prior, failed=None):
    slots = [sum(1 << index for index in pair) for pair in combinations(range(5), 2)]
    holes = [tuple(sorted(pair)) for pair in combinations(slots, 2) if (pair[0] | pair[1]) & 1]
    assert len(holes) == 30
    order = [(0, 0), (0, 1), (1, 0), (1, 1)] + list(product((2, 3, 4, 5, 6, 7, 8, 9), (0, 1)))
    order = [item if index < 4 else item[::-1] for index, item in enumerate(order)]
    words = {pair: ''.join('01'[slots[slot] not in pair[side]] for side, slot in order)
             for pair in product(holes, repeat=2)}
    assert len(set(words.values())) == 900 and {word.count('0') for word in words.values()} == {4}
    perms = [(0, *tail) for tail in permutations(range(1, 5))]
    actions = {perm: {pair: tuple(sorted(sum(1 << target for target, source in enumerate(perm)
                                            if mask & (1 << source)) for mask in pair)) for pair in holes}
               for perm in perms}
    attempts = defaultdict(list)
    for name, row in status['terminal'].items():
        attempts[row['board'], row['prefix']].append((name, row['result']))
    for name, row in (failed or {}).items():
        attempts[row['board'], row['prefix']].append((name, row['result']))
    census = {}
    queue = []
    for number in status['boards_open']:
        board = manifest[number]
        checked = status['proofs'].get(str(number), {})
        gaps = complement(checked)
        grid = tuple(map(tuple, board['grid']))
        stabilizer = []
        for left, right in product(perms, repeat=2):
            moved = tuple(tuple(grid[row][col] for col in right) for row in left)
            if moved == grid:
                stabilizer.append((left, right, False))
            if tuple(zip(*moved)) == grid:
                stabilizer.append((left, right, True))
        assert len(stabilizer) * board['orbit_size'] == 1152
        hit = set()
        seen = set()
        residual = {}
        split = {}
        for gap in gaps:
            prev = attempts[number, gap]
            any_capped = any(any(label in label_text for label in ('cap', 'resource', 'timeout', 'envelope'))
                             for _, label_text in prev)
            if any_capped:
                split[gap] = [gap + sign for sign in '01']
            elif len(gaps) == 1 and not gap:
                split[gap] = ['0', '1']
            else:
                split[gap] = [gap]
        scopes = [child for children in split.values() for child in children]
        for ident, pair in enumerate(board['keys']):
            orig = tuple(map(tuple, pair))
            orbit = set()
            for left, right, transposed in stabilizer:
                moved = actions[left][orig[0]], actions[right][orig[1]]
                orbit.add(moved[::-1] if transposed else moved)
            assert orig == min(orbit) and not seen & orbit
            seen |= orbit
            representations = {words[item] for item in orbit}
            if any(word.startswith(prefix) for word in representations for prefix in checked):
                hit.add(str(ident))
                continue
            coverage = {scope: sorted(word for word in representations if word.startswith(scope)) for scope in scopes}
            assert sum(map(len, coverage.values())) == len(orbit)
            residual[str(ident)] = {scope: units for scope, units in coverage.items() if units}
        assert seen == set(words)
        assert hit == set(prior['partial_keys'].get(str(number), {}))
        footprints = Counter(scope for coverage in residual.values() for scope in coverage)
        for gap, children in split.items():
            for scope in children:
                related = [result for pattern in (gap, '', scope) for _, result in attempts[number, pattern]]
                mode = 'DM' if any('SAT relaxation' in result for result in related) or not related else 'D'
                queue.append(dict(board=number, parent=gap, prefix=scope, mode=mode,
                                  keys=footprints[scope], id=f'g{number:03}_{scope or "full"}',
                                  labels=sum(word.startswith(scope) for word in words.values())))
        census[str(number)] = dict(maximal=gaps, splits=split, residual=residual)
    return census, queue


if __name__ == '__main__':
    stage = Path(sys.argv[1])
    manifest = json.loads((stage / '../round22/h5/manifest.json').read_text())
    status = json.loads((stage / 'incoming.json').read_text())
    holes = json.loads((stage / 'incoming-holes.json').read_text())
    census, queue = cylinder_rows(manifest, status, holes)
    total = sum(len(row['residual']) for row in census.values())
    assert total == 10612 and len(census) == 30
    assert len({row['id'] for row in queue}) == len(queue)
    (stage / 'complement.json').write_text(json.dumps(census, separators=(',', ':')) + '\n')
    queue.sort(key=lambda row: (-row['keys'], -len(row['prefix']), row['board']))
    (stage / 'queue.json').write_text(json.dumps(queue, indent=2) + '\n')
    print(json.dumps(dict(keys=total, maximal=sum(len(row['maximal']) for row in census.values()),
                          scopes=len(queue), zero_labelled=sum(not row['labels'] for row in queue),
                          zero_keys=sum(not row['keys'] for row in queue), modes=Counter(row['mode'] for row in queue))))
