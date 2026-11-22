"""Two coupled star decks on one labelled decorated path kernel."""

import argparse
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path

from pysat.solvers import Cadical195

from kernel_cnf import neg
from path_links import disjunction
from path_masks import build_table, split
from path_panel import target_catalogue
from path_growth import ROOT, bits, fixed_graph, read_profiles
from punct_path import core_instances, decode, neighbors, pairs, profile_key


def patterns(profiles):
    answer = set()
    for profile in profiles:
        graph = fixed_graph(profile)
        for order in ((4, 7, 5, 6), (0, 3, 2, 1)):
            answer.add(tuple((graph[left] & graph[right]).bit_count() for left, right in pairs(order)))
    return answer


def marks():
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            assert not cycle
            mask = lambda vertex: sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (mask(vertex), vertex))
            order = core + outer
            wings = [vertex for sig in (1, 16) for vertex in outer if mask(vertex) == sig]
            edges = {(src, dst) for src, dst in pairs(range(len(wings))) if wings[dst] in adj[wings[src]]}
            yield Counter(map(mask, outer)), edges, [sum(1 << index for index, other in enumerate(order) if other in adj[vertex]) for vertex in order], len(wings)


def conjunction(form, terms):
    return neg(disjunction(form, [neg(lit) for lit in terms]))


def short_hood(graph, root):
    for center in bits(graph[root]):
        kernel = (graph[root] | graph[center]) & ~((1 << root) | (1 << center))
        while kernel:
            start = kernel & -kernel
            found = fringe = start
            while fringe:
                fresh = 0
                for vertex in bits(fringe):
                    fresh |= graph[vertex]
                fringe = fresh & kernel & ~found
                found |= fringe
            if found.bit_count() > 6 or all((graph[vertex] & found).bit_count() == 2 for vertex in bits(found)):
                return False
            kernel &= ~found
    return True


def deck(form, graph, root, library, short, floor):
    hood = list(bits(graph[root]))
    outside = sorted(set(range(len(graph))) - set(hood) - {root})
    flag = {}
    trip = {}
    exact2 = {}
    key = lambda *vertices: tuple(sorted(vertices))
    for pair in pairs(hood):
        common = [conjunction(form, [form.edge(vertex, other) for other in pair]) for vertex in outside]
        flag[pair] = form.thresholds(common, 2)
        exact2[pair] = disjunction(form, [conjunction(form, [lit] + [neg(form.edge(vertex, other)) for other in hood if other not in pair]) for lit, vertex in zip(common, outside)])
    for triple in combinations(hood, 3):
        trip[triple] = disjunction(form, [conjunction(form, [form.edge(vertex, other) for other in triple]) for vertex in outside])
    if short:
        form.cardinality(list(trip.values()), max(0, len(hood) * (len(hood)-1) - 2*len(outside)), len(hood)*(len(hood)-1)//5)
        for center in hood:
            rest = [vertex for vertex in hood if vertex != center]
            for triple in combinations(rest, 3):
                form.add(*(neg(trip[key(center, *pair)]) for pair in pairs(triple)))
            for path in permutations(rest, 4):
                if path[0] < path[-1]:
                    form.add(*(neg(trip[key(center, left, right)]) for left, right in zip(path, path[1:])))
    for center, extended, mid, tip in permutations(hood, 4):
        trigger = [trip[key(center, extended, mid)], trip[key(center, mid, tip)], exact2[key(center, extended)]]
        if False in [term is not False for term in trigger]:
            continue
        if short:
            form.add(*(neg(term) for term in trigger), neg(flag[key(center, tip)][1]))
        for index, pair in enumerate(pairs((center, extended, mid, tip))):
            if len({entry[index] for entry in library}) == 1:
                value = next(iter(library))[index]
                for step, lit in enumerate(flag[key(*pair)], 2):
                    form.add(*(neg(term) for term in trigger), lit if value >= step else neg(lit))
        signature = [flag[key(*pair)] for pair in pairs((center, extended, mid, tip))]
        switches = [index for index in range(6) if len({entry[index] for entry in library}) > 1]
        allowed = {tuple(entry[index] for index in switches) for entry in library}
        for bad in product(range(floor, 4), repeat=len(switches)):
            if bad not in allowed:
                cut = [neg(term) for term in trigger]
                for index, value in zip(switches, bad):
                    if value > 1:
                        cut.append(neg(signature[index][value-2]))
                    if value < 3:
                        cut.append(signature[index][value-1])
                form.add(*cut)


def calibration():
    records = list(marks())
    lib = patterns([profile for profile, _, _, _ in records])
    seen = {}
    counts = Counter()
    for profile, edges, planted, width in records:
        if width != 4:
            continue
        graph, _, _ = split(profile, edges)
        qmax = max(sum((planted[center] & planted[other]).bit_count()-1 for other in bits(planted[root]) if other != center) for root in (0,4) for center in bits(planted[root]))
        shorts = tuple(short_hood(planted, root) for root in (0,4))
        token = profile_key(profile), tuple(sorted(edges)), qmax, shorts
        if token not in seen:
            form, _ = build_table(profile, edges, 6, 8, qmax, False)
            for root, short in zip((0,4), shorts):
                deck(form, graph, root, lib, short, 1)
            seen[token] = form
        form = seen[token]
        pins = [form.edge(src, dst, simplify=False) * (1 if planted[src] >> dst & 1 else -1) for src, dst in pairs(range(22))]
        with Cadical195(bootstrap_with=form.clauses) as solver:
            assert solver.solve(assumptions=pins)
        counts[shorts] += 1
    profile, edges, planted, _ = next(record for record in records if record[3] == 4)
    form, _ = build_table(profile, edges, 6, 8, 10, False)
    graph, _, _ = split(profile, edges)
    deck(form, graph, 0, {(1,1,1,1,1,1)}, False, 1)
    with Cadical195(bootstrap_with=form.clauses) as solver:
        assert not solver.solve(assumptions=[form.edge(src,dst,simplify=False)*(1 if planted[src] >> dst & 1 else -1) for src,dst in pairs(range(22))])
    assert sum(counts.values()) == 48
    print('PASS all 48 physical C22 component marks accepted; false profile rejected; local short flags', counts, 'distinct formulas', len(seen), 'signatures', sorted(lib))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--index', type=int)
    parser.add_argument('--panel', type=int)
    parser.add_argument('--arm', choices=('weak','joint'), default='joint')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.index is None:
        calibration()
    else:
        profiles = list(read_profiles(args.source))
        code, maximum, _ = target_catalogue()[args.panel]
        allowed = (2424,2431) if maximum == 12 else (2298,2424,2431)
        assert args.index in allowed
        edges = decode(code)
        graph, _, _ = split(profiles[args.index], edges)
        form, _ = build_table(profiles[args.index], edges, 9, 6, maximum, maximum == 12)
        if args.arm == 'joint':
            for root in (0,4):
                deck(form, graph, root, patterns([profiles[index] for index in allowed]), True, 1)
        form.write(args.out)
        print(args.index, args.panel, args.arm, form.nvars, len(form.clauses))
