#!/usr/bin/env python3
import itertools as it
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(line):
    order = ord(line[0]) - 63
    neighbours = [set() for _ in range(order)]
    bits = ((ord(symbol) - 63) >> index & 1 for symbol in line[1:]
            for index in range(5, -1, -1))
    for (high, low), edge in zip(((v, u) for v in range(order) for u in range(v)), bits):
        if edge:
            neighbours[low].add(high)
            neighbours[high].add(low)
    return neighbours


def encode(graph, sites):
    bits = [int(sites[low] in graph[sites[high]]) for high in range(len(sites)) for low in range(high)]
    bits += [0] * (-len(bits) % 6)
    return chr(63 + len(sites)) + "".join(
        chr(63 + sum(bit << (5 - index) for index, bit in enumerate(bits[start:start + 6])))
        for start in range(0, len(bits), 6))


def mask(sites):
    return sum(1 << site for site in sites)


def enumerate_literal(graph):
    if any(len(graph[high] & graph[low]) > 4 for high in range(len(graph)) for low in range(high)):
        return
    marks = [set(sites) for sites in it.combinations(range(len(graph)), 3)
             if all(low not in graph[high] for low, high in it.combinations(sites, 2))]
    for left, right in it.combinations(marks, 2):
        exterior = set(range(len(graph))) - (left | right)
        if len(exterior) != 1 or len(left & right) > 2:
            continue
        neutral, = exterior
        augmented = [row | ({len(graph)} if site in left else set())
                     | ({len(graph) + 1} if site in right else set())
                     for site, row in enumerate(graph)]
        if any(len(row) > 5 for row in augmented):
            continue
        if any(len(augmented[high] & augmented[low]) > 4
               for high in range(len(graph)) for low in range(high)):
            continue
        yield neutral, *sorted((mask(left), mask(right))), sum(len(graph[u]) for u in left | right), len(graph[neutral])


def join_grouped(source, target, order_source, order_target):
    buckets = defaultdict(list)
    for index, row in enumerate(target):
        buckets[row[-2:]].append(index)
    return {(index, other) for index, row in enumerate(source)
            for other in buckets.get((row[-2] + 5 * (order_target - order_source), 5 - row[-1]), ())}


def deficits(frame, catalogue):
    host, neutral, first, second, _, _ = frame
    graph = catalogue[host]
    private = set(range(len(graph))) - {neutral}
    require(all((first | second) & (1 << site) for site in private), "invalid control support")
    return len(graph[neutral]), sum(
        5 - len(graph[site]) - (first >> site & 1) - (second >> site & 1) for site in private)


def read_frame_table(path, catalogue):
    observed = [tuple(map(int, line.split())) for line in path.read_text().splitlines()]
    require(all(len(row) == 6 for row in observed), "frame column count")
    require(all(0 <= row[0] < len(catalogue) for row in observed), "frame host outside catalogue")
    require(all(len(catalogue[row[0]]) - 1 == (row[2] | row[3]).bit_count()
                for row in observed), "frame private size")
    require(all(5 * (len(catalogue[row[0]]) - 1) - 6 - row[-2] == deficits(row, catalogue)[1]
                for row in observed), "private degree total")
    expected = sorted((host, *rest) for host, graph in enumerate(catalogue) for rest in enumerate_literal(graph))
    require(sorted(observed) == expected, "literal frame roster differs")
    return observed


def physical_crossing(graph, orders, frames, labelled, catalogues):
    neutral_sites = [sites[frame[1]] for (sites, _), frame in zip(labelled, frames)]
    require(neutral_sites[0] == neutral_sites[1], "wrong physical neutral match")
    roots = [ordered_roots for _, ordered_roots in labelled]
    physical = [tuple(site for index, site in enumerate(sites) if index != frame[1])
                for (sites, _), frame in zip(labelled, frames)]
    order = (*roots[0], *roots[1], *physical[0], *physical[1], neutral_sites[0])
    require(len(order) == len(set(order)) == len(graph), "physical map is not a bijection")
    known = set(it.product(*roots))
    for order_size, (sites, ordered_roots), frame in zip(orders, labelled, frames):
        host, _, *remaining = frame
        window = catalogues[order_size][host]
        known.update((sites[low], sites[high]) for high, row in enumerate(window) for low in row if low < high)
        known.update((root, site) for root, mark in zip(ordered_roots, remaining[:2])
                     for index, site in enumerate(sites) if mark >> index & 1)
    crossing = {(low, high) for low, high in it.product(*physical) if low in graph[high]}
    expected = {frozenset((low, high)) for low, row in enumerate(graph) for high in row if low < high}
    restored = {frozenset(pair) for pair in known | crossing}
    require(expected == restored and crossing, "physical edge set not restored")
    broken = {frozenset(pair) for pair in known | (crossing - {min(crossing)})}
    degrees = Counter(site for edge in broken for site in edge)
    require(sum(degrees[site] != 5 for site in order) == 2, "broken crossing not detected")


def main(source, engine):
    listings = {6: [], 7: []}
    host_ids = {6: {}, 7: {}}
    plants = []
    regular = 0
    caps = Counter()
    for line in Path(source).read_text().splitlines():
        graph = decode(line)
        if set(map(len, graph)) != {5}:
            continue
        regular += 1
        cap = max(len(graph[low] & graph[high]) for high in range(16) for low in range(high))
        for shore in it.combinations(range(16), 2):
            for opposite in it.combinations(sorted(graph[shore[0]] & graph[shore[1]]), 2):
                if shore >= opposite:
                    continue
                roots = {0: shore, 1: opposite}
                root_sites = set(shore + opposite)
                private = {key: (graph[pair[0]] | graph[pair[1]]) - root_sites for key, pair in roots.items()}
                neutral_sites = set(range(16)) - root_sites - private[0] - private[1]
                if len(neutral_sites) != 1 or sorted(map(len, private.values())) != [5, 6]:
                    continue
                neutral, = neutral_sites
                caps[cap] += 1
                sides = sorted(private, key=lambda side: len(private[side]))
                plant = []
                labelled = []
                for side in sides:
                    sites = tuple(sorted(private[side] | {neutral}))
                    order = len(sites)
                    g6 = encode(graph, sites)
                    if g6 not in host_ids[order]:
                        host_ids[order][g6] = len(listings[order])
                        listings[order].append(g6)
                    index = {value: key for key, value in enumerate(sites)}
                    marked_roots = sorted((mask(index[site] for site in graph[root] & private[side]), root)
                                          for root in roots[side])
                    marks = tuple(value for value, _ in marked_roots)
                    labelled.append((sites, tuple(root for _, root in marked_roots)))
                    window = decode(g6)
                    plant.append((host_ids[order][g6], index[neutral], *marks,
                                  sum(len(window[index[site]]) for site in private[side]), len(window[index[neutral]])))
                plants.append((graph, plant, labelled))
    require(regular == 11 and caps == {3: 64, 4: 89}, f"smaller source census {regular} {caps}")
    tables, graphs = {}, {}
    for order, lines in listings.items():
        graphs[order] = list(map(decode, lines))
        g6 = Path(f"small{order}.g6")
        g6.write_text("".join(line + "\n" for line in lines))
        table = Path(f"small{order}.frames")
        with table.open("w") as sink:
            subprocess.run([engine, "frames", str(g6), str(order), str(len(lines)),
                            "2", "5", "4", "5", "0", str(len(lines))], stdout=sink, check=True)
        tables[order] = read_frame_table(table, graphs[order])
    total = 0
    for source, target in ((6, 7), (7, 6)):
        active, other = tables[source], tables[target]
        left = [deficits(row, graphs[source]) for row in active]
        right = [deficits(row, graphs[target]) for row in other]
        direct = {(lid, rid) for lid, (dl, sl) in enumerate(left) for rid, (dr, sr) in enumerate(right)
                  if dl + dr == 5 and sl == sr}
        fast = join_grouped(active, other, source, target)
        require(fast == direct, "bucket and literal ordered generation disagree")
        index = ({row: pid for pid, row in enumerate(active)}, {row: pid for pid, row in enumerate(other)})
        for graph, ordered, labels in plants:
            physical = ordered if source < target else ordered[::-1]
            labels = labels if source < target else labels[::-1]
            indices = tuple(mapping[row] for mapping, row in zip(index, physical))
            require(indices in direct, "missing planted header")
            physical_crossing(graph, (source, target), (active[indices[0]], other[indices[1]]), labels, graphs)
        print(f"read={source}/{target} hosts={len(graphs[source])}/{len(graphs[target])} "
              f"frames={len(active)}/{len(other)} exact_ordered_headers={len(direct)} plants={len(plants)}")
        total += len(fast)
    table = Path("small6.frames")
    original = table.read_text().splitlines()
    wrong = original[0].split()
    wrong[-2] = str(1 + int(wrong[-2]))
    wrong_size = list(map(str, tables[7][0]))
    wrong_size[0] = original[0].split()[0]
    bad = Path("bad.control.frames")
    for name, rest, message in (("swapped size", [" ".join(wrong_size), *original[1:]], "frame private size"),
                                ("dropped frame", original[1:], "literal frame roster differs"),
                                ("wrong private-degree total", [" ".join(wrong), *original[1:]], "private degree total")):
        bad.write_text("\n".join(rest) + "\n")
        try:
            read_frame_table(bad, graphs[6])
        except ValueError as error:
            require(str(error) == message, f"unexpected diagnostic: {error}")
            print(f"mutation rejected: {name}")
        else:
            raise ValueError(f"mutation accepted: {name}")
    bad.unlink()
    print(f"regular={regular} physical_bicliques={len(plants)} crossing_mutations={len(plants) * 2} both_read_total={total}")


if __name__ == "__main__":
    main(*sys.argv[1:])
