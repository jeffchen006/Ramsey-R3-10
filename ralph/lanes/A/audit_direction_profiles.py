#!/usr/bin/env python3
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
import csv
import sys

from one_neutral_control import decode, read_frame_table, require

WEIGHT_HEADER = 'order\tD\td\thost\tneutral\tprofile\tcount'


def bits(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


@dataclass(frozen=True)
class Frame:
    local: tuple
    dest: tuple
    marks: tuple
    assigned: tuple

    @property
    def profile(self):
        return tuple(sorted(tuple(sorted(group)) for group in self.assigned))


class Catalogue:
    def __init__(self, file, degree):
        self.lines = Path(file).read_text().splitlines()
        self.graphs = list(map(decode, self.lines))
        self.order = len(self.graphs[0])
        require(all(len(graph) == self.order for graph in self.graphs), 'nonuniform catalogue')
        self.degree = degree
        self.margin = {}
        self.row_types = {}
        for host, graph in enumerate(self.graphs):
            total = sum(map(len, graph))
            for neutral in range(self.order):
                self.margin[host, neutral] = (total - len(graph[neutral]), len(graph[neutral]))
                self.row_types[host, neutral] = tuple(
                    2 * (degree - 1 - len(row) + (neutral in row)) + (neutral in row)
                    for row in graph)

    @lru_cache(maxsize=8192)
    def group(self, host, neutral, singles):
        table = self.row_types[host, neutral]
        return tuple(table[site] for site in bits(singles))

    def frame(self, row):
        host, neutral, *marks = row
        require(all(first < second for first, second in zip(marks, marks[1:])), 'mark order')
        union, repeated = 0, 0
        for mark in marks:
            repeated |= union & mark
            union |= mark
        require(union == ((1 << self.order) - 1) ^ (1 << neutral), 'mark union')
        assigned = tuple(self.group(host, neutral, mark & ~repeated) for mark in marks)
        require(all(2 <= len(group) <= 4 and min(group) >= 0 for group in assigned), 'invalid demand group')
        return Frame(self.margin[host, neutral], (host, neutral), tuple(marks), assigned)


def profile_text(profile):
    return ';'.join(','.join(map(str, group)) for group in profile)


def complement(local, degree, difference):
    private_degrees, neutral_degree = local
    return private_degrees + degree * difference, degree - neutral_degree


def weighted_index(frames):
    index = defaultdict(lambda: defaultdict(Counter))
    for frame in frames:
        index[frame.local][frame.dest][frame.profile] += 1
    return index


def write_weight_rows(catalogue, grand, output):
    for (private, neutral, host, site, profile), total in sorted(grand.items()):
        print(catalogue.order, private, neutral, host, site, profile_text(profile), total, sep='\t', file=output)


def measure_small(left_cat, right_cat, left, right, observations, plants_file, plant6, plant7):
    matches = {}
    for left_id, left_frame in enumerate(left):
        for right_id, right_frame in enumerate(right):
            if complement(left_frame.local, 5, 1) == right_frame.local:
                matches[left_id, right_id] = (left_frame, right_frame)
    require(matches.keys() == observations.keys() and len(matches) == 34_504, 'literal ordered coverage')
    group_maps = ({}, {})
    full_maps = ({}, {})
    category = Counter()
    rows_by_bit = defaultdict(set)
    for ids, frames in matches.items():
        flags = []
        for side, (source, target, text) in enumerate(zip(frames, frames[::-1], observations[ids])):
            require(len(text) == len(source.assigned), 'wrong number of group bits')
            for assigned, bit in zip(source.assigned, text):
                demands = tuple(sorted(assigned))
                key = (target.dest, demands)
                require(group_maps[side].setdefault(key, bit == '1') == (bit == '1'), 'group cache collision')
                rows_by_bit[side, target.dest, demands, bit].add(assigned)
            flag = '0' not in text
            require(full_maps[side].setdefault((target.dest, source.profile), flag) == flag,
                    'full profile cache collision')
            flags.append(flag)
        category[tuple(flags)] += 1

    def filtered(side, source_weights, destination):
        def exists(profile):
            return all(group_maps[side][destination, group] for group in profile)
        return sum(weight for profile, weight in source_weights.items() if exists(profile))

    def for_order(left_first):
        indices = weighted_index(left), weighted_index(right)
        read_order = (0, 1) if left_first else (1, 0)
        first, second = (indices[side] for side in read_order)
        difference = 1 if left_first else -1
        weight = Counter()
        for first_key, first_dests in first.items():
            for (first_dest, first_profiles), (second_dest, second_profiles) in product(
                    first_dests.items(), second.get(complement(first_key, 5, difference), {}).items()):
                first_all, second_all = sum(first_profiles.values()), sum(second_profiles.values())
                first_pass = filtered(read_order[0], first_profiles, second_dest)
                second_pass = filtered(read_order[1], second_profiles, first_dest)
                weight[True, True] += first_pass * second_pass
                weight[True, False] += first_pass * (second_all - second_pass)
                weight[False, True] += (first_all - first_pass) * second_pass
                weight[False, False] += (first_all - first_pass) * (second_all - second_pass)
        literal = category if left_first else Counter({(rev, fwd): n for (fwd, rev), n in category.items()})
        require(weight == literal, 'weighted intersection differs from literal flags')
        return weight

    print(f'small group keys {list(map(len, group_maps))}; whole-profile keys {list(map(len, full_maps))}')
    for left_first in (True, False):
        weight = for_order(left_first)
        print(f'small read={"6/7" if left_first else "7/6"} total={weight.total()} '
              f'both_pass={weight[True, True]} read_only={weight[True, False]} '
              f'reverse_only={weight[False, True]} neither_pass={weight[False, False]}')

    plant_lines = [Path(file).read_text().splitlines() for file in (plant6, plant7)]
    host_id = [{line: index for index, line in enumerate(cat.lines)} for cat in (left_cat, right_cat)]
    frame_id = [{(frame.dest, frame.marks): index for index, frame in enumerate(side)} for side in (left, right)]
    checked_plants = set()
    distinct = set()
    for row in map(str.split, Path(plants_file).read_text().splitlines()):
        plant, repeat, *ends = map(int, row)
        require(plant == repeat and len(ends) == 8 and plant not in checked_plants, 'plant identity')
        literal = []
        for side in range(2):
            host, neutral, *marks = ends[4 * side:4 * side + 4]
            literal.append(frame_id[side][((host_id[side][plant_lines[side][host]], neutral), tuple(marks))])
        ids = tuple(literal)
        require(ids in matches and all('0' not in text for text in observations[ids]), 'literal plant lost')
        for source_side in (0, 1):
            source, target = matches[ids][source_side], matches[ids][1 - source_side]
            require(all(group_maps[source_side][target.dest, group] for group in source.profile), 'compressed plant lost')
        checked_plants.add(plant)
        distinct.add(ids)
    require(checked_plants == set(range(153)), 'plant coverage')
    print(f'small plants={len(checked_plants)} distinct_IDs={len(distinct)} retained both ways')

    reject_id, accept_id = (251, 326), (256, 326)
    reject, accept, source = left[reject_id[0]], left[accept_id[0]], right[reject_id[1]]
    require(reject.local == accept.local and reject.dest[1] == accept.dest[1] and
            reject.dest[0] != accept.dest[0] and
            left_cat.graphs[reject.dest[0]] != left_cat.graphs[accept.dest[0]], 'bad adjacency witness')
    require('0' in observations[reject_id][1] and '0' not in observations[accept_id][1],
            'equal-margin adjacency witness no longer separates')
    print(f'adjacency counterexample src_order=7 source_frame={reject_id[1]} margins={reject.local} '
          f'profile={profile_text(source.profile)} target_frame={reject_id[0]}:{observations[reject_id][1]},'
          f'{accept_id[0]}:{observations[accept_id][1]} destinations={reject.dest},{accept.dest} '
          f'host_g6={left_cat.lines[reject.dest[0]]},{left_cat.lines[accept.dest[0]]}')

    for (side, dest, demands, flag), assigned_set in rows_by_bit.items():
        if len(assigned_set) > 1:
            print(f'row permutation example dir={side} target={dest} type={demands} '
                  f'assignments={sorted(assigned_set)} common_answer={flag}')
            break
    else:
        raise ValueError('no different row ordering tested')
    for cat, side in zip((left_cat, right_cat), (left, right)):
        grand = Counter((*frame.local, *frame.dest, frame.profile) for frame in side)
        with Path(f'small.weights{cat.order}.tsv').open('w') as stream:
            print(WEIGHT_HEADER, file=stream)
            write_weight_rows(cat, grand, stream)


def read_observations(path):
    rows = {}
    for line in Path(path).read_text().splitlines():
        first, second, forward, reverse = line.split()
        key = int(first), int(second)
        require(key not in rows and set(forward + reverse) <= {'0', '1'}, 'bad oracle result')
        rows[key] = (forward, reverse)
    return rows


def crosscheck(cats, sides, observations, receipts):
    expected = {}
    for ids, flags in observations.items():
        frames = tuple(sides[side][ids[side]] for side in range(2))
        for side, (source, target, text) in enumerate(zip(frames, frames[::-1], flags)):
            for assigned, flag in zip(source.assigned, text, strict=True):
                query = (cats[1 - side].order, *target.dest, tuple(sorted(assigned)))
                require(expected.setdefault(query, int(flag)) == int(flag), 'inconsistent literal query')
    with Path(receipts).open() as stream:
        require(stream.readline().split() == 'order host neutral group pass'.split(), 'C receipt header')
        seen = set()
        for order, host, neutral, demand, answer in map(str.split, stream):
            query = int(order), int(host), int(neutral), tuple(map(int, demand.split(',')))
            require(query not in seen and expected[query] == int(answer), 'C query receipt mismatch')
            seen.add(query)
    require(seen == expected.keys(), 'A/C query roster mismatch')
    print(f'Independent C receipts match all {len(seen)} small group predicates.')


def weights(catalogue, old_counts):
    grand, reproduced = Counter(), Counter()
    previous = None
    print(WEIGHT_HEADER)
    for line in sys.stdin:
        *identity, private, neutral = map(int, line.split())
        frame = catalogue.frame(identity)
        order_key = (frame.dest[0], *frame.marks)
        require(previous is None or previous < order_key, 'duplicate or unordered frame')
        if previous is not None and previous[0] != order_key[0]:
            write_weight_rows(catalogue, grand, sys.stdout)
            grand.clear()
        previous = order_key
        require(frame.local == (private, neutral), 'private or neutral degree misbound')
        profile = frame.profile
        grand[(*frame.local, *frame.dest, profile)] += 1
        shape = int(''.join(map(str, sorted(map(len, profile), reverse=True))))
        reproduced[frame.dest[0], private, neutral, shape, int(shape in (3332, 4333))] += 1
    ref = {}
    for host, private, neutral, shape, triple, total in map(
            lambda row: map(int, row.split()), Path(old_counts).read_text().splitlines()):
        if total:
            key = (host, private, neutral, shape, triple)
            require(key not in ref, 'duplicate round-16 count key')
            ref[key] = total
    require(reproduced == ref, 'full weighted profile projection disagrees with round 16')
    write_weight_rows(catalogue, grand, sys.stdout)


def read_weights(path, catalogue):
    with Path(path).open() as stream:
        require(stream.readline().rstrip('\n') == WEIGHT_HEADER, 'weight header mismatch')
        for order, private, degree, host, neutral, profile, count in csv.reader(stream, delimiter='\t'):
            local = int(private), int(degree)
            dest = int(host), int(neutral)
            weight = int(count)
            require(local == catalogue.margin[dest] and int(order) == catalogue.order and weight > 0,
                    'weight schema mismatch')
            yield local, dest, profile, weight


def mass(cats, weight_files, strata_file):
    margins, denominators, destinations, profiles, groups, visits = [], [], [], [], [], []
    for cat, path in zip(cats, weight_files):
        shape_counts, denominators_by_key = Counter(), Counter()
        buckets_by_key = Counter()
        dest_by_key, profiles_by_key, groups_by_key = (defaultdict(set) for _ in range(3))
        bucket_count, max_weight = 0, 0
        for local, dest, profile, weight in read_weights(path, cat):
            profile_groups = profile.split(';')
            if profile not in profiles_by_key[local]:
                profiles_by_key[local].add(profile)
                groups_by_key[local].update(profile_groups)
            dest_by_key[local].add(dest)
            shape = ''.join(map(str, sorted((group.count(',') + 1 for group in profile_groups), reverse=True)))
            shape_counts[local, shape] += weight
            denominators_by_key[local] += weight
            buckets_by_key[local] += 1
            bucket_count += 1
            max_weight = max(max_weight, weight)
        margins.append(shape_counts)
        denominators.append(denominators_by_key)
        destinations.append({local: len(items) for local, items in dest_by_key.items()})
        profiles.append({local: len(items) for local, items in profiles_by_key.items()})
        groups.append({local: len(items) for local, items in groups_by_key.items()})
        visits.append(buckets_by_key)
        count_profiles = len(set().union(*profiles_by_key.values()))
        print(f'order={cat.order} frames={shape_counts.total()} dests={sum(destinations[-1].values())} '
              f'profiles={count_profiles} joint_buckets={bucket_count} max_weight={max_weight}')
    shapes = []
    for (loc_left, shape_left), left_n in margins[0].items():
        for (loc_right, shape_right), right_n in margins[1].items():
            if complement(loc_left, 9, 1) == loc_right:
                shapes.append((*loc_left, shape_left, *loc_right, shape_right, left_n, right_n, left_n * right_n))
    with Path(strata_file).open() as stream:
        ref = [tuple(map(int, row)) for row in list(csv.reader(stream, delimiter='\t'))[1:]]
    require(sorted(tuple(map(int, row)) for row in shapes) == sorted(ref), 'shape-stratum mass changed')
    total = sum(row[-1] for row in shapes)
    require(len(shapes) == 34 and total == 15_051_526_031, 'total target mass changed')
    tally = Counter()
    subtotal_visits = 0
    print('D16 d16 dest16 dest17 profiles16 profiles17 groups16 groups17 pair_dests queries16to17 queries17to16 mass')
    for local, nleft in sorted(destinations[0].items()):
        other = complement(local, 9, 1)
        nright = destinations[1].get(other, 0)
        if not nright:
            continue
        group_left, group_right = groups[0][local], groups[1][other]
        counts = (nleft * nright, group_left * nright, group_right * nleft,
                  denominators[0][local] * denominators[1][other])
        tally.update(dict(enumerate(counts)))
        subtotal_visits += visits[0][local] * nright + visits[1][other] * nleft
        print(*local, nleft, nright, profiles[0][local], profiles[1][other], group_left, group_right, *counts)
    require(tally[3] == total, 'total from complementary keys disagrees')
    print(f'strata={len(shapes)} destination_pairs={tally[0]} unique_group_queries16to17={tally[1]} '
          f'unique_group_queries17to16={tally[2]} subtotal_bucket_visits_no_short_circuit={subtotal_visits} '
          f'target_mass={total} target_filter_not_run')


def pilot(cats, weight_files, cases_file, oracle_file, stats_file):
    obs = read_observations(oracle_file)
    with Path(stats_file).open() as stream:
        header = stream.readline().split()
        archive = {}
        for line in stream:
            row = dict(zip(header, line.split(), strict=True))
            archive[int(row['left']), int(row['right'])] = tuple(int(item) > 0 for item in row['before'].split(','))
    maps = ({}, {})
    counts = Counter()
    seen = set()
    needed = (set(), set())
    for row in map(str.split, Path(cases_file).read_text().splitlines()):
        first, second, *ends = map(int, row)
        ids = first, second
        require(ids not in seen and len(ends) == 12, 'bad pilot row')
        seen.add(ids)
        frames = tuple(cat.frame(ends[6 * side:6 * side + 6]) for side, cat in enumerate(cats))
        flags = []
        for side, (source, target, text) in enumerate(zip(frames, frames[::-1], obs[ids])):
            needed[side].add((source.local, source.dest, profile_text(source.profile)))
            require(len(text) == 4 and len(source.assigned) == 4, 'pilot lost singleton')
            require(tuple(bit == '1' for bit in text) == archive[ids][side::2], 'pilot disagrees with prior domains')
            for group, bit in zip(source.assigned, text):
                query = target.dest, tuple(sorted(group))
                require(maps[side].setdefault(query, bit == '1') == (bit == '1'), 'pilot cache collision')
            flags.append(all(maps[side][target.dest, group] for group in source.profile))
        counts[tuple(flags)] += 1
    require(seen == obs.keys() == archive.keys() and len(seen) == 544 and counts[True, True] == 47,
            'pilot coverage or intersection')
    for cat, path, required in zip(cats, weight_files, needed):
        for local, dest, profile, _ in read_weights(path, cat):
            required.discard((local, dest, profile))
        require(not required, 'pilot missing weight')
    print(f'pilot group keys={list(map(len, maps))} total={counts.total()} both_pass={counts[True, True]} '
          f'16to17_only={counts[True, False]} 17to16_only={counts[False, True]} neither_pass={counts[False, False]}')


def main(mode, *args):
    if mode in ('small', 'cross'):
        cat6, cat7, frames6, frames7, oracle, *plants = args
        cats = Catalogue(cat6, 5), Catalogue(cat7, 5)
        sides = [[cat.frame(row[:-2]) for row in read_frame_table(Path(file), cat.graphs)]
                 for cat, file in zip(cats, (frames6, frames7))]
        if mode == 'small':
            measure_small(*cats, *sides, read_observations(oracle), *plants)
        else:
            crosscheck(cats, sides, read_observations(oracle), *plants)
    elif mode == 'weights':
        cat_file, old = args
        weights(Catalogue(cat_file, 9), old)
    else:
        require(mode in ('mass', 'pilot'), 'unknown mode')
        cat16, cat17, weights16, weights17, *rest = args
        cats = Catalogue(cat16, 9), Catalogue(cat17, 9)
        sides = weights16, weights17
        if mode == 'mass':
            mass(cats, sides, *rest)
        else:
            pilot(cats, sides, *rest)


if __name__ == '__main__':
    main(*sys.argv[1:])
