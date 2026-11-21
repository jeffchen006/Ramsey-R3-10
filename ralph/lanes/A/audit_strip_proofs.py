#!/usr/bin/env python3
"""Bind supplied paired-window LRATs to the exact cover and check both binaries."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import subprocess
import sys

from audit_floor_covers import require
from audit_path_leaf import vertices
from residue_bundle import parse_graph6


ROOT = Path(__file__).resolve().parents[3]


def graph_pins(encoded, masks):
    graph = parse_graph6(encoded)
    require(len(graph) == 27, 'bad window order')
    slots = tuple(tuple(vertices(mask)) for mask in masks)
    require(not masks[0] & masks[1] and all(len(side) == 4 for side in slots), 'bad strips')
    x_vertices = sorted(set(range(27)) - set(slots[0]) - set(slots[1]))
    neighbor = {(left, right): bool(graph[left] >> right & 1) for left, right in combinations(range(27), 2)}

    def add(first, second, present):
        pair = tuple(sorted((first, second)))
        require(pair not in neighbor or neighbor[pair] == present, 'conflicting fixed pair')
        neighbor[pair] = present

    for index, strip in enumerate(slots):
        root, centre = 27 + index, 29 + index
        incident = set(strip) | {27 + (1 - index), centre}
        for other in set(range(40)) - {root}:
            add(root, other, other in incident)
        for other in set(range(40)) - {27, 28, centre}:
            add(centre, other, other in {31, 32, 33, *(range(34 + 3 * index, 37 + 3 * index))})
        actual = Counter(tuple(anchor for anchor in strip if graph[vertex] >> anchor & 1) for vertex in x_vertices)
        available = Counter({(anchor,): 4 for anchor in strip}) + Counter(combinations(strip, 2))
        require(not (actual - available), 'bad margin in source mark')
        gaps = sorted((available - actual).elements())
        require(len(gaps) == 3, 'bad number of peripheral gaps')
        for removed, contacts in zip(range(34 + 3 * (1 - index), 37 + 3 * (1 - index)), gaps, strict=True):
            for anchor in strip:
                add(anchor, removed, anchor in contacts)
    for left, right in combinations(range(31, 40), 2):
        if not (34 <= left < 37 <= right):
            add(left, right, False)
    edges = [set() for _ in range(40)]
    for (left, right), bit in neighbor.items():
        if bit:
            edges[left].add(right)
            edges[right].add(left)
    for left, right in combinations(range(40), 2):
        if edges[left] & edges[right] and (left, right) not in neighbor:
            neighbor[left, right] = False
    return neighbor


def verified(binary, cnf, proof):
    result = subprocess.run(['nice', '-n', '5', 'timeout', '-k', '2s', '35s', 'prlimit', '--cpu=25',
                             str(ROOT / 'opt/bin' / binary), str(cnf), str(proof)], capture_output=True)
    marker = {'cake_lpr': b's VERIFIED UNSAT', 'lrat-check': b'c VERIFIED'}[binary]
    return result.returncode == 0 and marker in result.stdout.splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('proofs', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('logs', type=Path, nargs='+')
    parser.add_argument('--sample', type=int, default=4)
    parser.add_argument('--alternate', type=Path)
    parser.add_argument('--require-cover', action='store_true')
    parser.add_argument('--bind-only', action='store_true')
    parser.add_argument('--shard', type=int, nargs=2, default=(0, 1))
    args = parser.parse_args()
    keys = {}
    for line in args.keys.read_text().splitlines():
        row, left, right, graph = line.split()
        key = '_'.join((row, left, right))
        require(key not in keys, 'duplicate input key')
        keys[key] = (graph, (int(left), int(right)))
    hashes = {}
    for path in args.logs:
        for line in path.read_text().splitlines():
            key, status, checksum, *tail = line.split()
            if status != 'CERT':
                continue
            require(key in keys and key not in hashes and len(tail) == 2, 'unbound or duplicate proof receipt')
            hashes[key] = (checksum, int(tail[0]))
    if args.require_cover:
        require(set(keys) == set(hashes), 'terminal proof receipts do not exactly cover the input')
    proof_roots = [args.proofs] + ([args.alternate] if args.alternate else [])
    proof_paths = {}
    for key, (_, size) in hashes.items():
        claims = [path / (key + '.lrat.gz') for path in proof_roots if (path / (key + '.lrat.gz')).is_file()]
        require(len(claims) == 1 and claims[0].stat().st_size == size, 'absent, ambiguous or wrong-size trace')
        proof_paths[key] = claims[0]
    if args.require_cover:
        observed_paths = {path for root in proof_roots for path in root.glob('*.lrat.gz')}
        require(observed_paths == set(proof_paths.values()), 'trace directories do not match the bound receipts')
    if args.bind_only:
        for key in sorted(hashes):
            print(key, *hashes[key], proof_paths[key], sep='\t')
        return
    selected = sorted(hashes)
    shard, count = args.shard
    require(0 <= args.sample <= len(selected) and 0 <= shard < count, 'invalid sample or shard')
    if args.sample:
        selected = [selected[index * len(selected) // args.sample] for index in range(args.sample)]
    selected = selected[shard::count]
    sys.path.insert(0, str(ROOT / 'ralph/lanes/G'))
    from strip_completion import window

    args.output.mkdir(parents=True, exist_ok=True)
    outputs = []
    for key in selected:
        encoded, masks = keys[key]
        fixed = graph_pins(encoded, masks)
        problem = window(encoded, *masks, 0, True)
        expected = {pair: 1 if state else -1 for pair, state in fixed.items()}
        require({pair: state for pair, state in problem.edge.items() if abs(state) == 1} == expected,
                'CNF edge pin set differs from independent reconstruction')
        cnf = args.output / (key + '.cnf')
        proof = args.output / (key + '.lrat')
        problem.formula.write(cnf)
        stored = proof_paths[key]
        actual = sha256(cnf.read_bytes()).hexdigest(), stored.stat().st_size
        require(actual == hashes[key], 'certificate receipt or reconstructed CNF differs')
        proof_bytes = stored.read_bytes()
        proof.write_bytes(gzip.decompress(proof_bytes))
        require(all(verified(binary, cnf, proof) for binary in ('cake_lpr', 'lrat-check')), 'failed proof replay')
        if args.sample:
            outputs.append((cnf, proof))
        else:
            cnf.unlink()
            proof.unlink()
        print(key, 'independent pins', len(fixed), 'dual LRAT OK', *actual, sha256(proof_bytes).hexdigest(), flush=True)
    if len(outputs) >= 2:
        require(not any(verified(binary, outputs[0][0], outputs[1][1]) for binary in ('cake_lpr', 'lrat-check')),
                'crossed proof was not rejected')
        print('crossed LRAT rejected by both checkers')


if __name__ == '__main__':
    main()
