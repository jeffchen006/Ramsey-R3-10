"""Semantic checks of physical target witnesses and immutable receipt inventory."""

from collections import Counter
from itertools import combinations, product
import argparse
import hashlib
import json
from pathlib import Path

from round22_fold import Fold


def independent_target_rows(fold):
    size = len(fold.grid)
    width = fold.width
    selectors = {literal: option for option, literal in fold.gates.items()}
    endpoints = {literal: pair for pair, literal in fold.edges[0].items()}
    allanchors = (1 << (2 * width)) - 1

    def tail(support):
        alive = allanchors ^ support
        low = alive & ((1 << width) - 1)
        high = alive >> width
        return max(alive.bit_count() - bool(low & high & 1), 1 + low.bit_count(), 1 + high.bit_count())

    common = {support: sum(1 << index for index, grid in enumerate(fold.grid) if support & grid)
              for support in set(fold.supports)}

    def verify_block(row):
        guards = tuple(-lit for lit in row if lit < 0)
        assert len(guards) <= 1 and all(guard in selectors for guard in guards)
        guardside = selectors[guards[0]] if guards else None
        positive = set(row) - {-guard for guard in guards}
        sites = {site for literal in positive for site in endpoints[literal]}
        if guardside:
            physical = size + guardside[0]
            sites.add(physical)
        assert all(site < size or (guardside is not None and site == size + guardside[0]) for site in sites)

        def mask(site):
            if site < size:
                return fold.grid[site]
            first, second = guardside
            return fold.slots[0][first] | fold.slots[1][second] << width

        for first, second in combinations(sorted(sites), 2):
            assert mask(first) & mask(second) or fold.edges[0].get((first, second)) in positive

        union = 0
        available = (1 << size) - 1
        for site in sites:
            union |= mask(site)
            available &= common[mask(site)]
            if site < size:
                available &= ~(1 << site)

        def search(support, count, options):
            if count + tail(support) >= fold.bound:
                return True
            if count + tail(support) + options.bit_count() < fold.bound:
                return False
            while options:
                one = options & -options
                options ^= one
                grid = fold.grid[one.bit_length() - 1]
                if search(support | grid, count + 1, options & common[grid]):
                    return True
            return False

        assert search(union, len(sites), available)

    blockers = [row for row, tag in fold.rows.items() if tag == 'padded-I']
    for row in blockers:
        verify_block(row)
    mutations = 0
    for row in blockers:
        if row[0] < 0 and any(any(site >= size for site in endpoints[literal]) for literal in row[1:]):
            try:
                verify_block(row[1:])
            except AssertionError:
                mutations += 1
                break
            raise AssertionError('accepted unguarded padded edge')

    chosen = {(row, col): [] for row, col in product(range(width), repeat=2)
              if (row or col) and fold.board[row][col] == 0}
    for literal, (first, second) in selectors.items():
        low, high = fold.slots[0][first], fold.slots[1][second]
        for row, col in chosen:
            if low & (1 << row) and high & (1 << col):
                chosen[row, col].append(literal)
    expected = {tuple(sorted(row)) for row in chosen.values()}
    assert expected == {row for row, tag in fold.rows.items() if tag == 'anchor-MTF'}
    expected_grid = set()
    expected_slot = set()
    for side in range(2):
        supports = tuple(mask >> (side * width) & ((1 << width) - 1) for mask in fold.grid) + fold.slots[side]
        for anchor in range(width):
            bit = 1 << anchor
            attached = {site for site, support in enumerate(supports) if support & bit}
            for site in range(size + len(fold.slots[side])):
                if site in attached:
                    continue
                edges = tuple(literal for (first, second), literal in fold.edges[side].items()
                              if (first == site and second in attached) or (second == site and first in attached))
                if site < size:
                    if anchor or not fold.grid[site] & (1 << ((1 - side) * width)):
                        expected_grid.add(tuple(sorted(edges)))
                else:
                    for literal, option in selectors.items():
                        if option[side] == site - size and (anchor or not fold.slots[1 - side][option[1 - side]] & 1):
                            expected_slot.add(tuple(sorted((-literal, *edges))))
    actual_grid = {row for row, tag in fold.rows.items() if tag == 'grid-MTF'}
    actual_slot = {row for row, tag in fold.rows.items() if tag == 'slot-MTF'}
    assert actual_grid <= expected_grid and expected_grid <= fold.rows.keys()
    assert actual_slot <= expected_slot and expected_slot <= fold.rows.keys()
    return dict(padded=len(blockers), anchors=len(expected), grid=len(expected_grid), slots=len(expected_slot), rejected=mutations)


def timing(path):
    values = path.read_text().splitlines()[-1].split()
    return float(values[0]) + float(values[1]), int(values[2])


def receipt_report(base):
    manifest = json.loads((base / 'manifest.json').read_text())
    accepted = {}
    split = {}
    open_rows = []
    combined = Counter()
    for folder in sorted((base / 'work').iterdir()):
        raw = folder / 'raw.bytes'
        formulas = folder / 'binding.json'
        if raw.exists():
            combined['raw_written'] += int(raw.read_text())
        for clock in folder.glob('*.time'):
            if clock.stat().st_size:
                cpu, rss = timing(clock)
                combined['cpu_seconds'] += cpu
                combined['max_rss_kib'] = max(combined['max_rss_kib'], rss)
        result = folder / 'result'
        if not result.exists() or not result.read_text().startswith('CHECKED '):
            open_rows.append((folder.name, result.read_text().strip() if result.exists() else 'no final receipt'))
            continue
        data = json.loads(formulas.read_text())
        ident = data['board']
        assert data['grid'] == manifest[ident]['grid']
        assert data['manifest'] == hashlib.sha256((base / 'manifest.json').read_bytes()).hexdigest()
        assert 's UNSATISFIABLE' in (folder / 'solve.log').read_text().splitlines()
        assert 'c VERIFIED' in (folder / 'lrat.log').read_text().splitlines()
        assert 's VERIFIED UNSAT' in (folder / 'cake.log').read_text().splitlines()
        archive = base / 'archive' / f'{folder.name}.lrat.zst'
        assert (folder / 'archived.bytes').read_text().strip() == str(archive.stat().st_size)
        checksums = (folder / 'sha256').read_text().splitlines()
        assert checksums[0].split()[0] == hashlib.sha256((folder / 'grid.cnf').read_bytes()).hexdigest()
        digest = hashlib.sha256()
        with archive.open('rb') as stream:
            for block in iter(lambda: stream.read(1 << 20), b''):
                digest.update(block)
        assert checksums[2].split()[0] == digest.hexdigest()
        data.update(receipt=folder.name, raw_bytes=int(raw.read_text()), archived_bytes=archive.stat().st_size)
        if data['split'] is None:
            assert ident not in accepted
            accepted[ident] = data
        else:
            split.setdefault(ident, []).append(data)
    composites = {}
    for ident, parts in split.items():
        groups = {}
        for data in parts:
            side, slot, polarity = data['split']
            groups.setdefault((side, slot), set()).add(polarity)
        if any(signs == {-1, 1} for signs in groups.values()):
            composites[ident] = [part['receipt'] for part in parts]
    covered = accepted.keys() | composites.keys()
    assert not (accepted.keys() & composites.keys())
    print(json.dumps(dict(whole=accepted, complementary_splits=composites, checked_leaves=split,
                          covered=sorted(covered), boards_open=[board['id'] for board in manifest if board['id'] not in covered],
                          keys_covered=sum(len(manifest[ident]['keys']) for ident in covered), open_attempts=open_rows,
                          **combined), indent=1, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('rows', 'receipts'))
    parser.add_argument('base', type=Path)
    parser.add_argument('boards', type=int, nargs='*')
    args = parser.parse_args()
    if args.action == 'rows':
        manifest = json.loads((args.base / 'manifest.json').read_text())
        for ident in args.boards:
            print(ident, independent_target_rows(Fold(manifest[ident]['grid'], 8, True)), flush=True)
    else:
        receipt_report(args.base)
