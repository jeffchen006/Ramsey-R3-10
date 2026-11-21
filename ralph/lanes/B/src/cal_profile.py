"""Exact rooted control comparison for profile-pinned MTF gluing."""

import argparse
from pathlib import Path

from cal_mtf import canon, dual, glue, is_mtf, parse_graph6, to_graph6


def profile(rows, root=-1):
    degrees = [neighbors.bit_count() for neighbors in rows]
    local = sorted(degrees[vertex] for vertex in range(len(rows)) if rows[root] >> vertex & 1)
    return ''.join(map(str, local)), ','.join(str(degrees.count(degree)) for degree in range(10))


def controls(source):
    for graph in source.read_text().splitlines():
        rows = parse_graph6(graph)
        if is_mtf(rows):
            for root in range(len(rows)):
                yield graph, rows, root


def run(source, alpha, limit):
    checked = 0
    keys = set()
    excluded = 0
    for graph, rows, root in controls(source):
        degrees = [neighbors.bit_count() for neighbors in rows]
        local, histogram = profile(rows, root)
        edges = sum(degrees) // 2
        key = (edges, local, histogram)
        if key in keys:
            continue
        keys.add(key)
        base = ('-k', str(alpha), '-d', str(degrees[root]), '-m', str(min(degrees)),
                '-E', str(edges), '-e', str(edges))
        residue = to_graph6(dual(rows, root))
        baseline = []
        for candidate in glue('glue2', residue, *base):
            parsed = parse_graph6(candidate)
            if not is_mtf(parsed):
                continue
            if profile(parsed) == (local, histogram):
                baseline.append(candidate)
            else:
                excluded += 1
        actual = glue('mtfcover_r5', residue, *base, '-X', '-s', local, '-p', histogram)
        expected_keys, actual_keys = canon('\n'.join(baseline)), canon('\n'.join(actual))
        assert expected_keys == actual_keys and canon(graph) <= actual_keys
        checked += 1
        print(f'control {checked}: rows={local} histogram={histogram} canonical={len(actual_keys)}')
        if checked == limit:
            break
    assert checked == limit
    wrong = [int(field) for field in histogram.split(',')]
    wrong[degrees[root]] -= 1
    wrong[degrees[root]+1] += 1
    assert not glue('mtfcover_r5', residue, *base, '-X', '-s', local, '-p', ','.join(map(str, wrong)))
    print(f'{checked} exact positive controls and a corrupted histogram; {excluded} off-profile labelled baseline outputs rejected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('alpha', type=int)
    parser.add_argument('limit', type=int)
    arguments = parser.parse_args()
    run(arguments.source, arguments.alpha, arguments.limit)
