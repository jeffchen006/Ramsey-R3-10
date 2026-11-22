from collections import defaultdict
import csv
import json
from pathlib import Path
import sys


def timings(folder, *names):
    return sum(sum(map(float, (folder / f'{name}.time').read_text().splitlines()[-1].split()[:2]))
               for name in names)


def price(production, review, alignments):
    audited = json.loads((production / 'presolve-sets.json').read_text())
    receipts = json.loads((production / 'checked-union.json').read_text())
    baseline = {(board, tuple(left), tuple(right)) for board, left, right in audited['baseline']}
    expect = defaultdict(list)
    for pilot in audited['pilots']:
        for board, left, right in pilot['scope']:
            key = board, tuple(left), tuple(right)
            if key not in baseline:
                expect[key].append(pilot['pilot'])

    seats, first_seen = {}, {}
    with alignments.open(newline='') as file:
        for row in csv.DictReader(file, delimiter='\t'):
            board = int(row['board'])
            left, right = (tuple(map(int, row[name].split(','))) for name in ('left_pairs', 'right_pairs'))
            key = board, left, right
            assert key not in seats
            membership = list(map(int, row['pilots_after_baseline'].split(',')))
            assert membership == expect[key]
            first_seen[key] = int(row['first_pilot'])
            assert first_seen[key] == min(membership)
            seats[key] = int(row['fixed_labelled_alignments'])
    assert expect.keys() == seats.keys()

    print('pilot\tboard\tvars\tclauses\tfresh_keys\tfresh_alignments\tprefix_alignments'
          '\tgen_s\tprebind_s\tsolve_s\tproduction_replay_s\tclean_replay_s\tproof_bytes')
    checked = set()
    for pilot in receipts['checked_pilots']:
        number = pilot['pilot']
        fresh = {(board, tuple(left), tuple(right)) for board, left, right in pilot['fresh']}
        assert fresh == {key for key in seats if first_seen[key] == number}
        assert not checked & fresh
        checked |= fresh
        folder = production / f'p{number}'
        independent = review / f'p{number}'
        with (folder / 'grid.cnf').open() as file:
            _, _, variables, clauses = file.readline().split()
        gen = timings(folder, 'gen')
        prebind = timings(folder, 'audit')
        solve = timings(folder, 'solve')
        replay = timings(folder, 'rebind', 'rebind-audit', 'lrat', 'cake')
        again = timings(independent, 'gen', 'audit', 'lrat', 'cake')
        print(number, pilot['board'], variables, clauses, len(fresh), sum(seats[key] for key in fresh),
              sum(seats[key] for key in checked), f'{gen:.2f}', f'{prebind:.2f}', f'{solve:.2f}',
              f'{replay:.2f}', f'{again:.2f}', (folder / 'grid.lrat').stat().st_size, sep='\t')


if __name__ == '__main__':
    price(*map(Path, sys.argv[1:]))
