from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path


def decode(record):
    order = ord(record[0]) - 63
    assert 0 <= order <= 62
    pairs = [(first, last) for last in range(order) for first in range(last)]
    bits = [int(bit) for char in record[1:] for bit in f"{ord(char) - 63:06b}"]
    assert len(pairs) <= len(bits) < len(pairs) + 6
    assert not any(bits[len(pairs):])
    rows = [set() for _ in range(order)]
    for (first, last), bit in zip(pairs, bits):
        if bit:
            rows[first].add(last)
            rows[last].add(first)
    return rows


def encode(rows):
    bits = [int(first in rows[last]) for last in range(len(rows)) for first in range(last)]
    bits.extend([0] * (-len(bits) % 6))
    return chr(len(rows) + 63) + "".join(
        chr(63 + sum(bit << (5 - offset) for offset, bit in enumerate(bits[index:index + 6])))
        for index in range(0, len(bits), 6)
    )


def admissible_pair(rows, first, last):
    return len(rows[first] & rows[last]) <= (0 if first in rows[last] else 2)


def all_pairs_admissible(rows):
    return all(admissible_pair(rows, first, last) for first, last in combinations(range(len(rows)), 2))


def circulant(order, steps):
    return [{(site + sign * step) % order for step in steps for sign in (-1, 1)}
            for site in range(order)]


def complete_columns(rows, degree, pending):
    if not pending:
        yield encode(rows)
        return
    site = pending[0]
    rest = pending[1:]
    need = degree - len(rows[site])
    available = [other for other in rest if len(rows[other]) < degree and not rows[site] & rows[other]]
    for partners in combinations(available, need):
        for other in partners:
            rows[site].add(other)
            rows[other].add(site)
        if all_pairs_admissible(rows):
            yield from complete_columns(rows, degree, rest)
        for other in partners:
            rows[site].remove(other)
            rows[other].remove(site)


def rooted(order, degree):
    spokes = range(1, degree + 1)
    doubletypes = tuple(combinations(spokes, 2))
    for choices in product((0, 1), repeat=len(doubletypes)):
        doubles = [mask for bit, mask in zip(choices, doubletypes) if bit]
        singleton_counts = [degree - 1 - sum(site in mask for mask in doubles) for site in spokes]
        if min(singleton_counts) < 0:
            continue
        masks = doubles + [(site,) for site, count in zip(spokes, singleton_counts) for _ in range(count)]
        zeros = order - degree - 1 - len(masks)
        if zeros < 0:
            continue
        masks.extend([()] * zeros)
        rows = [set(spokes)] + [{0} for _ in spokes] + [set(mask) for mask in masks]
        for column in range(degree + 1, order):
            for site in rows[column]:
                rows[site].add(column)
        if all_pairs_admissible(rows):
            yield from complete_columns(rows, degree, tuple(range(degree + 1, order)))


def independence(rows):
    sites = range(len(rows))
    return next(size for size in range(len(rows), 0, -1)
                if any(all(last not in rows[first] for first, last in combinations(group, 2))
                       for group in combinations(sites, size)))


def codegrees(rows):
    return Counter(len(rows[first] & rows[last]) for first, last in combinations(range(len(rows)), 2)
                   if last not in rows[first])


def hall_shortages(rows, root):
    contacts = rows[root]
    assert len(contacts) == independence(rows)
    outsiders = set(range(len(rows))) - contacts - {root}
    return [group for size in range(1, len(outsiders) + 1) for group in combinations(outsiders, size)
            if all(last not in rows[first] for first, last in combinations(group, 2))
            and len(set().union(*(rows[site] & contacts for site in group))) < size]


def hall_controls():
    for rows in (circulant(5, (1,)), circulant(13, (1, 5))):
        assert independence(rows) == len(rows[0])
        assert all(not hall_shortages(rows, root) for root in range(len(rows)))
    rows = circulant(5, (1,))
    rows[2].add(5)
    rows.append({2})
    contacts = rows[0]
    assert contacts == {1, 4} and not rows[5] & contacts
    assert all(last not in rows[first] for first, last in combinations((1, 4, 5), 2))
    assert independence(rows) == 3
    print("Hall literal controls: C5 and C13 pass all roots; added site 5 to C5 exposes {1,4,5}")


def filter_geng(order, degree, pathname):
    records = Path(pathname).read_text().splitlines()
    assert len(records) == len(set(records))
    kept = []
    for record in records:
        rows = decode(record)
        assert len(rows) == order and all(len(row) == degree for row in rows)
        assert encode(rows) == record
        assert all(not rows[first] & rows[last] for first in range(order) for last in rows[first])
        if all_pairs_admissible(rows):
            kept.append(record)
    if kept:
        print("\n".join(kept))


def inspect_low12(pathname):
    record, = Path(pathname).read_text().splitlines()
    rows = decode(record)
    support = [{other for other in range(12) if len(row & rows[other]) == 1} for row in rows]
    blocks = {frozenset({site} | neighbors) for site, neighbors in enumerate(support)}
    assert len(blocks) == 4 and all(len(block) == 3 for block in blocks)
    assert set.union(*(set(block) for block in blocks)) == set(range(12))
    assert all(support[site] == block - {site} and not rows[site] & block for block in blocks for site in block)
    assert codegrees(rows) == {1: 12, 2: 30} and independence(rows) == 4
    print("Low12: four disjoint independent triples in codegree-one support")


def inspect_low13(pathname):
    record, = Path(pathname).read_text().splitlines()
    rows = decode(record)
    assert codegrees(rows) == {1: 26, 2: 26} and independence(rows) == 4
    assert not any(all(len(rows[first] & rows[last]) == 1 for first, last in combinations(group, 2))
                   for group in combinations(range(13), 3))
    print("Low13: codegree-one support triangle-free; no high contact can meet three low sites")


def case_bound():
    for count_low, count_seven, expected in ((12, 16, [12]), (13, 14, [9, 11, 13])):
        eligible = [count_a for count_a in range(count_low + 1)
                    if (5 * count_low - count_a) % 2 == 0
                    and max(0, 2 * count_a - count_seven) <= count_low * (count_low - 16) + 5 * count_a]
        assert eligible == expected
    assert 13 - 2 - (5 - 1) > 8 - 2
    assert 2 * 13 > 3 * 8
    print("Integer cut: s=13 initial |B| in {0,2,4}; |B|=2 needs 7 distinct D7 contacts in 6 sites")
    candidates = []
    for count_eight in range(5, 13):
        count_low = count_eight + 8
        count_seven = 40 - 2 * count_low
        for count_b in range(0, count_low + 1, 2):
            count_a = count_low - count_b
            for singletons in range(4):
                if count_b < 2 * count_eight - singletons:
                    continue
                demand = max(0, 2 * count_a - count_seven) + count_b - count_eight
                budget = count_low * (count_low - 16) + 5 * count_a
                if demand <= budget:
                    candidates.append((count_eight, count_a, count_b, singletons))
    assert candidates == [(8, 2, 14, 2), (8, 2, 14, 3), (9, 1, 16, 2),
                          (9, 1, 16, 3), (10, 0, 18, 2), (10, 0, 18, 3)]
    for count_eight, _, count_b, singletons in candidates:
        double_fibres = count_eight - singletons
        excess = count_b - singletons - 2 * double_fibres
        if singletons == 3:
            assert excess == 1 and (double_fibres == 5 if count_eight == 8 else double_fibres > 5)
        else:
            assert excess == 0
            assert double_fibres - 1 > 5 or (count_eight == 8 and 8 - (double_fibres - 2) < 8)
    print("Occupied non-singleton fibres: only (n8,a,b)=(8,2,14),(9,1,16),(10,0,18), each with 2 or 3 singletons")


def main():
    parser = ArgumentParser()
    parser.add_argument("mode", choices=("rooted", "filter", "circulant", "controls", "inspect"))
    parser.add_argument("args", nargs="*")
    call = parser.parse_args()
    if call.mode == "rooted":
        for record in rooted(*map(int, call.args)):
            print(record)
    elif call.mode == "filter":
        order, degree, path = call.args
        filter_geng(int(order), int(degree), path)
    elif call.mode == "circulant":
        order, *steps = map(int, call.args)
        print(encode(circulant(order, steps)))
    elif call.mode == "inspect":
        inspect_low12(call.args[0])
        inspect_low13(call.args[1])
    else:
        hall_controls()
        case_bound()


if __name__ == "__main__":
    main()
