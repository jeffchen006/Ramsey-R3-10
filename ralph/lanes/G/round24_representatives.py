"""Plan exact covers by physical key, independent of proof-side slot choices."""

import json
import sys
from pathlib import Path


def plan(stage, status_path, count_per_board=160, omit=()):
    input_cover = json.loads((stage / 'complement.json').read_text())
    status = json.loads(status_path.read_text())
    scopes = stage / 'representatives'
    scopes.mkdir(exist_ok=True)
    jobs = []
    for board, payload in input_cover.items():
        if int(board) in omit:
            continue
        witnesses = list(status['proofs'].get(board, {}))
        candidates = []
        for ident, labels_by_prefix in payload['residual'].items():
            labelled = sorted(word for labels in labels_by_prefix.values() for word in labels)
            if any(word.startswith(prefix) for word in labelled for prefix in witnesses):
                continue
            assert labelled
            candidates.append((int(ident), labelled[0]))
        assert len({word for _, word in candidates}) == len(candidates)
        for start in range(0, len(candidates), count_per_board):
            chosen = dict(candidates[start:start + count_per_board])
            name = f'k{int(board):03}_{start // count_per_board:02}'
            scope = dict(board=int(board), keys=chosen, parent_snapshot=status_path.name)
            path = scopes / f'{name}.json'
            if (stage / 'work' / name).exists():
                continue
            path.write_text(json.dumps(scope, separators=(',', ':')) + '\n')
            jobs.append(dict(id=name, board=int(board), prefix='', parent='', mode='DN', keys=len(chosen), labels=len(chosen)))
    assert len({row['id'] for row in jobs}) == len(jobs)
    return sorted(jobs, key=lambda row: (row['keys'], row['board'], row['id']))


if __name__ == '__main__':
    stage, snapshot, outfile = map(Path, sys.argv[1:])
    jobs = plan(stage, snapshot)
    outfile.write_text(json.dumps(jobs, indent=2) + '\n')
    print(len(jobs), 'non-overlapping representative scopes covering', sum(row['keys'] for row in jobs), 'keys')
