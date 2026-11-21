#!/usr/bin/env python3
"""Check exact memberships, terminal shards and retained proof bytes."""

import argparse
from collections import Counter
import gzip
import hashlib
from itertools import zip_longest
from pathlib import Path
import re
import subprocess

from check_root_cover import graph


ROOT = Path(__file__).resolve().parents[3]
LOWER_SHA = 'f64e710e848585dbf7b5fa45fd226d238d878148de8e49918a79ec1312e60149'
LEVELS = {123: 5, 124: 44, 125: 149, 126: 266, 127: 294, 128: 184, 129: 41, 130: 1}


def canonical(rows):
    output = subprocess.run([ROOT / 'opt/bin/shortg', '-q'], input=b''.join(rows),
                            capture_output=True, check=True).stdout
    return output.splitlines(keepends=True)


def digest(path):
    stream_type = gzip.open if path.suffix == '.gz' else open
    result = hashlib.sha256()
    with stream_type(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            result.update(block)
    return result.hexdigest()


def verify_manifest(work, manifest):
    seen = set()
    for line in manifest.read_text().splitlines():
        expected, name = line.split('  ', 1)
        assert name not in seen
        seen.add(name)
        path = work / name
        if path.suffix == '.lrat':
            path = path.with_suffix('.lrat.gz')
        assert digest(path) == expected, path
    return seen


def audit_shards(work, source, stems, kind):
    shards = []
    survivors = []
    cpu = [0., 0.]
    for stem in stems:
        def get(extension):
            return work / f'{stem}.{extension}'

        assert get('done').stat().st_size > 0
        primary = 'max' if kind == 'inner' else 'out'
        log = 'max.log' if kind == 'inner' else 'log'
        supplied = get('in').read_bytes().splitlines(keepends=True)
        shards.append(supplied)
        actual = get(primary).read_bytes().splitlines(keepends=True)
        assert actual == get('audit').read_bytes().splitlines(keepends=True)
        survivors.extend(actual)
        for index, name in enumerate((log, 'audit.log')):
            summary = get(name).read_text()
            assert summary.startswith(f'in={len(supplied)} out={len(actual)} ')
            cpu[index] += float(re.search(r'cpu=([0-9.]+)\s*s', summary)[1])
        assert verify_manifest(work, get('sha256')) == {f'{stem}.{extension}' for extension in
                                                        (('in', 'max', 'out', 'max.log', 'out.log') if kind == 'inner'
                                                         else ('in', 'out', 'log'))}
        if kind == 'inner':
            assert get('audit.done').stat().st_size > 0
            assert verify_manifest(work, get('audit.sha256')) == {
                f'{stem}.{extension}' for extension in ('in', 'audit', 'audit.log')}
            assert not get('out').stat().st_size
            summary = get('out.log').read_text()
            assert f'in={len(actual)} ' in summary and 'out=0 ' in summary
    entries = (row for block in zip_longest(*shards) for row in block if row is not None)
    for actual, expected in zip_longest(entries, source.read_bytes().splitlines(keepends=True)):
        assert actual == expected, (kind, actual, expected)
    print(f'{kind}: {sum(map(len, shards))} exact round-robin keys; {len(survivors)} survivors; CPU-s {cpu}')
    return survivors


def audit(work, check_lrat):
    source = work / 'r38_27.g6'
    assert digest(source) == LOWER_SHA
    lower = source.read_bytes().splitlines(keepends=True)
    assert len(lower) == 477142 and all(len(line) == 61 and line[:1] == b'Z' for line in lower)
    assert len(canonical(lower)) == len(lower)
    survivors = canonical(audit_shards(work, source, [f'd5/full.{index:02d}' for index in range(32)], 'inner'))
    assert len(survivors) == 118 and b''.join(survivors) == (work / 'd5/survivors.g6').read_bytes()

    frozen = work / 'd5/full_e130.can.g6'
    graphs = frozen.read_bytes().splitlines(keepends=True)
    for variant, raw_count in (('', 989), ('.audit', 1446)):
        produced = (work / f'd5/full_e130{variant}.g6').read_bytes().splitlines(keepends=True)
        assert len(produced) == raw_count and canonical(produced) == graphs
    counts = Counter()
    for row in graphs:
        adj = graph.parse_graph6(row.decode().strip())
        degrees = tuple(map(int.bit_count, adj))
        assert len(adj) == 33 and min(degrees) == 5 and max(degrees) <= 8
        assert graph.triangle_free(adj) and graph.alpha(adj) == 8
        counts[sum(degrees) // 2] += 1
    assert len(graphs) == 984 and counts == LEVELS
    print('exact degree-five levels:', sorted(counts.items()))
    assert not audit_shards(work, frozen, [f'd6/full.{index}' for index in range(8)], 'outer')
    if check_lrat:
        actual = sorted((work / 'd5/cap122').glob('*.sha256'))
        assert len(actual) == len(survivors)
        for index, (row, manifest) in enumerate(zip(survivors, actual), 1):
            stem = f'd5/cap122/{index:04d}'
            assert manifest.relative_to(work).as_posix() == stem + '.sha256'
            assert (work / f'{stem}.g6').read_bytes() == row
            assert verify_manifest(work, manifest) == {
                f'{stem}.{extension}' for extension in ('g6', 'cnf', 'lrat', 'verify', 'cake')}
            assert '\nc VERIFIED\n' in (work / f'{stem}.verify').read_text()
            assert 's VERIFIED UNSAT\n' in (work / f'{stem}.cake').read_text()
        print('118 cap122 fixed-core inputs, DIMACS, proofs, and both verdicts bound by SHA-256')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path)
    parser.add_argument('--lrat', action='store_true')
    args = parser.parse_args()
    audit(args.work.resolve(), args.lrat)
