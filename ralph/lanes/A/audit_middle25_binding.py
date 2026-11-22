#!/usr/bin/env python3
"""Independent ordered audit of G's d8/j2/minimum-2 middle-only bundle."""

import argparse
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import sys

from audit_residual_binding import expected_pins
from audit_strip_extensions import ROOT, bind, eager_tail, raw_link, read_keys
from mixed_selector import Window, role_id, roles


@lru_cache(maxsize=32)
def parse_window(row_id, first, second, encoded):
    window = Window.parse(f'{row_id} {first} {second} {encoded}')
    assert window.order == 25 and min(ns.bit_count() for ns in window.adj) == 2
    assert sum(ns.bit_count() for ns in window.adj) <= 166
    return window


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slice', type=int, nargs=2, default=(0, 1), metavar=('INDEX', 'COUNT'))
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    index, count = args.slice
    assert 0 <= index < count
    sys.path.insert(0, str(ROOT / 'ralph/lanes/G'))
    from mixed_strip_completion import instance

    producer = ROOT / 'scratch/G/round10'
    prefix = 'r25.d8.middle'
    source = {key: value for key, value in
              read_keys([ROOT / 'scratch/A/strip10/roles.25.8.edge.keys']).items()
              if value[0][3] == 'middle'}
    scheduled = read_keys([producer / f'{prefix}.keys'])
    assert len(source) == 21236 and scheduled == source
    logs = [producer / f'{prefix}.{shard}.log' for shard in range(12)]
    ordered = {log: list(scheduled)[shard::12] for shard, log in enumerate(logs)}
    covered, counts, attempted = bind(source, [[producer / prefix, *logs]], ordered)
    absent = sorted(set(source) - attempted)
    nonterminal = sorted(attempted - set(covered))
    if absent or nonterminal:
        for key in absent:
            print(f'MISSING {key}', file=sys.stderr)
        for key in nonterminal:
            print(f'NONTERMINAL {key}', file=sys.stderr)
        raise ValueError(counts)
    assert counts == Counter(CERT=len(source))
    stray = {trace for trace in (producer / prefix).glob('*.lrat.gz')} - {
        trace for trace, _ in covered.values()}
    assert not stray, sorted(stray)
    graph_ids = {}
    with (producer.parent / 'round7/lowdegree25.raw.g6').open('rb') as raw:
        for fields, encoded in source.values():
            row_id = fields[0]
            if row_id not in graph_ids:
                raw_link(raw.name, row_id, encoded, raw)
            assert graph_ids.setdefault(row_id, encoded) == encoded, row_id
    print(f'Partition and 12 ordered shards: {len(source)} CERT, {len(graph_ids)} raw rows, '
          f'{len(absent)} missing, {len(nonterminal)} nonterminal, {len(stray)} stray', file=sys.stderr)

    cnf = Path(f'binding25.{index}.tmp.cnf')
    failures = []
    total_pins, total_tail = 0, 0
    try:
        for key in sorted(source)[index::count][:args.limit]:
            try:
                fields, encoded = source[key]
                row_id, first, second, shape, left, right, peer = fields
                window = parse_window(row_id, first, second, encoded)
                row = ' '.join((*fields, encoded))
                holes, = [holes for name, holes in roles(window, 8) if role_id(window, 8, name, holes) == row]
                base = instance(encoded, int(first), int(second), shape, int(left), int(right), int(peer),
                                0, residual=True)
                expected, exclusive = expected_pins(window, holes, degree=8)
                assert expected == {pair: state for pair, state in base.edge.items() if abs(state) == 1}, 'pins'
                tail = list(eager_tail(base.edge, window.adj, exclusive, window.pivots))
                base.formula.clauses.extend(tail)
                base.formula.write(cnf)
                trace, receipt_hash = covered[key]
                cnf_hash = sha256(cnf.read_bytes()).hexdigest()
                assert cnf_hash == receipt_hash, f'expected {receipt_hash}, rebuilt {cnf_hash}'
                trace_hash = sha256(trace.read_bytes()).hexdigest()
                print(key, cnf_hash, trace_hash, trace.relative_to(producer), trace.stat().st_size, sep='\t')
                total_pins += len(expected)
                total_tail += len(tail)
            except (ValueError, AssertionError, OSError) as error:
                print(f'FAIL {key} {error!r}', file=sys.stderr, flush=True)
                failures.append(key)
    finally:
        cnf.unlink(missing_ok=True)
    print(f'{len(failures)} failures; {total_pins} fixed edges, {total_tail} accepted eager rows',
          file=sys.stderr)
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
