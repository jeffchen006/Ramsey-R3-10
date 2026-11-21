"""Necessary cyclic join of the eight overlapping order-22 residual windows."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import subprocess
import time

from kernel_projection import bits, decode


def labelled_maps(left_graph, right_graph):
    order = len(left_graph)
    combined = left_graph + [mask << order for mask in right_graph]
    colours = [0] * (order * 2)
    while True:
        sign = [(colours[index], tuple(sorted(colours[vertex] for vertex in bits(mask))))
                for index, mask in enumerate(combined)]
        numbering = {key: number for number, key in enumerate(sorted(set(sign)))}
        revised = [numbering[key] for key in sign]
        if revised == colours:
            break
        colours = revised
    full = (1 << order) - 1
    candidates = [sum(1 << vertex for vertex in range(order) if colours[index] == colours[vertex+order])
                  for index in range(order)]
    mapping = [-1] * order

    def visit(todo, assigned):
        if not todo:
            yield tuple(mapping)
            return
        smallest = order + 1
        selected = -1
        domain = 0
        for index in bits(todo):
            options = candidates[index] & ~assigned
            for done in bits(full ^ todo):
                related = right_graph[mapping[done]]
                options &= related if left_graph[index] >> done & 1 else ~related
            count = options.bit_count()
            if count == 0:
                return
            if count < smallest:
                smallest, selected, domain = count, index, options
        for target in bits(domain):
            mapping[selected] = target
            yield from visit(todo ^ (1 << selected), assigned | (1 << target))

    yield from visit(full, 0)


def three_types(six_masks):
    choices = (1, 2, 3, 4, 5)
    for j in choices:
        remaining = tuple(value for value in choices if value != j)
        for k in remaining[1:]:
            last = tuple(value for value in remaining[1:] if value != k)
            pairs = [(0, j), (remaining[0], k), last]
            types = tuple(tuple(sorted((six_masks[left], six_masks[right]))) for left, right in pairs)
            if any((first & second).bit_count() > 3 for first, second in types):
                continue
            for ordered in set(permutations(types)):
                if any((left & right).bit_count() > 4
                       for a, b in ((0, 1), (1, 2)) for left in ordered[a] for right in ordered[b]):
                    continue
                if any((left & right).bit_count() > 5 for left in ordered[0] for right in ordered[2]):
                    continue
                yield ordered


def cycle_join(allowed, total, cycle_size, emit_limit=None):
    before = defaultdict(set)
    after = defaultdict(set)
    load = {}
    for first, second, third in allowed:
        before[second, third].add(first)
        after[first, second].add(third)
        for group in (first, second, third):
            if group not in load:
                load[group] = tuple(vertex for mask in group for vertex in bits(mask))
    nodes = 0
    results = []
    for initial_first, initial_second in sorted(set(after) & set(before)):
        if emit_limit is not None and len(results) >= emit_limit:
            break
        selected = []
        remain = list(total)

        def apply(group, value):
            valid = True
            for vertex in load[group]:
                remain[vertex] += value
                if remain[vertex] < 0:
                    valid = False
            return valid

        def visit():
            nonlocal nodes
            nodes += 1
            first, second = selected[-2:]
            if len(selected) == cycle_size:
                if any(remain):
                    return
                if initial_first in after.get((first, second), ()) and initial_second in after.get((second, initial_first), ()):
                    results.append(tuple(selected))
                return
            for third in sorted(after.get((first, second), ())):
                if emit_limit is not None and len(results) >= emit_limit:
                    break
                valid = apply(third, -1)
                if valid:
                    selected.append(third)
                    visit()
                    selected.pop()
                apply(third, 1)

        first_ok = apply(initial_first, -1)
        second_ok = apply(initial_second, -1)
        if first_ok and second_ok:
            selected.extend((initial_first, initial_second))
            visit()
    return results, nodes


def meet_join(allowed, total):
    tails = defaultdict(set)
    for first, second, third in allowed:
        tails[first, second].add(third)
    target = sum(need << (5 * vertex) for vertex, need in enumerate(total))
    type_load = {group: sum(1 << (5 * vertex) for mask in group for vertex in bits(mask))
                 for triple in allowed for group in triple}
    by_score = defaultdict(list)
    words = 0
    for first, second, third in allowed:
        for fourth in tails.get((second, third), ()):
            score = sum(type_load[group] for group in (first, second, third, fourth))
            by_score[score].append((first, second, third, fourth))
            words += 1
    candidates = 0
    for score, first_half in by_score.items():
        second_half = by_score.get(target - score, ())
        candidates += len(first_half) * len(second_half)
        for one, two, three, four in first_half:
            for five, six, seven, eight in second_half:
                if (five in tails.get((three, four), ()) and six in tails.get((four, five), ()) and
                    one in tails.get((seven, eight), ()) and two in tails.get((eight, one), ())):
                    return True, words, candidates, set(by_score)
    return False, words, candidates, set(by_score)


def sparse_obstruction(scores, total):
    target = sum(need << (5 * vertex) for vertex, need in enumerate(total))
    kept = list(range(len(total)))

    def separates(vertices):
        select = sum(31 << (5 * vertex) for vertex in vertices)
        cut_scores = {score & select for score in scores}
        cut_target = target & select
        return not any(cut_target - score in cut_scores for score in cut_scores)

    if not separates(kept):
        return None
    for vertex in tuple(kept):
        others = [index for index in kept if index != vertex]
        if separates(others):
            kept = others
    return kept


def check_obstruction(allowed, total, vertices):
    if sorted(set(vertices)) != vertices or any(not 0 <= index < len(total) for index in vertices):
        raise ValueError('invalid vertex projection')
    starters = defaultdict(list)
    for first, second, third in allowed:
        starters[first, second].append(third)
    scores = set()
    for first, second, third in allowed:
        for last in starters.get((second, third), ()):
            word = (first, second, third, last)
            scores.add(tuple(sum((mask >> vertex) & 1 for group in word for mask in group) for vertex in vertices))
    for score in scores:
        dual = tuple(total[vertex] - amount for vertex, amount in zip(vertices, score))
        if dual in scores:
            raise ValueError(f'complementary load profiles at {vertices}')
    return len(scores)


def calibrate():
    cycle = [(1 << ((index + 1) % 6)) | (1 << ((index - 1) % 6)) for index in range(6)]
    assert len(set(labelled_maps(cycle, cycle))) == 12
    source = random.Random(3010)
    types = ((0, 1), (1, 2), (2, 3))
    hits = count = 0
    for cycle_size in (4, 5, 8):
        for _ in range(10):
            planted = source.choices(types, k=cycle_size)
            total = [sum(mask >> bit & 1 for group in planted for mask in group) for bit in range(2)]
            allowed = {triple for triple in product(types, repeat=3) if source.randrange(3) == 0}
            if count % 2 == 0:
                allowed |= {tuple(planted[(index + off) % cycle_size] for off in range(3))
                            for index in range(cycle_size)}
            expected = set()
            for candidate in product(types, repeat=cycle_size):
                degrees = [sum(mask >> bit & 1 for group in candidate for mask in group) for bit in range(2)]
                if degrees == total and all(tuple(candidate[(index+off) % cycle_size] for off in range(3)) in allowed
                                             for index in range(cycle_size)):
                    expected.add(candidate)
            obtained, _ = cycle_join(allowed, total, cycle_size)
            assert len(obtained) == len(set(obtained)) and set(obtained) == expected
            if cycle_size == 8:
                assert meet_join(allowed, total)[0] == bool(expected)
            count += 1
            hits += bool(expected)
    assert 0 < hits < count
    print('calibrated join:', count, 'small cycles checked by brute force;', hits, 'positive cases')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', nargs='?')
    parser.add_argument('candidates', nargs='?')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--labelg')
    parser.add_argument('--write-obstructions')
    parser.add_argument('--verify-obstructions')
    parser.add_argument('--only-calibrate', action='store_true')
    args = parser.parse_args()
    calibrate()
    if args.only_calibrate:
        return
    sources = [decode(row) for row in Path(args.census).read_text().splitlines()]
    candidate_rows = Path(args.candidates).read_text().splitlines()[:args.limit]
    if not candidate_rows:
        raise ValueError('empty candidate list')
    representations = '\n'.join(row.rsplit('\t', 1)[1] for row in candidate_rows) + '\n'
    labelled = subprocess.run([args.labelg, '-q'], input=representations, capture_output=True, text=True, check=True)
    keys = labelled.stdout.splitlines()
    assert len(keys) == len(candidate_rows)
    families = {}
    seen_iso = 0
    started = time.process_time()
    for row, key in zip(candidate_rows, keys):
        line, isolated, text = row.split('\t')
        isolated = int(isolated)
        adj = decode(text)
        assert len(adj) == 16
        if key not in families:
            families[key] = (adj, set())
        representative, triples = families[key]
        outside = list(bits(((1 << 22) - 1) ^ isolated))
        original = sources[int(line)]
        template = [sum(1 << index for index, v in enumerate(outside) if original[u] >> v & 1) for u in bits(isolated)]
        found = False
        for isom in labelled_maps(adj, representative):
            found = True
            seen_iso += 1
            masks = [sum(1 << isom[index] for index in bits(mask)) for mask in template]
            triples.update(three_types(masks))
        assert found
    print('families', len(families), 'label maps', seen_iso, 'windows', sum(len(rec[1]) for rec in families.values()),
          f'build CPU={time.process_time()-started:.3f}', flush=True)
    nested = Counter()
    retained = 0
    proofs = {}
    if args.verify_obstructions:
        proofs = json.loads(Path(args.verify_obstructions).read_text())
        assert proofs.keys() == families.keys()
        sizes = Counter()
        for key, (adj, triples) in families.items():
            degrees = [9 - mask.bit_count() for mask in adj]
            assert list(adj) == proofs[key]['adj']
            assert check_obstruction(triples, degrees, proofs[key]['vertices']) == proofs[key]['profiles']
            sizes[len(proofs[key]['vertices'])] += 1
        print('verified projected obstructions:', sorted(sizes.items()))
        return
    for key, (adj, triples) in families.items():
        degrees = [9 - mask.bit_count() for mask in adj]
        examples, nodes = cycle_join(triples, degrees, 8, emit_limit=1)
        nested['nodes'] += nodes
        intersects, words, pairs, loads = meet_join(triples, degrees)
        assert intersects == bool(examples)
        nested['words'] += words
        nested['pairs'] += pairs
        if args.write_obstructions:
            projection = sparse_obstruction(loads, degrees)
            assert projection is not None
            count = check_obstruction(triples, degrees, projection)
            proofs[key] = dict(adj=adj, vertices=projection, profiles=count)
        if examples:
            retained += 1
    print('families with join', retained, 'search nodes', nested['nodes'], 'meet-in-middle words', nested['words'],
          'capacity-matched pairs', nested['pairs'], f'total CPU={time.process_time()-started:.3f}')
    if args.write_obstructions:
        Path(args.write_obstructions).write_text(json.dumps(proofs, indent=2, sort_keys=True) + '\n')
        print('obstruction projection sizes:', sorted(Counter(len(row['vertices']) for row in proofs.values()).items()))


if __name__ == '__main__':
    main()
