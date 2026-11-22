import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
import subprocess
from time import process_time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195

from reciprocal_audit import ROOT, SOURCE22, decode
from reciprocal_r12_reroot import add, attach_masks, bits, build_upper, independent, positive_cases, setup, sites


def pair(first, second):
    return (min(first, second), max(first, second))


class Projection:
    def __init__(self, host, mark, degree, cap, templates, wings):
        lower, left, right, common, region, outside, _ = setup(host, mark, degree, templates)
        deficit = sum(degree - lower[vertex].bit_count() for vertex in range(len(host)))
        doubled = degree * outside.bit_count() - 3 * (degree - 3) - deficit
        assert doubled % 2 == 0
        self.target = doubled // 2
        attach_masks(lower, common, wings)
        upper = build_upper(lower, region, outside, cap)
        self.lower, self.upper = lower, upper
        self.degree, self.cap = degree, cap
        self.outside = outside
        self.shared = region & ~(mark[0] | mark[1] | mark[2])
        self.centres = left + common
        self.window = self.shared | outside
        self.global_sites = (1 << len(lower)) - 1
        self.vars = {edge: index for index, edge in enumerate(
            ((first, second) for first, second in combinations(sites(self.window), 2)
             if upper[first] & ~lower[first] & (1 << second)), 1)}
        self.formula = CNF()
        self.pool = IDPool(start_from=len(self.vars) + 1)
        self.reasons = Counter()
        for point in sites(self.shared):
            self.eq([lit for edge, lit in self.vars.items() if point in edge],
                    degree - lower[point].bit_count())
        self.eq([lit for (first, second), lit in self.vars.items()
                 if outside & (1 << first) and outside & (1 << second)], self.target)
        for vertex in sites(outside):
            from_window = [lit for edge, lit in self.vars.items() if vertex in edge]
            degree_left = degree - lower[vertex].bit_count()
            maximum_cross = (upper[vertex] & ~self.window & ~lower[vertex]).bit_count()
            self.card('atmost', from_window, degree_left)
            self.card('atleast', from_window, degree_left - maximum_cross)
        for first, second, third in combinations(sites(self.window), 3):
            if (upper[first] >> second & upper[first] >> third & upper[second] >> third) & 1:
                self.formula.append([-self.vars[edge] for edge in ((first, second), (first, third), (second, third))
                                     if edge in self.vars])
        for root in self.centres:
            neighbourhood = lower[root] & self.window
            assert neighbourhood.bit_count() == degree - 3
            for vertex in sites(self.window ^ neighbourhood):
                if not (lower[vertex] & neighbourhood):
                    self.formula.append([self.vars[pair(vertex, other)] for other in sites(neighbourhood)
                                         if pair(vertex, other) in self.vars])

    def card(self, kind, literals, bound):
        if (kind == 'atleast' and bound <= 0) or (kind == 'atmost' and bound >= len(literals)):
            return
        if bound < 0 or bound > len(literals):
            self.formula.append([])
        else:
            self.formula.extend(getattr(CardEnc, kind)(lits=literals, bound=bound,
                                                        encoding=EncType.seqcounter, vpool=self.pool).clauses)

    def eq(self, literals, count):
        self.card('atmost', literals, count)
        self.card('atleast', literals, count)

    def models(self, literals):
        lower = list(self.lower)
        upper = list(self.upper)
        for (first, second), lit in self.vars.items():
            if lit in literals:
                add(lower, first, second)
            else:
                upper[first] ^= 1 << second
                upper[second] ^= 1 << first
        return lower, upper

    def negative(self, present_edges):
        return [-self.vars[edge] for edge in sorted(set(present_edges)) if edge in self.vars]

    def violation(self, lower, upper):
        for first, second in combinations(range(len(lower)), 2):
            shared = lower[first] & lower[second]
            if shared.bit_count() > self.cap:
                return 'cap', self.negative(pair(vertex, other)
                                            for vertex in (first, second)
                                            for other in tuple(sites(shared))[:self.cap + 1])
        for first in range(len(lower)):
            for second in sites(lower[first] & ~((1 << (first + 1)) - 1)):
                shared = lower[first] & lower[second]
                if shared:
                    third = next(sites(shared))
                    return 'triangle', self.negative([pair(first, second), pair(first, third), pair(second, third)])
        witness = independent(lower, self.window, self.degree - 2)
        if witness is not None:
            return 'window-IS', [self.vars[edge] for edge in combinations(sites(witness), 2) if edge in self.vars]
        for reroot in combinations(self.centres, 3):
            unavailable = bits(reroot)
            for root in reroot:
                unavailable |= upper[root]
            witness = independent(upper, self.global_sites ^ unavailable, self.degree - 2)
            if witness is not None:
                return 'reroot-IS', [self.vars[edge] for edge in combinations(sites(witness), 2) if edge in self.vars]
        return None

    def solve(self, planted=None, conflict_cap=8000, rounds=500):
        if planted is not None:
            for (first, second), lit in self.vars.items():
                self.formula.append([lit if planted[first] & (1 << second) else -lit])
        with Cadical195(bootstrap_with=self.formula.clauses) as solver:
            for _ in range(rounds):
                solver.conf_budget(conflict_cap)
                verdict = solver.solve_limited()
                if verdict is None:
                    return 'conflict-cap', ()
                if not verdict:
                    return 'UNSAT', ()
                model = set(solver.get_model())
                assert all(any(lit in model for lit in clause) for clause in self.formula.clauses)
                lower, upper = self.models(model)
                violation = self.violation(lower, upper)
                if violation is None:
                    self.check(lower)
                    return 'projection-SAT', tuple(edge for edge, lit in self.vars.items() if lit in model)
                reason, clause = violation
                self.reasons[reason] += 1
                self.formula.append(clause)
                solver.add_clause(clause)
        return 'iteration-cap', ()

    def check(self, lower):
        window = set(sites(self.window))
        outside = set(sites(self.outside))
        graph = [set(sites(row)) for row in lower]
        assert sum(len(graph[vertex] & outside) for vertex in outside) == 2 * self.target
        assert all(len(graph[vertex]) == self.degree for vertex in window - outside)
        assert all(len(graph[vertex]) <= self.degree for vertex in outside)
        assert all(not (graph[first] & graph[second]) for first, row in enumerate(graph) for second in row)
        assert max(len(first & second) for first, second in combinations(graph, 2)) <= self.cap
        for root in self.centres:
            for vertex in window - graph[root]:
                assert graph[vertex] & graph[root] & window
        assert all(any(graph[vertex] & set(choice) for vertex in choice)
                   for choice in combinations(sorted(window), self.degree - 2))


def certify(formula, folder, name):
    cnf, lrat = folder / (name + '.cnf'), folder / (name + '.lrat')
    formula.to_file(str(cnf))
    args = ['timeout', '18', 'prlimit', '--cpu=12:14', str(ROOT / 'opt/bin/cadical'),
            '--lrat', '--binary=false', str(cnf), str(lrat)]
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    cnf.with_suffix('.solve').write_text(result.stdout)
    if result.returncode != 20:
        return 'proof-capped', ()
    if [] in formula.clauses:
        lrat.write_text(f'{len(formula.clauses) + 1} 0 {1 + formula.clauses.index([])} 0\n')
    for program, signature in [('cake_lpr', 's VERIFIED UNSAT'), ('lrat-check', 'c VERIFIED')]:
        args = ['timeout', '18', 'prlimit', '--cpu=12:14', str(ROOT / 'opt/bin' / program), str(cnf), str(lrat)]
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        cnf.with_suffix('.' + program).write_text(result.stdout)
        assert result.returncode == 0 and signature in result.stdout
    return 'dual-LRAT', tuple(sha256(path.read_bytes()).hexdigest() for path in (cnf, lrat))


def controls(folder):
    for index, (host, mark, degree, cap, templates, planted) in enumerate(positive_cases()):
        _, _, _, common, _, outside, _ = setup(host, mark, degree, templates)
        wings = tuple(planted[vertex] & outside for vertex in common)
        good = Projection(host, mark, degree, cap, templates, wings)
        assert good.solve(planted)[0] == 'projection-SAT'
        bad = Projection(host, mark, degree, cap, templates, wings)
        wrong = next(edge for edge in bad.vars if planted[edge[0]] & (1 << edge[1]))
        mutant = list(planted)
        mutant[wrong[0]] ^= 1 << wrong[1]
        mutant[wrong[1]] ^= 1 << wrong[0]
        assert bad.solve(mutant)[0] == 'UNSAT'
        assert certify(bad.formula, folder, f'control-{index}-bad')[0] == 'dual-LRAT'
    print('C24 in two labelings: pinned genuine projections model-checked; pinned edge deletions dual LRAT', flush=True)


def select(journal, host_bank, per_bin, dense_only=False):
    groups = defaultdict(lambda: defaultdict(list))
    for line in journal.read_text().splitlines():
        raw, first, second, reason, *_ = line.split('\t')
        if reason != 'live':
            continue
        row, core, *mark = map(int, raw.split())
        edge_count = sum(mask.bit_count() for mask in host_bank[row]) // 2 - 45
        groups[edge_count][(row, core, *mark)].append((int(first), int(second)))
    random = Random(3101205)
    if dense_only:
        assert len(groups[20]) == 9 and all(len(rows) == 36 for rows in groups[20].values())
        for key, cases in sorted(groups[20].items()):
            assert len(set(cases)) == len(cases)
            for wings in sorted(cases):
                yield 20, key, wings
        return
    for edge_count, group in sorted(groups.items()):
        candidates = sorted(group)
        assert len(candidates) >= per_bin
        for index in range(per_bin):
            start, end = index * len(candidates) // per_bin, (index + 1) * len(candidates) // per_bin
            key = candidates[random.randrange(start, end)]
            yield edge_count, key, random.choice(group[key])


def pilot(journal, folder, per_bin, dense_only):
    host_bank = [[bits(row) for row in decode(line)] for line in SOURCE22.read_text().splitlines()]
    templates = (1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6)
    counts = Counter()
    with (folder / 'projection.jsonl').open('w') as output:
        for index, (edge_count, key, wings) in enumerate(select(journal, host_bank, per_bin, dense_only)):
            start = process_time()
            projection = Projection(host_bank[key[0]], key[2:], 9, 5, templates, wings)
            assert projection.target == edge_count
            status, model = projection.solve()
            receipt = ()
            if status == 'UNSAT':
                status, receipt = certify(projection.formula, folder, f'pilot-{index:02d}')
            counts[edge_count, status] += 1
            print(json.dumps(dict(index=index, edges=edge_count, key=key, wings=wings, result=status, model=model,
                                  counts=projection.reasons, receipt=receipt, cpu=round(process_time() - start, 6))),
                  file=output, flush=True)
            print(index, edge_count, status, dict(projection.reasons), round(process_time() - start, 4), flush=True)
    print('pilot totals', sorted(counts.items()), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    parser.add_argument('--pilot', type=Path)
    parser.add_argument('--per-bin', type=int, default=2)
    parser.add_argument('--dense-only', action='store_true')
    options = parser.parse_args()
    options.folder.mkdir(exist_ok=True, parents=True)
    controls(options.folder)
    if options.pilot:
        pilot(options.pilot, options.folder, options.per_bin, options.dense_only)
