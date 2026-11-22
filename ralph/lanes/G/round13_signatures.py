#!/usr/bin/env python3
"""Integer pricing for one and two degree-six equality roots at e=170."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from itertools import combinations, combinations_with_replacement, permutations
from math import inf
from pathlib import Path
from time import process_time

from check_root_cover import graph, vertices
from round13_thresholds import ledger, live_cases
from scan import solve, verify
from signature_rows import supports_model
from typed_lp import Model


def counts_map(counts):
    return dict(zip(range(6, 10), counts))


def groups(order, doubles):
    return tuple((index,) for index in range(order)) + tuple(doubles)


def root_degrees(width, private, doubles):
    return tuple(private + 1 + sum(index in support for support in doubles) for index in range(width))


def root_signatures():
    pairs = tuple(combinations(range(6), 2))
    actions = [tuple(1 << pairs.index(tuple(sorted((perm[first], perm[second])))) for first, second in pairs)
               for perm in permutations(range(6))]
    allowed = []
    raw = 0
    for indices in combinations(range(len(pairs)), 9):
        supports = tuple(pairs[index] for index in indices)
        degrees = root_degrees(6, 4, supports)
        if min(degrees) < 7 or max(degrees) > 9:
            continue
        raw += 1
        mask = sum(1 << index for index in indices)
        if all(sum(action[index] for index in indices) >= mask for action in actions):
            allowed.append((mask, supports, Counter((6, *degrees))))
    return raw, allowed


def side_shapes():
    pairs = tuple(combinations(range(1, 6), 2))
    seen = set()
    for missing in combinations(pairs, 2):
        left = tuple(pair for pair in pairs if pair not in missing)
        signature = ((0, 1), *left)
        degrees = root_degrees(6, 4, signature)
        if max(degrees) > 9 or degrees[1] < 8 or min(degrees[1:]) < 7:
            continue
        canonical = min(tuple(sorted(tuple(sorted((perm[first - 2] if first > 1 else first,
                                                     perm[second - 2] if second > 1 else second)))
                                           for first, second in missing))
                        for perm in permutations(range(2, 6)))
        assert (1 in canonical[0] or 1 in canonical[1])
        seen.add(canonical)
    result = {}
    for missing in sorted(seen):
        touch = Counter(index for pair in missing for index in pair)
        tag = 'matching' if len(touch) == 4 else 'middle' if touch[1] == 2 else 'leaf'
        assert tag not in result
        result[tag] = ((0, 1), *(pair for pair in pairs if pair not in missing))
    assert set(result) == {'matching', 'middle', 'leaf'}
    return result


def feasible_histogram(counts, required):
    return all(required[degree] <= count for degree, count in counts.items())


def validate(model, assignment):
    assert assignment.keys() <= model.bounds.keys()
    for key, value in assignment.items():
        assert isinstance(value, int) and 0 <= value <= model.bounds[key], (key, value)
    for row, rhs, name in model.rows:
        lhs = sum(coefficient * assignment.get(key, 0) for key, coefficient in row.items())
        assert lhs <= rhs, (name, lhs, rhs)


def copy_model(target, source, side):
    for key, upper in source.bounds.items():
        target.col((side, *key), upper)
    for row, rhs, name in source.rows:
        target.le({(side, *key): value for key, value in row.items()}, rhs, f'{side}_{name}')


def compact(model):
    distinct = {}
    for row, rhs, name in model.rows:
        identity = frozenset(row.items())
        if identity not in distinct or rhs < distinct[identity][1]:
            distinct[identity] = row, rhs, name
    model.rows = list(distinct.values())
    return model


def paired_model(doubles, width, private, counts, total, min_residue=0, star=False, strengthened=True):
    """Two rooted projections, glued at the integral tuple of masks and degree of each W site."""
    cross_count = width - 1 - private
    assert cross_count >= 0
    peer_doubles = tuple((0, index) for index in range(1, cross_count + 1))
    for side in doubles:
        assert tuple(pair for pair in side if 0 in pair) == peer_doubles
    alpha = width + private - 1
    signature_lists = [groups(width, side) for side in doubles]
    kept = [tuple(support for support in signatures if 0 not in support) for signatures in signature_lists]
    degrees = tuple(root_degrees(width, private, side) for side in doubles)
    model = Model()
    for side in range(2):
        projection = supports_model(doubles[side], width, private, counts, total, strengthen=strengthened,
                                    target=(min_residue == 6))
        copy_model(model, projection, side)

    jointly = defaultdict(list)
    margins = defaultdict(list)
    deg_mass = defaultdict(list)
    for left in kept[0]:
        for right in kept[1]:
            if any(index in left and index in right for index in range(1, cross_count + 1)):
                continue
            for degree in counts:
                if not counts[degree] or degree < max(len(left), len(right)) + min_residue:
                    continue
                key = model.col(('site', left, right, degree), private if max(len(left), len(right)) == 1 else 1)
                jointly[left, right].append(key)
                margins[0, left, degree].append(key)
                margins[1, right, degree].append(key)
                deg_mass[degree].append(key)
    for side in range(2):
        signatures = signature_lists[side]
        for support in kept[side]:
            index = signatures.index(support)
            opposite = {key: mask_pair[1 - side] for mask_pair, columns in jointly.items()
                        if mask_pair[side] == support for key in columns}
            for degree in counts:
                cell = (side, 'count', index, degree)
                row = {key: 1 for key in margins[side, support, degree]}
                if cell in model.bounds:
                    row[cell] = -1
                model.eq(row, 0, f'same_W_degree_{side}_{support}_{degree}')
            for peer_support in ((0,), *peer_doubles):
                peer_index = signatures.index(peer_support)
                cell = (side, 'edge', *sorted((index, peer_index)))
                row = {key: -(int(peer_support[1] in opp) if len(peer_support) == 2
                              else sum(index > cross_count for index in opp))
                       for key, opp in opposite.items()}
                if cell in model.bounds:
                    row[cell] = 1
                model.eq(row, 0, f'same_cross_edges_{side}_{support}_{peer_support}')
        for anchor in range(1, width):
            noncross = range(cross_count + 1, width)
            lower = private - 1 + int(anchor <= cross_count)
            for size in range(1, private + 1):
                for targets in combinations(noncross, size):
                    need = lower - (private - size)
                    if need <= 0:
                        continue
                    row = {key: -1 for pair, keys in jointly.items() if pair[side] == (anchor,)
                           and set(targets).intersection(pair[1 - side]) for key in keys}
                    model.le(row, -need, f'peer_matching_{side}_{anchor}_{targets}')

    for degree, count in counts.items():
        wing = sum(side[1:].count(degree) for side in degrees)
        model.eq({key: 1 for key in deg_mass[degree]}, count - wing - 2 * (degree == width), 'joint_degree_mass')
    for first in range(1, width):
        for second in range(1, width):
            common = {key: 1 for (left, right), keys in jointly.items() if first in left and second in right for key in keys}
            if first == second and first <= cross_count:
                assert not common
                continue
            model.le({key: -1 for key in common}, -1, f'cross_pair_dominated_{first}_{second}')
            if min_residue == 6:
                model.le(common, degrees[0][first] + degrees[1][second] - 11, f'cross_cap_{first}_{second}')

    if star:
        occupied = [(sum(1 << (index - 1) for index in left) |
                     sum(1 << (width - 2 + index) for index in right), keys)
                    for (left, right), keys in jointly.items()]
        double_wing_order = 2 * (width - 1)
        cross_masks = tuple((1 << index) | (1 << (width - 1 + index)) for index in range(cross_count))
        for allowed in range(1, 1 << double_wing_order):
            outside = double_wing_order - allowed.bit_count() - sum(not allowed & crossing for crossing in cross_masks)
            maximum = alpha - outside
            for anchor in vertices(allowed):
                if maximum >= degrees[anchor // (width - 1)][1 + anchor % (width - 1)]:
                    continue
                row = {key: 1 for support, keys in occupied if (support >> anchor & 1) and not support & ~allowed
                       for key in keys}
                if row:
                    model.le(row, maximum, f'joint_independent_star_{allowed}_{anchor}')
    return model


def joint_assignment(adj, roots, wings, doubles, model):
    width = len(wings[0]) + 1
    assignment = Counter()
    for side, (root, own) in enumerate(zip(roots, wings)):
        neighborhood = (roots[1 - side], *own)
        outside = tuple(vertices(((1 << len(adj)) - 1) & ~(adj[root] | 1 << root)))
        supports = {vertex: tuple(index for index, anchor in enumerate(neighborhood) if adj[vertex] >> anchor & 1)
                    for vertex in outside}
        signatures = groups(width, doubles[side])
        for vertex, support in supports.items():
            assignment[side, 'count', signatures.index(support), adj[vertex].bit_count()] += 1
        for first, second in combinations(outside, 2):
            if adj[first] >> second & 1:
                pair = sorted((signatures.index(supports[first]), signatures.index(supports[second])))
                assignment[(side, 'edge', *pair)] += 1
    kept = set(range(len(adj))).difference(roots, *wings)
    for vertex in kept:
        left, right = (tuple(index for index, anchor in enumerate(wing, 1) if adj[vertex] >> anchor & 1)
                       for wing in wings)
        assignment['site', left, right, adj[vertex].bit_count()] += 1
    validate(model, assignment)
    return assignment


def control_graph(adj, width, alpha):
    assert graph.alpha(adj) == alpha and graph.triangle_free(adj)
    assert all(adj[first] & adj[second] or adj[first] >> second & 1
               for first, second in combinations(range(len(adj)), 2))
    private = alpha + 1 - width
    cross_count = width - 1 - private
    equality = width + 2 * (len(adj) - width - 1) - width * private
    counts = Counter(map(int.bit_count, adj))
    tested = 0
    rejected = Counter()
    for left, right in combinations(range(len(adj)), 2):
        if not (adj[left] >> right & 1):
            continue
        if any(adjacency.bit_count() != width or sum(adj[vertex].bit_count() for vertex in vertices(adjacency)) != equality
               for adjacency in (adj[left], adj[right])):
            continue
        roots = (left, right)
        wings = [list(vertices(adj[root] & ~(1 << roots[1 - side]))) for side, root in enumerate(roots)]
        cross = [(first, second) for first in wings[0] for second in wings[1] if adj[first] >> second & 1]
        assert len(cross) == cross_count
        wings = [list(ends) + [vertex for vertex in wing if vertex not in ends] for wing, ends in zip(wings, zip(*cross))]
        assert all(len(wing) == width - 1 and len(set(wing)) == width - 1 for wing in wings)
        doubles = []
        for side, (root, wing) in enumerate(zip(roots, wings)):
            anchors = (roots[1 - side], *wing)
            outside = tuple(vertices(((1 << len(adj)) - 1) & ~(adj[root] | 1 << root)))
            signatures = [tuple(index for index, anchor in enumerate(anchors) if adj[vertex] >> anchor & 1)
                          for vertex in outside]
            doubles.append(tuple(sorted(support for support in signatures if len(support) == 2)))
        model = paired_model(doubles, width, private, counts, sum(map(int.bit_count, adj)) // 2, star=True)
        assignment = joint_assignment(adj, roots, wings, doubles, model)
        sites = [key for key in assignment if key[0] == 'site']
        for first, second in combinations(sites, 2):
            if first[1] == second[1] or first[2] == second[2] or first[3] != second[3]:
                continue
            corrupt = assignment.copy()
            for old, new in ((first, second), (second, first)):
                corrupt[old] -= 1
                corrupt['site', old[1], new[2], old[3]] += 1
            try:
                validate(model, +corrupt)
            except AssertionError as error:
                reason = error.args[0][0] if error.args else 'cross-triangle'
                rejected[reason.partition('_')[0]] += 1
        tested += 1
    return tested, rejected


def controls():
    adj = [sum(1 << ((vertex + step) % 13) for step in (1, -1, 5, -5)) for vertex in range(13)]
    tested, broken = control_graph(adj, 4, 4)
    assert tested == 26 and broken['cross-triangle'] and sum(broken.values()) > broken['cross-triangle']
    print(f'C13(1,5): {tested} actual adjacent equality pairs accepted, {sum(broken.values())} broken alignments rejected', broken)


def integer(model, cap):
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    from warnings import catch_warnings, simplefilter

    indices = {key: index for index, key in enumerate(model.bounds)}
    terms, rows, columns, rhs = [], [], [], []
    for index, (row, bound, _) in enumerate(model.rows):
        rhs.append(bound)
        for key, coefficient in row.items():
            rows.append(index)
            columns.append(indices[key])
            terms.append(coefficient)
    matrix = coo_matrix((terms, (rows, columns)), shape=(len(rhs), len(indices))).tocsc()
    with catch_warnings():
        simplefilter('ignore', RuntimeWarning)
        result = milp(np.zeros(len(indices)), integrality=np.ones(len(indices)),
                      bounds=Bounds(0, tuple(model.bounds.values())),
                      constraints=LinearConstraint(matrix, -inf, rhs),
                      options={'threads': 1, 'time_limit': cap, 'presolve': True})
    if result.x is None:
        return f'mip-{result.status}', None
    assignment = {key: int(round(number)) for key, number in zip(indices, result.x) if int(round(number))}
    validate(model, assignment)
    return 'integer-witness', assignment


def roster(pair):
    baseline, _ = ledger()
    survivors, _ = live_cases(baseline)
    raw, single = root_signatures()
    shapes = side_shapes()
    pair_shapes = [(first + '+' + second, (shapes[first], shapes[second]))
                   for first, second in combinations_with_replacement(sorted(shapes), 2)]
    print(f'roster: {raw} single labelled masks, {len(single)} orbits, {len(pair_shapes)} unordered wing pairs', flush=True)
    for key in sorted(survivors):
        edges, *population = key
        if edges != 170 or population[0] != (2 if pair else 1):
            continue
        counts = counts_map(population)
        if not pair:
            for tag, signature, required in single:
                if feasible_histogram(counts, required):
                    yield key, str(tag), signature
            continue
        for tag, signature in pair_shapes:
            required = Counter([6, 6, *(degree for wing in signature for degree in root_degrees(6, 4, wing)[1:])])
            if feasible_histogram(counts, required):
                yield key, tag, signature


def make_model(pair, key, signature):
    counts = counts_map(key[1:])
    model = (paired_model(signature, 6, 4, counts, key[0], min_residue=6, star=True) if pair else
             supports_model(signature, 6, 4, counts, key[0], strengthen=True, target=True))
    return compact(model)


def replay(mode, directory):
    pair = mode == 'pair'
    expected = {(key, tag): signature for key, tag, signature in roster(pair)}
    tally = Counter()
    seen = set()
    for line in (directory / f'{mode}.witnesses.jsonl').read_text().splitlines():
        record = json.loads(line)
        identity = tuple(record['key']), record['tag']
        assert identity not in seen and identity in expected
        seen.add(identity)
        model = make_model(pair, identity[0], expected[identity])
        if record['status'] == 'integer-witness':
            columns = tuple(model.bounds)
            validate(model, {columns[int(index)]: amount for index, amount in record['artifact'].items()})
        else:
            assert record['status'] == 'farkas'
            assert verify(model, {int(index): Fraction(amount) for index, amount in record['artifact'].items()})
        tally[record['status']] += 1
    print(f'{mode}: {len(seen)}/{len(expected)} exact replays; {dict(tally)}', flush=True)


def run(mode, directory, cap, maximum):
    pair = mode == 'pair'
    tally = Counter()
    print('key,template,columns,rows,status,cpu', flush=True)
    with (directory / f'{mode}.witnesses.jsonl').open('w') as witness:
        for index, (key, tag, signature) in enumerate(roster(pair)):
            if maximum and index >= maximum:
                break
            start = process_time()
            model = make_model(pair, key, signature)
            status, artifact = integer(model, cap)
            if status == 'mip-2':
                exact, weights = solve(model)
                if exact == 'cert':
                    status, artifact = 'farkas', weights
            tally[status] += 1
            print(','.join(map(str, (*key, tag, len(model.bounds), len(model.rows), status, f'{process_time()-start:.4f}'))),
                  flush=True)
            if artifact is not None:
                if status == 'integer-witness':
                    artifact = {str(index): artifact[column] for index, column in enumerate(model.bounds) if column in artifact}
                print(json.dumps({'key': key, 'tag': tag, 'status': status, 'artifact': artifact}), file=witness, flush=True)
    print(dict(tally), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'single', 'pair'))
    parser.add_argument('path', type=Path)
    parser.add_argument('--cap', type=float, default=4)
    parser.add_argument('--maximum', type=int, default=0)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.mode == 'control':
        controls()
    elif args.verify:
        replay(args.mode, args.path)
    else:
        run(args.mode, args.path, args.cap, args.maximum)


if __name__ == '__main__':
    main()
