"""Add an exact four-positive-literal exclusion for each nonchosen occupancy."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from itertools import combinations, product
from pathlib import Path

from round22_split import cnf_data
from round23_deficit import extended
from round23_deficit_audit import exact


def controls():
    from pysat.solvers import Solver
    occupancy = tuple(range(1, 9))
    holes = [left + right for left, right in product(combinations(occupancy[:4], 2), combinations(occupancy[4:], 2))]
    assert len(holes) == 36
    clauses = []
    for shore in (occupancy[:4], occupancy[4:]):
        for triple in combinations(shore, 3):
            clauses.extend([triple, tuple(-variable for variable in triple)])
    allowed = set(holes[3::5])
    with Solver(name='cadical195', bootstrap_with=clauses + [option for option in holes if option not in allowed]) as solver:
        for label in holes:
            assert solver.solve(assumptions=[-variable if variable in label else variable for variable in occupancy]) == (label in allowed)
    mutant = next(word for word in holes if word not in allowed)
    with Solver(name='cadical195', bootstrap_with=clauses + [word for word in holes if word not in allowed and word != mutant]) as solver:
        assert solver.solve(assumptions=[-variable if variable in mutant else variable for variable in occupancy])
    print(f'normalized exact projection control: {len(holes)} labelled populations, {len(allowed)} allowed, omitted-cut mutant accepted')


def row_data(scope, board, manifest):
    data = json.loads(scope.read_text())
    assert data['board'] == board
    allowed = set(data['keys'].values())
    target = json.loads(manifest.read_text())[board]
    assert data['keys'] and len(allowed) == len(data['keys'])
    assert all(0 <= int(key) < len(target['keys']) for key in data['keys'])
    return allowed


def emit(scope, board, manifest):
    allowed = row_data(scope, board, manifest)
    grid = json.loads(manifest.read_text())[board]['grid']
    fold, _ = extended(grid, '')
    keys = tuple((side, slot) for slot in (0, 1) for side in (0,)) + ((1, 0), (1, 1)) + tuple(
        (side, slot) for slot in range(2, 10) for side in (0, 1))
    holes = [set(pair) for pair in combinations(range(10), 2) if any(fold.pairs[i] & 1 for i in pair)]
    seen = set()
    for left, right in product(holes, repeat=2):
        absent = (left, right)
        code = ''.join('0' if slot in absent[side] else '1' for side, slot in keys)
        if code in allowed:
            seen.add(code)
        else:
            fold.add(tuple(fold.activity[side][slot] for side, slot in keys if slot in absent[side]),
                     'occupancy-representative')
    assert seen == allowed and len(holes) == 30
    fold.dump(sys.stdout)
    print(json.dumps(dict(board=board, grid=grid, prefix='', budget=False, counts=fold.counts,
                          variables=fold.variables, clauses=len(fold.rows),
                          manifest=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                          scope=hashlib.sha256(scope.read_bytes()).hexdigest())), file=sys.stderr)


def audit(scope, board, manifest, stage):
    allowed = row_data(scope, board, manifest)
    here = Path.cwd()
    current_variables, current = cnf_data(here / 'grid.cnf')
    data = json.loads(scope.read_text())
    entry = json.loads((stage / 'complement.json').read_text())[str(board)]
    for key, word in data['keys'].items():
        moves = sorted(word for label in entry['residual'][key].values() for word in label)
        assert word == moves[0]
    assert allowed <= {word for labels in entry['residual'].values() for chunks in labels.values() for word in chunks}
    bits = (1, 2, 14, 15, 3, 16, 4, 17, 5, 18, 6, 19, 7, 20, 8, 21, 9, 22, 10, 23)
    cross = ({1, 2, 3, 4}, {14, 15, 16, 17})
    all_left = [set(group) for group in combinations(range(1, 11), 2) if set(group) & cross[0]]
    all_right = [set(group) for group in combinations(range(14, 24), 2) if set(group) & cross[1]]
    expect = set()
    for left, right in product(all_left, all_right):
        zeros = left | right
        selector = ''.join('01'[item not in zeros] for item in bits)
        if selector not in allowed:
            expect.add(' '.join(map(str, [*sorted(zeros), 0])).encode())
    assert len(expect) == 900 - len(allowed)
    with tempfile.TemporaryDirectory(prefix='occupancy-rebind-', dir=here) as directory:
        os.chdir(directory)
        try:
            with Path('grid.cnf').open('w') as output, Path('binding.json').open('w') as binding:
                subprocess.run([sys.executable, '-B', Path(__file__).with_name('round23_deficit.py'), 'emit',
                                manifest, str(board), '-', '--deficit'], check=True, stdout=output, stderr=binding)
            exact(manifest, stage / '../round22/h5', board, '-', 'D')
            variables, original = cnf_data(Path('grid.cnf'))
            assert variables == current_variables and current == original | expect
        finally:
            os.chdir(here)
    print('normalized occupancy scope:', len(allowed), 'literal representatives;', len(expect), 'other words banned')


if __name__ == '__main__':
    if sys.argv[1:] == ['control']:
        controls()
        sys.exit(0)
    options = argparse.ArgumentParser()
    options.add_argument('action', choices=('emit', 'audit'))
    options.add_argument('manifest', type=Path)
    options.add_argument('scope', type=Path)
    options.add_argument('board', type=int)
    options.add_argument('stage', type=Path, nargs='?')
    args = options.parse_args()
    if args.action == 'emit':
        emit(args.scope, args.board, args.manifest)
    else:
        audit(args.scope.resolve(), args.board, args.manifest.resolve(), args.stage.resolve())
