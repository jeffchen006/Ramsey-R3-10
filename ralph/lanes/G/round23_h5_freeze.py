"""Freeze an immutable accepted h5 snapshot without copying proof storage."""

import hashlib
import json
import sys
from pathlib import Path

from round22_control import ROOT


def freeze(snapshot):
    base = snapshot.parent.resolve()
    baseline = json.loads((base / 'baseline.json').read_text())
    fixed = json.loads(snapshot.read_text())
    root = ROOT.resolve()
    files = [snapshot.resolve(), base / 'baseline.json', base / '../round22/h5/manifest.json']
    selected = set()
    for board, prefixes in fixed['proofs'].items():
        for prefix, receipts in prefixes.items():
            for receipt in receipts:
                job = base / 'work' / receipt
                data = fixed['terminal'][receipt]
                assert (data['board'], data['prefix']) == (int(board), prefix)
                assert data['result'].startswith('CHECKED ')
                files.extend(job / item for item in ('job', 'binding.json', 'result', 'audit.log', 'lrat.log', 'cake.log', 'sha256'))
                files.extend(job.glob('witness.jsonl'))
                hashed = (job / 'sha256').read_text().splitlines()
                (encoded, filename), (_, proofname), (proof, archive) = (line.split(None, 1) for line in hashed)
                assert (filename, proofname) == ('grid.cnf', 'grid.lrat')
                assert hashlib.sha256((job / filename).read_bytes()).hexdigest() == encoded
                assert Path(archive).resolve() == (base / 'archive' / (receipt + '.lrat.zst')).resolve()
                print(f'{encoded}  {(job / filename).relative_to(root)}')
                print(f'{proof}  {Path(archive).resolve().relative_to(root)}')
                selected.add(receipt)
    assert len(selected) == sum(data['result'].startswith('CHECKED ') for data in fixed['terminal'].values())
    assert fixed['original'] == baseline['board_count']
    for artifact in sorted(set(files)):
        print(f'{hashlib.sha256(artifact.read_bytes()).hexdigest()}  {artifact.resolve().relative_to(root)}')


if __name__ == '__main__':
    freeze(Path(sys.argv[1]))
