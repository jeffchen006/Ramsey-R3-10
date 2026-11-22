"""Calibrate one-edge descent, and inventory (not generate) target inputs."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from itertools import combinations, islice
import json
import lzma
from pathlib import Path
import subprocess

from critical_witness import independent, parse_graph6, triangle_free, witness
from check_graph import to_graph6


def size(rows):
    return sum(row.bit_count() for row in rows) // 2


def pairs(rows):
    return combinations(range(len(rows)), 2)


def available(rows):
    return [(left, right) for left, right in pairs(rows)
            if not ((rows[left] >> right) & 1 or rows[left] & rows[right])]


def run_graph_tool(executable, args, inputs):
    data = ''.join(f'{key}\n' for key in inputs).encode()
    result = subprocess.run(['timeout', '20s', executable, *args], input=data,
                            capture_output=True, check=True)
    return result.stdout.decode().splitlines()


def canonical(keys):
    result = run_graph_tool('../../opt/bin/labelg', ['-q'], keys)
    assert len(keys) == len(result)
    return result


def down(parents, forbidden):
    marked = []
    for parent in parents:
        rows = parse_graph6(parent)
        universe = (1 << len(rows)) - 1
        for left, right in pairs(rows):
            if not ((rows[left] >> right) & 1):
                continue
            outside = universe & ~(rows[left] | rows[right])
            if independent(rows, outside, forbidden - 2) is not None:
                continue
            rows[left] ^= 1 << right
            rows[right] ^= 1 << left
            key = to_graph6(rows)
            if witness(key, forbidden) is not None:
                marked.append((key, parent))
            rows[left] ^= 1 << right
            rows[right] ^= 1 << left
    provenance = defaultdict(set)
    for key, (_, parent) in zip(canonical([key for key, _ in marked]), marked, strict=True):
        provenance[key].add(parent)
    return provenance, len(marked)


def small_control(out):
    catalogue = Path('val/r3_6_16.g6').read_text().splitlines()
    assert len(set(canonical(catalogue))) == len(catalogue) == 2576
    sizes = [(size(parse_graph6(key)), key) for key in catalogue]
    parents = [key for edges, key in sizes if edges == 34]
    assert len(parents) == 200
    recovered, raw = down(parents, 6)
    target = [key for edges, key in sizes if edges == 33]
    assert len(target) == 39
    withheld = set(canonical(run_graph_tool('build/irreducible', ['6'], target)))
    assert len(withheld) == 13
    addable = {key for key in withheld if available(parse_graph6(key))}
    saturated = withheld - addable
    assert set(recovered) == addable
    print(f'complete (3,6;16): {len(catalogue)}; e34={len(parents)}, e33={len(target)}; '
          f'{len(withheld)} withheld criticals; {raw} labelled critical deletions; '
          f'{len(recovered)} recovered unique, {len(saturated)} unrecovered saturated, 0 extras')
    chosen = min(addable, key=lambda key: (len(recovered[key]), key))
    dropped = recovered[chosen]
    missing, _ = down([key for key in parents if key not in dropped], 6)
    assert chosen not in missing and chosen in addable and missing.keys() <= addable
    print(f'incomplete-source control: removed {len(dropped)} parents of one addable key; '
          f'{len(addable - missing.keys())} addable keys then unrecovered, including that key')

    roster = defaultdict(list)
    for mask in range(1 << 10):
        rows = [0] * 5
        for index, (left, right) in enumerate(pairs(rows)):
            if mask >> index & 1:
                rows[left] |= 1 << right
                rows[right] |= 1 << left
        if triangle_free(rows) and independent(rows, 31, 3) is None:
            roster[mask.bit_count()].append(to_graph6(rows))
    saturated = set(canonical(roster[5]))
    assert len(saturated) == 1 and not roster[6]
    key, = saturated
    assert not available(parse_graph6(key)) and witness(key, 3) is not None
    assert not down(roster[6], 3)[0]
    print(f'saturated control (3,3;5): {len(roster[5])} labelled e5 graphs, '
          '1 withheld critical C5, 0 recovered, 1 saturated not recoverable')
    (out / 'small-recovered.g6').write_text(''.join(f'{key}\n' for key in sorted(recovered)))
    (out / 'small-withheld.g6').write_text(''.join(f'{key}\n' for key in sorted(withheld)))


def target_addability(out):
    source = Path('work/e108_r11/critical.g6').read_bytes()
    assert sha256(source).hexdigest() == '2a499d1abf447b2ef98d749e8a19c8d1a3564b052d8ad153415ac48756f1dd17'
    count = Counter()
    with (out / 'known-critical-addability.tsv').open('w') as result:
        result.write('key\taddable_pairs\tfirst_pair\n')
        for key in source.decode().splitlines():
            rows = parse_graph6(key)
            assert len(rows) == 32 and size(rows) == 108 and triangle_free(rows)
            additions = available(rows)
            count[len(additions)] += 1
            pair = ','.join(map(str, additions[0])) if additions else '-'
            result.write(f'{key}\t{len(additions)}\t{pair}\n')
    assert sum(count.values()) == 1875
    print(json.dumps({'supplied_addable': 1875 - count[0], 'supplied_saturated': count[0],
                      'addable_pairs_histogram': count}, sort_keys=True))


def sniff(path):
    if path.suffix in ('.gz', '.xz'):
        open_func = gzip.open if path.suffix == '.gz' else lzma.open
        with open_func(path, 'rb') as stream:
            return list(islice(stream, 8))
    with path.open('rb') as stream:
        length = path.stat().st_size
        samples = []
        for position in sorted({0, length // 2, max(0, length - 2048)}):
            stream.seek(position)
            if position:
                stream.readline(1024)
            samples.extend(islice(stream, 8))
    return samples


def inventory(paths, out):
    counts = Counter()
    with (out / 'source-screen.tsv').open('w') as result:
        result.write('status\tobserved_order32_edge_counts\tpath\n')
        for name in sorted(set(paths.read_text().splitlines())):
            path = Path(name)
            edges = set()
            status = 'OK'
            try:
                samples = sniff(path)
                for row in samples:
                    row = row.strip().removeprefix(b'>>graph6<<')
                    if row[:1] == b'_' and len(row) == 84:
                        edges.add(size(parse_graph6(row.decode())))
                    elif row.removeprefix(b'>>sparse6<<')[:2] == b':_':
                        status = 'ORDER32_SPARSE6'
            except (OSError, EOFError, ValueError) as error:
                status = f'UNREADABLE:{type(error).__name__}'
            counts['examined'] += 1
            if edges:
                counts['g6_order32_observed'] += 1
            if 109 in edges:
                counts['g6_e109_observed'] += 1
            if status != 'OK':
                counts[status] += 1
            result.write(f'{status}\t{",".join(map(str, sorted(edges)))}\t{name}\n')
    print(json.dumps(dict(counts), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('inventory', 'control'))
    parser.add_argument('out', type=Path)
    parser.add_argument('--paths', type=Path)
    args = parser.parse_args()
    if args.mode == 'inventory':
        inventory(args.paths, args.out)
    else:
        small_control(args.out)
        target_addability(args.out)
