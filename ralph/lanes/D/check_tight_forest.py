#!/usr/bin/env python3
"""Match exact labelled C16 outputs and every count pin against known controls."""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import time

from kernel_projection import bits, decode
from max_root import catalogue
from tight_forest_sat import cyclic_kernel, run


def forest(graph):
    root_forests = 0
    branching = 0
    for first, row in enumerate(graph):
        for second in bits(row & ~((1 << (first + 1)) - 1)):
            vertices = (row ^ (1 << second)) | (graph[second] ^ (1 << first))
            if any((graph[vertex] & vertices).bit_count() == 2 for vertex in bits(vertices)):
                branching += 1
            remaining = vertices
            while remaining:
                leaves = sum(1 << vertex for vertex in bits(remaining)
                             if (graph[vertex] & remaining).bit_count() <= 1)
                if not leaves:
                    return False, branching
                remaining ^= leaves
            root_forests += 1
    assert root_forests == sum(row.bit_count() for row in graph) // 2
    return True, branching


def twos(graph, degree):
    size = (1 << (degree - 1)) - 1
    return sum((graph[vertex] & size).bit_count() == 2 and
               (graph[vertex] >> (degree - 1) & size).bit_count() == 2
               for vertex in range(2 * degree, len(graph)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('controls', type=Path)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--compact', action='store_true')
    args = parser.parse_args()
    order, degree = 16, 5
    counts = Counter()
    start = time.process_time()
    codes = list(catalogue(order, degree))
    for index, code in enumerate(codes):
        codes_expected = (args.controls / f'eager-{index}.g6').read_text().splitlines()
        clean = {}
        for control in codes_expected:
            graph = decode(control)
            is_forest, branching = forest(graph)
            assert is_forest == (not cyclic_kernel(graph))
            counts['labeled'] += 1
            counts['forest'] += is_forest
            counts['nontrivial-forest'] += is_forest and bool(branching)
            if is_forest:
                clean[control] = twos(graph, degree)
        for variant, pin in [('plain', None), ('forest', None)] + [('signed', pin) for pin in range(7)]:
            expect = (set(codes_expected) if variant == 'plain' else
                      {code for code, count in clean.items() if pin is None or count == pin})
            prefix = args.directory / f'{index}-{variant}-{pin}'
            with prefix.with_suffix('.log').open('w') as log:
                with redirect_stdout(log):
                    output = StringIO()
                    run(decode(code), order, degree, variant, pin, output, compact=args.compact)
            lines = output.getvalue().splitlines()
            prefix.with_suffix('.g6').write_text(output.getvalue())
            assert len(lines) == len(set(lines)) and set(lines) == expect, (index, variant, pin, expect, lines)
            counts['solves'] += 1
    assert counts['labeled'] == 13 and counts['forest'] > 0
    print(f'PASS {dict(counts)} from {len(codes)} complete keys CPU={time.process_time()-start:.3f}')


if __name__ == '__main__':
    main()
