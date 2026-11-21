"""Independent incidence and proof-key audits for the new P3 strata."""

import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path

from p3_e63_index import CENSUS_DIGEST


def has_independent(neighbours, available, need):
    if not need:
        return True
    while available.bit_count() >= need:
        bit = available & -available
        available ^= bit
        if has_independent(neighbours, available & ~neighbours[bit.bit_length() - 1], need - 1):
            return True
    return False


def census(path):
    assert sha256(path.read_bytes()).hexdigest() == CENSUS_DIGEST
    lines = path.read_text().splitlines()
    assert len(set(lines)) == len(lines) == 191
    result = {}
    for index, line in enumerate(lines):
        assert line[0] == 'U' and len(line) == 40
        payload = ''.join(format(ord(char)-63, '06b') for char in line[1:])
        assert payload[231:] == '000'
        neighbours = [0] * 22
        edge_count = 0
        for (row, col), present in zip(((low, high) for high in range(22) for low in range(high)), payload):
            if present == '1':
                neighbours[row] |= 1 << col
                neighbours[col] |= 1 << row
                edge_count += 1
        assert all(not neighbours[first] & neighbours[second] for first, second in combinations(range(22), 2)
                   if neighbours[first] >> second & 1)
        assert not has_independent(neighbours, (1 << 22) - 1, 7)
        result[index] = (edge_count, sha256(line.encode()).hexdigest())
    assert Counter(edges for edges, _ in result.values()) == {60: 1, 61: 6, 62: 30, 63: 60, 64: 59, 65: 25, 66: 10}
    return result


def boundary_edges(key):
    matrix, left, right, middle = key
    edges = {(wing, 3 + opposite) for wing in range(3) for opposite in range(3)
             if matrix >> (3 * wing + opposite) & 1}
    for root, adjacent in [(15, list(range(3)) + list(range(6, 12))), (16, range(6, 15)),
                           (17, [3, 4, 5, 6, 7, 8, 9, 10, 12])]:
        edges.update((vertex, root) for vertex in adjacent)
    for column, memberships in [(11, (0, right)), (12, (left, 0)), (13, middle[0]), (14, middle[1])]:
        edges.update((3 * side + vertex, column) for side, mask in enumerate(memberships)
                     for vertex in range(3) if mask >> vertex & 1)
    return edges


def boundary_pass(edges):
    neighbourhoods = [0] * 18
    for low, high in edges:
        neighbourhoods[low] |= 1 << high
        neighbourhoods[high] |= 1 << low
    if min(mask.bit_count() for mask in neighbourhoods) < 3:
        return False
    for left, right in combinations(range(18), 2):
        codegree = (neighbourhoods[left] & neighbourhoods[right]).bit_count()
        if codegree > 6:
            return False
        if right >= 15 and left < 15 and (left, right) not in edges and not 1 <= codegree <= 5:
            return False
    for size, limit in ((3, 6), (4, 5)):
        for a_side in combinations(range(18), size):
            common = (1 << 18) - 1
            for vertex in a_side:
                common &= neighbourhoods[vertex]
            if common.bit_count() >= limit:
                return False
    return not has_independent(neighbourhoods, (1 << 18) - 1, 10)


def low_boundary(work):
    ordered = defaultdict(set)
    for line in (work / 'p3boundary-independent.log').read_text().splitlines():
        if line.startswith('key '):
            total, matrix, left, right, p_left, p_right, q_left, q_right, _ = map(int, line.split()[1:])
            ordered[total + 45].add((matrix, left, right, ((p_left, p_right), (q_left, q_right))))
    assert {size: len(keys) for size, keys in ordered.items()} == {63: 13, 62: 90, 61: 361, 60: 976}
    unoriented = {}
    for line in (work / 'p3-boundary-levels.log').read_text().splitlines():
        if line.startswith('key 62 '):
            _, _, index, status, key = line.split(' ', 4)
            unoriented[int(index)] = (ast.literal_eval(key), status == 'pass')
    assert list(unoriented) == list(range(49))
    ordered_by_edges = {frozenset(boundary_edges(key)): key for key in ordered[62]}
    cover = set()
    good = set()
    for index, (key, passing) in unoriented.items():
        edges = boundary_edges(key)
        assert len(edges) == 44 and boundary_pass(edges) == passing
        equivalents = set()
        for left_wing in permutations((3, 4, 5)):
            for right_wing in permutations((0, 1, 2)):
                for private in ((13, 14), (14, 13)):
                    mapping = (*left_wing, *right_wing, 6, 7, 8, 9, 10, 12, 11, *private, 17, 16, 15)
                    converted = frozenset(tuple(sorted((mapping[low], mapping[high]))) for low, high in edges)
                    if converted in ordered_by_edges:
                        equivalents.add(ordered_by_edges[converted])
        assert len(equivalents) == 1
        orbit = equivalents | {key}
        assert key == min(orbit) and not cover & orbit
        cover |= orbit
        if passing:
            good.add(index)
    assert cover == ordered[62] and len(good) == 44
    print('PASS e62 independent 27-bit boundary cover: 90 ordered -> 49 reversal orbits -> 44 passing')
    return good


def inventory(log, kind):
    checked, bounds, nonchecked = {}, {}, {}
    for line in log.read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == 'row':
            assert len(fields) == 5, (log, line)
            key = fields[1]
            if kind == 'lower':
                row, mode, layout, count = key.split('-')
                assert mode == 'fixed' and count == '1'
                key = (int(row), int(layout))
            else:
                key = int(key)
            if fields[2] == 'checked':
                assert key not in checked
                checked[key] = float(fields[-1])
            else:
                assert key not in nonchecked
                nonchecked[key] = fields[2]
        if fields and fields[0] == 'bound':
            assert len(fields) == 5, (log, line)
            if kind == 'lower':
                row, mode, layout, count = fields[1].split('-')
                assert mode == 'fixed' and count == '1'
                key = (int(row), int(layout))
            else:
                key = int(fields[1])
            assert key not in bounds
            assert all(len(digest) == 64 for digest in fields[2:4])
            bounds[key] = tuple(fields[2:])
    return {key: bounds[key] for key in checked}, nonchecked


def upper(work, rows):
    indexed = []
    for diagonal in (3, 4):
        pilot, pilot_open = inventory(work / f'p3flex-pilot-{diagonal - 2}.log', 'upper')
        production, rest_open = inventory(work / f'p3flex-upper-{diagonal}.log', 'upper')
        replay, replay_open = inventory(work / f'p3flex-upper-replay-{diagonal}.log', 'upper')
        expected = {row for row, (size, _) in rows.items() if size in (65, 66)}
        assert not (pilot_open or rest_open or replay_open or set(pilot) & set(production))
        assert pilot | production == replay and set(replay) == expected and len(expected) == 35
        for row, binding in sorted(replay.items()):
            file = work / 'p3flex-pilot' / f'{diagonal}-guarded-{row:03d}.lrat'
            assert file.stat().st_size == int(binding[-1])
            indexed.append((diagonal, row, *rows[row], *binding))
    print('PASS 70/70 e65/e66 flexible keys; producer and replay CNF/proof hashes match')
    return indexed


def isolated_upper(work, rows):
    pilot, pilot_open = inventory(work / 'p2anchor-pilot-1.log', 'upper')
    production, rest_open = inventory(work / 'p2anchor-full-1.log', 'upper')
    replay, replay_open = inventory(work / 'p2anchor-replay-1.log', 'upper')
    expected = {row for row, (size, _) in rows.items() if size == 65}
    assert not (pilot_open or rest_open or replay_open or set(pilot) & set(production))
    assert pilot | production == replay and set(replay) == expected and len(expected) == 25
    for row, binding in replay.items():
        assert (work / 'p2anchor' / f'p2anchor-1-{row}.lrat').stat().st_size == int(binding[-1])
    print('PASS 25/25 isolated P2 anchor e65 keys; producer and replay CNF/proof hashes match')
    return [(row, *rows[row], *binding) for row, binding in sorted(replay.items())]


def lower(work, rows, replay, partial):
    layouts = low_boundary(work)
    expected = {(row, layout) for row, (size, _) in rows.items() if size == 62 for layout in layouts}
    assert len(expected) == 1320
    proved, deferred = {}, {}
    for path in sorted(work.glob('p3e62-full-*.log')) + sorted(work.glob('p3low-pilot-*-fixed.log')):
        batch, unfinished = inventory(path, 'lower')
        assert not (set(proved) & set(batch) or set(deferred) & set(unfinished))
        proved.update(batch)
        deferred.update(unfinished)
    assert set(proved) | set(deferred) <= expected and not set(proved) & set(deferred)
    print(f'e62 checked={len(proved)} deferred={len(deferred)} absent={len(expected - set(proved) - set(deferred))}')
    for key, status in sorted(deferred.items()):
        print('deferred', *key, status)
    if replay:
        checked = {}
        for path in sorted(work.glob('p3e62-replay-*.log')):
            batch, other = inventory(path, 'lower')
            assert not other and not set(checked) & set(batch)
            checked.update(batch)
        assert checked == proved
    assert partial or set(proved) == expected
    indexed = []
    for (row, layout), binding in sorted(proved.items()):
        file = work / 'p3low-pilot' / f'{row}-fixed-{layout}-1.lrat'
        assert file.stat().st_size == int(binding[-1])
        indexed.append((row, layout, *rows[row], *binding))
    return indexed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--part', choices=['boundary', 'upper', 'lower', 'isolated-upper'], required=True)
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = census(args.census)
    if args.part == 'boundary':
        low_boundary(args.work)
        return
    if args.part == 'upper':
        result = upper(args.work, rows)
    elif args.part == 'isolated-upper':
        result = isolated_upper(args.work, rows)
    else:
        result = lower(args.work, rows, args.replay, args.partial)
    if args.output:
        args.output.write_text(''.join('\t'.join(map(str, record)) + '\n' for record in result))


if __name__ == '__main__':
    main()
