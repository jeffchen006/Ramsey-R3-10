"""Matched private-wing column join, with or without the six-set index."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from time import process_time

from kernel_projection import bits, decode
from p3_high_f import classify
from p3_round4_index import census
from p3_singleton_cover import attachment_masks, bitset, independent_levels, zero_compatibility
from p3_zero_conditioned import condition, verify
from p3_zero_residue import placements
from path_three_top import plant


def misses(sets, order):
    avoiding = [(1 << len(sets)) - 1] * order
    for index, block in enumerate(sets):
        for vertex in bits(block):
            avoiding[vertex] ^= 1 << index
    return avoiding


def miss_signature(mask, index, universe):
    for vertex in bits(mask):
        universe &= index[vertex]
    return universe


def row_domains(core, masks, common, boundary_blocks, zeroes, zero_positions, degree, cap):
    zero_at = dict(zip(zero_positions, zeroes))
    signatures = {mask: bitset(index for index, block in enumerate(boundary_blocks) if not mask & block)
                  for mask in masks}
    sizes = {size: [mask for mask in masks if mask & common and mask.bit_count() == size]
             for size in {mask.bit_count() for mask in masks}}
    domains = []
    for vertex, neighbours in enumerate(core):
        if vertex in zero_at:
            domains.append([zero_at[vertex]])
            continue
        exact = degree - neighbours.bit_count()
        pinned = [(zero_mask, bool(neighbours >> zero_vertex & 1),
                   (neighbours & core[zero_vertex]).bit_count(), signatures[zero_mask])
                  for zero_vertex, zero_mask in zero_at.items()]
        allowed = []
        for mask in sizes.get(exact, ()):
            for zero_mask, edge, inside, zero_miss in pinned:
                total = inside + (mask & zero_mask).bit_count()
                if (edge and total) or (not edge and (not 1 <= total <= cap or signatures[mask] & zero_miss)):
                    break
            else:
                allowed.append(mask)
        domains.append(allowed)
    return domains


def project(domains, wing):
    positions = {bitset(outer for local, outer in enumerate(wing) if code >> local & 1): code
                 for code in range(1 << len(wing))}
    support = [0] * len(positions)
    window = bitset(wing)
    for vertex, domain in enumerate(domains):
        for mask in domain:
            support[positions[mask & window]] |= 1 << vertex
    return support


def column_projections(support, wing, all_rows):
    result = []
    for local in range(len(wing)):
        allowed_zero = allowed_one = 0
        for pattern, vertices in enumerate(support):
            if pattern >> local & 1:
                allowed_one |= vertices
            else:
                allowed_zero |= vertices
        result.append((all_rows ^ allowed_zero, allowed_one))
    return result


def selected_wings(boundary):
    root_y, _, root_z = boundary[-3:]
    return [tuple(bits(root & ~other & ~boundary[-2])) for root, other in ((root_y, root_z), (root_z, root_y))]


def pair_range(boundary, first, second, cap):
    common = (boundary[first] & boundary[second]).bit_count()
    return (-common, -common) if boundary[first] >> second & 1 else (1 - common, cap - common)


def pair_links(columns, pair_bound, signatures):
    lower, upper = pair_bound
    result = []
    for first in columns[0]:
        signature = signatures[first] if signatures is not None else 0
        result.append(bitset(index for index, second in enumerate(columns[1])
                             if lower <= (first & second).bit_count() <= upper
                             and (not signature or not signature & signatures[second])))
    return result


def count_join(columns, boundary, wing, cap, support, signatures, all_rows):
    assert len(wing) in (2, 3)
    if not all(columns):
        return 0, 0
    links = {(left, right): pair_links((columns[left], columns[right]),
                                     pair_range(boundary, wing[left], wing[right], cap), signatures)
             for left, right in combinations(range(len(wing)), 2)}
    edges = sum(value.bit_count() for links_pair in links.values() for value in links_pair)
    if len(wing) == 2:
        return edges, sum(not ((all_rows ^ (first | second)) & ~support[0]
                                    or (first & ~second) & ~support[1] or (second & ~first) & ~support[2]
                                    or (first & second) & ~support[3])
                          for first, link in zip(columns[0], links[0, 1])
                          for second in (columns[1][index] for index in bits(link)))
    has_final = [bitset(index for index, mask in enumerate(columns[2]) if mask >> vertex & 1)
                 for vertex in bits(all_rows)]
    result = 0
    for left, (first, first_link) in enumerate(zip(columns[0], links[0, 1])):
        for middle in bits(first_link):
            possible = links[0, 2][left] & links[1, 2][middle]
            if not possible:
                continue
            second = columns[1][middle]
            colours = (all_rows ^ (first | second), first & ~second, second & ~first, first & second)
            must, forbidden = 0, 0
            for pattern, subset in enumerate(colours):
                if subset & ~(support[pattern] | support[pattern + 4]):
                    break
                must |= subset & ~support[pattern]
                forbidden |= subset & ~support[pattern + 4]
            else:
                for vertex in bits(must):
                    possible &= has_final[vertex]
                    if not possible:
                        break
                if possible:
                    for vertex in bits(forbidden):
                        possible &= ~has_final[vertex]
                        if not possible:
                            break
                result += possible.bit_count()
    return edges, result


def direct(picks, core, boundary, wing, indep, domains, cap, use_sets):
    window = bitset(wing)
    for vertex, domain in enumerate(domains):
        expected = bitset(outer for outer, mask in zip(wing, picks) if mask >> vertex & 1)
        if not any(mask & window == expected for mask in domain):
            return False
    for left, right in combinations(range(len(wing)), 2):
        common = sum((picks[left] >> vertex & 1) and (picks[right] >> vertex & 1)
                     for vertex in range(len(core)))
        lower, upper = pair_range(boundary, wing[left], wing[right], cap)
        if not lower <= common <= upper:
            return False
        if use_sets and any(not block & (picks[left] | picks[right]) for block in indep):
            return False
    return True


def check_projected(core, boundary, degree, cap, indep, domains, planted):
    from itertools import product

    all_rows = (1 << len(core)) - 1
    index = misses(indep, len(core))
    levels = independent_levels(core)
    signatures = {mask: miss_signature(mask, index, (1 << len(indep)) - 1) for level in levels for mask in level}
    for wing in selected_wings(boundary):
        support = project(domains, wing)
        columns = [[mask for mask in levels[degree - boundary[outer].bit_count()]
                    if mask & allowed == mask and mask & must == must]
                   for outer, (must, allowed) in zip(wing, column_projections(support, wing, all_rows))]
        for use_sets in (False, True):
            counts = count_join(columns, boundary, wing, cap, support, signatures if use_sets else None, all_rows)
            expected = sum(direct(picks, core, boundary, wing, indep, domains, cap, use_sets)
                           for picks in product(*columns))
            assert counts[1] == expected
        if planted is not None:
            picks = [bitset(vertex for vertex in range(len(core)) if planted[vertex] >> (len(core) + outer) & 1)
                     for outer in wing]
            assert all(mask in candidates for mask, candidates in zip(picks, columns))
            assert direct(picks, core, boundary, wing, indep, domains, cap, True)
        else:
            assert counts[1] == 0


def control():
    core, boundary, actual = plant()
    levels = independent_levels(boundary)
    masks = attachment_masks(boundary, levels, 6, 3, 4, 3)
    common = boundary[-1] & boundary[-2] & boundary[-3]
    full = [actual[vertex] >> len(core) for vertex in range(len(core))]
    zeros = [(vertex, mask) for vertex, mask in enumerate(full) if not mask & common]
    domains = row_domains(core, masks, common, levels[5], [mask for _, mask in zeros],
                          [vertex for vertex, _ in zeros], 6, 4)
    assert all(mask in domain for mask, domain in zip(full, domains))
    indep = independent_levels(core)[3]
    check_projected(core, boundary, 6, 4, indep, domains, actual)
    bad_inner = next(vertex for vertex, mask in enumerate(full) if mask & boundary[-3])
    bad = list(domains)
    bad[bad_inner] = []
    check_projected(core, boundary, 6, 4, indep, bad, None)
    print('C21 two exact zeros: planted survives; impossible row rejected; complete direct counts agree')
    triple_control(core, indep)


def triple_control(core, indep):
    from itertools import product
    from random import Random

    wing = (0, 1, 2)
    boundary = [8, 8, 8, 7]
    indep = indep[:2]
    all_rows = (1 << len(core)) - 1
    index = misses(indep, len(core))
    stable = independent_levels(core)[2]
    signatures = {mask: miss_signature(mask, index, (1 << len(indep)) - 1) for mask in stable}
    random = Random(38671)
    accepted = rejected = 0
    for _ in range(24):
        columns = [random.sample(stable, 8) for _ in wing]
        domains = [random.sample(list(range(8)), 6) for _ in core]
        support = project(domains, wing)
        for use_sets in (False, True):
            index_values = signatures if use_sets else None
            _, counted = count_join(columns, boundary, wing, 4, support, index_values, all_rows)
            direct_count = sum(direct(picks, core, boundary, wing, indep, domains, 4, use_sets)
                               for picks in product(*columns))
            assert counted == direct_count
            if use_sets:
                accepted += counted
            else:
                rejected += counted
    assert 0 < accepted < rejected
    print('Three-column arithmetic control on C21 residue: direct and indexed agree;',
          accepted, 'accepted and', rejected - accepted, 'six-set rejections')


def experiment(path, rows_path, witnesses_path, output, mode, sample):
    from p3_singleton_cover import capacity_rows

    key = (1, (0, 1), (1, 1))
    layout = '1:0:1:1:1'
    boundary = classify(9, 6, 4, key)
    levels = independent_levels(boundary)
    masks = attachment_masks(boundary, levels, 9, 3, 5, 5)
    common = boundary[-1] & boundary[-2] & boundary[-3]
    zeros, _, _, patterns = zero_compatibility(masks, common, levels[8], 22)
    witnesses = json.loads(witnesses_path.read_text())
    base_rows = capacity_rows(boundary, levels, masks, 9, 9, 6, 22, strong=True)
    live = []
    for pattern in patterns:
        selected = [zeros[index] for index in pattern]
        name = layout + '/' + ','.join(map(str, pattern))
        if name not in witnesses:
            live.append((pattern, selected))
        else:
            rows, groups = condition(masks, common, levels[8], base_rows, selected, 9, 22)
            verify(rows, [int(level == 1) for _, level in groups], 20 - 2 * len(selected), witnesses[name])
    assert live == [((0,), [(1 << 0) | (1 << 4) | (1 << 14)])]
    known = {int(row.split('\t')[3]): row.strip().split('\t')
             for row in rows_path.read_text().splitlines()[1:] if row.split('\t')[2] == layout}
    all_cores = path.read_bytes().splitlines()
    expected = census(path)
    assert set(known) == {row for row, (edges, digest) in expected.items() if edges == 62}
    start = process_time()
    counts = Counter()
    with output.open('w') as stream:
        stream.write('layout\trow\tg6_sha256\tpattern\tpositions\twing0_edges\twing0_tuples\twing1_edges\twing1_tuples\n')
        for number, (row, entry) in enumerate(sorted(known.items())):
            if sample == 'scout' and number % 5 != 0 or sample == 'heldout' and number % 5 == 0:
                continue
            digest = sha256(all_cores[row]).hexdigest()
            assert digest == entry[4] == expected[row][1]
            core = decode(all_cores[row].decode())
            all_rows = (1 << len(core)) - 1
            core_levels = independent_levels(core)
            indep = core_levels[6]
            index = misses(indep, len(core))
            wings = selected_wings(boundary)
            signatures = None if mode == 'base' else {
                mask: miss_signature(mask, index, (1 << len(indep)) - 1)
                for size in {9 - boundary[outer].bit_count() for wing in wings for outer in wing}
                for mask in core_levels[size]}
            placed = passed = 0
            for pattern, selected in live:
                for positions in placements(core, selected, levels[8], 9, 6):
                    placed += 1
                    domains = row_domains(core, masks, common, levels[8], selected, positions, 9, 6)
                    attachment_counts = []
                    for wing in wings:
                        support = project(domains, wing)
                        columns = [[mask for mask in core_levels[9 - boundary[outer].bit_count()]
                                    if mask & allowed == mask and mask & must == must]
                                   for outer, (must, allowed) in zip(wing, column_projections(support, wing, all_rows))]
                        attachment_counts.extend(count_join(columns, boundary, wing, 6, support, signatures, all_rows))
                    passing = all(attachment_counts[1::2])
                    passed += passing
                    counts['wing_edges'] += sum(attachment_counts[::2])
                    counts['wing_tuples'] += sum(attachment_counts[1::2])
                    stream.write('\t'.join(map(str, (layout, row, digest, ','.join(map(str, pattern)),
                                                       ','.join(map(str, positions)), *attachment_counts))) + '\n')
            assert placed == int(entry[-1])
            print('ROW', row, 'placements', placed, 'both wings nonempty', passed, 'CPU-s', round(process_time() - start, 3), flush=True)
            counts.update(rows=1, placements=placed, passed=passed, surviving_rows=bool(passed))
    print('TOTAL', mode, sample, dict(counts), 'CPU-s', round(process_time() - start, 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'base', 'index'))
    parser.add_argument('sample', choices=('scout', 'heldout', 'all'), nargs='?')
    parser.add_argument('output', type=Path, nargs='?')
    parser.add_argument('--catalogue', type=Path, default=Path('../../../gluing/val/r3_7_22.g6'))
    parser.add_argument('--bindings', type=Path, default=Path('../r8/zero-residue-bindings.tsv'))
    parser.add_argument('--witnesses', type=Path, default=Path('../r8/zero-all.json'))
    args = parser.parse_args()
    if args.mode == 'control':
        control()
    else:
        assert args.sample and args.output
        experiment(args.catalogue, args.bindings, args.witnesses, args.output, args.mode, args.sample)


if __name__ == '__main__':
    main()
