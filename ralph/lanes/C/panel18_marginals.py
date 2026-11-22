#!/usr/bin/env python3
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations_with_replacement, product
from pathlib import Path

from panel16_audit import hits_columns, independent_masks, union
from panel17_audit import predicate as literal_predicate
from panel18_bind import SLICES, read_integer_rows
from verify_panel17 import bits, graph6


@lru_cache(maxsize=32768)
def options(graph, neutral, demand, beta):
    columns = tuple(hits_columns(graph, beta-depth) for depth in range(4))
    allowed = []
    for row in independent_masks(graph, demand//2):
        if bool(row & (1 << neutral)) != bool(demand % 2):
            continue
        sites = tuple(bits(row))
        masks = tuple(full ^ union(entries[site] for site in sites) for entries, full in columns)
        if not masks[0]:
            allowed.append(masks[1:])
    return tuple(allowed)


@lru_cache(maxsize=32768)
def predicate(graph, neutral, group, beta):
    rows = sorted((options(graph, neutral, demand, beta) for demand in group), key=len)
    if not rows[0]:
        return False
    if len(rows) == 2:
        return any(not (first[0] & second[0]) for first in rows[0] for second in rows[1])
    for first in rows[0]:
        second_support = tuple(second for second in rows[1] if not (first[0] & second[0]))
        third_support = tuple(third for third in rows[2] if not (first[0] & third[0]))
        if len(rows) == 4:
            fourth_support = tuple(fourth for fourth in rows[3] if not (first[0] & fourth[0]))
            if not fourth_support:
                continue
        for second in second_support:
            first_second = first[1] & second[1]
            for third in third_support:
                if second[0] & third[0] or first_second & third[1]:
                    continue
                if len(rows) == 3:
                    return True
                first_third = first[1] & third[1]
                second_third = second[1] & third[1]
                first_second_third = first[2] & second[2] & third[2]
                if any(not (second[0] & fourth[0] or third[0] & fourth[0]
                            or (first_second | first_third | second_third) & fourth[1]
                            or first_second_third & fourth[2]) for fourth in fourth_support):
                    return True
    return False


def scoped_weights(path, catalogue, order, shapes):
    resolved = defaultdict(lambda: defaultdict(dict))
    with path.open() as stream:
        assert next(stream).split() == ['order', 'D', 'd', 'host', 'neutral', 'profile', 'count']
        for line in stream:
            raw_order, total, degree, host, neutral, profile, count = line.split()
            target = int(total), int(degree)
            if target not in shapes:
                continue
            shape = ''.join(sorted(str(group.count(',')+1) for group in profile.split(';')))
            if shapes[target] is not None and shape != shapes[target]:
                continue
            host_index, neutral_index, multiplicity = map(int, (host, neutral, count))
            assert 0 <= host_index < len(catalogue) and 0 <= neutral_index < order
            graph = catalogue[host_index]
            assert int(raw_order) == len(graph) == order and multiplicity > 0
            assert graph[neutral_index].bit_count() == target[1]
            assert sum(row.bit_count() for row in graph)-target[1] == target[0]
            groups = tuple(tuple(map(int, group.split(','))) for group in profile.split(';'))
            assert all(tuple(sorted(group)) == group for group in groups) and tuple(sorted(groups)) == groups
            bucket = resolved[target][host_index, neutral_index]
            assert groups not in bucket
            bucket[groups] = multiplicity
    return resolved


def audit_products(small, large, catalogues, beta):
    buckets = {}
    receipts = {}
    for degree_key, pair in sorted(small.items()):
        for smaller, larger in product(sorted(pair), sorted(large[degree_key])):
            by_side = pair[smaller], large[degree_key][larger]
            totals = tuple(sum(profiles.values()) for profiles in by_side)
            allowed = []
            for side, dest in enumerate((larger, smaller)):
                host, neutral = dest
                graph = catalogues[1-side][host]
                count = 0
                decisions = {}
                for profile, multiplicity in by_side[side].items():
                    for group in profile:
                        if group not in decisions:
                            decisions[group] = predicate(graph, neutral, group, beta)
                            receipts[len(graph), host, neutral, group] = decisions[group]
                    if all(decisions[group] for group in profile):
                        count += multiplicity
                allowed.append(count)
            buckets[degree_key + smaller + larger] = (
                totals[0]*totals[1], allowed[0]*totals[1], totals[0]*allowed[1], allowed[0]*allowed[1])
    return buckets, receipts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('control', 'target'))
    parser.add_argument('catalogues', nargs=2, type=Path)
    parser.add_argument('weights', nargs=2, type=Path)
    parser.add_argument('reference', type=Path)
    parser.add_argument('buckets', type=Path)
    parser.add_argument('--receipts', type=Path)
    args = parser.parse_args()
    catalogues = tuple(tuple(map(tuple, graph6(path))) for path in args.catalogues)
    if args.mode == 'control':
        orders, degree, beta = (6, 7), 5, 4
        reference = {}
        shapes = ({}, {})
        with args.reference.open() as stream:
            assert next(stream).split() == ['D','d','left_host','left_neutral','right_host','right_neutral',
                                           'raw','forward','reverse','both']
            for line in stream:
                row = tuple(map(int, line.split()))
                reference[row[:6]] = row[6:]
                total, neutral = row[:2]
                shapes[0][total, neutral] = None
                shapes[1][total+degree,degree-neutral] = None
    else:
        orders, degree, beta = (16, 17), 9, 6
        shapes = ({(total, neutral): left for total, neutral, left, _ in SLICES},
                  {(total+degree, degree-neutral): right for total, neutral, _, right in SLICES})
    left, right = (scoped_weights(path, catalogue, order, side_shapes) for path, catalogue, order, side_shapes
                   in zip(args.weights, catalogues, orders, shapes, strict=True))
    right = {(total-degree,degree-neutral): bucket for (total,neutral),bucket in right.items()}
    assert left.keys() == right.keys() == shapes[0].keys()
    buckets, receipts = audit_products(left, right, catalogues, beta)
    if args.receipts is not None:
        expected_receipts = {}
        with args.receipts.open() as stream:
            for line in stream:
                order, host, neutral, group, flag = line.split()
                key = int(order), int(host), int(neutral), tuple(map(int, group.split(',')))
                assert flag in ('0', '1') and key not in expected_receipts
                expected_receipts[key] = flag == '1'
        assert receipts == expected_receipts
    if args.mode == 'control':
        assert buckets == reference and len(buckets) == 29220
        print('all 29220 small host-pair products and 34504 raw headers matched')
        four_rows = Counter()
        for host in (0, 6, 7):
            for demanded in combinations_with_replacement((2, 4, 5, 6, 7, 8, 9, 10, 11), 4):
                graph = catalogues[1][host]
                outcome = literal_predicate(graph, host % 7, demanded, beta)
                assert outcome == predicate(graph, host % 7, demanded, beta)
                four_rows[outcome] += 1
        assert four_rows == {False: 1462, True: 23}
        print('four-row literal controls: 1485 demands, 23 true and 1462 false')
    else:
        checks = Counter()
        for row in read_integer_rows(args.reference, 14):
            left_host, left_neutral, right_host, right_neutral = row[2:4]+row[8:10]
            total = sum(adj.bit_count() for adj in catalogues[0][left_host])-catalogues[0][left_host][left_neutral].bit_count()
            neutral = catalogues[0][left_host][left_neutral].bit_count()
            host_pair = total, neutral, left_host, left_neutral, right_host, right_neutral
            checks[host_pair] += 1
        assert checks == {key: value[3] for key, value in buckets.items() if value[3]}
        for key, expected in sorted(SLICES.items()):
            cohort = [value for host_pair, value in buckets.items() if host_pair[:2] == key[:2]]
            observed = tuple(sum(field) for field in zip(*cohort))
            assert observed == expected
            print(*key, *observed, 'host_pairs', len(cohort), 'both_positive_host_pairs', sum(row[3] > 0 for row in cohort))
    with args.buckets.open('w') as stream:
        print('D d left_host left_neutral right_host right_neutral raw forward reverse both', file=stream)
        for key, row in sorted(buckets.items()):
            print(*key, *row, file=stream)
    print('independently tested distinct labelled hitting predicates', len(receipts))


if __name__ == '__main__':
    main()
