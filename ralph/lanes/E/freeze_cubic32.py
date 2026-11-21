#!/usr/bin/env python3
"""Freeze the exact expected CNF, proof, and checker log bindings."""

from hashlib import sha256
from pathlib import Path
import re
import sys


def main():
    prefix, count = sys.argv[1], int(sys.argv[2])
    manifest = Path('windows.jsonl')
    assert len(manifest.read_bytes().splitlines()) == count
    cpu = [0.0] * 3
    sizes = {'cnf': 0, 'lrat': 0}
    rows = [(sha256(manifest.read_bytes()).hexdigest(), manifest)]
    for index in range(count):
        base = f'{prefix}.{index}'
        cnf, proof, check = (Path(base + suffix) for suffix in ('.cnf', '.lrat', '.lrat.log'))
        assert 's VERIFIED UNSAT' in check.read_text().splitlines(), index
        if not proof.stat().st_size:
            assert b'0' in cnf.read_bytes().splitlines()[1:], index
        assert 'CHECKED_UNSAT' in Path(base + '.log').read_text().splitlines(), index
        for artifact in (cnf, proof, check):
            rows.append((sha256(artifact.read_bytes()).hexdigest(), artifact))
            if artifact.suffix[1:] in sizes:
                sizes[artifact.suffix[1:]] += artifact.stat().st_size
        for column, suffix in enumerate(('.log', '.solve.log', '.lrat.log')):
            timings = re.findall(r'cpu=(\d+\.\d+)\+(\d+\.\d+)', Path(base + suffix).read_text())
            assert len(timings) == 1, (index, suffix, timings)
            cpu[column] += sum(map(float, timings[0]))
    bundle = ''.join(f'{digest}  {artifact}\n' for digest, artifact in rows).encode('ascii')
    Path('certificates.sha256').write_bytes(bundle)
    print('checked', count, 'CPU seconds (encode, solve, check)', [round(value, 2) for value in cpu],
          'core hours', round(sum(cpu) / 3600, 4), 'bytes', sizes)
    print('bundle index SHA-256', sha256(bundle).hexdigest())


if __name__ == '__main__':
    main()
