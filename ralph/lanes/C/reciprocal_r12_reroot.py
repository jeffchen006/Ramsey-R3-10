from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import process_time

from reciprocal_audit import SOURCE22, decode


def sites(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def bits(sequence):
    return sum(1 << site for site in sequence)


def independent(adjacency, available, demand):
    if not demand:
        return 0
    while available.bit_count() >= demand:
        site = max(sites(available), key=lambda vertex: (available & adjacency[vertex]).bit_count())
        available ^= 1 << site
        child = independent(adjacency, available & ~adjacency[site], demand - 1)
        if child is not None:
            return child | (1 << site)
    return None


def add(graph, first, second):
    graph[first] |= 1 << second
    graph[second] |= 1 << first


def attach_masks(graph, roots, masks):
    for root, mask in zip(roots, masks, strict=True):
        for target in sites(mask):
            add(graph, root, target)


def setup(host, mark, degree, templates):
    order = len(host)
    start = order + 6
    left = tuple(range(order, order + 3))
    right = tuple(range(order + 3, order + 6))
    common = tuple(sites(mark[0] & mark[1] & mark[2]))
    assert len(common) == 2
    shared = ((1 << order) - 1) ^ (mark[0] | mark[1] | mark[2])
    petals = ((1 << order) - 1) ^ (shared | bits(common))
    outside = ((1 << len(templates)) - 1) << start
    lower = list(host) + [0] * (6 + len(templates))
    attach_masks(lower, right, mark)
    attach_masks(lower, right, (bits(left),) * 3)
    left_masks = tuple(bits(start + site for site, kind in enumerate(templates) if kind >> role & 1)
                       for role in range(3))
    assert all(mask.bit_count() == degree - 3 for mask in left_masks)
    attach_masks(lower, left, left_masks)
    assert all((host[vertex] & ~shared) == 0 for vertex in common)
    return lower, left, right, common, petals | shared, outside, left_masks


def wing_options(lower, vertex, outside, left_masks, degree, cap):
    for choice in combinations(tuple(sites(outside)), degree - lower[vertex].bit_count()):
        picked = bits(choice)
        if all((picked & mask).bit_count() <= cap - 3 for mask in left_masks):
            yield picked


def canonical(first, second, start, templates):
    kinds = list(zip(templates, [2 * (first >> (start + idx) & 1) + (second >> (start + idx) & 1)
                                for idx in range(len(templates))], strict=True))
    return all(type1 != type2 or code1 >= code2
               for (type1, code1), (type2, code2) in zip(kinds, kinds[1:]))


def build_upper(lower, variable_host, outside, cap):
    order = len(lower)
    upper = list(lower)
    spent = [bits(other for other in range(order) if other != vertex
                  and (neighbors & lower[other]).bit_count() == cap)
             for vertex, neighbors in enumerate(lower)]
    region = variable_host | outside
    for first in sites(outside):
        for second in sites(region & ~(1 << first)):
            if lower[first] & lower[second]:
                continue
            if (spent[first] & lower[second]) or (spent[second] & lower[first]):
                continue
            add(upper, first, second)
    return upper


def reject(lower, upper, centres, other_side, degree, cap):
    order = len(lower)
    universe = (1 << order) - 1
    for vertex, neighbors in enumerate(lower):
        if neighbors.bit_count() > degree or upper[vertex].bit_count() < degree:
            return 'degree', (vertex,)
        for other in range(vertex):
            if (neighbors & lower[other]).bit_count() > cap:
                return 'cap', (other, vertex)
            if not (upper[vertex] & (1 << other)) and not (upper[vertex] & upper[other]):
                return 'undominated', (other, vertex)
    for roots in (*combinations(centres, 3), other_side):
        union = bits(roots)
        for root in roots:
            union |= upper[root]
        assert all(lower[root] == upper[root] for root in roots)
        witness = independent(upper, universe ^ union, degree - 2)
        if witness is not None:
            return ('reroot' if roots != other_side else 'opposite'), (*roots, *sites(witness))
    witness = independent(upper, universe, degree + 1)
    if witness is not None:
        return 'unrestricted', tuple(sites(witness))
    return 'live', ()


def test_wings(lower, centres, other_side, common, variable_host, outside, degree, cap, first, second):
    attached = list(lower)
    attach_masks(attached, common, (first, second))
    upper = build_upper(attached, variable_host, outside, cap)
    return reject(attached, upper, centres, other_side, degree, cap)


def positive_cases():
    degree, cap = 8, 6
    graph = [{(site + shift) % 24 for shift in (1, -1, 4, -4, 6, -6, 11, -11)} for site in range(24)]
    original = [bits(row) for row in graph]
    assert all((original[site] & original[other]) == 0 for site in range(24) for other in graph[site])
    assert max(len(first & second) for first, second in combinations(graph, 2)) == cap
    assert independent(original, (1 << 24) - 1, degree + 1) is None
    left, right = (1, 11, 23), (0, 5, 12)
    assert set.intersection(*(graph[vertex] for vertex in left)) == set(right)
    host_original = set(range(24)) - set(left) - set.union(*(graph[vertex] for vertex in left))
    outside_original = set(range(24)) - set(left) - set(right) - host_original
    kind = lambda vertex: bits(index for index, root in enumerate(left) if vertex in graph[root])
    templates_order = sorted(outside_original, key=kind)
    for flip in (False, True):
        host_order = tuple(sorted(host_original, reverse=flip))
        ordering = host_order + left + right + tuple(templates_order)
        host = [bits(host_order.index(other) for other in graph[vertex] & host_original) for vertex in host_order]
        mark = tuple(bits(host_order.index(other) for other in graph[root] & host_original) for root in right)
        templates = tuple(map(kind, templates_order))
        before = [bits(ordering.index(other) for other in graph[vertex]) for vertex in ordering]
        yield host, mark, degree, cap, templates, before


def positive():
    for host, mark, degree, cap, templates, before in positive_cases():
        lower, new_left, new_right, common, region, outside, left_masks = setup(host, mark, degree, templates)
        planted = tuple(before[root] & outside for root in common)
        assert all(wing in set(wing_options(lower, root, outside, left_masks, degree, cap))
                   for wing, root in zip(planted, common, strict=True))
        assert (planted[0] & planted[1]).bit_count() + (lower[common[0]] & lower[common[1]]).bit_count() <= cap
        attach_masks(lower, common, planted)
        upper = build_upper(lower, region, outside, cap)
        assert all((lower_row & ~true_row) == (true_row & ~upper_row) == 0
                   for lower_row, true_row, upper_row in zip(lower, before, upper, strict=True))
        assert reject(lower, upper, new_left + common, new_right, degree, cap) == ('live', ())
    print('C24(1,4,6,11): d=8, alpha=8, cap=6; rooted five common sites; two labelings retained')


def target(input_path, prefix, maximum):
    before = process_time()
    hosts = [[bits(row) for row in decode(line)] for line in SOURCE22.read_text().splitlines()]
    templates = (1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6)
    totals, supports, cards, host_ids = Counter(), Counter(), set(), set()
    all_marks = 0
    with Path(str(prefix) + '.reroot').open('w') as log:
        for raw in input_path.read_text().splitlines()[:maximum]:
            row, core, *mark = map(int, raw.split())
            lower, left, right, common, region, outside, left_masks = setup(hosts[row], mark, 9, templates)
            assert len(lower) == 40 and core == ((1 << 22) - 1) ^ (mark[0] | mark[1] | mark[2])
            seed_counts = Counter()
            orig_cap = max((first & second).bit_count() for first, second in combinations(lower, 2))
            stop = 5 - (lower[common[0]] & lower[common[1]]).bit_count()
            if orig_cap <= 5:
                pools = [tuple(wing_options(lower, vertex, outside, left_masks, 9, 5)) for vertex in common]
                for first, second in product(*pools):
                    if (first & second).bit_count() > stop or not canonical(first, second, 28, templates):
                        continue
                    reason, witness = test_wings(lower, left + common, right, common, region, outside, 9, 5, first, second)
                    seed_counts[reason] += 1
                    print(raw, first, second, reason, *witness, sep='\t', file=log)
            all_marks += 1
            totals.update(seed_counts)
            if orig_cap > 5:
                supports['base-cap'] += 1
                print(raw, '-', '-', 'base-cap', sep='\t', file=log)
            elif seed_counts['live']:
                supports['live'] += 1
                cards.add((row, core))
                host_ids.add(row)
            elif not seed_counts:
                supports['no-wing'] += 1
                print(raw, '-', '-', 'no-wing', sep='\t', file=log)
            else:
                supports['ruled-out'] += 1
    print('tested', all_marks, 'rooted marks; surviving cards', len(cards), 'hosts', len(host_ids))
    print('support', dict(sorted(supports.items())))
    print('wing orbits', dict(sorted(totals.items())))
    print('CPU', round(process_time() - before, 5))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=Path)
    parser.add_argument('--prefix', type=Path)
    parser.add_argument('--maximum', type=int, default=1307)
    args = parser.parse_args()
    positive()
    if args.input:
        target(args.input, args.prefix, args.maximum)
