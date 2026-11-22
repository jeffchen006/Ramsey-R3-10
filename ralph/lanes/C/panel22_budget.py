#!/usr/bin/env python3
"""Exact fixed-label projections for physical shared-core degree budgets."""

import argparse
from collections import Counter
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path

from panel18_bind import frame_binding, read_integer_rows
from panel19_fifth import catalogue, independent, triangle_free, word
from verify_panel17 import bits
import panel21_budget_toy as toy


def pair_add(graph, first, second):
    graph[first] |= 1 << second
    graph[second] |= 1 << first


def pair_remove(graph, first, second):
    graph[first] &= ~(1 << second)
    graph[second] &= ~(1 << first)


def edge_set_graph(order, edges):
    graph = [0] * order
    for first, second in edges:
        pair_add(graph, first, second)
    return tuple(graph)


def pin_propagation(lower, upper, degree):
    lower, upper = list(lower), list(upper)
    while True:
        changed = False
        if not triangle_free(lower):
            return None
        for first, row in enumerate(lower):
            assert not row & ~upper[first]
            unknown = upper[first] & ~row
            required = degree - row.bit_count()
            if not 0 <= required <= unknown.bit_count():
                return None
            if not required:
                for second in bits(unknown):
                    pair_remove(upper, first, second)
                    changed = True
            elif required == unknown.bit_count():
                for second in bits(unknown):
                    pair_add(lower, first, second)
                    changed = True
        for first, row in enumerate(lower):
            for second in bits(upper[first] & ~row):
                if row & lower[second]:
                    pair_remove(upper, first, second)
                    changed = True
        if not changed:
            return tuple(lower), tuple(upper)


@cache
def core_atlas(core_adjacency):
    alpha = [0] * (1 << len(core_adjacency))
    for mask in range(1, len(alpha)):
        first = mask & -mask
        rem = mask ^ first
        alpha[mask] = max(alpha[rem], 1 + alpha[rem & ~core_adjacency[first.bit_length() - 1]])
    return tuple(alpha)


@cache
def column_domain(rows, cap, fixed, optional, min_new, max_new):
    alpha = core_atlas(rows)
    full = len(alpha) - 1
    col = []
    subset = optional
    while True:
        all_contacts = fixed | subset
        if (min_new <= subset.bit_count() <= max_new
                and independent(rows, all_contacts) and alpha[full ^ all_contacts] < cap):
            col.append((all_contacts, subset))
        if not subset:
            break
        subset = (subset - 1) & optional
    return tuple(sorted(col, key=lambda row: (row[1].bit_count(), row[1])))


def card_domain(lower, upper, degree, core, root, sites, cap, exact_total=None, focus=None):
    """Yield all admissible added-contact column words, in physical site order."""
    core_set, site_set = word(core), word(sites)
    assert not core_set & site_set and not (core_set | site_set) >> root & 1
    assert not upper[root] & core_set and (lower[root] & site_set) == site_set
    assert all(not upper[site] & site_set for site in sites)
    assert all(not (upper[site] ^ lower[site]) & core_set for site in core)
    rows = tuple(word(index for index, peer in enumerate(core) if lower[site] >> peer & 1)
                 for site in core)
    alpha = core_atlas(rows)
    full = len(alpha) - 1
    if 1 + alpha[full] > cap:
        return
    capacity = [len(sites) if degree is None else degree - lower[site].bit_count() for site in core]
    if focus is not None:
        pos, bound = focus
        capacity[pos] = min(capacity[pos], bound)
    if any(amount < 0 for amount in capacity):
        return
    candidates = []
    for site in sites:
        fixed = word(index for index, peer in enumerate(core) if lower[site] >> peer & 1)
        optional = word(index for index, peer in enumerate(core)
                        if capacity[index] and (upper[site] ^ lower[site]) >> peer & 1)
        residual = len(core) if degree is None else degree - lower[site].bit_count()
        outside = ((upper[site] ^ lower[site]) & ~core_set).bit_count()
        min_new = 0 if degree is None else max(0, residual - outside)
        candidates.append(column_domain(rows, cap, fixed, optional, min_new, residual))
    order = sorted(range(len(sites)), key=lambda pos: (len(candidates[pos]), pos))
    unions = [0] * (1 << len(sites))
    chosen = [0] * len(sites)

    def extend(index, total):
        if index == len(sites):
            if exact_total is None or total == exact_total:
                yield tuple(chosen)
            return
        prefix = 1 << index
        pos = order[index]
        for contacts, added in candidates[pos]:
            new_total = total + contacts.bit_count()
            if exact_total is not None and new_total > exact_total:
                continue
            if any(capacity[pos] == 0 for pos in bits(added)):
                continue
            for other in range(prefix):
                merged = contacts | unions[other]
                if alpha[full ^ merged] > cap - 1 - other.bit_count():
                    break
                unions[prefix | other] = merged
            else:
                chosen[pos] = added
                for contact in bits(added):
                    capacity[contact] -= 1
                yield from extend(index + 1, new_total)
                for contact in bits(added):
                    capacity[contact] += 1

    yield from extend(0, 0)


def masks_to_edges(core, sites, columns):
    return frozenset(toy.edge(core[pos], site) for site, mask in zip(sites, columns, strict=True)
                     for pos in bits(mask))


def minima(domain, order):
    count = 0
    profile = [None] * order
    for columns in domain:
        count += 1
        possible = word(pos for pos, value in enumerate(profile) if value != 0)
        for pos in bits(possible):
            hits = sum(column >> pos & 1 for column in columns)
            if profile[pos] is None or hits < profile[pos]:
                profile[pos] = hits
    return count, tuple(profile)


def least_profile(lower, upper, degree, core, root, sites, cap, exact_total=None):
    args = lower, upper, degree, core, root, sites, cap, exact_total
    initial = next(card_domain(*args), None)
    if initial is None:
        return (), ()
    witness = [initial] * len(core)

    def hits(columns, pos):
        return sum(column >> pos & 1 for column in columns)

    for pos in range(len(core)):
        for bound in range(hits(witness[pos], pos)):
            found = next(card_domain(*args, focus=(pos, bound)), None)
            if found is not None:
                for other in range(len(core)):
                    if hits(found, other) < hits(witness[other], other):
                        witness[other] = found
                break
    return tuple(hits(found, pos) for pos, found in enumerate(witness)), tuple(witness)


def small_catalogue_control(repo):
    core, root = (0, 1, 2, 3), 4
    comparisons = assignments = 0
    for core_edges in ((), ((0, 1),), ((0, 1), (2, 3)), ((0, 1), (1, 2), (2, 3))):
        for size in range(4):
            order = len(core) + 1 + size
            sites = tuple(range(root + 1, order))
            lower = edge_set_graph(order, (*core_edges, *((root, site) for site in sites)))
            upper = list(lower)
            for first, second in product(core, sites):
                pair_add(upper, first, second)
            domain = set(card_domain(lower, upper, None, core, root, sites, 3))
            oracle = set()
            for graph in catalogue(repo / f'gluing/val/r3_4_{order}.g6'):
                for actual_root, row in enumerate(graph):
                    if row.bit_count() != size:
                        continue
                    neighbours = tuple(bits(row))
                    residual = tuple(site for site in range(order) if site not in (*neighbours, actual_root))
                    for binding in permutations(residual):
                        edges = tuple((left, right) for left, right in combinations(core, 2)
                                      if graph[binding[left]] >> binding[right] & 1)
                        if edges != core_edges:
                            continue
                        for singletons in permutations(neighbours):
                            oracle.add(tuple(word(pos for pos, actual in enumerate(binding)
                                                  if graph[singleton] >> actual & 1)
                                             for singleton in singletons))
            assert domain == oracle, (core_edges, size, domain ^ oracle)
            profile, witnesses = least_profile(lower, upper, None, core, root, sites, 3)
            assert profile == (minima(domain, len(core))[1] if domain else ())
            assert all(found in oracle for found in witnesses)
            comparisons += 1
            assignments += len(domain)
    assert comparisons == 16 and assignments
    print('small catalogue literal labelled sets', comparisons, 'assignments', assignments)


def control(repo):
    planted = {toy.edge(site, (site + offset) % 13) for site in toy.VERTICES for offset in (1, 5)}
    toy.graph_control(planted, toy.POSITIVE_FORBIDDEN, 4)
    lower = edge_set_graph(13, toy.PRESCRIBED)
    core = toy.CORE
    checked = 0
    for label, forbidden in (('strict', toy.NEGATIVE_FORBIDDEN), ('C13', toy.POSITIVE_FORBIDDEN)):
        upper = list(lower)
        for first, second in (*product(core, (*toy.GROUPS[0], *toy.GROUPS[1])), *product(*toy.GROUPS)):
            if toy.edge(first, second) not in forbidden:
                pair_add(upper, first, second)
        profiles = []
        counts = []
        for root, group in zip(toy.POLES, toy.GROUPS, strict=True):
            domain = tuple(card_domain(lower, upper, 4, core, root, group, 3, exact_total=5))
            actual = {masks_to_edges(core, group, columns) | frozenset(
                toy.edge(site, peer) for site in core for peer in group if lower[site] >> peer & 1)
                      for columns in domain}
            _, _, oracle = toy.card_profiles(root, group, forbidden)
            assert len(actual) == len(domain) and oracle == actual
            checked += 4096
            if label == 'C13':
                assert frozenset(toy.edge(site, peer) for site in core for peer in group
                                 if toy.edge(site, peer) in planted) in actual
            count, profile = minima(domain, len(core))
            least, witnesses = least_profile(lower, upper, 4, core, root, group, 3, exact_total=5)
            assert least == profile and all(found in domain for found in witnesses)
            counts.append(count)
            profiles.append(profile)
        overloads = tuple(site for pos, site in enumerate(core)
                          if sum(prof[pos] for prof in profiles) > 4 - lower[site].bit_count())
        assert overloads == ((6,) if label == 'strict' else ())
        print(label, 'domains', counts, 'minima', profiles, 'overloads', overloads)
    assert checked == 16384
    small_catalogue_control(repo)


def bind(case, catalogues, root):
    frames = case[2:8], case[8:]
    windows = tuple(graphs[frame[0]] for frame, graphs in zip(frames, catalogues, strict=True))
    neutral = tuple(frame[1] for frame in frames)
    marks = tuple(frame[2:] for frame in frames)
    for window, zed, mark in zip(windows, neutral, marks, strict=True):
        frame_binding(window, zed, mark, 9, 5, 4, 9)
    left, right = windows
    left_labels = tuple(range(8, 24))
    right_labels = tuple(left_labels[neutral[0]] if idx == neutral[1] else 24 + idx - (idx > neutral[1])
                         for idx in range(17))
    labels = left_labels, right_labels
    lower = [0] * 40
    for first, second in product(range(4), range(4, 8)):
        pair_add(lower, first, second)
    for side, (window, positions, mark_rows) in enumerate(zip(windows, labels, marks, strict=True)):
        for first, row in enumerate(window):
            for second in bits(row):
                pair_add(lower, positions[first], positions[second])
        for index, mark in enumerate(mark_rows):
            for site in bits(mark):
                pair_add(lower, side * 4 + index, positions[site])
    x = left_labels[root]
    own = tuple(left_labels[site] for site in bits(left[root]))
    core = tuple(site for site in left_labels if site not in (x, *own))
    assert len(core) == 12 and len(own) == 3 and left_labels[neutral[0]] in own
    contacts = tuple(idx for idx, mark in enumerate(marks[0]) if mark >> root & 1)
    assert len(contacts) == 3
    partition = [set(left_labels[site] for site in bits(marks[0][idx]) if site != root) for idx in contacts]
    assert all(len(part) == 4 and part <= set(core) for part in partition)
    assert set().union(*partition) == set(core)
    upper = list(lower)
    for first, second in product(left_labels, right_labels):
        if first != left_labels[neutral[0]] and second != right_labels[neutral[1]]:
            pair_add(upper, first, second)
    right_singletons = tuple(tuple(site for site in range(17)
                                   if mark >> site & 1 and sum(item >> site & 1 for item in marks[1]) == 1)
                             for mark in marks[1])
    assert sorted(map(len, right_singletons)) == [3, 3, 3, 4]
    return tuple(lower), tuple(upper), core, x, own, right, neutral[1], marks[1], right_labels, right_singletons


def target(repo, cases, detail, exhaustive):
    catalogues = tuple(catalogue(repo / f'gluing/val/r3_6_{order}.g6') for order in (16, 17))
    total = Counter()
    with detail.open('w') as stream:
        print('left right T state nonempty capacity minima overload', file=stream)
        for case in read_integer_rows(cases, 14):
            lower, upper, core, x, own, right, neutral, marks, labels, original = bind(case, catalogues, 1)
            results = Counter()
            print('core', *case[:2], *core, 'x', x, 'own', *own)
            for triple in combinations((idx for idx in range(17) if idx != neutral), 3):
                choice = word(triple)
                if not independent(right, choice | 1 << neutral) or any((choice & mark).bit_count() > 2 for mark in marks):
                    continue
                new_lower, new_upper = list(lower), list(upper)
                for idx, site in enumerate(labels):
                    if idx in triple:
                        pair_add(new_lower, x, site)
                    elif idx != neutral:
                        pair_remove(new_upper, x, site)
                solved = pin_propagation(new_lower, new_upper, 9)
                fields = '-', '-', '-', '-'
                if solved is None:
                    status = 'pins'
                else:
                    pres, allow = solved
                    groups = (own, *(tuple(labels[idx] for idx in group if idx not in triple) for group in original))
                    assert sum(map(len, groups)) == len(set().union(*map(set, groups)))
                    poles = (x, 4, 5, 6, 7)
                    for pole, group in zip(poles, groups, strict=True):
                        assert all(not allow[peer] & word((*core, pole, *group)) for peer in poles if peer != pole)
                    if exhaustive:
                        rows = tuple(minima(card_domain(pres, allow, 9, core, pole, group, 5), len(core))
                                     for pole, group in zip(poles, groups, strict=True))
                        profiles = tuple(profile if count else () for count, profile in rows)
                    else:
                        profiles = tuple(least_profile(pres, allow, 9, core, pole, group, 5)[0]
                                         for pole, group in zip(poles, groups, strict=True))
                    nonempty = tuple(int(bool(profile)) for profile in profiles)
                    capacity = tuple(9 - pres[site].bit_count() for site in core)
                    if min(nonempty) == 0:
                        status, overload = 'card', ()
                    else:
                        overload = tuple((site, sum(profile[idx] for profile in profiles), capacity[idx])
                                         for idx, site in enumerate(core)
                                         if sum(profile[idx] for profile in profiles) > capacity[idx])
                        status = 'budget' if overload else 'live'
                    fields = tuple(repr(item).replace(' ', '') for item in (nonempty, capacity, profiles, overload))
                results[status] += 1
                print(*case[:2], choice, status, *fields, file=stream, flush=True)
            assert sum(results.values()) > 0
            total.update(results)
            print('rows', *case[:2], sum(results.values()), *sorted(results.items()))
    print('total', sum(total.values()), *sorted(total.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', type=Path)
    parser.add_argument('--cases', type=Path)
    parser.add_argument('--detail', type=Path)
    parser.add_argument('--exhaustive', action='store_true')
    args = parser.parse_args()
    if args.cases:
        assert args.detail
        target(args.repo, args.cases, args.detail, args.exhaustive)
    else:
        control(args.repo)


if __name__ == '__main__':
    main()
