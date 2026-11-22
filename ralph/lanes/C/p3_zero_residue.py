"""Bind exact zero-pattern obstructions to the frozen P3 residue index."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path

from kernel_projection import decode
from p3_high_f import NO_HOLE, classify, filter_target, layouts
from p3_round4_index import census
from p3_singleton_cover import attachment_masks, bitset, capacity_rows, independent_levels, zero_compatibility
from p3_zero_conditioned import calibrate, condition, verify
from path_three_top import plant


def placements(residue, zeros, blockers, degree, cap):
    signatures = [bitset(index for index, blocker in enumerate(blockers) if not mask & blocker) for mask in zeros]
    choices = [[vertex for vertex, neighbours in enumerate(residue) if neighbours.bit_count() == degree - mask.bit_count()]
               for mask in zeros]
    for vertices in product(*choices):
        if len(set(vertices)) != len(zeros):
            continue
        for first, second in combinations(range(len(zeros)), 2):
            left, right = vertices[first], vertices[second]
            adjacent = bool(residue[left] >> right & 1)
            overlap = (zeros[first] & zeros[second]).bit_count()
            forced_edge = bool(signatures[first] & signatures[second])
            codegree = overlap + (residue[left] & residue[right]).bit_count()
            if (forced_edge and not adjacent) or (adjacent and codegree) or (not adjacent and not 1 <= codegree <= cap):
                break
        else:
            yield vertices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('witnesses', type=Path)
    parser.add_argument('bindings', type=Path)
    args = parser.parse_args()
    calibrate()
    core, boundary, full = plant()
    common = boundary[-1] & boundary[-2] & boundary[-3]
    actual = [(full[vertex] >> len(core), vertex) for vertex in range(len(core))
              if not (full[vertex] >> len(core)) & common]
    assert len(actual) == 2
    assert tuple(vertex for _, vertex in actual) in set(placements(core, [mask for mask, _ in actual],
                                                                  independent_levels(boundary)[5], 6, 4))
    print('C21 planted zero-pair placement preserved')
    residues = census(args.catalogue)
    graphs = [decode(line) for line in args.catalogue.read_text().splitlines()]
    witnesses = json.loads(args.witnesses.read_text())
    bindings = ['diagonal\tedges\tlayout\trow\tg6_sha256\tlive_patterns\tlive_placements']
    totals = Counter()
    for size, key in layouts(9, 6, 4, 8, 16, 18):
        if NO_HOLE in key[1:]:
            continue
        graph = classify(9, 6, 4, key)
        if filter_target(graph) != 'pass':
            continue
        levels = independent_levels(graph)
        masks = attachment_masks(graph, levels, 9, 3, 5, 5)
        common = bitset(range(6, 10))
        zeros, _, _, patterns = zero_compatibility(masks, common, levels[8], 22)
        assert patterns is not None
        base_rows = capacity_rows(graph, levels, masks, 9, 9, 6, 22, strong=True)
        layout = ':'.join(map(str, (key[0], *key[1], *key[2])))
        live = []
        for pattern in patterns:
            chosen = [zeros[index] for index in pattern]
            identifier = layout + '/' + ','.join(map(str, pattern))
            if identifier not in witnesses:
                live.append(chosen)
                continue
            rows, groups = condition(masks, common, levels[8], base_rows, chosen, 9, 22)
            verify(rows, [int(level == 1) for _, level in groups], 20 - 2 * len(chosen), witnesses.pop(identifier))
        stats = Counter()
        for row, (edges, digest) in residues.items():
            if edges != 45 + size:
                continue
            counts = [sum(1 for _ in placements(graphs[row], chosen, levels[8], 9, 6)) for chosen in live]
            live_patterns, live_placements = sum(bool(count) for count in counts), sum(counts)
            assert bool(live_patterns) == bool(live_placements)
            bindings.append(f'4\t{edges}\t{layout}\t{row}\t{digest}\t{live_patterns}\t{live_placements}')
            stats['rows'] += 1
            stats['empty'] += not live_patterns
            stats['pattern-rows'] += live_patterns
            stats['placements'] += live_placements
        totals.update(stats)
        print('layout', 45 + size, layout, 'live zero patterns', len(live), dict(stats),
              'live counts by q', sorted(Counter(map(len, live)).items()))
    assert not witnesses
    assert totals['rows'] == 4 * 30 + 5 * 60
    args.bindings.write_text('\n'.join(bindings) + '\n')
    print('TOTAL', dict(totals))


if __name__ == '__main__':
    main()
