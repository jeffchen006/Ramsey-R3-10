"""Redundant order-three degree and quotient rows for orbit SAT experiments."""
from collections import Counter
from functools import lru_cache
from itertools import combinations


RAMSEY = {1: 1, 2: 3, 3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36}


class Rows:
    def __init__(self, top):
        self.top = top
        self.clauses = []
        self.unions = {}

    def fresh(self):
        self.top += 1
        return self.top

    def add(self, *terms):
        if not any(term is True for term in terms):
            self.clauses.append(tuple(term for term in terms if term is not False))

    def disjunction(self, variables):
        variables = tuple(sorted(set(variables)))
        if len(variables) == 1:
            return variables[0]
        if variables not in self.unions:
            node = self.fresh()
            self.add(-node, *variables)
            for literal in variables:
                self.add(node, -literal)
            self.unions[variables] = node
        return self.unions[variables]

    def atleast(self, weights, bound, guard=()):
        choices = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
        suffix = [0] * (len(choices) + 1)
        for index in range(len(choices) - 1, -1, -1):
            suffix[index] = suffix[index + 1] + choices[index][1]

        @lru_cache(None)
        def suffix_node(index, needed):
            if needed <= 0:
                return True
            if needed > suffix[index]:
                return False
            literal, weight = choices[index]
            miss = suffix_node(index + 1, needed)
            hit = suffix_node(index + 1, needed - weight)
            if miss == hit:
                return miss
            result = self.fresh()
            self.add(-result, literal, miss)
            self.add(-result, -literal, hit)
            return result

        self.add(*guard, suffix_node(0, bound))
        suffix_node.cache_clear()

    def write(self, path):
        with open(path, 'w') as output:
            print('p cnf', self.top, len(self.clauses), file=output)
            for clause in self.clauses:
                print(*clause, 0, file=output)


def build(spec, pairmap, top, mode, dmin=None):
    size, target, fixed_count = (spec[field] for field in ('n', 'K', 'f'))
    assert spec['p'] == 3
    group_end = size - fixed_count
    moving = list(range(0, group_end, 3))
    fixed = list(range(group_end, size))
    rows = Rows(top)

    def edge(left, right):
        return pairmap[min(left, right), max(left, right)]

    def block(left, right):
        return [edge(left, right + shift) for shift in range(3)]

    if dmin is None:
        dmin = max(0, size - RAMSEY[target - 1])
    for rep in moving + fixed:
        degree = Counter(edge(rep, other) for other in range(size) if rep != other)
        rows.atleast(degree, dmin)
        rows.atleast({-literal: weight for literal, weight in degree.items()}, size - target)
    if mode == 'degree':
        return rows

    for rep in moving:
        rows.add(-edge(rep, rep + 1))
    quotient = {pair: rows.disjunction(block(*pair)) for pair in combinations(moving, 2)}

    def quotient_edge(left, right):
        return quotient[min(left, right), max(left, right)]

    max_attach = spec.get('amax', fixed_count)
    for count in range(1, 3):
        limit = target - 3 * count
        for reps in combinations(moving, count):
            if limit <= 0:
                rows.add(*(quotient[pair] for pair in combinations(reps, 2)))
                continue
            threshold = size - 3 * count - (RAMSEY[limit] - 1)
            if threshold <= 0:
                continue
            touching = [rows.disjunction(quotient_edge(rep, other) for rep in reps)
                        for other in moving if other not in reps]
            attaching = [rows.disjunction(edge(rep, vertex) for rep in reps) for vertex in fixed]
            guards = tuple(quotient[pair] for pair in combinations(reps, 2))
            coarse = max(0, (threshold - min(fixed_count, count * max_attach) + 2) // 3)
            if coarse >= len(touching):
                if coarse == len(touching):
                    for literal in touching:
                        rows.add(*guards, literal)
                    rows.atleast(dict.fromkeys(attaching, 1), threshold - 3 * coarse, guards)
                else:
                    rows.add(*guards)
            else:
                rows.atleast(dict.fromkeys(touching, 1), coarse, guards)
                rows.atleast(dict.fromkeys(touching, 3) | dict.fromkeys(attaching, 1), threshold, guards)

    if mode == 'quotient':
        return rows

    for count in range(1, (target // 3) + 1):
        needed = target - 3 * count
        if not 0 <= needed <= fixed_count:
            continue
        for reps in combinations(moving, count):
            guards = [quotient[pair] for pair in combinations(reps, 2)]
            if needed == 1 and fixed_count > count * max_attach:
                rows.add(*guards)
                continue
            for vertices in combinations(fixed, needed):
                rows.add(*guards, *(edge(*pair) for pair in combinations(vertices, 2)),
                         *(edge(rep, vertex) for rep in reps for vertex in vertices))
    return rows
