"""Bind round-five checked P3 strata to their exact jobs and retained proofs."""

import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

from p3_round4_index import census, inventory, low_boundary, lower


def digest(path):
    checksum = sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def terminal(path, kind, diagonal=None):
    observed, declared = defaultdict(Counter), {}
    cpu_seconds = 0.0
    current_row = None
    closed = False
    for line in path.read_text().splitlines():
        if line.startswith('row '):
            prefix, key, status, cpu_label, elapsed = line.split()
            assert prefix == 'row' and cpu_label == 'CPU-s' and not closed
            row = int(key.split('-')[0]) if kind == 'lower' else diagonal
            assert current_row in (None, row) and row not in declared, (path, row)
            current_row = row
            observed[row][status] += 1
            cpu_seconds += float(elapsed)
        if line.startswith('TERMINAL '):
            header, elapsed = line.rsplit(' CPU-s ', 1)
            _, row, mode, values = header.split(' ', 3)
            row = int(row)
            assert mode == {'lower': 'fixed', 'upper': 'guarded', 'mixed': 'lite6'}[kind]
            assert row == current_row and row not in declared, (path, row)
            declared[row] = ast.literal_eval(values)
            assert float(elapsed) >= 0
            current_row = None
            closed = kind != 'lower'
        assert not line.startswith('REPLAY-SKIP'), (path, line)
    assert dict(observed) == declared and current_row is None, path
    return declared, cpu_seconds


def lower_index(work, rows, hash_retained):
    indexed = lower(work, rows, True, False)
    residues = sorted(row for row, (edges, _) in rows.items() if edges == 62)
    assert [int(row) for row in (work / 'p3e62-residues.txt').read_text().splitlines()] == residues
    layouts = low_boundary(work)
    pilot_keys = {}
    costs = Counter()
    for path in sorted(work.glob('p3low-pilot-*-fixed.log')):
        checked, unfinished = inventory(path, 'lower')
        terms, elapsed = terminal(path, 'lower')
        assert not unfinished and len(terms) == 1 and len(checked) == 6
        row = next(iter(terms))
        assert row not in pilot_keys and {residue for residue, _ in checked} == {row}
        pilot_keys[row] = set(checked)
        costs['pilot'] += elapsed
    assert set(pilot_keys) == {17, 118}
    for shard in range(4):
        for phase in ('full', 'replay'):
            path = work / f'p3e62-{phase}-{shard}.log'
            checked, unfinished = inventory(path, 'lower')
            terms, elapsed = terminal(path, 'lower')
            expected = {(row, layout) for row in residues[shard::4] for layout in layouts}
            if phase == 'full':
                expected -= set().union(*pilot_keys.values())
            assert not unfinished and set(checked) == expected
            assert list(terms) == residues[shard::4]
            assert all(terms[row] == {'checked': sum(key[0] == row for key in expected)} for row in terms)
            costs[phase] += elapsed
    if hash_retained:
        for row, layout, _, _, _, proof_hash, _ in indexed:
            assert digest(work / 'p3low-pilot' / f'{row}-fixed-{layout}-1.lrat') == proof_hash
    print('PASS e62 exact terminal shards and bindings; pilot/production/replay CPU-s:', dict(costs))
    print('retained proof SHA256 validation:', 'all 1320' if hash_retained else 'skipped')
    return indexed


def upper_index(work, rows, hash_retained, partial, mixed):
    indexed = []
    pilots = {13, 44, 79, 133} if mixed else {0, 95, 139, 163}
    level = 63 if mixed else 64
    kind = 'mixed' if mixed else 'upper'
    expected = {row for row, (edges, _) in rows.items() if edges == level}
    assert len(expected) == (60 if mixed else 59) and pilots <= expected
    for diagonal in (3, 4):
        if mixed:
            pilot_path = work / f'p3r5-mixed-{diagonal}-pilot.log'
            pilot, unfinished = inventory(pilot_path, kind)
            pilot_terms, _ = terminal(pilot_path, kind, diagonal)
            assert set(pilot) == pilots and not unfinished and pilot_terms == {diagonal: {'checked': 4}}
        else:
            pilot_mid, _ = inventory(work / f'p3flex-midpilot-{diagonal}.log', kind)
            pilot_extra, unfinished = inventory(work / f'p3extra-e64-{diagonal}.log', kind)
            assert set(pilot_mid) == {0} and set(pilot_extra) == pilots - {0} and not unfinished
            pilot = pilot_mid | pilot_extra
        done, deferred, absent, missing_replay = set(), {}, set(), set()
        costs = Counter()
        for shard in range(3):
            prefix = work / f'p3r5-{"mixed" if mixed else "e64"}-{diagonal}-{shard}'
            production = Path(f'{prefix}-produce.log')
            replay = Path(f'{prefix}-replay.log')
            shard_keys = {row for row in expected if row % 3 == shard}
            production_keys = shard_keys - pilots
            checked, capped = inventory(production, kind)
            assert set(checked) | set(capped) <= production_keys and not set(checked) & set(capped)
            producer_terms, elapsed = terminal(production, kind, diagonal)
            costs['production'] += elapsed
            completed = set(checked) | set(capped)
            assert partial or (completed == production_keys and producer_terms)
            absent |= production_keys - completed
            deferred.update(capped)
            required = checked | {row: pilot[row] for row in shard_keys & pilots}
            matching, other = inventory(replay, kind)
            assert not other and set(matching) <= set(required)
            replay_terms, elapsed = terminal(replay, kind, diagonal)
            costs['replay'] += elapsed
            assert partial or (matching == required and replay_terms)
            missing_replay |= set(required) - set(matching)
            for row, binding in matching.items():
                assert required[row] == binding
                proof = (work / 'p3r5-mixed' / f'{diagonal}-{row}.lrat' if mixed else
                         work / 'p3flex-pilot' / f'{diagonal}-guarded-{row:03d}.lrat')
                assert proof.stat().st_size == int(binding[-1])
                if hash_retained:
                    assert digest(proof) == binding[1]
                indexed.append((diagonal, row, *rows[row], *binding))
                done.add(row)
        print(f'e{level} diagonal={diagonal}: checked={len(done)} deferred={deferred} absent={sorted(absent)} '
              f'missing_replay={sorted(missing_replay)} CPU-s={dict(costs)}')
        assert partial or done == expected
    return sorted(indexed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--part', required=True, choices=('lower', 'upper', 'mixed'))
    parser.add_argument('--hash-retained', action='store_true')
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = census(args.census)
    if args.part == 'lower':
        assert not args.partial
        indexed = lower_index(args.work, rows, args.hash_retained)
    else:
        indexed = upper_index(args.work, rows, args.hash_retained, args.partial, args.part == 'mixed')
    args.output.write_text(''.join('\t'.join(map(str, row)) + '\n' for row in indexed))


if __name__ == '__main__':
    main()
