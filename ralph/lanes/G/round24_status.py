"""Freeze checked local receipts, then recompute whole-board and orbit coverage."""

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from round23_h5_status import covered


def sha(path):
    with path.open('rb') as file:
        digest = hashlib.sha256()
        for block in iter(lambda: file.read(1 << 22), b''):
            digest.update(block)
        return digest.hexdigest()


def scan(root, stage, out, hash_archive=True):
    prior = json.loads((stage / 'incoming.json').read_text())
    manifest = stage / '../round22/h5/manifest.json'
    mh = sha(manifest)
    boards = json.loads(manifest.read_text())
    checked = prior['proofs']
    delta = {}
    terminal = {}
    pending = []
    billed = Counter()
    all_hashes = []
    for folder in sorted((stage / 'work').iterdir()):
        if not (folder / 'job').exists() or not (folder / 'result').exists():
            pending.append(folder.name)
            continue
        outcome = (folder / 'result').read_text().strip()
        board, scope, mode, ident = (folder / 'job').read_text().split()
        assert ident == folder.name
        number, prefix = int(board), '' if scope == '-' else scope
        terminal[ident] = dict(board=number, prefix=prefix, mode=mode, result=outcome)
        for path in folder.glob('*.time'):
            for raw in path.read_text().splitlines():
                fields = raw.split()
                if len(fields) == 5 and fields[0][0].isdigit():
                    billed['cpu_hundredths'] += round(100 * (float(fields[0]) + float(fields[1])))
                    billed['peak_rss_kib'] = max(billed['peak_rss_kib'], int(fields[2]))
        if (folder / 'raw.bytes').exists():
            billed['raw_bytes'] += int((folder / 'raw.bytes').read_text())
        if not outcome.startswith('CHECKED '):
            continue
        assert outcome == f'CHECKED {board} {scope} {mode} {ident}'
        binding = json.loads((folder / 'binding.json').read_text())
        assert binding['manifest'] == mh and binding['grid'] == boards[number]['grid']
        assert (binding['board'], binding['prefix'], binding['budget']) == (number, prefix, False)
        assert 'physical addresses checked; exact delta' in (folder / 'audit.log').read_text()
        assert 'independent deficit input/output binding' in (folder / 'audit.log').read_text()
        assert 'c VERIFIED' in (folder / 'lrat.log').read_text().splitlines()
        assert 's VERIFIED UNSAT' in (folder / 'cake.log').read_text().splitlines()
        lines = [line.split() for line in (folder / 'sha256').read_text().splitlines()]
        assert len(lines) == 3 and lines[0][1] == 'grid.cnf' and lines[1][1] == 'grid.lrat'
        proof = stage / 'archive' / f'{ident}.lrat.zst'
        assert Path(lines[2][1]).resolve() == proof.resolve()
        assert sha(folder / 'grid.cnf') == lines[0][0]
        if hash_archive:
            assert sha(proof) == lines[2][0]
        if 'M' in mode:
            assert sha(folder / 'witness.jsonl') == binding['witnesses']
        if 'P' in mode:
            assert sha(folder / 'shore.jsonl') == binding['shore']
            assert 'physical shore projections: exact delta' in (folder / 'audit.log').read_text()
        if 'N' in mode:
            assert sha(folder / 'scope.json') == binding['scope']
            assert 'normalized occupancy scope:' in (folder / 'audit.log').read_text()
        assert int((folder / 'archived.bytes').read_text()) == proof.stat().st_size
        billed['proof_bytes'] += proof.stat().st_size
        all_hashes += [f'{lines[2][0]}  {proof.relative_to(root)}']
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.name not in ('solve.log', 'learn.log'):
                all_hashes.append(f'{sha(path)}  {path.relative_to(root)}')
        delta[ident] = dict(board=number, prefix=prefix, mode=mode, cnf=lines[0][0],
                            ascii=lines[1][0], packed=lines[2][0])
        if 'N' in mode:
            delta[ident]['key_ids'] = sorted(map(int, json.loads((folder / 'scope.json').read_text())['keys']))
        else:
            checked.setdefault(board, {}).setdefault(prefix, []).append(ident)
    old = set(prior['added'])
    new = {int(board) for board, prefixes in checked.items() if covered(prefixes)} - old
    whole_gain = sum(len(boards[number]['keys']) for number in new)
    prior.update(timestamp=datetime.now().astimezone().isoformat(timespec='seconds'),
                 board_count=prior['board_count'] + len(new),
                 boards_open=sorted(set(prior['boards_open']) - new),
                 added=sorted(old | new), key_count=prior['key_count'] + whole_gain,
                 new_complete=sorted(new), whole_gain=whole_gain, r24_receipts=delta,
                 r24_terminal=terminal, r24_pending=pending, r24_totals=dict(billed))
    out.write_text(json.dumps(prior, sort_keys=True, indent=1) + '\n')
    out.with_suffix('.sha256').write_text('\n'.join(all_hashes) + '\n')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[3]
    scan(root, Path(sys.argv[1]).resolve(), Path(sys.argv[2]), '--quick' not in sys.argv[3:])
