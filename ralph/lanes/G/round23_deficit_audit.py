"""Rebuild the deficit instances from literal, independently addressed sites."""

import json
import os
import shutil
import sys
from pathlib import Path

from round22_split import cnf_data
from round23_deficit import encode
from round23_h5_audit import audit, literals


def exact(manifest, previous, board, prefix, mode):
    assert 'D' in mode and 'B' not in mode
    grid = json.loads(manifest.read_text())[board]['grid']
    origin = 'p285' if board == 285 else f'b{board:03}'
    old, _ = cnf_data(previous / 'work' / origin / 'grid.cnf')
    actual, present = cnf_data(Path('grid.cnf'))
    edges, selectors, contacts = literals(grid)
    count = len([key for key in contacts if isinstance(key, int)])
    descriptions = []
    for vertex in range(count + 13):
        incident = tuple(literal for pair, literal in edges if vertex in pair)
        if vertex < count:
            descriptions.append((incident, 0, [(7, 2, ())]))
        else:
            left = vertex - count
            cases = []
            for allowed in (5, 6):
                gates = [gate for pair, gate in selectors.items() if pair[0] == left and
                         sum(map(len, contacts[pair])) == 9 - allowed]
                if gates:
                    cases.append((allowed, 1, gates))
            descriptions.append((incident, left + 1, cases))
    assert count == 17
    expected, additions = encode(old, descriptions, 8)
    audit_rows = set(' '.join(map(str, (*sorted(set(row)), 0))).encode() for row in additions)
    assert expected == actual and audit_rows <= present
    assert all(any(abs(int(number)) > old for number in row.split()) for row in audit_rows)
    remaining = present - audit_rows
    if prefix != '-' and len(prefix) > 2:
        units = [14, 15, *[literal for place in range(3, 11) for literal in (place, place + 13)]]
        for literal, sign in zip(units, prefix[2:]):
            unit = f'{literal if sign == "1" else -literal} 0'.encode()
            assert unit in remaining
            remaining.remove(unit)
        prefix = prefix[:2]
    here = Path.cwd()
    temp = here / 'deficit-rebind'
    temp.mkdir()
    try:
        os.chdir(temp)
        with Path('grid.cnf').open('wb') as reduced:
            reduced.write(f'p cnf {old} {len(remaining)}\n'.encode())
            for row in sorted(remaining):
                reduced.write(row + b'\n')
        if 'M' in mode:
            Path('witness.jsonl').symlink_to(here / 'witness.jsonl')
        audit(manifest, previous, board, prefix, mode.replace('D', ''))
    finally:
        os.chdir(here)
        shutil.rmtree(temp)
    print('independent deficit input/output binding:', len(audit_rows), 'clauses')


if __name__ == '__main__':
    manifest, previous, ident, prefix, mode = sys.argv[1:]
    exact(Path(manifest), Path(previous), int(ident), prefix, mode)
