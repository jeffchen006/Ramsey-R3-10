#!/usr/bin/env python3
"""Check exact one-edge coverage of supplied residue classes, not census completeness."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import subprocess
import sys

from audit_floor_covers import BIN, digest, has_independent, require
from residue_bundle import parse_graph6, read_catalogue, to_graph6, triangle_free


def labels(rows):
    if not rows:
        return []
    output = subprocess.run([str(BIN / 'labelg'), '-q'], input=b'\n'.join(rows) + b'\n',
                            capture_output=True, check=True, timeout=120).stdout.splitlines()
    require(len(output) == len(rows), 'canonicalizer row count changed')
    return output


def unique_labels(rows):
    result = labels(rows)
    require(len(result) == len(set(result)), 'duplicate isomorphism class')
    return result


def checked_catalogue(path, order, cap, expected=None):
    rows = read_catalogue(path)
    census = Counter()
    for row in rows:
        graph = parse_graph6(row.decode('ascii'))
        require(len(graph) == order and to_graph6(graph).encode('ascii') == row
                and triangle_free(graph) and not has_independent(graph, cap + 1),
                f'invalid graph at {path}: {row!r}')
        census[sum(map(int.bit_count, graph)) // 2] += 1
    if expected is not None:
        require(census == expected, f'wrong edge counts in {path}: {census}')
    return rows, unique_labels(rows)


def moves(binary, mode, cap, rows):
    if not rows:
        return []
    proc = subprocess.run([str(binary), mode, str(cap)], input=b'\n'.join(rows) + b'\n',
                          capture_output=True, check=True, timeout=150)
    print(proc.stderr.decode('ascii').strip(), flush=True)
    moved = []
    used = set()
    for line in proc.stdout.splitlines():
        source, lower, higher, row = line.split(b'\t')
        key = int(source) - 1, int(lower), int(higher)
        require(0 <= key[0] < len(rows) and key not in used, 'duplicate/bad emitted move index')
        used.add(key)
        moved.append((*key, row))
    return moved


def expected_moves(rows, mode, cap):
    result = set()
    for index, row in enumerate(rows):
        graph = parse_graph6(row.decode('ascii'))
        for lower, higher in combinations(range(len(graph)), 2):
            if bool(graph[lower] & (1 << higher)) != (mode == 'down'):
                continue
            modified = graph.copy()
            modified[lower] ^= 1 << higher
            modified[higher] ^= 1 << lower
            if triangle_free(modified) and not has_independent(modified, cap + 1):
                result.add((index, lower, higher, to_graph6(modified).encode('ascii')))
    return result


def relation(binary, mode, cap, rows, canonicals):
    raw = moves(binary, mode, cap, rows)
    moved_labels = labels([row for _, _, _, row in raw])
    pairs = {(canonicals[index], target) for (index, _, _, _), target in zip(raw, moved_labels)}
    sources = {first for first, _ in pairs}
    targets = {second for _, second in pairs}
    print(f'{mode}: {len(pairs)} canonical incidences, {len(sources)} sources, {len(targets)} targets',
          flush=True)
    return pairs, targets


def decomposition(binary, lower_rows, lower_labels, higher_rows, higher_labels, cap):
    upward, up_targets = relation(binary, 'up', cap, lower_rows, lower_labels)
    downward, down_targets = relation(binary, 'down', cap, higher_rows, higher_labels)
    require(upward == {(low, high) for high, low in downward},
            f'up/down canonical incidence mismatch ({len(upward)} vs {len(downward)})')
    require(up_targets <= set(higher_labels) and down_targets <= set(lower_labels), 'missing class')
    up_neighbors = defaultdict(set)
    for lower, higher in upward:
        up_neighbors[lower].add(higher)
    print('zero-addition lower:', len(set(lower_labels) - down_targets),
          '; deletion-critical higher:', len(set(higher_labels) - up_targets), flush=True)
    print('upper-neighbor multiplicity:', sorted(Counter(len(up_neighbors[item]) for item in lower_labels).items()),
          flush=True)
    return set(higher_labels) - up_targets


def expect_rejection(action, marker):
    try:
        action()
    except ValueError as error:
        require(marker in str(error), f'wrong negative result: {error}')
        print(f'PASS rejected {marker}: {error}', flush=True)
    else:
        raise ValueError(f'accepted {marker} negative control')


def bind_level(previous_labels, new_rows, new_labels, expected=None):
    require(len(previous_labels) == len(set(previous_labels)) and len(new_rows) == len(new_labels)
            and len(new_labels) == len(set(new_labels)), 'duplicate isomorphism in bind')
    previous = set(previous_labels)
    require(previous <= set(new_labels), 'frozen class omitted from new decomposition')
    require(expected is None or len(new_labels) == expected, 'bind does not attain expected count')
    return [row for row, label in zip(new_rows, new_labels) if label not in previous]


def calibrate(binary, path, cap=6):
    rows, canonicals = checked_catalogue(path, 22, cap,
                                        {60: 1, 61: 6, 62: 30, 63: 60, 64: 59, 65: 25, 66: 10})
    levels = defaultdict(list)
    for row, label in zip(rows, canonicals):
        size = sum(map(int.bit_count, parse_graph6(row.decode('ascii')))) // 2
        levels[size].append((row, label))
    positives = {mode: expected_moves(rows, mode, cap) for mode in ('up', 'down')}
    for mode, expected in positives.items():
        require(expected == set(moves(binary, mode, cap, rows)), f'C22 labelled {mode} disagreement')
    for index in range(60, 66):
        decomposition(binary, *zip(*levels[index]), *zip(*levels[index + 1]), cap)
    sample = parse_graph6(rows[0].decode('ascii'))
    last = len(sample) - 1
    perm = [last, *range(1, last), 0]
    relabelled = to_graph6([sum(1 << j for j, other in enumerate(perm) if sample[old] >> other & 1)
                            for old in perm]).encode('ascii')
    require(relabelled != rows[0], 'permutation did not change bytes')
    expect_rejection(lambda: unique_labels([rows[0], relabelled]), 'duplicate isomorphism')
    lower_rows, lower_labels = zip(*levels[65])
    higher_rows, higher_labels = zip(*levels[66])
    upward = labels([row for _, _, _, row in moves(binary, 'up', cap, lower_rows)])
    omitted = next(index for index, label in enumerate(higher_labels) if label in upward)
    expect_rejection(lambda: decomposition(binary, lower_rows, lower_labels,
                                           higher_rows[:omitted] + higher_rows[omitted + 1:],
                                           higher_labels[:omitted] + higher_labels[omitted + 1:], cap),
                     'incidence mismatch')
    expect_rejection(lambda: checked_catalogue(path, 22, cap, {66: 10}), 'wrong edge counts')
    require(bind_level(higher_labels[:-1], higher_rows, higher_labels, 10) == [higher_rows[-1]],
            'exact-count delta binding lost class')
    expect_rejection(lambda: bind_level(higher_labels[:1], higher_rows[1:], higher_labels[1:], 10),
                     'frozen class omitted')
    expect_rejection(lambda: bind_level(higher_labels[:-1], higher_rows[:-1], higher_labels[:-1], 10),
                     'expected count')
    print('PASS census and exact labelled moves for all 191 C22 classes', flush=True)


def run(binary, low, middle, high, critical_path=None):
    lower_rows, lower_labels = checked_catalogue(low, 33, 8, {118: 5, 119: 69})
    middle_rows, middle_labels = checked_catalogue(middle, 33, 8)
    high_rows, high_labels = checked_catalogue(high, 33, 8)
    for rows, edge in ((middle_rows, 120), (high_rows, 121)):
        require(all(sum(map(int.bit_count, parse_graph6(row.decode('ascii')))) == 2 * edge for row in rows),
                f'mixed edge level: {edge}')
    at119 = [(row, label) for row, label in zip(lower_rows, lower_labels)
             if sum(map(int.bit_count, parse_graph6(row.decode('ascii')))) == 238]
    middle_critical = decomposition(binary, *zip(*at119), middle_rows, middle_labels, 8)
    high_critical = decomposition(binary, middle_rows, middle_labels, high_rows, high_labels, 8)
    if critical_path is not None:
        require(high_critical == set(unique_labels(read_catalogue(critical_path))),
                'e121 critical split differs from frozen set')
    print(f'deletion-critical levels: e120 {len(middle_critical)}, e121 {len(high_critical)}')
    print(f'census: 74 + {len(middle_rows)} + {len(high_rows)} = {74 + len(middle_rows) + len(high_rows)}')


def bind_delta(old_paths, new_paths, output, partial):
    previous_total = next_total = 74
    additions_by_edge = {}
    frozen_sha = {120: '7db2550bbfc2f03238c74e9e62f7199008db509e4df54ebff89645ca9cde3e16',
                  121: 'e0aec16b130743337a05b242ca170fc5ee050df3b018f7c5a0d3523efb9d001c'}
    for edge, old, new in zip((120, 121), old_paths, new_paths):
        count_old = {120: 1223, 121: 13092}[edge]
        require(digest(old.read_bytes()) == frozen_sha[edge], f'wrong frozen e{edge} baseline')
        old_rows, frozen = checked_catalogue(old, 33, 8, {edge: count_old})
        if old.resolve() == new.resolve():
            rows, canonical = old_rows, frozen
        else:
            rows, canonical = checked_catalogue(new, 33, 8)
            require(all(sum(map(int.bit_count, parse_graph6(row.decode('ascii')))) == 2 * edge for row in rows),
                    f'new catalogue mixes edge levels: {new}')
        additions_by_edge[edge] = bind_level(frozen, rows, canonical)
        previous_total += len(frozen)
        next_total += len(rows)
    require(previous_total <= next_total <= 14395, 'combined count outside published bounds')
    require(partial or next_total == 14395, f'combined count still short by {14395 - next_total}')
    output.mkdir(exist_ok=True)
    for edge, additions in additions_by_edge.items():
        path = output / f'delta{edge}.g6'
        path.write_bytes(b''.join(row + b'\n' for row in additions))
        print(f'e{edge}: {len(additions)} exact new canonical classes; labelled inputs at {path}', flush=True)
    print(f'{previous_total} → {next_total}; gap {14395 - next_total}; no exclusions implied')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    sub = parser.add_subparsers(dest='action', required=True)
    small = sub.add_parser('calibrate')
    small.add_argument('census', type=Path)
    official = sub.add_parser('run')
    official.add_argument('lower', type=Path)
    official.add_argument('middle', type=Path)
    official.add_argument('higher', type=Path)
    official.add_argument('--critical', type=Path)
    bind = sub.add_parser('bind-delta')
    bind.add_argument('old120', type=Path)
    bind.add_argument('old121', type=Path)
    bind.add_argument('new120', type=Path)
    bind.add_argument('new121', type=Path)
    bind.add_argument('output', type=Path)
    bind.add_argument('--allow-gap', action='store_true')
    args = parser.parse_args()
    if args.action == 'calibrate':
        calibrate(args.binary, args.census)
    elif args.action == 'bind-delta':
        bind_delta((args.old120, args.old121), (args.new120, args.new121), args.output, args.allow_gap)
    else:
        run(args.binary, args.lower, args.middle, args.higher, args.critical)


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        sys.exit(str(error))
