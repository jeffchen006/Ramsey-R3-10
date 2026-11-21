#!/usr/bin/env python3
"""Prepare and independently audit fixed-core joins of two or three vertices."""

import argparse
import csv
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
from random import Random
import subprocess

from orbit_extend import ROOT, independent, independent_sets, parse_graph6, to_graph6, vertices


def one_graph(path):
    [text] = path.read_text().strip().splitlines()
    return parse_graph6(text)


def relabel(graph, ordered):
    return [sum(((graph[old] >> other) & 1) << index for index, other in enumerate(ordered))
            for old in ordered]


def canonical_poles(graph, add):
    base = tuple(range(len(graph) - add))
    return min(to_graph6(relabel(graph, base + permutation))
               for permutation in permutations(range(len(base), len(graph))))


def num_edges(graph):
    return sum(mask.bit_count() for mask in graph) // 2


def write_lines(path, lines):
    path.write_text(''.join(line + '\n' for line in lines))


def prepare_controls(add):
    random = Random(41194)
    data = set()
    while len(data) < 36:
        order = random.randrange(3, 9)
        graph = [0] * order
        for left, right in combinations(range(order), 2):
            if graph[left] & graph[right] or random.random() > 0.48:
                continue
            graph[left] |= 1 << right
            graph[right] |= 1 << left
        data.add(to_graph6(graph))
    data.update(['Bw', 'Bg'])
    write_lines(Path('ctl_small.g6'), sorted(data))
    for label, graph_path in [('ctl35', '../r1/fast35_11.found.g6'), ('ctl38', '../r3/ctl38comp.0.0.g6')]:
        graph = one_graph(Path(graph_path))
        print(label, 'order=', len(graph), 'edges=', num_edges(graph),
              'degree range=', min(mask.bit_count() for mask in graph), max(mask.bit_count() for mask in graph))
        used = set()
        cores = []
        witnesses = []
        for poles in combinations(range(len(graph)), add):
            internal = tuple(sorted((graph[vertex] & sum(1 << other for other in poles)).bit_count()
                                    for vertex in poles))
            if internal in used:
                continue
            used.add(internal)
            base = tuple(vertex for vertex in range(len(graph)) if vertex not in poles)
            cores.append(to_graph6(relabel(graph, base)))
            witnesses.append(canonical_poles(relabel(graph, base + poles), add))
        assert len(used) == {2: 2, 3: 3, 4: 7}[add]
        suffix = {2: 'pair', 3: '', 4: 'quad'}[add]
        write_lines(Path(f'{label}{suffix}.g6'), cores)
        write_lines(Path(f'{label}{suffix}.witness.g6'), witnesses)


def canon_text(lines):
    raw = ''.join(line + '\n' for line in lines)
    result = subprocess.run([str(ROOT / 'opt/bin/labelg'), '-q'], input=raw, capture_output=True,
                            text=True, check=True)
    result_lines = result.stdout.splitlines()
    if len(result_lines) != raw.count('\n'):
        raise RuntimeError('canonicalization count mismatch')
    return result_lines


def prepare_anchor(source, old, add, prefix):
    graph = one_graph(source)
    anchor = one_graph(old)
    canonical = canon_text([to_graph6(graph), to_graph6(anchor)])
    if canonical[0] == canonical[1] or len(graph) != 40 or any(not independent(row, graph) for row in graph):
        raise ValueError('baseline is not a distinct triangle-free n40 seed')
    degrees = [degree.bit_count() for degree in graph]
    if min(degrees) < 4 or max(degrees) > 9 or num_edges(graph) < 161:
        raise ValueError('baseline fails degree or edge window')
    write_lines(Path(prefix + '.compare.g6'), canonical)
    bad = list(independent_sets(graph, (1 << len(graph)) - 1, 10))
    cores, marks = [], []
    pool = set(range(len(graph)))
    for poles in combinations(range(len(graph)), add):
        mask = sum(1 << vertex for vertex in poles)
        if all(mask & witness for witness in bad):
            cores.append(to_graph6(relabel(graph, sorted(pool.difference(poles)))))
            marks.append(','.join(map(str, poles)))
    unique = {}
    for core, mark in zip(canon_text(cores), marks, strict=True):
        unique.setdefault(core, []).append(mark)
    write_lines(Path(prefix + '.g6'), sorted(unique))
    write_lines(Path(prefix + '.marks.tsv'), [f'{index}\t{";".join(unique[core])}' for index, core in enumerate(sorted(unique))])
    print(f'source={source} old={old} canonical_distinct=1 I10={len(bad)} '
          f'e={num_edges(graph)} degree={min(degrees)}..{max(degrees)} marked={len(marks)} unique={len(unique)}')


def prepare_sources(sources, sample):
    valid = []
    labels = []
    for source in sources:
        graph = one_graph(source)
        if (len(graph) != 39 or any(not independent(row, graph) for row in graph) or
                next(independent_sets(graph, (1 << 39) - 1, 10), None) is not None):
            print(f'ineligible_source={source}')
            continue
        valid.append(to_graph6(graph))
        labels.append(source.name)
    seeds = {}
    for source, label in zip(canon_text(valid), labels, strict=True):
        seeds.setdefault(source, []).append(label)
    ordered = sorted(seeds)
    universe = set(range(39))
    raw_cores = []
    marks = []
    for index, source in enumerate(ordered):
        graph = parse_graph6(source)
        print(f'source={index} e={num_edges(graph)} labels={",".join(seeds[source])}')
        for left, right in combinations(range(39), 2):
            raw_cores.append(to_graph6(relabel(graph, sorted(universe - {left, right}))))
            marks.append((index, left, right))
    cores = {}
    for core, mark in zip(canon_text(raw_cores), marks, strict=True):
        cores.setdefault(core, []).append(','.join(map(str, mark)))
    ordered_cores = sorted(cores)
    write_lines(Path('seeds39.g6'), ordered)
    write_lines(Path('seeds37.g6'), ordered_cores)
    write_lines(Path('seeds37.marks.tsv'), [f'{index}\t{";".join(cores[core])}' for index, core in enumerate(ordered_cores)])
    indices = [index * len(cores) // sample for index in range(sample)]
    if len(set(indices)) != sample:
        raise ValueError('sample must fit the distinct core count')
    write_lines(Path('seeds37pilot.idx'), map(str, indices))
    write_lines(Path('seeds37pilot.g6'), (ordered_cores[index] for index in indices))
    print(f'terminal sources={len(seeds)} marks={len(marks)} distinct_cores={len(cores)} sample={sample}')


def prepare_projected(close, pool, scores, outside, limit, sample):
    pool = pool.read_text().splitlines()
    outside = set(outside.read_text().splitlines())
    with scores.open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    if len(rows) != len(pool) or any(int(record['idx']) != index for index, record in enumerate(rows)):
        raise ValueError('score catalogue does not bind to every pool row')
    ranked = sorted((int(record['I_k']), index, source)
                    for index, (record, source) in enumerate(zip(rows, pool, strict=True))
                    if record['I_k'] != 'NA' and source in outside)[:limit]
    chosen = sorted(set(close.read_text().splitlines()).union(source for _, _, source in ranked))
    marks, cores = [], []
    for index, core in enumerate(chosen):
        graph = parse_graph6(core)
        for deleted in range(len(graph)):
            cores.append(to_graph6(relabel(graph, [vertex for vertex in range(len(graph)) if vertex != deleted])))
            marks.append(f'{index},{deleted}')
    unique = {}
    for core, mark in zip(canon_text(cores), marks, strict=True):
        unique.setdefault(core, []).append(mark)
    ordered = sorted(unique)
    write_lines(Path('project38.source39.g6'), chosen)
    write_lines(Path('project38.ranked.tsv'), (f'{score}\t{index}' for score, index, _ in ranked))
    write_lines(Path('project38.g6'), ordered)
    write_lines(Path('project38.marks.tsv'), [f'{index}\t' + ';'.join(unique[core])
                                             for index, core in enumerate(ordered)])
    indices = [index * len(ordered) // sample for index in range(sample)]
    if len(set(indices)) != sample:
        raise ValueError('sample exceeds the distinct core count')
    write_lines(Path('project38pilot.idx'), map(str, indices))
    write_lines(Path('project38pilot.g6'), (ordered[index] for index in indices))
    print(f'terminal scored_pool={len(pool)} selected_outside={len(ranked)} '
          f'unique_sources={len(chosen)} raw_cores={len(cores)} unique_cores={len(ordered)} sample={sample}')


def sat_models(base, add, k, low, emin, emax):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Cadical195

    size = len(base)
    order = size + add
    universe = (1 << size) - 1
    if any(not independent(mask, base) for mask in base) or next(independent_sets(base, universe, k), None) is not None:
        return set()
    pool = IDPool()
    edges = {edge: pool.id(edge) for edge in combinations(range(order), 2) if edge[1] >= size}
    clauses = []
    for trio in combinations(range(order), 3):
        pairs = list(combinations(trio, 2))
        if any(right < size and not (base[left] & (1 << right)) for left, right in pairs):
            continue
        clauses.append([-edges[pair] for pair in pairs if pair in edges])
    for count in range(1, add + 1):
        for mask in independent_sets(base, universe, k - count):
            for poles in combinations(range(size, order), count):
                clauses.append([edges[edge] for edge in combinations(poles, 2)] +
                               [edges[vertex, pole] for vertex in vertices(mask) for pole in poles])

    def bound(literals, minimum, maximum):
        if minimum > len(literals) or maximum < 0 or minimum > maximum:
            clauses.append([])
            return
        if minimum > 0:
            clauses.extend(CardEnc.atleast(literals, minimum, vpool=pool, encoding=EncType.seqcounter).clauses)
        if maximum < len(literals):
            clauses.extend(CardEnc.atmost(literals, maximum, vpool=pool, encoding=EncType.seqcounter).clauses)

    for vertex in range(order):
        degree = base[vertex].bit_count() if vertex < size else 0
        bound([var for edge, var in edges.items() if vertex in edge], low - degree, k - 1 - degree)
    bound(list(edges.values()), emin - num_edges(base), emax - num_edges(base))
    answers = set()
    with Cadical195(bootstrap_with=clauses) as solver:
        while solver.solve():
            active = {var for var in solver.get_model() if 0 < var <= len(edges)}
            graph = base + [0] * add
            for (left, right), var in edges.items():
                if var in active:
                    graph[left] |= 1 << right
                    graph[right] |= 1 << left
            answers.add(canonical_poles(graph, add))
            for permutation in permutations(range(size, order)):
                ordered = tuple(range(size)) + permutation
                solver.add_clause([(-var if graph[ordered[left]] & (1 << ordered[right]) else var)
                                   for (left, right), var in edges.items()])
    return answers


def audit(args):
    bases = [parse_graph6(line) for line in args.cores.read_text().splitlines()]
    models = [set() for _ in bases]
    counts = [[0] * 5 for _ in bases]
    with args.models.open() as stream:
        for record in csv.DictReader(stream, delimiter='\t'):
            index = int(record['row'])
            graph = parse_graph6(record['graph6'])
            base = bases[index]
            assert len(graph) == len(base) + args.add
            assert relabel(graph, range(len(base))) == base
            counts[index][int(record['internal_edges'])] += 1
            models[index].add(canonical_poles(graph, args.add))
    with args.summary.open() as stream:
        lines = stream.read().splitlines()
        trailers = [line for line in lines if line.startswith('terminal ')]
        assert trailers == [f'terminal rows={len(bases)} capped=0'], trailers
        summaries = list(csv.DictReader((line for line in lines if not line.startswith('terminal ')), delimiter='\t'))
    assert len(summaries) == len(bases)
    planted = args.witness.read_text().splitlines() if args.witness else None
    if planted is not None:
        assert len(planted) == len(bases)
    for index, (record, base, found) in enumerate(zip(summaries, bases, models, strict=True)):
        assert int(record['row']) == index
        assert record['status'] in {'complete', 'bad_core'}
        assert [int(record.get(f'edges{edge}', 0)) for edge in range(5)] == counts[index]
        if planted is not None:
            assert planted[index] in found, index
        if args.sat:
            expected = sat_models(base, args.add, args.k, args.low, args.emin, args.emax)
            assert found == expected, (index, len(found), len(expected), list(found - expected)[:1], list(expected - found)[:1])
        print(f'row={index} patterns={counts[index]} distinct_mod_pole_labels={len(found)}', flush=True)
    print(f'PASS cores={len(bases)} planted={len(bases) if planted is not None else 0} '
          f'exact_sat={len(bases) if args.sat else 0}', flush=True)


def soft_brute(base, k, lo, emin, emax, poles=2, include_fixed=False):
    size = len(base)
    universe = (1 << size) - 1
    if any(not independent(mask, base) for mask in base) or (
            not include_fixed and next(independent_sets(base, universe, k), None) is not None):
        return None
    base_edges = num_edges(base)
    columns = [mask for mask in range(1 << size) if mask.bit_count() <= k - 1 and independent(mask, base)]
    best = None
    pairs = [(left, right) for right in range(poles) for left in range(right)]
    for selected in combinations_with_replacement(columns, poles):
        degrees = [mask.bit_count() + sum((column >> vertex) & 1 for column in selected)
                   for vertex, mask in enumerate(base)]
        if min(degrees) < lo or max(degrees) >= k:
            continue
        for pattern in range(1 << len(pairs)):
            edges = base_edges + sum(column.bit_count() for column in selected) + pattern.bit_count()
            if not emin <= edges <= emax:
                continue
            graph = [mask | sum(((column >> vertex) & 1) << (size + index) for index, column in enumerate(selected))
                     for vertex, mask in enumerate(base)] + list(selected)
            for bit, (left, right) in enumerate(pairs):
                if (pattern >> bit) & 1:
                    graph[size + left] |= 1 << (size + right)
                    graph[size + right] |= 1 << (size + left)
            if any(not lo <= mask.bit_count() < k or not independent(mask, graph) for mask in graph[size:]):
                continue
            count = sum(1 for _ in independent_sets(graph, (1 << len(graph)) - 1, k))
            if best is None or count < best:
                best = count
                if best == 0:
                    return best
    return best


def audit_soft(args):
    core_lines = args.cores.read_text().splitlines()
    lines = args.summary.read_text().splitlines()
    assert lines[-1] == f'terminal rows={len(core_lines)} capped=0'
    by_row = {}
    with args.models.open() as stream:
        for record in csv.DictReader(stream, delimiter='\t'):
            index = int(record['row'])
            assert 0 <= index < len(core_lines) and index not in by_row
            graph = parse_graph6(record['graph6'])
            base = parse_graph6(core_lines[index])
            assert len(graph) == len(base) + args.poles and relabel(graph, range(len(base))) == base
            assert args.emin <= num_edges(graph) <= args.emax
            assert all(args.low <= mask.bit_count() < args.k and independent(mask, graph) for mask in graph)
            count = sum(1 for _ in independent_sets(graph, (1 << len(graph)) - 1, args.k))
            assert count == int(record['I_k']) <= args.ceiling
            by_row[index] = count
    brute_checked = positive = 0
    for index, (record, core_line) in enumerate(zip(csv.DictReader(lines[:-1], delimiter='\t'), core_lines, strict=True)):
        assert int(record['row']) == index
        assert record['status'] in ('complete', 'bad_core')
        if not args.clean_labels or args.brute:
            base = parse_graph6(core_line)
            is_bad = any(not independent(mask, base) for mask in base) or (
                not args.include_fixed and next(independent_sets(base, (1 << len(base)) - 1, args.k), None) is not None)
            assert (record['status'] == 'bad_core') == is_bad and (not is_bad or index not in by_row)
        else:
            assert record['status'] == 'complete'
        score = by_row.get(index)
        assert record['I_k'] == ('NA' if score is None else str(score))
        if args.brute:
            minimum = soft_brute(base, args.k, args.low, args.emin, args.emax, args.poles, args.include_fixed)
            assert score == (minimum if minimum is not None and minimum <= args.ceiling else None), (index, score, minimum)
            brute_checked += 1
            positive += minimum is not None and minimum > 0
        if not args.clean_labels or score is not None:
            print(f'row={index} score={score}', flush=True)
    print(f'PASS cores={len(core_lines)} emitted={len(by_row)} brute={brute_checked} brute_positive={positive}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='action', required=True)
    controls = modes.add_parser('prepare-controls')
    controls.add_argument('--add', type=int, choices=(2, 3, 4), default=3)
    anchor = modes.add_parser('prepare-anchor')
    anchor.add_argument('source', type=Path)
    anchor.add_argument('old', type=Path)
    anchor.add_argument('--add', type=int, choices=(2, 3, 4), default=3)
    anchor.add_argument('--prefix', default='anchor37')
    seeds = modes.add_parser('prepare-sources')
    seeds.add_argument('sources', type=Path, nargs='+')
    seeds.add_argument('--sample', type=int, default=128)
    project = modes.add_parser('prepare-projected')
    for name in ('close', 'pool', 'scores', 'outside'):
        project.add_argument(name, type=Path)
    project.add_argument('--limit', type=int, default=64)
    project.add_argument('--sample', type=int, default=256)
    check = modes.add_parser('audit')
    for name in ('cores', 'models', 'summary'):
        check.add_argument(name, type=Path)
    for name in ('add', 'k', 'low', 'emin', 'emax'):
        check.add_argument(name, type=int)
    check.add_argument('--witness', type=Path)
    check.add_argument('--sat', action='store_true')
    soft = modes.add_parser('audit-soft')
    for name in ('cores', 'models', 'summary'):
        soft.add_argument(name, type=Path)
    for name in ('k', 'low', 'emin', 'emax', 'ceiling'):
        soft.add_argument(name, type=int)
    soft.add_argument('--brute', action='store_true')
    soft.add_argument('--poles', choices=(2, 3, 4), type=int, default=2)
    soft.add_argument('--clean-labels', action='store_true', help='require complete labels; recount all witnesses, not every bare core')
    soft.add_argument('--include-fixed', action='store_true')
    args = parser.parse_args()
    if args.action == 'prepare-controls':
        prepare_controls(args.add)
    elif args.action == 'prepare-anchor':
        prepare_anchor(args.source, args.old, args.add, args.prefix)
    elif args.action == 'prepare-sources':
        prepare_sources(args.sources, args.sample)
    elif args.action == 'prepare-projected':
        prepare_projected(args.close, args.pool, args.scores, args.outside, args.limit, args.sample)
    elif args.action == 'audit-soft':
        audit_soft(args)
    else:
        audit(args)


if __name__ == '__main__':
    main()
