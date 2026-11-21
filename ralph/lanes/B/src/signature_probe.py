"""Count exact pair-compatibility signatures on the dispersed anchor sample."""

from collections import Counter
from pathlib import Path


def independent_masks(rows, floor, ceiling):
    def search(vertices, selected, size):
        if size >= floor:
            yield selected
        if size == ceiling:
            return
        while vertices and vertices.bit_count() + size >= floor:
            bit = vertices & -vertices
            vertices ^= bit
            yield from search(vertices & ~rows[bit.bit_length()-1], selected | bit, size+1)

    yield from search((1 << len(rows))-1, 0, 0)


def decode(line):
    order = line[0]-63
    rows = [0]*order
    for right in range(1, order):
        for left in range(right):
            position = right*(right-1)//2 + left
            if (line[1+position//6]-63) & (32 >> (position % 6)):
                rows[left] |= 1 << right
                rows[right] |= 1 << left
    return rows


def members(mask):
    while mask:
        bit = mask & -mask
        mask ^= bit
        yield bit.bit_length()-1


def counts(rows, root_degree, alpha_bound, floor, ceilings):
    degree = [row.bit_count() for row in rows]
    witnesses = list(independent_masks(rows, alpha_bound-1, alpha_bound-1))
    full = (1 << len(witnesses))-1
    hits = [0]*len(rows)
    for index, witness in enumerate(witnesses):
        for vertex in members(witness):
            hits[vertex] |= 1 << index
    signatures, critical, critical_by_size = Counter(), Counter(), Counter()
    for candidate in independent_masks(rows, floor, alpha_bound-1):
        size = candidate.bit_count()
        if root_degree + sum(degree[vertex]+1 for vertex in members(candidate)) > ceilings[size+1]:
            continue
        missed = full
        for vertex in members(candidate):
            missed &= ~hits[vertex]
        signatures[missed] += 1
        if missed:
            critical[missed] += 1
            critical_by_size[(size, missed)] += 1
    return (sum(signatures.values()), len(signatures), sum(critical.values()),
            len(critical), len(critical_by_size))


def test():
    rows = decode(b'Cl')
    witnesses = set(independent_masks(rows, 2, 2))
    assert witnesses == {0b0101, 0b1010}
    result = counts(rows, 2, 3, 1, {2: 10, 3: 10})
    assert result == (6, 2, 6, 2, 4)
    print('C4 positive control: six candidates, two signatures, four size/signature keys')


def main():
    test()
    for level, root in ((44, 7), (52, 6)):
        totals = [0]*5
        for path in sorted(Path('work/paired_speed').glob(f'e{level}_b*.in')):
            for line in path.read_bytes().splitlines():
                result = counts(decode(line), root, 8, 4, {5:29, 6:36, 7:44, 8:53})
                totals = [previous + current for previous, current in zip(totals, result, strict=True)]
        print(f'e{level}: {totals} [sets, signatures, critical sets, critical signatures, critical size/signature keys]')


if __name__ == '__main__':
    main()
