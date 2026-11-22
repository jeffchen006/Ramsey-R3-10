"""Marked Y support census. Never pairs wings or calls a solver."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from math import factorial
from pathlib import Path
import json
import sys


def pairs(order):
    return tuple((1 << left) | (1 << right) for left, right in combinations(range(order), 2))


def family_fails(rows):
    covered = 0
    for mask in rows:
        covered |= mask
    return len(rows) > covered.bit_count()


def hall(order, ordinary, triple):
    for special in (0, triple):
        edges = [mask for mask in ordinary if not special or mask & special]
        for center in range(order):
            family = [mask for mask in edges if mask & (1 << center)]
            if special:
                family.append(special)
            if family_fails(family):
                return 'triple' if special else 'ordinary'
        for vertices in combinations(range(order), 3):
            cover = sum(1 << vertex for vertex in vertices)
            family = [mask for mask in edges if mask & cover == mask]
            if special:
                family.append(special)
            if family_fails(family):
                return 'triple' if special else 'ordinary'
    return 'pass'


def all_words(degrees, triple):
    order = len(degrees)
    ordinary = tuple(degree - (triple >> index & 1) for index, degree in enumerate(degrees))

    @lru_cache(None)
    def rows(total, bounds):
        if not bounds:
            return [()] if total == 0 else []
        return [(weight, *tail) for weight in range(min(total, bounds[0]) + 1)
                for tail in rows(total - weight, bounds[1:])]

    def visit(vertex, need, prefix):
        if not need:
            yield bytes(prefix)
            return
        bounds = tuple(min(remaining, 2 - ((triple >> vertex) & (triple >> neighbor) & 1))
                       for neighbor, remaining in enumerate(need[1:], vertex + 1))
        for row in rows(need[0], bounds):
            yield from visit(vertex + 1, tuple(remaining - weight for remaining, weight in zip(need[1:], row)), prefix + row)

    yield from visit(0, ordinary, ())


def actions(order, triple):
    masks = pairs(order)
    for tail in permutations(range(1, order)):
        perm = (0, *tail)
        def image(mask):
            return sum(1 << dest for src, dest in enumerate(perm) if mask >> src & 1)
        if image(triple) == triple:
            yield tuple(masks.index(image(mask)) for mask in masks)


def orbit_roster(degrees, triple):
    order = len(degrees)
    masks = pairs(order)
    group = list(actions(order, triple))
    universe = set(all_words(degrees, triple))
    for word in sorted(universe):
        if word not in universe:
            continue
        orbit = {bytes(word[index] for index in action) for action in group}
        assert orbit <= universe and min(orbit) == word
        universe -= orbit
        ordinary = [mask for mask, weight in zip(masks, word) for _ in range(weight)]
        aut = sum(all(word[dst] == word[src] for src, dst in enumerate(action)) for action in group)
        assert len(orbit) * aut == len(group)
        yield dict(triple=triple, word=''.join(map(str,word)), status=hall(order, ordinary, triple),
                   aut=aut, fixed=len(orbit), oriented=factorial(order)//aut)
    assert not universe


def literal_fails(rows):
    return any(family_fails(family) and all(left & right for left, right in combinations(family, 2))
               for size in range(len(rows) + 1) for family in combinations(rows, size))


def controls():
    masks = pairs(4)
    states = Counter()
    for word in product(range(3), repeat=6):
        ordinary = [mask for mask, weight in zip(masks,word) for _ in range(weight)]
        for triple in (7,14):
            if any(weight + int(mask & triple == mask) > 2 for mask,weight in zip(masks,word)):
                continue
            status = hall(4,ordinary,triple)
            literal = 'ordinary' if literal_fails(ordinary) else 'triple' if literal_fails(ordinary+[triple]) else 'pass'
            assert status == literal
            states[status] += 1
    assert min(states[key] for key in ('ordinary','triple','pass')) > 0
    print('four-pole literal subsets classifications incl parallel edges:', sorted(states.items()))
    for triple in (7,14):
        truth = {bytes(word) for word in product(range(3),repeat=6)
                 if all(weight + int(mask & triple == mask) <= 2 for mask,weight in zip(masks,word))
                 and [sum(weight for mask,weight in zip(masks,word) if mask >> vertex & 1) + (triple >> vertex & 1)
                      for vertex in range(4)] == [3,2,2,2]}
        assert truth == set(all_words((3,2,2,2),triple)) and truth
        reps = list(orbit_roster((3,2,2,2),triple))
        assert sum(row['fixed'] for row in reps) == len(truth)
        print('four-pole fixed triple',triple,'words',len(truth),'reps',len(reps))
    left, right = (1,2,2,2),(2,2,2,2)
    for perm in permutations(range(4)):
        direct = tuple(left[site] for site in perm),tuple(right[site] for site in perm)
        assert (direct == (left,right)) == (perm[0] == 0)
        assert direct[::-1] != (left,right)
    assert hall(4,[9,10,12,9],7) == 'triple'
    print('negative control: T=012 plus 03,03,13,23 passes ordinary Hall but fails with T; no marked swap')
    known_graphs()


def known_graphs():
    import networkx as nx
    root = Path(__file__).resolve().parents[3]
    counts = Counter()
    lines = (root/'gluing/val/r3_7_22.g6').read_bytes().splitlines()
    for line in lines:
        graph = nx.from_graph6_bytes(line)
        if any(deg != 6 for _,deg in graph.degree()):
            continue
        counts['regular'] += 1
        stars = [set(graph[site]) for site in graph]
        if max(len(stars[left] & stars[right]) for left,right in combinations(graph,2)) > 3:
            continue
        counts['hosts'] += 1
        for left,right in combinations(graph,2):
            common = stars[left] & stars[right]
            if len(common) != 1 or right in stars[left]:
                continue
            middle, = common
            poles = sorted(stars[middle]-{left,right})
            rest = sorted(set(graph)-stars[left]-stars[right]-stars[middle]-{left,right,middle})
            contacts = [sum(1 << index for index,pole in enumerate(poles) if site in stars[pole]) for site in rest]
            assert not literal_fails(contacts) and len(poles)+2 == 6
            for first,second in combinations(poles,2):
                other = (stars[first]&stars[second])-{middle}
                assert len(other) <= 2 and other <= set(rest)|stars[left]|stars[right]
            counts['marks'] += 1
            counts['mark with triple'] += any(mask.bit_count()==3 for mask in contacts)
    assert len(lines)==191 and (counts['regular'],counts['hosts'],counts['marks'])==(10,3,125)
    print('C22 known physical Hall and pair-upper checks', sorted(counts.items()))


def census(destination):
    with destination.open('x') as output:
        for triple in (7,14):
            stats = Counter()
            for record in orbit_roster((5,4,4,4,4,4,4),triple):
                output.write(json.dumps(record,separators=(',',':'))+'\n')
                for key in ('reps','fixed','oriented'):
                    stats[record['status'],key] += record.get(key,1)
            print('triple',triple,'(status,measure):',sorted(stats.items()),flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'controls':
        controls()
    elif sys.argv[1] == 'census':
        census(Path(sys.argv[2]))
    else:
        raise SystemExit('controls | census NEW-ROSTER')
