#!/usr/bin/env python3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import math
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT / 'scratch/ideas/r012_R'
CATALOGUE = ROOT / 'gluing/val'


def graph6(path):
    for line in path.read_text().splitlines():
        order = ord(line[0]) - 63
        graph = [0] * order
        code = ''.join(f'{ord(symbol) - 63:06b}' for symbol in line[1:])
        for index, (first, last) in enumerate(
            (first, last) for last in range(order) for first in range(last)
        ):
            if code[index] == '1':
                graph[first] |= 1 << last
                graph[last] |= 1 << first
        yield graph


def bits(mask):
    while mask:
        take = mask & -mask
        yield take.bit_length() - 1
        mask ^= take


def controls():
    count = 0
    for graph in graph6(CATALOGUE / 'r3_7_22.g6'):
        if any(row.bit_count() != 6 for row in graph):
            continue
        cap = max((first & second).bit_count() for first, second in combinations(graph, 2))
        vertices = list(range(22))
        for first, second in combinations(vertices, 2):
            for third, fourth in combinations(bits(graph[first] & graph[second]), 2):
                full = (1 << len(graph)) - 1
                earlier = full & ~(graph[first] | graph[second] | 1 << first | 1 << second)
                later = full & ~(graph[third] | graph[fourth] | 1 << third | 1 << fourth)
                earlier_unresolved = (earlier & ~later) & ~(graph[third] ^ graph[fourth])
                later_unresolved = (later & ~earlier) & ~(graph[first] ^ graph[second])
                lower, upper = graph[:], graph[:]
                for earlier_site in bits(earlier_unresolved):
                    for later_site in bits(later_unresolved):
                        lower[earlier_site] &= ~(1 << later_site)
                        lower[later_site] &= ~(1 << earlier_site)
                        upper[earlier_site] |= 1 << later_site
                        upper[later_site] |= 1 << earlier_site
                print(6, cap, len(graph), *lower, *upper)
                count += 1
    assert count == 2118


def verify_roster():
    hosts = list(graph6(CATALOGUE / 'r3_6_17.g6'))
    frames = []
    by_frame = [Counter(), Counter()]
    for line in (SCOUT / 'frames17-5-2.txt').read_text().splitlines():
        host, *marks = map(int, line.split())
        graph = hosts[host]
        multiplicity = [sum(mark >> vertex & 1 for mark in marks) for vertex in range(17)]
        first, second = [vertex for vertex, mult in enumerate(multiplicity) if not mult]
        triple = max(multiplicity) == 3
        total = sum(graph[vertex].bit_count() for vertex in range(17) if multiplicity[vertex])
        edge = graph[first] >> second & 1
        common = (graph[first] & graph[second]).bit_count()
        first_degree, second_degree = graph[first].bit_count(), graph[second].bit_count()
        first_key = (host, total, edge, first_degree, second_degree, common)
        second_key = (host, total, edge, second_degree, first_degree, common)
        by_frame[0][first_key, triple] += 1
        by_frame[1][second_key, triple] += 1
        frames.append((first_key, second_key, triple))
    left_keys = {code for code, _ in by_frame[0]}
    base = {}
    for flip in (0, 1):
        for left_key in left_keys:
            for right_key in {code for code, _ in by_frame[flip]}:
                _, total, edge, left_first, left_second, left_common = left_key
                _, right_total, right_edge, right_first, right_second, right_common = right_key
                if (total != right_total or edge != right_edge or left_first + right_first != 9 + edge
                    or left_second + right_second != 9 + edge or left_common + right_common > 5):
                    continue
                left_pair = [by_frame[0][left_key, triple] for triple in (False, True)]
                right_pair = [by_frame[flip][right_key, triple] for triple in (False, True)]
                base[(*left_key, *right_key, flip)] = (
                    sum(left_pair) * sum(right_pair), left_pair[1] * sum(right_pair),
                    left_pair[0] * right_pair[1]
                )

    def key(left, right, flip):
        return (*frames[left][0], *frames[right][flip], flip)

    def encode(left, right, flip):
        assert 0 <= left < len(frames) and 0 <= right < len(frames) and flip in (0, 1)
        return 2 * (left * len(frames) + right) + flip

    legacy = set()
    legacy_counts = Counter()
    for line in Path('legacy.unique').open():
        left, right, flip = map(int, line.split())
        for first, second in ((left, right), (right, left)):
            identity = encode(first, second, flip)
            if identity in legacy:
                continue
            legacy.add(identity)
            if not (frames[first][2] or frames[second][2]):
                legacy_counts[key(first, second, flip)] += 1

    observed = set()
    selected = Counter()
    reverse_pairs = self_inverse = 0
    host_extrema = defaultdict(lambda: [len(frames), -1])
    for line in Path('pilot.ids').open():
        left, right, flip = map(int, line.split())
        identity = encode(left, right, flip)
        assert identity not in observed and identity not in legacy
        assert not frames[left][2] and not frames[right][2]
        assert key(left, right, flip) in base
        reverse_pairs += encode(right, left, flip) in observed
        self_inverse += left == right
        observed.add(identity)
        selected[key(left, right, flip)] += 1
        extremes = host_extrema[frames[left][0][0]]
        extremes[0] = min(extremes[0], left)
        extremes[1] = max(extremes[1], left)

    with Path('pilot.strata').open() as path:
        next(path)
        rows = [list(map(int, line.split())) for line in path]
    assert len(rows) == len(base) == len({tuple(row[:13]) for row in rows})
    for row in rows:
        signature = tuple(row[:13])
        header, left_triple, right_only, old, fresh, chosen = row[13:]
        assert base[signature] == (header, left_triple, right_only)
        assert legacy_counts[signature] == old and selected[signature] == chosen
        assert header - left_triple - right_only - old == fresh
        assert fresh // 100 <= chosen <= (fresh + 99) // 100
    print('independent strata sums', len(base), *map(sum, zip(*(row[13:] for row in rows))))
    print('unique pilot ordered IDs', len(observed), 'legacy overlap 0', 'triple overlap 0')
    print('pilot internal reversal pairs', reverse_pairs, 'self-inverse ordered IDs', self_inverse)
    print('covered left ID extrema per host', dict(sorted(host_extrema.items())))


def scout_terminal(path):
    sys.path.insert(0, str(SCOUT))
    import terminal

    terminal.setup()
    for line in Path(path).open():
        frame_id = tuple(map(int, line.split()))
        detail = Counter()
        start = time.process_time_ns()
        terminal.audit(*frame_id, detail)
        milliseconds = (time.process_time_ns() - start) / 1e6
        print(*frame_id, *(detail[key] for key in ('degree', 'triangle', 'codegree', 'I10', 'still-live')),
              f'{milliseconds:.3f}')


def summarize(path):
    record = [list(map(float, line.split())) for line in Path(path).open()]
    assert all(len(row) == 9 for row in record)
    by_id = {(row[0], row[1], row[2]) for row in record}
    assert len(by_id) == len(record) > 0
    outputs = [row[3:8] for row in record]
    fills = [sum(row) for row in outputs]
    joint = sum(bool(value) for value in fills)
    remain = sum(bool(row[-1]) for row in outputs)
    totals = [int(sum(values)) for values in zip(*outputs)]
    times = sorted(row[-1] for row in record)
    tails = {f'p{percent}': times[math.ceil(percent * len(times) / 100) - 1]
             for percent in (50, 95, 99, 100)}
    print('panel', len(record), 'joint', joint, 'no-joint', len(record) - joint,
          'terminal', joint - remain, 'open', remain)
    print('fillings', int(sum(fills)), 'totals by degree/triangle/codegree/I10/open', totals,
          'max per ID', int(max(fills)))
    print('CPU-ms per ID', tails, 'sum', round(sum(times), 3))


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'controls':
        controls()
    elif action == 'roster':
        verify_roster()
    elif action == 'scout':
        scout_terminal(sys.argv[2])
    elif action == 'summary':
        summarize(sys.argv[2])
    else:
        raise SystemExit('unknown action')
