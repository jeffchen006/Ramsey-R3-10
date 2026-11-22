#!/usr/bin/env python3
"""Audit marked lower and mixed sources, receipts, pins, and eager clauses."""

import argparse
from collections import Counter
from functools import lru_cache
import gzip
from hashlib import sha256
from itertools import combinations, islice, product
from pathlib import Path
import re
import sys

import pynauty

from audit_floor_covers import require
from audit_path_leaf import vertices
from audit_strip_proofs import verified
from residue_bundle import parse_graph6, triangle_free


ROOT = Path(__file__).resolve().parents[3]


def independent(adj, size, remaining=None, chosen=()):
    if size == 0:
        yield chosen
        return
    if remaining is None:
        remaining = (1 << len(adj)) - 1
    while remaining.bit_count() >= size:
        bit = remaining & -remaining
        vertex = bit.bit_length() - 1
        remaining ^= bit
        yield from independent(adj, size-1, remaining & ~adj[vertex], (*chosen, vertex))


@lru_cache(maxsize=8192)
def validate_graph(encoded):
    adj = tuple(parse_graph6(encoded))
    require(triangle_free(adj), 'triangle in source graph')
    require(next(independent(adj, 8), None) is None, 'source alpha > 7')
    require(next(independent(adj, 7), None) is not None, 'source alpha < 7')
    return adj


def mark(adj, left, right):
    require(left.bit_count() == right.bit_count() == 4 and not left & right, 'invalid side widths')
    sides = tuple(tuple(vertices(mask)) for mask in (left, right))
    require(not any(adj[vertex] & mask for mask, side in zip((left, right), sides) for vertex in side),
            'nonindependent side')
    cross = [(first, second) for first, second in product(*sides) if adj[first] >> second & 1]
    require(len(cross) == 1, 'wrong cross edge count')
    outside = tuple(vertices(((1 << len(adj)) - 1) ^ left ^ right))
    require(all(0 < (adj[vertex] & mask).bit_count() <= 2 for mask in (left, right) for vertex in outside),
            'invalid outside support width')
    supports = tuple(Counter(tuple(anchor for anchor in side if adj[vertex] >> anchor & 1) for vertex in outside)
                     for side in sides)
    require(all(count <= (4 if len(signature) == 1 else 1) for counts in supports
                for signature, count in counts.items()), 'invalid support multiplicity')
    return sides, cross[0], supports


def raw_link(path, row_id, encoded, raw):
    order = ord(encoded[0]) - 63
    stride = 2 + (order * (order-1)//2 + 5)//6
    raw.seek((int(row_id)-1)*stride)
    require(raw.read(stride) == encoded.encode() + b'\n', f'source row mismatch: {path}:{row_id}')


def colored_key(adj, sides):
    order = len(adj)
    adjacency = {vertex: list(vertices(mask)) for vertex, mask in enumerate(adj)}
    for marker, side in enumerate(sides, order):
        adjacency[marker] = list(side)
        for vertex in side:
            adjacency[vertex].append(marker)
    anchors = set().union(*map(set, sides))
    colors = [set(range(order, order+2)), anchors, set(range(order)) - anchors]
    return pynauty.certificate(pynauty.Graph(order+2, adjacency_dict=adjacency, vertex_coloring=colors))


def source_lower(marked, expected, source, universe):
    core_keys = set()
    for line in universe.read_text().splitlines():
        adj = tuple(parse_graph6(line))
        require(len(adj) == 22 and triangle_free(adj) and next(independent(adj, 7), None) is None,
                'invalid (3,7;22) core')
        core_keys.add(pynauty.certificate(pynauty.Graph(22, adjacency_dict={index: list(vertices(ns))
                                                                          for index, ns in enumerate(adj)})))
    require(len(core_keys) == 191 and len(universe.read_text().splitlines()) == 191, 'wrong core class count')

    def load(mark_file):
        records = set()
        classes = Counter()
        with source.open('rb') as raw:
            for line in mark_file.read_text().splitlines():
                row_id, first, second, encoded = line.split()
                require(int(row_id) > 0 and line not in records, 'duplicate mark or nonpositive row')
                records.add(line)
                raw_link(source, row_id, encoded, raw)
                adj = validate_graph(encoded)
                sides, _, _ = mark(adj, int(first), int(second))
                order = len(adj)
                degrees = tuple(mask.bit_count() for mask in adj)
                require(order in (25, 26) and degrees[-1] == min(degrees) == order-23 and max(degrees) <= 7,
                        'wrong minimum-degree root or degree range')
                rest = tuple(vertices(((1 << (order-1))-1) & ~adj[-1]))
                root_core = pynauty.certificate(pynauty.Graph(22, adjacency_dict={
                    index: [other for other, peer in enumerate(rest) if adj[vertex] >> peer & 1]
                    for index, vertex in enumerate(rest)}))
                require(root_core in core_keys, 'root antineighborhood absent from exact core source')
                classes[colored_key(adj, sides)] += 1
        return records, classes

    marked_rows, classes = load(marked)
    rep_rows, reps = load(expected)
    require(rep_rows <= marked_rows, 'representative has no marked source row')
    require(set(classes) == set(reps) and all(count == 1 for count in reps.values()), 'incorrect marked quotient')
    print(f'source lower {len(core_keys)} cores, {len(marked_rows)} valid marked rows, {len(reps)} exact orbits', flush=True)


def mixed_roles(side, star, contacts):
    pivot = max(side)+1
    pairs = tuple(combinations((*side, pivot), 2))
    for holes in combinations(pairs, 2):
        if sum(pivot in hole for hole in holes) != 1:
            continue
        first, second = next(hole for hole in holes if pivot not in hole)
        if (first, second) in contacts:
            continue
        peer, _ = next(hole for hole in holes if pivot in hole)
        degrees = Counter(vertex for hole in holes for vertex in hole)
        if max(degrees.values()) == 1 and degrees[star] == 1:
            yield ('matching', first, second, peer)
        if max(degrees.values()) == 2 and degrees[star] == 2:
            yield ('middle', first, second, peer)


def source_mixed(marked, expected, source):
    roles = set()
    notes = Counter()
    distinct = set()
    with source.open('rb') as raw:
        for line in marked.read_text().splitlines():
            row, first, second, encoded = line.split()
            require(line not in distinct, 'duplicate paired mark')
            distinct.add(line)
            raw_link(source, row, encoded, raw)
            adj = validate_graph(encoded)
            require(len(adj) == 27, 'wrong source order')
            sides, stars, counts = mark(adj, int(first), int(second))
            for path, mixed, index in ((first, second, 1), (second, first, 0)):
                for case, left, right, peer in mixed_roles(sides[index], stars[index], counts[index]):
                    rendered = f'{row} {path} {mixed} {case} {left} {right} {peer} {encoded}'
                    require(rendered not in roles, 'duplicate mixed role')
                    roles.add(rendered)
                    notes[index, case] += 1
    supplied = expected.read_text().splitlines()
    require(len(supplied) == len(set(supplied)) and set(supplied) == roles, 'mixed roles differ')
    print(f'source mixed {len(distinct)} marks, {len(roles)} exact ordered roles, {dict(notes)}', flush=True)


def read_keys(files):
    result = {}
    for path in files:
        for line in path.read_text().splitlines():
            *fields, encoded = line.split()
            key = '_'.join(fields)
            require(key not in result, f'duplicate key {key}')
            result[key] = (fields, encoded)
    return result


def bind(source, batches, ordered_shards=None):
    covered = {}
    attempts = set()
    statuses = Counter()
    for folder, *logs in batches:
        folder = Path(folder)
        for log in map(Path, logs):
            for number, line in enumerate(log.read_text().splitlines()):
                key, status, *rest = line.split()
                require(key in source and key not in attempts, f'unknown or duplicate receipt: {key}')
                if ordered_shards is not None:
                    wanted = ordered_shards[log]
                    require(number < len(wanted) and key == wanted[number], f'receipt ordering mismatch {log}:{number+1}')
                attempts.add(key)
                statuses[status] += 1
                if status != 'CERT':
                    require(status in ('CAP', 'RELAXED_SAT', 'TIMEOUT', 'SIGNAL', 'CPU_CAP', 'ERROR')
                            and len(rest) == 2, f'bad nonterminal receipt {line}')
                    continue
                require(len(rest) == 3 and re.fullmatch('[0-9a-f]{64}', rest[0]), f'bad terminal receipt {line}')
                trace = folder / f'{key}.lrat.gz'
                require(trace.is_file() and trace.stat().st_size == int(rest[1]), f'trace size/file mismatch: {trace}')
                covered[key] = (trace, rest[0])
    return covered, statuses, attempts


def pins(fields, adj):
    _, first, second, *role = fields
    first, second = int(first), int(second)
    sides, stars, counts = mark(adj, first, second)
    order = len(adj)
    roots = (order, order+1)
    centres = (order+2, order+3)
    shared = order-(23 if role else 24)
    common = tuple(range(order+4, order+4+shared))
    split = len(common)+order+4+6-shared
    exclusive = (tuple(range(order+4+shared, split)), tuple(range(split, 40)))
    hole = None
    if role:
        case, *labels = role
        left, right, peer = map(int, labels)
        require((case, left, right, peer) in set(mixed_roles(sides[1], stars[1], counts[1])), 'invalid mixed role')
        hole = (left, right)

    def pair(left, right):
        return (min(left, right), max(left, right))

    assigned = {edge: bool(adj[edge[0]] >> edge[1] & 1) for edge in combinations(range(order), 2)}

    def put(left, right, value):
        edge = pair(left, right)
        require(edge not in assigned or assigned[edge] == value, f'contradictory fixed edge {edge}')
        assigned[edge] = value

    for index, side in enumerate(sides):
        root, centre = roots[index], centres[index]
        for vertex in range(40):
            if vertex != root:
                put(vertex, root, vertex in side or vertex in roots or vertex == centre)
            if vertex not in roots and vertex != centre:
                put(vertex, centre, vertex in common or vertex in exclusive[index])
        wanted = Counter({(anchor,): 4 for anchor in side})
        wanted.update(pair for pair in combinations(side, 2) if index == 0 or pair != hole)
        require(not counts[index] - wanted, 'invalid covered role signatures')
        for vertex, contact in zip(exclusive[1-index], sorted((wanted - counts[index]).elements()), strict=True):
            for anchor in side:
                put(vertex, anchor, anchor in contact)
    for left, right in combinations(common + exclusive[0] + exclusive[1], 2):
        if not (left in exclusive[0] and right in exclusive[1]):
            put(left, right, False)
    supports = [set() for _ in range(40)]
    for (left, right), value in assigned.items():
        if value:
            supports[left].add(right)
            supports[right].add(left)
    for left, right in combinations(range(40), 2):
        if supports[left] & supports[right] and (left, right) not in assigned:
            put(left, right, False)
    return {edge: 1 if value else -1 for edge, value in assigned.items()}, exclusive, centres


def eager_tail(edge, adj, exclusive, centres):
    order = len(adj)
    require(all(edge[retained, centre] == -1 for retained in range(order) for centre in centres),
            'centre has an unassigned or present retained edge')
    for size in (7, 6):
        groups = []
        for index, candidates in enumerate(exclusive):
            for removed in combinations(candidates, 9-size):
                fixed = sorted((*removed, centres[1-index]))
                require(len(fixed) == len(set(fixed)) == 10-size and min(fixed) >= order
                        and all(edge[pair] == -1 for pair in combinations(fixed, 2)), 'wrong fixed eager edges')
                rows = [tuple(edge[retained, peer] for peer in removed) for retained in range(order)]
                blocked = sum(1 << retained for retained, row in enumerate(rows) if 1 in row)
                groups.append((blocked, [tuple(lit for lit in row if lit > 1) for row in rows]))
        for retained in islice(independent(adj, size), 10000):
            mask = sum(1 << vertex for vertex in retained)
            for blocked, rows in groups:
                if not mask & blocked:
                    yield tuple(literal for vertex in retained for literal in rows[vertex])


def replay(args):
    source = read_keys([args.keys])
    schedule = {}
    require(len(args.batch) == len(args.schedule), 'each batch needs a schedule')
    scheduled = set()
    for (_, *logs), list_file in zip(args.batch, args.schedule):
        ordered = read_keys([list_file])
        require(all(key in source and source[key] == value for key, value in ordered.items())
                and not (scheduled & ordered.keys()), 'overlapping or wrong scheduled source')
        scheduled |= ordered.keys()
        for index, log in enumerate(logs):
            schedule[Path(log)] = list(ordered)[index::len(logs)]
    require(scheduled == set(source), 'pilot/pending key union differs from exact source')
    for folder, *logs in args.continuation or ():
        for log in logs:
            require(Path(log) not in schedule, 'continued log duplicates a primary log')
    primary, statuses, attempts = bind(source, args.batch, schedule)
    covered = dict(primary)
    all_traces = {trace for trace, _ in primary.values()}
    if args.continuation:
        require(len(args.continuation) == len(args.resume), 'each continuation needs a resume schedule')
        allowed_overlap = set(args.allow_overlap.read_text().split()) if args.allow_overlap else set()
        remaining = (source.keys() - attempts) | allowed_overlap
        require(allowed_overlap <= primary.keys(), 'overlap is not already certified')
        for (_, *logs), list_file in zip(args.continuation, args.resume):
            ordered = read_keys([list_file])
            require(all(key in remaining and source[key] == value for key, value in ordered.items()),
                    'resume not from unattempted or explicitly permitted primary keys')
            remaining = remaining - ordered.keys()
            for index, log in enumerate(logs):
                schedule[Path(log)] = list(ordered)[index::len(logs)]
        require(not remaining, 'resume schedules omit unattempted primary keys')
        batches = args.batch + args.continuation
        secondary, second_statuses, secondary_attempts = bind(source, args.continuation, schedule)
        for key, (trace, checksum) in secondary.items():
            if key in primary:
                require(primary[key][1] == checksum, 'repeated key with different CNF hash')
            else:
                covered[key] = trace, checksum
            all_traces.add(trace)
        print(f'continuation attempted {len(secondary_attempts)}, including {len(secondary_attempts & attempts)} '
              f'explicit repeats; receipts {dict(second_statuses)}', flush=True)
        statuses.update(second_statuses)
        attempts |= secondary_attempts
    else:
        batches = args.batch
    missing = sorted(source.keys() - attempts)
    print(f'{len(source)} keys; receipts {dict(statuses)}; {len(covered)} unique certificates; '
          f'{len(missing)} unattempted', flush=True)
    if args.require_cover:
        require(set(covered) == set(source), 'terminal certificates do not exactly cover source')
        traces = {trace for folder, *_ in batches for trace in Path(folder).glob('*.lrat.gz')}
        require(traces == all_traces, 'orphan trace(s)')
    if args.bind_only:
        for key in sorted(covered):
            trace, digest = covered[key]
            print(f'{key}\t{digest}\t{trace.stat().st_size}\t{trace}')
        return

    sys.path.insert(0, str(ROOT / 'ralph/lanes/G'))
    from mixed_strip_completion import instance
    from strip_completion import window

    done = set()
    for old in args.exclude:
        for row in old.read_text().splitlines():
            fields = row.split()
            if not (len(fields) == 5 and re.fullmatch('[0-9a-f]{64}', fields[-1])):
                continue
            key, _, _, checksum, proof_hash = fields
            require(key in covered and key not in done and covered[key][1] == checksum,
                    'replay exclusion has duplicate key, missing receipt or different CNF digest')
            require(sha256(covered[key][0].read_bytes()).hexdigest() == proof_hash,
                    'excluded proof trace changed since replay')
            done.add(key)
    candidates = set(covered) - (primary.keys() if args.only_continuation else set())
    require(not args.only_continuation or args.continuation, 'no continuation to verify')
    selected = sorted(candidates - done)
    if args.sample:
        require(0 < args.sample <= len(selected), 'bad sample size')
        selected = [selected[index*len(selected)//args.sample] for index in range(args.sample)]
    rank, count = args.shard
    require(0 <= rank < count, 'bad shard')
    args.output.mkdir(parents=True, exist_ok=True)
    for key in selected[rank::count]:
        fields, encoded = source[key]
        adj = validate_graph(encoded)
        expected, exclusive, centres = pins(fields, adj)
        _, first, second, *role = fields
        eager = 0 if args.fast_hash else 10000
        if role:
            case, *labels = role
            problem = instance(encoded, int(first), int(second), case, *map(int, labels), eager)
        else:
            problem = window(encoded, int(first), int(second), eager, True, True)
        require(expected == {pair: state for pair, state in problem.edge.items() if abs(state) == 1}, 'pin mismatch')
        tail = list(eager_tail(problem.edge, adj, exclusive, centres))
        if args.fast_hash:
            problem.formula.clauses.extend(tail)
        elif tail:
            require(tail == problem.formula.clauses[-len(tail):], 'eager clause mismatch')
        if args.sample and not args.fast_hash:
            if role:
                bare = instance(encoded, int(first), int(second), case, *map(int, labels), 0)
            else:
                bare = window(encoded, int(first), int(second), 0, True, True)
            require(problem.formula.clauses == bare.formula.clauses + tail and
                    problem.formula.last == bare.formula.last, 'eager clauses not exact suffix')
        trace, digest = covered[key]
        cnf, proof = [args.output / f'{key}.{ext}' for ext in ('cnf', 'lrat')]
        problem.formula.write(cnf)
        require(sha256(cnf.read_bytes()).hexdigest() == digest, f'reconstructed CNF hash mismatch {key}')
        compressed = trace.read_bytes()
        if args.verify:
            proof.write_bytes(gzip.decompress(compressed))
            require(all(verified(binary, cnf, proof) for binary in ('cake_lpr', 'lrat-check')), f'LRAT mismatch {key}')
        print(key, len(expected), len(tail), digest, sha256(compressed).hexdigest(), flush=True)
        if not args.sample:
            cnf.unlink()
            proof.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for mode in ('lower', 'mixed'):
        child = sub.add_parser(mode)
        for name in ('marked', 'expected', 'source') + (('universe',) if mode == 'lower' else ()):
            child.add_argument(name, type=Path)
    child = sub.add_parser('replay')
    child.add_argument('keys', type=Path)
    child.add_argument('output', type=Path)
    child.add_argument('--batch', action='append', nargs='+', required=True)
    child.add_argument('--schedule', action='append', type=Path, required=True)
    child.add_argument('--continuation', action='append', nargs='+')
    child.add_argument('--resume', action='append', type=Path, default=[])
    child.add_argument('--allow-overlap', type=Path)
    child.add_argument('--require-cover', action='store_true')
    child.add_argument('--bind-only', action='store_true')
    child.add_argument('--sample', type=int, default=0)
    child.add_argument('--shard', type=int, nargs=2, default=(0, 1))
    child.add_argument('--verify', action='store_true')
    child.add_argument('--fast-hash', action='store_true')
    child.add_argument('--exclude', action='append', type=Path, default=[])
    child.add_argument('--only-continuation', action='store_true')
    args = parser.parse_args()
    if args.command == 'lower':
        source_lower(args.marked, args.expected, args.source, args.universe)
    elif args.command == 'mixed':
        source_mixed(args.marked, args.expected, args.source)
    else:
        replay(args)


if __name__ == '__main__':
    main()
