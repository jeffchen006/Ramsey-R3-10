#!/usr/bin/env python3
"""Bind fixed degree-six residue LRATs to independently rebuilt DIMACS files."""

import argparse
from collections import Counter
from gzip import compress, decompress
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import alpha, parse_graph6, to_graph6, triangle_free


HEADER = 'row\tedges\tgraph6_sha256\tdimacs_sha256\tlrat_sha256\n'


def neighbors(adj):
    return [{other for other in range(len(adj)) if mask >> other & 1} for mask in adj]


def formula(residual, degree, alpha_cap):
    size = len(residual)
    verts = range(size)

    def variable(part, vertex):
        return part * size + vertex + 1

    clauses = []
    for part in range(degree):
        for vertex in verts:
            present = variable(part, vertex)
            clauses.append((present, *(variable(part, other) for other in sorted(residual[vertex]))))
            for other in sorted(residual[vertex]):
                if other > vertex:
                    clauses.append((-present, -variable(part, other)))
    for vertex in verts:
        occurrences = tuple(variable(part, vertex) for part in range(degree))
        clauses.append(occurrences)
        capacity = alpha_cap - len(residual[vertex])
        if capacity < 0:
            clauses.append(())
        else:
            clauses.extend(combinations((-literal for literal in occurrences), capacity + 1))
    top = degree * size
    aux = []
    for first, second in combinations(verts, 2):
        if second in residual[first] or residual[first] & residual[second]:
            continue
        group = []
        for part in range(degree):
            top += 1
            group.append(top)
            aux.append((top, variable(part, first), variable(part, second)))
            clauses += [(-top, variable(part, first)), (-top, variable(part, second))]
        clauses.append(tuple(group))
    return top, clauses, aux


def encode(top, clauses):
    records = [f'p cnf {top} {len(clauses)}\n']
    records.extend(' '.join(map(str, (*clause, 0))) + '\n' for clause in clauses)
    return ''.join(records).encode('ascii')


def calibration(census):
    count = 0
    for row in census.read_text().splitlines():
        graph = parse_graph6(row)
        if not all(mask.bit_count() == 6 for mask in graph):
            continue
        if len(graph) != 22 or not triangle_free(graph) or alpha(graph) != 6:
            raise ValueError('invalid (3,7,22) control graph')
        local = neighbors(graph)
        for root, attachments in enumerate(local):
            exterior = sorted(set(range(22)) - {root} - attachments)
            induced = [{index for index, other in enumerate(exterior) if other in local[vertex]}
                       for vertex in exterior]
            top, clauses, aux = formula(induced, 6, 6)
            assignment = [False] + [other in local[vertex]
                                    for vertex in sorted(attachments) for other in exterior]
            for index, first, second in aux:
                if index != len(assignment):
                    raise ValueError('auxiliary ordering mismatch')
                assignment.append(assignment[first] and assignment[second])
            if len(assignment) != top + 1 or not all(
                    any(assignment[abs(literal)] == (literal > 0) for literal in clause)
                    for clause in clauses):
                raise ValueError(f'planted root {root} falsified a clause')
            count += 1
    if count != 220:
        raise ValueError('wrong control census count')
    print(f'PASS positive substitution at {count} rooted controls')


def read_catalogue(path):
    lines = path.read_bytes().splitlines()
    if not lines or len(lines) != len(set(lines)):
        raise ValueError('empty or duplicated labelled input')
    return lines


def residue(line):
    adj = parse_graph6(line.decode('ascii'))
    edges = sum(mask.bit_count() for mask in adj) // 2
    if (len(adj) != 33 or edges not in (118, 119) or to_graph6(adj).encode('ascii') != line
            or not triangle_free(adj) or alpha(adj) > 8):
        raise ValueError('invalid fixed residue')
    top, clauses, _ = formula(neighbors(adj), 6, 9)
    return edges, encode(top, clauses)


def index_line(index, edges, line, cnf, proof):
    digests = '\t'.join(sha256(item).hexdigest() for item in (line, cnf, proof))
    return f'{index:04d}\t{edges}\t{digests}'


def pack(catalogue, source, bundle):
    lines = read_catalogue(catalogue)
    bundle.mkdir()
    summary = Counter()
    index_rows = [HEADER.strip()]
    for index, line in enumerate(lines, 1):
        edges, cnf = residue(line)
        if cnf != (source / f'{index:04d}.cnf').read_bytes():
            raise ValueError(f'{index:04d}: retained and reconstructed CNFs differ')
        proof = (source / f'{index:04d}.lrat').read_bytes()
        index_rows.append(index_line(index, edges, line, cnf, proof))
        (bundle / f'{index:04d}.lrat.gz').write_bytes(compress(proof, compresslevel=6, mtime=0))
        summary[edges] += 1
    (bundle / 'residues.g6').write_bytes(catalogue.read_bytes())
    (bundle / 'index.tsv').write_text('\n'.join(index_rows) + '\n', encoding='ascii')
    print(f'Packed {dict(sorted(summary.items()))}; all retained DIMACS files match independently')


def replay(bundle, bin_dir, select):
    lines = read_catalogue(bundle / 'residues.g6')
    index_rows = (bundle / 'index.tsv').read_text(encoding='ascii').splitlines(keepends=True)
    if not index_rows or index_rows[0] != HEADER or len(index_rows) != len(lines) + 1:
        raise ValueError('bad index header or length')
    if select is not None and not 1 <= select <= len(lines):
        raise ValueError('selected row is not in the catalogue')
    counts = Counter()
    with TemporaryDirectory(prefix='replay-', dir=Path.cwd()) as folder:
        cnf_path, lrat_path = Path(folder) / 'residue.cnf', Path(folder) / 'residue.lrat'
        for index, line in enumerate(lines, 1):
            if select is not None and index != select:
                continue
            edges, cnf = residue(line)
            proof = decompress((bundle / f'{index:04d}.lrat.gz').read_bytes())
            if index_rows[index] != index_line(index, edges, line, cnf, proof) + '\n':
                raise ValueError(f'{index:04d}: residue/CNF/LRAT binding mismatch')
            cnf_path.write_bytes(cnf)
            lrat_path.write_bytes(proof)
            for tool, verdict in (('lrat-check', 'c VERIFIED'), ('cake_lpr', 's VERIFIED UNSAT')):
                proc = subprocess.run([str(bin_dir / tool), str(cnf_path), str(lrat_path)],
                                      capture_output=True, text=True, timeout=25)
                if proc.returncode or verdict not in proc.stdout.splitlines():
                    raise ValueError(f'{index:04d}: {tool} rejected: {proc.stdout}\n{proc.stderr}')
            counts[edges] += 1
            print(f'PASS {index:04d} e={edges} bound to both LRAT checks')
    print(f'PASS counts by edge number: {dict(sorted(counts.items()))}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    calibration_parser = commands.add_parser('calibrate')
    calibration_parser.add_argument('census', type=Path)
    pack_parser = commands.add_parser('pack')
    pack_parser.add_argument('catalogue', type=Path)
    pack_parser.add_argument('source', type=Path)
    pack_parser.add_argument('bundle', type=Path)
    replay_parser = commands.add_parser('replay')
    replay_parser.add_argument('bundle', type=Path)
    replay_parser.add_argument('--bin', required=True, type=Path)
    replay_parser.add_argument('--row', type=int)
    args = parser.parse_args()
    if args.action == 'calibrate':
        calibration(args.census)
    elif args.action == 'pack':
        pack(args.catalogue, args.source, args.bundle)
    else:
        replay(args.bundle, args.bin.resolve(), args.row)


if __name__ == '__main__':
    main()
