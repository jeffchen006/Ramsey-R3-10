#!/usr/bin/env python3
"""Independently bind the already accepted degree-six and degree-seven covers."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from residue_bundle import (alpha, encode, formula, neighbors, parse_graph6, read_catalogue,
                            residue, to_graph6, triangle_free)


ROOT = Path(__file__).resolve().parents[3]
BIN = ROOT / 'opt/bin'
LEVELS = {104: ('canon32_e104.g6', 39, 0), 105: ('e105.add.g6', 952, 1),
          106: ('e106.add.g6', 18598, 67)}
GROUPS = {104: (), 105: (('e105.exception.g6', 'e105_exception_core', 1),),
          106: tuple((f'e106.exception.part.{part:02d}', f'e106_exception_core.{part:02d}', count)
                     for part, count in enumerate((23, 22, 22)))}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def canonical(lines):
    proc = subprocess.run([str(BIN / 'labelg'), '-q'], input=b'\n'.join(lines) + b'\n',
                          capture_output=True, check=True, timeout=40)
    labels = proc.stdout.splitlines()
    require(len(labels) == len(lines) == len(set(labels)), 'canonical count mismatch')
    return labels


def root6(certs, previous, bundle):
    old = read_catalogue(previous / 'residues.g6')
    all_rows = read_catalogue(bundle / 'residues.g6')
    extra = read_catalogue(certs / 'new119.g6')
    require((certs / 'complete33_le119.g6').read_bytes() == (bundle / 'residues.g6').read_bytes(),
            'complete ordered source and bundle differ')
    require(Counter(residue(row)[0] for row in old) == {118: 5, 119: 63}, 'old edge census mismatch')
    require(Counter(residue(row)[0] for row in extra) == {119: 6}, 'six added rows are not all e119')
    edges = [residue(row)[0] for row in all_rows]
    require(Counter(edges) == {118: 5, 119: 69}, 'complete edge census mismatch')
    old_labels, extra_labels, all_labels = (canonical(lines) for lines in (old, extra, all_rows))
    official_min = canonical(read_catalogue(certs / 'hog33_118.g6'))
    require({label for label, edge in zip(all_labels, edges) if edge == 118} == set(official_min),
            'minimum-level reference differs')
    require(not (set(old_labels) & set(extra_labels)), 'added class in old snapshot')
    origin = {label: ('retained-v1', index, row)
              for index, (label, row) in enumerate(zip(old_labels, old), 1)}
    origin.update({label: ('new119', index, row)
                   for index, (label, row) in enumerate(zip(extra_labels, extra), 1)})
    require(set(origin) == set(all_labels), 'canonical union does not match complete cover')
    old_index = (previous / 'index.tsv').read_text().splitlines()[1:]
    new_index = (bundle / 'index.tsv').read_text().splitlines()[1:]
    added = dict(reversed(line.split()) for line in
                 (certs / 'e119_new/dimacs_lrat.sha256').read_text().splitlines())
    require(len(old_index) == len(old) and len(new_index) == len(all_rows) and len(added) == 12,
            'proof index lengths mismatch')
    print('row\tedges\tinput\tinput_row\tidentical_labels\tcanonical_sha256')
    for index, (row, edge, label) in enumerate(zip(all_rows, edges, all_labels), 1):
        name, source_row, raw = origin[label]
        fields = new_index[index - 1].split('\t')[1:]
        require(row == raw and fields[1] == digest(row), f'raw labelled input changed at {index}')
        if name == 'retained-v1':
            unchanged = fields == old_index[source_row - 1].split('\t')[1:]
        else:
            unchanged = fields[2:] == [added[f'{source_row:04d}.{kind}'] for kind in ('cnf', 'lrat')]
        require(unchanged, f'retained proof binding changed at {index}')
        print(index, edge, name, source_row, int(raw == row), digest(label), sep='\t')


def has_independent(adj, target):
    """Clique decision in the complement, using greedy color upper bounds."""
    vertices = (1 << len(adj)) - 1
    complement = [vertices ^ (1 << vertex) ^ nbrs for vertex, nbrs in enumerate(adj)]

    def visit(active, needed):
        if needed == 1:
            return bool(active)
        if active.bit_count() < needed:
            return False
        order = []
        remaining = active
        colors = 0
        while remaining:
            colors += 1
            uncolored = remaining
            while uncolored:
                bit = uncolored & -uncolored
                vertex = bit.bit_length() - 1
                order.append((colors, bit, vertex))
                remaining ^= bit
                uncolored &= ~(bit | complement[vertex])
        for color, bit, vertex in reversed(order):
            if color < needed:
                return False
            if visit(active & complement[vertex], needed - 1):
                return True
            active ^= bit
        return False

    return visit(vertices, target)


def positions(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def clique_demands(adj, masks, degree):
    if len(masks) != degree + 1 or len(set(masks)) != len(masks):
        return False
    neighbor_unions = []
    for mask in masks:
        if not 0 < mask < 1 << len(adj) or mask.bit_count() > 2:
            return False
        ends = tuple(positions(mask))
        union = adj[ends[0]]
        if len(ends) == 2:
            if union & ((1 << ends[1]) | adj[ends[1]]):
                return False
            union |= adj[ends[1]]
        neighbor_unions.append(union)
    return all(neighbor_unions[left] & masks[right] for left, right in combinations(range(len(masks)), 2))


def control(census):
    lines = read_catalogue(census)
    require(len(canonical(lines)) == 191, 'control catalogue mismatch')
    require(canonical(lines[:10][::-1]) == canonical(lines[:10])[::-1], 'labelg reordered input')
    count = 0
    mtf = 0
    pairs = 0
    for row in lines:
        adj = parse_graph6(row.decode('ascii'))
        require(len(adj) == 22 and triangle_free(adj) and alpha(adj) == 6, 'bad C22 control')
        require(has_independent(adj, 6) and not has_independent(adj, 7), 'alpha disagrees on C22')
        count += 1
        if not all(mask.bit_count() == 6 for mask in adj):
            continue
        for root, attached in enumerate(adj):
            exterior = [vertex for vertex in range(len(adj)) if vertex != root and not attached >> vertex & 1]
            exterior_mask = sum(1 << vertex for vertex in exterior)
            for first, second in combinations(exterior, 2):
                if not adj[first] & ((1 << second) | (adj[second] & exterior_mask)):
                    require(adj[first] & adj[second] & attached, 'C22 uncovered pair not attached')
                    pairs += 1
            require(all(adj[vertex] & attached for vertex in exterior), 'C22 singleton not attached')
            mtf += 1
    require((count, mtf) == (191, 220), 'incorrect C22 control counts')
    require(pairs > 0, 'C22 pair control was vacuous')
    edge_and_isolate = [2, 1, 0]
    require(clique_demands(edge_and_isolate, [1, 2], 1), 'valid demands rejected')
    require(not clique_demands(edge_and_isolate, [1, 3], 1), 'edge mistaken for uncovered pair')
    require(not clique_demands(edge_and_isolate, [1, 4], 1), 'missing conflict accepted')
    print(f'PASS C22: 191 alpha cross-checks, 220 planted MTF roots, {pairs} uncovered pairs, '
          'and three demand controls')


def root7(source, level, sample):
    name, count, missing_count = LEVELS[level]
    catalogue = source / name
    lines = read_catalogue(catalogue)
    require(len(lines) == count, f'e{level}: published count mismatch')
    canonical(lines)
    trace = source / f'e{level}.cliq.tsv'
    provided = {}
    for record in trace.read_text().splitlines():
        index, *masks = record.split()
        index = int(index)
        require(1 <= index <= count and index not in provided, 'bad or repeated trace index')
        provided[index] = tuple(int(mask, 16) for mask in masks)
    residual = [(index, row) for index, row in enumerate(lines, 1) if index not in provided]
    manifest = b''.join(f'{index}\t'.encode() + row + b'\n' for index, row in residual)
    require(len(residual) == missing_count and manifest == (source / f'e{level}.unproved.tsv').read_bytes(),
            f'e{level}: exception complement mismatch')
    selected = range(count) if not sample else [index * count // sample for index in range(sample)]
    for slot in selected:
        row = lines[slot]
        adj = parse_graph6(row.decode('ascii'))
        require(len(adj) == 32 and to_graph6(adj).encode() == row
                and sum(mask.bit_count() for mask in adj) == 2 * level and triangle_free(adj)
                and not has_independent(adj, 9), f'e{level}: bad graph at row {slot + 1}')
        if slot + 1 in provided:
            require(clique_demands(adj, provided[slot + 1], 7), f'e{level}: invalid demands at row {slot + 1}')
    print(f'PASS e{level}: {len(selected)}/{count} graph/demand checks, '
          f'{len(provided)} indexed witnesses, {missing_count} exceptions; '
          f'ordered graph6 SHA-256 {digest(catalogue.read_bytes())}', flush=True)
    cursor = 0
    with TemporaryDirectory(prefix='root7-', dir=Path.cwd()) as folder:
        result = Path(folder) / 'recomputed.cnf'
        for input_name, proof_dir, size in GROUPS[level]:
            group = residual[cursor:cursor + size]
            group_input = source / input_name
            require(group_input.read_bytes() == b''.join(row + b'\n' for _, row in group),
                    f'wrong order/content in {input_name}')
            cursor += size
            for ordinal, (index, row) in enumerate(group, 1):
                if sample and ordinal != 1:
                    continue
                adj = parse_graph6(row.decode('ascii'))
                top, clauses, _ = formula(neighbors(adj), 7, 9)
                cnf = encode(top, clauses)
                key = source / proof_dir / f'{ordinal:04d}'
                require(key.with_suffix('.cnf').read_bytes() == cnf, f'{key}: independent CNF differs')
                result.write_bytes(cnf)
                proof = key.with_suffix('.lrat')
                verdicts = []
                for tool, verdict in (('lrat-check', b'c VERIFIED'), ('cake_lpr', b's VERIFIED UNSAT')):
                    proc = subprocess.run([str(BIN / tool), str(result), str(proof)],
                                          capture_output=True, timeout=30)
                    require(proc.returncode == 0 and verdict in proc.stdout.splitlines(),
                            f'{tool} rejected {key}: {proc.stdout!r} {proc.stderr!r}')
                    verdicts.append(verdict.decode())
                print('LRAT', level, index, f'{proof_dir}/{ordinal:04d}', digest(row), digest(cnf),
                      digest(proof.read_bytes()), *verdicts, sep='\t', flush=True)
        require(cursor == len(residual), f'e{level}: incomplete proof index')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    six = commands.add_parser('root6')
    six.add_argument('certs', type=Path)
    six.add_argument('previous', type=Path)
    six.add_argument('bundle', type=Path)
    seven = commands.add_parser('root7')
    seven.add_argument('source', type=Path)
    seven.add_argument('level', type=int, choices=LEVELS)
    seven.add_argument('--sample', type=int)
    cal = commands.add_parser('calibrate')
    cal.add_argument('census', type=Path)
    args = parser.parse_args()
    if args.command == 'root6':
        root6(args.certs, args.previous, args.bundle)
    elif args.command == 'root7':
        require(args.sample is None or 0 < args.sample <= LEVELS[args.level][1], 'invalid sample size')
        root7(args.source.resolve(), args.level, args.sample)
    else:
        control(args.census)


if __name__ == '__main__':
    main()
