"""Crosscheck the production shore generator on independent saved placements."""

import hashlib
import json
import sys
from itertools import islice
from pathlib import Path

from round22_control import unflatten
from round22_deep import projected_activity
from round22_three import ThreeDefect
from round23_h5 import Physical, load_models
from round23_deficit import extended
from round24_shore import projected, row

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'ralph/lanes/A'))
from physical_blocker23 import toy
from shore_blocker24 import projected as independent, with_activity


def main(stage):
    manifest = json.loads((stage / '../round22/h5/manifest.json').read_text())
    source = ROOT / 'scratch/A/r24'
    destination = stage / 'shore-seeds'
    destination.mkdir(exist_ok=True)
    for target in json.loads((source / 'targets.json').read_text()):
        board = target['board']
        fold, physical = extended(manifest[board]['grid'], target['prefix'])
        projected_fixture = target['witness']['projected']
        fixture = {key: projected_fixture[key] for key in ('side', 'coords', 'boundary')}
        folder = source / 'inputs' / 'work' / target['leaf']
        assert hashlib.sha256((folder / 'grid.cnf').read_bytes()).hexdigest() == target['formula_sha256']
        assignment = load_models(folder / 'solve.log')
        result = row(fold, physical, fixture)
        assert result == tuple(projected_fixture['clause'])
        assert all((lit not in assignment if lit > 0 else -lit in assignment) for lit in result)
        (destination / f'{board}.jsonl').write_text(json.dumps(fixture, sort_keys=True) + '\n')
        print(target['leaf'], 'exact signed row and falsified by saved model', *result)
    controls = ROOT / 'scratch/G/round22/h5/n17.d3.placements.jsonl'
    if not controls.exists():
        controls = next((ROOT / 'scratch/G/round22').rglob('n17.d3.placements.jsonl'))
    samples = json.loads((source / 'controls.json').read_text())
    seen = set()
    for line in islice(controls.open(), 1960):
        entry = json.loads(line)
        if entry['board'] in seen:
            continue
        seen.add(entry['board'])
        grid = unflatten(entry['board'], 3)
        model = ThreeDefect(grid, 3, False, bound=6)
        oracle = Physical(grid)
        assignment = projected_activity(model, entry)
        external, _, _, positives = toy(entry)
        full = with_activity(external, list(enumerate(entry['mates'])), positives)
        left_witness, _ = oracle.model_witness(assignment, 6)
        for fixture in projected(oracle, left_witness):
            raw = independent(external, fixture['side'], tuple(fixture['boundary']), tuple(fixture['coords']), 6)
            assert raw is not None and row(model, oracle, fixture) == tuple(raw['clause'])
            assert all((lit not in full if lit > 0 else -lit in full) for lit in raw['clause'])
    assert len(seen) == 16 and samples
    print('six fixed target models and two literal side rows on each of', len(seen), 'width-three boards')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
