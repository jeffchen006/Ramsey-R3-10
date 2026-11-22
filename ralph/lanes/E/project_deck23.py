#!/usr/bin/env python3
"""Refute or recover the 26-vertex card of a marked high-degree residue."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
from time import process_time

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from cubic32 import pin_graph
from involution_cores import bits, graph
from involution_sat import from_graph6, to_graph6, witnesses
from lift_deck23 import proof
from m11_sat import FastCuts, calibration, encode
from residue8_23 import admissible as extreme_roster
from residue23 import degree_vector, roster_cells


class CardinalRows:
    def __init__(self, variables, base):
        self.variables, self.base = variables, base

    def new(self):
        self.variables += 1
        return self.variables

    def cap(self, literals, bound, guard=()):
        if bound < 0:
            self.base.append(tuple(guard))
        elif bound < len(literals):
            row = CardEnc.atmost(lits=literals, bound=bound, top_id=self.variables, encoding=EncType.seqcounter)
            self.variables = max(self.variables, row.nv)
            self.base.extend((*guard, *clause) for clause in row.clauses)

    def equality(self, literals, target):
        self.cap(literals, target)
        self.cap([-value for value in literals], len(literals)-target)

    def designated(self, row, high):
        marker = self.new()
        self.cap(row, high-1, (marker,))
        self.cap([-value for value in row], len(row)-high, (-marker,))
        return marker


class Projection(CardinalRows):
    def __init__(self, key, groups, residue, high_count, fast, cut_size):
        core = tuple(from_graph6(key))
        core_edges = sum(row.bit_count() for row in core)//2
        small_degrees = [degree_vector(group, 8) for group in groups]
        if core_edges == 10:
            assert high_count in roster_cells(core, small_degrees, list(residue))
        else:
            assert core_edges == 8 and extreme_roster(core, groups, residue, high_count)
        variables, base, pinned, edges = encode(core, groups, (None,)*3, edge_target=74,
                                                cut_size=cut_size, fast=fast)
        super().__init__(variables, base)
        _, parts = pin_graph(core, groups)
        self.pinned, self.edges = tuple(pinned), edges
        self.domain = (1 << len(pinned))-1
        self.high_count = high_count
        self.parts = parts
        self.budgets = tuple(high_count - row.count(1) for row in small_degrees)
        assert all(0 <= limit <= 2 for limit in self.budgets)
        self.special = {}
        for vertex in range(len(core), len(pinned)):
            incident = [variable for edge, variable in edges.items() if vertex in edge]
            need = 7 - pinned[vertex].bit_count()
            self.special[vertex] = self.designated(incident, need)
        assert tuple(row.bit_count() for row in pinned[:8]) == tuple(7-row for row in residue)
        outside_count = high_count - residue.count(0)
        self.equality(list(self.special.values()), outside_count)
        for left, right in combinations(self.special, 2):
            constraint = (-self.special[left], -self.special[right])
            variable = self.edges.get((left, right))
            if variable is not None:
                constraint += (variable,)
            self.base.append(constraint)
        for omitted, block in enumerate(parts):
            absence = []
            for vertex in (site for index, part in enumerate(parts) if index != omitted for site in part):
                incident = [edges[pair] for peer in block if (pair := tuple(sorted((vertex, peer)))) in edges]
                if self.budgets[omitted] == 0:
                    self.base.append(tuple(incident))
                else:
                    marker = self.new()
                    absence.append(marker)
                    self.base.append(tuple((*incident, marker)))
            if absence:
                self.cap(absence, self.budgets[omitted])
        if any(not clause for clause in self.base):
            contradictory = self.new()
            self.base = [clause if clause else (contradictory,) for clause in self.base]
            self.base.append((-contradictory,))

    def clause(self, picked):
        assert picked & self.domain == picked and picked.bit_count() == 8
        assert not any(self.pinned[vertex] & picked for vertex in bits(picked))
        return tuple(variable for (left, right), variable in self.edges.items() if picked >> left & 1 and picked >> right & 1)

    def decode(self, model):
        result = list(self.pinned)
        for (left, right), variable in self.edges.items():
            if model[variable-1] == variable:
                result[left] |= 1 << right
                result[right] |= 1 << left
        degrees = [row.bit_count() for row in result]
        assert degrees.count(7) == self.high_count and max(degrees) <= 7 and sum(degrees) == 148
        assert not any(result[vertex] & result[peer] for vertex, row in enumerate(result) for peer in bits(row))
        for left, right in combinations((vertex for vertex in self.special if degrees[vertex] == 7), 2):
            assert result[left] >> right & 1
        for left, budget in zip(self.parts, self.budgets):
            block = sum(1 << peer for peer in left)
            assert sum(not result[vertex] & block for right in self.parts if right != left for vertex in right) <= budget
        return tuple(result)

    def discover(self, budget, cut_limit):
        start = process_time()
        seen = set()
        cuts = []
        with Solver(name='cadical195', bootstrap_with=self.base) as solver:
            while process_time() - start < budget and len(cuts) < cut_limit:
                solver.conf_budget(10000)
                status = solver.solve_limited()
                if status is False:
                    return 'UNSAT_FOR_LRAT', cuts, None
                if status is None:
                    continue
                model = solver.get_model()
                adj = self.decode(model)
                blocked = 0
                for picked in witnesses(adj, self.domain, 8):
                    clause = self.clause(picked)
                    assert all(model[variable-1] < 0 for variable in clause)
                    if clause in seen:
                        continue
                    seen.add(clause)
                    cuts.append((picked,))
                    solver.add_clause(clause)
                    blocked += 1
                    if blocked == 48:
                        break
                if not blocked:
                    assert not next(witnesses(adj, self.domain, 8), None)
                    return 'MISSING_CARD', cuts, adj
        return 'OPEN_LAZY', cuts, None


def control(fast):
    calibration(fast)
    checks = 0
    for target in range(5):
        rows = CardinalRows(4, [])
        marker = rows.designated([1, 2, 3, 4], target)
        with Solver(name='cadical195', bootstrap_with=rows.base) as solver:
            for selection in product((False, True), repeat=4):
                pins = [index if chosen else -index for index, chosen in enumerate(selection, 1)]
                literal = marker if sum(selection) >= target else -marker
                assert solver.solve(assumptions=[*pins, literal])
                assert not solver.solve(assumptions=[*pins, -literal])
                checks += 1
    print('projection cardinality physical truth-table', checks, flush=True)


def run(args, fast):
    rows = [json.loads(line) for line in args.plan.read_text(encoding='ascii').splitlines()]
    args.output.mkdir(exist_ok=True)
    with (args.output/f'worker.{args.offset}.jsonl').open('x', encoding='ascii', buffering=1) as log:
        index_set = args.indexes if args.indexes is not None else [index for index in range(args.offset, len(rows), args.stride) if index not in args.skip]
        stats = Counter()
        archive_bytes = 0
        for index in index_set:
            if archive_bytes >= args.archive_limit:
                stats['OPEN_ARCHIVE_LIMIT'] += 1
                print(json.dumps((index, 'OPEN_ARCHIVE_LIMIT', None, None, 0, 0, 0)), file=log)
                continue
            key, group, residue, high = rows[index]
            start = process_time()
            projected = Projection(key, group, residue, high, fast, args.width)
            status, cut, card = projected.discover(args.lazy, args.max_witnesses)
            detail = (status, None, None, 0)
            directory = args.output/f'{index:07d}'
            directory.mkdir()
            (directory/'witnesses.json').write_text(json.dumps(cut, separators=(',', ':'))+'\n', encoding='ascii')
            if status == 'UNSAT_FOR_LRAT':
                detail = proof(projected, directory, cut, args.proof)
            if status == 'MISSING_CARD':
                (directory/'card.g6').write_text(to_graph6(card)+'\n', encoding='ascii')
            archive_bytes += sum(path.stat().st_size for path in directory.iterdir())
            stats[detail[0]] += 1
            print(json.dumps((index, *detail, len(cut), round(process_time()-start, 4)), separators=(',', ':')), file=log)
        print('projection terminal', args.offset, dict(stats), 'archive_bytes', archive_bytes, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fast', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('control')
    command = sub.add_parser('run')
    command.add_argument('plan', type=Path)
    command.add_argument('output', type=Path)
    command.add_argument('--lazy', type=int, default=6)
    command.add_argument('--proof', type=int, default=10)
    command.add_argument('--width', type=int, default=3)
    command.add_argument('--max-witnesses', type=int, default=25000)
    command.add_argument('--archive-limit', type=int, default=32*1024**2)
    command.add_argument('--offset', type=int, default=0)
    command.add_argument('--stride', type=int, default=1)
    command.add_argument('--indexes', type=int, nargs='+')
    command.add_argument('--skip', type=int, nargs='*', default=())
    args = parser.parse_args()
    fast = FastCuts(args.fast)
    if args.mode == 'control':
        control(fast)
    else:
        run(args, fast)
