"""Independently reconstruct the exterior saturation input and exact CNF delta."""

import json
import os
import shutil
import sys
from pathlib import Path

from round22_split import cnf_data
from round23_deficit_audit import exact
from round23_h5_audit import literals
from round23_mtf import encode


def validate(manifest, past, ident, prefix, mode):
    grid = json.loads(manifest.read_text())[ident]['grid']
    maximum, rows = cnf_data(Path('grid.cnf'))
    edges, selectors, supports = literals(grid)
    source = [{anchor - 7 for anchor in supports[index][1]} for index in range(17)]
    bins = [(slot + 1, [(guard, {anchor - 7 for anchor in supports[pair][1]})
                        for pair, guard in selectors.items() if pair[0] == slot]) for slot in range(13)]
    size, _ = encode(maximum, source, bins, dict(edges), 5)
    prior = 2 * maximum - size
    actual, generated = encode(prior, source, bins, dict(edges), 5)
    assert actual == maximum
    addition = set(' '.join(map(str, (*sorted(set(clause)), 0))).encode() for clause in generated)
    assert addition <= rows
    delta = {row for row in addition if any(abs(int(number)) > prior for number in row.split())}
    prior_rows = rows - delta
    directory = Path.cwd()
    stage = directory / 'saturation-rebind'
    stage.mkdir()
    try:
        os.chdir(stage)
        with Path('grid.cnf').open('wb') as output:
            output.write(f'p cnf {prior} {len(prior_rows)}\n'.encode())
            for clause in sorted(prior_rows):
                output.write(clause + b'\n')
        if 'M' in mode:
            Path('witness.jsonl').symlink_to(directory / 'witness.jsonl')
        exact(manifest, past, ident, prefix, mode)
    finally:
        os.chdir(directory)
        shutil.rmtree(stage)
    print('physical exterior maximality delta:', len(delta), 'clauses')


if __name__ == '__main__':
    manifest, past, ident, prefix, mode = sys.argv[1:]
    validate(Path(manifest), Path(past), int(ident), prefix, mode)
