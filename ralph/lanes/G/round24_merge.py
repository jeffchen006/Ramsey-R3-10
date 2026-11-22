"""Anti-join normalized receipts with checked prefix orbits, preserving both scopes."""

import json
import sys
from pathlib import Path


def merge(stage, status, holes):
    manifest = json.loads((stage / '../round22/h5/manifest.json').read_text())
    census = json.loads((stage / 'complement.json').read_text())
    original = set(holes['whole'])
    covered = {int(board): set(map(int, keys)) for board, keys in holes['partial_keys'].items()}
    unique = {}
    for name, proof in status['r24_receipts'].items():
        if proof['mode'] != 'DN':
            continue
        number = proof['board']
        if number in original:
            continue
        previous = covered.setdefault(number, set())
        new = set(proof['key_ids']) - previous
        assert new <= set(map(int, census[str(number)]['residual']))
        previous.update(new)
        if new:
            unique[name] = sorted(new)
    full = original | {board for board, keys in covered.items() if len(keys) == len(manifest[board]['keys'])}
    total = holes['key_count'] + sum(map(len, unique.values()))
    return dict(raw_boards=status['board_count'], raw_keys=status['key_count'], orbit_boards=len(full),
                total_keys=total, remaining_keys=156112 - total, normalized_gain=unique,
                whole=sorted(full), remaining_per_board={str(item['id']): len(item['keys']) - len(covered.get(item['id'], ()))
                                                        for item in manifest if item['id'] not in full})


if __name__ == '__main__':
    stage, state, orbit = map(Path, sys.argv[1:])
    print(json.dumps(merge(stage, json.loads(state.read_text()), json.loads(orbit.read_text())), sort_keys=True))
