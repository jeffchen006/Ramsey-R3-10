"""Harvest compact witnesses from completed SAT attempts, not live logs."""

import json
import os
import sys
from collections import Counter
from pathlib import Path

from round23_h5 import Physical, load_models
from round23_oracle import convert


def harvest(base):
    previous = base / '../round22/h5'
    records = json.loads((previous / 'manifest.json').read_text())
    fixtures = json.loads((base / '../../A/r23/physical.v2.json').read_text())
    pending = {}
    frequencies = Counter()

    def add(ident, physical, witness):
        row = physical.row(witness, 10)
        pending.setdefault(ident, {})[row] = witness

    for target in fixtures['targets']:
        ident = target['board']
        physical = Physical(records[ident]['grid'])
        for key in ('witness', 'repeated_witness'):
            add(ident, physical, convert(physical, target[key]))

    for directory in (previous, base):
        for folder in (directory / 'work').iterdir():
            result = folder / 'result'
            binding = folder / 'binding.json'
            if not result.exists() or 'SAT relaxation' not in result.read_text() or not binding.exists():
                continue
            ident = json.loads(binding.read_text())['board']
            physical = Physical(records[ident]['grid'])
            positive = load_models(folder / 'solve.log')
            witness, graph = physical.model_witness(positive, 10)
            if graph is not None:
                print(json.dumps(dict(board=ident, log=str(folder / 'solve.log'), graph=graph)), flush=True)
            else:
                add(ident, physical, witness)
                frequencies[directory.name] += 1
            more = folder / 'witness.jsonl'
            if more.exists():
                for line in more.read_text().splitlines():
                    add(ident, physical, json.loads(line))

    scratch = base / 'seeds-follow'
    scratch.mkdir(exist_ok=True)
    for ident, witnesses in pending.items():
        tmp = scratch / f'{ident}.tmp'
        with tmp.open('w') as output:
            for _, witness in sorted(witnesses.items()):
                output.write(json.dumps(witness, sort_keys=True) + '\n')
        os.replace(tmp, scratch / f'{ident}.jsonl')
    print(json.dumps(dict(boards=len(pending), witnesses=sum(map(len, pending.values())), processed=frequencies), sort_keys=True))


if __name__ == '__main__':
    harvest(Path(sys.argv[1]))
