"""Count only independently rebound checked LRATs and complete prefix covers."""

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def covered(prefixes, prefix=''):
    if prefix in prefixes:
        return True
    if not any(item.startswith(prefix) for item in prefixes):
        return False
    return all(covered(prefixes, prefix + digit) for digit in '01')


def process_view(base):
    ids = {int(line.split()[0]) for path in base.glob('*.pids') for line in path.read_text().splitlines()
           if line.split() and line.split()[0].isdigit()}
    process_data = {}
    children = defaultdict(list)
    sample = subprocess.check_output(['ps', '-eo', 'pid=,ppid=,stat=,cputimes=,args='], text=True, errors='replace')
    for line in sample.splitlines():
        cols = line.split(None, 4)
        if len(cols) != 5 or not cols[0].isdigit() or not cols[1].isdigit() or not cols[3].isdigit():
            continue
        ident, parent, cpu = map(int, (cols[0], cols[1], cols[3]))
        children[parent].append(ident)
        process_data[ident] = (cpu, cols[2], cols[4])
    live = {}
    for root in sorted(ids):
        if (root not in process_data or not any(worker in process_data[root][2] for worker in
                ('round23_h5_worker.sh', 'round23_binary_worker.sh')) or process_data[root][1][0] == 'Z'):
            continue
        forest = [root]
        for ident in forest:
            forest.extend(children[ident])
        live[root] = dict(cpu=sum(process_data[node][0] for node in forest), stat=process_data[root][1],
                          args=process_data[root][2], children=[(node, *process_data[node]) for node in forest[1:]])
    return live


def sample(base):
    baseline = json.loads((base / 'baseline.json').read_text())
    raw = (base / '../round22/h5/manifest.json').read_bytes()
    manifest = json.loads(raw)
    manifest_hash = hashlib.sha256(raw).hexdigest()
    assert manifest_hash == baseline['manifest']
    proofs = defaultdict(dict)
    terminal = {}
    pending = {}
    totals = Counter()
    for folder in sorted((base / 'work').iterdir()):
        state = folder / 'result'
        job = folder / 'job'
        if not job.exists() or not job.read_text().strip():
            continue
        ident, prefix, mode, name = job.read_text().split()
        ident = int(ident)
        prefix = '' if prefix == '-' else prefix
        assert name == folder.name
        for path in folder.glob('*.time'):
            for line in path.read_text().splitlines():
                cols = line.split()
                if len(cols) == 5 and cols[0][0].isdigit():
                    totals['cpu_hundredths'] += int(round(100 * (float(cols[0]) + float(cols[1]))))
                    totals['peak_rss_kib'] = max(totals['peak_rss_kib'], int(cols[2]))
        row = dict(board=ident, prefix=prefix, mode=mode)
        if not state.exists() or not state.read_text().strip():
            pending[name] = row
            continue
        row['result'] = state.read_text().strip()
        terminal[name] = row
        for field in ('raw.bytes', 'archived.bytes'):
            path = folder / field
            if path.exists():
                totals[field] += int(path.read_text())
        if not row['result'].startswith('CHECKED '):
            continue
        binding = json.loads((folder / 'binding.json').read_text())
        assert binding['manifest'] == manifest_hash and binding['grid'] == manifest[ident]['grid']
        assert (binding['board'], binding['prefix'], binding['budget']) == (ident, prefix, 'B' in mode)
        assert 'physical addresses checked; exact delta' in (folder / 'audit.log').read_text()
        assert 'c VERIFIED' in (folder / 'lrat.log').read_text().splitlines()
        assert 's VERIFIED UNSAT' in (folder / 'cake.log').read_text().splitlines()
        archive = base / 'archive' / (name + '.lrat.zst')
        assert int((folder / 'archived.bytes').read_text()) == archive.stat().st_size
        expected = (folder / 'sha256').read_text().splitlines()
        assert len(expected) == 3 and expected[-1].endswith(archive.name)
        proofs[ident].setdefault(prefix, []).append(name)
    new = sorted(number for number, places in proofs.items() if covered(places))
    old = set(map(int, baseline['reviewed']))
    assert not old.intersection(new)
    total = old.union(new)
    exact_bill = int(subprocess.check_output(['du', '-sb', str(base)], text=True).split()[0])
    return dict(timestamp=datetime.now().astimezone().isoformat(timespec='seconds'), original=len(old),
                added=new, board_count=len(total), key_count=sum(len(manifest[ix]['keys']) for ix in total),
                boards_open=sorted(set(range(len(manifest))) - total), totals=dict(totals),
                proofs=dict(proofs), terminal=terminal, pending=pending, live=process_view(base), stage_bytes=exact_bill)


if __name__ == '__main__':
    print(json.dumps(sample(Path(sys.argv[1])), indent=1, sort_keys=True))
