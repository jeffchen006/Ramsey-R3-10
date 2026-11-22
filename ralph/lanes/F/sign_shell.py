"""Score sparse changes of matching signs about a specified lift."""

import argparse
import csv
from collections import Counter
from functools import reduce
from itertools import combinations
from operator import xor
from pathlib import Path
import sys

from pole_audit import independent, parse_graph6, relabel, to_graph6, write_lines
from relift_audit import encode, quotient, walk_score

sys.path.insert(0, str(Path.cwd()))
import ev


def interleaved(text):
    graph = parse_graph6(text)
    size = len(graph) // 2
    return relabel(graph, [index + side * size for index in range(size) for side in range(2)])


def columns(graph):
    base = quotient(graph)
    size = len(base)
    marks = {pair: 0 for pair in combinations(range(size), 2) if base[pair[0]][pair[1]] == 1}
    triangle = 1
    for triple in combinations(range(size), 3):
        edges = list(combinations(triple, 2))
        if all(edge in marks for edge in edges):
            for edge in edges:
                marks[edge] |= triangle
            triangle <<= 1
    return marks


def changed(graph, edges):
    result = graph.copy()
    for left, right in edges:
        for side in range(2):
            result[2 * left + side] ^= 3 << (2 * right)
            result[2 * right + side] ^= 3 << (2 * left)
    return result


def shell(graph, radius, cyclic):
    marks = columns(graph)
    size = len(graph) // 2
    if cyclic:
        assert any(relabel(graph, [2 * ((index + 1) % size) + (side ^ (carry & (index == size - 1)))
                                   for index in range(size) for side in range(2)]) == graph for carry in (0, 1))
    for weight in range(1, radius + 1):
        seen = set()
        for subset in combinations(marks, weight):
            if cyclic and subset in seen:
                continue
            if reduce(xor, (marks[edge] for edge in subset), 0):
                continue
            if cyclic:
                orbit = {tuple(sorted(tuple(sorted(((left + shift) % size, (right + shift) % size)))
                                      for left, right in subset)) for shift in range(size)}
                seen.update(orbit)
            yield subset, len(orbit) if cyclic else 1


def compare_small():
    from cyclic_base import baselines, profiles
    bases = edits = 0
    for profile, _ in profiles(4, 0, 7):
        for _, natural in baselines(4, profile, True):
            graph = interleaved(to_graph6(natural))
            marks = columns(graph)
            raw = set()
            for weight in (1, 2, 3):
                for subset in combinations(marks, weight):
                    mutant = changed(graph, subset)
                    if all(independent(row, mutant) for row in mutant):
                        raw.add(subset)
            generated = {subset for subset, _ in shell(graph, 3, False)}
            assert raw == generated
            scores = Counter(walk_score(changed(graph, subset), 4) for subset in raw)
            reduced = Counter()
            for subset, multiplicity in shell(graph, 3, True):
                reduced[ev.indep(changed(graph, subset), 4)] += multiplicity
            assert reduced == scores
            bases += 1
            edits += len(raw)
    print('PASS explicit n8 triangle tests and score histograms', bases, 'graphs', edits, 'edits')


def score_shell(graph, radius, cyclic, ksize):
    best = ev.indep(graph, ksize)
    witness, changes = graph, ()
    labelled = scored = 0
    for subset, multiplicity in shell(graph, radius, cyclic):
        labelled += multiplicity
        scored += 1
        mutant = changed(graph, subset)
        score = ev.indep(mutant, ksize, best + 1)
        if score < best:
            best, witness, changes = score, mutant, subset
    assert walk_score(witness, ksize) == best and all(independent(row, witness) for row in witness)
    return best, witness, changes, labelled, scored


def controls():
    compare_small()
    [text] = Path('ctl.recovered.g6').read_text().splitlines()
    graph = parse_graph6(text)
    for radius in (1, 2, 3):
        for subset, _ in shell(graph, radius, False):
            if len(subset) != radius:
                continue
            mutant = changed(graph, subset)
            start = ev.indep(mutant, 10)
            if not start:
                continue
            if radius == 3:
                assert reduce(xor, (columns(mutant)[edge] for edge in subset), 0) == 0
                assert changed(mutant, subset) == graph
                print('PASS reversible n38 weight 3 (not a radius-3 search)', start, subset)
                break
            result, recovered, moves, labelled, scored = score_shell(mutant, radius, False, 10)
            assert result == 0
            Path(f'shell.ctl{radius}.g6').write_text(to_graph6(recovered) + '\n')
            print('PASS n38 planted radius', radius, 'scores', start, result, 'best move', moves, 'tried', scored)
            break
        else:
            raise RuntimeError('no positive mutant at planted radius')


def target(radius, rows):
    with open('target.meta.tsv') as handle:
        metadata = list(csv.DictReader(handle, delimiter='\t'))
    graphs = Path('target.baseline.g6').read_text().splitlines()
    for index in rows:
        graph = interleaved(graphs[index])
        row = metadata[index]
        assert encode(quotient(graph)) == row['quotient'] and ev.indep(graph, 10) == int(row['baseline'])
        best, witness, changes, labelled, scored = score_shell(graph, radius, True, 10)
        print(f'row={index} radius={radius} baseline={row["baseline"]} best={best} labelled={labelled} '
              f'scored={scored} changes={changes}', flush=True)
        Path(f'shell.{index}.{radius}.g6').write_text(to_graph6(witness) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('ctl', 'target'))
    parser.add_argument('--radius', type=int, choices=(1, 2, 3), default=2)
    parser.add_argument('--rows', nargs='+', type=int, default=list(range(4)))
    args = parser.parse_args()
    if args.mode == 'ctl':
        controls()
    else:
        target(args.radius, args.rows)
