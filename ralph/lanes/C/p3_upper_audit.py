"""Integer audit of witness coverage, without the production row builders."""

import argparse
from collections import Counter, defaultdict
from functools import reduce
from itertools import combinations, combinations_with_replacement
import json
from math import gcd, lcm
from pathlib import Path

from kernel_projection import bits
from p3_high_f import NO_HOLE, classify, filter_target, layouts


def independent(adj, mask):
    return all(not adj[vertex] & mask for vertex in bits(mask))


def blocks(adj, size):
    return [mask for vertices in combinations(range(len(adj)), size)
            if independent(adj, mask := sum(1 << vertex for vertex in vertices))]


def signature(mask, blockers):
    return sum(1 << index for index, block in enumerate(blockers) if not mask & block)


def forced_pairs(input_masks, signatures):
    return {(first, second) for first, second in combinations(range(len(input_masks)), 2)
            if signatures[input_masks[first]] & signatures[input_masks[second]]}


def compatible(input_masks, signatures):
    forced = forced_pairs(input_masks, signatures)
    return not any(input_masks[first] & input_masks[second] for first, second in forced) and len(forced) < 3


def groups(masks, zeros, signatures, common):
    forced = forced_pairs(zeros, signatures)
    result = defaultdict(list)
    for mask in masks:
        count = (mask & common).bit_count()
        if count == 0:
            continue
        joins = {slot for slot, zero in enumerate(zeros) if signatures[mask] & signatures[zero]}
        if any(mask & zeros[slot] for slot in joins) or any(first in joins and second in joins for first, second in forced):
            continue
        result[mask & ~common, count].append(mask)
    assert all(len(group) == (4 if key[1] in (1, 3) else 6 if key[1] == 2 else 1) for key, group in result.items())
    return result


def source_row(name, adj, masks, cache):
    if name in cache:
        return cache[name]
    kind, suffix = name.split(':')
    if kind == 'deg':
        column = int(suffix)
        selected = {mask for mask in masks if mask >> column & 1}
        base_cap = 9 - adj[column].bit_count()
    else:
        assert kind in ('tag', 'avoid')
        tag, block = map(int, suffix.split(',')) if kind == 'tag' else (None, int(suffix))
        size = block.bit_count()
        assert size in (6, 7, 8) and 0 <= block < 1 << len(adj) and independent(adj, block)
        selected = {mask for mask in masks if not mask & block}
        if kind == 'tag':
            assert 0 <= tag < len(adj) - 3 and not block >> tag & 1
            selected = {mask for mask in selected if mask >> tag & 1}
            base_cap = 9 - size
        else:
            base_cap = {6: 8, 7: 5, 8: 2}[size] if any(not left & right for left in selected for right in selected) else 9 - size
    cache[name] = selected, base_cap
    return selected, base_cap


def check(weights, adj, masks, zeros, orbits, cache):
    scale = weights['scale']
    assert type(scale) is int and scale > 0
    factor = lcm(*(len(masks) for masks in orbits.values()))
    marginals, numerator = Counter(), 0
    for name, weight in weights['weights'].items():
        assert type(weight) is int and weight > 0
        affected, cap = source_row(name, adj, masks, cache)
        full_cap = factor * (cap - sum(mask in affected for mask in zeros))
        vector = {key: (factor // len(group)) * sum(mask in affected for mask in group) for key, group in orbits.items()}
        divisor = reduce(gcd, vector.values(), abs(full_cap)) or 1
        numerator += weight * (full_cap // divisor)
        marginals.update({key: weight * (value // divisor) for key, value in vector.items()})
    assert all(marginals[key] >= scale for key in orbits if key[1] == 1), 'undercovers singleton orbit'
    return numerator, scale


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('new', type=Path)
    args = parser.parse_args()
    prior = json.loads(args.original.read_text())
    new = json.loads(args.new.read_text())
    counts = Counter()
    for size, key in layouts(9, 6, 4, 8, 16, 18):
        if NO_HOLE in key[1:]:
            continue
        adj = classify(9, 6, 4, key)
        if filter_target(adj) != 'pass':
            continue
        label = ':'.join(map(str, (key[0], *key[1], *key[2])))
        common = adj[-1] & adj[-2] & adj[-3]
        eight, nine = blocks(adj, 8), blocks(adj, 9)
        masks = [mask for mask in range(1 << (len(adj) - 3)) if mask.bit_count() in (3, 4, 5)
                 and independent(adj, mask) and all(mask & block for block in nine)
                 and all((mask & neighbours).bit_count() < 6 for neighbours in adj[-3:])]
        zero_types = [mask for mask in masks if not mask & common]
        signatures = {mask: signature(mask, eight) for mask in masks}
        assert all(not compatible(triple, signatures) for triple in combinations_with_replacement(zero_types, 3))
        cache = {}
        for q in range(3):
            for indices in combinations_with_replacement(range(len(zero_types)), q):
                zeros = [zero_types[index] for index in indices]
                if not compatible(zeros, signatures):
                    continue
                name = label + '/' + ','.join(map(str, indices))
                assert (name in prior) != (name in new)
                old = name in prior
                numerator, scale = check((prior if old else new).pop(name), adj, masks, zeros,
                                         groups(masks, zeros, signatures, common), cache)
                excess = numerator // scale - (20 - 2 * q)
                assert (old and excess < 0) or (not old and excess in (0, 1))
                counts['excluded' if old else 'excess_' + str(excess)] += 1
                print(45 + size, name, numerator, scale, excess)
    assert not prior and not new
    assert counts == {'excluded': 34, 'excess_0': 47, 'excess_1': 24}
    print('PASS: all 9 layouts have no compatible zero triple;', dict(counts))


if __name__ == '__main__':
    main()
