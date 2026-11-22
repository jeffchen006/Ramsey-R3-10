"""Join common six-columns with their exact local witness-slack budgets."""

import argparse
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from time import process_time

from kernel_projection import bits, decode
from p3_common_cover import cases, four_cover
from p3_round4_index import census
from p3_singleton_cover import bitset, independent_levels
from p3_six_join import row_domains
from p3_tight_sat import raw_slack
from p3_zero_residue import placements


def local_cost(options, many_cap, single_weights, many_weight):
    states = {(0, 0): 0}
    for options_at_vertex in options:
        next_states = {}
        for (used, count), cost in states.items():
            for mask, extra, margin in options_at_vertex:
                if mask & used or count + extra > many_cap:
                    continue
                key = (mask | used, count + extra)
                value = cost + margin
                if key not in next_states or value < next_states[key]:
                    next_states[key] = value
        states = next_states
    return min((margin + sum(weight for index, weight in enumerate(single_weights) if not used >> index & 1)
                + many_weight * (many_cap - count) for (used, count), margin in states.items()), default=1000)


def control():
    from random import Random

    generator = Random(9043)
    feasible = impossible = 0
    for _ in range(120):
        options = [tuple((generator.randrange(16), generator.randrange(2), generator.randrange(3))
                         for _ in range(4)) for _ in range(generator.randrange(3, 7))]
        weights = (1, 1, 2, 2)
        expected = 1000
        for arrangement in product(*options):
            counts = [sum(mask >> position & 1 for mask, _, _ in arrangement) for position in range(4)]
            many = sum(extra for _, extra, _ in arrangement)
            if max(counts) <= 1 and many <= 3:
                expected = min(expected, 3 - many + sum(weight * (1 - count) for weight, count in zip(weights, counts))
                               + sum(margin for _, _, margin in arrangement))
        actual = local_cost(options, 3, weights, 1)
        assert expected == actual
        feasible += actual != 1000
        impossible += actual == 1000
    assert feasible > 0 and impossible > 0
    print('tag DP direct check', feasible, 'finite,', impossible, 'impossible')


def tag_instances(caps, common, witness):
    representative = next(bits(common))
    single = [(block, weight) for block, (cap, weight) in caps.items() if cap == 1 and not block >> representative & 1]
    [(many, (many_cap, many_weight))] = [(block, (cap, weight)) for block, (cap, weight) in caps.items()
                                        if cap != 1 and not block >> representative & 1]
    degree = [(1 << int(name.split(':')[1]), weight) for name, weight in witness['weights'].items()
              if name.startswith('deg:')]
    return representative, single, many, many_cap, many_weight, degree


def placement(core, allowed, common, caps, witness, budget, target, six):
    representative, single, many, many_cap, many_weight, degree = tag_instances(caps, common, witness)
    scale = witness['scale']
    must_double = forbid_double = 0
    singles = [()] * len(core)
    doubles = [1000] * len(core)
    for vertex in bits(target):
        options = set()
        for mask in allowed[vertex]:
            count = (mask & common).bit_count()
            if count not in (1, 2):
                continue
            degree_score = sum(weight for column, weight in degree if mask & column)
            if count == 2:
                doubles[vertex] = min(doubles[vertex], degree_score)
                continue
            if not mask >> representative & 1:
                continue
            missed = bitset(index for index, (block, _) in enumerate(single) if not block & mask)
            extra = int(not many & mask)
            margin = degree_score + sum(weight for index, (_, weight) in enumerate(single) if missed >> index & 1)
            margin += extra * many_weight - scale
            assert margin >= 0
            options.add((missed, extra, margin))
        singles[vertex] = tuple(sorted(options))
        if not options and doubles[vertex] == 1000:
            return Counter()
        if not options:
            must_double |= 1 << vertex
        if doubles[vertex] == 1000:
            forbid_double |= 1 << vertex
    single_weights = tuple(weight for _, weight in single)

    @lru_cache(None)
    def cost(options):
        return local_cost(options, many_cap, single_weights, many_weight)

    @lru_cache(None)
    def for_tag(vertices):
        return cost(tuple(sorted(singles[vertex] for vertex in bits(vertices))))

    @lru_cache(None)
    def for_double(vertices):
        return sum(doubles[vertex] for vertex in bits(vertices))

    counts = Counter()
    for columns, doubled in four_cover(six, target, must_double, forbid_double, True):
        counts['covers'] += 1
        lower = for_double(doubled)
        for column in columns:
            if lower > budget:
                break
            lower += for_tag(column & ~doubled)
        if lower <= budget:
            counts['after_slack'] += 1
    counts['tag_contexts'] = for_tag.cache_info().currsize
    counts['tag_dp'] = cost.cache_info().currsize
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'scout', 'heldout', 'all'))
    parser.add_argument('output', nargs='?', type=Path)
    parser.add_argument('--layout', default='1:0:1:1:1', choices=('1:0:1:1:1', '3:0:1:2:1'))
    args = parser.parse_args()
    control()
    if args.mode == 'control':
        return
    original = json.loads(Path('../r8/zero-all.json').read_text())
    witness = json.loads(Path('rounded.json').read_text())[args.layout + '/0']
    label, edges, boundary, blockers, masks, common, pattern, chosen, rows, goal = next(cases(original, args.layout))
    caps, budget, margins = raw_slack(independent_levels(boundary), common, chosen[0], masks,
                                      boundary, rows, goal, witness)
    print('Raw checked layout', label, 'pattern', pattern, 'budget', budget, 'margins', dict(margins), flush=True)
    path = Path('../../../gluing/val/r3_7_22.g6')
    cores = path.read_bytes().splitlines()
    totals = Counter()
    start = process_time()
    counts_by_row = {int(fields[3]): int(fields[-1])
                     for line in Path('../r8/zero-residue-bindings.tsv').read_text().splitlines()[1:]
                     if (fields := line.split('\t'))[2] == label}
    with args.output.open('w') as stream:
        stream.write('layout\trow\tdigest\tzero\tbase_covers\tafter_slack\ttag_contexts\tdistinct_tag_dp\n')
        for number, (row, digest) in enumerate((row, digest) for row, (edge_count, digest) in census(path).items()
                                               if edge_count == edges):
            if args.mode == 'scout' and number % 5 or args.mode == 'heldout' and number % 5 == 0:
                continue
            assert sha256(cores[row]).hexdigest() == digest
            core = decode(cores[row].decode())
            six = independent_levels(core)[6]
            summary = Counter()
            for (zero,) in placements(core, chosen, blockers, 9, 6):
                domains = row_domains(core, masks, common, blockers, chosen, (zero,), 9, 6)
                target = ((1 << len(core)) - 1) ^ (1 << zero)
                counts = placement(core, domains, common, caps, witness, budget, target, six)
                stream.write('\t'.join(map(str, (label, row, digest, zero, counts['covers'], counts['after_slack'],
                                                   counts['tag_contexts'], counts['tag_dp']))) + '\n')
                summary.update(counts)
                summary.update(placements=1, passing=bool(counts['after_slack']))
            assert summary['placements'] == counts_by_row[row]
            totals.update(summary)
            totals.update(rows=1, surviving_rows=bool(summary['passing']))
            print('ROW', row, dict(summary), 'CPU-s', round(process_time()-start, 3), flush=True)
    print('TOTAL', args.mode, dict(totals), 'CPU-s', round(process_time()-start, 3))


if __name__ == '__main__':
    main()
