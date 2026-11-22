"""Smaller literal controls for the single-deficit identities, not D's census."""

from itertools import product

from check_middle_star import physical_controls


def literal_contacts(pole_count, supports):
    incidence = [[int(pole in support) for pole in range(pole_count)] for support in supports]
    pole_degrees = list(map(sum, zip(*incidence)))
    column_degrees = list(map(sum, incidence))
    assert sum(column_degrees) == sum(pole_degrees) == sum(map(len, supports))
    return pole_degrees, column_degrees


def check_literal_supports():
    inside = [{0, 1}, {0, 1}, {0, 2}, {0, 2}, {1, 2}, {0, 1, 2}]
    outside = [{0, 1}, {0, 1}, {0, 2}, {0, 2}, {0, 3}, {1, 3}, {2, 3}, {1, 2, 3}]
    for pole_count, supports, expected_member in [(3, inside, True), (4, outside, False)]:
        degrees, columns = literal_contacts(pole_count, supports)
        assert degrees == [5] + [4] * (pole_count - 1)
        assert columns == [2] * (2 * pole_count - 1) + [3]
        assert (0 in supports[-1]) == expected_member
        for exceptional_wings in [(1, 2), (2, 1)]:
            wings = [exceptional_wings] + [(2, 2)] * (pole_count - 1)
            assert [sum(pair) + degree for pair, degree in zip(wings, degrees)] == [8] * pole_count
    bad = inside.copy()
    bad[0] = {1}
    bad[4] = {0, 1, 2}
    degrees, columns = literal_contacts(3, bad)
    assert degrees == [5, 4, 4] and columns == [1, 2, 2, 2, 3, 3]
    print("PASS 3x6 and 4x8 physical incidences: triple contains/avoids the exceptional pole; "
          "both shore orientations; a mass-preserving mutation fails the column floor")


def check_wing_arithmetic():
    possibilities = list(product(range(3), repeat=2))
    by_mass = {}
    for wings in product(possibilities, repeat=3):
        degrees = tuple(8 - sum(pair) for pair in wings)
        by_mass.setdefault(sum(degrees), []).append((wings, degrees))
    assert by_mass[12] == [(((2, 2),) * 3, (4, 4, 4))]
    expected = set()
    for pivot, exceptional in product(range(3), [(1, 2), (2, 1)]):
        wing_row = [(2, 2)] * 3
        wing_row[pivot] = exceptional
        outside_row = [4] * 3
        outside_row[pivot] = 5
        expected.add((tuple(wing_row), tuple(outside_row)))
    assert len(by_mass[13]) == 6 and set(by_mass[13]) == expected
    assert (((0, 2), (2, 2), (2, 2)), (6, 4, 4)) in by_mass[14]
    print("PASS 729 smaller literal wing arrays: tight count 1, deficit-one count 6, "
          "deficit-two permits a zero wing")


if __name__ == "__main__":
    physical_controls()
    check_literal_supports()
    check_wing_arithmetic()
