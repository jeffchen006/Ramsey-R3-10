#!/usr/bin/env python3
"""Bounded, matched proof pilot for pinned noncross equality anchors."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip

from pinned_anchor_window import independent_core, instance, roles, select_rows, unpack
from prove_strip_windows import BIN, bounded, verify


def select(source, degree, parents, count):
    selected = []
    for row in select_rows(source, 0, None, parents):
        row_id, adj, small, large = unpack(row)
        for role in roles(adj, small, large, degree):
            orientation, _, _, _, _, shape, hole, peer_hole = role
            key = '_'.join(map(str, (row_id, *row.split()[1:3], degree, orientation, shape, *hole, *peer_hole)))
            selected.append((key, adj, small, large, role))
    if count:
        assert count <= len(selected)
        return [selected[index * len(selected) // count] for index in range(count)]
    return selected


def run_key(item, args):
    key, adj, small, large, role = item
    out = args.output / key
    cnf = out.with_suffix('.cnf')
    proof = out.with_suffix('.lrat')
    stored = out.with_suffix('.lrat.gz')
    start = monotonic()
    try:
        problem = instance(adj, small, large, args.degree, role, independent_core(adj, 6),
                           eager=True, sorted_slots=True)
        problem.formula.write(cnf)
        if args.replay:
            proof.write_bytes(gzip.decompress(stored.read_bytes()))
        else:
            answer = bounded([BIN / 'cadical', '-q', '-n', '--lrat', '--no-binary',
                              '-c', args.conflicts, cnf, proof], args.cpu)
            if answer.returncode != 20:
                status = {0: 'CAP', 10: 'RELAXED_SAT', 124: 'TIMEOUT', 137: 'SIGNAL', 152: 'CPU_CAP',
                          -24: 'CPU_CAP'}.get(answer.returncode, 'ERROR')
                if status == 'ERROR':
                    raise RuntimeError((answer.returncode, answer.stdout, answer.stderr))
                print(key, status, 'elapsed', f'{monotonic()-start:.3f}', flush=True)
                return
            assert b's UNSATISFIABLE' in answer.stdout.splitlines()
        verify(cnf, proof)
        if not args.replay:
            stored.write_bytes(gzip.compress(proof.read_bytes(), compresslevel=1, mtime=0))
        cnf_digest = sha256(cnf.read_bytes()).hexdigest()
        stored_bytes = stored.read_bytes()
        print(key, 'REPLAY' if args.replay else 'CERT', cnf_digest, sha256(stored_bytes).hexdigest(), len(stored_bytes),
              'elapsed', f'{monotonic()-start:.3f}', flush=True)
    finally:
        cnf.unlink(missing_ok=True)
        proof.unlink(missing_ok=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--degree', type=int, choices=(8, 9), required=True)
    parser.add_argument('--parents', type=int)
    parser.add_argument('--count', type=int)
    parser.add_argument('--cpu', type=int, default=16)
    parser.add_argument('--conflicts', type=int, default=50000)
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--shard', nargs=2, type=int, default=(0, 1))
    args = parser.parse_args()
    if not args.parents and not args.count:
        parser.error('explicitly select either --parents or --count')
    selected = select(args.source, args.degree, args.parents, args.count)
    args.output.mkdir(parents=True, exist_ok=True)
    shard, jobs = args.shard
    assert 0 <= shard < jobs
    for item in selected[shard::jobs]:
        if not args.replay or (args.output / (item[0] + '.lrat.gz')).is_file():
            run_key(item, args)


if __name__ == '__main__':
    main()
