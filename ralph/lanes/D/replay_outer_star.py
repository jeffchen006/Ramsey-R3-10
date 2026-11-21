#!/usr/bin/env python3
"""Recheck an outer-star projection trace and its local DIMACS proofs."""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, groupby
import json
from pathlib import Path
import resource
import subprocess
import time

from factor_sat import Formula
from max_root import MaxProjection, catalogue
from outer_star import Star
from kernel_projection import bits, decode


ROOT = Path(__file__).resolve().parents[3]


class Dimacs:
    def __init__(self):
        self.rows = []

    def add_clause(self, clause):
        self.rows.append(clause)

    def write(self, path, variables):
        with path.open('w') as stream:
            print('p cnf', variables, len(self.rows), file=stream)
            for row in self.rows:
                print(*row, 0, file=stream)


def witness_ok(star, active, mask, witness):
    assert isinstance(witness, list) and len(set(witness)) == star.degree - mask.bit_count() == len(witness)
    assert all(other in active and not other & mask for other in witness)
    for coord in bits(star.interior ^ mask):
        paths = (star.adj[coord] & mask).bit_count() + sum(other >> coord & 1 for other in witness)
        assert star.floor <= paths <= 3
    for first, second in combinations(bits(star.interior ^ mask), 2):
        pair = (1 << first) | (1 << second)
        paths = (star.adj[first] & star.adj[second]).bit_count() + sum(other & pair == pair for other in witness)
        assert paths <= 3
    assert all((first & second).bit_count() <= 2 for first, second in combinations(witness, 2))


def check_proof(star, mask, directory, iteration):
    stem = directory / f'r{iteration}-{mask}'
    cnf, lrat = stem.with_suffix('.cnf'), stem.with_suffix('.lrat')
    dimacs = Dimacs()
    formula = Formula(dimacs)
    star.compile(formula, mask, False)
    assert formula.clauses == len(dimacs.rows)
    dimacs.write(cnf, formula.variables)
    limit = ['nice', '-n', '5', 'timeout', '40', 'prlimit', '--cpu=30:32', '--fsize=67108864:67108864']
    result = subprocess.run(limit + [str(ROOT / 'opt/bin/cadical'), '--quiet', '--lrat', cnf, lrat],
                            capture_output=True, text=True)
    assert result.returncode == 20 and 's UNSATISFIABLE' in result.stdout, (mask, result.returncode, result.stdout[-300:])
    checked = subprocess.run(limit + [str(ROOT / 'opt/bin/cake_lpr'), cnf, lrat], capture_output=True, text=True)
    assert 's VERIFIED UNSAT' in checked.stdout, (mask, checked.stdout[-300:], checked.stderr[-300:])
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in (cnf, lrat)]
    return dict(mask=mask, iteration=iteration, cnf_sha256=hashes[0], lrat_sha256=hashes[1],
                variables=formula.variables, clauses=formula.clauses)


def replay(args):
    projection = json.loads(args.projection.read_text())
    index = projection['index']
    code = list(catalogue(args.order, args.degree))[index]
    assert code == projection['code']
    star = Star(decode(code), args.order, args.degree)
    partition = dict(star.orbits())
    active = set(star.masks)
    initial = active.copy()
    results = Counter()
    trace = list(map(json.loads, args.trace.read_text().splitlines()))
    model = MaxProjection(decode(code), args.order, args.degree)
    needed = set()
    direct_columns = ()
    if args.direct:
        assert projection['status'] == 'cert'
        combine = [0] * len(model.masks)
        assert any(row == len(model.rows) and weight > 0 for row, weight in projection['proof'])
        for row, weight in projection['proof']:
            if row == len(model.rows):
                continue
            for col, coeff in model.rows[row][0]:
                combine[col] += weight * coeff
        direct_columns = tuple((col, 1) for col, coeff in enumerate(combine) if coeff < 0)
        needed = {model.masks[col] for col, _ in direct_columns} & initial
        print(f'direct_projection columns={len(direct_columns)} require_star={len(needed)}', flush=True)
    if args.proofs:
        args.proofs.mkdir(parents=True, exist_ok=True)
    for expected, (iteration, group) in enumerate(groupby(trace, key=lambda row: row['iteration']), start=1):
        rows = list(group)
        assert expected == iteration and len(rows) == len(partition)
        assert {row['mask'] for row in rows} == set(partition)
        gone = set()
        for row in rows:
            mask = row['mask']
            block = partition[mask]
            assert block == row['block'] and set(block) <= active
            if row['status'] == 'viable':
                witness_ok(star, active, mask, row['neighbors'])
                results['witness'] += 1
            else:
                assert row['status'] == 'unsat' and row['neighbors'] is None
                if args.proofs and (not args.direct or (iteration == 1 and needed.intersection(block))):
                    evidence = check_proof(star, mask, args.proofs, iteration)
                    print(json.dumps(evidence, separators=(',', ':')), flush=True)
                    results['lrat'] += 1
                gone.update(partition.pop(mask))
                results['removed_orbits'] += 1
        if args.direct and iteration == 1:
            assert needed <= gone, f'{len(needed - gone)} columns need later-iteration prerequisites'
        active -= gone
        star.masks = [mask for mask in star.masks if mask in active]
    assert not gone and sorted(active) == projection['kept']
    deleted = tuple((col, 1) for col, mask in enumerate(model.masks) if mask not in active)
    assert len(deleted) == projection['deleted']
    if projection['status'] == 'cert':
        model.rows.append((direct_columns if args.direct else deleted, 0, 'outer-star-fixed-point'))
        model.check(projection['proof'])
        results['farkas'] += 1
    print(f'PASS {index=} {dict(results)} kept={len(active)}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('trace', type=Path)
    parser.add_argument('projection', type=Path)
    parser.add_argument('--proofs', type=Path)
    parser.add_argument('--direct', action='store_true')
    args = parser.parse_args()
    start = time.process_time()
    replay(args)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    print(f'cpu_parent={time.process_time()-start:.3f} cpu_children={children.ru_utime+children.ru_stime:.3f}')


if __name__ == '__main__':
    main()
