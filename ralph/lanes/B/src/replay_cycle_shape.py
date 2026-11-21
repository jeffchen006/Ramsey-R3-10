"""Replay the four-vertex subclaim of CYCLE162.md across all labelled masks."""

from itertools import combinations


def survives(rows):
    return (all(len(row) <= 2 for row in rows) and
            all(not rows[left].intersection(rows[right]) if right in rows[left]
                else bool(rows[left].intersection(rows[right]))
                for left, right in combinations(range(len(rows)), 2)))


def matrices(order):
    pairs = list(combinations(range(order), 2))
    for mask in range(1 << len(pairs)):
        rows = [set() for _ in range(order)]
        for index, (left, right) in enumerate(pairs):
            if mask & (1 << index):
                rows[left].add(right)
                rows[right].add(left)
        yield rows


controls = [rows for rows in matrices(3) if survives(rows)]
assert len(controls) == 3 and all(sorted(map(len, rows)) == [1, 1, 2] for rows in controls)
targets = [rows for rows in matrices(4) if survives(rows)]
assert len(targets) == 3 and all([len(row) for row in rows] == [2, 2, 2, 2] for rows in targets)
print('three labelled P3 controls; exactly three labelled C4 targets out of 64 masks')


def component_shape(rows):
    unseen = set(range(len(rows)))
    shape = []
    while unseen:
        pending = [unseen.pop()]
        vertices = []
        while pending:
            vertex = pending.pop()
            vertices.append(vertex)
            for neighbor in rows[vertex] & unseen:
                unseen.remove(neighbor)
                pending.append(neighbor)
        shape.append(('C' if all(len(rows[vertex]) == 2 for vertex in vertices) else 'P', len(vertices)))
    return tuple(sorted(shape))


shapes = set()
for rows in matrices(6):
    if any(len(row) > 2 for row in rows) or not 10 <= sum(map(len, rows)) <= 12:
        continue
    if any(rows[left] & rows[right] for left, right in combinations(range(6), 2) if right in rows[left]):
        continue
    shapes.add(component_shape(rows))
assert shapes == {(('P', 6),), (('C', 4), ('P', 2)), (('C', 5), ('P', 1)), (('C', 6),)}
print('exhaustive six-label max-degree-two shape replay agrees:', sorted(shapes))
