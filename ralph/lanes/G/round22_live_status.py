"""Snapshot complete worker receipts without rereading live proof files."""

from collections import Counter
from pathlib import Path
import hashlib
import json
import sys


def publish(base):
    manifest_path = base / 'manifest.json'
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    digest = hashlib.sha256(raw_manifest).hexdigest()
    reviewed = {}
    unresolved = {}
    attempt_cpu = 0.0
    archived = 0
    raw = 0
    maximum_rss = 0
    for folder in sorted((base / 'work').iterdir()):
        receipt = folder / 'result'
        if not receipt.exists():
            continue
        state = receipt.read_text().strip()
        if not state:
            continue
        for clock in folder.glob('*.time'):
            lines = clock.read_text().splitlines()
            if lines:
                user, kernel, rss = lines[-1].split()[:3]
                attempt_cpu += float(user) + float(kernel)
                maximum_rss = max(maximum_rss, int(rss))
        raw_size = folder / 'raw.bytes'
        if raw_size.exists():
            raw += int(raw_size.read_text())
        if not state.startswith('CHECKED '):
            unresolved[folder.name] = state
            continue
        data = json.loads((folder / 'binding.json').read_text())
        ident = data['board']
        assert data['manifest'] == digest and data['grid'] == manifest[ident]['grid'] and data['split'] is None
        assert ident not in reviewed
        assert 'c VERIFIED' in (folder / 'lrat.log').read_text().splitlines()
        assert 's VERIFIED UNSAT' in (folder / 'cake.log').read_text().splitlines()
        proof = base / 'archive' / (folder.name + '.lrat.zst')
        size = proof.stat().st_size
        assert int((folder / 'archived.bytes').read_text()) == size
        archived += size
        reviewed[ident] = dict(receipt=folder.name, checked_bytes=size, context_keys=len(manifest[ident]['keys']))
    covered = set(reviewed)
    print(json.dumps(dict(reviewed=reviewed, unresolved=unresolved,
                          open_counts=Counter(unresolved.values()), board_count=len(covered),
                          boards_open=sorted(set(range(len(manifest))) - covered),
                          context_keys=sum(data['context_keys'] for data in reviewed.values()),
                          cpu_seconds=round(attempt_cpu, 2), peak_rss_kib=maximum_rss, raw_reported=raw,
                          checked_archive_bytes=archived, manifest=digest), indent=1, sort_keys=True))


if __name__ == '__main__':
    publish(Path(sys.argv[1]))
