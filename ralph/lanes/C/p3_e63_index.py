"""Audit the e63 graph6 census, boundary reversal, and checked proof inventory."""

import argparse
import ast
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path

from p3_e63 import boundary_keys, boundary_masks


REPRESENTATIVES = [0, 1, 2, 3, 6, 7, 9, 12]
CENSUS_DIGEST = '228d886ee01b3003d90c768af57804954f7adccbca901a3eeb3c69ccc020e8c5'


def residue_rows(path):
    assert sha256(path.read_bytes()).hexdigest() == CENSUS_DIGEST
    lines = path.read_text().splitlines()
    assert len(set(lines)) == len(lines) == 191
    rows = {}
    for row, line in enumerate(lines):
        assert len(line) == 40 and ord(line[0]) - 63 == 22
        digits = ''.join(f'{ord(symbol)-63:06b}' for symbol in line[1:])
        assert digits[231:] == '000'
        positions = [(low, high) for high in range(22) for low in range(high)]
        edges = {edge for edge, bit in zip(positions, digits) if bit == '1'}
        if len(edges) != 63:
            continue
        neighbours = [set() for _ in range(22)]
        for low, high in edges:
            neighbours[low].add(high)
            neighbours[high].add(low)
        assert all(not neighbours[low] & neighbours[high] for low, high in edges)

        def independent(nodes, size):
            if size == 0:
                return True
            while len(nodes) >= size:
                vertex = nodes.pop()
                if independent(nodes.difference(neighbours[vertex]), size - 1):
                    return True
            return False

        assert not independent(set(range(22)), 7)
        rows[row] = sha256(line.encode()).hexdigest()
    assert len(rows) == 60
    return rows


def audit_reflection(expected_file):
    line = next(line for line in expected_file.read_text().splitlines() if line.startswith('f 18 orbits 13 keys '))
    expected = ast.literal_eval(line.split(' keys ', 1)[1])
    assert boundary_keys() == expected
    graphs = [boundary_masks(key) for key in expected]
    pairs = list(combinations(range(18), 2))
    edge_sets = [{(low, high) for low, high in pairs if masks[low] >> high & 1} for masks in graphs]
    for edges in edge_sets:
        assert len(edges) == 27 + 18
    reflections = []
    for source in edge_sets:
        matches = set()
        for left_wing in permutations((3, 4, 5)):
            for right_wing in permutations((0, 1, 2)):
                for middle in ((13, 14), (14, 13)):
                    mapping = (*left_wing, *right_wing, 6, 7, 8, 9, 10, 12, 11, *middle, 17, 16, 15)
                    reflected = {tuple(sorted((mapping[low], mapping[high]))) for low, high in source}
                    matches.update(index for index, edges in enumerate(edge_sets) if reflected == edges)
        assert len(matches) == 1
        reflections.append(matches.pop())
    assert [index for index, reflected in enumerate(reflections) if index <= reflected] == REPRESENTATIVES
    print('PASS thirteen boundary keys match earlier exact audit; edge-by-edge reflections', reflections)


def read_rows(path):
    mode = None
    terminal = []
    for line in path.read_text().splitlines():
        if line.startswith('row '):
            fields = line.split()
            assert fields[2] == 'checked' and len(fields) == 11, (path, line)
            yield int(fields[1]), tuple(fields[3:9])
        elif line.startswith('TERMINAL '):
            terminal.append(line)
    assert len(terminal) == 1 and "'checked':" in terminal[0], path


def audit_proofs(args, rows):
    checked = {}
    for orbit in REPRESENTATIVES:
        pilot = args.work / f'p3e63-minpilot-{orbit}.log'
        pilot_end = pilot.read_text().split('WRAPPER lite6 0', 1)[0]
        record = [line.split() for line in pilot_end.splitlines() if line.startswith('row ')]
        assert len(record) == 1 and record[0][2] == 'checked'
        pilot_row, pilot_fields = int(record[0][1]), tuple(record[0][3:9])
        produced = list(read_rows(args.work / f'p3e63-full-{orbit}.log'))
        produced.append((pilot_row, pilot_fields))
        assert len(produced) == len(rows) and {row for row, _ in produced} == set(rows)
        if args.replay:
            replayed = list(read_rows(args.work / f'p3e63-replay-{orbit}.log'))
            assert sorted(replayed) == sorted(produced), orbit
        for row, fields in produced:
            var_count, clause_count, row_hash, cnf_hash, lrat_hash, size = fields
            assert int(var_count) > 0 and int(clause_count) > 0
            assert row_hash == rows[row]
            assert all(len(key) == 64 and all(symbol in '0123456789abcdef' for symbol in key)
                       for key in (cnf_hash, lrat_hash))
            proof = args.work / 'p3e63-minproofs' / f'{orbit:02d}-lite6-{row:03d}.lrat'
            assert proof.stat().st_size == int(size)
            assert (orbit, row) not in checked
            checked[(orbit, row)] = fields
    assert len(checked) == 480
    print('PASS 480 exact checked keys (60 residues x 8 boundary classes); replay:', args.replay)
    if args.output:
        args.output.write_text(''.join('\t'.join(map(str, (*key, *value))) + '\n'
                                      for key, value in sorted(checked.items())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--coverage-only', action='store_true')
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = residue_rows(args.census)
    audit_reflection(args.work / 'p3boundary-e63.log')
    print('PASS sixty independent graph6 residue rows; expected exact cover differentiates', len(rows) * 8, 'keys')
    if not args.coverage_only:
        audit_proofs(args, rows)


if __name__ == '__main__':
    main()
