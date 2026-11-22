#!/usr/bin/env python3
import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

from panel16_audit import bits, graph6, hits_all, independent_masks, source_groups, union


def catalogue(path):
    return tuple(tuple(graph) for graph in graph6(Path(path)))


def integers(line):
    return tuple(map(int, line.split()))


def frame_profile(source, neutral, marks, degree):
    return tuple(tuple(2 * (degree - 1 - source[site].bit_count()) +
                       3 * bool(source[site] & (1 << neutral)) for site in group)
                 for group in source_groups(marks))


@lru_cache(maxsize=32000)
def predicate(target, neutral, demands, beta):
    options = [tuple(row for row in independent_masks(target, demand//2)
                     if bool(row & (1 << neutral)) == bool(demand % 2) and hits_all(target, row, beta))
               for demand in demands]
    options.sort(key=len)

    def extend(chosen):
        if len(chosen) == len(options):
            return True
        for row in options[len(chosen)]:
            if all(hits_all(target, row | union(previous), beta - count)
                   for count in range(1, len(chosen)+1) for previous in combinations(chosen, count)):
                if extend(chosen + (row,)):
                    return True
        return False

    return extend(())


def direct(source, destination, degree, beta):
    source_graph, source_neutral, source_marks = source
    dest_graph, dest_neutral, _ = destination
    return all(predicate(dest_graph, dest_neutral, demands, beta)
               for demands in frame_profile(source_graph, source_neutral, source_marks, degree))


def small_prepare(args):
    cats = [catalogue(path) for path in args.catalogues]
    raw = [[integers(line) for line in Path(path).open()] for path in args.frames]
    cells = Counter()
    decoded = []
    for side, records in enumerate(raw):
        side_frames = []
        for host, neutral, first, second, degree_sum, neutral_degree in records:
            graph = cats[side][host]
            assert degree_sum == sum(neighbors.bit_count() for site, neighbors in enumerate(graph) if site != neutral)
            assert neutral_degree == graph[neutral].bit_count()
            marks = first, second
            profile = sorted(tuple(sorted(group)) for group in frame_profile(graph, neutral, marks, 5))
            serial = ';'.join(','.join(map(str, group)) for group in profile)
            cells[len(graph), degree_sum, neutral_degree, host, neutral, serial] += 1
            side_frames.append((graph, neutral, marks))
        decoded.append(side_frames)
    with Path(args.weights).open('w') as stream:
        print('order D d host neutral profile count', file=stream)
        for key, mass in sorted(cells.items()):
            print(*key, mass, file=stream)
    with Path(args.cases).open('w') as cases, Path(args.literal).open('w') as literal:
        print('left right forward reverse both', file=literal)
        count = Counter()
        for (left_id, left), (right_id, right) in product(*map(enumerate, raw)):
            if right[4:] != (left[4] + 5, 5 - left[5]):
                continue
            forward = direct(decoded[0][left_id], decoded[1][right_id], 5, 4)
            reverse = direct(decoded[1][right_id], decoded[0][left_id], 5, 4)
            count[forward, reverse] += 1
            print(left_id, right_id, *left[:4], *right[:4], file=cases)
            print(left_id, right_id, int(forward), int(reverse), int(forward and reverse), file=literal)
    assert sum(count.values()) == 34504
    print('small literal', sorted(count.items()), 'cells', len(cells), predicate.cache_info())


def case_flags(path):
    result = {}
    for line in Path(path).open():
        if line[0].isdigit():
            left, right, forward, reverse, both = integers(line)
            assert (left, right) not in result and both == (forward and reverse)
            result[left, right] = forward, reverse
    return result


def small_check(args):
    literal = case_flags(args.literal)
    assert literal == case_flags(args.compressed)
    frame_records = [[integers(line) for line in Path(path).open()] for path in args.frames]
    counts = Counter()
    for (lid, rid), (forward, reverse) in literal.items():
        left, right = frame_records[0][lid], frame_records[1][rid]
        key = (*left[4:], *left[:2], *right[:2])
        counts[key, 'raw'] += 1
        counts[key, 'forward'] += forward
        counts[key, 'reverse'] += reverse
        counts[key, 'both'] += forward and reverse
    observed_keys = set()
    for line in Path(args.buckets).open():
        if line[0].isdigit():
            *fields, raw, forward, reverse, both = integers(line)
            key = tuple(fields)
            assert key not in observed_keys
            observed_keys.add(key)
            assert (raw, forward, reverse, both) == tuple(counts[key, name] for name in ('raw','forward','reverse','both'))
    assert observed_keys == {key for key, _ in counts}
    print('literal per-ID and weighted directional totals match on every host pair:', len(literal), len(observed_keys))


def pilot_check(args):
    cats = [catalogue(path) for path in args.catalogues]
    actual = case_flags(args.compressed)
    old = {}
    with Path(args.old_stats).open() as stream:
        header = next(stream).split()
        for line in stream:
            record = dict(zip(header, line.split()))
            domains = tuple(map(int, record['before'].split(',')))
            assert len(domains) == 8
            old[int(record['left']), int(record['right'])] = int(all(domains[::2])), int(all(domains[1::2]))
    assert actual == old
    checked = {}
    shapes = Counter()
    for line in Path(args.cases).open():
        left, right, *fields = integers(line)
        frames = []
        for side, cat in enumerate(cats):
            rim, neutral, *marks = fields[6*side:6*(side+1)]
            frames.append((cat[rim], neutral, tuple(marks)))
            for group in source_groups(marks):
                shapes[side, len(group)] += 1
        forward, reverse = direct(*frames, 9, 6), direct(*frames[::-1], 9, 6)
        assert (left, right) not in checked
        checked[left, right] = int(forward), int(reverse)
    assert actual == checked and len(checked) == 544
    assert sum(all(outcome) for outcome in checked.values()) == 47
    print('pilot matched both directions against all literal domains and independent hitting:', sorted(Counter(checked.values()).items()))
    print('pilot physical group occurrences by side, size:', sorted(shapes.items()))
    print('pilot independent cache:', predicate.cache_info())


def receipts_check(args):
    cats = {len(cat[0]): cat for path in args.catalogues if (cat := catalogue(path))}
    cnt = Counter()
    seen = set()
    with Path(args.receipts).open() as stream:
        assert next(stream).split() == ['order', 'host', 'neutral', 'group', 'pass']
        for line in stream:
            order, host, neutral, group, outcome = line.split()
            assert (order, host, neutral, group) not in seen
            seen.add((order, host, neutral, group))
            types = tuple(map(int, group.split(',')))
            target = cats[int(order)][int(host)]
            assert predicate(target, int(neutral), types, args.beta) == bool(int(outcome)), line
            cnt[len(types), int(outcome)] += 1
    assert cnt
    print('independent group receipts by size and outcome:', sorted(cnt.items()), 'total', sum(cnt.values()))


def target_arith(args):
    host_weights = Counter()
    for line in Path(args.weights).open():
        if line[0].isdigit():
            order, degree_sum, neutral_degree, host, neutral, _, mass = line.split()
            key = tuple(map(int, (order, degree_sum, neutral_degree, host, neutral)))
            host_weights[key] += int(mass)
    observed = Counter()
    prev_key = None
    with Path(args.buckets).open() as stream:
        assert next(stream).split() == ['D', 'd', 'left_host', 'left_neutral', 'right_host', 'right_neutral',
                                       'raw', 'forward', 'reverse', 'both']
        for line in stream:
            degree_sum, neutral_degree, left_host, left_z, right_host, right_z, raw, forward, reverse, both = integers(line)
            key = degree_sum, neutral_degree, left_host, left_z, right_host, right_z
            assert prev_key is None or prev_key < key
            prev_key = key
            left_weight = host_weights[(16, degree_sum, neutral_degree, left_host, left_z)]
            right_weight = host_weights[(17, degree_sum+9, 9-neutral_degree, right_host, right_z)]
            assert raw == left_weight * right_weight and raw > 0
            assert reverse % left_weight == forward % right_weight == 0
            assert 0 <= both <= min(forward, reverse) <= max(forward, reverse) <= raw
            assert both == (forward // right_weight) * (reverse // left_weight)
            for name, value in zip(('raw', 'forward', 'reverse', 'both', 'neither'),
                                   (raw, forward, reverse, both, raw-forward-reverse+both)):
                observed[key[:2], name] += value
    old_shapes = {}
    for line in Path(args.strata).open():
        if line[0].isdigit():
            degree_sum, neutral_degree, left, _, _, right, _, _, raw = line.split()
            key = int(degree_sum), int(neutral_degree), ''.join(sorted(left)), ''.join(sorted(right))
            assert key not in old_shapes
            old_shapes[key] = int(raw)
    expected = {}
    actual_shapes = {}
    pooled_shapes = Counter()
    names = ('raw', 'forward', 'reverse', 'both', 'neither')
    for line in Path(args.count).open():
        tag, *fields = line.split()
        if tag == 'stratum':
            key = tuple(map(int, fields[:2]))
            assert key not in expected
            expected[key] = tuple(map(int, fields[-5:]))
            assert expected[key] == tuple(observed[key, name] for name in names)
        if tag == 'shape':
            key = (*map(int, fields[:2]), *fields[2:4])
            assert key not in actual_shapes
            actual_shapes[key] = int(fields[4])
            for name, value in zip(names, map(int, fields[4:])):
                pooled_shapes[key[:2], name] += value
        if tag == 'total':
            summed = tuple(sum(counts[index] for counts in expected.values()) for index in range(len(names)))
            assert summed == tuple(map(int, fields[-5:]))
    assert actual_shapes == {key: raw for key, raw in old_shapes.items() if key[:2] in expected}
    assert observed == pooled_shapes
    print('independent host-pair arithmetic and raw shape binding:', len(expected), 'keys,', len(actual_shapes), 'shape strata')
    print('aggregate raw/forward/reverse/both/neither:', summed)


def forward_zero(args):
    cat = catalogue(args.dest_catalogue)
    profiles = Counter()
    rims = Counter()
    for line in Path(args.weights).open():
        if not line[0].isdigit():
            continue
        order, degree_sum, neutral_degree, host, neutral, text, mass = line.split()
        margin = int(degree_sum), int(neutral_degree)
        if order == '16' and margin == (args.degree_sum, args.neutral_degree):
            profile = tuple(tuple(map(int, group.split(','))) for group in text.split(';'))
            profiles[profile] += int(mass)
        if order == '17' and margin == (args.degree_sum+9, 9-args.neutral_degree):
            rims[int(host), int(neutral)] += int(mass)
    assert profiles and rims
    groups = sorted(set(group for profile in profiles for group in profile))
    checks, passes, raw = 0, 0, 0
    for (host, neutral), multiplicity in sorted(rims.items()):
        flags = {group: predicate(cat[host], neutral, group, 6) for group in groups}
        pass_weight = sum(mass for profile, mass in profiles.items() if all(flags[group] for group in profile))
        checks += len(flags)
        raw += multiplicity*sum(profiles.values())
        passes += multiplicity*pass_weight
        print('destination', host, neutral, 'source group types', len(flags), 'groups pass', sum(flags.values()),
              'source profiles', len(profiles), 'passing source frame weight', pass_weight)
    assert passes == 0
    print('full one-direction zero, independent hitting queries:', checks, 'raw labelled mass:', raw)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)
    part = sub.add_parser('small-prepare')
    part.add_argument('catalogues', nargs=2)
    part.add_argument('frames', nargs=2)
    part.add_argument('weights')
    part.add_argument('cases')
    part.add_argument('literal')
    part.set_defaults(run=small_prepare)
    part = sub.add_parser('small-check')
    part.add_argument('frames', nargs=2)
    part.add_argument('literal')
    part.add_argument('compressed')
    part.add_argument('buckets')
    part.set_defaults(run=small_check)
    part = sub.add_parser('pilot')
    part.add_argument('catalogues', nargs=2)
    part.add_argument('cases')
    part.add_argument('old_stats')
    part.add_argument('compressed')
    part.set_defaults(run=pilot_check)
    part = sub.add_parser('receipts')
    part.add_argument('catalogues', nargs=2)
    part.add_argument('receipts')
    part.add_argument('beta', type=int)
    part.set_defaults(run=receipts_check)
    part = sub.add_parser('target-arith')
    for field in ('weights', 'strata', 'count', 'buckets'):
        part.add_argument(field)
    part.set_defaults(run=target_arith)
    part = sub.add_parser('forward-zero')
    part.add_argument('weights')
    part.add_argument('dest_catalogue')
    part.add_argument('degree_sum', type=int)
    part.add_argument('neutral_degree', type=int)
    part.set_defaults(run=forward_zero)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
