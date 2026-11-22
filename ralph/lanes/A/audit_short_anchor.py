#!/usr/bin/env python3
"""Independent literal controls for the short-anchor (order-21) projection."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, islice, product
import json
from pathlib import Path

import pynauty

from audit_path_leaf import vertices
from audit_strip_extensions import ROOT, independent
from residue_bundle import parse_graph6, to_graph6, triangle_free


def bitset(group):
    return sum(1 << vertex for vertex in group)


def support_counts(adj, anchors, outside):
    return Counter(adj[vertex] & anchors for vertex in vertices(outside))


def capacity(anchors, singles=4):
    return Counter({1 << vertex: singles for vertex in vertices(anchors)}) + Counter(
        bitset(pair) for pair in combinations(vertices(anchors), 2))


def marked(adj, short, long, singles=4):
    outside = ((1 << len(adj)) - 1) ^ short ^ long
    if short & long or any(adj[vertex] & side for side in (short, long) for vertex in vertices(side)):
        return None
    cross = [(left, right) for left, right in product(vertices(short), vertices(long)) if adj[left] >> right & 1]
    if len(cross) != 1:
        return None
    if any(support_counts(adj, side, outside) - capacity(side, singles) for side in (short, long)):
        return None
    return cross[0]


def project(adj, keep):
    return tuple(bitset(index for index, peer in enumerate(keep) if adj[vertex] >> peer & 1)
                 for vertex in keep)


def relabel(ordered, mask):
    return bitset(index for index, old in enumerate(ordered) if mask >> old & 1)


def coloured_certificate(adj, short, long):
    partition = (set(vertices(short)), set(vertices(long)), set(vertices(((1 << len(adj)) - 1) ^ short ^ long)))
    return pynauty.certificate(pynauty.Graph(len(adj), vertex_coloring=partition,
                                             adjacency_dict={i: list(vertices(row)) for i, row in enumerate(adj)}))


@lru_cache(maxsize=16384)
def decode(encoded):
    adj = tuple(parse_graph6(encoded))
    assert triangle_free(adj)
    assert next(independent(adj, 7), None) is None
    return adj


def parent_catalogue(path):
    parent_rows = {}
    histogram = Counter()
    for line in path.read_text().splitlines():
        parent_id, short, long, encoded = line.split()
        short, long = int(short), int(long)
        adj = decode(encoded)
        assert len(adj) == 21 and (short.bit_count(), long.bit_count()) == (3, 4)
        cross = marked(adj, short, long)
        assert cross is not None
        outside = ((1 << 21) - 1) ^ short ^ long
        missing, = (capacity(short) - support_counts(adj, short, outside)).elements()
        assert missing >> cross[0] & 1
        assert adj[cross[0]].bit_count() == 6
        for vertex in vertices(short & ~(1 << cross[0])):
            assert adj[vertex].bit_count() in (5, 6)
        key = (encoded, short, long)
        assert key not in parent_rows
        parent_rows[key] = (int(parent_id), missing, cross)
        histogram[missing.bit_count()] += 1
    assert len(parent_rows) == 6160
    print('supplied marked parents', len(parent_rows), 'deficit frequencies by width', sorted(histogram.items()))
    return parent_rows


def graft_controls(path, parent_rows, limit):
    histogram, controls, tested = Counter(), {}, 0
    with path.open() as stream:
        for line in islice(stream, limit):
            graft_id, first, second, encoded = line.split()
            adj = tuple(parse_graph6(encoded))
            assert len(adj) == 24
            low = min(mask.bit_count() for mask in adj)
            first, second = int(first), int(second)
            cross = marked(adj, first, second)
            assert cross is not None
            for first_side, second_side, star in ((first, second, cross[0]), (second, first, cross[1])):
                for anchor in vertices(first_side & ~(1 << star)):
                    if adj[anchor].bit_count() != 2:
                        continue
                    assert not adj[anchor] & (first_side | second_side)
                    survivors = tuple(vertices(((1 << 24) - 1) ^ adj[anchor] ^ (1 << anchor)))
                    parent_bits = project(adj, survivors)
                    core = to_graph6(parent_bits)
                    short, long = relabel(survivors, first_side), relabel(survivors, second_side)
                    assert marked(parent_bits, short, long) is not None
                    parent = parent_rows.get((core, short, long))
                    if parent is None:
                        continue
                    histogram[parent[1].bit_count(), low] += 1
                    tested += 1
                    layout = (*survivors, anchor, *vertices(adj[anchor]))
                    key = (parent[1].bit_count(), low)
                    if key not in controls:
                        assert triangle_free(adj) and next(independent(adj, 8), None) is None
                        controls[key] = dict(graft=int(graft_id), parent=parent[0], core=core,
                                             short=short, long=long, missing=parent[1], cross=parent[2],
                                             delta=low, target=to_graph6(project(adj, layout)), original=encoded,
                                             layout=layout)
    assert tested and any(width == 1 for width, _ in controls), controls
    print(f'{tested} literal rooted addbacks with labelled order-21 parent in first {limit} graft records',
          sorted(histogram.items()))
    return controls


def nonglobal_control(path, parent_rows):
    parents = {}
    for (encoded, short, long), (parent_id, _, _) in parent_rows.items():
        parents.setdefault(coloured_certificate(decode(encoded), short, long), parent_id)
    with path.open() as stream:
        for line in stream:
            graft_id, first, second, encoded = line.split()
            adj = tuple(parse_graph6(encoded))
            if len(adj) - 22 <= min(map(int.bit_count, adj)):
                continue
            first, second = int(first), int(second)
            cross = marked(adj, first, second)
            assert cross is not None
            for short_side, long_side, star in ((first, second, cross[0]), (second, first, cross[1])):
                for anchor in vertices(short_side & ~(1 << star)):
                    if adj[anchor].bit_count() != len(adj)-22:
                        continue
                    assert not adj[anchor] & (short_side | long_side)
                    survivors = tuple(vertices(((1 << len(adj)) - 1) ^ adj[anchor] ^ (1 << anchor)))
                    core = project(adj, survivors)
                    short, long = relabel(survivors, short_side), relabel(survivors, long_side)
                    core_cross = marked(core, short, long)
                    assert core_cross is not None and core_cross[0] == survivors.index(star)
                    outside = ((1 << 21) - 1) ^ short ^ long
                    missing, = (capacity(short) - support_counts(core, short, outside)).elements()
                    parent_id = parents[coloured_certificate(core, short, long)]
                    layout = (*survivors, anchor, *vertices(adj[anchor]))
                    assert triangle_free(adj) and next(independent(adj, 8), None) is None
                    print(f'nonminimum equality anchor: source {graft_id}, parent orbit {parent_id}, '
                          f'degree {adj[anchor].bit_count()}, delta {min(map(int.bit_count, adj))}')
                    return dict(graft=int(graft_id), parent=parent_id, core=to_graph6(core), short=short, long=long,
                                missing=missing, cross=core_cross, delta=min(map(int.bit_count, adj)),
                                target=to_graph6(project(adj, layout)), original=encoded, layout=layout)
    raise ValueError('no nonglobal marked equality anchor in source')


def missing_mutations(control):
    adj = tuple(parse_graph6(control['core']))
    short, long = control['short'], control['long']
    star = control['cross'][0]
    assert control['missing'] == 1 << star
    outside = ((1 << len(adj)) - 1) ^ short ^ long
    mutants = []
    for peer in vertices(short & ~(1 << star)):
        altered_support = bitset((star, peer))
        exterior, = [vertex for vertex in vertices(outside) if adj[vertex] & short == altered_support]
        mutated = list(adj)
        mutated[exterior] ^= 1 << peer
        mutated[peer] ^= 1 << exterior
        assert triangle_free(mutated) and marked(mutated, short, long) == tuple(control['cross'])
        missing, = (capacity(short) - support_counts(mutated, short, outside)).elements()
        assert missing == altered_support
        witness = next(independent(mutated, 7), None)
        target = list(parse_graph6(control['target']))
        target[exterior] ^= 1 << peer
        target[peer] ^= 1 << exterior
        assert triangle_free(target) and marked(target, short | (1 << 21), long) == tuple(control['cross'])
        mutants.append(dict(control, core=to_graph6(mutated), target=to_graph6(target), missing=missing,
                            mutation_edge=(exterior, peer), parent_I7=witness,
                            lift_I8=next(independent(target, 8), None)))
    print('two physical double-deficit mutations', [(m['mutation_edge'], m['missing'], m['parent_I7'], m['lift_I8'])
                                                     for m in mutants])
    return mutants


def small_census(path):
    rows = [tuple(parse_graph6(line)) for line in path.read_text().splitlines()]
    assert len(rows) == 410
    control = Counter()
    examples = {}
    for adj in rows:
        assert len(adj) == 8 and triangle_free(adj)
        for short in combinations(range(8), 2):
            for long in combinations(set(range(8)) - set(short), 2):
                short_mask, long_mask = bitset(short), bitset(long)
                cross = marked(adj, short_mask, long_mask, 2)
                if cross is None:
                    continue
                control['marks'] += 1
                anchor, = set(short) - {cross[0]}
                if not adj[anchor]:
                    continue
                survivors = tuple(vertices(255 ^ adj[anchor] ^ (1 << anchor)))
                core = project(adj, survivors)
                short_mask, long_mask = relabel(survivors, short_mask), relabel(survivors, long_mask)
                assert marked(core, short_mask, long_mask, 2) is not None
                control['positive degree addbacks'] += 1
                examples.setdefault(adj[anchor].bit_count(), (to_graph6(adj), short, long, anchor))
    assert control['marks'] == 42
    print('all smaller controls', len(rows), dict(control), sorted(examples.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=6000)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    producer = ROOT / 'scratch/G/round10'
    small_census(producer.parent / 'round7/control8.g6')
    parents = parent_catalogue(producer / 'short-anchor.full.keys')
    controls = list(graft_controls(producer / 'short-anchor.graft24.pilot.keys', parents, args.limit).values())
    nonglobal = nonglobal_control(producer.parent / 'round7/lowdegree25.canon.keys', parents)
    mutations = missing_mutations(controls[0])
    args.output.write_text(json.dumps(dict(positives=(*controls, nonglobal), mutations=mutations), indent=2) + '\n')


if __name__ == '__main__':
    main()
