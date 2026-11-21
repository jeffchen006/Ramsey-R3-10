"""Exact necessary package counts for a nonedge with K2,2 exclusive neighbours."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from kernel_projection import bits, decode, independent_masks


def restrict(adj, vertices):
    return [sum(1 << index for index, other in enumerate(vertices) if adj[vertex] >> other & 1)
            for vertex in vertices]


def count_packages(adj, degree, cap, planted=(), output=None, stride=1):
    full = (1 << len(adj)) - 1
    deficits = [degree - neighbors.bit_count() for neighbors in adj]
    if min(deficits) < 1:
        assert not planted
        return {'bad-deficit': 1}
    lab_size = degree - 3
    cannot_double = sum(1 << vertex for vertex, deficit in enumerate(deficits) if deficit <= 2)
    cannot_touch = sum(1 << vertex for vertex, deficit in enumerate(deficits) if deficit <= 1)
    indeps = list(independent_masks(adj, full))
    if any(mask.bit_count() > degree - 2 for mask in indeps):
        assert not planted
        return {'bad-independence': 1}
    largest = [mask for mask in indeps if mask.bit_count() == degree - 2]
    todo = (1 << len(largest)) - 1
    masks = [mask for mask in indeps if mask.bit_count() == lab_size and not mask & cannot_touch]
    options = []
    for mask in masks:
        need = full ^ mask
        for vertex in bits(mask):
            need &= ~adj[vertex]
        covered = sum(1 << i for i, indep in enumerate(largest) if indep & mask)
        options.append((mask, need, covered))
    packages = []
    for i, (left, needs_left, covers_left) in enumerate(options):
        for j in range(i, len(options)):
            right, needs_right, covers_right = options[j]
            overlap = left & right
            if overlap & cannot_double or overlap.bit_count() > cap - 3:
                continue
            if covers_left | covers_right != todo:
                continue
            union = left | right
            need = needs_left | needs_right
            if need & union:
                continue
            packages.append((union, need, overlap, left, right))

    by_union = [bytearray((len(packages) + 7) // 8) for _ in adj]
    by_need = [bytearray((len(packages) + 7) // 8) for _ in adj]
    lookup = {}
    for index, (union, need, _, left, right) in enumerate(packages):
        if planted:
            lookup[tuple(sorted((left, right)))] = index
        for vertex in bits(union):
            by_union[vertex][index >> 3] |= 1 << (index & 7)
        for vertex in bits(need):
            by_need[vertex][index >> 3] |= 1 << (index & 7)
    in_union = [int.from_bytes(arr, 'little') for arr in by_union]
    in_need = [int.from_bytes(arr, 'little') for arr in by_need]
    all_packages = (1 << len(packages)) - 1
    support = 0
    pairs = 0
    emitted = 0
    witnesses = {lookup[tuple(sorted(pair))] for pair in planted}
    seen = set()
    for index, (union, need, _, left, right) in enumerate(packages):
        compatible = all_packages
        for vertex in bits(need):
            compatible &= in_union[vertex]
            if not compatible:
                break
        if not compatible:
            continue
        for vertex in bits(union):
            compatible &= ~in_union[vertex]
        for vertex in bits(full ^ union):
            compatible &= ~in_need[vertex]
        if not compatible:
            continue
        support += 1
        pairs += compatible.bit_count()
        if output is not None:
            after = compatible >> (index + 1) << (index + 1)
            for partner in bits(after):
                if emitted % stride == 0:
                    _, _, _, other_left, other_right = packages[partner]
                    print(left, right, other_left, other_right, file=output)
                emitted += 1
        if index in witnesses:
            partners = witnesses - {index}
            assert len(partners) == 1 and compatible >> next(iter(partners)) & 1
            seen.add(index)
    if planted:
        for pair in planted:
            assert tuple(sorted(pair)) in lookup
        assert len(witnesses) == 2 and witnesses == seen
    assert pairs % 2 == 0
    if output is not None:
        assert emitted == pairs // 2
    return {'I_max': len(largest), 'masks': len(masks), 'packages': len(packages),
            'support': support, 'pairs': pairs // 2}


def calibration(path, outdir=None, all_out=False):
    tally = Counter()
    for line in Path(path).read_text().splitlines():
        adj = decode(line)
        degree = adj[0].bit_count()
        assert all(mask.bit_count() == degree for mask in adj)
        cap = max((adj[left] & adj[right]).bit_count() for left, right in combinations(range(len(adj)), 2))
        for left, right in combinations(range(len(adj)), 2):
            common = adj[left] & adj[right]
            if common.bit_count() != degree - 2:
                continue
            side_a = adj[left] ^ common
            side_b = adj[right] ^ common
            if not all(adj[vertex] & side_b == side_b for vertex in bits(side_a)):
                continue
            outside = list(bits(((1 << len(adj)) - 1) & ~(adj[left] | adj[right] | (1 << left) | (1 << right))))
            masks = [tuple(sum(1 << i for i, y in enumerate(outside) if adj[z] >> y & 1) for z in bits(side))
                     for side in (side_a, side_b)]
            reduced = restrict(adj, outside)
            if outdir is not None:
                with (Path(outdir) / f'cal_pair{tally["pairs-tested"]}.txt').open('w') as output:
                    print(degree, cap, len(reduced), file=output)
                    print(*reduced, file=output)
                    if all_out:
                        result = count_packages(reduced, degree, cap, planted=masks, output=output)
                    else:
                        print(*masks[0], *masks[1], file=output)
                        result = count_packages(reduced, degree, cap, planted=masks)
            else:
                result = count_packages(reduced, degree, cap, planted=masks)
            assert result['pairs'] > 0
            tally['graphs-with-pair'] += (tally.get(line, 0) == 0)
            tally[line] += 1
            tally['pairs-tested'] += 1
    assert tally['pairs-tested'] > 0
    print('calibration', {name: tally[name] for name in ('graphs-with-pair', 'pairs-tested')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('scan', 'calibrate'))
    parser.add_argument('file')
    parser.add_argument('--index', type=int)
    parser.add_argument('--out')
    parser.add_argument('--stride', type=int, default=1)
    parser.add_argument('--all-out', action='store_true')
    args = parser.parse_args()
    if args.stride <= 0:
        parser.error('--stride must be positive')
    if args.mode == 'calibrate':
        calibration(args.file, args.out, args.all_out)
        return
    for index, line in enumerate(Path(args.file).read_text().splitlines()):
        if args.index is not None and args.index != index:
            continue
        adj = decode(line)
        if args.out:
            with Path(f'{args.out}.{index}.txt').open('w') as output:
                print(9, 7, len(adj), file=output)
                print(*adj, file=output)
                result = count_packages(adj, 9, 7, output=output, stride=args.stride)
        else:
            result = count_packages(adj, 9, 7)
        print(index, result, flush=True)


if __name__ == '__main__':
    main()
