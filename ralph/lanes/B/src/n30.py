"""Checked, resumable version of t9_88.sh's order-30 generation stages."""
import argparse
from pathlib import Path
from seed import SRC, PICKG, calibrate_increments, filtered, generate, run


def order30(edges, workers, program, prefix):
    covered = 87 if prefix else edges
    increments = {5:3, 6:covered-84, 7:1 if covered == 87 else 3}
    calibrate_increments(9, 30, covered, increments)
    lower = {5:56, 6:49, 7:42}
    dependency = {5:58, 6:52, 7:44}
    cases = []
    for degree, inc in increments.items():
        order = 29-degree
        maximum = lower[degree]+inc-1
        preferred = Path(f'val/r38_{order}_le{maximum}.g6')
        seed = preferred if preferred.is_file() else filtered(Path(f'val/r38_{order}_le{dependency[degree]}.g6'), maximum)
        binary = {5:'gluepair', 6:'gluetrans', 7:'glue5'}[degree] if program == 'mixed' else program
        cases.append((degree, seed, [f'build/{binary}', '-k', 8, '-d', degree,
                                     '-m', 2, '-M', 8, '-e', edges]))
    family = f'r39_30_le{edges}_{program}' + ('_prefix' if prefix else '')
    generate(family, cases, 128, workers, '86:1800,87:147335' if edges == 87 else '')
    found = Path(f'val/{family}.g6')
    if edges == 88:
        lower_part = filtered(found, 87)
        run(['python3', SRC / 'ecount.py', lower_part, '86:1800,87:147335'])
    e86 = Path(f'work/{family}_e86.g6')
    run([PICKG, '-q', '-e86', found, e86])
    reference = Path('work/hog_30_86.canon')
    if e86.read_bytes() != reference.read_bytes():
        raise ValueError('independent HoG e86 set differs')
    print(f'{family}: exact e86 HoG equality and GR T14 lower-level counts checked; full through e={covered}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('edges', type=int, choices=[87, 88])
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--program', default='glue5')
    parser.add_argument('--prefix', action='store_true', help='generate partial e88 and all e<=87')
    args = parser.parse_args()
    order30(args.edges, args.workers, args.program, args.prefix)
