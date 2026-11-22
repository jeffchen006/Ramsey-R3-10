"""Audit the exact two-shore formula delta using A's independent layout."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from round22_split import cnf_data
from round23_deficit_audit import exact

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'ralph/lanes/A'))
from physical_blocker23 import Layout
from shore_blocker24 import projected


def as_cnf(clause):
    return ' '.join(map(str, (*clause, 0))).encode()


def check(manifest, previous, board, prefix, mode):
    here = Path.cwd()
    nv, actual = cnf_data(here / 'grid.cnf')
    layout = Layout(json.loads(manifest.read_text())[board]['grid'])
    assert 'D' in mode and 'P' in mode
    additions = set()
    for line in (here / 'shore.jsonl').read_text().splitlines():
        item = json.loads(line)
        fixture = projected(layout, item['side'], tuple(item['boundary']), tuple(item['coords']), 10)
        assert fixture is not None
        additions.add(as_cnf(fixture['clause']))
    assert additions <= actual
    with tempfile.TemporaryDirectory(prefix='shore-rebind-', dir=here) as temporary:
        os.chdir(temporary)
        try:
            args = [sys.executable, '-B', Path(__file__).with_name('round23_deficit.py'), 'emit',
                    manifest, str(board), prefix, '--deficit']
            if 'M' in mode:
                Path('witness.jsonl').symlink_to(here / 'witness.jsonl')
                args += ['--witnesses', here / 'witness.jsonl']
            with Path('grid.cnf').open('w') as formula, Path('binding.json').open('w') as binding:
                subprocess.run(args, stdout=formula, stderr=binding, check=True)
            exact(manifest, previous, board, prefix, mode.replace('P', ''))
            base_nv, base = cnf_data(Path('grid.cnf'))
            assert nv == base_nv and actual == base | additions
        finally:
            os.chdir(here)
    print('physical shore projections: exact delta', len(actual - base), 'from', len(additions), 'validated rows')


if __name__ == '__main__':
    manifest, previous, board, prefix, mode = sys.argv[1:]
    check(Path(manifest).resolve(), Path(previous).resolve(), int(board), prefix, mode)
