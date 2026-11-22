"""Root-relative archive manifest for the accepted named 32/e108 inventory."""

import argparse
from collections import Counter
import csv
from hashlib import sha256
from pathlib import Path

from e108_r16_crosswalk import COHORTS, HEX, require


LANE = Path('ralph/lanes/B')
WORK = Path('scratch/B/work')
CROSSWALK = WORK / 'e108_r16/critical-crosswalk.tsv'


def add(entries, path, digest):
    require(not path.is_absolute() and '..' not in path.parts, f'not repository relative: {path}')
    require(HEX.fullmatch(digest.encode()), f'bad SHA256: {path}')
    require(path not in entries or entries[path] == digest, f'conflicting hashes: {path}')
    entries[path] = digest


def verify(root, entries):
    byte_count = 0
    for path, expected in entries.items():
        digest = sha256()
        with (root / path).open('rb') as stream:
            for block in iter(lambda: stream.read(1024**2), b''):
                digest.update(block)
            byte_count += stream.tell()
        require(digest.hexdigest() == expected, f'changed bytes: {path}')
    return byte_count


def from_manifest(path, relative_to=Path()):
    entries = {}
    for row in path.read_text().splitlines():
        digest, name = row.split(maxsplit=1)
        add(entries, relative_to / name, digest)
    return entries


def freeze(name):
    relative_to = Path('scratch/B') if name == 'ROUND6_REPLAY.sha256' else Path()
    return from_manifest(LANE / name, relative_to)


def select(entries, manifest, paths):
    for path in paths:
        add(entries, path, manifest[path])


def receipts(entries, base, expected, modern):
    names = set()
    with (base / ('proofs.tsv' if modern else 'replay.log')).open() as stream:
        for row in stream:
            fields = row.split()
            if not modern and fields[0] == 'counts':
                require(int(fields[1]) == expected and not stream.read(), f'bad footer: {base}')
                break
            rank, digest = (fields[1], fields[3]) if modern else (fields[0], fields[2])
            path = base / 'proofs' / f'{int(rank):07d}.lrat'
            require(path not in names, f'duplicate receipt: {path}')
            names.add(path)
            add(entries, path, digest)
        else:
            require(modern, f'missing footer: {base}')
    require(len(names) == expected, f'wrong receipt count: {base}')
    return names


def prepare():
    entries = {}
    for number in (11, 14, 15, 16):
        manifest = freeze(f'ROUND{number}.sha256')
        verify(Path(), {path: manifest[path] for path in {
            11: [WORK / 'e108_r11/critical.g6'],
            14: [WORK / 'e108_r14/proofs.tsv', WORK / 'e108_r14/lrats.sha256'],
            15: [WORK / 'e108_r6_unit/replay.log'],
            16: [CROSSWALK],
        }[number]})
        if number == 11:
            select(entries, manifest, (WORK / 'e108_r11' / name for name in ('union.g6', 'critical.g6')))
        elif number == 14:
            old = WORK / 'e108_r14'
            select(entries, manifest, [WORK / 'e108_r5/reducible.g6', WORK / 'e108_r14_replay/replay.tsv',
                                      *(old / name for name in ('input.g6', 'cliques.tsv', 'complement.tsv',
                                        'pins.tsv', 'source-ids.tsv', 'pilot-overlap.tsv', 'proofs.tsv', 'lrats.sha256')),
                                      *(WORK / 'e108_r6_pilot' / name for name in ('input.g6', 'clique.cliq.tsv',
                                        'clique.missing.tsv', 'pins.tsv'))])
            payloads = receipts(entries, old, 1361, modern=True)
            frozen_payloads = from_manifest(old / 'lrats.sha256')
            require(payloads == frozen_payloads.keys(), 'round-14 payload list differs from receipt')
            select(entries, frozen_payloads, payloads)
        elif number == 15:
            packed = WORK / 'e108_r15'
            names = ('adopted.tsv', 'residual.u32', 'rank-dispositions.tsv', 'summary.json', 'unchecked-ranks.txt')
            select(entries, manifest, [*(packed / name for name in names),
                                      *(packed / f's{shard:03d}' / name for shard in range(257)
                                        for name in ('cliques.tsv', 'proofs.tsv', 'proofs.pack', 'done.json')),
                                      *(WORK / 'e108_r6_unit' / name for name in ('production.log', 'replay.log'))])
            receipts(entries, WORK / 'e108_r6_unit', 173, modern=False)
        else:
            select(entries, manifest, [CROSSWALK])

    expected = {cohort.name: cohort for cohort in COHORTS}
    cohort_manifests = {name: freeze(name) for name in {cohort.freeze for cohort in COHORTS}}
    counts = Counter()
    via_crosswalk = Counter()
    for cohort in COHORTS:
        base = WORK / cohort.directory
        select(entries, cohort_manifests[cohort.freeze], [WORK / cohort.input,
            *(base / name for name in (cohort.cliques, cohort.complement, 'pins.tsv', 'production.log', 'replay.log'))])
    with CROSSWALK.open(newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            cohort = expected[row['cohort']]
            if row['kind'] == 'clique':
                require(row['pins_line'] == row['payload'] == '-', 'wrong clique fields')
                counts['clique'] += 1
                continue
            require(row['kind'] == 'LRAT' and int(row['pins_line']) >= 0, 'unbound critical key')
            counts['pinned' if int(row['pins_line']) else 'unpinned'] += 1
            path = WORK / cohort.directory / 'proofs' / row['payload']
            require(path.name == f"{int(row['input_rank']):07d}.lrat", 'wrong critical payload rank')
            add(entries, path, row['lrat_sha256'])
            if path in cohort_manifests[cohort.freeze]:
                select(entries, cohort_manifests[cohort.freeze], [path])
            else:
                via_crosswalk[cohort.name] += 1
    require(counts == {'clique': 1431, 'pinned': 430, 'unpinned': 14}, f'wrong critical counts: {counts}')
    print(f'critical archive: {dict(sorted(counts.items()))}')
    print(f'payload hashes supplied by confirmed crosswalk only: {dict(sorted(via_crosswalk.items()))}')
    return entries


def control(fixture, root):
    manifest = from_manifest(fixture)
    require(manifest.keys() == {Path('pins'), Path('unpinned')} and verify(root, manifest) == 2,
            'two labelled controls not intact')
    for label, paths in [('missing pins', ['pins-missing', 'unpinned']),
                         ('swapped pins', ['unpinned', 'pins'])]:
        entries = {Path(first): manifest[Path(second)] for first, second in zip(paths, ['pins', 'unpinned'], strict=True)}
        try:
            verify(root, entries)
        except (FileNotFoundError, ValueError):
            print(f'control {label}: rejected')
        else:
            raise ValueError(f'control {label}: not rejected')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'check', 'control'))
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root', type=Path, default=Path())
    args = parser.parse_args()
    if args.mode == 'control':
        control(args.manifest, args.root)
        return
    entries = prepare() if args.mode == 'prepare' else from_manifest(args.manifest)
    size = verify(args.root, entries)
    if args.mode == 'prepare':
        with args.manifest.open('x') as stream:
            stream.writelines(f'{digest}  {path}\n' for path, digest in sorted(entries.items()))
    print(f'archive hashes OK: {len(entries)} files ({size} bytes)')


if __name__ == '__main__':
    main()
