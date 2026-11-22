"""Rounded singleton bounds and four common-column covers."""

from collections import Counter, defaultdict
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from time import process_time

from kernel_projection import bits, decode
from p3_high_f import classify, filter_target, layouts
from p3_round4_index import census
from p3_singleton_cover import attachment_masks, bitset, capacity_rows, independent_levels, zero_compatibility
from p3_six_join import row_domains
from p3_zero_conditioned import condition, propose, verify
from p3_zero_residue import placements
from path_three_top import plant


def cases(original, selected_layout=None):
    keys = {'1:0:1:1:1', '3:0:1:2:1'}
    found = set()
    for size, key in layouts(9, 6, 4, 8, 16, 18):
        label = ':'.join(map(str, (key[0], *key[1], *key[2])))
        if label not in keys or (selected_layout and selected_layout != label):
            continue
        boundary = classify(9, 6, 4, key)
        assert filter_target(boundary) == 'pass'
        levels = independent_levels(boundary)
        masks = attachment_masks(boundary, levels, 9, 3, 5, 5)
        common = boundary[-1] & boundary[-2] & boundary[-3]
        zeros, _, _, patterns = zero_compatibility(masks, common, levels[8], 22)
        assert patterns is not None
        base_rows = capacity_rows(boundary, levels, masks, 9, 9, 6, 22, strong=True)
        found.add(label)
        live = []
        for pattern in patterns:
            chosen = [zeros[index] for index in pattern]
            rows, groups = condition(masks, common, levels[8], base_rows, chosen, 9, 22)
            goal = [int(level == 1) for _, level in groups]
            name = label + '/' + ','.join(map(str, pattern))
            if name in original:
                verify(rows, goal, 20 - 2 * len(chosen), original[name])
            else:
                live.append((pattern, chosen, rows, goal))
        assert len(live) == 1 and len(live[0][0]) == 1
        yield (label, 45 + size, boundary, levels[8], masks, common, *live[0])
    assert found == ({selected_layout} if selected_layout else keys)


def four_cover(choices, target, must_double, forbid_double, audit=False):
    assert not (must_double | forbid_double) & ~target
    choices = [choice for choice in choices if choice & target == choice]
    universe = target.bit_length()
    pairs = []
    suffix = []
    for left, first in enumerate(choices):
        suffix.append(len(pairs))
        for right in range(left + 1, len(choices)):
            other = choices[right]
            doubled = first & other
            if not doubled & forbid_double:
                pairs.append((left, right, first | other, doubled))
    suffix.append(len(pairs))
    bytes_needed = (len(pairs) + 7) // 8
    union_bytes = [bytearray(bytes_needed) for _ in range(universe)]
    double_bytes = [bytearray(bytes_needed) for _ in range(universe)]
    for index, (_, _, union, doubled) in enumerate(pairs):
        byte, bit = divmod(index, 8)
        for vertex in bits(union):
            union_bytes[vertex][byte] |= 1 << bit
        for vertex in bits(doubled):
            double_bytes[vertex][byte] |= 1 << bit
    unions_at = [int.from_bytes(data, 'little') for data in union_bytes]
    doubled_at = [int.from_bytes(data, 'little') for data in double_bytes]
    all_pairs = (1 << len(pairs)) - 1
    for left, right, union, doubled in pairs:
        admitted = all_pairs & (-1 << suffix[right + 1])
        for vertex in bits(target ^ union):
            admitted &= doubled_at[vertex] if must_double >> vertex & 1 else unions_at[vertex]
            if not admitted:
                break
        if not admitted:
            continue
        for vertex in bits(must_double & union & ~doubled):
            admitted &= unions_at[vertex]
        for vertex in bits(doubled | (union & forbid_double)):
            admitted &= ~unions_at[vertex]
        for vertex in bits(union):
            admitted &= ~doubled_at[vertex]
        for index in bits(admitted):
            third, last, other_union, other_doubled = pairs[index]
            total_double = doubled | other_doubled | (union & other_union)
            if audit:
                assert left < right < third < last and union | other_union == target
                assert not (doubled & other_union or other_doubled & union)
                assert must_double & total_double == must_double and not forbid_double & total_double
            yield (choices[left], choices[right], choices[third], choices[last]), total_double


def control():
    core, boundary, actual = plant()
    common = boundary[-1] & boundary[-2] & boundary[-3]
    old_columns = [bitset(vertex for vertex in range(len(core)) if actual[vertex] >> (len(core) + outer) & 1)
                   for outer in bits(common)]
    assert len(old_columns) == 2 and all(mask.bit_count() == 3 for mask in old_columns)
    added = [tuple(bits(mask)) for mask in old_columns]
    planted = set(old_columns + [bitset(added[0][:2]), bitset(added[1][:2])])
    assert len(planted) == 4
    target = old_columns[0] | old_columns[1]
    must_double = bitset(added[0][:2] + added[1][:2])
    choices = [mask for size in (2, 3) for mask in independent_levels(core)[size] if mask & target == mask]
    expected = set()
    for picked in combinations(choices, 4):
        counts = [sum(bool(mask >> vertex & 1) for mask in picked) for vertex in bits(target)]
        if all(count in (1, 2) for count in counts) and all(
                count == 2 for vertex, count in zip(bits(target), counts) if must_double >> vertex & 1):
            expected.add(frozenset(picked))
    actual_covers = {frozenset(picked) for picked, _ in four_cover(choices, target, must_double, 0, True)}
    assert expected == actual_covers and frozenset(planted) in actual_covers
    assert not list(four_cover(choices, target, must_double, must_double, True))
    print('C21 common columns + two subcolumns: planted survives, inconsistent mutation rejected;',
          len(actual_covers), 'covers equal direct enumeration')


def run(args, original):
    witnesses = json.loads(args.rounded.read_text())
    known = defaultdict(dict)
    for line in args.bindings.read_text().splitlines()[1:]:
        _, edges, label, row, digest, _, count = line.split('\t')
        known[label][int(row)] = int(edges), digest, int(count)
    expected = census(args.catalogue)
    graphs = args.catalogue.read_bytes().splitlines()
    totals = Counter()
    start = process_time()
    with args.output.open('w') as stream:
        stream.write('layout\trow\tdigest\tzero_pattern\tzero_positions\tcovers\tdouble_sets\n')
        for label, edges, boundary, blockers, masks, common, pattern, chosen, rows, goal in cases(original, args.layout):
            assert set(known[label]) == {row for row, (count, _) in expected.items() if count == edges}
            name = label + '/' + ','.join(map(str, pattern))
            print('Rounded singleton witness', name, verify(rows, goal, 19, witnesses[name]), flush=True)
            assert common.bit_count() == 4 and all(boundary[outer].bit_count() == 3 for outer in bits(common))
            for number, (row, (count, digest, expected_placements)) in enumerate(sorted(known[label].items())):
                if args.sample == 'scout' and number % 5 != 0:
                    continue
                assert count == edges and expected[row][1] == digest == sha256(graphs[row]).hexdigest()
                core = decode(graphs[row].decode())
                six = independent_levels(core)[6]
                all_rows = (1 << len(core)) - 1
                local = Counter()
                for occupied in placements(core, chosen, blockers, 9, 6):
                    target = all_rows ^ bitset(occupied)
                    domains = row_domains(core, masks, common, blockers, chosen, occupied, 9, 6)
                    must_double = forbid_double = 0
                    possible = True
                    for vertex in bits(target):
                        counts = {(mask & common).bit_count() for mask in domains[vertex]} & {1, 2}
                        if not counts:
                            possible = False
                            break
                        if counts == {1}:
                            forbid_double |= 1 << vertex
                        if counts == {2}:
                            must_double |= 1 << vertex
                    covers = Counter()
                    if possible:
                        for _, doubled in four_cover(six, target, must_double, forbid_double, True):
                            assert doubled.bit_count() == 3
                            covers[doubled] += 1
                    local.update(placements=1, passing=bool(covers), covers=sum(covers.values()), double_sets=len(covers))
                    stream.write('\t'.join(map(str, (label, row, digest, pattern[0], occupied[0],
                                                       sum(covers.values()), len(covers)))) + '\n')
                assert local['placements'] == expected_placements
                totals.update(local)
                totals.update(rows=1, surviving=bool(local['passing']))
                print('ROW', label, row, dict(local), 'CPU-s', round(process_time() - start, 3), flush=True)
    print('TOTAL', args.sample, dict(totals), 'CPU-s', round(process_time() - start, 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'discover', 'verify', 'run'))
    parser.add_argument('rounded', type=Path, nargs='?', default=Path('rounded.json'))
    parser.add_argument('--original', type=Path, default=Path('../r8/zero-all.json'))
    parser.add_argument('--catalogue', type=Path, default=Path('../../../gluing/val/r3_7_22.g6'))
    parser.add_argument('--bindings', type=Path, default=Path('../r8/zero-residue-bindings.tsv'))
    parser.add_argument('--layout', choices=('1:0:1:1:1', '3:0:1:2:1'))
    parser.add_argument('--sample', choices=('scout', 'all'), default='scout')
    parser.add_argument('--output', type=Path, default=Path('common-scout.tsv'))
    args = parser.parse_args()
    if args.mode == 'control':
        control()
        return
    original = json.loads(args.original.read_text())
    if args.mode == 'run':
        run(args, original)
        return
    witnesses = {} if args.mode == 'discover' else json.loads(args.rounded.read_text())
    discovered = {}
    for label, _, _, _, _, _, pattern, _, rows, goal in cases(original):
        name = label + '/' + ','.join(map(str, pattern))
        if args.mode == 'discover':
            status, proof = propose(rows, goal, 19)
            assert proof is not None, status
            discovered[name] = proof
        else:
            proof = witnesses.pop(name)
        print(name, 'exact upper bound <19:', verify(rows, goal, 19, proof))
    assert not witnesses
    if args.mode == 'discover':
        args.rounded.write_text(json.dumps(discovered, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    main()
