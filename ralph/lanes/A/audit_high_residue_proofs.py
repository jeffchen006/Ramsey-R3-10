#!/usr/bin/env python3
"""Bind the frozen upper residue proofs, distinguishing unpinned and exact e169."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from pysat.card import CardEnc

from audit_floor_covers import BIN, ROOT, clique_demands, digest, has_independent, require
from audit_residue_moves import checked_catalogue, expect_rejection
from residue_bundle import encode, formula, neighbors, parse_graph6, read_catalogue, triangle_free

LOWER = ROOT / 'scratch/A/root-residue/complete-v2/residues.g6'
G_CERTS = ROOT / 'ralph/lanes/G/root_certs'


def fixed_total(adj, degree, min_degree, cap, total):
    size = len(adj)
    edges = sum(map(int.bit_count, adj)) // 2
    exterior = neighbors(adj)
    private_cap = cap + 1 - degree
    cross_edges = total - edges - degree
    require(cross_edges == 2 * size - degree * private_cap, 'expected exact private-cell equality')
    columns = [tuple(part * size + vertex + 1 for vertex in range(size)) for part in range(degree)]
    clauses = []
    last = degree * size

    def add_bound(literals, lower, upper):
        nonlocal last
        if lower > upper or lower > len(literals) or upper < 0:
            clauses.append(())
            return
        if lower > 0:
            card = CardEnc.atleast(literals, bound=lower, top_id=last)
            last = max(last, card.nv)
            clauses.extend(card.clauses)
        if upper < len(literals):
            card = CardEnc.atmost(literals, bound=upper, top_id=last)
            last = max(last, card.nv)
            clauses.extend(card.clauses)

    for column in columns:
        for vertex, nbrs in enumerate(exterior):
            clauses.append((column[vertex], *(column[other] for other in sorted(nbrs))))
            clauses.extend((-column[vertex], -column[other]) for other in sorted(nbrs) if other > vertex)
        add_bound(column, min_degree - 1, cap - 1)
    by_vertex = list(zip(*columns))
    for cell, nbrs in zip(by_vertex, exterior):
        add_bound(cell, max(1, min_degree - len(nbrs)), min(2, cap - len(nbrs)))
    doubles = range(last + 1, last + 1 + size)
    last += size
    for cell, indicator in zip(by_vertex, doubles):
        clauses.extend((-first, -second, indicator) for first, second in combinations(cell, 2))
        clauses.extend((-indicator, -chosen, *(other for other in cell if other != chosen)) for chosen in cell)
    add_bound(tuple(doubles), cross_edges - size, cross_edges - size)
    for column in columns:
        private = range(last + 1, last + 1 + size)
        last += size
        for hit, double, alone in zip(column, doubles, private):
            clauses.extend(((-alone, hit), (-alone, -double), (-hit, double, alone)))
        add_bound(tuple(private), private_cap, private_cap)
    for first, second in combinations(range(size), 2):
        if second in exterior[first] or exterior[first] & exterior[second]:
            continue
        previous = last
        for column in columns:
            last += 1
            clauses.extend(((-last, column[first]), (-last, column[second])))
        clauses.append(tuple(range(previous + 1, last + 1)))
    return last, clauses, columns


def calibrate():
    from pysat.solvers import Cadical195

    order = 13
    adj = [sum(1 << ((vertex + offset) % order) for offset in (-5, -1, 1, 5))
           for vertex in range(order)]
    require(triangle_free(adj) and not has_independent(adj, 5) and has_independent(adj, 4),
            'bad C13 control')
    for root in range(order):
        nbrs = [vertex for vertex in range(order) if adj[root] >> vertex & 1]
        away = [vertex for vertex in range(order) if vertex != root and vertex not in nbrs]
        residual = [sum(1 << idx for idx, other in enumerate(away) if adj[vertex] >> other & 1)
                    for vertex in away]
        _, clauses, columns = fixed_total(residual, 4, 4, 4, 26)
        assumptions = [lit if adj[other] >> vertex & 1 else -lit
                       for other, column in zip(nbrs, columns) for vertex, lit in zip(away, column)]
        with Cadical195(bootstrap_with=clauses) as solver:
            require(solver.solve(assumptions=assumptions), 'C13 equality root falsified pinned CNF')
        if root == 0:
            expect_rejection(lambda: fixed_total(residual, 4, 4, 4, 27), 'private-cell equality')
    print('PASS actual attachments at all 13 C13 equality roots', flush=True)


def manifest(path):
    result = {}
    for line in path.read_text().splitlines():
        claimed, relative = line.split('  ')
        require(len(claimed) == 64 and all(digit in '0123456789abcdef' for digit in claimed)
                and relative not in result and not Path(relative).is_absolute() and '..' not in Path(relative).parts,
                f'bad manifest row: {line}')
        result[relative] = claimed
    return result


def partition(rows, clique_file, exceptional_file, scope):
    used = {}
    for line in clique_file.read_bytes().splitlines():
        ordinal, mask_field = line.split(b'\t')
        index = int(ordinal) - 1
        require(0 <= index < len(rows) and index not in used, 'bad or repeated partition index')
        masks = [int(token, 16) for token in mask_field.split()]
        require(clique_demands(parse_graph6(rows[index].decode('ascii')), masks, 6),
                f'bad clique demand at {scope}:{index + 1}')
        used[index] = ('clique-unpinned', masks)
    exceptions = []
    for line in exceptional_file.read_bytes().splitlines():
        ordinal, row = line.split(b'\t')
        index = int(ordinal) - 1
        require(0 <= index < len(rows) and index not in used and rows[index] == row,
                'bad or repeated partition index / exceptional graph6 mismatch')
        used[index] = ('exception', None)
        exceptions.append(row)
    require(len(used) == len(rows), f'missing partition member: {scope}')
    return used, exceptions


def partition_controls(source, work):
    rows = read_catalogue(source / 'strict120.s8.g6')
    cliques = (source / 's8.e120.cliq.tsv').read_bytes().splitlines(keepends=True)
    exceptions = source / 's8.e120.exception.tsv'
    with TemporaryDirectory(dir=work) as temporary:
        changed = Path(temporary) / 'cliques.tsv'
        changed.write_bytes(b''.join(cliques[:-1]))
        expect_rejection(lambda: partition(rows, changed, exceptions, 'omission'), 'missing partition member')
        changed.write_bytes(b''.join([cliques[0], *cliques]))
        expect_rejection(lambda: partition(rows, changed, exceptions, 'duplicate'), 'repeated partition index')
        ordinal, masks = cliques[0].split(b'\t')
        bad_mask = b' '.join([masks.split()[0]] * 7)
        changed.write_bytes(b''.join([ordinal + b'\t' + bad_mask + b'\n', *cliques[1:]]))
        expect_rejection(lambda: partition(rows, changed, exceptions, 'wrong mask'), 'bad clique demand')


def validate_model(top, clauses, model_file):
    records = model_file.read_bytes().splitlines()
    require(b's SATISFIABLE' in records, 'missing unpinned SAT model')
    values = [int(literal) for line in records if line.startswith(b'v ') for literal in line.split()[1:]]
    require(values and values[-1] == 0 and len(values) == top + 1, 'incomplete unpinned SAT model')
    assignment = set(values[:-1])
    require({abs(literal) for literal in assignment} == set(range(1, top + 1))
            and all(any(literal in assignment for literal in clause) for clause in clauses),
            'unpinned SAT model does not satisfy regenerated core')


def dual(cnf, proof, expected=True):
    for tool, verdict in (('lrat-check', b'c VERIFIED'), ('cake_lpr', b's VERIFIED UNSAT')):
        check = subprocess.run([str(BIN / tool), str(cnf), str(proof)], capture_output=True, timeout=25)
        accepted = check.returncode == 0 and verdict in check.stdout.splitlines()
        require(accepted == expected, f'{tool} unexpected verdict on {proof}')


def timed_sample(source, index, count):
    lines = index.read_text().splitlines()[1:]
    prefixes = [line.split('\t')[4] for line in lines if line.split('\t')[2] == 'lrat-unpinned']
    require(0 < count <= len(prefixes), 'invalid timing sample size')
    for offset in range(count):
        prefix = prefixes[offset * len(prefixes) // count]
        dual(source / f'{prefix}.cnf', source / f'{prefix}.lrat')
    print(f'PASS spread timing sample: {count} dual LRATs', flush=True)


def run(source, index_path, sample):
    outer = manifest(G_CERTS / 'e121_frozen.sha256')
    for name, claimed in outer.items():
        require(digest((source / name).read_bytes()) == claimed, f'frozen outer hash mismatch: {name}')
    inner = manifest(source / 'e121.frozen.sha256')
    lower_manifest = manifest(G_CERTS / 'e120_partial.sha256')
    require(all(inner.get(name) == claimed for name, claimed in lower_manifest.items() if name in inner),
            'conflicting manifest hashes')
    for name, claimed in (inner | lower_manifest).items():
        require(digest((source / name).read_bytes()) == claimed, f'row artifact hash mismatch: {name}')
    require(LOWER.read_bytes() == (G_CERTS / 'complete33_le119.g6').read_bytes(), 'lower catalogue changed')
    levels = [(120, 'strict120.s8.g6', 's8.e120', ['s8_e120_core'], 1223),
              (121, 'strict121.bridge8.g6', 'e121.bridge8', [f'e121_bridge8/in.{idx:02d}' for idx in range(10)], None),
              (121, 'e121.delta.rare.g6', 'e121.delta.rare', ['e121_delta_rare'], None),
              (121, 'e121.delta.last.g6', 'e121.delta.last', ['e121_delta_last'], None)]
    pinned = {}
    pinned_rows = read_catalogue(source / 'e121.core.sat.g6')
    for index, line in enumerate((source / 'e121.core.sat.tsv').read_bytes().splitlines(), 1):
        stem, unit, row = line.split(b'\t')
        old = f'{stem.decode()}/{unit.decode()}'
        require(old not in pinned and index <= len(pinned_rows) and pinned_rows[index - 1] == row,
                'pinned fallback row mismatch')
        pinned[old] = row, f'e121_e169/{index:04}'
    require(len(pinned) == len(pinned_rows) == 11, 'pinned fallback count mismatch')
    frozen_high, high_labels = checked_catalogue(source / 'e121.frozen.g6', 33, 8, {121: 13092})
    distinct = set()
    all_high = []
    counts = Counter()
    visited_pins = set()
    header = 'edge\tgraph6_sha256\tmethod\tinput_location\tproof_prefix\tcnf_sha256\tlrat_sha256\n'
    with index_path.open('w') as index, TemporaryDirectory(dir=index_path.resolve().parent) as tmp:
        index.write(header)
        regenerated = Path(tmp) / 'audit.cnf'
        for edge, name, stem, blocks, count in levels:
            rows = read_catalogue(source / name)
            require(count is None or len(rows) == count, f'wrong count: {name}')
            if edge == 120:
                checked_catalogue(source / name, 33, 8, {120: count})
            else:
                all_high += rows
            require(not distinct.intersection(rows), f'repeated labelled input: {name}')
            distinct.update(rows)
            split, exceptions = partition(rows, source / f'{stem}.cliq.tsv', source / f'{stem}.exception.tsv', stem)
            mapping = {}
            for block in blocks:
                if stem == 'e121.bridge8':
                    block_rows = read_catalogue(source / f'{block}.g6')
                else:
                    block_rows = read_catalogue(source / f'{stem}.exception.g6')
                for number, row in enumerate(block_rows, 1):
                    require(row not in mapping, 'duplicate exceptional input')
                    mapping[row] = f'{block}/{number:04}'
            require(list(mapping) == exceptions, 'shards do not match ordered exceptions')
            for ordinal, row in enumerate(rows, 1):
                method, masks = split[ordinal - 1]
                prefix = cnf_hash = proof_hash = '-'
                if masks is not None:
                    prefix = ' '.join(format(mask, 'x') for mask in masks)
                else:
                    old = mapping[row]
                    if old in pinned:
                        pin_row, prefix = pinned[old]
                        require(edge == 121 and pin_row == row, f'pinned labelled row changed: {old}')
                        require(f'{old}.lrat' not in inner, 'pinned was also indexed as unpinned')
                        visited_pins.add(old)
                        method = 'lrat-e169'
                    else:
                        prefix = old
                        method = 'lrat-unpinned'
                    hashes = lower_manifest if edge == 120 else inner
                    cnf_hash = hashes[f'{prefix}.cnf']
                    proof_hash = hashes[f'{prefix}.lrat']
                    graph = parse_graph6(row.decode('ascii'))
                    if method == 'lrat-e169':
                        untopped, unpinned_clauses, _ = formula(neighbors(graph), 6, 9)
                        unpinned = encode(untopped, unpinned_clauses)
                        require(unpinned == (source / f'{old}.cnf').read_bytes(), 'fallback core changed')
                        validate_model(untopped, unpinned_clauses, source / f'{old}.solve')
                        if len(visited_pins) == 1:
                            regenerated.write_bytes(unpinned)
                            dual(regenerated, source / f'{prefix}.lrat', expected=False)
                            print('PASS both checkers reject one e169 LRAT against its SAT unpinned core', flush=True)
                        top, clauses, _ = fixed_total(graph, 6, 6, 9, 169)
                    else:
                        top, clauses, _ = formula(neighbors(graph), 6, 9)
                    cnf = encode(top, clauses)
                    require(digest(cnf) == cnf_hash, f'independently regenerated CNF differs: {prefix}')
                    if sample == 0 or counts[(edge, method)] < sample or method == 'lrat-e169':
                        regenerated.write_bytes(cnf)
                        dual(regenerated, source / f'{prefix}.lrat')
                counts[(edge, method)] += 1
                print(edge, digest(row), method, f'{name}:{ordinal}', prefix, cnf_hash, proof_hash, sep='\t', file=index)
    require(visited_pins == set(pinned), 'unseen pinned fallback')
    require(len(high_labels) == len(all_high) == len(set(all_high)) and set(frozen_high) == set(all_high),
            'e121 clique/proof partitions do not equal frozen labelled set')
    require(counts == {(120, 'clique-unpinned'): 1157, (120, 'lrat-unpinned'): 66,
                       (121, 'clique-unpinned'): 10268, (121, 'lrat-unpinned'): 2813,
                       (121, 'lrat-e169'): 11}, f'proof scope count mismatch: {counts}')
    print(f'PASS {sorted(counts.items())}; dual replay sample={sample} (0 means all)', flush=True)
    print('PASS full SAT assignments for all 11 unpinned fallback cores', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('calibrate')
    audit = subs.add_parser('audit')
    audit.add_argument('source', type=Path)
    audit.add_argument('index', type=Path)
    audit.add_argument('--sample', type=int, default=3)
    timing = subs.add_parser('timing')
    timing.add_argument('source', type=Path)
    timing.add_argument('index', type=Path)
    timing.add_argument('--count', type=int, default=50)
    negatives = subs.add_parser('partition-controls')
    negatives.add_argument('source', type=Path)
    negatives.add_argument('work', type=Path)
    args = parser.parse_args()
    if args.command == 'calibrate':
        calibrate()
    elif args.command == 'timing':
        timed_sample(args.source.resolve(), args.index, args.count)
    elif args.command == 'partition-controls':
        partition_controls(args.source.resolve(), args.work.resolve())
    else:
        require(args.sample >= 0, 'negative sample size')
        run(args.source.resolve(), args.index, args.sample)


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        sys.exit(str(error))
