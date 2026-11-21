"""Replay the P5 packing refutation without importing the proof producer."""

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from kernel_projection import bits, decode


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def independent_sets(adj, variants, size):
    if size == 0:
        yield 0
    elif variants.bit_count() >= size:
        vertex = max(bits(variants), key=lambda index: (adj[index] & variants).bit_count())
        rest = variants ^ (1 << vertex)
        yield from independent_sets(adj, rest, size)
        for chosen in independent_sets(adj, rest & ~adj[vertex], size - 1):
            yield chosen | (1 << vertex)


def replay(line, record):
    require(isinstance(record, list) and len(record) == 4, 'wrong record structure')
    digest, reason, witness, program = record
    require(digest == sha256(line.encode()).hexdigest(), 'wrong input hash')
    require(isinstance(witness, list) and isinstance(program, list), 'bad trace types')
    adj = decode(line)
    order = len(adj)
    require(order == 30, 'wrong residue order')
    full = (1 << order) - 1
    rootmask = 15 << (order - 4)
    requirements = [3, 3, 3] + [9 - mask.bit_count() for mask in adj]
    relevant = []
    for group in range(3):
        left = order - 4 + group
        roots = 3 << left
        require(not adj[left] >> (left + 1) & 1, 'adjacent compulsory roots')
        rest = full & ~(rootmask | adj[left] | adj[left + 1])
        for free in sorted(independent_sets(adj, rest, 6), key=lambda mask: tuple(bits(mask))):
            full_mask = free | roots
            if all((mask & full_mask).bit_count() <= 6 for mask in adj):
                relevant.append((group, full_mask))
    domains = [0] * (order + 3)
    for index, (group, mask) in enumerate(relevant):
        domains[group] |= 1 << index
        for vertex in bits(mask):
            domains[vertex + 3] |= 1 << index

    def missing_pair(left, right):
        return not (adj[left] >> right & 1 or adj[left] & adj[right])

    if reason == 'load':
        require(not program and len(witness) == 1, 'invalid load record')
        vertex = witness[0]
        require(type(vertex) is int and 0 <= vertex < order, 'invalid vertex')
        capacity = sum(min(3, (domains[group] & domains[vertex + 3]).bit_count()) for group in range(3))
        require(capacity < requirements[vertex + 3], 'load is not short')
        return 0
    if reason == 'mtf':
        require(not program and len(witness) == 2, 'invalid pair record')
        left, right = witness
        require(type(left) is int and type(right) is int and 0 <= left < right < order, 'invalid pair')
        require(missing_pair(left, right), 'pair does not require a witness')
        require(not domains[left + 3] & domains[right + 3], 'pair actually has an eligible witness')
        return 0
    require(reason == 'tree' and not witness, 'unknown trace category')

    for left, right in combinations(range(order), 2):
        if missing_pair(left, right):
            domains.append(domains[left + 3] & domains[right + 3])
            requirements.append(1)
    row_for_mask = [[] for _ in relevant]
    for row, domain in enumerate(domains):
        for chosen in bits(domain):
            row_for_mask[chosen].append(row)

    witnesses = list(independent_sets(adj, full, 8))
    misses = [sum(1 << idx for idx, candidate in enumerate(witnesses) if not candidate & mask)
              for _, mask in relevant]
    excludes = [0] * len(relevant)
    for first, second in combinations(range(len(relevant)), 2):
        if ((relevant[first][1] & relevant[second][1]).bit_count() >= 6 or
                misses[first] & misses[second]):
            excludes[first] |= 1 << second
            excludes[second] |= 1 << first
    stream = iter(program)
    end_of_stream = object()
    count = 0

    def visit(remaining, balance, depth):
        nonlocal count
        require(depth < 9, 'trace encountered a complete packing')
        token = next(stream, end_of_stream)
        require(type(token) is int, 'missing or invalid proof node')
        count += 1
        row = token if token >= 0 else -token - 1
        require(0 <= row < len(domains) and balance[row] > 0, 'invalid active row')
        domain = domains[row] & remaining
        if token < 0:
            require(domain.bit_count() < balance[row], 'forged shortage leaf')
            return
        require(domain != 0, 'empty support used as a branch')
        for chosen in bits(domain):
            remaining ^= 1 << chosen
            revised = remaining & ~excludes[chosen]
            needs = list(balance)
            for charged in row_for_mask[chosen]:
                if charged < order + 3:
                    require(needs[charged] > 0, 'overspent exact quota')
                    needs[charged] -= 1
                    if needs[charged] == 0:
                        revised &= ~domains[charged]
                else:
                    needs[charged] = 0
            visit(revised, needs, depth + 1)

    visit((1 << len(relevant)) - 1, requirements, 0)
    require(next(stream, end_of_stream) is end_of_stream, 'trailing proof nodes')
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cover', type=Path)
    parser.add_argument('trace', type=Path)
    args = parser.parse_args()
    start = time.process_time()
    lines = args.cover.read_text().splitlines()
    records = args.trace.read_text().splitlines()
    require(bool(lines) and len(lines) == len(records), 'empty input or missing records')
    nodes = 0
    for index, (line, record) in enumerate(zip(lines, records)):
        try:
            nodes += replay(line, json.loads(record))
        except ValueError as exc:
            raise SystemExit(f'REJECTED at row {index}: {exc}') from exc
    print(f'VERIFIED {len(lines)} supplied residues, {nodes} trace nodes, CPU-s {time.process_time() - start:.3f}')


if __name__ == '__main__':
    main()
