"""Anti-join closed physical ranks to the frozen source and worker plans."""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--level', type=int, choices=(48, 49))
    parser.add_argument('--max5', action='store_true')
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--terminal', action='store_true')
    args = parser.parse_args()
    directory = args.directory
    rows = (directory / 'plan.tsv').read_text().splitlines()
    d3 = set((directory / 'd3.source.g6').read_text().splitlines())
    max5 = set((directory / 'e49.min4.max5.g6').read_text().splitlines()) if args.max5 else set()
    prefix = 'follow' if args.max5 else 'queue'
    denominator = {}
    for index, row in enumerate(rows, 1):
        rank, edge, mark, stem = row.split('\t')
        assert int(rank) == index and int(edge) in (48, 49)
        in_scope = stem in max5 if args.max5 else (int(edge) == 48 or stem in d3)
        if in_scope:
            denominator[index] = (int(edge), mark, stem)
    plans = {}
    terminal = {}
    cpu = 0.0
    receipts = []
    for slot in (0, 1):
        for row in (directory / f'{prefix}.{slot}.tsv').read_text().splitlines():
            rank, edge, mark, stem = row.split('\t')
            index = int(rank)
            assert index % 2 == slot and index not in plans
            plans[index] = (int(edge), mark, stem)
        complete_lines = (directory / f'{prefix}.{slot}.stdout').read_text().split('\n')[:-1]
        for row in complete_lines:
            if not row[:1].isdigit():
                continue
            rank, edge, result, size, *_ = row.split('\t')
            index = int(rank)
            edge = int(edge)
            if args.level is not None and edge != args.level:
                continue
            assert index % 2 == slot and index not in terminal
            assert plans[index][0] == edge
            terminal[index] = result in ('DUAL', 'ADOPT')
            if not terminal[index]:
                assert result.startswith('OPEN:')
                continue
            job = directory / 'normalized' / rank
            assert (job / 'stem.g6').read_text() == plans[index][2] + '\n'
            assert (job / 'marked').read_text() == plans[index][1] + '\n'
            proof = job / 'lift.lrat.xz'
            proof_bytes = proof.read_bytes()
            digest = hashlib.sha256(proof_bytes).hexdigest()
            assert len(proof_bytes) == int(size)
            assert (job / 'archive.sha256').read_text().split() == [digest, str(proof)]
            cnf, uncompressed = [line.split()[0] for line in (job / 'uncompressed.sha256').read_text().splitlines()]
            assert all(re.fullmatch(r'[0-9a-f]{64}', value) for value in (cnf, uncompressed))
            assert 's VERIFIED UNSAT' in (job / 'cake.log').read_text().splitlines()
            assert 'c VERIFIED' in (job / 'lrat.log').read_text().splitlines()
            assert (job / 'job.stdout').read_text().strip() == f'DUAL depth={(job / "depth").read_text().strip()} bytes={size} profile=xz'
            seconds = 0.0
            for time_log in job.glob('*.time'):
                timing = re.search(r'cpu=([0-9.]+)\+([0-9.]+)', time_log.read_text())
                assert timing is not None
                seconds += float(timing[1]) + float(timing[2])
            cpu += seconds
            receipts.append((index, edge, plans[index][1], plans[index][2], size,
                             digest, cnf, uncompressed, seconds))
    assert denominator == plans
    wanted = {rank for rank, (edge, _, _) in denominator.items() if args.level in (None, edge)}
    closed = {rank for rank, done in terminal.items() if done}
    assert closed <= wanted
    status = dict(planned=dict(Counter(denominator[rank][0] for rank in wanted)),
                  dual=dict(Counter(denominator[rank][0] for rank in closed)),
                  attempted_open=sorted(rank for rank in terminal if rank not in closed),
                  not_yet_logged=len(wanted - terminal.keys()),
                  proof_bytes=sum(int(row[4]) for row in receipts),
                  completed_stage_cpu_s=round(cpu, 2))
    print(json.dumps(status, sort_keys=True))
    if args.terminal:
        assert closed == wanted
    if args.freeze:
        with args.freeze.open('x') as stream:
            for row in sorted(receipts):
                print(*row, sep='\t', file=stream)


if __name__ == '__main__':
    main()
