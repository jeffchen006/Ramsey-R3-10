#!/usr/bin/env python3
"""Exact-checkable extensions of the degree-class LP. See rows/*.md."""

from itertools import combinations, combinations_with_replacement
from math import comb

import degseq as baseline
from etables import e3


RAMSEY = {1: 1, 2: 3, 3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36}
FAMILIES = ("profiles", "wedge", "private", "internal", "pair")
PRESENT = {
    "profiles": {"profiles"},
    "wedge": {"profiles", "wedge"},
    **{name: {"profiles", "wedge", name} for name in FAMILIES[2:]},
    "all": set(FAMILIES),
    "lifted": {"profiles", "wedge", "lifted"},
    "combined": set(FAMILIES) | {"lifted"},
    "packing": set(FAMILIES) | {"lifted", "packing"},
}


def incidences(first, second, degree):
    return int(first == degree) + int(second == degree)


class Model:
    def __init__(self):
        self.bounds = {}
        self.rows = []

    def col(self, key, ub):
        assert key not in self.bounds and ub >= 0, (key, ub)
        self.bounds[key] = ub
        return key

    def le(self, coefficients, rhs, name):
        row = {key: val for key, val in coefficients.items() if val}
        assert row.keys() <= self.bounds.keys(), (name, row.keys() - self.bounds.keys())
        self.rows.append((row, rhs, name))

    def eq(self, coefficients, rhs, name):
        self.le(coefficients, rhs, name + "+")
        self.le({key: -val for key, val in coefficients.items()}, -rhs, name + "-")


def min_z_mtf(order, alpha, degree):
    return degree + 2 * (order - 1 - degree) - degree * (alpha + 1 - degree)


def add_lifted(model, profiles, counts, degrees, edges, order, alpha, mtf, packing):
    pair_caps = {key[1:]: upper for key, upper in model.bounds.items() if key[0] == "p"}
    links = {}
    for first, second, common in pair_caps:
        pair_key = ("p", first, second, common)
        links[first, second, common] = {pair_key: -(1 + (first == second))}
        if first != second:
            links[second, first, common] = {pair_key: -1}

    cap_deficit = order - RAMSEY[alpha - 1] - 1
    for root in degrees:
        exterior_order = order - 1 - root
        for profile, hist, weighted in profiles[root]:
            root_edges = edges - weighted
            exterior_counts = {degree: counts[degree] - hist[degree] - (degree == root)
                               for degree in degrees}
            total_codegree = {profile: -(weighted - root)}
            private = {profile: -root * (alpha + 1 - root)}
            internal = {profile: -exterior_order * root_edges}
            choose = lambda number, size: comb(number, size) if 0 <= size <= number else 0
            if packing:
                subset = {size: {profile: -comb(root, size) * (RAMSEY[alpha + 1 - size] - 1 - (root - size))}
                          for size in range(2, root + 1)}
                major = {size: {profile: sum(degree - 1 for degree in profile[2][-size:])}
                         for size in range(1, root)}
                two = {profile: -sum(min(first, second, first + second - cap_deficit) - 1
                                     for first, second in combinations(profile[2], 2))}
            for other, available in exterior_counts.items():
                if not available:
                    continue
                remaining = [degree for degree in degrees
                             for _ in range(exterior_counts[degree] - (degree == other))]
                mass = {profile: -available}
                first, second = sorted((root, other))
                for common in range(int(mtf), min(root, other, root + other - cap_deficit) + 1):
                    if (first, second, common) not in pair_caps:
                        continue
                    residual = other - common
                    if residual > min(alpha - 1, len(remaining)):
                        continue
                    sub_order = exterior_order - 1 - residual
                    lower = e3(alpha - 1, sub_order)
                    upper = min(sub_order * (alpha - 2) // 2, sub_order**2 // 4)
                    crossing_caps = lambda degree: min(root - common, max(0, root + degree - cap_deficit))
                    cheapest = sorted(degree - crossing_caps(degree) for degree in remaining)
                    if root_edges - sum(cheapest[:residual]) < lower:
                        continue
                    cross_lower = max(0, root + other - common - alpha)
                    if mtf:
                        cross_lower = max(cross_lower, root - common, residual)
                    if root_edges - sum(remaining[len(remaining) - residual:]) + cross_lower > upper:
                        continue
                    key = model.col(("q", root, profile[2], other, common), available * counts[root])
                    mass[key] = 1
                    links[root, other, common][key] = 1
                    total_codegree[key] = common
                    if common == 1:
                        private[key] = 1
                    internal[key] = residual**2 + lower
                    if packing:
                        for size, coeff in subset.items():
                            coeff[key] = choose(root - common, size)
                        for size, coeff in major.items():
                            coeff[key] = -min(common, size)
                        two[key] = comb(common, 2)
                model.eq(mass, 0, f"lifted_mass_{root}_{profile[2]}_{other}")
            model.eq(total_codegree, 0, f"lifted_codegree_{root}_{profile[2]}")
            model.le(private, 0, f"lifted_private_{root}_{profile[2]}")
            model.le(internal, 0, f"lifted_internal_{root}_{profile[2]}")
            if packing:
                for size, coeff in subset.items():
                    model.le(coeff, 0, f"root_subset_{root}_{profile[2]}_{size}")
                for size, coeff in major.items():
                    model.le(coeff, 0, f"root_majorisation_{root}_{profile[2]}_{size}")
                model.le(two, 0, f"root_second_moment_{root}_{profile[2]}")
    for pair, coeff in links.items():
        model.eq(coeff, 0, f"lifted_link_{pair}")


def build(counts, lower, order, alpha, mtf, families):
    degrees = sorted(degree for degree, size in counts.items() if size)
    pairs = list(combinations_with_replacement(degrees, 2))
    edges = sum(degree * counts[degree] for degree in degrees) // 2
    model = Model()
    if order == 40 and alpha == 9:
        distribution = tuple(counts.get(degree, 0) for degree in baseline.DEGS)
        variables, rows, upper = baseline.build_lp(distribution, lower, mtf=mtf)
        for first, second in variables:
            model.col(("m", first, second), upper[first, second])
        for coefficients, rhs, name in rows:
            model.le({("m", *key): val for key, val in coefficients.items()}, rhs, "base_" + name)
    else:
        for first, second in pairs:
            upper = comb(counts[first], 2) if first == second else counts[first] * counts[second]
            model.col(("m", first, second), upper)

    profiles = {}
    for degree in degrees:
        info = profiles[degree] = []
        for multiset in combinations_with_replacement(degrees, degree):
            hist = {other: multiset.count(other) for other in degrees}
            if any(hist[other] > counts[other] - (other == degree) for other in degrees):
                continue
            weighted = sum(multiset)
            if edges - weighted < lower[degree]:
                continue
            if mtf and weighted < min_z_mtf(order, alpha, degree):
                continue
            key = model.col(("x", degree, multiset), counts[degree])
            info.append((key, hist, weighted))
        model.eq({key: 1 for key, _, _ in info}, counts[degree], f"profile_mass_{degree}")
        for other in degrees:
            coeff = {key: hist[other] for key, hist, _ in info}
            coeff[("m", *sorted((degree, other)))] = -(1 + (degree == other))
            model.eq(coeff, 0, f"profile_link_{degree}_{other}")

    if "wedge" not in families:
        return model

    internal = {degree: {} for degree in degrees}
    private = {degree: {} for degree in degrees}
    endpoint_z = {degree: {} for degree in degrees}
    paths = {degree: {} for degree in degrees}

    for first, second in pairs:
        total = comb(counts[first], 2) if first == second else counts[first] * counts[second]
        max_common = min(first, second, first + second + RAMSEY[alpha - 1] + 1 - order)
        pair_mass = {("m", first, second): 1}
        typed_wedge = {center: {} for center in degrees}
        wedge = {}
        globals_present = all(profiles[degree] for degree in (first, second))
        for common in range(int(mtf), max_common + 1) if globals_present else ():
            if not total:
                continue
            external = order - 2 - first - second + common
            if external < 0 or min(first, second) - common < 0:
                continue
            if "internal" in families and max(first, second) - common >= alpha:
                continue
            key = model.col(("p", first, second, common), total)
            pair_mass[key] = 1
            wedge[key] = common
            for degree in set((first, second)):
                other = first + second - degree
                factor = incidences(first, second, degree)
                if common == 1:
                    private[degree][key] = factor
                if "internal" in families:
                    residual = other - common
                    internal[degree][key] = factor * (residual**2 + e3(alpha - 1, external))
                if "pair" in families:
                    paths[degree][key] = factor * common * (common - 1)

            if "pair" not in families:
                continue
            upper_x = min(external * (alpha - 2) // 2, external * external // 4)
            lower_x = e3(alpha - 1, external)
            side_a, side_b = first - common, second - common
            cross_upper = side_a * side_b
            cross_lower = max(0, first + second - common - alpha)
            if mtf:
                cross_lower = max(cross_lower, side_a, side_b)
            cross = model.col(("f", first, second, common), total * cross_upper)
            model.le({cross: 1, key: -cross_upper}, 0, "f_max")
            model.le({cross: -1, key: cross_lower}, 0, "f_min")
            above = {key: edges - upper_x, cross: 1}
            common_mass = {key: -common}
            for degree in degrees:
                upper_common = min(common, counts[degree] - incidences(first, second, degree))
                if upper_common <= 0:
                    continue
                shared = model.col(("w", first, second, common, degree), total * upper_common)
                model.le({shared: 1, key: -upper_common}, 0, "shared_max")
                typed_wedge[degree][shared] = 1
                common_mass[shared] = 1
                above[shared] = degree
            model.eq(common_mass, 0, "shared_total")
            for degree in set((first, second)):
                factor = incidences(first, second, degree)
                values = [weighted for _, _, weighted in profiles[degree]]
                upper_z, lower_z = max(values) * factor, min(values) * factor
                weighted_key = model.col(("z", first, second, common, degree), total * upper_z)
                model.le({weighted_key: 1, key: -upper_z}, 0, "endpoint_z_max")
                model.le({weighted_key: -1, key: lower_z}, 0, "endpoint_z_min")
                endpoint_z[degree][weighted_key] = 1
                above[weighted_key] = -1
                paths[degree][cross] = factor
            below = {column: -value for column, value in above.items()}
            below[key] = lower_x - edges
            model.le(below, 0, "pair_e_min")
            model.le(above, 0, "pair_e_max")

        model.eq(pair_mass, total, f"pair_mass_{first}_{second}")
        for center, info in profiles.items():
            coeff = typed_wedge[center] if "pair" in families else wedge
            for column, hist, _ in info:
                count = comb(hist[first], 2) if first == second else hist[first] * hist[second]
                coeff[column] = -count
            if "pair" in families:
                model.eq(coeff, 0, f"typed_wedge_{first}_{second}_{center}")
        if "pair" not in families:
            model.eq(wedge, 0, f"wedge_{first}_{second}")

    for degree, info in profiles.items():
        external = order - 1 - degree
        if "private" in families:
            model.le(private[degree], counts[degree] * degree * (alpha + 1 - degree), f"private_{degree}")
        if "internal" in families:
            coeff = internal[degree]
            coeff.update({column: -external * (edges - weighted) for column, _, weighted in info})
            model.le(coeff, 0, f"internal_{degree}")
        if "pair" in families:
            coeff = endpoint_z[degree]
            coeff.update({column: -external * weighted for column, _, weighted in info})
            model.eq(coeff, 0, f"endpoint_z_{degree}")
            coeff = paths[degree]
            for center_profiles in profiles.values():
                for column, hist, weighted in center_profiles:
                    coeff[column] = -hist[degree] * (weighted - column[1] - (degree - 1))
            model.eq(coeff, 0, f"paths_{degree}")
    if "lifted" in families:
        add_lifted(model, profiles, counts, degrees, edges, order, alpha, mtf, "packing" in families)
    return model
