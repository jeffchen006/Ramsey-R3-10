"""Physical small-case controls for the pole and two-term footprint interfaces."""

from collections import Counter
from itertools import combinations

from check_round13_controls import records


def submasks(mask):
    subset = mask
    while True:
        yield subset
        if subset == 0:
            return
        subset = (subset - 1) & mask


def independent(rows, subset):
    return all(not row & subset for vertex, row in enumerate(rows) if subset >> vertex & 1)


def independence(rows):
    return max(subset.bit_count() for subset in submasks((1 << len(rows)) - 1)
               if independent(rows, subset))


def adjacency(order, edges):
    rows = [0] * order
    for first, second in edges:
        rows[first] |= 1 << second
        rows[second] |= 1 << first
    return rows


def mate_invariant(rows, mate):
    old_pairs = combinations(range(len(mate)), 2)
    return all(((rows[first] >> second) & 1) == ((rows[mate[first]] >> mate[second]) & 1)
               for first, second in old_pairs)


def mate_and_columns(tally):
    cycle_edges = [(vertex, (vertex + 1) % 5) for vertex in range(5)]
    cycle = adjacency(5, cycle_edges)
    assert mate_invariant(cycle, (3, 2, 1, 0))
    assert independence(cycle) == cycle[4].bit_count() == 2 and cycle[4] == 9
    mutation = adjacency(5, cycle_edges[:-1])
    assert mate_invariant(mutation, (3, 2, 1, 0))
    assert independence(mutation) == 3 and independent(mutation, 21)
    for order in (5, 6):
        edges = list(combinations(range(order), 2))
        for mask in range(1 << len(edges)):
            chosen = [edge for bit, edge in enumerate(edges) if mask >> bit & 1]
            rows = adjacency(order, chosen)
            if any(rows[first] & rows[second] for first, second in chosen):
                continue
            alpha = independence(rows)
            tally[order, 'labelled triangle-free'] += 1
            for mate in ((1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0)):
                if not mate_invariant(rows, mate):
                    continue
                for pole in range(4, order):
                    contacts = rows[pole] & 15
                    image = sum(1 << mate[site] for site in range(4) if contacts >> site & 1)
                    assert independent(rows, image)
                    if contacts.bit_count() == alpha:
                        assert contacts & image and independent(rows, contacts)
                        tally['maximal mate positives'] += 1
                    if not contacts & image:
                        assert independent(rows, image | (1 << pole))
                        tally['disjoint mate extends'] += 1
            if order == 6:
                poles = range(2, 6)
                columns = [rows[pole] & 3 for pole in poles]
                disjoint = not any(first & second for first, second in combinations(columns, 2))
                slots = [(rows[site] & 60).bit_count() for site in (0, 1)]
                assert disjoint == (max(slots) <= 1)
                if not disjoint:
                    tally['adverse overlapping columns'] += 1
                    continue
                tally['literal disjoint four-column graphs'] += 1
                for pole, column in zip(poles, columns):
                    first, second = next((first, second)
                        for first, second in combinations([peer for peer in poles if peer != pole], 2)
                        if not (rows[first] >> second & 1))
                    assert independent(rows, column | (1 << first) | (1 << second))
                    assert column.bit_count() + 2 <= alpha
                    if column and column.bit_count() + 2 == alpha:
                        tally['tight positive columns'] += 1
    assert tally[5, 'labelled triangle-free'] == 388
    assert tally[6, 'labelled triangle-free'] == 5789
    assert tally['maximal mate positives'] and tally['tight positive columns']


def footprints(tally):
    for name, regular_count in (('r35_13', 1), ('r37_22', 10)):
        regular = [rows for rows in records(name) if len({len(row) for row in rows}) == 1]
        assert len(regular) == regular_count
        for rows in regular:
            order = len(rows)
            universe = set(range(order))
            degree = len(rows[0])
            codegree = max(len(rows[first] & rows[second]) for first, second in combinations(universe, 2))
            for offset in range(order):
                boundary = tuple((offset + delta) % order for delta in (0, 1, 3, 5, 8))
                opposite = set(sorted(universe.difference(boundary))[:5])
                for mask in range(1 << len(boundary)):
                    selected = tuple(vertex for bit, vertex in enumerate(boundary) if mask >> bit & 1)
                    neighborhoods = {vertex: rows[vertex].difference(boundary) for vertex in selected}
                    reached = set().union(*neighborhoods.values())
                    sizes = sum(degree - len(rows[vertex].intersection(boundary)) for vertex in selected)
                    actual = 0
                    caps = 0
                    for first, second in combinations(selected, 2):
                        actual += len(neighborhoods[first] & neighborhoods[second])
                        inside = len((rows[first] & rows[second]).intersection(boundary))
                        upper = 0 if first in rows[second] else codegree
                        caps += upper - inside
                    assert actual <= caps
                    assert sizes - caps <= sizes - actual <= len(reached)
                    assert len(reached) <= order - 5
                    opposite_hits = len(reached & opposite)
                    assert sizes - caps <= (order - 10) + opposite_hits
                    tally[order, 'footprints'] += 1
                    if sizes > len(reached):
                        tally['adverse ignoring overlaps'] += 1
                    if len(reached) > len(reached - opposite):
                        tally['physical opposite contacts'] += 1
    assert tally[13, 'footprints'] == 13 * 32
    assert tally[22, 'footprints'] == 10 * 22 * 32
    assert tally['adverse ignoring overlaps']


if __name__ == '__main__':
    counts = Counter()
    mate_and_columns(counts)
    footprints(counts)
    for key, value in counts.items():
        print(f'{key}: {value}')
    print('PASS', 'C5/P5 mate mutation; labelled four-pole/slot controls; smaller physical footprints')
