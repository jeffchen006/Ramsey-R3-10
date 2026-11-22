"""Find/replay upper witnesses for the excess above the singleton minimum."""

import argparse
from collections import Counter
import json
from pathlib import Path

from p3_high_f import NO_HOLE, classify, filter_target, layouts
from p3_singleton_cover import attachment_masks, bitset, capacity_rows, independent_levels, zero_compatibility
from p3_zero_conditioned import calibrate, condition, propose, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('discover', 'verify'))
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--original', type=Path, default=Path('../r8/zero-all.json'))
    args = parser.parse_args()
    calibrate()
    prior = json.loads(args.original.read_text())
    untested = {} if args.mode == 'discover' else json.loads(args.certificate.read_text())
    proposed = {}
    totals = Counter()
    for size, key in layouts(9, 6, 4, 8, 16, 18):
        if NO_HOLE in key[1:]:
            continue
        boundary = classify(9, 6, 4, key)
        if filter_target(boundary) != 'pass':
            continue
        label = ':'.join(map(str, (key[0], *key[1], *key[2])))
        levels = independent_levels(boundary)
        masks = attachment_masks(boundary, levels, 9, 3, 5, 5)
        common = bitset(range(6, 10))
        zeros, _, _, patterns = zero_compatibility(masks, common, levels[8], 22)
        base = capacity_rows(boundary, levels, masks, 9, 9, 6, 22, strong=True)
        for pattern in patterns:
            rows, groups = condition(masks, common, levels[8], base, [zeros[index] for index in pattern], 9, 22)
            name = label + '/' + ','.join(map(str, pattern))
            goal = [int(level == 1) for _, level in groups]
            floor = 20 - 2 * len(pattern)
            if name in prior:
                verify(rows, goal, floor, prior.pop(name))
                continue
            totals['open_patterns'] += 1
            if args.mode == 'discover':
                outcome, witness = propose(rows, goal, floor + 2)
                if witness is None:
                    print(name, 'unproved; LP discovery:', outcome, flush=True)
                    continue
                proposed[name] = witness
            elif name not in untested:
                continue
            else:
                witness = untested.pop(name)
            numerator, denominator = verify(rows, goal, floor + 2, witness)
            allowance = numerator // denominator - floor
            assert allowance in (0, 1)
            totals['excess_at_most_' + str(allowance)] += 1
            print('CHECKED', 45 + size, name, f'q={len(pattern)}', f'excess<={allowance}',
                  f'S<={numerator}/{denominator}', flush=True)
    assert not prior and not untested
    if args.mode == 'discover':
        args.certificate.write_text(json.dumps(proposed, sort_keys=True, indent=2) + '\n')
    print('TOTAL', args.mode, dict(totals))


if __name__ == '__main__':
    main()
