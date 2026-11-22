#!/usr/bin/env python3
"""Coarse-passing re-pairings and independent capacity bounds for round 14."""

from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
from random import Random
from time import process_time

from round14_shared_edges import (bounded_lp, build, descriptors, excess, graph, groups, instances, integer,
                                  joint_assignment, lines, make_model, pack, paired_model, unpack, validate, vertices)
from scan import verify
from typed_lp import RAMSEY


ROOT = Path(__file__).resolve().parents[3]


def capacities(model, assignment, signatures):
    columns = [{support: index for index, support in enumerate(side)} for side in signatures]
    types = [key for key in model.bounds if key[0] == 'site' and assignment.get(key)]
    supply = Counter()
    for first, second in combinations(types, 2):
        if set(first[1]).intersection(second[1]) or set(first[2]).intersection(second[2]):
            continue
        for side in range(2):
            pair = tuple(sorted(columns[side][site[side + 1]] for site in (first, second)))
            supply[(side, 'edge', *pair)] += assignment[first] * assignment[second]
    allowed = [{index for index, support in enumerate(side) if 0 not in support} for side in signatures]
    return [(key, amount, supply[key]) for key, amount in assignment.items() if key[1] == 'edge'
            and set(key[2:]) <= allowed[key[0]] and amount > supply[key]]


def support_failures(point, width, cross_count):
    occupied = [column for column, amount in point.items() if column[0] == 'site' and amount]
    failures = []
    for site in occupied:
        left, right = map(set, site[1:3])
        eligible = [other for other in occupied if not (left.intersection(other[1]) or right.intersection(other[2]))]
        for side, own in enumerate((left, right)):
            available = set().union(*(other[side + 1] for other in eligible))
            via_cross = set(index for index in site[2 - side] if index <= cross_count)
            missing = set(range(1, width)) - own - available - via_cross
            if missing:
                failures.append((site, side, sorted(missing)))
    return failures


def smaller():
    circulant = [sum(1 << ((vertex + step) % 13) for step in (1, -1, 5, -5)) for vertex in range(13)]
    sources = [('C13', 4, [circulant])]
    for target, order in ((5, 12), (5, 13), (6, 17), (6, 16), (7, 22)):
        source = f'r3_{target}_{order}.g6'
        sources.append((source, target - 1, map(graph.parse_graph6, (ROOT / 'gluing/val' / source).read_text().splitlines())))
    cases = 0
    tally = Counter()
    for source, alpha, graphs in sources:
        for graph_id, adj in enumerate(graphs):
            if not all(adj[first] & adj[second] or adj[first] >> second & 1
                       for first, second in combinations(range(len(adj)), 2)) or graph.alpha(adj) != alpha:
                continue
            for roots, wings, doubles, width, private, counts, total in descriptors(adj, alpha):
                cases += 1
                if not cases % 1000:
                    print('Smaller rooted controls', cases, dict(tally), flush=True)
                model = paired_model(doubles, width, private, counts, total, star=True)
                point = joint_assignment(adj, roots, wings, doubles, model)
                signatures = [groups(width, side) for side in doubles]
                assert not capacities(model, point, signatures)
                assert not support_failures(point, width, width - 1 - private)
                common = sorted(set(range(len(adj))).difference(roots, *wings))
                simple = [(first, second) for first, second in combinations(common, 2) if adj[first] >> second & 1]
                for side in range(2):
                    projection = {vertex: signatures[side].index(tuple(index for index, anchor in enumerate(wings[side], 1)
                                                                          if adj[vertex] >> anchor & 1)) for vertex in common}
                    def project(first, second):
                        return (side, 'edge', *sorted((projection[first], projection[second])))

                    for (first, second), (third, fourth) in combinations(simple, 2):
                        if len({first, second, third, fourth}) != 4:
                            continue
                        for third, fourth in ((third, fourth), (fourth, third)):
                            removed = (project(first, second), project(third, fourth))
                            added = (project(first, third), project(second, fourth))
                            if any(key not in model.bounds for key in added) or Counter(removed) == Counter(added):
                                continue
                            mutant = point.copy()
                            mutant.subtract(removed)
                            mutant.update(added)
                            tally['attempts'] += 1
                            try:
                                validate(model, mutant)
                            except AssertionError:
                                continue
                            tally['old-passing'] += 1
                            obstruction = capacities(model, mutant, signatures)
                            if obstruction:
                                print('Smaller adverse control:', source, graph_id, roots, removed, added, obstruction,
                                      'after', cases, 'rooted controls', dict(tally), flush=True)
                                return True
    print('Smaller switch sweep:', cases, 'rooted controls', dict(tally), flush=True)
    return False


def extremal_controls():
    from check_rows import saturated

    cycle = [sum(1 << ((vertex + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16)) for vertex in range(35)]
    complement = graph.parse_matrix((ROOT / 'scratch/G/exoo39.matrix').read_text().splitlines())
    exoo = saturated([row ^ ((1 << 39) - 1) ^ (1 << vertex) for vertex, row in enumerate(complement)])
    rng = Random(140170)
    for name, adj, alpha in [('C35', cycle, 8), ('Exoo39-sat', exoo, 9)]:
        assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
        n = len(adj)
        full = (1 << n) - 1
        cap_deficit = n - 1 - RAMSEY[alpha - 1]
        windows = codegree = 0
        for first, second in combinations(range(n), 2):
            if not (adj[first] >> second & 1):
                continue
            roots = (1 << first) | (1 << second)
            boundary = adj[first] | adj[second] | roots
            wing = boundary & ~roots
            outside = full ^ boundary
            for site in vertices(outside):
                for anchor in vertices(wing & ~adj[site]):
                    actual = adj[site] & adj[anchor]
                    via_boundary = (actual & boundary).bit_count()
                    inside = (actual & outside).bit_count()
                    assert 1 <= via_boundary + inside <= adj[site].bit_count() + adj[anchor].bit_count() - cap_deficit
                    codegree += 1
            pool = list(vertices(boundary))
            tested = set()
            for _ in range(8):
                rng.shuffle(pool)
                forbidden = independent = 0
                for vertex in pool:
                    if forbidden >> vertex & 1:
                        continue
                    independent |= 1 << vertex
                    forbidden |= (1 << vertex) | adj[vertex]
                    target = alpha + 1 - independent.bit_count()
                    if not 1 <= target <= 7 or independent in tested:
                        continue
                    tested.add(independent)
                    for added in (0, boundary & ~forbidden):
                        kept = outside & ~forbidden
                        induced = kept | added
                        internal = sum((adj[other] & kept).bit_count() for other in vertices(kept)) // 2
                        attachments = sum((adj[other] & added).bit_count() for other in vertices(kept))
                        fixed = sum((adj[other] & added).bit_count() for other in vertices(added)) // 2
                        assert sum((adj[other] & induced).bit_count() for other in vertices(induced)) == 2 * (internal + attachments + fixed)
                        assert induced.bit_count() < RAMSEY[target]
                        assert all(dx * (internal + attachments + fixed) >= dy * induced.bit_count() + offset
                                   for dx, dy, offset in lines(target))
                        windows += 1
        print(name, windows, 'literal window checks;', codegree, 'literal codegree checks', flush=True)


def re_pair(model, point, signatures):
    original = {key for key, _, _ in capacities(model, point, signatures)}
    available = [{index for index, support in enumerate(side) if 0 not in support} for side in signatures]
    for side in range(2):
        eligible = [key for key in point if key[:2] == (side, 'edge') and set(key[2:]) <= available[side]]
        for first, second in combinations(eligible, 2):
            left, right = first[2:]
            third, fourth = second[2:]
            if len({left, right, third, fourth}) != 4:
                continue
            for third, fourth in ((third, fourth), (fourth, third)):
                added = tuple((side, 'edge', *sorted(pair)) for pair in ((left, third), (right, fourth)))
                if any(column not in model.bounds for column in added):
                    continue
                point[first] -= 1
                point[second] -= 1
                point[added[0]] = point.get(added[0], 0) + 1
                point[added[1]] = point.get(added[1], 0) + 1
                try:
                    validate(model, point)
                    obstructions = [obstruction for obstruction in capacities(model, point, signatures)
                                    if obstruction[0] in added and obstruction[0] not in original]
                    if obstructions:
                        return (first, second), added, obstructions
                except AssertionError:
                    pass
                finally:
                    point[first] += 1
                    point[second] += 1
                    point[added[0]] -= 1
                    point[added[1]] -= 1
    return None


def target_pins():
    table = {(tuple(record['key']), record['tag']): record for record in map(json.loads,
             (ROOT / 'scratch/G/round13/pair.witnesses.jsonl').read_text().splitlines())}
    failures = re_pairs = missing = 0
    direct_cpu = 0.
    for key, tag, signature in instances():
        model = make_model(True, key, signature)
        receipt = table[key, tag]
        assert receipt['status'] == 'integer-witness'
        point = unpack(model, receipt['artifact'])
        validate(model, point)
        signatures = [groups(6, side) for side in signature]
        start = process_time()
        missing_columns = support_failures(point, 6, 1)
        direct_cpu += process_time() - start
        print('Cheap fixed-population support failures:', key, tag, missing_columns, flush=True)
        missing += bool(missing_columns)
        conflicts = capacities(model, point, signatures)
        failures += bool(conflicts)
        print('Old target projection (all masks and both tables pinned):', key, tag,
              len(conflicts), 'oversubscribed margins, first:', conflicts[:1], flush=True)
        switch = re_pair(model, point, signatures)
        assert switch
        re_pairs += 1
        print('Coarse-passing 2-switch creates a newly oversubscribed marginal:', switch, flush=True)
    assert failures == re_pairs == 4
    assert missing == 3
    print('Cheap fixed-population support checks for four patterns:', round(direct_cpu, 6), 'CPU seconds', flush=True)


def audit_shared_point(key, tag, signature, point, plain, edges):
    validate(plain, point)
    assert not excess(edges, point)
    base = make_model(True, key, signature)
    projection = {column: amount for column, amount in point.items() if column in base.bounds}
    validate(base, projection)
    signatures = [groups(6, side) for side in signature]
    assert not capacities(base, projection, signatures)
    switched = re_pair(base, projection.copy(), signatures)
    assert switched
    print('Re-pairing a compatible integer projection passes old rows but fails the shared count:', switched,
          flush=True)
    occupied = {column: index for index, column in enumerate(column for column, amount in point.items()
                                                            if column[0] == 'site' and amount)}
    if len(occupied) == 28:
        assert all(point[column] == 1 for column in occupied)
        rows = [0] * 28
        for (first, second), column in edges.items():
            if point.get(column):
                assert point[column] == 1
                left, right = occupied[first], occupied[second]
                rows[left] |= 1 << right
                rows[right] |= 1 << left
        triangle_count = sum((rows[first] & rows[second]).bit_count() for first, second in combinations(range(28), 2)
                             if rows[first] >> second & 1) // 3
        print('Point has 28 singleton types; literal W with 86 edges has', triangle_count, 'triangles', flush=True)
        assert triangle_count
    window_model, _ = build(key, signature, True)
    assert window_model.bounds == plain.bounds
    failures = Counter(name for row, rhs, name in window_model.rows
                       if sum(coefficient * point.get(column, 0) for column, coefficient in row.items()) > rhs)
    print('Compatible point, stronger window row violations:', dict(failures), flush=True)


def explain(model, weights):
    weighted_columns = Counter()
    weighted_rhs = Fraction(0)
    for index, weight in weights.items():
        row, rhs, label = model.rows[index]
        weighted_rhs += weight * rhs
        for column, coefficient in row.items():
            weighted_columns[column] += weight * coefficient
        live = [(column, coefficient) for column, coefficient in row.items() if model.bounds[column]]
        print('  multiplier', weight, 'row', index, label, rhs, 'nonzero box columns', live, flush=True)
    minimum = sum(value * model.bounds[column] for column, value in weighted_columns.items() if value < 0)
    assert minimum > weighted_rhs
    print('  exact contradiction: box min', minimum, '>', weighted_rhs, flush=True)


def recomplete(directory, windows, replay):
    table = {(tuple(record['key']), record['tag']): record for record in map(json.loads,
             (ROOT / 'scratch/G/round13/pair.witnesses.jsonl').read_text().splitlines())}
    destination = directory / f'recomplete-{int(windows)}.jsonl'
    records = {}
    if replay:
        for line in destination.read_text().splitlines():
            record = json.loads(line)
            identity = tuple(record['key']), record['tag']
            assert identity not in records
            records[identity] = record
    with destination.open('r' if replay else 'w') as evidence:
        for key, tag, signature in instances():
            start = process_time()
            model, edges = build(key, signature, windows)
            base = make_model(True, key, signature)
            old = unpack(base, table[key, tag]['artifact'])
            validate(base, old)
            for column in base.bounds:
                if column[0] != 'site':
                    continue
                mass = old.get(column, 0)
                model.bounds[column] = mass
                if mass:
                    model.le({column: -1}, -mass, 'old_population_receipt')
            for (first, second), column in edges.items():
                model.bounds[column] = old.get(first, 0) * old.get(second, 0)
            if replay:
                record = records.pop((key, tag))
                status, artifact = record['status'], record['artifact']
                if status == 'cert':
                    weights = {int(index): Fraction(weight) for index, weight in artifact.items()}
                    assert verify(model, weights)
                    explain(model, weights)
                elif status == 'integer-witness':
                    point = unpack(model, artifact)
                    validate(model, point)
                    if not windows:
                        plain, edges = build(key, signature, False)
                        audit_shared_point(key, tag, signature, point, plain, edges)
                else:
                    assert artifact is None
                print(key, tag, status, 'replayed', flush=True)
                continue
            status, artifact = bounded_lp(model, 5)
            lp_status = status
            if status == 'feasible':
                status, point = integer(model, 5)
                if point:
                    artifact = pack(model, point)
            elif status == 'cert':
                assert verify(model, {int(index): Fraction(weight) for index, weight in artifact.items()})
            print(key, tag, lp_status, status, round(process_time() - start, 3), flush=True)
            print(json.dumps({'key': key, 'tag': tag, 'status': status, 'artifact': artifact}), file=evidence, flush=True)
    assert not records


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'recomplete', 'recomplete-windows'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.mode == 'control':
        smaller()
        extremal_controls()
        target_pins()
    else:
        recomplete(args.directory, args.mode == 'recomplete-windows', args.verify)
