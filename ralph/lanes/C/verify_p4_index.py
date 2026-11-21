"""Independent audit of the P4 Y--Z filter, proof bindings and pattern cover."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path


def graph_edges(graph):
    order = ord(graph[0]) - 63
    pairs = [(left, right) for right in range(order) for left in range(right)]
    digits = [ord(letter) - 63 for letter in graph[1:]]
    if order != 26 or len(digits) != (len(pairs) + 5) // 6 or not all(0 <= digit < 64 for digit in digits):
        raise ValueError('malformed graph6')
    raw = [bool(value & (1 << shift)) for value in digits for shift in range(5, -1, -1)]
    if any(raw[len(pairs):]):
        raise ValueError('nonzero graph6 padding')
    return {edge for edge, present in zip(pairs, raw) if present}


def passes(edges):
    return all(((left, right) in edges) == (not any((vertex, left) in edges and (vertex, right) in edges
                                                    for vertex in range(20)))
               for left in (20, 21) for right in (22, 23))


@lru_cache(maxsize=None)
def patterns(edge_count):
    output = set()
    for positions in combinations(range(9), edge_count):
        chosen = set(positions)
        images = []
        for cols in permutations(range(3)):
            row_values = [sum(1 << offset for offset, col in enumerate(cols) if row * 3 + col in chosen)
                          for row in range(3)]
            images.append(sum(value << (index * 3)
                              for index, value in enumerate(sorted(row_values, reverse=True))))
        output.add(f'p{min(images):03d}')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('unfiltered', type=Path)
    parser.add_argument('filtered', type=Path)
    parser.add_argument('--high', type=Path)
    parser.add_argument('--low', type=Path)
    parser.add_argument('--index', type=Path)
    args = parser.parse_args()
    original = args.unfiltered.read_text().splitlines()
    filtered = args.filtered.read_text().splitlines()
    if len(original) != len(set(original)) or len(original) != 2454:
        raise ValueError('invalid cover size or duplicate')
    if [row for row in original if passes(graph_edges(row))] != filtered:
        raise ValueError('forced Y--Z filter mismatch')
    print('FILTER', len(original), len(filtered), flush=True)
    records = defaultdict(dict)
    edge_counts = [len(graph_edges(row)) for row in filtered]
    for folder in (args.high, args.low):
        if folder is None:
            continue
        log_files = sorted(folder.parent.glob(folder.name + '-*.log'))
        if len(log_files) != 4:
            raise ValueError(f'expected four logs for {folder}')
        logged_files = set()
        claimed_rows = set()
        for log in log_files:
            lines = log.read_text().splitlines()
            if not lines or not lines[-1].startswith('TERMINAL '):
                raise ValueError(f'incomplete {log}')
            for line in lines:
                fields = line.split()
                if len(fields) < 10 or fields[0] != 'row' or fields[4] != 'checked':
                    continue
                _, number, label, edge_text, _, key, row_hash, cnf_hash, proof_hash, size, *_ = fields
                index = int(number)
                if label != 'e' or not 0 <= index < len(filtered) or key in records[index]:
                    raise ValueError(f'invalid or duplicate record: {line}')
                edges = edge_counts[index]
                if row_hash != sha256(filtered[index].encode()).hexdigest() or edges != int(edge_text):
                    raise ValueError(f'row hash/count mismatch: {index}')
                proof = folder / f'{index:04d}-{key}.lrat'
                contents = proof.read_bytes()
                if len(contents) != int(size) or sha256(contents).hexdigest() != proof_hash:
                    raise ValueError(f'proof hash mismatch: {proof}')
                if folder == args.high and (edges < 79 or key not in {'0', '1', '01'}):
                    raise ValueError(f'wrong high stratum: {line}')
                if folder == args.low and (edges > 78 or key not in patterns(edges - 72)):
                    raise ValueError(f'wrong low pattern: {line}')
                claimed_rows.add(index)
                logged_files.add(proof)
                records[index][key] = (edges, row_hash, cnf_hash, proof_hash, str(proof))
        if logged_files != set(folder.glob('*.lrat')):
            raise ValueError(f'unindexed proof files: {folder}')
        print('INDEXED', str(folder), len(claimed_rows), len(logged_files), flush=True)
    counts = Counter()
    missing = []
    for index, edge_count in enumerate(edge_counts):
        if edge_count >= 79:
            if args.high is None:
                continue
            if len(records[index]) > 1:
                raise ValueError(f'not one high record for {index}')
            solved = bool(records[index])
        else:
            if args.low is None:
                continue
            solved = set(records[index]) == patterns(edge_count - 72)
        counts[edge_count, solved] += 1
        if not solved:
            missing.append(index)
    if args.index:
        with args.index.open('w') as out:
            for index, evidence in sorted(records.items()):
                for key, (edges, row_hash, cnf_hash, proof_hash, name) in sorted(evidence.items()):
                    print(index, edges, key, row_hash, cnf_hash, proof_hash, name, sep='\t', file=out)
    print('ROWS', sorted(counts.items()), 'missing', missing, flush=True)
    if missing:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
