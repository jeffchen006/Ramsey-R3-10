#!/usr/bin/env python3
import csv
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from pathlib import Path

from audit_direction_profiles import Catalogue, WEIGHT_HEADER, bits, complement, measure_small, read_observations
from one_neutral_control import require
from one_neutral_pilot import verify_sample


SLICES = {(67, 5): (1078, 30, 13690, 792, 46), (68, 4): (311, 91, 12968, 116, 24)}
PAST_SHAPE = {16: 3332, 17: 4333}
MARGINS = {16: set(SLICES), 17: {complement(local, 9, 1) for local in SLICES}}


def shape(profile):
    return ''.join(map(str, sorted(map(len, profile))))


def group_text(group):
    return ','.join(map(str, group))


@dataclass(frozen=True)
class Physical:
    number: int
    row: tuple
    info: object
    singletons: tuple

    @property
    def profile(self):
        return self.info.profile


def physical(number, row, catalogue):
    info = catalogue.frame(row[:-2])
    require(info.local == row[-2:], 'physical margins differ from graph')
    marks = row[2:-2]
    singletons = tuple(tuple(bits(mark & ~union(marks[:index] + marks[index+1:])))
                       for index, mark in enumerate(marks))
    require(tuple(map(len, singletons)) == tuple(map(len, info.assigned)), 'singleton position mismatch')
    return Physical(number, row, info, singletons)


def union(words):
    combined = 0
    for word in words:
        combined |= word
    return combined


def extract(catalogue, count_path):
    order = catalogue.order
    expected = {}
    for line in Path(count_path).open():
        host, private, degree, group_shape, _, count = map(int, line.split())
        if (private, degree) in MARGINS[order] and group_shape == PAST_SHAPE[order]:
            key = host, private, degree
            require(count > 0 and key not in expected, 'duplicate expected count')
            expected[key] = count
    retained = Counter()
    earlier = None
    total = 0
    for number, line in enumerate(sys.stdin.buffer):
        total = number + 1
        row = tuple(map(int, line.split()))
        host, _, *mark_fields, private, degree = row
        masks = tuple(mark_fields)
        ordinal_key = (host, masks)
        require(earlier is None or earlier < ordinal_key, 'physical frame order or duplication')
        earlier = ordinal_key
        key = host, private, degree
        if key not in expected:
            continue
        repeated = 0
        for index, mark in enumerate(masks):
            repeated |= mark & union(masks[:index])
        observed = ''.join(map(str, sorted(((mark & ~repeated).bit_count() for mark in masks), reverse=True)))
        if int(observed) != PAST_SHAPE[order]:
            continue
        verify_sample(row, catalogue.graphs[host], masks, union(masks), PAST_SHAPE[order])
        physical(number, row, catalogue)
        retained[key] += 1
        print(number, *row, sep='\t')
    require(total == {16: 2817701, 17: 59521}[order] and retained == expected, 'physical side census')
    print(f'order={order} global_stream={total} selected={retained.total()} host/margin_cells={len(retained)}',
          file=sys.stderr)


def load(path, catalogue, target):
    frames = []
    for index, line in enumerate(Path(path).open()):
        row = tuple(map(int, line.split()))
        number, row = (row[0], row[1:]) if target else (index, row)
        require(not frames or frames[-1].number < number, 'frame IDs unsorted')
        frames.append(physical(number, row, catalogue))
    require(len({frame.row for frame in frames}) == len(frames), 'repeated physical frame')
    return frames


def roster(frames):
    index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for frame in frames:
        index[frame.info.local][frame.info.dest][frame.profile].append(frame)
    return index


def check_weights(catalogue, path, index):
    observed = {}
    with Path(path).open() as stream:
        require(stream.readline().strip() == WEIGHT_HEADER, 'bad weight header')
        for line in stream:
            order, private, degree, host, neutral, profile, count = line.split()
            local = int(private), int(degree)
            if local not in MARGINS[catalogue.order]:
                continue
            demand = tuple(tuple(map(int, part.split(','))) for part in profile.split(';'))
            if shape(demand) != str(PAST_SHAPE[catalogue.order])[::-1]:
                continue
            cell = local, (int(host), int(neutral)), demand
            require(int(order) == catalogue.order and cell not in observed, 'weight identity')
            observed[cell] = int(count)
    expected = {(local, dest, profile): len(frames) for local, destinations in index.items()
                for dest, profiles in destinations.items() for profile, frames in profiles.items()}
    require(observed == expected, 'frozen order/host/neutral/profile/weight mismatch')
    print(f'weights{catalogue.order}: {len(expected)} exact cells, {sum(expected.values())} frames')


def bucket_pairs(indices, degree):
    for local, left in sorted(indices[0].items()):
        right = indices[1].get(complement(local, degree, 1), {})
        for (left_rim, left_cells), (right_rim, right_cells) in product(sorted(left.items()), sorted(right.items())):
            yield local, left_rim, right_rim, left_cells, right_cells


def query(order, rim, group):
    return (order, *rim, group_text(group))


def all_queries(indices, orders, degree):
    queries = set()
    for _, left_rim, right_rim, left, right in bucket_pairs(indices, degree):
        queries.update(query(orders[1], right_rim, group) for profile in left for group in profile)
        queries.update(query(orders[0], left_rim, group) for profile in right for group in profile)
    return queries


def load_queries(path, header=False):
    decisions = {}
    with Path(path).open() as stream:
        if header:
            require(stream.readline().split() == 'order host neutral group pass'.split(), 'bad receipt header')
        for line in stream:
            order, host, neutral, group, decision = line.split()
            key = int(order), int(host), int(neutral), group
            require(key not in decisions and decision in ('0', '1'), 'duplicate or malformed predicate receipt')
            decisions[key] = decision == '1'
    return decisions


def flags(frame, dest, dest_order, decisions):
    return ''.join(str(int(decisions[query(dest_order, dest, tuple(sorted(group)))]))
                   for group in frame.info.assigned)


def bind(indices, orders, degree, decisions):
    receipts, survivors = {}, {}
    for local, left_rim, right_rim, left, right in bucket_pairs(indices, degree):
        def subtotal(cells, dest, order):
            accepted = [frames for profile, frames in cells.items()
                        if all(decisions[query(order, dest, group)] for group in profile)]
            return [frame for frames in accepted for frame in frames]

        left_pass = subtotal(left, right_rim, orders[1])
        right_pass = subtotal(right, left_rim, orders[0])
        left_raw, right_raw = (sum(map(len, cells.values())) for cells in (left, right))
        key = (local, left_rim, right_rim)
        require(key not in receipts, 'duplicate bucket identity')
        receipts[key] = (left_raw * right_raw, len(left_pass) * right_raw,
                         left_raw * len(right_pass), len(left_pass) * len(right_pass))
        for first, second in product(left_pass, right_pass):
            ids = first.number, second.number
            require(ids not in survivors, 'physical header duplicated across cells')
            survivors[ids] = first, second
    return receipts, survivors


def literal(frames, orders, degree, decisions):
    receipts, result = defaultdict(Counter), {}
    for left, right in product(*frames):
        if complement(left.info.local, degree, 1) != right.info.local:
            continue
        ids = left.number, right.number
        require(ids not in result, 'duplicate literal header')
        forward = flags(left, right.info.dest, orders[1], decisions)
        reverse = flags(right, left.info.dest, orders[0], decisions)
        result[ids] = forward, reverse
        receipts[left.info.local, left.info.dest, right.info.dest]['0' not in forward, '0' not in reverse] += 1
    return {key: (counter.total(), counter[True, True] + counter[True, False],
                  counter[True, True] + counter[False, True], counter[True, True])
            for key, counter in receipts.items()}, result


def case(ids, left, right):
    return (*ids, *left.row[:-2], *right.row[:-2])


def bind_pilot(directory, raw, frames):
    selected, pilot_bits = {}, read_observations(directory / 'scratch/A/r17-stream/pilot.oracle.tsv')
    physical_by_id = tuple({frame.number: frame for frame in side} for side in frames)
    ranks = []
    for side in frames:
        seen = Counter()
        indices = {}
        for frame in side:
            indices[frame.number] = seen[frame.info.local]
            seen[frame.info.local] += 1
        ranks.append((indices, seen))
    bound_cases = {tuple(row[:2]): tuple(row) for line in (directory / 'scratch/C/r16/bound.cases.tsv').open()
                   for row in [list(map(int, line.split()))]}
    with (directory / 'scratch/A/r16/pilot.index.tsv').open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            ids = int(row['frame16']), int(row['frame17'])
            intended = ((int(row['D16']), int(row['d16'])) in SLICES and int(row['shape16']) == 3332
                        and int(row['shape17']) == 4333)
            require(intended == (ids in raw), 'pilot stratum inconsistent with physical intersection')
            if intended:
                first, second = (physical_by_id[side][ids[side]] for side in range(2))
                old_ranks = tuple(ranks[side][0][ids[side]] for side in range(2))
                total_right = ranks[1][1][second.info.local]
                ordinal = old_ranks[0] * total_right + old_ranks[1]
                require(old_ranks == (int(row['rank16']), int(row['rank17']))
                        and ordinal == int(row['bucket_ordinal']), 'old raw bucket ranks do not rebind')
                require(case(ids, first, second) == bound_cases[ids] and raw[ids] == pilot_bits[ids],
                        'old pilot ID, physical fields or predicate bits do not rebind')
                require(ids not in selected, 'duplicated pilot overlap')
                selected[ids] = (int(row['pilot_row']), ordinal)
    require(len(selected) == 32, 'expected all 16 pilot ranks in each raw slice')
    return selected


def check_small(directory, cats, frames, raw, survivors):
    expected = read_observations(directory / 'scratch/A/r17-stream/small.oracle.tsv')
    require(raw == expected, 'small predicate/group labels differ from all literal IDs')
    require(len(raw) == 34504 and len(survivors) == 31495, 'small control counts')
    print('small: all 34,504 literal IDs and ordered group bits agree; 31,495 both-pass')
    prior = directory / 'scratch/C/r16'
    measure_small(*cats, *(tuple(frame.info for frame in side) for side in frames), raw,
                  prior / 'controls.tsv', prior / 'control6.g6', prior / 'control7.g6')


def finish_target(directory, frames, buckets, raw, survivors):
    pilot = bind_pilot(directory, raw, frames)
    print(f'target: physical raw-pilot overlaps={len(pilot)}; both-pass-pilot overlaps={len(survivors.keys() & pilot.keys())}')
    totals = defaultdict(Counter)
    with Path('buckets.tsv').open('w') as sink:
        print('D16 d16 host16 neutral16 host17 neutral17 raw forward reverse both', file=sink)
        for (local, left_rim, right_rim), counts in sorted(buckets.items()):
            totals[local].update(dict(zip(('raw', 'forward', 'reverse', 'both'), counts)))
            print(*local, *left_rim, *right_rim, *counts, sep='\t', file=sink)
    left_by_id = {frame.number: frame for frame in frames[0]}
    with Path('pilot-overlap.tsv').open('w') as sink:
        print('D16 d16 frame16 frame17 pilot_row ordinal forward_groups reverse_groups both', file=sink)
        for ids, (pilot_row, ordinal) in sorted(pilot.items()):
            print(*left_by_id[ids[0]].info.local, *ids, pilot_row, ordinal, *raw[ids], int(ids in survivors),
                  sep='\t', file=sink)
    frozen = {}
    with (directory / 'scratch/C/r17/target.count.log').open() as stream:
        for fields in (line.split() for line in stream):
            if fields[0] != 'shape' or fields[3:5] != ['2333', '3334']:
                continue
            local = tuple(map(int, fields[1:3]))
            if local in SLICES:
                require(local not in frozen, 'duplicate frozen shape total')
                frozen[local] = tuple(map(int, fields[5:9]))
    for local, (left_count, right_count, forward, reverse, both) in SLICES.items():
        expected = dict(zip(('raw', 'forward', 'reverse', 'both'), (left_count * right_count, forward, reverse, both)))
        require(totals[local] == expected and tuple(expected.values()) == frozen[local],
                'weighted count differs from archived target shape result')
        count_left = sum(frame.info.local == local for frame in frames[0])
        count_right = sum(frame.info.local == complement(local, 9, 1) for frame in frames[1])
        require((count_left, count_right) == (left_count, right_count), 'target side count')
        overlap = [ids for ids in pilot if left_by_id[ids[0]].info.local == local]
        print(f'{local}: {left_count} x {right_count} = {totals[local]["raw"]} '
              f'forward={forward} reverse={reverse} both={both} pilot_raw={len(overlap)} '
              f'pilot_both={sum(ids in survivors for ids in overlap)}')
    with Path('survivors.cases.pending').open('w') as cases, Path('survivors.tsv').open('w') as sink:
        print('frame16 frame17 D16 d16 host16 neutral16 masks16 singleton16 host17 neutral17 masks17 '
              'singleton17 row_labels column_labels orientation prior_pilot_row', file=sink)
        for ids, (left, right) in sorted(survivors.items()):
            print(*case(ids, left, right), sep='\t', file=cases)
            print(*ids, *left.info.local,
                  *(field for frame in (left, right) for field in (
                      *frame.info.dest, group_text(frame.info.marks), ';'.join(map(group_text, frame.singletons)))),
                  group_text(site for site in range(16) if site != left.info.dest[1]),
                  group_text(site for site in range(17) if site != right.info.dest[1]),
                  '16private_rows__17private_cols', pilot.get(ids, ('-', '-'))[0], sep='\t', file=sink)
    Path('survivors.cases.pending').replace('survivors.cases.tsv')
    with Path('raw.cases.tsv').open('w') as cases, Path('raw.flags.tsv').open('w') as sink:
        bound = tuple({frame.number: frame for frame in side} for side in frames)
        for ids, (forward, reverse) in sorted(raw.items()):
            print(*case(ids, *(bound[side][ids[side]] for side in range(2))), sep='\t', file=cases)
            print(*ids, forward, reverse, sep='\t', file=sink)


def main(mode, *args):
    if mode == 'extract':
        catalogue, counts = args
        extract(Catalogue(catalogue, 9), counts)
        return
    phase, root, left_cat, right_cat, left_frames, right_frames, *weight_paths = args
    require(mode in ('target', 'small') and phase in ('queries', 'finish'), 'invalid mode')
    directory = Path(root)
    target = mode == 'target'
    orders, degree = ((16, 17), 9) if target else ((6, 7), 5)
    cats = tuple(Catalogue(path, degree) for path in (left_cat, right_cat))
    frames = tuple(load(path, cat, target) for path, cat in zip((left_frames, right_frames), cats))
    indices = tuple(map(roster, frames))
    queries = all_queries(indices, orders, degree)
    if phase == 'queries':
        for key in sorted(queries):
            print(*key, sep='\t')
        return
    decisions = load_queries('receipts.tsv')
    require(decisions.keys() == queries, 'not all requested group queries resolved')
    if target:
        for cat, path, index in zip(cats, weight_paths, indices, strict=True):
            check_weights(cat, path, index)
        archived = load_queries(directory / 'scratch/C/r17/target.groups.tsv', header=True)
        overlap = decisions.keys() & archived.keys()
        require(overlap and all(decisions[key] == archived[key] for key in overlap), 'archived target receipt differs')
        print(f'target: {len(overlap)} overlapping archived whole-roster group receipts agree')
    else:
        require(decisions == load_queries(directory / 'scratch/C/r17/small.groups.tsv', header=True), 'small C receipts differ')
    buckets, survivors = bind(indices, orders, degree, decisions)
    literal_buckets, raw = literal(frames, orders, degree, decisions)
    require(buckets == literal_buckets and survivors.keys() == {ids for ids, values in raw.items()
                                                               if not any('0' in bits for bits in values)},
            'literal frame pairs differ from per-bucket weight calculation')
    print(f'{mode}: {len(decisions)} exact group decisions; {len(buckets)} raw host-pair buckets match literal enumeration')
    if target:
        finish_target(directory, frames, buckets, raw, survivors)
    else:
        check_small(directory, cats, frames, raw, survivors)


if __name__ == '__main__':
    main(*sys.argv[1:])
