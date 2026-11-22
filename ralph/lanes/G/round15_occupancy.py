#!/usr/bin/env python3
"""Four-template matched price for occupancy-only MTF implications."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter, process_time

from check_rows import saturated
from round13_signatures import groups, make_model, paired_model, validate
from round14_edge_control import capacities, support_failures
from round14_shared_edges import bounded_lp, descriptors, graph, instances, integer, joint_assignment, pack, unpack
from scan import verify


ROOT = Path(__file__).resolve().parents[3]
OLD_WITNESSES = ROOT / 'scratch/G/round13/pair.witnesses.jsonl'
FIXED_EXPECTED = {
    'matching+matching': [(('site', (5,), (1, 4), 8), 0, [3])],
    'matching+middle': [],
    'middle+middle': [(('site', (3, 4), (2,), 9), 1, [1])],
    'leaf+leaf': [(('site', (3, 4), (3,), 9), 1, [1])],
}


def mask(indices):
    return sum(1 << index for index in indices)


def matching_boundary(width, crossings):
    opposite = tuple(1 << anchor if 1 <= anchor <= crossings else 0 for anchor in range(width))
    return opposite, opposite


def type_columns(model):
    return tuple(column for column, upper in model.bounds.items() if column[0] == 'site' and upper)


def install(model, opposite):
    """Only the population columns appear in a newly appended row."""
    types = [(column, (mask(column[1]), mask(column[2]))) for column in type_columns(model)]
    rows = {}
    for column, wings in types:
        compatible = [(other, other_wings) for other, other_wings in types
                      if not (other_wings[0] & wings[0] or other_wings[1] & wings[1])]
        upper = model.bounds[column]
        for side, boundary in enumerate(opposite):
            for anchor in range(1, len(boundary)):
                if wings[side] & (1 << anchor) or wings[1 - side] & boundary[anchor]:
                    continue
                coefficients = {other: -upper for other, other_wings in compatible if other_wings[side] & (1 << anchor)}
                coefficients[column] = 1
                rows[column, side, anchor] = len(model.rows)
                model.le(coefficients, 0, 'occupancy_common_neighbor')
    return rows


def row_failures(model, indices, assignment):
    failures = {}
    for identity, index in indices.items():
        row, rhs, _ = model.rows[index]
        lhs = sum(weight * assignment.get(column, 0) for column, weight in row.items())
        if lhs > rhs:
            failures[identity] = (index, lhs, rhs)
    return failures


def equality_controls(adj, alpha, width_filter=None):
    checks = Counter()
    for roots, wings, doubles, width, private, counts, total in descriptors(adj, alpha):
        if width_filter is not None and width != width_filter:
            continue
        model = paired_model(doubles, width, private, counts, total, star=True)
        literal = joint_assignment(adj, roots, wings, doubles, model)
        crossings = width - 1 - private
        assert not support_failures(literal, width, crossings)
        indices = install(model, matching_boundary(width, crossings))
        validate(model, literal)
        assert not row_failures(model, indices, literal)
        for column in type_columns(model):
            if not literal[column]:
                continue
            for side in range(2):
                for anchor in range(1, width):
                    expected = anchor not in column[side + 1] and not (
                        anchor <= crossings and anchor in column[2 - side])
                    assert ((column, side, anchor) in indices) == expected
                    checks['required' if expected else 'adjacent' if anchor in column[side + 1] else 'exempt'] += 1
        checks['pairs'] += 1
    return dict(checks)


def extremal_controls(adj, alpha):
    from typed_lp import Model

    assert graph.alpha(adj) == alpha and graph.triangle_free(adj)
    assert all(adj[first] & adj[second] or adj[first] >> second & 1 for first, second in combinations(range(len(adj)), 2))
    checks = Counter()
    for roots in combinations(range(len(adj)), 2):
        first, second = roots
        if not (adj[first] >> second & 1):
            continue
        wings = (tuple(index for index in range(len(adj)) if index != second and adj[first] >> index & 1),
                 tuple(index for index in range(len(adj)) if index != first and adj[second] >> index & 1))
        outside = tuple(sorted(set(range(len(adj))).difference(roots, *wings)))
        sites = {index: ('site', *(tuple(offset for offset, wing_vertex in enumerate(wing, 1)
                                      if adj[index] >> wing_vertex & 1) for wing in wings), adj[index].bit_count())
                 for index in outside}
        model = Model()
        literal = Counter(sites.values())
        for column, count in literal.items():
            model.col(column, count)
        boundary = tuple((0, *(mask(offset for offset, wing_vertex in enumerate(wings[1 - side], 1)
                                     if adj[anchor] >> wing_vertex & 1) for anchor in wing))
                         for side, wing in enumerate(wings))
        indices = install(model, boundary)
        validate(model, literal)
        outside_mask = mask(outside)
        for site, column in sites.items():
            for side, wing in enumerate(wings):
                for offset, anchor in enumerate(wing, 1):
                    common = adj[site] & adj[anchor]
                    is_adjacent = bool(adj[site] >> anchor & 1)
                    exempt = bool(common & ~outside_mask)
                    identity = column, side, offset
                    assert (identity in indices) == (not is_adjacent and not exempt)
                    if identity in indices:
                        row = model.rows[indices[identity]][0]
                        assert common and all(row[sites[other]] == -model.bounds[column]
                                              for other in outside if common >> other & 1)
                    checks['adjacent' if is_adjacent else 'exempt' if exempt else 'required'] += 1
        checks['edges'] += 1
    return dict(checks)


def controls():
    cycle = lambda order, steps: [mask((index + step) % order for step in steps) for index in range(order)]
    small = cycle(13, (1, -1, 5, -5))
    result = equality_controls(small, 4)
    assert result['pairs'] == 26 and result['exempt'] > 0
    print('C13(1,5) full paired-model control:', result, flush=True)
    extra = 0
    for target, order in ((5, 12), (5, 13), (6, 17), (6, 16), (7, 22)):
        tally = Counter()
        for text in (ROOT / 'gluing/val' / f'r3_{target}_{order}.g6').read_text().splitlines():
            adj = graph.parse_graph6(text)
            if graph.alpha(adj) != target - 1 or any(not (adj[left] & adj[right] or adj[left] >> right & 1)
                                                     for left, right in combinations(range(order), 2)):
                continue
            tally.update(equality_controls(adj, target - 1))
        print('Corpus equality controls:', target, order, dict(tally), flush=True)
        extra += tally['pairs']
    assert extra + result['pairs'] == 52
    c35 = cycle(35, (1, -1, 7, -7, 11, -11, 16, -16))
    comp = graph.parse_matrix((ROOT / 'scratch/G/exoo39.matrix').read_text().splitlines())
    exoo = saturated([row ^ ((1 << 39) - 1) ^ (1 << index) for index, row in enumerate(comp)])
    for label, adj, alpha in (('C35', c35, 8), ('Exoo39-sat', exoo, 9)):
        print(label, 'literal wing analogue:', extremal_controls(adj, alpha), flush=True)


def fixed_receipts(directory):
    old = {(tuple(record['key']), record['tag']): record for record in map(json.loads, OLD_WITNESSES.read_text().splitlines())}
    with (directory / 'fixed.jsonl').open('w') as output:
        for key, tag, signature in instances():
            model = make_model(True, key, signature)
            record = old[key, tag]
            assert record['status'] == 'integer-witness'
            assignment = unpack(model, record['artifact'])
            validate(model, assignment)
            expected = support_failures(assignment, 6, 1)
            assert expected == FIXED_EXPECTED[tag], (tag, expected)
            added = install(model, matching_boundary(6, 1))
            failures = row_failures(model, added, assignment)
            assert set(failures) == {(column, side, anchor) for column, side, anchors in expected for anchor in anchors}
            receipts = []
            for (column, side, anchor), (index, lhs, rhs) in failures.items():
                row = model.rows[index][0]
                assert assignment[column] == lhs > rhs == 0
                assert all(not assignment.get(other, 0) for other in row if other != column)
                receipts.append({'type': column, 'side': side, 'anchor': anchor, 'terms': len(row) - 1,
                                 'occupied_suppliers': 0, 'mass': lhs})
            print(key, tag, 'fixed occupancy violations', receipts, flush=True)
            print(json.dumps({'key': key, 'tag': tag, 'receipts': receipts}, sort_keys=True), file=output)


def composition(old, new, model):
    return sum(abs(old.get(column, 0) - new.get(column, 0)) for column in type_columns(model))


def exact_audit(model, key, tag, signature, point, mode, old):
    validate(model, point)
    assert sum(point.get(column, 0) for column in type_columns(model)) == 28
    failures = support_failures(point, 6, 1)
    if mode == 'occupancy':
        assert not failures, (key, tag, failures)
    signatures = tuple(groups(6, side) for side in signature)
    return {'mass_L1_from_r13': composition(old, point, model),
            'unsupplied_anchors': sum(len(anchors) for _, _, anchors in failures),
            'oversubscribed_old_edge_cells': len(capacities(model, point, signatures))}


def timing(start):
    return {'cpu': round(process_time() - start[0], 4), 'wall': round(perf_counter() - start[1], 4)}


def clock():
    return process_time(), perf_counter()


def price(directory, replay, lp_cap, mip_cap):
    old = {(tuple(record['key']), record['tag']): record for record in map(json.loads, OLD_WITNESSES.read_text().splitlines())}
    tally = Counter()
    path = directory / 'matched.jsonl'
    records = {}
    if replay:
        for line in path.read_text().splitlines():
            record = json.loads(line)
            identity = tuple(record['key']), record['tag'], record['mode']
            assert identity not in records
            records[identity] = record
        assert len(records) == 8
    with path.open('r' if replay else 'w') as output:
        for index, (key, tag, signature) in enumerate(instances()):
            modes = ('old', 'occupancy') if index % 2 == 0 else ('occupancy', 'old')
            for mode in modes:
                setup_start = clock()
                model = make_model(True, key, signature)
                base_setup = timing(setup_start)
                assignment = unpack(model, old[key, tag]['artifact'])
                validate(model, assignment)
                before = len(model.rows)
                overlay_start = clock()
                added = install(model, matching_boundary(6, 1)) if mode == 'occupancy' else {}
                overlay_setup = timing(overlay_start)
                assert len(model.rows) == before + len(added)
                if replay:
                    result = records.pop((key, tag, mode))
                    assert result['columns'] == len(model.bounds) and result['rows'] == len(model.rows)
                else:
                    lp_start = clock()
                    lp_status, artifact = bounded_lp(model, lp_cap)
                    lp_time = timing(lp_start)
                    mip_start = clock()
                    mip_status = 'not run (certified LP)' if lp_status == 'cert' else None
                    if mip_status is None:
                        mip_status, point = integer(model, mip_cap)
                        if point is not None:
                            artifact = pack(model, point)
                    result = {'key': key, 'tag': tag, 'mode': mode, 'columns': len(model.bounds), 'rows': len(model.rows),
                              'added': len(added), 'base': base_setup, 'overlay': overlay_setup, 'lp': lp_status,
                              'lp_time': lp_time, 'mip': mip_status, 'mip_time': timing(mip_start), 'artifact': artifact}
                if result['lp'] == 'cert':
                    assert verify(model, {int(row): Fraction(weight) for row, weight in result['artifact'].items()})
                elif result['mip'] == 'integer-witness':
                    diagnostics = exact_audit(model, key, tag, signature, unpack(model, result['artifact']), mode, assignment)
                    if replay:
                        assert result['diagnostics'] == diagnostics
                    else:
                        result['diagnostics'] = diagnostics
                else:
                    assert result['artifact'] is None
                print(json.dumps({field: value for field, value in result.items() if field != 'artifact'}, sort_keys=True),
                      flush=True)
                if not replay:
                    print(json.dumps(result, sort_keys=True), file=output, flush=True)
                tally[mode, result['lp'], result['mip']] += 1
    assert not records
    print('Exact replay tallies:' if replay else 'Matched tallies:', dict(tally), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'fixed', 'price', 'verify'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--lp-cap', type=float, default=8)
    parser.add_argument('--mip-cap', type=float, default=10)
    args = parser.parse_args()
    if args.mode == 'control':
        controls()
    elif args.mode == 'fixed':
        fixed_receipts(args.directory)
    else:
        price(args.directory, args.mode == 'verify', args.lp_cap, args.mip_cap)
