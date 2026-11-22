#!/usr/bin/env python3
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path

import pynauty

from one_neutral_control import decode, encode, require


FORMAT = 'r310.deletion-cards/1'


def load_catalogue(path, order, expected):
    records = Path(path).read_text().splitlines()
    require(len(records) == len(set(records)) == expected, f'catalogue count: {path}')
    graphs = [decode(record) for record in records]
    for record, graph in zip(records, graphs):
        require(len(graph) == order and encode(graph, range(order)) == record, 'graph6 binding')
        require(all(not graph[site] & graph[other]
                    for site in range(order) for other in graph[site]), 'triangle in catalogue')
    return graphs


def pin_deleted(graph, root):
    singleton_labels = tuple(sorted(graph[root]))
    core_labels = tuple(site for site in range(len(graph)) if site != root and site not in graph[root])
    require(len(singleton_labels) + len(core_labels) + 1 == len(graph), 'root deletion partition')
    return singleton_labels, core_labels


def induced(graph, labels):
    return [{pos for pos, other in enumerate(labels) if other in graph[site]} for site in labels]


def nauty_graph(graph):
    return pynauty.Graph(len(graph), adjacency_dict={site: sorted(row) for site, row in enumerate(graph)})


def canonical(core):
    order = tuple(pynauty.canon_label(nauty_graph(core))) if core else ()
    return encode(core, order), order


def automorphisms(core):
    identity = tuple(range(len(core)))
    if not core:
        return [identity]
    generators, size, exponent, _, _ = pynauty.autgrp(nauty_graph(core))
    discovered, frontier = {identity}, [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            move = tuple(generator[site] for site in current)
            if move not in discovered:
                discovered.add(move)
                frontier.append(move)
    require(exponent == 0 and len(discovered) == size, 'nauty group size')
    return sorted(discovered)


def contact_mask(graph, site, canonical_core):
    return sum(1 << position for position, label in enumerate(canonical_core) if label in graph[site])


def build(catalogues, qualifies, expected):
    groups = defaultdict(list)
    for order, catalogue in sorted(catalogues.items()):
        for host, graph in enumerate(catalogue):
            for root, row in enumerate(graph):
                if not qualifies(order, host, len(row)):
                    continue
                singletons, core_labels = pin_deleted(graph, root)
                key, canon_order = canonical(induced(graph, core_labels))
                core = tuple(core_labels[site] for site in canon_order)
                contacts = tuple(contact_mask(graph, site, core) for site in singletons)
                require(encode(graph, core) == key, 'canonical graph relation')
                groups[key].append([order, host, root, list(core), list(singletons), list(contacts)])
    count = Counter(card[0] for group in groups.values() for card in group)
    require(expected is None or count == expected, f'root counts {count}')
    return {'format': FORMAT, 'pynauty': pynauty.__version__,
            'groups': {key: {'aut': automorphisms(decode(key)), 'cards': cards}
                       for key, cards in sorted(groups.items())}}


def restorations(index, core, singleton_count, known=(), neutral=None):
    """Yield (order, host, root, image, neutral_image) for every size-3/4 binding.

    Physical positions are core input positions, then singleton positions in
    caller order. `known` is an iterable of (position, position, edge_bool),
    recording both edges and nonedges; `neutral` is a physical position in the
    union, or None if absent. Absence of a recorded pair is unconstrained.
    """
    require(index['format'] == FORMAT, 'lookup format')
    require(singleton_count in (3, 4), 'small singleton counts are not indexed')
    order_core = len(core)
    span = order_core + singleton_count
    require(neutral is None or 0 <= neutral < span, 'neutral position')
    known = tuple(known)
    require(all(0 <= first < span and 0 <= second < span and first != second and edge in (0, 1)
                for first, second, edge in known), 'bad known pair')
    key, query_canon = canonical(core)
    query_position = {site: pos for pos, site in enumerate(query_canon)}
    group = index['groups'].get(key)
    if group is None:
        return
    for order, host, root, card_core, singletons, contacts in group['cards']:
        if len(singletons) != singleton_count:
            continue
        for auto in group['aut']:
            core_image = tuple(auto[query_position[site]] for site in range(order_core))
            for assignment in permutations(range(singleton_count)):
                def adjacent(first, second):
                    if first > second:
                        first, second = second, first
                    if second < order_core:
                        return second in core[first]
                    if first >= order_core:
                        return False
                    return bool(contacts[assignment[second-order_core]] >> core_image[first] & 1)

                if all(adjacent(first, second) == edge for first, second, edge in known):
                    image = tuple(card_core[pos] for pos in core_image) + tuple(singletons[pos] for pos in assignment)
                    yield order, host, root, image, None if neutral is None else image[neutral]


def literal_isomorphisms(source, target, exhaustive=False):
    if len(source) != len(target):
        return set()
    order = len(source)
    if exhaustive:
        return {image for image in permutations(range(order))
                if all((second in source[first]) == (image[second] in target[image[first]])
                       for first, second in combinations(range(order), 2))}
    def signature(graph, site):
        return (len(graph[site]), tuple(sorted(len(graph[other]) for other in graph[site])))

    choices = [tuple(other for other in range(order) if signature(source, site) == signature(target, other))
               for site in range(order)]
    assigned = [-1] * order
    result = set()

    def visit(sequence, used):
        if not sequence:
            result.add(tuple(assigned))
            return
        site, *suffix = sequence
        for other in choices[site]:
            if other not in used and all((prior in source[site]) == (image in target[other])
                                         for prior, image in enumerate(assigned) if image != -1):
                assigned[site] = other
                visit(suffix, used | {other})
                assigned[site] = -1

    visit(sorted(range(order), key=lambda site: (len(choices[site]), -len(source[site]), site)), set())
    return result


def valid_binding(source_graph, source_root, query_labels, card_graph, card_root, image):
    if len(query_labels) != len(image) or set(image) != set(range(len(card_graph))) - {card_root}:
        return False
    source = (source_root, *query_labels)
    target = (card_root, *image)
    return all((source[second] in source_graph[source[first]]) == (target[second] in card_graph[target[first]])
               for first, second in combinations(range(len(source)), 2))


def audit(catalogues, qualifies, index, small=False):
    seen, representatives, reconstructed = set(), defaultdict(list), 0
    neutral_counts = Counter()
    map_counts = Counter()
    for key, group in index['groups'].items():
        canonical_graph = decode(key)
        checked = literal_isomorphisms(canonical_graph, canonical_graph,
                                       exhaustive=small and len(canonical_graph) <= 5)
        require(checked == {tuple(move) for move in group['aut']}, 'incomplete residual action')
        invariant = (len(canonical_graph), tuple(sorted(map(len, canonical_graph))))
        for previous in representatives[invariant]:
            require(not literal_isomorphisms(previous, canonical_graph), 'split canonical class')
        representatives[invariant].append(canonical_graph)
        for card in group['cards']:
            order, host, root, canon_to_host, singleton_labels, contact_masks = card
            require((order, host, root) not in seen, 'duplicate root')
            seen.add((order, host, root))
            graph = catalogues[order][host]
            singletons = tuple(site for site in reversed(range(order)) if root in graph[site])
            core_labels = tuple(site for site in reversed(range(order)) if site != root and root not in graph[site])
            query = induced(graph, core_labels)
            require(sorted(singletons) == singleton_labels and sorted(core_labels) == sorted(canon_to_host),
                    'catalogue root/singleton/core misbinding')
            relabel_key, query_to_canon = canonical(query)
            require(relabel_key == key, 'lost reversed-label plant')
            ref = induced(graph, sorted(core_labels))
            literal = literal_isomorphisms(query, ref, exhaustive=small and len(query) <= 5)
            literal = {tuple(sorted(core_labels)[site] for site in move) for move in literal}
            query_position = tuple(query_to_canon.index(site) for site in range(len(query)))
            expanded = {tuple(canon_to_host[auto[pos]] for pos in query_position) for auto in group['aut']}
            require(literal == expanded and core_labels in expanded, 'residual binding mismatch')
            map_counts[order] += len(expanded)
            require(len(singleton_labels) == len(contact_masks) and
                    all(0 <= mask < (1 << len(canon_to_host)) for mask in contact_masks), 'bad contact mask width')
            for single, contacts in zip(singleton_labels, contact_masks):
                require({canon_to_host[bit] for bit in range(len(canon_to_host)) if contacts >> bit & 1}
                        == graph[single] & set(core_labels), 'literal singleton contacts differ')
                require(root in graph[single] and not graph[single] & set(singleton_labels),
                        'literal singleton row shape differs')

            labels = core_labels + singletons
            known = [(first, second, labels[second] in graph[labels[first]])
                     for first, second in combinations(range(len(labels)), 2)]
            expected = {move + assignment for move in literal for assignment in permutations(singleton_labels)
                        if valid_binding(graph, root, labels, graph, root, move + assignment)}
            require(labels in expected, 'full reconstruction lost original labelled plant')

            if len(singletons) in (3, 4):
                single_card = {'format': FORMAT, 'groups': {key: {'aut': group['aut'], 'cards': [card]}}}
                for neutral in (0, len(labels)-1):
                    actual = set(restorations(single_card, query, len(singletons), known, neutral))
                    expected_with_pin = {(order, host, root, image, image[neutral]) for image in expected}
                    require(actual == expected_with_pin, 'API lost labelled reconstruction/neutral')
                    neutral_counts['core' if neutral == 0 and query else 'singleton'] += 1
            if core_labels and singletons:
                damaged = list(labels)
                damaged[0], damaged[-1] = damaged[-1], damaged[0]
                require(not valid_binding(graph, root, labels, graph, root, damaged), 'corrupt row binding accepted')
                reconstructed += 1
    literal_roots = {(order, host, root) for order, catalogue in catalogues.items()
                     for host, graph in enumerate(catalogue) for root in range(order)
                     if qualifies(order, host, sum(root in graph[site] for site in range(order)))}
    require(literal_roots == seen, 'missing catalogue root')
    print('classes', len(index['groups']), 'roots', sorted(Counter(order for order, _, _ in seen).items()),
          'residual maps', sorted(map_counts.items()), 'mutants rejected', reconstructed,
          'neutral checks', sorted(neutral_counts.items()))


def test_small_catalogues(catalogues):
    def qualifies(order, host, degree):
        return True

    index = build(catalogues, qualifies, None)
    audit(catalogues, qualifies, index, small=True)
    checked = Counter()
    for order, catalogue in sorted(catalogues.items()):
        for host, graph in enumerate(catalogue):
            for pole in range(order):
                singletons, core = pin_deleted(graph, pole)
                count = len(singletons)
                if count not in (3, 4):
                    continue
                labels = tuple(reversed(core)) + tuple(reversed(singletons))
                query = induced(graph, labels[:len(core)])
                known = tuple((first, second, labels[second] in graph[labels[first]])
                              for first, second in combinations(range(len(labels)), 2))
                partial = tuple((first, second, edge) for first, second, edge in known
                                if second < len(core) or first >= len(core) or second == len(labels)-1)
                neutral = len(labels)-1
                expected, expected_partial = set(), set()
                for other_host, other in enumerate(catalogue):
                    for other_pole in range(order):
                        sites, tail = pin_deleted(other, other_pole)
                        if len(sites) != count:
                            continue
                        for move in literal_isomorphisms(query, induced(other, tail), exhaustive=True):
                            for assignment in permutations(sites):
                                image = tuple(tail[pos] for pos in move) + assignment
                                receipt = order, other_host, other_pole, image, image[neutral]
                                if valid_binding(graph, pole, labels, other, other_pole, image):
                                    expected.add(receipt)
                                if all((image[second] in other[image[first]]) == edge for first, second, edge in partial):
                                    expected_partial.add(receipt)
                observed = set(restorations(index, query, count, known, neutral))
                require(expected == observed and (order, host, pole, labels, labels[neutral]) in observed,
                        'literal small complete rooted lifts differ')
                require(set(restorations(index, query, count, partial, neutral)) == expected_partial,
                        'literal small partial rooted lifts differ')
                flipped = tuple((first, second, edge or (first, second) == (len(core), len(core)+1))
                                for first, second, edge in known)
                require(not list(restorations(index, query, count, flipped, neutral)), 'fake singleton edge survived')
                checked[count] += 1
    require(checked.total() > 0, 'no small rooted lift controls')
    print('literal small complete rooted lift sets', sorted(checked.items()), 'negative controls', checked.total())
    return checked


def small_control(root):
    counts = {4: 6, 5: 9, 6: 15, 7: 9, 8: 3}
    catalogues = {order: load_catalogue(root / f'r3_4_{order}.g6', order, count) for order, count in counts.items()}
    degree_three = test_small_catalogues(catalogues)
    degree_four = test_small_catalogues({6: load_catalogue(root / 'r3_5_6.g6', 6, 32)})
    require(degree_three[3] and degree_four[4], 'small controls must exercise both singleton counts')


def main():
    mode, catalogue, *args = sys.argv[1:]
    catalogue = Path(catalogue)
    if mode == 'small':
        require(not args, 'unexpected small-control arguments')
        small_control(catalogue)
        return
    require(mode in ('sample', 'target') and len(args) == (mode == 'target'), 'bad command')
    catalogues = {order: load_catalogue(catalogue / f'r3_6_{order}.g6', order, count)
                  for order, count in ((16, 2576), (17, 7))}

    def qualifies(order, host, degree):
        return degree == order - 13 and (mode == 'target' or order == 17 or host % 143 == 0)

    index = build(catalogues, qualifies, {16: 1458, 17: 21} if mode == 'target' else None)
    audit(catalogues, qualifies, index)
    if mode == 'target':
        with Path(args[0]).open('x') as output:
            json.dump(index, output, sort_keys=True, separators=(',', ':'))
            output.write('\n')


if __name__ == '__main__':
    main()
