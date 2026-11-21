"""Generate every triangle-free one-edge addition, independently of edgeup.c."""

from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from check_graph import parse_graph6


def main():
    parents = children = 0
    for text in sys.stdin:
        graph = parse_graph6(text)
        if not 1 <= len(graph) <= 62 or not text.endswith('\n'):
            raise ValueError('expected short graph6 records')
        parents += 1
        for left, right in combinations(range(len(graph)), 2):
            if graph[left] & ((1 << right) | graph[right]):
                continue
            word, bit = divmod(right * (right - 1) // 2 + left, 6)
            position = word + 1
            replacement = chr(63 + ((ord(text[position]) - 63) | (32 >> bit)))
            sys.stdout.write(text[:position] + replacement + text[position+1:])
            children += 1
    print(f'independent addition: {parents} parents, {children} labelled children', file=sys.stderr)


if __name__ == '__main__':
    main()
