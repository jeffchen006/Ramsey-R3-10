"""Bind stitch receipts to a partition of the finite parent inventory."""

from collections import Counter
from csv import DictReader
from hashlib import sha256
from pathlib import Path
import re
import sys


def unique_keys(path):
    lines = path.read_bytes().splitlines(keepends=True)
    assert all(line.endswith(b'\n') for line in lines), path
    assert lines == sorted(set(lines)), path
    return set(lines)


def write_keys(path, keys):
    path.write_bytes(b''.join(sorted(keys)))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def table(path):
    with path.open() as source:
        records = list(DictReader(source, delimiter='\t'))
    indexed = {record['id']: record for record in records}
    assert len(records) == len(indexed), path
    return indexed


def main(out, source, base):
    plan, done = (table(out / name) for name in ('plan.tsv', 'done.tsv'))
    assert done.keys() <= plan.keys()
    inventory = unique_keys(source / 'total.98.fresh')
    known = unique_keys(source / 'deck.known_r10r11')
    conservative = unique_keys(source / 'deck.conservative_only')
    assert (len(inventory), len(known), len(conservative)) == (7954, 471, 745)
    assert len(inventory | known | conservative) == 9170
    assert inventory | known | conservative == unique_keys(source / 'total.98.g6')
    excluded = unique_keys(source / 'excluded98.g6')
    assert excluded & (inventory | known | conservative) == known | conservative
    origins = {origin: unique_keys(out / f'{origin}.pool')
               for origin in ('old-only', 'scout', 'shared', 'frontier')}
    assert origins['old-only'] | origins['shared'] == unique_keys(source / 'old.98.fresh')
    assert origins['scout'] | origins['shared'] == unique_keys(source / 'scout_other.98.fresh')
    assert origins['frontier'] == unique_keys(source / 'frontier.98.fresh') - (origins['old-only'] | origins['scout'] | origins['shared'])
    listed, target_tested, adaptive_tested, all_keys, all_new = (set() for _ in range(5))
    counts = Counter()
    for ident, record in plan.items():
        origin = record['origin']
        parents_path = out / (ident + '.parents')
        parents = unique_keys(parents_path)
        assert digest(parents_path) == record['key_sha256']
        assert len(parents) == int(record['parents'])
        if ident.startswith('target.'):
            assert parents <= origins[origin] and not parents & excluded
        else:
            assert ident.startswith('adapt.') and not parents & (inventory | excluded)
            assert parents <= unique_keys(out / f'{origin}.fresh')
        assert not listed & parents
        listed |= parents
        if ident not in done:
            continue
        receipt = done[ident]
        assert receipt['origin'] == origin and receipt['parents'] == record['parents']
        assert receipt['parent_sha256'] == record['key_sha256']
        for degree in (7, 8):
            count_out = int(receipt[f'd{degree}_raw'])
            with (out / f'{ident}.{degree}.raw').open('rb') as raw:
                assert sum(1 for _ in raw) == count_out
            log = (out / f'{ident}.{degree}.log').read_text()
            assert re.fullmatch(rf'inputs {len(parents)} d {degree} roots \d+ anchors \d+ viable \d+ nodes \d+ legalminimal \d+ critical {count_out}\n', log)
            counts[origin, f'd{degree}'] += count_out
        key_path = out / f'{ident}.keys'
        keys = unique_keys(key_path)
        novel = unique_keys(out / f'{ident}.new')
        assert novel <= keys
        assert len(keys) == int(receipt['keys']) and digest(key_path) == receipt['key_sha256']
        all_keys |= keys
        all_new |= novel
        counts[origin, 'parents'] += len(parents)
        if ident.startswith('target.'):
            target_tested |= parents
        else:
            adaptive_tested |= parents
    assert listed & inventory == inventory
    with (base / 'union.g6').open('rb') as old:
        intersection = {line for line in old if line in all_keys}
    assert all_keys - intersection == all_new == unique_keys(out / 'novel.g6')
    write_keys(out / 'target.tested', target_tested)
    write_keys(out / 'target.remaining', inventory - target_tested)
    write_keys(out / 'adaptive.tested', adaptive_tested)
    write_keys(out / 'produced.keys', all_keys)
    for origin in sorted({origin for origin, _ in counts}):
        print(origin, ' '.join(f'{label}={counts[origin, label]}' for label in ('parents', 'd7', 'd8')))
    print(f'PASS target {len(target_tested)}/{len(inventory)}; adaptive {len(adaptive_tested)}; '
          f'known-tested {len(known)}; set aside {len(conservative)}; '
          f'{len(all_keys)} output keys; {len(all_new)} novel')


if __name__ == '__main__':
    main(*map(Path, sys.argv[1:]))
