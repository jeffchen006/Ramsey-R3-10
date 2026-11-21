#!/usr/bin/env python3
import argparse
from hashlib import sha256
from pathlib import Path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read_batch(prefix, shards, cases):
    results = {}
    cpu = 0.
    for shard in range(shards):
        path = Path(f'{prefix}-{shard}.log')
        lines = path.read_text().splitlines()
        assert len(lines) > 3 and [line.split()[0] for line in lines[-3:]] == ['real', 'user', 'sys']
        cpu += sum(float(line.split()[1]) for line in lines[-2:])
        expected = list(range(shard, len(cases), shards))
        assert len(lines) - 3 == len(expected), (path, len(lines), len(expected))
        for index, line in zip(expected, lines[:-3]):
            fields = line.split('\t')
            assert len(fields) == 9 and int(fields[0]) == index and index not in results
            assert fields[4] == 'VERIFIED', (index, fields)
            assert fields[5] == sha256(cases[index].encode()).hexdigest()
            results[index] = fields[:8]
    assert set(results) == set(range(len(cases)))
    return results, cpu


def read_cnf_hashes(work, cases, indexed, check_proofs):
    keys = {f'pack-{index:05d}' for index in range(len(cases))}
    assert {path.stem for path in work.glob('*.cnf')} == keys
    assert not any(work.glob('*.model'))
    assert {path.stem for path in work.glob('*.lrat')} == (keys if check_proofs else set())
    for index, fields in indexed.items():
        base = work / f'pack-{index:05d}'
        assert digest(base.with_suffix('.cnf')) == fields[6], base
        if check_proofs:
            assert digest(base.with_suffix('.lrat')) == fields[7], base


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cases', type=Path)
    parser.add_argument('production', type=Path)
    parser.add_argument('replay', type=Path)
    parser.add_argument('index', type=Path)
    parser.add_argument('--shards', type=int, default=4)
    args = parser.parse_args()
    cases = args.cases.read_text().splitlines()
    assert cases and len(set(cases)) == len(cases)
    production, work_cpu = read_batch(args.production, args.shards, cases)
    replay, replay_cpu = read_batch(args.replay, args.shards, cases)
    assert production == replay
    read_cnf_hashes(args.production, cases, production, True)
    read_cnf_hashes(args.replay, cases, replay, False)
    with args.index.open('x') as stream:
        for index in range(len(cases)):
            stream.write('\t'.join(production[index]) + '\n')
    print(f'PASS exact {len(cases)} terminal verified rows, order/shards/retained hashes/replay matched; '
          f'production={work_cpu:.2f} CPU-s, replay={replay_cpu:.2f} CPU-s')
