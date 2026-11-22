#!/usr/bin/env python3
"""Literal independent replay on small rectangles and translated C13 decks."""

from collections import Counter, defaultdict
from itertools import combinations, permutations, product
import json
import sys
from time import process_time

from crown23_factor import (bits, crown_witness, graph, hall_failure, induced,
                            independent_witness, matching_failure, shared_colors,
                            stitch, supported)


def all_subsets(items):
    for size in range(len(items) + 1):
        yield from combinations(items, size)


def small_factors(left_count, right_count):
    pairs = tuple(product(range(left_count), range(right_count)))
    counts = Counter()
    for available in all_subsets(pairs):
        allowed = tuple(sum(1 << other for vertex, other in available if vertex == index)
                        for index in range(left_count))
        capacities = tuple(sum(vertex == index for vertex, other in available) for index in range(left_count))
        capacities += tuple(sum(other == index for vertex, other in available) for index in range(right_count))
        feasible = defaultdict(set)
        for subset in all_subsets(available):
            needs = tuple(sum(vertex == index for vertex, other in subset) for index in range(left_count))
            needs += tuple(sum(other == index for vertex, other in subset) for index in range(right_count))
            feasible[needs].update(subset)
        for demands in product(*(range(capacity + 1) for capacity in capacities)):
            left, right = demands[:left_count], demands[left_count:]
            fail, union = supported(allowed, left, right)
            counts['instances'] += 1
            if demands in feasible:
                assert fail is None
                assert union == tuple(sum(1 << other for vertex, other in feasible[demands] if vertex == index)
                                      for index in range(left_count))
                counts['factor_positive'] += 1
            elif sum(left) == sum(right):
                assert fail[0] == 'cut'
                _, mask, demand, capacity = fail
                selected = {vertex for vertex in range(left_count) if (mask >> vertex) & 1}
                assert demand == sum(left[vertex] for vertex in selected)
                assert capacity == sum(min(right[index], sum((vertex, index) in available for vertex in selected))
                                       for index in range(right_count))
                assert demand > capacity
                counts['cut_negative'] += 1
            else:
                assert fail[0] == 'totals'
                counts['totals_negative'] += 1
    print(f'SMALL {left_count}x{right_count}: {dict(counts)}', flush=True)


def isos(first, second, color_first=None, color_second=None):
    order = len(first)
    candidates = tuple(tuple(other for other in range(order)
                             if row.bit_count() == second[other].bit_count()
                             and (color_first is None or color_first[vertex] == color_second[other]))
                       for vertex, row in enumerate(first))
    sequence = tuple(sorted(range(order), key=lambda vertex: (len(candidates[vertex]), vertex)))
    images = {}

    def visit(index, used):
        if index == order:
            yield tuple(images[vertex] for vertex in range(order))
            return
        vertex = sequence[index]
        for other in candidates[vertex]:
            if used & (1 << other):
                continue
            if any(((first[vertex] >> known) ^ (second[other] >> image)) & 1
                   for known, image in images.items()):
                continue
            images[vertex] = other
            yield from visit(index + 1, used | (1 << other))
            del images[vertex]

    yield from visit(0, 0)


def sets(rows):
    return tuple(set(bits(row)) for row in rows)


def no_edges(adjacency, selected):
    return all(right not in adjacency[left] for left, right in combinations(selected, 2))


def literal_cards(one, two, shared_count):
    shift = len(one) - shared_count
    left = sets(one)
    right = sets(two)

    def image(vertex):
        return vertex if vertex < shared_count else vertex + shift

    merged = [set(row) for row in left] + [set() for vertex in two[shared_count:]]
    for vertex, row in enumerate(right):
        merged[image(vertex)].update(map(image, row))
    return merged


def literal_factors(merged, left, right, degrees):
    visits = 0
    accepted = []
    pairs = tuple(product(left, right))
    delta = tuple(degree - len(row) for degree, row in zip(degrees, merged))
    total = sum(delta)
    if total < 0 or total % 2:
        return visits, accepted
    for selected in combinations(pairs, total // 2):
        visits += 1
        gained = Counter(vertex for pair in selected for vertex in pair)
        if any(gained[vertex] != needed for vertex, needed in enumerate(delta)):
            continue
        if any(merged[vertex] & merged[other] for vertex, other in selected):
            continue
        accepted.append(selected)
    return visits, accepted


def completed(merged, edges):
    result = [set(row) for row in merged]
    for left, right in edges:
        result[left].add(right)
        result[right].add(left)
    return result


def circulant_decks(width):
    start = process_time()
    target = graph(13, ((index, (index + step) % 13) for index in range(13) for step in (1, 5)))
    target_sets = sets(target)
    assert not any(no_edges(target_sets, selected) for selected in combinations(range(13), 5))
    assert any(no_edges(target_sets, selected) for selected in combinations(range(13), 4))
    shares = 13 - 2 * width
    degrees = (4,) * 13
    counts = Counter()
    fixtures = {}
    oracle_seconds = fast_seconds = 0.0
    cases = set()
    for left in combinations(range(13), width):
        if not no_edges(target_sets, left):
            continue
        for step in range(1, 13):
            right = tuple(sorted((vertex + step) % 13 for vertex in left))
            if set(left) & set(right) or left > right or (left, right) in cases:
                continue
            cases.add((left, right))
            overlap = tuple(sorted(set(range(13)) - set(left) - set(right)))
            overlap_graph = induced(target, overlap)
            one = induced(target, overlap + left)
            two0 = induced(target, overlap + right)
            left_color, right_color = shared_colors(one, two0, shares, degrees)
            colored = set(isos(overlap_graph, overlap_graph, left_color, right_color))
            counts['decks'] += 1
            left_places = tuple(range(shares, shares + width))
            right_places = tuple(range(shares + width, 13))
            for image in isos(overlap_graph, overlap_graph):
                counts['alignments'] += 1
                two = induced(target, tuple(overlap[index] for index in image) + right)
                merged = literal_cards(one, two, shares)
                shared_bad = any(len(merged[vertex]) != degrees[vertex] for vertex in range(shares))
                assert (image in colored) == (not shared_bad)
                answer = None
                clock = process_time()
                stage, receipt = stitch(one, two, shares, degrees)
                if stage == 'rectangle':
                    assert sets(receipt.lower) == tuple(merged)
                    failure, union = supported(receipt.allowed, receipt.left_need, receipt.right_need)
                    if failure is not None:
                        stage, answer = 'hall', failure
                    else:
                        upper = receipt.with_edges(union)
                        witness = independent_witness(upper, 5)
                        if witness is None:
                            stage = 'live'
                        else:
                            stage, answer = 'upper-I5', tuple(bits(witness))
                            assert no_edges(sets(upper), answer)
                else:
                    answer = receipt
                fast_seconds += process_time() - clock
                counts[stage] += 1
                clock = process_time()
                visits, factors = literal_factors(merged, left_places, right_places, degrees)
                counts['literal_rectangles'] += visits
                if stage == 'shared-degree':
                    assert shared_bad and not factors
                elif stage == 'hall':
                    assert not shared_bad and not factors and answer[0] == 'cut'
                else:
                    assert factors
                    expected = set(pair for factor in factors for pair in factor)
                    assert {(left_places[index], right_places[other])
                             for index, row in enumerate(union) for other in bits(row)} == expected
                exact = 0
                for factor in factors:
                    full = completed(merged, factor)
                    if not any(no_edges(full, selected) for selected in combinations(range(13), 5)):
                        exact += 1
                        assert stage == 'live'
                        as_masks = tuple(sum(1 << other for other in row) for row in full)
                        assert next(isos(as_masks, target), None) is not None
                    if stage == 'upper-I5':
                        assert no_edges(full, answer)
                oracle_seconds += process_time() - clock
                counts['literal_factors'] += len(factors)
                counts['exact_completions'] += exact
                counts['exact_positive_alignments'] += exact > 0
                if image == tuple(range(shares)):
                    assert stage == 'live' and exact > 0
                    counts['plants'] += 1
                elif stage == 'live' and not exact:
                    counts['live_but_no_completion'] += 1
                if stage not in fixtures:
                    fixtures[stage] = dict(left=left, right=right, overlap=overlap, image=image,
                                           one=one, two=two, receipt=answer, oracle_factors=len(factors),
                                           oracle_completions=exact)
    assert counts['decks'] == counts['plants'] > 0
    assert counts['shared-degree'] > 0
    print(f'C13 width={width}: {dict(counts)}', flush=True)
    for stage, row in sorted(fixtures.items()):
        print(f'FIXTURE C13/{width}/{stage} {json.dumps(row, sort_keys=True)}', flush=True)
    print(f'TIME C13/{width} full={process_time() - start:.6f} filter={fast_seconds:.6f} '
          f'literal={oracle_seconds:.6f}', file=sys.stderr)


def crown_padding():
    moved = tuple(product(range(2), range(4)))
    edges = {frozenset((first, second)) for first, second in combinations(moved, 2)
             if first[0] != second[0] and first[1] != second[1]}
    caps = (5, 6, 7, 7, 9)
    for touched in all_subsets(tuple(range(4))):
        available = tuple(site for site in moved if site[1] not in touched)
        allowed = tuple(chosen for chosen in all_subsets(available)
                        if not any(frozenset(pair) in edges for pair in combinations(chosen, 2)))
        assert 9 - max(map(len, allowed)) == caps[len(touched)]
    assert crown_witness(graph(8, ()), (3, 12, 48, 192)) is None
    assert crown_witness(graph(9, ()), (3, 28, 224, 256)) == (8, 255)
    print('PADDING all 16 touched-role sets matched literal moved-set enumeration', flush=True)


def physical_rectangle(allowed):
    width = len(allowed)
    blocks = tuple((left, right) for left, right in product(range(width), repeat=2)
                   if not allowed[left] & (1 << right))
    shared = len(blocks)
    one = graph(shared + width, ((vertex, shared + left) for vertex, (left, right) in enumerate(blocks)))
    two = graph(shared + width, ((vertex, shared + right) for vertex, (left, right) in enumerate(blocks)))
    degrees = (2,) * shared + tuple(row.bit_count() + 1 for row in one[shared:] + two[shared:])
    return shared, one, two, degrees


def adversarial_rectangles():
    shared, one, two, degrees = physical_rectangle((1, 1, 6))
    assert next(isos(one, two), None) is not None
    stage, rectangle = stitch(one, two, shared, degrees)
    assert stage == 'rectangle'
    assert rectangle.allowed == (1, 1, 6)
    assert rectangle.left_need == rectangle.right_need == (1, 1, 1)
    assert all(rectangle.allowed) and (rectangle.allowed[0] | rectangle.allowed[1] | rectangle.allowed[2]) == 7
    assert hall_failure(rectangle.allowed, rectangle.left_need, rectangle.right_need) == ('cut', 3, 2, 1)
    merged = literal_cards(one, two, shared)
    left = tuple(range(shared, shared + 3))
    right = tuple(range(shared + 3, shared + 6))
    assert literal_factors(merged, left, right, degrees) == (84, [])
    counts = Counter()
    positive = None
    for image in permutations(range(shared)):
        permuted = induced(two, image + left)
        status, rect = stitch(one, permuted, shared, degrees)
        assert status == 'rectangle'
        failure, options = supported(rect.allowed, rect.left_need, rect.right_need)
        assert rect.left_need == rect.right_need == (1, 1, 1)
        _, factors = literal_factors(literal_cards(one, permuted, shared), left, right, degrees)
        assert bool(factors) == (failure is None)
        counts['positive_alignments' if factors else 'cut_alignments'] += 1
        if factors and positive is None:
            positive = image, options, factors[0]
    assert positive is not None
    print(f'HALL local capacities pass but S=3 demands 2 vs capacity 1; {dict(counts)}; positive={positive}')

    shared, one, two, degrees = physical_rectangle((3, 6, 5))
    assert shared == 3 and next(isos(one, two), None) is not None
    status, rect = stitch(one, two, shared, degrees)
    assert status == 'rectangle'
    assert supported(rect.allowed, rect.left_need, rect.right_need) == (None, (3, 6, 5))
    _, factors = literal_factors(literal_cards(one, two, shared), (3, 4, 5), (6, 7, 8), degrees)
    assert len(factors) == 2
    tested = 0
    for left_scope, right_scope, size in product(range(8), range(8), range(4)):
        found = any(sum(bool(left_scope & (1 << (vertex - 3)) and right_scope & (1 << (peer - 6)))
                        for vertex, peer in factor) >= size for factor in factors)
        assert matching_failure(rect.allowed, rect.left_need, rect.right_need, left_scope, right_scope, size) == (not found)
        tested += 1
    assert matching_failure(rect.allowed, rect.left_need, rect.right_need, 3, 5, 2)
    assert ((3 >> 0) & 1) and ((6 >> 2) & 1)
    nine_cycle = graph(9, ((vertex, (vertex + 1) % 9) for vertex in range(9)))
    for factor in factors:
        degrees_sets = completed(literal_cards(one, two, shared), factor)
        full = tuple(sum(1 << peer for peer in row) for row in degrees_sets)
        assert next(isos(full, nine_cycle), None) is not None
        assert independent_witness(full, 4) is not None and independent_witness(full, 5) is None
    print(f'JOINT {tested} scopes/sizes agree with two literal C9 factors; 0b011 x 0b101 cannot realize 2 matches')


def sparse_rectangles(width):
    base = tuple((index, width + index) for index in range(width - 1))
    extras = tuple(pair for pair in product(range(width), range(width, 2 * width)) if pair not in base)
    order = tuple(range(2 * width))
    counts = Counter()
    for option in (None, *extras):
        edges = base + (() if option is None else (option,))
        adj = sets(graph(2 * width, edges))
        max_sets = tuple(frozenset(candidate) for candidate in combinations(order, width + 1)
                         if no_edges(adj, candidate))
        assert any(no_edges(adj, candidate) for candidate in combinations(order, width))
        assert not any(no_edges(adj, candidate) for candidate in combinations(order, width + 2))
        isolates = tuple(vertex for vertex, neighbors in enumerate(adj) if not neighbors)
        if not max_sets:
            assert len(edges) == width and all(len(row) == 1 for row in adj)
            counts['perfect'] += 1
            continue
        common = set.intersection(*(set(option) for option in max_sets))
        if option is None:
            assert common == set(isolates) and len(isolates) == 2
            predicted = {frozenset((vertex,)) for vertex in isolates}
            counts['matching_plus_isolates'] += 1
        else:
            centers = {vertex for vertex, neighbors in enumerate(adj) if len(neighbors) == 2}
            ends = set.union(*(adj[vertex] for vertex in centers)) - centers
            if len(centers) == 1:
                assert len(ends) == 2 and len(isolates) == 1 and common == ends | set(isolates)
                predicted = {frozenset((vertex,)) for vertex in common}
                counts['path3'] += 1
            else:
                assert len(centers) == 2 and len(ends) == len(isolates) == 2 and common == set(isolates)
                predicted = {frozenset(ends)} | {frozenset((vertex,)) for vertex in isolates}
                counts['path4'] += 1
        actual = {frozenset(candidate) for candidate in all_subsets(order) if no_edges(adj, candidate)
                  and all(set(candidate) & maximum for maximum in max_sets)
                  and all(any(not (set(candidate) - {vertex}) & maximum for maximum in max_sets)
                          for vertex in candidate)}
        assert actual == predicted
    print(f'SPARSE width={width}: {dict(counts)}; literal independent blockers match')


def seven_edge_families():
    families = (('cycle4', 4, ((0, 1), (1, 2), (2, 3), (3, 0)), 2, ()),
                ('arms122', 6, ((0, 1), (0, 2), (2, 3), (0, 4), (4, 5)), 2, (1,)),
                ('arms112', 5, ((0, 1), (0, 2), (0, 3), (3, 4)), 1, (1, 2)))
    for name, component, edges, isolates, leaves in families:
        for width in ((component + isolates) // 2, 6):
            extra_edges = tuple((index, index + 1) for index in range(component, 2 * width - isolates, 2))
            adj = sets(graph(2 * width, edges + extra_edges))
            order = tuple(range(len(adj)))
            max_sets = tuple(frozenset(candidate) for candidate in combinations(order, width + 1)
                             if no_edges(adj, candidate))
            assert max_sets and not any(no_edges(adj, candidate) for candidate in combinations(order, width + 2))
            must_see = set(leaves) | set(range(2 * width - isolates, 2 * width))
            assert all(set(candidate) & must_see for candidate in all_subsets(order)
                       if no_edges(adj, candidate) and all(set(candidate) & maximum for maximum in max_sets))
            print(f'SPARSE+ {name} width={width}: {len(max_sets)} exact maximum independent sets')


def wide_deck_geometry():
    def site(role, parity, column):
        return 8 + 6 * role + 3 * parity + column

    edges = [(vertex, (vertex + 1) % 8) for vertex in range(8)]
    for vertex, role in product(range(8), range(4)):
        pos = (vertex // 2 - role) % 4
        edges.append((vertex, site(role, 1 - (vertex % 2), pos % 3)))
        if pos in (0, 1):
            edges.append((vertex, site(role, 1 - (vertex % 2), pos + 1)))
    for (first, second), parity, column in product(combinations(range(4), 2), range(2), range(3)):
        edges.append((site(first, parity, column), site(second, 1 - parity, column)))
        if (second - first) % 2:
            offset = 1 if parity == 0 else -1
            edges.append((site(first, parity, column), site(second, 1 - parity, (column + offset) % 3)))
    full = graph(32, edges)
    assert tuple(row.bit_count() for row in full) == (8,) * 8 + (7,) * 24
    group = tuple(tuple(range(8 + 6 * role, 14 + 6 * role)) for role in range(4))
    assert tuple(sum((full[vertex] & sum(1 << site for site in wing)).bit_count() for vertex in range(8))
                 for wing in group) == (12,) * 4
    counts = Counter()
    for left_role, right_role in combinations(range(4), 2):
        left, right = group[left_role], group[right_role]
        overlap = tuple(sorted(set(range(32)) - set(left) - set(right)))
        one, two = induced(full, overlap + left), induced(full, overlap + right)
        assert sum(row.bit_count() for row in one) == sum(row.bit_count() for row in two) == 148
        shift = (left_role - right_role) % 4

        def translate(vertex):
            return ((vertex + 2 * shift) % 8 if vertex < 8
                    else 8 + 6 * (((vertex - 8) // 6 + shift) % 4) + (vertex - 8) % 6)

        assert induced(full, tuple(translate(vertex) for vertex in overlap + left)) == one
        assert set(translate(vertex) for vertex in overlap + left) == set(overlap + right)
        status, rect = stitch(one, two, 20, (8,) * 8 + (7,) * 24)
        assert status == 'rectangle'
        options = tuple(sum(1 << index for index, other in enumerate(right) if full[vertex] & (1 << other))
                        for vertex in left)
        blocks = sum(row.bit_count() for row in options)
        assert blocks in (6, 12)
        assert all(row.bit_count() == (1 if blocks == 6 else 2) for row in options)
        assert rect.with_edges(options) == induced(full, overlap + left + right)
        fail, union = supported(rect.allowed, rect.left_need, rect.right_need)
        assert fail is None and all(not (known & ~envelope) for known, envelope in zip(options, union))
        common = induced(full, overlap)
        assert sum(row.bit_count() for row in common) // 2 == 32 + blocks
        group_masks = tuple(sum(1 << (overlap + left + right).index(vertex) for vertex in wing) for wing in group)
        assert crown_witness(rect.with_edges(union), group_masks) is not None
        changed = list(two)
        changed[0] ^= 2
        changed[1] ^= 1
        assert stitch(one, tuple(changed), 20, (8,) * 8 + (7,) * 24)[0] == 'sign'
        counts[blocks] += 1
    print(f'WIDTH6 geometry only, 26/e74 isomorphic cards and b=(12,12,12,12): {dict(counts)}; all fail crown alpha')


if __name__ == '__main__':
    small_factors(2, 3)
    small_factors(3, 3)
    circulant_decks(3)
    circulant_decks(4)
    crown_padding()
    adversarial_rectangles()
    for width in (3, 4, 5, 6):
        sparse_rectangles(width)
    seven_edge_families()
    wide_deck_geometry()
    assert hall_failure((3, 3), (1, 1), (1, 1)) is None
