#!/usr/bin/env python3
"""Independently rebind and dual-check marked-window addbacks."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess

from pysat.card import CardEnc, EncType


TOOLS = Path(__file__).resolve().parents[3] / 'opt' / 'bin'


def encode(key, word, raw_parts, witnesses):
    assert ord(key[0]) - 63 == 26
    packed = ''.join(f'{ord(char) - 63:06b}' for char in key[1:])
    known = {(left, right) for right in range(26) for left in range(right)
             if packed[right*(right-1)//2+left] == '1'}
    assert len(known) == 74
    all_sites = frozenset(range(32))
    core = frozenset(index for index in range(26) if word >> index & 1)
    groups = tuple(frozenset(index for index in range(26) if part >> index & 1) for part in raw_parts)
    assert len(core) == 8 and [len(part) for part in groups] == [6, 6, 6]
    assert set().union(core, *groups) == set(range(26))
    new_sites = all_sites - frozenset(range(26))
    rows = []
    top = 26*6

    def variable(left, right):
        return 1 + 6*left + right - 26

    def cap(literals, bound):
        nonlocal top
        if bound < 0:
            rows.append(())
        elif bound < len(literals):
            new = CardEnc.atmost(lits=list(literals), bound=bound, top_id=top, encoding=EncType.seqcounter)
            top = max(top, new.nv)
            rows.extend(new.clauses)

    for vertex in range(32):
        literals = ([variable(vertex, peer) for peer in range(26, 32)] if vertex < 26
                    else [variable(peer, vertex) for peer in range(26)])
        residual = (8 if vertex in core else 7) - sum(vertex in edge for edge in known)
        cap(literals, residual)
        cap([-literal for literal in literals], len(literals)-residual)
    for first, second in sorted(known):
        for peer in range(26, 32):
            rows.append((-variable(first, peer), -variable(second, peer)))
    for vertex in sorted(core):
        rows.append(tuple(variable(vertex, peer) for peer in range(26, 32)))
    domains = [(all_sites - part, 8) for part in groups] + [(all_sites, 10), (core | new_sites, 7), (core, 6)]
    blocked = set()
    for region, pick in witnesses:
        which, order = domains[region]
        sites = {vertex for vertex in range(32) if pick >> vertex & 1}
        assert 0 <= pick < 1 << 32 and len(sites) == order and sites <= which
        assert not any(set(edge) <= sites for edge in known)
        clause = tuple(variable(left, right) for left, right in combinations(sorted(sites), 2) if left < 26 <= right)
        assert clause not in blocked
        blocked.add(clause)
        rows.append(clause)
    return (f'p cnf {top} {len(rows)}\n' + ''.join(' '.join(map(str, (*clause, 0)))+'\n' for clause in rows)).encode('ascii')


def replay(plan, directories, offset, stride, work):
    wanted = [json.loads(line) for line in plan.open(encoding='ascii')]
    terminal = {}
    for subtree in directories:
        for stream in subtree.glob('worker.*.jsonl'):
            for row in map(json.loads, stream.open(encoding='ascii')):
                key = row[0]
                assert 0 <= key < len(wanted) and key not in terminal
                directory = subtree/f'{key:05d}'
                assert directory.is_dir()
                terminal[key] = directory, row
    assert sorted(terminal) == list(range(len(wanted)))
    work.mkdir(exist_ok=True)
    cnf, proof = work/f'{offset}.cnf', work/f'{offset}.lrat'
    stats = Counter()
    with (work/f'{offset}.jsonl').open('x', encoding='ascii', buffering=1) as log:
        for index in range(offset, len(wanted), stride):
            _, label, core, parts = wanted[index]
            directory, record = terminal[index]
            _, status, cnf_hash, proof_hash, size, count, _ = record
            stats[status] += 1
            if status == 'CHECKED':
                witnesses = json.loads((directory/'witnesses.json').read_bytes())
                assert len(witnesses) == count
                raw_cnf = encode(label, core, parts, witnesses)
                raw_proof = gzip.decompress((directory/'proof.lrat.gz').read_bytes())
                assert sha256(raw_cnf).hexdigest() == cnf_hash
                assert sha256(raw_proof).hexdigest() == proof_hash and len(raw_proof) == size
                cnf.write_bytes(raw_cnf)
                proof.write_bytes(raw_proof)
                for tool, flags, marker in (('cake_lpr', ('--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=64'), b's VERIFIED UNSAT'),
                                            ('lrat-check', (), b'c VERIFIED')):
                    result = subprocess.run(['timeout', '-k', '2s', '30s', 'prlimit', '--cpu=10:11', '--', str(TOOLS/tool),
                                             *flags, str(cnf), str(proof)], capture_output=True, check=False)
                    assert result.returncode == 0 and marker in {line.rstrip() for line in result.stdout.splitlines()}
                cnf.unlink()
                proof.unlink()
            print(json.dumps(record), file=log)
    print('fresh dual check / bound IDs', offset, stride, dict(stats), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('directories', nargs='+', type=Path)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args()
    replay(args.plan, args.directories, args.offset, args.stride, args.work)
