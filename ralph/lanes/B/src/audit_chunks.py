"""Audit a finished Lane B generation or MTF pass against an exact input count."""
import argparse
import re
from pathlib import Path


def audit(directory, degree, size, chunk_size):
    expected = [f'd{degree}_{index:05d}' for index in range((size + chunk_size - 1) // chunk_size)]
    actual = sorted(file.stem for file in directory.glob('*.canon'))
    if actual != expected:
        raise ValueError(f'wrong chunk index set: expected {len(expected)}, found {len(actual)}')
    cpu = 0.0
    raw = 0
    for index, stem in enumerate(expected):
        log = (directory / f'{stem}.log').read_text()
        rows = re.findall(r'\bin=(\d+) .*\bout=(\d+) cpu=([\d.]+)s', log)
        want = min(chunk_size, size - index * chunk_size)
        if len(rows) != 1 or int(rows[0][0]) != want or 'bad graph6' in log:
            raise ValueError(f'{stem}: invalid or incomplete count')
        _, output, seconds = rows[0]
        canonical_nonempty = (directory / f'{stem}.canon').stat().st_size > 0
        if canonical_nonempty != (int(output) > 0):
            raise ValueError(f'{stem}: canonical output disagrees with log')
        cpu += float(seconds)
        raw += int(output)
    print(f'{directory}: audited {size} inputs, {len(expected)} chunks, {raw} raw outputs, {cpu:.2f} solver CPU s')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('degree', type=int)
    parser.add_argument('size', type=int)
    parser.add_argument('chunk_size', type=int)
    args = parser.parse_args()
    audit(args.directory, args.degree, args.size, args.chunk_size)
