#!/usr/bin/env python3
import argparse
from collections import Counter
from itertools import combinations, zip_longest
from pathlib import Path

from panel16_audit import independent_masks, load_plant_line
from verify_panel17 import bits, graph6


SLICES = {(67, 5, '2333', '3334'): (32340, 13690, 792, 46),
          (68, 4, '2333', '3334'): (28301, 12968, 116, 24)}


def read_integer_rows(path, width):
    with Path(path).open() as stream:
        for line in stream:
            row = tuple(map(int, line.split()))
            assert len(row) == width, (path, line)
            yield row


def frame_binding(graph, neutral, marks, degree, cap, root_count, alpha):
    order = len(graph)
    assert 0 <= neutral < order and len(marks) == root_count
    assert tuple(sorted(set(marks))) == marks
    assert all(0 <= mark < (1 << order) and mark.bit_count() == degree-root_count for mark in marks)
    rows = tuple(frozenset(bits(row)) for row in graph)
    mark_sets = tuple(frozenset(bits(mark)) for mark in marks)
    private = set(range(order)) - {neutral}
    assert set().union(*mark_sets) == private
    assert all(root_count + len(first & second) <= cap for first, second in combinations(mark_sets, 2))
    assert not independent_masks(graph, alpha-root_count+1)
    memberships = tuple(frozenset(index for index, mark in enumerate(mark_sets) if site in mark)
                        for site in range(order))
    for site, row in enumerate(rows):
        assert len(row) + len(memberships[site]) <= degree
        for root, mark in enumerate(mark_sets):
            overlap = len(row & mark)
            assert overlap <= cap and (not overlap or root not in memberships[site])
    for first, second in combinations(range(order), 2):
        assert len(rows[first] & rows[second]) + len(memberships[first] & memberships[second]) <= cap
        assert not (second in rows[first] and rows[first] & rows[second])
    groups = tuple(tuple(site for site in sorted(private) if memberships[site] == {root})
                   for root in range(root_count))
    assert all(groups)
    private_degree = sum(len(rows[site]) for site in private)
    return private_degree, len(rows[neutral]), groups


def bind(path, catalogues, orders, degree, cap, roots, alpha, unique_frame_ids):
    bound = {}
    id_to_physical = ({}, {})
    physical_to_id = ({}, {})
    step = roots + 2
    for record in read_integer_rows(path, 2 + 2*step):
        identity, tail = record[:2], record[2:]
        assert min(identity) >= 0 and identity not in bound
        physical = tuple(tail[side*step:(side+1)*step] for side in range(2))
        binding = []
        graphs = []
        for side, info in enumerate(physical):
            host, neutral, *marks = info
            assert 0 <= host < len(catalogues[side])
            if unique_frame_ids:
                assert id_to_physical[side].setdefault(identity[side], info) == info
                assert physical_to_id[side].setdefault(info, identity[side]) == identity[side]
            graph = catalogues[side][host]
            assert len(graph) == orders[side]
            binding.append(frame_binding(graph, neutral, tuple(marks), degree, cap, roots, alpha))
            graphs.append(graph)
        (left_sum, left_degree, left_groups), (right_sum, right_degree, right_groups) = binding
        assert right_sum == left_sum+(orders[1]-orders[0])*degree and left_degree+right_degree == degree
        shapes = tuple(''.join(map(str, sorted(map(len, groups)))) for groups in (left_groups, right_groups))
        bound[identity] = ((left_sum, left_degree, *shapes), physical, tuple(graphs), (left_groups, right_groups))
    return bound


def labelled_specs(groups):
    return tuple((side, root, sites) for root, pair in enumerate(zip_longest(*groups))
                 for side, sites in enumerate(pair) if sites is not None)


def crossing(specs, physical, graphs, flat):
    cursor = 0
    signed = ({}, {})
    for side, _, sites in specs:
        destination_neutral = physical[1-side][1]
        source_neutral = physical[side][1]
        opposite_order = len(graphs[1-side])
        for site in sites:
            row = flat[cursor]
            assert 0 <= row < 1 << opposite_order
            assert bool(row & (1 << destination_neutral)) == bool(graphs[side][site] & (1 << source_neutral))
            for peer in range(opposite_order):
                if peer == destination_neutral:
                    continue
                edge = (site, peer) if not side else (peer, site)
                assert edge not in signed[side]
                signed[side][edge] = bool(row & (1 << peer))
            cursor += 1
    assert cursor == len(flat)
    if any(signed[0][edge] != signed[1][edge] for edge in signed[0].keys() & signed[1].keys()):
        return None
    return signed[0] | signed[1]


def control(args):
    catalogues = tuple(tuple(map(tuple, graph6(path))) for path in args.catalogues)
    cases = bind(args.cases, catalogues, (6, 7), 5, 4, 2, 5, False)
    plants = dict(map(load_plant_line, args.plants.read_text().splitlines()))
    assert len(cases) == len(plants) == 153 and cases.keys() == plants.keys()
    keyed_live = set()
    for line in args.fills.read_text().splitlines():
        left, right, reason, *flat = map(int, line.split())
        if reason == 4:
            keyed_live.add(((left, right), tuple(flat)))
    flips = [0, 0]
    for identity, (_, physical, graphs, groups) in cases.items():
        labels = []
        next_private = 1
        for graph, (_, neutral, *_) in zip(graphs, physical, strict=True):
            label = []
            for site in range(len(graph)):
                label.append(0 if site == neutral else next_private)
                next_private += site != neutral
            labels.append(label)
        plant = plants[identity]

        def seen(first, second):
            return (min(first, second), max(first, second)) in plant

        for side, graph in enumerate(graphs):
            for first, second in combinations(range(len(graph)), 2):
                assert bool(graph[first] & (1 << second)) == seen(labels[side][first], labels[side][second])
            for root, mark in enumerate(physical[side][2:]):
                assert all(bool(mark & (1 << site)) == seen(next_private+2*side+root, vertex)
                           for site, vertex in enumerate(labels[side]))
        specs = labelled_specs(groups)
        positions = ({}, {})
        flat = []
        for side, _, sites in specs:
            for site in sites:
                positions[side][site] = len(flat)
                row = sum(1 << peer for peer, label in enumerate(labels[1-side]) if seen(labels[side][site], label))
                flat.append(row)
        assert (identity, tuple(flat)) in keyed_live, identity
        fixed = crossing(specs, physical, graphs, flat)
        assert fixed is not None and all(value == seen(labels[0][first], labels[1][second])
                                         for (first, second), value in fixed.items())
        for side in range(2):
            site, peer = next(iter(positions[side])), next(iter(positions[1-side]))
            mutated = flat.copy()
            mutated[positions[side][site]] ^= 1 << peer
            assert crossing(specs, physical, graphs, mutated) is None
            assert (identity, tuple(mutated)) not in keyed_live
            flips[side] += 1
    print('labelled physical plants', len(plants), 'one-direction crossing corruptions', *flips)


def read_weighted_count(path):
    expected = {}
    for line in path.read_text().splitlines():
        columns = line.split()
        if columns[0] == 'shape' and columns[1] != 'D':
            total, neutral, left, right, raw, forward, reverse, both, neither = columns[1:]
            key = (int(total), int(neutral), left, right)
            if key in SLICES:
                values = tuple(map(int, (raw, forward, reverse, both)))
                assert key not in expected and values == SLICES[key]
                assert int(neither) == values[0]-values[1]-values[2]+values[3]
                expected[key] = values
    assert expected == SLICES
    return expected


def target(args):
    catalogues = tuple(tuple(map(tuple, graph6(path))) for path in args.catalogues)
    assert tuple(map(len, catalogues)) == (2576, 7)
    expected = read_weighted_count(args.weights)
    cases = bind(args.cases, catalogues, (16, 17), 9, 5, 4, 9, True)
    assert len(cases) == 70 and list(cases) == sorted(cases)
    survivor_counts = Counter(binding[0] for binding in cases.values())
    assert survivor_counts == {key: entry[3] for key, entry in expected.items()}
    old = {row[:2]: (ordinal, row[2:]) for ordinal, row in enumerate(read_integer_rows(args.pilot, 14))}
    assert len(old) == 544
    with args.companion.open() as stream:
        assert next(stream).split() == ['frame16', 'frame17', 'D16', 'd16', 'host16', 'neutral16', 'masks16',
                                       'singleton16', 'host17', 'neutral17', 'masks17', 'singleton17', 'row_labels',
                                       'column_labels', 'orientation', 'prior_pilot_row']
        companion = [line.split() for line in stream]
    assert len(companion) == len(cases)
    overlap = Counter()
    with args.labels.open('w') as stream:
        print('frame16 frame17 side root host neutral mark singleton_labels', file=stream)
        for (identity, (key, physical, _, groups)), receipt in zip(cases.items(), companion, strict=True):
            pilot_row = '-'
            if identity in old:
                ordinal, old_physical = old[identity]
                assert old_physical == physical[0]+physical[1]
                overlap[key] += 1
                pilot_row = str(ordinal)
            fields = list(map(str, identity + key[:2]))
            for side, (host, neutral, *marks) in enumerate(physical):
                fields.extend([str(host), str(neutral), ','.join(map(str, marks)),
                               ';'.join(','.join(map(str, group)) for group in groups[side])])
            for side, (_, neutral, *_) in enumerate(physical):
                fields.append(','.join(str(site) for site in range(16+side) if site != neutral))
            fields.extend(['16private_rows__17private_cols', pilot_row])
            assert receipt == fields, identity
            for side, root, sites in labelled_specs(groups):
                host, neutral, *marks = physical[side]
                print(*identity, 16+side, root, host, neutral, marks[root], ','.join(map(str, sites)), file=stream)
    for key, (raw, forward, reverse, both) in expected.items():
        print(*key, 'raw', raw, 'neither/forward-only/reverse-only/both',
              raw-forward-reverse+both, forward-both, reverse-both, both, 'pilot-overlap', overlap[key])


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='mode', required=True)
    controls = sub.add_parser('control')
    targets = sub.add_parser('target')
    for command in (controls, targets):
        command.add_argument('catalogues', nargs=2, type=Path)
        command.add_argument('cases', type=Path)
    controls.add_argument('plants', type=Path)
    controls.add_argument('fills', type=Path)
    targets.add_argument('weights', type=Path)
    targets.add_argument('pilot', type=Path)
    targets.add_argument('companion', type=Path)
    targets.add_argument('labels', type=Path)
    args = parser.parse_args()
    (control if args.mode == 'control' else target)(args)


if __name__ == '__main__':
    main()
