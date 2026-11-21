"""Small census for the eight-cycle necessary seed constraints."""

import argparse
from collections import Counter
from pathlib import Path

from kernel_projection import bits, decode, encode, independent_masks
from pair_packages import restrict


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census')
    parser.add_argument('--output')
    args = parser.parse_args()
    census_edges = Counter()
    surviving_edges = Counter()
    all_masks = 0
    output = []
    for index, line in enumerate(Path(args.census).read_text().splitlines()):
        adj = decode(line)
        assert len(adj) == 22
        assert all(not adj[left] & adj[right] for left in range(22) for right in bits(adj[left]))
        census_edges[sum(mask.bit_count() for mask in adj) // 2] += 1
        full = (1 << len(adj)) - 1
        for mask in independent_masks(adj, full):
            size = mask.bit_count()
            assert size <= 6
            if size != 6:
                continue
            all_masks += 1
            complement = full ^ mask
            degrees = [(adj[vertex] & complement).bit_count() for vertex in bits(complement)]
            edges = sum(degrees) // 2
            if not (24 <= edges <= 32 and max(degrees) <= 4):
                continue
            spend = sum(6 - adj[vertex].bit_count() for vertex in bits(mask))
            if spend > 2 * (edges - 24):
                continue
            surviving_edges[edges] += 1
            graph = encode(restrict(adj, list(bits(complement))))
            output.append(f'{index}\t{mask}\t{graph}')
    assert sum(census_edges.values()) == 191
    print('22-census by edges:', sorted(census_edges.items()), 'independent 6-sets:', all_masks)
    print('eligible sets by e(X):', sorted(surviving_edges.items()))
    print('22-seeds with eligible sets:', len({line.split('\t')[0] for line in output}))
    if args.output:
        Path(args.output).write_text(''.join(line + '\n' for line in output))


if __name__ == '__main__':
    main()
