"""Bind P3 diagonal-five/e64 checked proofs to exact census row keys."""

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path


def core_edge_count(line):
    order = ord(line[0]) - 63
    digits = [ord(letter) - 63 for letter in line[1:]]
    if order != 22 or len(digits) != 39 or not all(0 <= digit < 64 for digit in digits) or digits[-1] & 7:
        raise ValueError('malformed order-22 graph6 row')
    return sum(digit.bit_count() for digit in digits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = args.catalogue.read_text().splitlines()
    if len(rows) != len(set(rows)) or len(rows) != 191:
        raise ValueError('wrong census row set size')
    inputs = {index: sha256(line.encode()).hexdigest() for index, line in enumerate(rows)
              if core_edge_count(line) == 64}
    if len(inputs) != 59:
        raise ValueError('wrong e64 census size')
    records = {}
    cap_rows = set()
    for path, folder in [(Path('p3_e64_proofcal.log'), Path('p3e64-proofcal'))] + [
            (Path(f'p3e64-full-{shard}.log'), Path('p3e64-full')) for shard in range(4)]:
        logs = path.read_text().splitlines()
        if not logs or not logs[-1].startswith('TERMINAL '):
            raise ValueError(f'not completed: {path}')
        for line in logs:
            words = line.split()
            if not words or words[0] != 'row':
                continue
            index = int(words[1])
            status = words[2]
            if index not in inputs or index in records or index in cap_rows:
                raise ValueError(f'unexpected/duplicate row {index}')
            if status == 'wall-cap':
                cap_rows.add(index)
                continue
            if status != 'checked':
                raise ValueError(f'unexpected status: {line}')
            _, _, _, row_hash, cnf_hash, proof_hash, length, *_ = words
            if row_hash != inputs[index]:
                raise ValueError(f'wrong row hash: {index}')
            proof = folder / f'{index:03d}.lrat'
            if int(length) != proof.stat().st_size:
                raise ValueError(f'wrong proof length: {index}')
            with proof.open('rb') as contents:
                if sha256(contents.read()).hexdigest() != proof_hash:
                    raise ValueError(f'wrong proof hash: {index}')
            records[index] = (row_hash, cnf_hash, proof_hash, str(proof))
    uncovered = sorted(set(inputs) - records.keys())
    if set(uncovered) != cap_rows:
        raise ValueError('unreported missing rows')
    for folder, proper_count in [('p3e64-proofcal', 3), ('p3e64-full', 56 - len(cap_rows))]:
        paths = {str(path) for path in Path(folder).glob('*.lrat')}
        expected = {record[-1] for record in records.values() if record[-1].startswith(folder + '/')}
        if paths != expected or len(paths) != proper_count:
            raise ValueError(f'unindexed/missing proofs: {folder}')
    if args.output:
        with args.output.open('w') as stream:
            for index, record in sorted(records.items()):
                print(index, *record, sep='\t', file=stream)
    print('expected', len(inputs), 'checked', len(records), 'caps', sorted(cap_rows), flush=True)
    if uncovered:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
