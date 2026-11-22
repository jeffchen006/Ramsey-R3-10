#!/usr/bin/env python3
"""Independent physical CNF regeneration and projection proof receipt join."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess

from pysat.card import CardEnc, EncType

from bind_width74 import dimacs, narrow_clauses
from involution_sat import from_graph6
from rebind_deck23 import TOOLS


def formula(projected, additions):
    label, groups, residue, high = projected
    graph = from_graph6(label)
    pinned = [{peer for peer in range(8) if row >> peer & 1} for row in graph]
    parts = (tuple(range(8, 14)), tuple(range(14, 20)), tuple(range(20, 26)))
    for columns in groups:
        for contact in columns:
            site = len(pinned)
            pinned.append({root for root in range(8) if contact >> root & 1})
            for root in pinned[site]:
                pinned[root].add(site)
    assert len(pinned) == 26 and [len(nbrs) for nbrs in pinned[:8]] == [7-amount for amount in residue]
    edge_id = {}
    for source, target in combinations(parts, 2):
        for left, right in product(source, target):
            if not pinned[left].intersection(pinned[right]):
                edge_id[left, right] = len(edge_id)+1
    variables = len(edge_id)
    clauses = []

    def cap(row, bound, condition=()):
        nonlocal variables
        if bound < 0:
            clauses.append(tuple(condition))
        elif bound < len(row):
            compiled = CardEnc.atmost(lits=row, bound=bound, top_id=variables, encoding=EncType.seqcounter)
            clauses.extend(tuple(condition) + tuple(clause) for clause in compiled.clauses)
            variables = max(variables, compiled.nv)

    for positions in product(*parts):
        edge_set = tuple(combinations(positions, 2))
        if all(edge in edge_id for edge in edge_set):
            clauses.append(tuple(-var for var in sorted(edge_id[edge] for edge in edge_set)))
    remaining_edges = 74 - sum(map(len, pinned))//2
    cap(list(edge_id.values()), remaining_edges)
    cap([-var for var in edge_id.values()], len(edge_id)-remaining_edges)
    incident = [[var for edge, var in edge_id.items() if vertex in edge] for vertex in range(26)]
    for vertex, link in enumerate(incident):
        cap(link, 7-len(pinned[vertex]))
    clauses.extend(narrow_clauses(pinned, edge_id, [(set(range(26)), 8)], width=3))
    marks = {}
    for vertex in range(8, 26):
        variables += 1
        marks[vertex] = variables
        necessary = 7-len(pinned[vertex])
        cap(incident[vertex], necessary-1, (marks[vertex],))
        cap([-var for var in incident[vertex]], len(incident[vertex])-necessary, (-marks[vertex],))
    exterior = high - sum(len(row) == 7 for row in pinned[:8])
    cap(list(marks.values()), exterior)
    cap([-var for var in marks.values()], len(marks)-exterior)
    for left, right in combinations(marks, 2):
        clauses.append((-marks[left], -marks[right], *([edge_id[left, right]] if (left, right) in edge_id else [])))
    for wing in parts:
        misses = []
        for vertex in range(8, 26):
            if vertex in wing:
                continue
            contacts = tuple(edge_id[pair] for target in wing if (pair := tuple(sorted((vertex, target)))) in edge_id)
            if high == 6:
                clauses.append(contacts)
            else:
                variables += 1
                misses.append(variables)
                clauses.append((*contacts, variables))
        if misses:
            cap(misses, high-6)
    if any(not clause for clause in clauses):
        variables += 1
        clauses = [clause or (variables,) for clause in clauses]
        clauses.append((-variables,))
    for picked, in additions:
        vertices = [vertex for vertex in range(26) if picked >> vertex & 1]
        assert 0 <= picked < 1 << 26 and len(vertices) == 8
        assert not any(pinned[vertex].intersection(vertices) for vertex in vertices)
        clauses.append(tuple(var for (left, right), var in edge_id.items() if left in vertices and right in vertices))
    return dimacs(variables, clauses)


def ledgers(plan):
    rows = plan.read_bytes().splitlines()
    pilot = Path('projected.pilot.plan').read_bytes().splitlines()
    mined = {}
    pilot_receipts = {}
    for folder in ('projected.pilot', 'projected.pilot2'):
        for terminal in map(json.loads, (Path(folder)/'worker.0.jsonl').open(encoding='ascii')):
            if terminal[1] == 'CHECKED':
                pilot_receipts[folder, terminal[0]] = terminal
    for line in Path('projected.pilots.tsv').read_text(encoding='ascii').splitlines():
        identity, folder, original = line.split()
        identity, original = int(identity), int(original)
        assert pilot[original] == rows[identity] and identity not in mined
        terminal = pilot_receipts.pop((folder, original))
        mined[identity] = (Path(folder)/f'{original:07d}', [identity, *terminal[1:]])
    assert not pilot_receipts
    for offset in range(16):
        for terminal in map(json.loads, (Path('projected.final')/f'worker.{offset}.jsonl').open(encoding='ascii')):
            index = terminal[0]
            assert index % 16 == offset and index not in mined and 0 <= index < len(rows)
            mined[index] = Path('projected.final')/f'{index:07d}', terminal
    assert set(mined) == set(range(len(rows)))
    return rows, mined


def replay(plan, output, offset, stride):
    rows, by_id = ledgers(plan)
    output.mkdir(exist_ok=True)
    cnf, lrat = output/f'proof.{offset}.cnf', output/f'proof.{offset}.lrat'
    tally = Counter()
    with (output/f'receipts.{offset}.jsonl').open('x', encoding='ascii', buffering=1) as stream:
        for index in range(offset, len(rows), stride):
            folder, terminal = by_id[index]
            _, status, cnf_hash, proof_hash, size, count, _ = terminal
            tally[status] += 1
            if status == 'CHECKED':
                witnesses = json.loads((folder/'witnesses.json').read_bytes())
                assert len(witnesses) == count
                source = formula(json.loads(rows[index]), witnesses)
                proof = gzip.decompress((folder/'proof.lrat.gz').read_bytes())
                assert (sha256(source).hexdigest(), sha256(proof).hexdigest(), len(proof)) == (cnf_hash, proof_hash, size), index
                cnf.write_bytes(source)
                lrat.write_bytes(proof)
                for tool, flags, marker in (('cake_lpr', ('--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=64'), b's VERIFIED UNSAT'),
                                            ('lrat-check', (), b'c VERIFIED')):
                    check = subprocess.run(['timeout', '-k', '2s', '30s', 'prlimit', '--cpu=10:11', '--', str(TOOLS/tool),
                                            *flags, str(cnf), str(lrat)], capture_output=True, check=False)
                    assert check.returncode == 0 and marker in {line.rstrip() for line in check.stdout.splitlines()}, index
                cnf.unlink()
                lrat.unlink()
            print(json.dumps(terminal), file=stream)
    print('degree-roster proof replay', offset, stride, dict(tally), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args()
    replay(args.plan, args.output, args.offset, args.stride)
