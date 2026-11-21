#!/usr/bin/env python3
"""Small labelled oracle and reproducible three-orbit calibration fixture."""

import argparse
from itertools import combinations
from pathlib import Path
from random import Random
from types import SimpleNamespace

from orbit_extend import independent, independent_sets, parse_graph6, perm_for, to_graph6
from window_repair import SetEngine, Window, repair


def oracle(library):
    random = Random(31147)
    engine = SetEngine(library)
    counters = {'model': 0, 'unsat': 0, 'soft': 0, 'nonempty_frozen': 0}
    for trial in range(60):
        cycles = ((3, 3, 1), (2, 2, 2, 1), (3, 1, 1, 1, 1))[trial % 3]
        bases = [sum(cycles[:index]) for index in range(len(cycles))]
        masks = [((1 << length) - 1) << base for base, length in zip(bases, cycles)]
        size = sum(cycles)
        permutation = perm_for(cycles)
        all_vertices = (1 << size) - 1
        args = SimpleNamespace(k=random.choice([3, 4]), min_degree=random.randrange(3),
                               max_degree=random.randrange(2, 6), min_edges=random.randrange(10),
                               flips=random.choice([None, 1, 2, 3]), attachment=random.choice([None, 1, 2]),
                               batch=2, conflicts=20000, rounds=300, deviation=trial % 2,
                               frontier=12 if trial % 4 < 2 else 0, max_edges=5 if trial % 5 == 0 else None)
        chosen = random.sample(masks, random.choice([1, 2]))
        movable = sum(chosen)
        seed_window = Window([0] * size, permutation, bases, all_vertices, args)
        orbits = list(enumerate(seed_window.orbits, 1))
        random.shuffle(orbits)
        active = []
        seed = [0] * size
        for index, _ in orbits[:random.randrange(len(orbits) + 1)]:
            graph = seed_window.graph([*active, index])
            if all(independent(mask, graph) for mask in graph):
                active.append(index)
                seed = graph
        bad = list(independent_sets(seed, all_vertices, args.k))
        assert set(engine.sets(seed, args.k, 1000)) == set(bad)
        frozen = sum(not (witness & movable) for witness in bad)
        fixed = sum(mask for mask, length in zip(masks, cycles) if length == 1)
        tests = [frozen, frozen + 1, frozen + 2, frozen + 3, frozen + 6]
        window = Window(seed, permutation, bases, movable, args)
        minimum = float('inf')
        for state in range(1 << len(window.orbits)):
            model = [index for index in range(1, len(window.orbits) + 1) if state >> (index - 1) & 1]
            graph = window.graph(model)
            flips = sum((lit > 0) != (abs(lit) in model) for lit in window.phases)
            degrees = [mask.bit_count() for mask in graph]
            if (args.flips is not None and flips > args.flips or flips < args.deviation or min(degrees) < args.min_degree or
                    max(degrees) > args.max_degree or sum(degrees) < 2 * args.min_edges or
                    args.max_edges is not None and sum(degrees) > 2 * args.max_edges or
                    not all(independent(mask, graph) for mask in graph) or
                    args.attachment is not None and any((mask & fixed).bit_count() > args.attachment
                                                        for vertex, mask in enumerate(graph)
                                                        if not (fixed >> vertex & 1))):
                continue
            count = sum(1 for _ in independent_sets(graph, all_vertices, args.k))
            minimum = min(count, minimum)
        for goal in tests:
            status, graph, count, _ = repair(window, bad, frozen, permutation, engine, goal)
            assert status == ('model' if minimum <= goal else 'unsat'), (trial, goal, minimum, status)
            if status == 'model':
                recount = sum(1 for _ in independent_sets(graph, all_vertices, args.k))
                assert minimum <= recount == count <= goal
            counters[status] += 1
            counters['soft'] += goal > frozen
            counters['nonempty_frozen'] += frozen > 0
    print(f'PASS {counters}', flush=True)


def compound_fixture(graph_path, output, library):
    base = parse_graph6(graph_path.read_text().strip())
    cycles = [2] * (len(base) // 2) + [1] * (len(base) % 2)
    permutation = perm_for(cycles)
    assert all(base[vertex] >> other & 1 for vertex in range(len(base))
               for other in range(vertex + 1, len(base))
               if base[permutation[vertex]] >> permutation[other] & 1)
    window = Window(base, permutation, list(range(0, len(base), 2)), (1 << len(base)) - 1,
                    SimpleNamespace(min_degree=0, max_degree=9, attachment=None, min_edges=0, flips=None))
    active = {lit for lit in window.phases if lit > 0}
    random = Random(10403)
    engine = SetEngine(library)
    assert not engine.sets(base, 10, 1)
    orbit_masks = [3 << index for index in range(0, len(base), 2)]
    covers = [[sum(group) for group in combinations(orbit_masks, width)] for width in (2, 3)]
    for trial in range(1, 1501):
        removed = random.sample(sorted(active), 5)
        seed = window.graph(active.difference(removed))
        bad = engine.sets(seed, 10, 2000)
        if not bad or len(bad) >= 2000:
            continue
        counts = [sum(all(mask & witness for witness in bad) for mask in level) for level in covers]
        if counts[0] or not counts[1]:
            continue
        output.write_text(to_graph6(seed) + '\n')
        print(f'fixture trial={trial} independent10={len(bad)} 2/3-orbit covers={counts}; '
              f'removed={[window.orbits[lit - 1] for lit in removed]}', flush=True)
        return
    raise RuntimeError('no suitable fixture')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, default=Path('../build/window_sets.so'))
    parser.add_argument('--fixture', nargs=2, type=Path)
    options = parser.parse_args()
    if options.fixture:
        compound_fixture(*options.fixture, options.library)
    else:
        oracle(options.library)
