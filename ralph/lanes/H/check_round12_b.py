"""Bind the completed B queue and the frozen e108 supply, not lift semantics."""

from collections import Counter
from csv import DictReader
from hashlib import sha256
from check_round11_receipts import WORK, check_delta, main as check_round11


def ordered_keys(path):
    data = path.read_bytes()
    keys = data.splitlines()
    assert (not data or data.endswith(b'\n')) and all(a < b for a, b in zip(keys, keys[1:]))
    return set(keys), sha256(data).hexdigest()


def records(path):
    with path.open(newline='') as stream:
        rows = list(DictReader(stream, delimiter='\t'))
    keyed = {row['id']: row for row in rows}
    assert len(rows) == len(keyed)
    return keyed


def main():
    check_round11()
    base = WORK / 'e108_r11'
    complement = WORK / 'e108_r11_complement'
    run = WORK / 'e108_r12'
    check_delta(WORK / 'e108_r5/reducible.g6', base / 'critical.g6', base / 'union.g6', 2_104_146)
    critical, _ = ordered_keys(base / 'critical.g6')
    assert len(critical) == 1875
    target, _ = ordered_keys(complement / 'total.98.fresh')
    tested, _ = ordered_keys(complement / 'deck.known_r10r11')
    set_aside, _ = ordered_keys(complement / 'deck.conservative_only')
    all_parents, _ = ordered_keys(complement / 'total.98.g6')
    assert (len(target), len(tested), len(set_aside), len(all_parents)) == (7954, 471, 745, 9170)
    assert target | tested | set_aside == all_parents

    plan, done = (records(run / name) for name in ('plan.tsv', 'done.tsv'))
    assert plan.keys() == done.keys()
    parents = set()
    emitted = set()
    parent_counts, raw_degrees = Counter(), Counter()
    for shard, planned in plan.items():
        completed = done[shard]
        assert planned['origin'] == completed['origin'] and planned['parents'] == completed['parents']
        shard_parents, digest = ordered_keys(run / f'{shard}.parents')
        assert digest == planned['key_sha256'] == completed['parent_sha256']
        assert not parents & shard_parents and len(shard_parents) == int(planned['parents'])
        parents |= shard_parents
        parent_counts[planned['origin']] += len(shard_parents)
        shard_keys, digest = ordered_keys(run / f'{shard}.keys')
        assert digest == completed['key_sha256'] and len(shard_keys) == int(completed['keys'])
        emitted |= shard_keys
        for degree in (7, 8):
            with (run / f'{shard}.{degree}.raw').open('rb') as stream:
                raw_rows = sum(1 for _ in stream)
            assert raw_rows == int(completed[f'd{degree}_raw'])
            raw_degrees[degree] += raw_rows
    assert parents == target == ordered_keys(run / 'target.tested')[0]
    assert all(not (run / name).read_bytes() for name in ('target.remaining', 'adaptive.tested'))
    assert emitted == ordered_keys(run / 'produced.keys')[0] and len(emitted) == 1724
    assert emitted <= critical and not (run / 'novel.g6').read_bytes()
    print(f'{len(plan)} matching plan/terminal shards, exact queue and frozen base partition; {parent_counts}, raw={raw_degrees}')
    print('All 1,724 output keys already in the 1,875-key critical set. This binds producer results only.')


if __name__ == '__main__':
    main()
