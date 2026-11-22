"""Publish open witnesses and a disjoint labelled successor frontier."""

import json
import sys
from collections import defaultdict
from pathlib import Path

from round24_plan import complement


def residual(stage, status, merger):
    opening = json.loads((stage / 'complement.json').read_text())
    whole = set(merger['whole'])
    exact = defaultdict(set)
    for receipt in status['r24_receipts'].values():
        if receipt['mode'] == 'DN':
            exact[str(receipt['board'])].update(map(str, receipt['key_ids']))
    output = {}
    for board, data in opening.items():
        if int(board) in whole:
            continue
        checked = status['proofs'].get(board, {})
        gaps = complement(checked)
        keys = {}
        for key, original in data['residual'].items():
            if key in exact[board]:
                continue
            words = [word for subset in original.values() for word in subset]
            if any(word.startswith(prefix) for word in words for prefix in checked):
                continue
            keys[key] = sorted(words)
        if not keys:
            continue
        members = {prefix: sorted(int(key) for key, words in keys.items() if any(word.startswith(prefix) for word in words))
                   for prefix in gaps}
        for words in keys.values():
            assert all(sum(word.startswith(prefix) for prefix in gaps) == 1 for word in words)
        assert set().union(*(set(options) for options in members.values())) == set(map(int, keys))
        output[board] = dict(raw_maximal_prefixes=gaps, keys=keys, prefixes_with_new_keys=members)
    assert sum(len(board['keys']) for board in output.values()) == merger['remaining_keys']
    return output


if __name__ == '__main__':
    stage, snapshot, merger = map(Path, sys.argv[1:])
    print(json.dumps(residual(stage, json.loads(snapshot.read_text()), json.loads(merger.read_text())),
                     separators=(',', ':')))
