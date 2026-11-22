#!/usr/bin/env python3
"""Preselect fresh fixed-label headers without a new restoration test."""

from pathlib import Path
from sys import argv

from panel18_bind import read_integer_rows
from panel19_bind import frame_rows, independent_flags
from panel19_fifth import catalogue


def main(repo, work):
    previous = repo / 'scratch/C/r19'
    catalogues = tuple(catalogue(repo / f'gluing/val/r3_6_{order}.g6') for order in (16, 17))
    left_id, root = 42072, 1
    left_index, left, key = next(row for row in frame_rows(previous / 'frames16.tsv') if row[0] == left_id)
    assert key == (66, 4) and left_index != 42679
    assert left[:2] == (97, 6)
    assert catalogues[0][left[0]][root].bit_count() == 3
    assert sum(mark >> root & 1 for mark in left[2:]) == 3
    excluded = {row[:2] for path in (
        repo / 'scratch/C/r16/bound.cases.tsv', previous / 'pilot.tsv',
        repo / 'scratch/critic/R18/survivors.cases') for row in read_integer_rows(path, 14)}
    roster = []
    for right_id, right, right_key in frame_rows(previous / 'frames17.tsv'):
        if right_key != (75, 5) or not any(sum(mark >> site & 1 for mark in right[2:]) == 3
                                          for site in range(17)):
            continue
        roster.append((left_id, right_id, *left, *right))
    assert len(roster) == 116
    assert [row[:2] for row in roster if row[:2] in excluded] == [(42072, 16780)]
    fresh = [row for row in roster if row[:2] not in excluded]
    flags = dict(independent_flags(fresh, catalogues))
    positive = [row for row in fresh if all('0' not in flag for flag in flags[row[:2]])]
    print('left/root', left_id, root, 'payload', left)
    print('raw', len(roster), 'fresh', len(fresh), 'both-old-positive', len(positive))
    chosen = positive[:8]
    assert chosen
    for row in chosen:
        print('selected', *row, *flags[row[:2]])
    (work / 'chosen.tsv').write_text(''.join(' '.join(map(str, row)) + '\n' for row in chosen))


if __name__ == '__main__':
    main(*map(Path, argv[1:]))
