"""Physical incidence controls for the disjoint added-degree budget."""

from itertools import combinations, product


def check_budget(actual, prescribed, groups):
    assert prescribed <= actual and not groups[0] & groups[1]
    added = [len((actual - prescribed) & group) for group in groups]
    capacity = len(actual) - len(prescribed)
    for minima in product(*(range(count + 1) for count in added)):
        assert sum(minima) <= sum(added) <= capacity
    return sum(added) == capacity


def main():
    order = 13
    graph = [{(site + step) % order for step in (-5, -1, 1, 5)} for site in range(order)]
    assert all(len(row) == 4 and all(not row & graph[other] for other in row) for row in graph)
    assert not any(all(right not in graph[left] for left, right in combinations(sites, 2))
                   for sites in combinations(range(order), 5))

    cases = tight = 0
    for actual in graph:
        for allocation in product(range(4), repeat=len(actual)):
            prescribed, first, second, outside = [
                {site for site, label in zip(sorted(actual), allocation) if label == index}
                for index in range(4)]
            tight += check_budget(actual, prescribed, (first, second))
            assert len(outside) == len(actual) - len(prescribed) - len(first) - len(second)
            cases += 1
    assert (cases, tight) == (3328, 1053)
    actual = graph[0]
    site = min(actual)
    prescribed = actual - {site}
    assert check_budget(actual, prescribed, ({site}, set()))
    shared = ({site}, {site})
    assert shared[0] & shared[1] and sum(len(group - prescribed) for group in shared) > 1
    assert check_budget(actual, prescribed, (actual, set()))
    assert len(actual) > len(actual) - len(prescribed)
    print(f"C13(1,5): {cases} physical budgets, {tight} tight; "
          "overlapping-group and prescribed-double-count mutations both fail")


if __name__ == "__main__":
    main()
