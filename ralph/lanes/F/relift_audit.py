#!/usr/bin/env python3
"""Generate quotient fixtures and independently audit relift rows and witnesses."""

import argparse
import csv
from itertools import combinations, product
from pathlib import Path
from random import Random

from pole_audit import independent, independent_sets, num_edges, one_graph, parse_graph6, write_lines


def pairs(size):
    return [(left, right) for right in range(size) for left in range(right + 1)]


def encode(matrix):
    return chr(ord('A') + len(matrix)) + ''.join(str(matrix[right][left]) for left, right in pairs(len(matrix)))


def decode(text):
    size = ord(text[0]) - ord('A')
    matrix = [[0] * size for _ in range(size)]
    for (left, right), char in zip(pairs(size), text[1:], strict=True):
        matrix[left][right] = matrix[right][left] = int(char)
    return matrix


def quotient(graph):
    assert len(graph) % 2 == 0 and all(independent(row, graph) for row in graph)
    for left in range(len(graph)):
        for right in range(len(graph)):
            assert (graph[left] >> right) & 1 == (graph[left ^ 1] >> (right ^ 1)) & 1
    size = len(graph) // 2
    result = [[0] * size for _ in range(size)]
    for left, right in pairs(size):
        result[left][right] = result[right][left] = ((graph[2 * left] >> (2 * right)) & 3).bit_count()
    return result


def explicit_lift(matrix, signs):
    size = len(matrix)
    graph = [0] * (2 * size)

    def add(left, right):
        graph[left] |= 1 << right
        graph[right] |= 1 << left

    for left, right in pairs(size):
        value = matrix[left][right]
        if not value:
            continue
        if left == right:
            assert value == 1
            add(2 * left, 2 * left + 1)
        elif value == 2:
            for side0, side1 in product(range(2), repeat=2):
                add(2 * left + side0, 2 * right + side1)
        else:
            sign = next(signs)
            add(2 * left, 2 * right + sign)
            add(2 * left + 1, 2 * right + (1 ^ sign))
    return graph


def walk_score(graph, target):
    return sum(1 for _ in independent_sets(graph, (1 << len(graph)) - 1, target))


def small_oracle():
    rng = Random(6121961)
    examples = set()
    while len(examples) < 160:
        size = rng.randrange(2, 7)
        matrix = [[0] * size for _ in range(size)]
        for left, right in pairs(size):
            value = rng.choices([0, 1, 2], [8, 4, 1] if left != right else [8, 3, 0])[0]
            matrix[left][right] = matrix[right][left] = value
        examples.add(encode(matrix))
    examples.update([encode([[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]]),
                     encode([[0, 1, 1], [1, 0, 1], [1, 1, 0]])])
    scores = []
    counts = []
    for text in sorted(examples):
        matrix = decode(text)
        size = len(matrix)
        count = sum(matrix[left][right] == 1 for left, right in combinations(range(size), 2))
        optimum, valid = None, 0
        for signs in product(range(2), repeat=count):
            graph = explicit_lift(matrix, iter(signs))
            if not all(independent(row, graph) for row in graph):
                continue
            valid += 1
            score = sum(all(not (graph[vertex] >> other) & 1 for vertex, other in combinations(subset, 2))
                        for subset in combinations(range(2 * size), 4))
            optimum = score if optimum is None else min(optimum, score)
        scores.append(-1 if optimum is None else optimum)
        counts.append(valid)
    write_lines(Path('small.q'), sorted(examples))
    write_lines(Path('small.expected'), (f'{score} {count}' for score, count in zip(scores, counts, strict=True)))
    print(f'small quotients={len(scores)} explicit_valid_signings={sum(counts)} min_score_values={sorted(set(scores))}')


def choose_attachments(matrix, lo, hi, min_old=0, max_old=9):
    size = len(matrix)
    deficits = [max_old - sum(row) for row in matrix]
    def rec(index, prefix, degree):
        if degree > hi or degree + sum(capacities[index:]) + 1 < lo:
            return
        if index == size:
            for vertical in range(2):
                if lo <= degree + vertical <= hi and (not vertical or 2 not in prefix):
                    yield prefix + [vertical]
            return
        double = any(value == 2 and matrix[other][index] for other, value in enumerate(prefix))
        for link in range(max(0, min_old - sum(matrix[index])), min(0 if double else 2, capacities[index]) + 1):
            if link == 2 and any(value and matrix[other][index] for other, value in enumerate(prefix)):
                continue
            yield from rec(index + 1, prefix + [link], degree + link)
    capacities = [min(1 if matrix[index][index] else 2, deficit) for index, deficit in enumerate(deficits)]
    if min(capacities, default=0) >= 0:
        yield from rec(0, [], 0)


def extend(matrix, column):
    return [row + [column[index]] for index, row in enumerate(matrix)] + [column]


def control(sources):
    fixtures = set()
    planted = set()
    for path in sources:
        graph = one_graph(path)
        matrix = quotient(graph)
        assert len(graph) == 38 and walk_score(graph, 10) == 0
        planted.add(encode(matrix))
        for removed in [0, 6, 12, 18]:
            order = [index for index in range(len(matrix)) if index != removed]
            source = [[matrix[left][right] for right in order] for left in order]
            expected = [matrix[left][removed] for left in order] + [matrix[removed][removed]]
            generated = list(choose_attachments(source, sum(expected), sum(expected), min_old=6))
            assert expected in generated
            score = encode(extend(source, expected))
            planted.add(score)
            alternatives = sorted(encode(extend(source, column)) for column in generated if column != expected)
            for index in [0, len(alternatives) // 2, len(alternatives) - 1]:
                if alternatives:
                    fixtures.add(alternatives[index])
            print(f'{path.name} removed={removed} candidate_columns={len(generated)}')
    write_lines(Path('control38.q'), sorted(fixtures | planted))
    write_lines(Path('control38.planted'), sorted(planted))


def sample_columns(matrix, lo, hi, rng, count):
    deficits = [9 - sum(row) for row in matrix]
    avail = [index for index, deficit in enumerate(deficits) if deficit]
    result = set()
    for _ in range(count * 6):
        column = [0] * (len(matrix) + 1)
        column[-1] = rng.randrange(2)
        target = rng.randint(lo, hi)
        if target <= len(avail) + column[-1]:
            for index in rng.sample(avail, target - column[-1]):
                column[index] = 1
            result.add(tuple(column))
        if len(result) == count:
            break
    return sorted(result)


def target(sources, sample):
    rng = Random(266231)
    all_rows = set()
    for number, path in enumerate(sources):
        graph = one_graph(path)
        matrix = quotient(graph)
        assert len(graph) == 38 and walk_score(graph, 10) == 0
        no_deletion = {encode(extend(matrix, column)) for column in choose_attachments(matrix, 6, 9, min_old=6)}
        schemes = [sorted(no_deletion)]
        single = [(left, right) for left, right in combinations(range(len(matrix)), 2) if matrix[left][right] == 1]
        for deletions in (1, 2, 3):
            seen = set()
            while len(seen) < sample:
                cut = tuple(sorted(rng.sample(single, deletions)))
                if len(set(sum((list(edge) for edge in cut), []))) != deletions * 2:
                    continue
                seen.add(cut)
            children = set()
            for cut in sorted(seen):
                base = [row.copy() for row in matrix]
                for left, right in cut:
                    base[left][right] = base[right][left] = 0
                for column in sample_columns(base, 7, 9, rng, 8):
                    updated = extend(base, list(column))
                    if any(sum(row) < 6 for row in updated):
                        continue
                    physical_edges = sum(sum(row) for row in updated)
                    if 171 <= physical_edges <= 180:
                        children.add(encode(updated))
            schemes.append(sorted(children))
        for deletions, batch in enumerate(schemes):
            print(f'{path.name} deleted_matchings={deletions} rows={len(batch)} new={len(set(batch) - all_rows)}')
            rng.shuffle(batch)
            write_lines(Path(f'target{number}_{deletions}.q'), (row for row in batch if row not in all_rows))
            all_rows.update(batch)


def legal_support(matrix):
    occupied = [sum(1 << index for index, weight in enumerate(row) if weight and other != index)
                for other, row in enumerate(matrix)]
    for left, right in combinations(range(len(matrix)), 2):
        if matrix[left][right] == 2 and (matrix[left][left] or matrix[right][right] or occupied[left] & occupied[right]):
            return False
    return True


def switches(matrix):
    size = len(matrix)
    for left, right, third, fourth in combinations(range(size), 4):
        matching = [[(left, right), (third, fourth)], [(left, third), (right, fourth)], [(left, fourth), (right, third)]]
        for smaller in range(3):
            if not all(matrix[aa][bb] for aa, bb in matching[smaller]):
                continue
            for larger in range(3):
                if smaller == larger or not all(matrix[aa][bb] < 2 for aa, bb in matching[larger]):
                    continue
                child = [row.copy() for row in matrix]
                for change, patch in [(-1, matching[smaller]), (1, matching[larger])]:
                    for aa, bb in patch:
                        child[aa][bb] += change
                        child[bb][aa] += change
                if legal_support(child):
                    yield encode(child)


def switch_control(sources):
    rng = Random(627208)
    for number, path in enumerate(sources):
        graph = one_graph(path)
        assert len(graph) == 38 and walk_score(graph, 10) == 0
        matrix = quotient(graph)
        planted = encode(matrix)
        mutant = rng.choice(sorted(set(switches(matrix))))
        assert mutant != planted
        neighborhood = sorted(set(switches(decode(mutant))))
        assert planted in neighborhood
        sample = [row for row in neighborhood if row != planted]
        sample = rng.sample(sample, min(len(sample), 47)) + [planted]
        rng.shuffle(sample)
        write_lines(Path(f'switchCtl{number}.q'), sample)
        write_lines(Path(f'switchCtl{number}.planted'), [planted])
        write_lines(Path(f'switchCtl{number}.mutant'), [mutant])
        print(f'{path.name} midpoint={mutant} full_degree_preserving_neighborhood={len(neighborhood)} sample={len(sample)}')


def switch_target(sources, sample):
    rng = Random(60117)
    for number, path in enumerate(sources):
        graph = one_graph(path)
        assert len(graph) == 40 and min(row.bit_count() for row in graph) >= 6 and max(row.bit_count() for row in graph) <= 9
        matrix = quotient(graph)
        neighbors = sorted(set(switches(matrix)))
        assert len(neighbors) >= sample
        rng.shuffle(neighbors)
        write_lines(Path(f'switchTarget{number}.q'), [encode(matrix)] + neighbors[:sample])
        print(f'{path.name} source={encode(matrix)} score={walk_score(graph,10)} full_neighbors={len(neighbors)} sample={sample}')


def deletions(matrix, depth, min_degree=6):
    def weights(index, remaining):
        if remaining == 0:
            yield encode(matrix)
            return
        for choice in range(index, len(cells)):
            left, right = cells[choice]
            if not matrix[left][right] or row_degrees[left] <= min_degree or row_degrees[right] <= min_degree:
                continue
            matrix[left][right] -= 1
            row_degrees[left] -= 1
            if right != left:
                matrix[right][left] -= 1
                row_degrees[right] -= 1
            yield from weights(choice, remaining - 1)
            matrix[left][right] += 1
            row_degrees[left] += 1
            if right != left:
                matrix[right][left] += 1
                row_degrees[right] += 1
    cells = [(left, right) for left, right in pairs(len(matrix)) if matrix[left][right]]
    row_degrees = [sum(row) for row in matrix]
    yield from weights(0, depth)


def sparse_sources(sources):
    rng = Random(66081)
    for number, path in enumerate(sources):
        graph = one_graph(path)
        assert len(graph) == 38 and walk_score(graph, 10) == 0
        matrix = quotient(graph)
        for depth in (1, 2):
            keys = sorted(set(deletions(matrix, depth)))
            assert len(keys) > 16 and all(legal_support(decode(key)) for key in keys)
            rng.shuffle(keys)
            write_lines(Path(f'sparse{number}_{depth}.q'), keys)
            write_lines(Path(f'sparse{number}_{depth}.pilot.q'), keys[:16])
            print(f'{path.name} deletion_units={depth} count={len(keys)}')


def sparse_control(sources):
    for number, path in enumerate(sources):
        graph = one_graph(path)
        assert len(graph) == 38 and walk_score(graph, 10) == 0
        matrix = quotient(graph)
        keys = sorted(set(deletions(matrix, 1)))
        expected = set()
        for left, right in pairs(len(matrix)):
            if not matrix[left][right] or sum(matrix[left]) <= 6 or sum(matrix[right]) <= 6:
                continue
            for side in (0, 1):
                if left == right and side == 0:
                    continue
                first, second = 2 * left, 2 * right + side
                if not (graph[first] >> second) & 1:
                    continue
                edited = graph.copy()
                for aa, bb in [(first, second), (first ^ 1, second ^ 1)]:
                    edited[aa] &= ~(1 << bb)
                    edited[bb] &= ~(1 << aa)
                expected.add(encode(quotient(edited)))
        assert set(keys) == expected
        print(f'PASS {path.name} deletion quotient coverage={len(keys)}')


def extend_sparse(sources):
    used = set()
    for path in sources:
        result = []
        parent_count = 0
        with path.open() as handle:
            for row in csv.DictReader(handle, delimiter='\t'):
                graph = parse_graph6(row['g6'])
                assert walk_score(graph, 10) == int(row['score']) == 0
                parent = quotient(graph)
                parent_count += 1
                primary = set()
                for column in choose_attachments(parent, 6, 9, min_old=6):
                    child = extend(parent, column)
                    if not legal_support(child) or not 161 <= sum(map(sum, child)) <= 180:
                        continue
                    key = encode(child)
                    primary.add(key)
                expected = set()
                component_ranges = [range(min(2, 9 - degree) + 1) for degree in map(sum, parent)] + [range(2)]
                for column in product(*component_ranges):
                    if not 6 <= sum(column) <= 9:
                        continue
                    child = extend(parent, list(column))
                    if legal_support(child) and 161 <= sum(map(sum, child)) <= 180:
                        expected.add(encode(child))
                assert expected == primary
                result.extend(sorted(primary - used))
                used.update(primary)
        write_lines(Path(f'{path.stem}.extend.q'), sorted(result))
        print(f'{path.name} positive_parent_keys={parent_count} new_n40_keys={len(result)}')


def audit(quotient_path, result_path, log_path, target_k, ceiling, expected_path=None, planted_path=None):
    quotients = quotient_path.read_text().splitlines()
    with result_path.open() as handle:
        records = list(csv.DictReader(handle, delimiter='\t'))
    results = {int(row['idx']): row for row in records}
    assert len(results) == len(records) and len(quotients) == len(set(quotients))
    log = log_path.read_text().splitlines()
    assert len(log) == len(quotients) + 1 and log[-1].startswith(f'END rows={len(quotients)} ')
    found = set()
    filters = caps = impossible = 0
    expected = [int(row.split()[0]) for row in expected_path.read_text().splitlines()] if expected_path else None
    assert expected is None or len(expected) == len(quotients)
    for index, (text, line) in enumerate(zip(quotients, log[:-1], strict=True)):
        assert line.startswith(f'row={index} status=')
        status = line.split()[1].partition('=')[2]
        assert status in {'yes', 'no', 'cap', 'filter'}
        if expected is not None:
            expect = expected[index]
            assert status == ('filter' if expect < 0 else 'yes' if expect <= ceiling else 'no'), (index, expect, line)
        if status == 'filter':
            filters += 1
        if status == 'no':
            impossible += 1
        if status == 'cap':
            caps += 1
        if status != 'yes':
            assert index not in results
            continue
        result = results.pop(index)
        graph = parse_graph6(result['g6'])
        assert encode(quotient(graph)) == text
        score = walk_score(graph, target_k)
        assert score == int(result['score']) <= ceiling
        print(f'row={index} recount={score} e={num_edges(graph)} degs={sorted({deg.bit_count() for deg in graph})}')
        found.add(text)
    assert not results
    assert log[-1] == f'END rows={len(quotients)} no={impossible} yes={len(found)} cap={caps} filter={filters}'
    if planted_path:
        assert set(planted_path.read_text().splitlines()) <= found
    print(f'PASS total={len(quotients)} found={len(found)} no={impossible} filtered={filters} capped={caps}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    modes.add_parser('small')
    for mode in ('control', 'target', 'switch_control', 'switch_target', 'sparse_sources', 'sparse_control', 'extend_sparse'):
        select = modes.add_parser(mode)
        select.add_argument('sources', type=Path, nargs='+')
        if mode in ('target', 'switch_target'):
            select.add_argument('--sample', type=int, default=32)
    select = modes.add_parser('audit')
    select.add_argument('quotient_path', type=Path)
    select.add_argument('result_path', type=Path)
    select.add_argument('log_path', type=Path)
    select.add_argument('target_k', type=int)
    select.add_argument('ceiling', type=int)
    select.add_argument('--expected', type=Path, dest='expected_path')
    select.add_argument('--planted', type=Path, dest='planted_path')
    args = vars(parser.parse_args())
    mode = args.pop('mode')
    {'small': small_oracle, 'control': control, 'target': target, 'audit': audit,
     'switch_control': switch_control, 'switch_target': switch_target, 'sparse_sources': sparse_sources,
     'sparse_control': sparse_control, 'extend_sparse': extend_sparse}[mode](**args)
