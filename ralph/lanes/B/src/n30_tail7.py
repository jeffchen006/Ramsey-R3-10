"""Generate and MTF-scan one missing d7 branch outside the prefix cover."""
import argparse
from pathlib import Path

from scan_mtf import scan
from seed import PICKG, SRC, generate, run


def tail7(level, workers):
    source = Path('val/r38_22_le44.g6')
    label = f'd7_e{level}_outside_prefix'
    selected = Path('work') / f'{label}_inputs.g6'
    temporary = selected.with_suffix('.tmp')
    run([PICKG, '-q', f'-e{level}', source, temporary])
    count = {43: 1521, 44: 72353}[level]
    run(['python3', SRC / 'ecount.py', temporary, f'{level}:{count}'])
    temporary.replace(selected)
    generation = [
        'build/gluecheap', '-k', 8, '-d', 7, '-m', 2, '-M', 8, '-E', 88, '-e', 88,
        '-A', 58, '-B', 51, '-C', 42,
    ]
    generate(label, [(7, selected, generation)], 32, workers)
    output = Path('val') / f'{label}.g6'
    print(f'{label}: canonical e88 graphs {output.stat().st_size // 75}', flush=True)
    scan(output, 88, workers, label)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('level', type=int, choices=(43, 44))
    parser.add_argument('--workers', type=int, required=True)
    args = parser.parse_args()
    tail7(args.level, args.workers)
