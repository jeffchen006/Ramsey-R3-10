"""Check the literal source/board/receipt join; optionally price e69 triple masks."""

import argparse
import hashlib
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cross_board(code):
    return {edge for bit, edge in enumerate(product(range(3), range(3, 6))) if code & (1 << bit)}


def board_type(edges):
    adjacent = [{right if left == index else left for left, right in edges if index in (left, right)}
                for index in range(6)]
    if not all(1 <= len(neighbors) <= 2 for neighbors in adjacent):
        return None
    if any(len(adjacent[first] & adjacent[second]) == 2 for first, second in combinations(range(6), 2)):
        return None
    remaining = set(range(6))
    sizes = []
    while remaining:
        component = {next(iter(remaining))}
        while True:
            closed = component.union(*(adjacent[vert] for vert in component))
            if closed == component:
                break
            component = closed
        sizes.append(len(component))
        remaining -= component
    return len(edges), tuple(sorted(sizes))


def lines(path):
    return path.read_text().splitlines()


def check(base, terminal):
    expected = {(3, (2, 2, 2)): (273, 6), (4, (2, 4)): (85, 36), (4, (3, 3)): (78, 9),
                (5, (6,)): (94, 36), (6, (6,)): (238, 6)}
    literal = Counter(filter(None, (board_type(cross_board(code)) for code in range(512))))
    assert literal == {key: count for key, (rep, count) in expected.items()}
    roster = {(edges, rep, count) for (edges, shape), (rep, count) in expected.items()}
    assert roster == {tuple(map(int, line.split())) for line in lines(base / 'roster.tsv')}
    assert all(board_type(cross_board(rep)) == key for key, (rep, count) in expected.items())
    print(f'cross boards: {len(roster)} shapes, {sum(literal.values())} labelled')

    sources = {}
    for ecount, nkeys in ((51, 4), (52, 70), (53, 717), (54, 5167)):
        keys = lines(base / f'stems{ecount}.g6')
        assert len(keys) == len(set(keys)) == nkeys and keys == sorted(keys)
        for graph in keys:
            assert len(graph) == 36 and graph[0] == 'T'
            assert sum((ord(char) - 63).bit_count() for char in graph[1:]) == ecount
        sources[ecount] = keys
    for rank, key in enumerate(sources[51], 1):
        job = base / str(rank)
        assert [key] == lines(job / 'stem.g6')
        assert 's VERIFIED UNSAT' in lines(job / 'cake.log') and 'c VERIFIED' in lines(job / 'lrat.log')

    queue = base / 'queue'
    manifest = lines(queue / 'manifest.tsv')
    assert manifest[::2] == lines(queue / 'slot0.tsv')
    assert manifest[1::2] == lines(queue / 'slot1.tsv')
    expected_rows = {(f'{rep}-{rank}', rep, 48 + ecount, rank, g6)
                     for ecount, rep, count in roster if ecount > 3
                     for rank, g6 in enumerate(sources[48 + ecount], 1)}
    actual_rows = {}
    for line in manifest:
        key, rep, edge, rank, g6, pilot = line.split('\t')
        assert key not in actual_rows
        actual_rows[key] = (key, int(rep), int(edge), int(rank), g6)
        if pilot != '-':
            assert [g6] == lines(base / Path(pilot).name / 'stem.g6')
    assert set(actual_rows.values()) == expected_rows

    present = {}
    total_cpu, total_payload = 0.0, 0
    histogram, modes = Counter(), Counter()
    for line in lines(queue / 'receipts.tsv'):
        key, rep, edge, rank, mode, bytes_, cnf, digest, cpu = line.split('\t')
        assert key not in present and (key, int(rep), int(edge), int(rank)) == actual_rows[key][:4]
        assert int(mode) in (0, 5, 6) and len(cnf) == 64
        proof = queue / 'archive' / f'{key}.lrat.gz'
        assert proof.is_file(), 'snapshot may straddle an in-flight receipt; retry after lock'
        payload = proof.read_bytes()
        assert len(payload) == int(bytes_) and sha(payload) == digest
        present[key] = digest
        total_cpu += float(cpu)
        total_payload += len(payload)
        histogram[int(rep)] += 1
        modes[int(mode)] += 1
    print(f'q=3 dual receipts 4; q=4..6 {len(present)}/{len(expected_rows)}, '
          f'boards={dict(sorted(histogram.items()))}, modes={dict(sorted(modes.items()))}, '
          f'cpu={total_cpu:.2f}, payload={total_payload}')
    if terminal:
        assert len(present) == len(expected_rows)
        assert {path.name for path in (queue / 'archive').iterdir()} == {f'{key}.lrat.gz' for key in present}
        assert not list(queue.glob('open.*.tsv'))


def masks():
    triple = frozenset(range(3))
    allrows = tuple(range(6))
    pairs = tuple(map(frozenset, combinations(allrows, 2)))
    actions = [dict(zip(allrows, left + right))
               for left, right in product(permutations(range(3)), permutations(range(3, 6)))]
    counts, survivor = Counter(), Counter()
    strict = Counter()
    orbit_before, orbit_after, orbit_strict = set(), set(), set()
    for doubles in combinations(pairs, 6):
        degrees = [4 + (row in triple) + sum(row in mask for mask in doubles) for row in allrows]
        if min(degrees) < 6 or max(degrees) > 8:
            continue
        low = [row for row in triple if degrees[row] == 6]
        canonical = min(tuple(sorted(tuple(sorted(action[row] for row in mask)) for mask in doubles))
                        for action in actions)
        counts[len(low)] += 1
        orbit_before.add(canonical)
        if all(sum(row in mask and mask <= triple for mask in doubles) == 1 for row in low):
            survivor[len(low)] += 1
            orbit_after.add(canonical)
            if not any(mask <= set(low) for mask in doubles):
                strict[tuple(sorted(degrees[row] for row in triple))] += 1
                orbit_strict.add(canonical)
    print(f'mask-only counts before {sorted(counts.items())}, after {sorted(survivor.items())}; '
          f'row orbits {len(orbit_before)} -> {len(orbit_after)}')
    print(f'after also forbidding low-low in the A–A double graph: {len(orbit_strict)} orbits, '
          f'profiles {sorted(strict.items())}')


def check_reduced(base, terminal):
    queue = base / 'reduced'
    manifests = lines(queue / 'manifest.tsv')
    assert manifests[::2] == lines(queue / 'slot0.tsv')
    assert manifests[1::2] == lines(queue / 'slot1.tsv')
    sources = {edge: lines(base / f'id4_w22_e{edge}.g6') for edge in (55, 56)}
    assert len(sources[55]) == 1 and len(sources[56]) == 39
    for edge, source in sources.items():
        stem_rows = lines(base / f'id4_pos{edge}.tsv')
        stem_set = {text.split('\t')[2] for text in stem_rows}
        weighted = {key: int(count) for _, count, key in
                    (text.split('\t') for text in lines(base / 'id4_w22_rec.tsv')) if key in stem_set}
        assert all(value in (0, 1) for value in weighted.values()) and weighted.keys() == stem_set
        assert source == sorted(key for key, value in weighted.items() if value)

    expected = set()
    for degrees in ('677', '678', '688'):
        for cross in (273, 78, 85, 94, 238):
            edge = 30 + sum(map(int, degrees)) + len(cross_board(cross))
            if edge in sources:
                for rank, stem in enumerate(sources[edge], 1):
                    expected.add((f'{degrees}-{cross}-{rank}', cross, edge, rank, stem, degrees))
    actual = {}
    for row in manifests:
        key, cross, edge, rank, stem, pilot, degrees = row.split('\t')
        assert key not in actual
        actual[key] = (key, int(cross), int(edge), int(rank), stem, degrees)
        if pilot != '-':
            assert [stem] == lines(base / Path(pilot).name / 'stem.g6')
    assert set(actual.values()) == expected and len(actual) == 160

    proved, modes = {}, Counter()
    cpu, payload = 0., 0
    for row in lines(queue / 'receipts.tsv'):
        key, cross, edge, rank, mode, byte_count, cnf, digest, seconds = row.split('\t')
        assert key not in proved and actual[key][:4] == (key, int(cross), int(edge), int(rank))
        proof = (queue / 'archive' / f'{key}.lrat.gz').read_bytes()
        assert len(proof) == int(byte_count) and sha(proof) == digest and len(cnf) == 64
        prove_mode = int(mode)
        assert prove_mode in (0, 5, 6)
        proved[key] = prove_mode
        cpu += float(seconds)
        payload += len(proof)
        modes[prove_mode] += 1
    print(f'one-low reduced: {len(proved)}/160, modes={dict(sorted(modes.items()))}, '
          f'cpu={cpu:.2f}, payload={payload}')
    if terminal:
        assert proved.keys() == actual.keys()
        assert {path.name for path in (queue / 'archive').iterdir()} == {f'{key}.lrat.gz' for key in proved}
        assert not list(queue.glob('open.*.tsv'))


def check_matching(base, terminal):
    queue = base / 'highq3'
    manifest = lines(queue / 'manifest.tsv')
    assert manifest[::2] == lines(queue / 'slot0.tsv') and manifest[1::2] == lines(queue / 'slot1.tsv')
    catalog = lines(base / 'stems54.g6')
    joined = lines(base / 'idjoin54.tsv')
    assert len(catalog) == len(joined) == 5167
    seeds = []
    for rank, (text, stem) in enumerate(zip(joined, catalog), 1):
        index, population, *bins, key = text.split('\t')
        assert rank == int(index) and stem == key and len(bins) == 4
        if any(map(int, bins)):
            seeds.append(stem)
    assert len(seeds) == len(set(seeds)) == 906 and seeds == lines(base / '777_q3.g6')
    expected = {}
    for rank, (stem, line) in enumerate(zip(seeds, manifest, strict=True), 1):
        key, cross, edge, irank, g6, pilot, profile = line.split('\t')
        assert (key, cross, edge, irank, g6, profile) == (f'777-273-{rank}', '273', '54', str(rank), stem, '777')
        expected[key] = irank
        if pilot != '-':
            assert [stem] == lines(base / Path(pilot).name / 'stem.g6')
    cpu, payload = 0., 0
    seen, modes = set(), Counter()
    for line in lines(queue / 'receipts.tsv'):
        key, cross, edge, rank, mode, byte_count, cnf, digest, seconds = line.split('\t')
        assert key not in seen and expected[key] == rank and cross == '273' and edge == '54'
        archive = (queue / 'archive' / f'{key}.lrat.gz').read_bytes()
        assert len(archive) == int(byte_count) and sha(archive) == digest and len(cnf) == 64
        assert int(mode) in (0, 5, 6)
        modes[int(mode)] += 1
        payload += len(archive)
        cpu += float(seconds)
        seen.add(key)
    print(f'777 matching: {len(seen)}/906, modes={dict(sorted(modes.items()))}, cpu={cpu:.2f}, payload={payload}')
    if terminal:
        assert seen == set(expected)
        assert {path.name for path in (queue / 'archive').iterdir()} == {f'{key}.lrat.gz' for key in seen}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('--terminal', action='store_true')
    parser.add_argument('--reduced', action='store_true')
    parser.add_argument('--matching', action='store_true')
    args = parser.parse_args()
    if args.reduced:
        check_reduced(args.base, args.terminal)
    elif args.matching:
        check_matching(args.base, args.terminal)
    else:
        check(args.base, args.terminal)
        masks()


if __name__ == '__main__':
    main()
