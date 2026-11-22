#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path

from panel18_bind import frame_binding, read_integer_rows
from panel18_marginals import predicate
from panel19_fifth import catalogue, old_groups
from verify_panel17 import bits


def frame_rows(path):
    for index, fields in enumerate(read_integer_rows(path, 8)):
        yield index, fields[:6], fields[6:]


def independent_flags(cases, graphs):
    for case in cases:
        physical = case[2:8], case[8:]
        records = [(graphs[side][host], neutral, marks) for side, (host, neutral, *marks) in enumerate(physical)]
        flags = []
        for side in range(2):
            origin, neutral, marks = records[side]
            dest, dest_neutral, _ = records[1-side]
            _, _, groups = frame_binding(origin, neutral, tuple(marks), 9, 5, 4, 9)
            profiles = [tuple(sorted(2 * (8 - origin[site].bit_count() + (origin[site] >> neutral & 1))
                                     + (origin[site] >> neutral & 1) for site in group)) for group in groups]
            flags.append(''.join(str(int(predicate(dest, dest_neutral, profile, 6))) for profile in profiles))
        yield case[:2], tuple(flags)


def marked_audit(path, records, flags, left_graph, root, graphs):
    with path.open() as stream:
        for line, case, row in zip(stream, records, flags, strict=True):
            marked = json.loads(line)
            assert tuple(marked['id']) == case[:2]
            assert tuple(marked['order16']) == case[2:8] and tuple(marked['order17']) == case[8:]
            assert tuple(marked['old_flags']) == row[1]
            assert marked['x16'] == root and marked['x_required_private_degree17'] == 3
            assert set(marked['x_old16_singletons']) == set(bits(left_graph[root]))
            assert set(marked['core16']) == set(range(16)) - {root, *bits(left_graph[root])}
            right_host, right_neutral, *right_marks = case[8:]
            left_neutral = case[3]
            assert marked['x_adjacent_neutral'] == bool(left_graph[root] >> left_neutral & 1)
            assert marked['axes'] == [[site for site in range(order) if site != neutral]
                                       for order, neutral in ((16, left_neutral), (17, right_neutral))]
            assert marked['old17_singletons'] == [list(bits(group)) for group in old_groups(right_marks, 17)]
            assert marked['full17_support'] == [sum(1 << pole for pole, mark in enumerate(right_marks)
                                                     if mark >> site & 1) for site in range(17)]
            assert marked['right_neutral_contacts'] == list(bits(graphs[1][right_host][right_neutral]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cat16', type=Path)
    parser.add_argument('cat17', type=Path)
    parser.add_argument('frames16', type=Path)
    parser.add_argument('frames17', type=Path)
    parser.add_argument('old_cases', type=Path)
    parser.add_argument('critic_vetoes', type=Path)
    parser.add_argument('a_base', type=Path)
    parser.add_argument('pilot', type=Path)
    args = parser.parse_args()
    graphs = catalogue(args.cat16), catalogue(args.cat17)
    right_candidates = []
    count_full = 0
    for index, right, degree_key in frame_rows(args.frames17):
        count_full += 1
        graph = graphs[1][right[0]]
        if degree_key == (75, 5) and any(sum(mark >> site & 1 for mark in right[2:]) == 3
                                         for site in range(len(graph))):
            right_candidates.append((index, right))
    assert count_full == 59521 and len(right_candidates) == 116
    old_ids = {fields[:2] for fields in read_integer_rows(args.old_cases, 14)}
    prior_veto = {fields[:2] for fields in read_integer_rows(args.critic_vetoes, 14)}
    assert len(prior_veto) == 56
    selection = []
    for index, left, degree_key in frame_rows(args.frames16):
        if degree_key != (66, 4):
            continue
        graph = graphs[0][left[0]]
        roots = [site for site, row in enumerate(graph) if row.bit_count() == 3
                 and sum(mark >> site & 1 for mark in left[2:]) == 3]
        if not roots:
            continue
        assert len(roots) == 1
        root = roots[0]
        cases = [(index, right_index, *left, *right) for right_index, right in right_candidates]
        overlap = tuple(case[:2] for case in cases if case[:2] in old_ids)
        print('eligible left', index, 'root', root, 'host', left[0], 'old overlap', len(overlap), *overlap)
        if overlap:
            selection.append((index, root, left[0], len(overlap), '-', '-', '-', '-'))
            continue
        flags = list(independent_flags(cases, graphs))
        counts = Counter(tuple(row == '1111' for row in flag) for _, flag in flags)
        ordered = tuple(counts[bool(label & 1), bool(label & 2)] for label in range(4))
        selection.append((index, root, left[0], 0, *ordered))
        if ordered[3]:
            break
    else:
        raise RuntimeError('no predeclared bin')
    assert ['\t'.join(map(str, row)) for row in selection] == (args.a_base / 'selection.tsv').read_text().splitlines()[1:]
    assert cases == list(read_integer_rows(args.a_base / 'heldout.cases.tsv', 14))
    reference_flags = [tuple(line.split()) for line in (args.a_base / 'heldout.flags.tsv').read_text().splitlines()]
    assert [(str(ids[0]), str(ids[1]), *signs) for ids, signs in flags] == reference_flags
    marked_audit(args.a_base / 'heldout.marked.jsonl', cases, flags, graph, root, graphs)
    positives = [case for case, (_, signs) in zip(cases, flags, strict=True) if signs == ('1111', '1111')]
    assert positives == list(read_integer_rows(args.a_base / 'heldout.positive.cases.tsv', 14))
    assert not ({case[:2] for case in cases} & (old_ids | prior_veto))
    total = len(positives)
    sample = min(64, total)
    with args.pilot.open('w') as stream:
        for index in range(sample):
            print(*positives[((2*index + 1)*total) // (2*sample)], file=stream)
    print('raw', len(cases), '00/10/01/11', *ordered, 'group bits', 8 * len(cases), 'pilot', sample,
          'old-overlap 0 prior-core13-overlap 0')
    print('root', root, 'left host', left[0], 'physical neutral', left[1])


if __name__ == '__main__':
    main()
