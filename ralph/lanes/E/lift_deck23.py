#!/usr/bin/env python3
"""Byte-bound local LRATs for adding a fourth attachment to a marked window."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
from time import process_time

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from bind_width74 import dimacs
from deficit73 import mask
from involution_cores import bits, graph
from involution_sat import from_graph6, to_graph6, witnesses


TOOLS = Path(__file__).resolve().parents[3] / 'opt' / 'bin'


class Lift:
    def __init__(self, card, core, groups, width, core_degree, rest_degree, window_limit, full_limit, single_limit):
        count = len(card)
        full = (1 << (count + width)) - 1
        added = full ^ ((1 << count) - 1)
        assert len(groups) == 3 and all(group.bit_count() == width for group in groups)
        assert (core | groups[0] | groups[1] | groups[2]) == (1 << count) - 1
        assert sum([core.bit_count(), *(group.bit_count() for group in groups)]) == count
        assert all(not row & group for group in groups for vertex, row in enumerate(card) if group >> vertex & 1)
        self.lower = (*card, *(0 for _ in range(width)))
        self.groups = (*groups, added)
        self.count, self.width = count, width
        self.edges = tuple(product(range(count), range(count, count + width)))
        self.edge_id = {pair: index for index, pair in enumerate(self.edges, 1)}
        self.domains = tuple((full ^ group, window_limit) for group in groups) + ((full, full_limit), (core | added, single_limit))
        if width == 6 and len(card) == 26:
            self.domains += ((core, 6),)
        self.degrees = tuple(core_degree if core >> vertex & 1 else rest_degree for vertex in range(count + width))
        self.variables = len(self.edges)
        self.base = []

        for vertex, degree in enumerate(self.degrees):
            literals = [variable for pair, variable in self.edge_id.items() if vertex in pair]
            needed = degree - self.lower[vertex].bit_count()
            self.clamp(literals, needed)
            self.clamp([-literal for literal in literals], len(literals) - needed)
        for first, row in enumerate(card):
            for second in bits(row & ~((2 << first) - 1)):
                for third in range(count, count + width):
                    self.base.append((-self.edge_id[first, third], -self.edge_id[second, third]))
        for vertex in bits(core):
            self.base.append(tuple(self.edge_id[vertex, peer] for peer in bits(added)))

    def clamp(self, literals, bound):
        if bound < 0:
            self.base.append(())
        elif bound < len(literals):
            result = CardEnc.atmost(lits=literals, bound=bound, top_id=self.variables, encoding=EncType.seqcounter)
            self.variables = max(result.nv, self.variables)
            self.base.extend(tuple(clause) for clause in result.clauses)

    def clause(self, region, picked):
        domain, order = self.domains[region]
        assert picked & domain == picked and picked.bit_count() == order
        assert all(not self.lower[vertex] & picked for vertex in bits(picked))
        return tuple(variable for (first, second), variable in self.edge_id.items() if picked >> first & 1 and picked >> second & 1)

    def model(self, values):
        adj = list(self.lower)
        for (first, second), value in zip(self.edges, values):
            if value > 0:
                adj[first] |= 1 << second
                adj[second] |= 1 << first
        assert tuple(row.bit_count() for row in adj) == self.degrees
        assert not any(adj[vertex] & adj[peer] for vertex, row in enumerate(adj) for peer in bits(row))
        return tuple(adj)

    def search(self, budget, max_witnesses):
        start = process_time()
        seen = set()
        blockers = []
        with Solver(name='cadical195', bootstrap_with=self.base) as solver:
            while process_time()-start < budget and len(blockers) < max_witnesses:
                solver.conf_budget(15000)
                verdict = solver.solve_limited()
                if verdict is None:
                    continue
                if not verdict:
                    return 'UNSAT_FOR_LRAT', blockers, None
                values = solver.get_model()[:len(self.edges)]
                assert tuple(map(abs, values)) == tuple(range(1, len(self.edges)+1))
                adj = self.model(values)
                found = 0
                for region, (domain, order) in enumerate(self.domains):
                    folded = 0
                    for picked in witnesses(adj, domain, order):
                        clause = self.clause(region, picked)
                        if clause in seen:
                            continue
                        seen.add(clause)
                        assert all(values[literal-1] < 0 for literal in clause)
                        solver.add_clause(clause)
                        blockers.append((region, picked))
                        folded += 1
                        found += 1
                        if folded == 32:
                            break
                if not found:
                    assert all(next(witnesses(adj, domain, order), None) is None for domain, order in self.domains)
                    return 'LIFT', blockers, adj
        return 'OPEN_LIMIT', blockers, None


def check_child(command, budget, wall=None):
    return subprocess.run(['timeout', '-k', '2s', f'{wall or 2*budget}s', 'prlimit', f'--cpu={budget}:{budget+1}', '--',
                           *map(str, command)], capture_output=True, check=False)


def proof(lift, directory, blockers, budget):
    cnf_raw = dimacs(lift.variables, (*lift.base, *(lift.clause(*row) for row in blockers)))
    cnf, lrat = directory/'formula.cnf', directory/'proof.lrat'
    cnf.write_bytes(cnf_raw)
    run = check_child([TOOLS/'cadical', '-q', '--lrat', '--no-binary', cnf, lrat], budget)
    report = [(run.returncode, run.stdout.decode('utf-8', 'replace')[-2048:])]
    verdict, proof_sha, size = f'OPEN_SOLVE_{run.returncode}', None, 0
    if run.returncode == 20:
        first = check_child([TOOLS/'cake_lpr', '--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=64', cnf, lrat], budget)
        second = check_child([TOOLS/'lrat-check', cnf, lrat], budget)
        report.extend((item.returncode, item.stdout.decode('utf-8', 'replace')[-4096:]) for item in (first, second))
        if (first.returncode == second.returncode == 0 and b's VERIFIED UNSAT' in first.stdout.splitlines()
                and any(line.rstrip() == b'c VERIFIED' for line in second.stdout.splitlines())):
            raw = lrat.read_bytes()
            size = len(raw)
            proof_sha = sha256(raw).hexdigest()
            (directory/'proof.lrat.gz').write_bytes(gzip.compress(raw, mtime=0))
            verdict = 'CHECKED'
        else:
            verdict = 'OPEN_CHECK'
    (directory/'check.json').write_text(json.dumps(report) + '\n', encoding='ascii')
    cnf.unlink()
    lrat.unlink(missing_ok=True)
    return verdict, sha256(cnf_raw).hexdigest(), proof_sha, size


def control(output):
    card = graph(4, [(0, 1), (0, 2), (0, 3)])
    groups = (2, 4, 8)
    totals = Counter()
    for limit, expected in ((4, 'LIFT'), (3, 'UNSAT_FOR_LRAT')):
        lift = Lift(card, 1, groups, 1, 4, 1, limit, 5, 2)
        status, blockers, model = lift.search(5, 1000)
        assert status == expected and (model is not None) == (status == 'LIFT')
        if model is not None:
            assert model == graph(5, [(0, leaf) for leaf in range(1, 5)])
        assert all(lift.clause(*row) for row in blockers)
        totals[status] += 1
        if status == 'UNSAT_FOR_LRAT':
            output.mkdir(exist_ok=False)
            result = proof(lift, output, blockers, 5)
            assert result[0] == 'CHECKED', result
    print('smaller full addback controls', dict(totals), flush=True)


def target(entry):
    _, key, core, groups = entry
    adj = from_graph6(key)
    assert len(adj) == 26 and sum(row.bit_count() for row in adj) == 148
    return Lift(adj, core, tuple(groups), 6, 8, 7, 8, 10, 7)


def augment(adj, groups):
    count = len(adj)
    wings = tuple((count + 2*role, count + 2*role + 1) for role in range(4))
    preserved = [(first, second) for first, row in enumerate(adj) for second in bits(row) if first < second]
    attach = [(vertex, moved) for sites, wing in zip(groups, wings) for vertex in bits(sites) for moved in wing]
    crown = [(left[0], right[1]) for left, right in product(wings, repeat=2) if left != right]
    return graph(count + 8, (*preserved, *attach, *crown))


def run(plan, output, offset, stride, lazy_budget, proof_budget, max_witnesses, indexes=None):
    rows = [json.loads(line) for line in plan.read_text(encoding='ascii').splitlines()]
    output.mkdir(exist_ok=True)
    with (output/f'worker.{offset}.jsonl').open('x', encoding='ascii', buffering=1) as stream:
        for index in list(range(offset, len(rows), stride)) if indexes is None else indexes:
            start = process_time()
            directory = output/f'{index:05d}'
            directory.mkdir()
            lift = target(rows[index])
            status, blockers, model = lift.search(lazy_budget, max_witnesses)
            (directory/'witnesses.json').write_text(json.dumps(blockers, separators=(',', ':')) + '\n', encoding='ascii')
            result = (status, None, None, 0)
            if status == 'UNSAT_FOR_LRAT':
                result = proof(lift, directory, blockers, proof_budget)
            elif status == 'LIFT':
                assert model is not None
                candidate = augment(model, lift.groups)
                assert not any(candidate[first] & candidate[second] for first, row in enumerate(candidate) for second in bits(row))
                assert not next(witnesses(candidate, (1 << len(candidate)) - 1, 10), None)
                (directory/'target.g6').write_text(to_graph6(candidate) + '\n', encoding='ascii')
            print(json.dumps((index, *result, len(blockers), round(process_time()-start, 4)), separators=(',', ':')), file=stream)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='mode', required=True)
    commands.add_parser('control').add_argument('output', type=Path)
    batch = commands.add_parser('run')
    batch.add_argument('plan', type=Path)
    batch.add_argument('output', type=Path)
    batch.add_argument('--offset', type=int, default=0)
    batch.add_argument('--stride', type=int, default=1)
    batch.add_argument('--lazy', type=int, default=10)
    batch.add_argument('--proof', type=int, default=12)
    batch.add_argument('--witnesses', type=int, default=25000)
    batch.add_argument('--indexes', type=int, nargs='+')
    batch.add_argument('--skip', type=int, nargs='*', default=[])
    args = parser.parse_args()
    if args.mode == 'control':
        control(args.output)
    else:
        indexes = args.indexes
        if args.skip:
            assert indexes is None
            indexes = [index for index, line in enumerate(args.plan.open(encoding='ascii'))
                       if index % args.stride == args.offset and index not in args.skip]
        run(args.plan, args.output, args.offset, args.stride, args.lazy, args.proof, args.witnesses, indexes)


if __name__ == '__main__':
    main()
