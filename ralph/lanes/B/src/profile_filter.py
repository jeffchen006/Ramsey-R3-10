"""Independent check of degree/dual-edge filters on labelled graph output."""
import argparse
import sys


def keep(line, low, exclusions):
    order = line[0] - 63
    if order not in (22, 30) or len(line) != 2 + (order * (order - 1) // 2 + 5) // 6 or line[-1] != 10:
        raise ValueError('invalid graph6 record')
    bits = ''.join(f'{value - 63:06b}' for value in line[1:-1])
    adjacent = [[] for _ in range(order)]
    for right in range(1, order):
        for left in range(right):
            if bits[right * (right - 1) // 2 + left] == '1':
                adjacent[left].append(right)
                adjacent[right].append(left)
    degrees = list(map(len, adjacent))
    if sum(degrees) != 2 * low:
        return False
    return all(low - sum(degrees[neighbor] for neighbor in adjacent[vertex]) > exclusions.get(degree, -1)
               for vertex, degree in enumerate(degrees))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('edge', type=int)
    parser.add_argument('threshold', nargs='*', type=int)
    args = parser.parse_args()
    exclusions = dict(zip((5, 6, 7), args.threshold, strict=bool(args.threshold)))
    seen = selected = 0
    for line in sys.stdin.buffer:
        seen += 1
        if keep(line, args.edge, exclusions):
            sys.stdout.buffer.write(line)
            selected += 1
    print(f'profile_filter in={seen} out={selected}', file=sys.stderr)
