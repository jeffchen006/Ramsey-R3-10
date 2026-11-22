"""Rebuild P3 singleton blockers and check small exact capacity witnesses."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from math import comb
from pathlib import Path

from p3_high_f import NO_HOLE, classify, control as layout_control, filter_target, layouts
from p3_round4_index import census, has_independent
from path_three_top import plant


def bitset(vertices):
    return sum(1 << vertex for vertex in vertices)


def points(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def independent_levels(graph):
    levels = [[] for _ in range(len(graph) + 1)]

    def extend(chosen, todo, size):
        levels[size].append(chosen)
        for point in points(todo):
            todo ^= 1 << point
            extend(chosen | (1 << point), todo & ~graph[point], size + 1)

    extend(0, (1 << len(graph)) - 1, 0)
    return levels


def boundary_direct(wing):
    edges = set()
    roots = ((0, 1, 2, 6, 7, 8, 9, 10, 11),
             (6, 7, 8, 9, 10, 11, 12, 13, 14),
             (3, 4, 5, 6, 7, 8, 9, 12, 13))
    for vertex, neighbours in enumerate(roots, 15):
        edges.update((other, vertex) for other in neighbours)
    edges.update((vertex, other) for vertex in range(3) for other in (12, 13, 14)
                 if (vertex, other) != (0, 14))
    edges.update((vertex, other) for vertex in range(3, 6) for other in (10, 11, 14)
                 if (vertex, other) != (3, 14))
    edges.add((0, 3))
    if wing == 3:
        edges.add((0, 4))
    return [bitset(high if low == vertex else low for low, high in edges
                   if vertex in (low, high)) for vertex in range(18)]


def attachment_masks(graph, levels, alpha, low, high, root_cap):
    nonroots = len(graph) - 3
    return sorted(mask for size in range(low, high + 1) for mask in levels[size]
                  if mask < (1 << nonroots)
                  and all(mask & maximum for maximum in levels[alpha])
                  and all((root & mask).bit_count() <= root_cap for root in graph[-3:]))


def scout_witness(graph, levels, masks, wing):
    common = bitset(range(6, 10))
    blockers = [bitset((0, 1, 2, 10, 11)), bitset((3, 4, 5, 12, 13)),
                bitset((10, 11, 12, 13, 14)),
                bitset((0, 1, 2, 4, 5) if wing == 1 else (1, 2, 3, 4, 5))]
    assert not any(not mask & common for mask in masks)
    for vertex in points(common):
        tag = 1 << vertex
        padded = [blocker | (common ^ tag) for blocker in blockers]
        assert all(not blocker & common and blocker in levels[5] for blocker in blockers)
        assert all(blocker in levels[8] for blocker in padded)
        assert all(not (graph[vertex] & blocker) for blocker in blockers)
        selected = [mask for mask in masks if mask & common == tag]
        uncovered = [sum(all(mask & blocker for blocker in padded[:count]) for mask in selected)
                     for count in (4, 3)]
        assert len(selected) == {1: 112, 3: 105}[wing] and uncovered == [0, 17]
        print('scout', wing, 'tag', vertex, 'q_masks', 0, 'single_masks', len(selected),
              'uncovered', uncovered[0], 'omit-fourth', uncovered[1])


def capacity_rows(graph, levels, masks, alpha, degree, cap, order, strong=False):
    nonroots = len(graph) - 3
    rows = {}

    def at_most(name, bound, condition):
        selected = tuple(index for index, mask in enumerate(masks) if condition(mask))
        if selected:
            rows[name] = (bound, selected)

    at_most('order', order, lambda mask: True)
    for vertex in range(nonroots):
        deficit = degree - graph[vertex].bit_count()
        at_most(f'deg:{vertex}', deficit, lambda mask: mask >> vertex & 1)
        at_most(f'not-deg:{vertex}', order - deficit, lambda mask: not mask >> vertex & 1)
    for first, second in combinations(range(nonroots), 2):
        if graph[first] >> second & 1:
            continue
        common = (graph[first] & graph[second]).bit_count()
        both = (1 << first) | (1 << second)
        at_most(f'pair:{first},{second}', cap - common, lambda mask: mask & both == both)
        if strong and common == 0:
            at_most(f'not-pair:{first},{second}', order - 1, lambda mask: mask & both != both)
    for size, limit, tagged_limit in ((alpha - 1, 2, 1), (alpha - 2, 5, 2), (alpha - 3, 8, 3)):
        if size != alpha - 1 and not strong:
            continue
        for avoid in levels[size]:
            keep = {mask for mask in masks if not mask & avoid}
            if not keep:
                continue
            possible_edge = any(not (first & second) for first in keep for second in keep)
            at_most(f'avoid:{avoid}', limit if possible_edge else tagged_limit, keep.__contains__)
            for tag in range(nonroots):
                if not ((1 << tag) & avoid):
                    at_most(f'tag:{tag},{avoid}', tagged_limit, lambda mask: mask in keep and mask >> tag & 1)
    return rows


def control():
    layout_control()
    core, graph, full = plant()
    assert not has_independent(full, (1 << len(full)) - 1, 7)
    assert all(full[vertex].bit_count() == 6 and not (full[vertex] & full[other])
               for vertex in range(len(full)) for other in points(full[vertex]))
    common = graph[-1] & graph[-2] & graph[-3]
    assert common.bit_count() == 2
    actual = [full[vertex] >> len(core) for vertex in range(len(core))]
    levels = independent_levels(graph)
    assert not has_independent(core, (1 << len(core)) - 1, 4)
    assert all(2 <= degree.bit_count() <= 3 for degree in core)
    masks = attachment_masks(graph, levels, 6, 3, 4, 4)
    assert set(actual) <= set(masks)
    counts = Counter(actual)
    zero, single = (sum((mask & common).bit_count() == size for mask in actual) for size in (0, 1))
    incidence = sum((mask & common).bit_count() for mask in actual)
    assert incidence == 2 * len(core) - single - 2 * zero
    rows = capacity_rows(graph, levels, masks, 6, 6, 4, len(core), strong=True)
    assert all(sum(counts[masks[index]] for index in indices) <= bound for bound, indices in rows.values())
    zero_masks, q_bound, _, patterns = zero_compatibility(masks, common, levels[5], len(core), known=actual)
    assert q_bound >= zero
    zero_attach = [mask for mask in actual if not mask & common]
    upper = tagged_counts(masks, common, levels[5], zero_attach, 6 - 3)
    assert all(sum(mask & common == 1 << tag for mask in actual) <= bound for tag, bound in upper.items())
    print('control C21', 'order', len(core), 'zero', zero, 'single', single, 'rows', len(rows))


def zero_compatibility(masks, common, blockers, order, known=()):
    zeros = [mask for mask in masks if not mask & common]
    assert len(zeros) <= 15
    rows = {}
    for blocker in blockers:
        avoiders = [index for index, mask in enumerate(zeros) if not mask & blocker]
        if not avoiders:
            continue
        key = bitset(avoiders)
        cap = 2 if any(not (zeros[first] & zeros[second]) for first in avoiders for second in avoiders) else 1
        rows[key] = min(rows.get(key, cap), cap)
    full = (1 << len(zeros)) - 1
    best = [order] * (full + 1)
    best[0] = 0
    for used in range(full + 1):
        for row, cap in rows.items():
            best[used | row] = min(best[used | row], best[used] + cap)
    bound = best[full]
    def compatible(pattern):
        forced = set()
        for row, cap in rows.items():
            avoiding = [index for index, tag in enumerate(pattern) if row >> tag & 1]
            if len(avoiding) > cap:
                return False
            if len(avoiding) == 2:
                first, second = avoiding
                if zeros[pattern[first]] & zeros[pattern[second]]:
                    return False
                forced.add((first, second))
        return not any((first, second) in forced and (second, third) in forced and (first, third) in forced
                       for first, second, third in combinations(range(len(pattern)), 3))

    if known:
        assert compatible(tuple(sorted(zeros.index(mask) for mask in known if not mask & common)))
    raw_count = comb(len(zeros) + bound, bound)
    if raw_count > 250_000:
        return zeros, bound, raw_count, None
    raw, patterns = 0, []
    for size in range(bound + 1):
        for pattern in combinations_with_replacement(range(len(zeros)), size):
            raw += 1
            if compatible(pattern):
                patterns.append(pattern)
    assert raw_count == raw
    return zeros, bound, raw, patterns


def tagged_counts(masks, common, blockers, zero_attach, cap):
    def avoids(mask):
        return bitset(index for index, blocker in enumerate(blockers) if not blocker & mask)

    zero_signatures = [(mask, avoids(mask)) for mask in zero_attach]
    bounds = {}
    for tag in points(common):
        candidates = [avoids(mask) for mask in masks if mask & common == 1 << tag
                      and all(not (mask & other and avoids(mask) & signature) for other, signature in zero_signatures)]
        if 0 in candidates:
            bounds[tag] = cap
            continue
        candidates = sorted(set(candidates), key=int.bit_count)
        spaces = [(1 << len(candidates)) - 1] * len(candidates)
        for first, left in enumerate(candidates):
            spaces[first] ^= (1 << (first + 1)) - 1
            for second in range(first + 1, len(candidates)):
                if left & candidates[second]:
                    spaces[first] ^= 1 << second

        def feasible(space, need):
            if need == 0:
                return True
            while space.bit_count() >= need:
                lowest = space & -space
                space ^= lowest
                if feasible(space & spaces[lowest.bit_length() - 1], need - 1):
                    return True
            return False

        bounds[tag] = next(count for count in range(cap, -1, -1) if feasible((1 << len(candidates)) - 1, count))
    return bounds


def score_witness(rows, goal, witness):
    assert witness and all(type(weight) is int and weight > 0 for weight in witness.values())
    scale = witness.pop('scale') if 'scale' in witness else 1
    coefficients = [0] * len(goal)
    cost = 0
    for name, weight in witness.items():
        bound, indices = rows[name]
        cost += weight * bound
        for index in indices:
            coefficients[index] += weight
    assert all(value >= scale * required for value, required in zip(coefficients, goal))
    assert cost < 20 * scale
    return cost, scale


def discover(rows, goal):
    from scipy.optimize import linprog
    from scipy.sparse import csc_array

    bounds, products, coordinates = [], [], []
    for number, (bound, indices) in enumerate(rows.values()):
        bounds.append(bound)
        products.extend(indices)
        coordinates.extend([number] * len(indices))
    matrix = csc_array(([-1.] * len(products), (products, coordinates)), shape=(len(goal), len(rows)))
    solved = linprog(bounds, A_ub=matrix, b_ub=[-value for value in goal], method='highs',
                     options={'time_limit': 5., 'threads': 1})
    if solved.status != 0:
        return solved.message, None
    for scale in (1, 2, 3, 4, 6, 12, 24, 60, 1000):
        if solved.fun >= 20 - 1e-7:
            break
        witness = {name: round(weight * scale) for name, weight in zip(rows, solved.x)
                   if round(weight * scale) > 0}
        witness['scale'] = scale
        try:
            score_witness(rows, goal, witness.copy())
        except AssertionError:
            continue
        return solved.fun, witness
    return solved.fun, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('bindings', type=Path)
    parser.add_argument('--discover', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--tagged', action='store_true')
    args = parser.parse_args()
    control()
    entries = census(args.catalogue)
    expected = json.loads(args.verify.read_text()) if args.verify else {}
    discovered = {}
    bindings = ['diagonal\tedges\tlayout\tboundary_sha256\trow\tg6_sha256']
    for size, key in layouts(9, 6, 4, 8, 16, 18):
        if NO_HOLE in key[1:]:
            continue
        graph = classify(9, 6, 4, key)
        if filter_target(graph) != 'pass':
            continue
        assert size == 16 + key[0].bit_count()
        edge_count = 45 + size
        digest = sha256(','.join(map(str, graph)).encode()).hexdigest()
        levels = independent_levels(graph)
        masks = attachment_masks(graph, levels, 9, 3, 5, 5)
        common = bitset(range(6, 10))
        counts = Counter((mask & common).bit_count() for mask in masks)
        print('layout', edge_count, key, 'T-mask counts', sorted(counts.items()))
        zero_masks, zero_upper, zero_raw, zero_patterns = zero_compatibility(masks, common, levels[8], 22)
        assert len(zero_masks) == counts[0]
        print('zero-patterns', 'q<=', zero_upper, 'raw', zero_raw, 'ledgers',
              sorted(Counter(map(len, zero_patterns)).items()) if zero_patterns is not None else 'defer')
        if args.tagged and zero_patterns is not None:
            costs, live = Counter(), Counter()
            for pattern in zero_patterns:
                bound = tagged_counts(masks, common, levels[8], [zero_masks[index] for index in pattern], 6)
                total = sum(bound.values()) + 2 * len(pattern)
                costs[len(pattern), total] += 1
                if total >= 20:
                    live[len(pattern)] += 1
            print('zero-conditioned singleton caps', sorted(costs.items()), 'live', sorted(live.items()))
        is_scout = key in ((1, (0, 1), (0, 1)), (3, (0, 1), (0, 1)))
        slug = ':'.join(map(str, (key[0], *key[1], *key[2])))
        if is_scout:
            assert graph == boundary_direct(key[0])
            scout_witness(graph, levels, masks, key[0])
        if args.discover or slug in expected:
            rows = capacity_rows(graph, levels, masks, 9, 9, 6, 22, strong=True)
            goal = [max(0, 2 - (mask & common).bit_count()) for mask in masks]
        if args.discover:
            status, witness = discover(rows, goal)
            print('dual-search', slug, status, 'checked', witness is not None)
            if witness:
                discovered[slug] = witness
        if slug in expected:
            score = score_witness(rows, goal, expected.pop(slug))
            print('exact cover', slug, score)
        else:
            score = None
        if is_scout or score:
            for index, (edges, graph_hash) in entries.items():
                if edges == edge_count:
                    bindings.append(f'4\t{edges}\t{slug}\t{digest}\t{index}\t{graph_hash}')
    assert not expected
    args.bindings.write_text('\n'.join(bindings) + '\n')
    if args.discover:
        args.discover.write_text(json.dumps(discovered, indent=2, sort_keys=True) + '\n')
    print('bindings', len(bindings) - 1)


if __name__ == '__main__':
    main()
