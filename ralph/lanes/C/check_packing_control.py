"""Reconstruct full smaller-case graphs from enumerator output and compare census."""

import argparse
from itertools import combinations
from pathlib import Path
import subprocess

from kernel_projection import bits, decode, encode, independent_masks


def fixed_shape(adj, degree):
    for upper, lower in combinations(range(len(adj)), 2):
        overlap = adj[upper] & adj[lower]
        if overlap.bit_count() != degree - 2:
            continue
        first, second = adj[upper] ^ overlap, adj[lower] ^ overlap
        if all(adj[vertex] & second == second for vertex in bits(first)):
            return True
    return False


def verify_inside(adj_x, side, colours, degree, cap):
    order_x = len(adj_x)
    start_common = order_x + 2
    start_side = start_common + degree - 2
    adj = adj_x[:] + [0] * (degree + 4)

    def edge(left, right):
        adj[left] |= 1 << right
        adj[right] |= 1 << left

    for vertex, mask in enumerate(colours + side, start=start_common):
        for target in bits(mask):
            edge(vertex, target)
    for vertex in range(start_common, start_side):
        edge(vertex, order_x)
        edge(vertex, order_x + 1)
    for side_index in range(4):
        edge(start_side + side_index, order_x + (side_index >= 2))
    for left in (0, 1):
        for right in (2, 3):
            edge(start_side + left, start_side + right)
    assert all(mask.bit_count() == degree for mask in adj)
    assert all(not adj[left] & adj[right] for left, neighbors in enumerate(adj) for right in bits(neighbors))
    for left, right in combinations(range(len(adj)), 2):
        if not adj[left] >> right & 1:
            assert 1 <= (adj[left] & adj[right]).bit_count() <= cap
    assert max(indep.bit_count() for indep in independent_masks(adj, (1 << len(adj)) - 1)) == degree
    return encode(adj)


def canonicalize(graphs, labelg):
    out = subprocess.run([labelg, '-q'], input=''.join(graph + '\n' for graph in sorted(graphs)),
                         text=True, capture_output=True, check=True)
    return set(out.stdout.splitlines())


def main():
    parse = argparse.ArgumentParser(description=__doc__)
    parse.add_argument('inputs')
    parse.add_argument('known')
    parse.add_argument('labelg')
    args = parse.parse_args()
    known = Path(args.known).read_text().splitlines()
    expected = {line for line in known if fixed_shape(decode(line), 6)}
    assert len(expected) == 7
    obtained = set()
    all_solutions = 0
    num_packages = 0
    for path in sorted(Path(args.inputs).glob('cal_pair*.txt')):
        lines = path.read_text().splitlines()
        degree, cap, order = map(int, lines[0].split())
        assert degree == 6 and cap == 4
        adj = list(map(int, lines[1].split()))
        assert len(adj) == order
        packages = [list(map(int, line.split())) for line in lines[2:]]
        closed = set()
        reported = 0
        for row in path.with_suffix('.results').read_text().splitlines():
            status, index, *values = row.split()
            index = int(index)
            assert 0 <= index < len(packages) and index not in closed
            if status == 'end':
                closed.add(index)
                reported += int(values[0])
            elif status == 'solution':
                all_solutions += 1
                obtained.add(verify_inside(adj, packages[index], list(map(int, values)), degree, cap))
            else:
                raise AssertionError((status, index))
        assert closed == set(range(len(packages)))
        num_packages += len(packages)
        print(path.name, 'packages', len(packages), 'solutions', reported)
    assert canonicalize(obtained, args.labelg) == canonicalize(expected, args.labelg)
    print('exact known seven-class subset recovered:', num_packages, 'packages;', all_solutions, 'labelled solutions')


if __name__ == '__main__':
    main()
