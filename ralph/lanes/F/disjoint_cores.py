#!/usr/bin/env python3
"""Split two marked core pools by canonical identity and retain full provenance."""

import argparse
import csv
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path

from pole_audit import canon_text, independent, independent_sets, num_edges, one_graph, to_graph6


G6_DIGITS = [chr(63 + int(f'{value:06b}'[::-1], 2)) for value in range(64)]


def deleted_graph6(graph, removed):
    reversed_cuts = [(vertex, (1 << vertex) - 1) for vertex in reversed(removed)]
    packed, position, degree_index = 0, 0, 0
    for vertex, mask in enumerate(graph):
        if vertex in removed:
            continue
        column = mask & ((1 << vertex) - 1)
        for cut, lower in reversed_cuts:
            if cut < vertex:
                column = (column & lower) | ((column >> (cut + 1)) << cut)
        packed |= column << position
        position += degree_index
        degree_index += 1
    return chr(63 + degree_index) + ''.join(G6_DIGITS[(packed >> shift) & 63] for shift in range(0, position, 6))


def delete_rows(source, count, fixed_ceiling):
    graph = one_graph(source)
    assert len(graph) == 40 and 161 <= num_edges(graph) <= 180
    assert all(4 <= neighbors.bit_count() <= 9 and independent(neighbors, graph) for neighbors in graph)
    bad = list(independent_sets(graph, (1 << len(graph)) - 1, 10))
    print(f'{source}: I10={len(bad)} edges={num_edges(graph)}')
    for removed in combinations(range(len(graph)), count):
        bits = sum(1 << vertex for vertex in removed)
        fixed = sum(not bits & witness for witness in bad)
        if (fixed == 0 if fixed_ceiling is None else 0 < fixed <= fixed_ceiling):
            yield deleted_graph6(graph, removed), ','.join(map(str, removed))


def completion_rows(source, bases, expected_order):
    base_rows = bases.read_text().splitlines()
    order = ord(base_rows[0][0]) - 63
    complete, partial = divmod(order * (order - 1) // 2, 6)
    prefix = complete + 1
    suffix = (expected_order * (expected_order - 1) // 2 + 5) // 6 + 1
    assert all(ord(line[0]) - 63 == order and len(line) == prefix + bool(partial) for line in base_rows)
    with source.open() as stream:
        for line, record in enumerate(csv.DictReader(stream, delimiter='\t')):
            core = record['graph6']
            row = int(record['row'])
            assert 0 <= row < len(base_rows)
            base = base_rows[row]
            assert len(core) == suffix and ord(core[0]) - 63 == expected_order and core[1:prefix] == base[1:prefix]
            if partial:
                assert (ord(core[prefix]) - 63) >> (6 - partial) == (ord(base[prefix]) - 63) >> (6 - partial)
            yield core, f'{row},{line}'


def catalogue(rows):
    raw = list(rows)
    marked = {}
    for key, (_, marker) in zip(canon_text([graph for graph, _ in raw]), raw, strict=True):
        marked.setdefault(key, []).append(marker)
    return raw, marked


def split(args):
    if args.delete:
        assert not args.bases and len(set(canon_text([to_graph6(one_graph(source)) for source in args.sources]))) == 2
        streams = [delete_rows(source, args.delete, args.fixed_ceiling) for source in args.sources]
    else:
        assert args.bases and args.fixed_ceiling is None
        streams = [completion_rows(source, base, args.order) for source, base in zip(args.sources, args.bases, strict=True)]
    excluded = {line for path in args.exclude for line in path.read_text().splitlines()}
    records = [catalogue(rows) for rows in streams]
    marked_a, marked_b = [record[1] for record in records]
    shared = marked_a.keys() & marked_b.keys()
    print(f'shared={len(shared)} excluded_unique={len(excluded)}')
    available = set(marked_a) | set(marked_b)
    files = []
    for side, (raw, marked) in enumerate(records):
        keys = sorted(marked.keys() - excluded - (marked_a.keys() if side else set()))
        prefix = f'{args.prefix}.{("A", "B")[side]}'
        core_path = Path(prefix + '.g6')
        core_path.write_text(''.join(key + '\n' for key in keys))
        marks_path = Path(prefix + '.marks.tsv')
        marks_path.write_text(''.join(f'{index}\t{";".join(marked_a.get(key, ()))}\t'
                                     f'{";".join(marked_b.get(key, ()))}\n' for index, key in enumerate(keys)))
        print(f'{prefix}: raw={len(raw)} unique={len(marked)} prior={len(marked.keys() & excluded)} '
              f'kept={len(keys)} sha256={sha256(core_path.read_bytes()).hexdigest()}')
        files.append(set(keys))
    assert not (files[0] & files[1]) and files[0] | files[1] == available - excluded


def sample(args):
    lines = args.input.read_text().splitlines()
    size = min(args.limit, len(lines))
    indices = [(2 * index + 1) * len(lines) // (2 * size) for index in range(size)]
    assert len(set(indices)) == size
    Path(args.prefix + '.g6').write_text(''.join(lines[index] + '\n' for index in indices))
    Path(args.prefix + '.idx').write_text(''.join(f'{index}\n' for index in indices))


def summary_counts(path, ncores):
    lines = path.read_text().splitlines()
    capped = []
    counts = Counter()
    for index, record in enumerate(csv.DictReader(lines[:-1], delimiter='\t')):
        assert index == int(record['row']) and index < ncores
        assert record['status'] in ('complete', 'output_cap')
        if record['status'] == 'output_cap':
            capped.append(index)
        for edges in range(5):
            count = int(record.get(f'edges{edges}', 0))
            assert count >= 0
            if count:
                counts[index, edges] = count
    assert ncores == index + 1 and lines[-1] == f'terminal rows={ncores} capped={len(capped)}'
    return counts, capped


def recover(args):
    bases = args.cores.read_text().splitlines()
    counts, capped = summary_counts(args.summary, len(bases))
    if args.replay:
        replay_bases, replay_summary, replay_models = args.replay
        assert replay_bases.read_text().splitlines() == [bases[index] for index in capped]
        replay_counts, still_capped = summary_counts(replay_summary, len(capped))
        assert not still_capped
    else:
        assert not capped

    def copy(source, expected, skipped, permutation, output):
        observed = Counter()
        with source.open() as stream:
            for record in csv.DictReader(stream, delimiter='\t'):
                index, edges = int(record['row']), int(record['internal_edges'])
                key = (index, edges)
                observed[key] += 1
                if index not in skipped:
                    output.write(f'{permutation(index)}\t{edges}\t{record["graph6"]}\n')
        assert observed == expected, (source, sum(observed.values()), sum(expected.values()))
        return sum(count for (index, _), count in observed.items() if index not in skipped)

    with args.output.open('w') as output:
        output.write('row\tinternal_edges\tgraph6\n')
        count = copy(args.models, counts, set(capped), lambda index: index, output)
        if args.replay:
            count += copy(replay_models, replay_counts, set(), capped.__getitem__, output)
    print(f'PASS cores={len(bases)} replay={capped} records={count} sha256={sha256(args.output.read_bytes()).hexdigest()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(required=True)
    splitting = modes.add_parser('split')
    splitting.add_argument('prefix')
    splitting.add_argument('sources', nargs=2, type=Path)
    mode = splitting.add_mutually_exclusive_group(required=True)
    mode.add_argument('--delete', type=int)
    mode.add_argument('--order', type=int)
    splitting.add_argument('--bases', nargs=2, type=Path)
    splitting.add_argument('--fixed-ceiling', type=int)
    splitting.add_argument('--exclude', nargs='*', type=Path, default=[])
    splitting.set_defaults(run=split)
    sampling = modes.add_parser('sample')
    sampling.add_argument('input', type=Path)
    sampling.add_argument('limit', type=int)
    sampling.add_argument('prefix')
    sampling.set_defaults(run=sample)
    recovery = modes.add_parser('recover')
    for name in ('cores', 'summary', 'models', 'output'):
        recovery.add_argument(name, type=Path)
    recovery.add_argument('--replay', nargs=3, type=Path)
    recovery.set_defaults(run=recover)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
