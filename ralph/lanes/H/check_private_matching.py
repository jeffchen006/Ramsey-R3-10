"""Literal small physical graphs for the private-cell matching interface."""

from itertools import product


def alpha(left, right, isolated, edges):
    order = left + right + isolated
    return max(
        mask.bit_count()
        for mask in range(1 << order)
        if all(not (mask >> site & 1 and mask >> (left + target) & 1) for site, target in edges)
    )


def largest_matching(left, right, edges):
    best = 0
    for trial in product(range(-1, right), repeat=left):
        real = [target for target in trial if target != -1]
        if len(real) != len(set(real)):
            continue
        if all(target == -1 or (site, target) in edges for site, target in enumerate(trial)):
            best = max(best, len(real))
    return best


def hall_deficiency(left, right, edges):
    return max(
        len(sites) - len({target for site in sites for target in range(right) if (site, target) in edges})
        for flags in product((False, True), repeat=left)
        for sites in [{site for site, take in enumerate(flags) if take}]
    )


def exhaustive():
    count = 0
    for left, right in ((0, 2), (1, 2), (2, 2), (2, 3)):
        possible = list(product(range(left), range(right)))
        for flags in product((False, True), repeat=len(possible)):
            edges = frozenset(edge for edge, present in zip(possible, flags) if present)
            maximum = largest_matching(left, right, edges)
            deficiency = hall_deficiency(left, right, edges)
            for isolated in (0, 1):
                bound = alpha(left, right, isolated, edges)
                assert bound == right + isolated + deficiency
                assert maximum == left + right + isolated - bound
                count += 1
    assert count == 170
    return count


def planted():
    twin = {(0, 0)}
    assert (alpha(2, 2, 0, twin), largest_matching(2, 2, twin)) == (3, 1)
    assert (alpha(2, 2, 1, twin), largest_matching(2, 2, twin)) == (4, 1)
    perfect = twin | {(1, 1)}
    assert (alpha(2, 2, 1, perfect), largest_matching(2, 2, perfect)) == (3, 2)

    perfect = {(site, site) for site in range(4)}
    near_perfect = perfect - {(3, 3)}
    assert (alpha(4, 4, 0, near_perfect), largest_matching(4, 4, near_perfect)) == (5, 3)
    assert (alpha(4, 4, 1, perfect), largest_matching(4, 4, perfect)) == (5, 4)
    assert (alpha(4, 4, 1, near_perfect), largest_matching(4, 4, near_perfect)) == (6, 3)

    repeated = {(site, 0) for site in range(3)} | {(3, 1), (3, 2)}
    assert len({target for _, target in repeated}) == 3
    assert (alpha(4, 4, 0, repeated), largest_matching(4, 4, repeated)) == (6, 2)


if __name__ == "__main__":
    print(f"PASS: {exhaustive()} exhaustive small physical graphs, with/without isolated site")
    planted()
    print("PASS: tight 2+2 and 4+4 controls; isolated-cap and double-site-reuse mutations rejected")
