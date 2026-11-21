"""Exact calibration of path algebra on C21(1,4,6) and the order-22 census."""

import argparse
from itertools import combinations
from pathlib import Path

from kernel_projection import MAX_ORDER, bits, decode, independent_masks


def find_path_blocks(adj, vertices, block_size):
    neighborhoods = [adj[vertex] for vertex in vertices]
    count = len(vertices)
    block = {index: neighborhoods[index - 1] & neighborhoods[index + 1] for index in range(1, count - 1)}
    block[0] = neighborhoods[1] & ~(block[1] | block[2])
    block[-1] = neighborhoods[0] & ~(block[0] | block[1])
    block[count - 1] = neighborhoods[-2] & ~(block[count - 3] | block[count - 2])
    block[count] = neighborhoods[-1] & ~(block[count - 2] | block[count - 1])
    for index in range(count):
        parts = [block[idx] for idx in range(index - 1, index + 2)]
        assert all(part.bit_count() == block_size for part in parts)
        assert not any(left & right for left, right in combinations(parts, 2))
        assert neighborhoods[index] == parts[0] | parts[1] | parts[2]
    return block


def main():
    parse = argparse.ArgumentParser(description=__doc__)
    parse.add_argument('order22')
    args = parse.parse_args()
    order = 21
    adj = [sum(1 << ((vertex + step) % order) for step in (1,-1,4,-4,6,-6)) for vertex in range(order)]
    assert all(not adj[left] & adj[right] for left in range(order) for right in bits(adj[left]))
    assert max(mask.bit_count() for mask in independent_masks(adj, (1 << order) - 1)) == 6
    for start in range(order):
        assert {other for other in range(order) if (adj[start] & adj[other]).bit_count() == 4} == {
            (start - 5) % order, (start + 5) % order}
        for step in (5, -5):
            vertices = [(start + index * step) % order for index in range(11)]
            block = find_path_blocks(adj, vertices, 2)
            witness = [vertices[index] for index in (0,1,2,8,9,10)]
            assert all(not (adj[left] >> right & 1) for left, right in combinations(witness, 2))
            seen = 0
            for vertex in witness:
                seen |= adj[vertex]
            assert seen.bit_count() == 10 * 2 - 5
            for index in range(-1, 4):
                assert (block[index] & block[index + 8]) >> vertices[index + 4] & 1
    print('C21: 42 oriented eleven-root paths, two-set partitions and six-root union bound sharp (15)')
    count22 = 0
    for line in Path(args.order22).read_text().splitlines():
        adj22 = decode(line)
        assert len(adj22) == 22 and all(neighbors.bit_count() == 6 for neighbors in adj22)
        for root in range(22):
            assert sum((adj22[root] & other).bit_count() == 4 for other in adj22) <= 1
        count22 += 1
    print('order 22:', count22, 'graphs respect the stronger no-two-partners bound')
    assert 40 - 6 - (10 * 3 - 5) > MAX_ORDER[9 - 6]
    print('order 40: same six-root pattern forces a forbidden nine-vertex residue of alpha<=3')


if __name__ == '__main__':
    main()
