"""A necessary fixed-boundary relaxation retaining only selected Ramsey rows."""

from itertools import combinations, product

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

from kernel_projection import bits
from path_four_factor import independent_sets


def formula_minimal(core, boundary, degree, cap, min_size, retain_saturated, uncapped_roots=()):
    order, outside = len(core), len(boundary)
    nonroots = outside - 3
    clauses, pool = CNF(), IDPool()
    edges = {(inner, outer): pool.id(('edge', inner, outer))
             for inner, outer in product(range(order), range(nonroots))}

    def atmost(literals, target):
        literals = list(literals)
        if target < 0:
            clauses.append([])
        elif target == 0:
            clauses.extend([[-literal] for literal in literals])
        elif target < len(literals):
            clauses.extend(CardEnc.atmost(literals, target, vpool=pool, encoding=EncType.seqcounter))

    def exactly(literals, target):
        literals = list(literals)
        atmost(literals, target)
        atmost((-literal for literal in literals), len(literals) - target)

    for inner, adjacent in enumerate(core):
        exactly((edges[inner, outer] for outer in range(nonroots)), degree - adjacent.bit_count())
    for outer, adjacent in enumerate(boundary):
        exactly((edges[inner, outer] for inner in range(order) if outer < nonroots), degree - adjacent.bit_count())

    def fixed_pair(adj, pairs):
        for first, second in combinations(range(len(adj)), 2):
            common = (adj[first] & adj[second]).bit_count()
            if adj[first] >> second & 1:
                if common:
                    clauses.append([])
                clauses.extend([[-left, -right] for left, right in pairs(first, second)])
                continue
            selectors = []
            for left, right in pairs(first, second):
                selector = pool.id(('overlap', left, right))
                clauses.extend([[-selector, left], [-selector, right], [selector, -left, -right]])
                selectors.append(selector)
            atmost(selectors, cap - common)
            if not common:
                clauses.append(selectors)

    fixed_pair(core, lambda first, second: ((edges[first, outer], edges[second, outer]) for outer in range(nonroots)))
    fixed_pair(boundary, lambda first, second: ((edges[inner, first], edges[inner, second])
                                               for inner in range(order) if second < nonroots))
    for inner, outer in product(range(order), range(outside)):
        common = [edges[inner, neighbour] for neighbour in bits(boundary[outer]) if neighbour < nonroots]
        if outer < nonroots:
            common.extend(edges[neighbour, outer] for neighbour in bits(core[inner]))
        atmost(common, cap if outer < nonroots or outer in uncapped_roots else cap - 1)
        edge = edges.get((inner, outer))
        clauses.append([*common, edge] if edge is not None else common)

    maximals = []
    for group in independent_sets(boundary, (1 << outside) - 1):
        covered = group
        for outer in bits(group):
            covered |= boundary[outer]
        if covered.bit_count() == outside:
            maximals.append((group.bit_count(), list(bits(group & ((1 << nonroots) - 1))),
                             (group >> nonroots).bit_count()))
    for independent in independent_sets(core, (1 << order) - 1):
        size = independent.bit_count()
        selected = [group for group in maximals if size + group[0] > degree
                    and (size <= 1 or size >= min_size or (retain_saturated and group[0] == degree))]
        if not selected:
            continue
        if not size:
            clauses.append([])
            continue
        available = {}
        for _, group, roots in selected:
            for outer in group:
                if outer not in available:
                    choices = [edges[inner, outer] for inner in bits(independent)]
                    if len(choices) == 1:
                        available[outer] = -choices[0]
                    else:
                        selected_literal = pool.id(('available', independent, outer))
                        clauses.append([selected_literal, *choices])
                        available[outer] = selected_literal
            atmost((available[outer] for outer in group), degree - size - roots)
    return clauses, edges
