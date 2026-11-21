"""Check C's pin representatives by adjacent-swap orbit closure, without SAT."""

import ast
from itertools import combinations, permutations, product
from pathlib import Path


def load_shape_functions():
    source = Path(__file__).resolve().parents[1] / 'C/path_four_mixed.py'
    functions = [node for node in ast.parse(source.read_text()).body
                 if isinstance(node, ast.FunctionDef) and node.name in ('cross_shape', 'cross_patterns')]
    assert len(functions) == 2
    names = dict(combinations=combinations, permutations=permutations, product=product,
                 bits=lambda mask: (index for index in range(mask.bit_length()) if mask >> index & 1))
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), names)
    return names['cross_patterns']


def adjacent_swaps(mask, block):
    for offset in range(block - 1):
        row_start = offset * block
        row_shift = ((mask >> row_start) ^ (mask >> (row_start + block))) & ((1 << block) - 1)
        yield mask ^ (row_shift << row_start) ^ (row_shift << (row_start + block))
        column_mask = sum(1 << (row * block + offset) for row in range(block))
        column_shift = (mask ^ (mask >> 1)) & column_mask
        yield mask ^ column_shift ^ (column_shift << 1)


def orbit_cover(block, weight):
    todo = {mask for mask in range(1 << (block * block)) if mask.bit_count() == weight}
    representatives = []
    total = len(todo)
    while todo:
        start = min(todo)
        representatives.append(start)
        todo.remove(start)
        queue = [start]
        for mask in queue:
            for image in adjacent_swaps(mask, block):
                if image in todo:
                    todo.remove(image)
                    queue.append(image)
    return representatives, total


def main():
    cross_patterns = load_shape_functions()
    for block, weight, count in ((2, 2, 3), (3, 5, 7), (3, 6, 6)):
        expected, total = orbit_cover(block, weight)
        actual = cross_patterns(block, weight)
        assert len(expected) == count and actual == expected
        print(f'PASS: {block} by {block}, weight {weight}: {total} matrices; {count} matching representatives')


if __name__ == '__main__':
    main()
