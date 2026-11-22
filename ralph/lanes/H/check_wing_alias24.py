"""Check physical projections and retained aliases without running a solver."""

import csv
import hashlib
import itertools as it
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "scratch/D/c6r23"
FREEZE = STORE / "final23"


def read_g6(text):
    order = ord(text[0]) - 63
    assert 0 < order < 63
    serial = "".join(f"{ord(char) - 63:06b}" for char in text[1:])
    assert len(serial) - order * (order - 1) // 2 in range(6)
    rows = [set() for _ in range(order)]
    for bit, (low, high) in zip(serial, ((low, high) for high in range(order) for low in range(high))):
        if bit == "1":
            rows[low].add(high)
            rows[high].add(low)
    return rows


def max_independent(rows, pool):
    if not pool:
        return 0
    pivot = max(pool, key=lambda site: len(rows[site] & pool))
    tail = pool - {pivot}
    return max(max_independent(rows, tail), 1 + max_independent(rows, tail - rows[pivot]))


def cycles(rows, sites, start):
    first, second = sorted(rows[start] & sites)
    orders = []
    for neighbor in (first, second):
        order = [start, neighbor]
        while len(order) < 6:
            available = (rows[order[-1]] & sites) - set(order)
            if len(available) != 1:
                return []
            order.append(available.pop())
        if start not in rows[order[-1]]:
            return []
        orders.append(order)
    return orders


def controls():
    marks = 0
    histogram = Counter()
    for text in (ROOT / "gluing/val/r3_7_22.g6").read_text().splitlines():
        rows = read_g6(text)
        pairs = list(it.combinations(range(22), 2))
        if {len(row) for row in rows} != {6} or any(len(rows[x] & rows[y]) > 3 for x, y in pairs):
            continue
        assert all(not (rows[x] & rows[y]) for x, y in pairs if y in rows[x])
        assert max_independent(rows, set(range(22))) == 6
        for tip, opposite in pairs:
            common = rows[tip] & rows[opposite]
            if len(common) != 1:
                continue
            marks += 1
            wing = (rows[tip] | rows[opposite]) - common
            for selection in it.combinations(sorted(wing), 6):
                sites = set(selection)
                if any(len(rows[site] & sites) != 2 for site in sites) or not cycles(rows, sites, min(sites)):
                    continue
                leaving = [(site, other) for site in sites for other in rows[site] & (wing - sites)]
                histogram[len(leaving)] += 1
                if len(leaving) <= 1:
                    check_projection(rows, wing, sites, leaving)
    assert marks == 125
    rows = [set() for _ in range(11)]
    for first, second in [(site, (site + 1) % 6) for site in range(6)] + [
        (0, 6), (6, 7), (6, 8), (7, 9), (8, 9), (2, 10), (4, 10)
    ]:
        rows[first].add(second)
        rows[second].add(first)
    wing, sites = set(range(9)), set(range(6))
    check_projection(rows, wing, sites, [(0, 6)])
    assert (rows[0] & rows[7] & (wing - sites)) == {6}
    visible = set(range(11)) - {7, 8}
    assert len(rows[6] & rows[9] & visible) == 0 and len(rows[6] & rows[9]) == 2
    assert (rows[2] & rows[4] & visible) == {3, 10}
    rows[2].add(8)
    rows[8].add(2)
    assert (rows[2] & rows[6] & {7, 8}) == {8}
    print("C22 calibration:", marks, "marks; hex leaving-edge histogram", dict(sorted(histogram.items())))
    print("adverse controls: omit real flap endpoint; leave z's lower bound unweakened; reuse exactness at two flaps")


def check_projection(rows, wing, sites, leaving):
    kept_wing = sites | {other for _, other in leaving}
    hidden = wing - kept_wing
    kept = set(range(len(rows))) - hidden
    assert all(not (rows[site] & hidden) for site in sites)
    for first in kept_wing:
        for second in kept - {first}:
            exact = len(rows[first] & rows[second])
            visible = len(rows[first] & rows[second] & kept)
            assert exact - len(rows[first] & hidden) <= visible <= exact
            if first in sites or second in sites:
                assert exact == visible


def hex_alphabet(flap):
    pair_cap = {1 << first | 1 << second: (1 if (second - first) % 2 == 0 else 3)
                for first, second in it.combinations(range(6), 2) if second - first not in (1, 5)}
    defects = [(None, None), (0, None), (21, None), (42, None), *((None, pair) for pair in pair_cap)]
    decks = set()
    for special, missing in (defects[1:] if flap else defects[:1]):
        deck = [] if special is None else [special]
        for pair, limit in pair_cap.items():
            count = limit - (pair == missing) - (special is not None and pair & special == pair)
            assert count >= 0
            deck.extend([pair] * count)
        for site in range(6):
            singleton = 1 << site
            remaining = 6 - (flap and site == 0) - sum(bool(word & singleton) for word in deck)
            assert remaining >= 0
            deck.extend([singleton] * remaining)
        assert len(deck) == 21
        decks.add(tuple(sorted(deck)))
    assert len(decks) == (12 if flap else 1)
    return decks


def permute_words(deck, pinned, order):
    source_positions = [pinned.index(site) for site in order]
    return tuple(sorted(sum(1 << dest for dest, src in enumerate(source_positions) if word >> src & 1)
                        for word in deck))


def hub_cells(deck, index):
    by_group = Counter(deck)
    left, right = sorted(by_group, key=lambda word: (-by_group[word], word))[:2]
    assert by_group[left] == by_group[right] == 3
    hist = Counter()
    columns = [{pos for pos, word in enumerate(deck) if word >> bit & 1} for bit in range(6)]
    group1 = {pos for pos, word in enumerate(deck) if word == left}
    group2 = {pos for pos, word in enumerate(deck) if word == right}
    for picks in it.combinations(range(21), 7):
        picked = set(picks)
        if all(1 <= len(picked & column) <= 2 for column in columns):
            hist[len(picked & group1), len(picked & group2)] += 1
    records = {}
    for line in (STORE / f"hub/cover{index}.tsv").read_text().splitlines():
        key, count, mask1, mask2 = line.split()
        number, size1, size2 = map(int, key.split("_"))
        assert number == index and (size1, size2) not in records
        assert int(mask1) == sum(1 << pos for pos in group1) and int(mask2) == sum(1 << pos for pos in group2)
        records[size1, size2] = int(count)
        assert hist[size1, size2] == int(count)
    assert set(records) == set(it.product(range(4), repeat=2)) and len(hist) == 9
    print(f"hub {index}: {len(hist)} feasible cells, {sum(hist.values())} physical seven-subsets")
    return {f"hub/{index}_{head}_{tail}" for head, tail in hist}


def check_aliases(index_file):
    reference = json.loads(index_file.read_text())
    flap_decks = list(map(tuple, reference["one_flap"]))
    isolated_deck = tuple(sorted(reference["isolated"]))
    assert len(flap_decks) == 12 and set(flap_decks) == hex_alphabet(True)
    assert {isolated_deck} == hex_alphabet(False)
    by_deck = {deck: index for index, deck in enumerate(flap_decks)}
    assert permute_words(flap_decks[7], list(range(6)), [0, 5, 4, 3, 2, 1]) == flap_decks[4]
    hub = {index: hub_cells(flap_decks[index], index) for index in (1, 4)}
    specs = {record["shape"]: record for record in map(json.loads, (STORE / "shapes.jsonl").read_text().splitlines())}
    decks = {number: [tuple(json.loads(line)) for line in (STORE / f"decks{number}.jsonl").read_text().splitlines()]
             for number in specs}
    assert all(len(rows) == specs[number]["count"] for number, rows in decks.items())
    expected_keys = {f"{number}_{index}" for number, rows in decks.items() for index in range(len(rows))}
    with (FREEZE / "coverage.tsv").open() as handle:
        coverage = list(csv.DictReader(handle, delimiter="\t"))
    with (FREEZE / "receipts.tsv").open() as handle:
        receipt_rows = list(csv.DictReader(handle, delimiter="\t"))
    receipt = {row["receipt_rel_to_c6r23"]: row for row in receipt_rows}
    assert len(receipt) == len(receipt_rows) == 3078
    assert expected_keys == {row["key"] for row in coverage} and len(coverage) == len(expected_keys) == 3114
    alias_sources, all_sources, alias_keys = set(), set(), set()
    for row in coverage:
        sources = set(row["receipts_rel_to_c6r23"].split(";"))
        all_sources |= sources
        if row["effective"].split(":")[0] not in {"isolated_hex", "one_flap"}:
            continue
        alias_keys.add(row["key"])
        alias_sources |= sources
        number, index = map(int, row["key"].split("_"))
        spec, deck = specs[number], decks[number][index]
        rows, pinned = read_g6(spec["g6"]), spec["pinned"]
        sites, wing = set(pinned), set(range(16))
        assert len(sites) == 6 and len(wing) == len(rows)
        assert all(len(rows[site] & sites) == 2 for site in sites)
        leaving = [(site, other) for site in sites for other in rows[site] & (wing - sites)]
        assert len(leaving) == int(row["slack"]) == spec["slack"]
        assert all(sum(bool(word >> pos & 1) for word in deck) == 8 - len(rows[site])
                   for pos, site in enumerate(pinned))
        assert all((site < 8) != (other < 8) for site, neighbors in enumerate(rows) for other in neighbors)
        check_projection(rows, wing, sites, leaving)
        orders = cycles(rows, sites, leaving[0][0] if leaving else min(sites))
        assert len(orders) == 2
        physical = {permute_words(deck, pinned, order) for order in orders}
        if not leaving:
            assert physical == {isolated_deck}
            assert sources == {"hexone-1-0-1-1.cnf"} and row["orientations"] == "-"
        else:
            oriented = {by_deck[pattern] for pattern in physical}
            assert oriented == set(map(int, row["orientations"].split(",")))
            selected = row["effective"].split(":")[1]
            chosen = int(selected.removeprefix("hub"))
            assert chosen in oriented
            assert sources == (hub[chosen] if selected.startswith("hub") else {f"flap/{chosen}"})
    assert all_sources == set(receipt)
    assert len(alias_keys) == 62 and len(alias_sources) == 26
    assert {"6_0", "11_0"} <= alias_keys
    assert {int(key.split("_")[0]) for key in alias_keys} == {2, 6, 7, 8, 10, 11, 12}
    bytes_read = 0
    for source in sorted(alias_sources):
        if source.endswith(".cnf"):
            archive = STORE.parent / "roles15" / source.replace(".cnf", ".lrat")
            left_log, right_log = STORE / "hex.lrat-check.log", STORE / "hex.cake256.log"
            assert hashlib.sha256((STORE / source).read_bytes()).hexdigest() == receipt[source]["cnf_sha256"]
        else:
            archive = STORE / source / "proof.zst"
            left_log, right_log = STORE / source / "check.log", STORE / source / "cake.log"
        digest = hashlib.sha256()
        with archive.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        assert digest.hexdigest() == receipt[source]["archive_sha256"]
        assert archive.stat().st_size == int(receipt[source]["archive_bytes"])
        assert "c VERIFIED" in left_log.read_text().splitlines()
        assert "s VERIFIED UNSAT" in right_log.read_text().splitlines()
        bytes_read += archive.stat().st_size
    print(f"cover joins: {len(coverage)} keys, {len(receipt)} receipt IDs; {len(alias_keys)} aliases, "
          f"{len(alias_sources)} distinct alias archives ({bytes_read} bytes), retained markers")


if __name__ == "__main__":
    controls()
    check_aliases(Path(sys.argv[1]))
