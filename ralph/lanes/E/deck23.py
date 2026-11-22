#!/usr/bin/env python3
"""Marked two-card joins, and exact physical marks of a concrete window."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
from time import process_time

from deficit73 import mask, mask_union
from involution_cores import bits, graph
from involution_sat import from_graph6, to_graph6, witnesses


@dataclass(frozen=True)
class Mark:
    core: int
    groups: tuple[int, ...]


def role_tables(card, core, width, totals):
    free = ((1 << len(card)) - 1) ^ core
    core_sets = tuple(subset for size in range(2, core.bit_count() + 1)
                      for subset in witnesses(card, core, size))
    available = {total: set() for total in totals}
    for group in witnesses(card, free, width):
        row = tuple((card[vertex] & group).bit_count() for vertex in bits(core))
        if sum(row) not in available or min(row) == 0:
            continue
        if any(mask_union(card, subset, group).bit_count() < subset.bit_count() for subset in core_sets):
            continue
        available[sum(row)].add(group)
    return available


def marks(card, core, profile, omitted, width, full_core_sum):
    count = len(card)
    roles = [index for index in range(4) if index != omitted]
    assert count == core.bit_count() + 3 * width
    if sum(card[vertex].bit_count() for vertex in bits(core)) != full_core_sum - profile[omitted]:
        return
    free = ((1 << count) - 1) ^ core
    available = role_tables(card, core, width, {profile[index] for index in roles})
    for first, second in product(*(sorted(available[profile[index]]) for index in roles[:2])):
        if first & second:
            continue
        third = free ^ (first | second)
        if third in available[profile[roles[2]]]:
            groups = [0] * 4
            for role, group in zip(roles, (first, second, third)):
                groups[role] = group
            yield Mark(core, tuple(groups))


def overlap(card, mark, other):
    import pynauty

    roles = (mark.core, *(group for slot, group in enumerate(mark.groups) if slot != other and group))
    nodes = tuple(bits(mask_union_value(roles)))
    by_node = {node: index for index, node in enumerate(nodes)}
    colors = [{by_node[node] for node in bits(group)} for group in roles]
    adj = {by_node[node]: [by_node[peer] for peer in bits(card[node]) if peer in by_node] for node in nodes}
    return pynauty.certificate(pynauty.Graph(len(nodes), adjacency_dict=adj, vertex_coloring=colors))


def mask_union_value(sets):
    result = 0
    for subset in sets:
        assert not result & subset
        result |= subset
    return result


def alignments(first, left, second, right, left_missing, right_missing):
    import networkx as nx

    def colored(card, mark, exclude):
        result = nx.Graph()
        for index, group in enumerate((mark.core, *mark.groups)):
            if index == exclude + 1:
                continue
            result.add_nodes_from(bits(group), role=index)
        result.add_edges_from((vertex, peer) for vertex, peer in combinations(sorted(result), 2) if card[vertex] >> peer & 1)
        return result

    low, high = colored(first, left, right_missing), colored(second, right, left_missing)
    matcher = nx.algorithms.isomorphism.GraphMatcher(high, low, node_match=lambda left, right: left['role'] == right['role'])
    yield from matcher.isomorphisms_iter()


def merge(first, left, second, right, left_missing, right_missing, matching):
    count = len(first)
    assert len(second) == count
    assert set(matching) == set(range(count)) - set(bits(right.groups[left_missing]))
    assert set(matching.values()) == set(range(count)) - set(bits(left.groups[right_missing]))
    for vertex, peer in combinations(matching, 2):
        assert (second[vertex] >> peer & 1) == (first[matching[vertex]] >> matching[peer] & 1)
    matching = dict(matching) | {vertex: count + index for index, vertex in enumerate(bits(right.groups[left_missing]))}
    union = {(vertex, peer) for vertex, row in enumerate(first) for peer in bits(row) if vertex < peer}
    union |= {tuple(sorted((matching[vertex], matching[peer])))
              for vertex, row in enumerate(second) for peer in bits(row) if vertex < peer}
    groups = list(left.groups)
    groups[left_missing] = mask(matching[vertex] for vertex in bits(right.groups[left_missing]))
    for index, group in enumerate(right.groups):
        if index != right_missing:
            assert groups[index] == mask(matching[vertex] for vertex in bits(group))
    assert left.core == mask(matching[vertex] for vertex in bits(right.core))
    return graph(len(matching) + groups[right_missing].bit_count(), union), Mark(left.core, tuple(groups))


def finishes(base, marking, omitted_pair, degrees, alpha_order=None, checked=None):
    left, right = (tuple(bits(marking.groups[index])) for index in omitted_pair)
    residual = [degrees[vertex] - row.bit_count() for vertex, row in enumerate(base)]
    assert not any(base[vertex] & base[peer] for vertex, row in enumerate(base) for peer in bits(row))
    if min(residual) < 0 or any(residual[vertex] for vertex in range(len(base)) if vertex not in left + right):
        return
    available = {vertex: tuple(peer for peer in right if not base[vertex] & base[peer]) for vertex in left}
    domains = tuple(tuple((vertex, *selection) for selection in combinations(available[vertex], residual[vertex]))
                    for vertex in left)
    for rows in product(*domains):
        counts = Counter(peer for row in rows for peer in row[1:])
        if any(counts[peer] != residual[peer] for peer in right):
            continue
        full = list(base)
        for vertex, *neighbors in rows:
            full[vertex] |= mask(neighbors)
            for peer in neighbors:
                full[peer] |= 1 << vertex
        assert tuple(row.bit_count() for row in full) == tuple(degrees)
        domain = (1 << len(full)) - 1
        bad = None if alpha_order is None else next(((role, rejected)
                    for role, group in enumerate(marking.groups)
                    if (rejected := next(witnesses(full, domain ^ group, alpha_order), None)) is not None), None)
        if checked is not None:
            checked(tuple(full), bad)
        if bad is None:
            yield tuple(full)


def control(cards=None):
    core = 7
    groups = tuple(7 << shift for shift in (3, 6, 9, 12))
    shifts = (3, 6, 9, 12)
    edges = [(0, 1), (1, 2)] + [(vertex, shift + vertex) for shift in shifts for vertex in range(3)]
    edges += [(left, right + 2) for left, right in product(shifts, repeat=2) if left != right]
    full = graph(15, edges)
    profile = (3,) * 4

    def omit(position, order):
        nodes = tuple(vertex for vertex in order if not groups[position] >> vertex & 1)
        card = graph(len(nodes), ((lx, rx) for lx, rx in combinations(range(len(nodes)), 2) if full[nodes[lx]] >> nodes[rx] & 1))
        traced = Mark(mask(index for index, node in enumerate(nodes) if core >> node & 1), tuple(
                    mask(index for index, node in enumerate(nodes) if group >> node & 1) for group in groups))
        assert traced in set(marks(card, traced.core, profile, position, 3, 16))
        return card, traced, nodes

    totals = Counter()
    examples = []
    for left_missing, right_missing in combinations(range(4), 2):
        first, left, left_nodes = omit(left_missing, range(15))
        second, right, right_nodes = omit(right_missing, [7, 8, 1, 10, 5, 6, 13, 2, 0, 3, 11, 12, 4, 14, 9])
        import pynauty

        assert pynauty.isomorphic(*(pynauty.Graph(len(card), adjacency_dict={vertex: list(bits(row))
                              for vertex, row in enumerate(card)}) for card in (first, second)))
        assert overlap(first, left, right_missing) == overlap(second, right, left_missing)
        common = {index: left_nodes.index(node) for index, node in enumerate(right_nodes) if node in left_nodes}
        maps = list(alignments(first, left, second, right, left_missing, right_missing))
        assert common in maps
        base, prem = merge(first, left, second, right, left_missing, right_missing, common)
        coordinates = left_nodes + tuple(right_nodes[index] for index in bits(right.groups[left_missing]))
        expected = graph(len(full), ((a, b) for a, b in combinations(range(len(full)), 2) if full[coordinates[a]] >> coordinates[b] & 1))
        degrees = tuple(full[vertex].bit_count() for vertex in coordinates)
        missing_edges = tuple(product(*(tuple(bits(prem.groups[role])) for role in (left_missing, right_missing))))
        exact = set()
        known = [(vertex, peer) for vertex, row in enumerate(base) for peer in bits(row) if vertex < peer]
        for count in range(len(missing_edges) + 1):
            for addition in combinations(missing_edges, count):
                trial = graph(len(full), (*known, *addition))
                if tuple(row.bit_count() for row in trial) == degrees and not any(trial[v] & trial[w] for v, w in (*known, *addition)):
                    exact.add(trial)
        assert expected in exact == set(finishes(base, prem, (left_missing, right_missing), degrees))
        assert not list(finishes(base, prem, (left_missing, right_missing), (degrees[0]+1, *degrees[1:])))
        lnode, rnode = next((a, b) for a, b in combinations(sorted(common), 2) if second[a] >> b & 1)
        altered = list(second)
        altered[lnode] ^= 1 << rnode
        altered[rnode] ^= 1 << lnode
        assert overlap(first, left, right_missing) != overlap(altered, right, left_missing)
        assert not list(alignments(first, left, altered, right, left_missing, right_missing))
        examples.extend((first, second, altered))
        totals.update({'role_pairs': 1, 'concrete_completions': len(exact), 'negative_overlap': 1, 'negative_terminal': 1})
    if cards is not None:
        cards.write_text(''.join(to_graph6(card) + '\n' for card in examples), encoding='ascii')
        with cards.with_suffix('.want').open('w', encoding='ascii') as sink:
            for index, card in enumerate(examples):
                for selection in combinations(range(len(card)), 3):
                    word = mask(selection)
                    degrees = [(card[v] & word).bit_count() for v in selection]
                    if (sum(card[v].bit_count() for v in selection) == 13 and sum(degrees) == 4
                            and all(1 <= degree <= 2 and card[v].bit_count() >= degree + 3
                                    for v, degree in zip(selection, degrees))):
                        print(index, word, file=sink)
    print('smaller deck controls', dict(totals), flush=True)


def known(catalogue, maskfile, output, profile, omitted, edges, offset, stride):
    start = process_time()
    stats = Counter()
    cards = catalogue.read_text(encoding='ascii').splitlines()
    with maskfile.open(encoding='ascii') as source, output.open('w', encoding='ascii') as sink:
        for row in source:
            index, word = map(int, row.split())
            if index % stride != offset:
                continue
            key = cards[index]
            card = from_graph6(key)
            assert len(card) == 26 and sum(adj.bit_count() for adj in card) == 148
            assert word.bit_count() == 8 and sum((card[v] & word).bit_count() for v in bits(word)) == 2 * edges
            stats['masks'] += 1
            for partition in marks(card, word, profile, omitted, 6, 64):
                stats['partition'] += 1
                print(json.dumps((index, key, partition.core, partition.groups), separators=(',', ':')), file=sink)
    print(dict(stats), f'cpu={process_time()-start:.4f}', flush=True)


def known8(catalogue, maskfile, output):
    bounds = defaultdict(set)
    for profile in combinations_with_replacement(range(10, 19), 4):
        if sum(profile) != 48:
            continue
        for slot, amount in enumerate(profile):
            if amount >= 13:
                bounds[amount].add(profile[:slot] + profile[slot+1:])
    stats = Counter()
    cards = catalogue.read_text(encoding='ascii').splitlines()
    lines = maskfile.read_text(encoding='ascii').splitlines()
    by_card = defaultdict(set)
    for line in lines:
        index, word = map(int, line.split())
        assert word not in by_card[index]
        by_card[index].add(word)
    with output.open('w', encoding='ascii') as sink:
        for index, word_list in by_card.items():
            card = from_graph6(cards[index])
            assert len(card) == 26 and sum(row.bit_count() for row in card) == 148
            degree = tuple(row.bit_count() for row in card)
            for word in sorted(word_list):
                assert word.bit_count() == 8 and all((card[vertex] & word).bit_count() == 2 for vertex in bits(word))
                amount = 64 - sum(degree[vertex] for vertex in bits(word))
                assert amount in bounds
                stats['masks'] += 1
                count = 0
                wanted = bounds[amount]
                table = role_tables(card, word, 6, set().union(*map(set, wanted)))
                free = ((1 << len(card)) - 1) ^ word
                for pattern in sorted(wanted):
                    for first, second in product(*(sorted(table[total]) for total in pattern[:2])):
                        if first & second or (pattern[0] == pattern[1] and first > second):
                            continue
                        last = free ^ (first | second)
                        if last in table[pattern[2]] and not (pattern[1] == pattern[2] and second > last):
                            result = tuple(sorted((first, second, last)))
                            print(json.dumps((index, cards[index], word, result), separators=(',', ':')), file=sink)
                            count += 1
                stats['partitions'] += count
    print('e8 known high incidence', dict(stats), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='mode', required=True)
    subs.add_parser('control').add_argument('--cards', type=Path)
    command = subs.add_parser('known')
    command.add_argument('catalogue', type=Path)
    command.add_argument('maskfile', type=Path)
    command.add_argument('output', type=Path)
    command.add_argument('--profile', type=int, nargs=4, default=(10, 10, 10, 14))
    command.add_argument('--omitted', type=int, default=3)
    command.add_argument('--edges', type=int, default=10)
    command.add_argument('--offset', type=int, default=0)
    command.add_argument('--stride', type=int, default=1)
    e8 = subs.add_parser('known8')
    for name in ('catalogue', 'maskfile', 'output'):
        e8.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.mode == 'control':
        control(args.cards)
    elif args.mode == 'known':
        known(args.catalogue, args.maskfile, args.output, args.profile, args.omitted, args.edges, args.offset, args.stride)
    else:
        known8(args.catalogue, args.maskfile, args.output)


if __name__ == '__main__':
    main()
