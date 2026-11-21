"""Static mixed P4 Ramsey rows, optionally with one pinned cross pattern."""

from itertools import combinations, permutations, product

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

from kernel_projection import bits
from path_four_factor import Factor, independent_sets


def cross_shape(pattern, block):
    perms = list(permutations(range(block)))
    return min(sum(1 << (lefts[left] * block + rights[right])
                   for left, right in (divmod(index, block) for index in bits(pattern)))
               for lefts, rights in product(perms, repeat=2))


def cross_patterns(block, count):
    return sorted({cross_shape(sum(1 << index for index in inds), block)
                   for inds in combinations(range(block * block), count)})


def mixed_groups(sides, block, pattern):
    left, right = sides
    inner = left[block:] + right[:block]
    exterior_left, exterior_right = left[:block], right[block:]
    if pattern is None:
        return (inner + exterior_left, inner + exterior_right)
    groups = []
    for chosen in range(1 << block):
        remaining = (1 << block) - 1
        for offset in bits(chosen):
            remaining &= ~(pattern >> (offset * block))
        if any(not (remaining & (pattern >> (offset * block))) for offset in range(block)
               if not chosen >> offset & 1):
            continue
        groups.append(inner + tuple(exterior_left[idx] for idx in bits(chosen)) +
                      tuple(exterior_right[idx] for idx in bits(remaining)))
    return groups


class Mixed(Factor):
    def __init__(self, seed, degree, alpha, block, cap, pattern=None):
        super().__init__(seed, degree, alpha, block, cap)
        self.pattern = pattern

    def formula(self, sides, eager=True):
        cnf, literals, edges = super().formula(sides, eager)
        assert sides == (0, 1)
        pool = IDPool(start_from=cnf.nv + 1)
        yes, no = 1, -1
        if self.pattern is not None:
            for index, (left, right) in enumerate(self.cross):
                variable = literals[left][right]
                cnf.append([variable if self.pattern >> index & 1 else -variable])

        available = {}

        def availability(vertex, independent):
            hits = tuple(literals[vertex][other] for other in bits(independent)
                         if literals[vertex][other] != no)
            if yes in hits:
                return no
            if not hits:
                return yes
            if len(hits) == 1:
                return -hits[0]
            value = available.get(hits)
            if value is None:
                value = available[hits] = pool.id(('mixed-available', hits))
                cnf.append([value, *hits])
            return value

        groups = mixed_groups(self.sides, self.block, self.pattern)
        for independent in independent_sets(self.seed, (1 << (len(self.seed) - 2)) - 1):
            limit = self.alpha - independent.bit_count()
            for group in groups:
                if limit >= len(group):
                    continue
                values = [availability(vertex, independent) for vertex in group]
                bound = limit - values.count(yes)
                variables = [value for value in values if value not in (yes, no)]
                if bound < 0:
                    cnf.append([])
                elif bound < len(variables):
                    cnf.extend(CardEnc.atmost(variables, bound, vpool=pool, encoding=EncType.seqcounter))
        return cnf, literals, edges
