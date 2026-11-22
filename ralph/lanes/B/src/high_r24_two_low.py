"""Bind the small e49 degree-six/d7 cover with two low common rows."""

import argparse
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from high_r24_lift import find_rows, make_lift


def roster(plan, max_five, output):
    stems = defaultdict(list)
    max_five_stems = set(max_five.read_text().splitlines())
    for row in plan.read_text().splitlines():
        rank, edges, marks, stem = row.split('\t')
        if edges == '49':
            stems[stem].append((int(rank), marks))
    pairs = []
    overlaps = 0
    for stem, marks in stems.items():
        for (first_rank, first), (second_rank, second) in combinations(marks, 2):
            if set(first.split(',')) & set(second.split(',')):
                overlaps += 1
                continue
            pairs.append((first_rank, second_rank, first, second, stem, int(stem in max_five_stems)))
    with output.open('w') as target:
        for row in sorted(pairs):
            print(*row, sep='\t', file=target)
    print(f'e49 stems={len(stems)} disjoint_pairs={len(pairs)} overlapping_pairs={overlaps} '
          f'max5_successor={sum(row[-1] for row in pairs)}')


def build(row, output, depth):
    first_rank, second_rank, first, second, stem, _ = row.split('\t')
    first_mark = tuple(map(int, first.split(',')))
    second_mark = tuple(map(int, second.split(',')))
    assert first_mark in tuple(find_rows(stem)) and second_mark in tuple(find_rows(stem))
    assert not (set(first_mark) & set(second_mark))
    lift = make_lift(stem, first_mark, depth, normalized=True)
    second_sites = {site + 12 for site in second_mark}
    for site in lift.stem:
        edge = (4, site)
        if edge in lift.var:
            lift.clause(lift.var[edge] if site in second_sites else -lift.var[edge])
        else:
            assert site not in second_sites
    lift.degree(3, 8, 8)
    lift.formula.to_file(output)
    print(f'bound two-low ranks={first_rank}/{second_rank} depth={depth} clauses={len(lift.formula.clauses)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    inventory = subparsers.add_parser('roster')
    inventory.add_argument('plan', type=Path)
    inventory.add_argument('max_five', type=Path)
    inventory.add_argument('output', type=Path)
    binder = subparsers.add_parser('build')
    binder.add_argument('row', type=Path)
    binder.add_argument('output', type=Path)
    binder.add_argument('--depth', type=int, default=6)
    args = parser.parse_args()
    if args.command == 'roster':
        roster(args.plan, args.max_five, args.output)
    else:
        build(args.row.read_text().strip(), args.output, args.depth)


if __name__ == '__main__':
    main()
