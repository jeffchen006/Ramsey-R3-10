#!/usr/bin/env python3
import random
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from one_neutral_control import decode, require


SHAPES = {16: {3322: 0, 3332: 1}, 17: {3333: 0, 4332: 0, 4333: 1}}
SIZE = {16: 2576, 17: 7}
SEED = 20261122


def bind_counts(order):
    roster = defaultdict(Counter)
    zero_hosts = set()
    for line in Path(f"count{order}.tsv").read_text().splitlines():
        host, degree, neutral, shape, triples, count = map(int, line.split())
        if count == 0:
            require((degree, neutral, shape, triples) == (0, 0, 0, 0) and host not in zero_hosts,
                    "bad zero host row")
            zero_hosts.add(host)
            continue
        require(0 < count and SHAPES[order].get(shape) == triples, "bad shape multiplicity")
        require((degree, neutral, shape) not in roster[host], "duplicate host shape profile")
        roster[host][degree, neutral, shape] = count
    require(set(roster) | zero_hosts == set(range(SIZE[order])) and not set(roster) & zero_hosts,
            "incomplete or contradictory host count")
    totals = Counter()
    for counts in roster.values():
        totals.update(counts)
    return roster, totals


def needed_pairs(totals):
    selected = {16: defaultdict(set), 17: defaultdict(set)}
    pairs = []
    generator = random.Random(SEED)
    subtotal = 0
    with Path("strata.tsv").open("w") as sink:
        print("D16", "d16", "shape16", "D17", "d17", "shape17", "frames16", "frames17", "ordered_headers",
              sep="\t", file=sink)
        for profile, count in sorted(totals[16].items()):
            degree, neutral, _ = profile
            for shape in sorted(SHAPES[17]):
                complement = degree + 9, 9 - neutral, shape
                other = totals[17][complement]
                if not other:
                    continue
                product = count * other
                subtotal += product
                print(*profile, *complement, count, other, product, sep="\t", file=sink)
                tail = {0, product // 2, product - 1} if product >= 3 else set(range(product))
                if product >= 16:
                    random_ordinals = generator.sample(range(product), 16)
                    ordinals = set(tail)
                    for element in random_ordinals:
                        if len(ordinals) >= 16:
                            break
                        ordinals.add(element)
                else:
                    ordinals = set(range(product))
                for ordinal in sorted(ordinals):
                    left_rank, right_rank = divmod(ordinal, other)
                    selected[16][profile].add(left_rank)
                    selected[17][complement].add(right_rank)
                    pairs.append((profile, complement, ordinal, left_rank, right_rank))
    return selected, pairs, subtotal


def verify_sample(row, graph, marks, union, shape):
    _, neutral, *_, degree, neutral_degree = row
    require(union == (1 << len(graph)) - 1 - (1 << neutral), "wrong neutral identification")
    private = set(range(len(graph))) - {neutral}
    require(degree == sum(len(graph[site]) for site in private) and neutral_degree == len(graph[neutral]),
            "bad private/neutral degree total")
    memberships = [set(site for site in private if mark & (1 << site)) for mark in marks]
    require(tuple(sorted(set(marks))) == marks and all(
        len(mark) == 5 and all(low not in graph[high] for low, high in combinations(mark, 2))
        for mark in memberships), "bad sampled mark")
    require(all(len(first & second) <= 1 for first, second in combinations(memberships, 2)), "repeated root pair")
    augmented = [row | {len(graph) + index for index, mark in enumerate(memberships) if site in mark}
                 for site, row in enumerate(graph)]
    require(all(len(row) <= 9 for row in augmented) and all(
        len(augmented[high] & augmented[low]) <= 5 for high in range(len(graph)) for low in range(high)),
        "bad sampled fixed cap/degree")
    singletons = {site for site in private if sum(site in mark for mark in memberships) == 1}
    require(int("".join(map(str, sorted((len(mark & singletons) for mark in memberships), reverse=True)))) == shape,
            "bad sampled singleton shape")


def frame_stream(engine, catalogue, order, requests, roster, totals):
    command = [engine, "frames", catalogue, str(order), str(SIZE[order]), "4", "9", "5", "5", "0", str(SIZE[order])]
    graphs = [decode(line) for line in Path(catalogue).read_text().splitlines()]
    selected = {}
    ranks = Counter()
    host_counts = defaultdict(Counter)
    prior = None
    with subprocess.Popen(command, stdout=subprocess.PIPE) as proc:
        for frame_id, line in enumerate(proc.stdout):
            row = tuple(map(int, line.split()))
            host, neutral, first, second, third, fourth, degree, neutral_degree = row
            identity = host, first, second, third, fourth
            require(prior is None or prior < identity, "frame ID not increasing (host, marks)")
            prior = identity
            repeated = first & second | (first | second) & third | (first | second | third) & fourth
            marks = (first, second, third, fourth)
            counts = sorted(((mark & ~repeated).bit_count() for mark in marks), reverse=True)
            shape = 1000 * counts[0] + 100 * counts[1] + 10 * counts[2] + counts[3]
            profile = degree, neutral_degree, shape
            rank = ranks[profile]
            ranks[profile] += 1
            host_counts[host][profile] += 1
            if rank in requests.get(profile, ()):
                verify_sample(row, graphs[host], marks, first | second | third | fourth, shape)
                selected[profile, rank] = frame_id, row
    require(proc.returncode == 0 and ranks == totals and host_counts == roster, "frame stream differs from count roster")
    require(len(selected) == sum(map(len, requests.values())), "missing requested frames")
    return selected


def main(engine, catalogue16, catalogue17):
    rosters, totals = {}, {}
    for order in (16, 17):
        rosters[order], totals[order] = bind_counts(order)
    requests, pairs, total = needed_pairs(totals)
    left = frame_stream(engine, catalogue16, 16, requests[16], rosters[16], totals[16])
    right = frame_stream(engine, catalogue17, 17, requests[17], rosters[17], totals[17])
    seen = set()
    with Path("pilot.index.tsv").open("w") as index, Path("pilot.frames").open("w") as frames, \
         Path("pilot.bound.tsv").open("w") as bound:
        print("pilot_row", "frame16", "frame17", "D16", "d16", "shape16", "shape17", "bucket_ordinal",
              "rank16", "rank17", sep="\t", file=index)
        for row_index, (profile, complement, ordinal, left_rank, right_rank) in enumerate(pairs):
            left_id, left_row = left[profile, left_rank]
            right_id, right_row = right[complement, right_rank]
            require((left_id, right_id) not in seen, "repeated pilot header")
            seen.add((left_id, right_id))
            print(row_index, left_id, right_id, *profile, complement[-1], ordinal, left_rank, right_rank,
                  sep="\t", file=index)
            print(*left_row[:6], *right_row[:6], sep="\t", file=frames)
            print(left_id, right_id, *left_row, *right_row, sep="\t", file=bound)
    print(f"frame16={sum(totals[16].values())} frame17={sum(totals[17].values())} headers={total} "
          f"strata={len({(first, second) for first, second, *_ in pairs})} pilot={len(pairs)} "
          f"unique_frame16={len(left)} unique_frame17={len(right)} seed={SEED}")


if __name__ == "__main__":
    main(*sys.argv[1:])
