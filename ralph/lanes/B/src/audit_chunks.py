"""Audit a finished Lane B generation or MTF pass against an exact input count."""
import argparse
import hashlib
import itertools
import re
from pathlib import Path


def audit(directory, degree, size, chunk_size, source=None, multi_degree=False):
    expected = [f'd{degree}_{index:05d}' for index in range((size + chunk_size - 1) // chunk_size)]
    pattern = f'd{degree}_*.canon' if multi_degree else '*.canon'
    actual = sorted(file.stem for file in directory.glob(pattern))
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
        if source is not None:
            block = list(itertools.islice(source, chunk_size))
            if len(block) != want:
                raise ValueError(f'{stem}: missing bound inputs')
            digest = hashlib.sha256(b''.join(block)).hexdigest()
            if re.findall(r'^input_sha256=([0-9a-f]{64})$', log, re.MULTILINE) != [digest]:
                raise ValueError(f'{stem}: ordered input hash differs')
        canonical_nonempty = (directory / f'{stem}.canon').stat().st_size > 0
        if canonical_nonempty != (int(output) > 0):
            raise ValueError(f'{stem}: canonical output disagrees with log')
        cpu += float(seconds)
        raw += int(output)
    if source is not None and source.read(1):
        raise ValueError('extra bound inputs')
    print(f'{directory}: audited {size} inputs, {len(expected)} chunks, {raw} raw outputs, {cpu:.2f} solver CPU s')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('degree', type=int)
    parser.add_argument('size', type=int)
    parser.add_argument('chunk_size', type=int)
    parser.add_argument('--bind', type=Path, help='verify ordered SHA-256 for each rendered input chunk')
    parser.add_argument('--multi-degree', action='store_true')
    args = parser.parse_args()
    if args.bind is not None:
        with args.bind.open('rb') as source:
            audit(args.directory, args.degree, args.size, args.chunk_size, source, args.multi_degree)
    else:
        audit(args.directory, args.degree, args.size, args.chunk_size, multi_degree=args.multi_degree)
