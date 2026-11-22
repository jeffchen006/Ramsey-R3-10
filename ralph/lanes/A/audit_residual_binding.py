#!/usr/bin/env python3
"""Bind G's 215 residual d9/j4/δ3 proofs without running a SAT solver."""

from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import sys

from audit_path_leaf import vertices
from audit_strip_extensions import ROOT, bind, eager_tail, read_keys
from mixed_selector import Window, bitset, role_id, roles, signatures


def expected_pins(window, holes, degree=9):
    order = window.order
    roots, pivots = (order, order+1), window.pivots
    shared = order - 31 + degree
    common = tuple(range(order+4, order+4+shared))
    split = order+4+shared
    exclusive = (tuple(range(split, split+6-shared)), tuple(range(split+6-shared, 40)))
    want = (signatures(window.active[0], ()), signatures(window.active[1], holes))
    removed = dict()
    for index, other_cut in enumerate(reversed(exclusive)):
        deficits = sorted(tuple(vertices(support)) for support in (want[index] - window.seen[index]).elements())
        assert not (window.seen[index] - want[index])
        removed.update((vertex, bitset(signature)) for vertex, signature in zip(other_cut, deficits, strict=True))
    known = [set() for _ in range(40)]
    all_pairs = tuple(combinations(range(40), 2))
    fixed = dict()
    for first, second in all_pairs:
        if second < order:
            fixed[first, second] = bool(window.adj[first] >> second & 1)
        elif first in roots or second in roots:
            matched = first if first in roots else second
            peer = second if first == matched else first
            fixed[first, second] = peer in roots or peer in window.sides[roots.index(matched)]
        elif first in pivots or second in pivots:
            matched = first if first in pivots else second
            peer = second if first == matched else first
            fixed[first, second] = peer in common or peer in exclusive[pivots.index(matched)]
        elif first >= 30:
            if first in exclusive[0] and second in exclusive[1]:
                continue
            fixed[first, second] = False
        elif second in removed:
            paired_side = window.active[0] if second in exclusive[1] else window.active[1]
            if first in paired_side:
                fixed[first, second] = bool(removed[second] >> first & 1)
    for (first, second), value in fixed.items():
        if value:
            known[first].add(second)
            known[second].add(first)
    for first, second in all_pairs:
        if known[first] & known[second]:
            assert not fixed.get((first, second))
            fixed[first, second] = False
    return {pair: 1 if value else -1 for pair, value in fixed.items()}, exclusive


def main(scratch):
    sys.path.insert(0, str(ROOT / 'ralph/lanes/G'))
    from mixed_strip_completion import instance

    producer = ROOT / 'scratch/G/round10'
    source = read_keys([scratch / 'roles.26.9.edge.keys'])
    schedule, all_scheduled, batches = {}, set(), []
    for batch, slots in (('pilot', 2), ('production', 4)):
        prefix = f'r26.d9.{batch}'
        scheduled = read_keys([producer / f'{prefix}.keys'])
        assert not (set(scheduled) & all_scheduled)
        assert all(source.get(key) == value for key, value in scheduled.items())
        all_scheduled.update(scheduled)
        logs = [producer / f'{prefix}.{index}.log' for index in range(slots)]
        for index, log in enumerate(logs):
            schedule[log] = list(scheduled)[index::slots]
        batches.append([producer / prefix, *logs])
    assert all_scheduled == set(source)
    covered, stats, attempted = bind(source, batches, schedule)
    assert len(source) == 215 and set(covered) == attempted == set(source) and stats == Counter(CERT=215)
    assert {path for folder, *_ in batches for path in folder.glob('*.lrat.gz')} == {
        path for path, _ in covered.values()}
    producer_index = {}
    for line in (producer / 'r26.d9.bound/certificates.tsv').read_text().splitlines():
        key, cnf_hash, trace_hash, path, size = line.split()
        assert key not in producer_index
        producer_index[key] = (cnf_hash, trace_hash, producer / path, int(size))
    assert set(producer_index) == set(source)

    cnf = scratch / 'binding.tmp.cnf'
    try:
        for key, (fields, encoded) in sorted(source.items()):
            source_id, first, second, shape, *labels = fields
            window = Window.parse(' '.join((source_id, first, second, encoded)))
            assert window.order == 26 and min(ns.bit_count() for ns in window.adj) == 3
            assert sum(ns.bit_count() for ns in window.adj) <= 174
            name, holes = next((name, holes) for name, holes in roles(window, 9)
                               if role_id(window, 9, name, holes) == ' '.join((*fields, encoded)))
            assert shape == 'full-' + name
            first_hole, second_hole, first_peer, second_peer = map(int, labels)
            base = instance(encoded, int(first), int(second), shape, first_hole, second_hole,
                            first_peer, 0, second_peer, residual=True)
            expected, exclusive = expected_pins(window, holes)
            assert expected == {pair: state for pair, state in base.edge.items() if abs(state) == 1}
            tail = list(eager_tail(base.edge, window.adj, exclusive, window.pivots))
            base.formula.clauses.extend(tail)
            base.formula.write(cnf)
            cnf_hash = sha256(cnf.read_bytes()).hexdigest()
            trace, receipt_hash = covered[key]
            assert cnf_hash == receipt_hash
            trace_hash = sha256(trace.read_bytes()).hexdigest()
            assert (cnf_hash, trace_hash, trace, trace.stat().st_size) == producer_index[key]
            print(key, len(expected), len(tail), cnf_hash, trace_hash, flush=True)
    finally:
        cnf.unlink(missing_ok=True)
    print('215/215 independent pins, eager CNF digests and producer-bound trace digests; no separate proof run')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
