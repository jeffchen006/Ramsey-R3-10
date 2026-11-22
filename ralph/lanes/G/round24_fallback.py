"""Resume key-bearing cylinders after the successor supervisor exits."""

import json
import subprocess
import sys
import time
from pathlib import Path

from round24_plan import complement
from round24_status import scan
from round24_supervise import supervise


def active_pid(ident, token):
    proc = subprocess.run(['ps', '-p', str(ident), '-o', 'stat=,args='], text=True, capture_output=True)
    text = proc.stdout.strip()
    return text and text[0] != 'Z' and token in text


def active_child(stage):
    for logfile in stage.glob('*.events.jsonl'):
        records = [json.loads(line) for line in logfile.read_text().splitlines()]
        ended = {item['id'] for item in records if item['event'] == 'exit'}
        for item in records:
            if item['event'] == 'launch' and item['id'] not in ended and active_pid(item['pid'], item['id']):
                return True
    return False


def generate(stage, snapshot):
    original = json.loads((stage / 'complement.json').read_text())
    queue = []
    explicit = {}
    for receipt in snapshot['r24_receipts'].values():
        if receipt['mode'] == 'DN':
            explicit.setdefault(receipt['board'], set()).update(map(str, receipt['key_ids']))
    for board in snapshot['boards_open']:
        proofs = snapshot['proofs'].get(str(board), {})
        residual = []
        for key, coded in original[str(board)]['residual'].items():
            if key in explicit.get(board, set()):
                continue
            words = [word for values in coded.values() for word in values]
            if not any(word.startswith(proof) for proof in proofs for word in words):
                residual.append(words)
        for prefix in complement(proofs):
            nodes = [prefix]
            for _ in range(2):
                refined = []
                for node in nodes:
                    mass = sum(word.startswith(node) for words in residual for word in words)
                    if mass:
                        refined.extend([node] if mass <= 50 or len(node) >= 11 else [node + sign for sign in '01'])
                nodes = refined
            for node in nodes:
                credit = sum(any(word.startswith(node) for word in words) for words in residual)
                if credit:
                    queue.append(dict(id=f'f{board:03}_{node or "all"}', board=board, prefix=node, parent=prefix,
                                      keys=credit, mode='DM', generation=2, budget=[96_000_000, 44_000_000, 130, 80]))
        assert all(any(word.startswith(item['prefix']) for item in queue if item['board'] == board)
                   for words in residual for word in words)
    return sorted(queue, key=lambda row: (-row['keys'], row['board'], row['prefix']))


def main(stage, preceding):
    while active_pid(preceding, 'round24_successor.py') or active_child(stage):
        time.sleep(5)
    snapshot = stage / 'before-fallback.json'
    scan(stage.parents[2], stage, snapshot, hash_archive=False)
    queue = stage / 'fallback.json'
    plan = generate(stage, json.loads(snapshot.read_text()))
    queue.write_text(json.dumps(plan, indent=2) + '\n')
    print('Fallback exact residual scopes:', len(plan), flush=True)
    if plan:
        supervise(stage, 16, 5100, 'fallback', queue)


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve(), int(sys.argv[2]))
