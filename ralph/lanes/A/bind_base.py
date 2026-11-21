#!/usr/bin/env python3
"""Check the unchanged round-1 PB input against a later full Lean cube export."""

import argparse
from hashlib import sha256
from itertools import combinations, zip_longest
from pathlib import Path


ROUND1_CUBE = "bb887a7c81a7f588a84434e1924602b75e0266e7e48632b60967359d03877dd9"
ROUND1_SMS = "53b117c3f8e024ee5aa9de0b39bbcaf78e4fee9a9921ed8410c4b04e2599c703"
N = 40
PB_VARIABLES = 503490
TOTAL_ROWS = 189418
CASE_AUX_FIRST = PB_VARIABLES - (N - 2) * (N * (N - 1) // 2) + 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_digest(path):
    digest = sha256()
    with path.open("rb") as source:
        while chunk := source.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def edge(first, second):
    low, high = sorted((first, second))
    return high * (high - 1) // 2 + low + 1


def row(literals, rhs=1):
    return tuple(token for literal in literals
                 for token in ("1", ("x" if literal > 0 else "~x") + str(abs(literal)))) + (
                     ">=", str(rhs))


def case_rows():
    for first, second in ((10, 11), (10, 12), (8, 11), (8, 12), (9, 11), (9, 12)):
        yield row([edge(first, second)])
    for vertex in range(1, 10):
        yield row([edge(10, vertex) * (1 if vertex <= 7 else -1)])

    next_aux = CASE_AUX_FIRST
    for first, second in combinations(range(N), 2):
        terms = []
        for middle in range(N):
            if middle in (first, second):
                continue
            left, right = edge(first, middle), edge(second, middle)
            yield row([-next_aux, left])
            yield row([-next_aux, right])
            yield row([next_aux, -left, -right])
            terms.append(next_aux)
            next_aux += 1
        yield row([-aux for aux in terms], 31)
    require(next_aux == PB_VARIABLES + 1, "unexpected case auxiliary range")

    block = [edge(first, second) for first, second in combinations(range(13, N), 2)]
    yield row([-variable for variable in block], len(block) - 85)
    yield row(block, 85)


def rows(path, proof_input=False):
    with path.open(encoding="ascii") as source:
        header = source.readline().split()
        if proof_input:
            require(header == ["*", "#variable=", str(PB_VARIABLES), "#constraint=", str(TOTAL_ROWS)],
                    "unexpected PB input header")
        for number, line in enumerate(source, start=2):
            tokens = tuple(line.replace(";", " ; ").split())
            require(tokens and tokens[-1] == ";" and ";" not in tokens[:-1],
                    f"malformed PB line {number} in {path}")
            if proof_input and tokens[0].startswith("@"):
                tokens = tokens[1:]
            yield tokens[:-1]


def identical(lhs, rhs, context, expected_count):
    count = 0
    for count, (left, right) in enumerate(zip_longest(lhs, rhs), start=1):
        require(left == right, f"{context}: mismatch at row {count}")
    require(count == expected_count, f"{context}: expected {expected_count} rows, saw {count}")


def full_input(cube, case):
    yield from rows(cube)
    yield from rows(case)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cube", type=Path)
    parser.add_argument("sms", type=Path)
    parser.add_argument("artifacts", type=Path)
    args = parser.parse_args()
    require(file_digest(args.cube) == ROUND1_CUBE, "cube differs from checked round-1 bytes")
    require(file_digest(args.sms) == ROUND1_SMS, "SMS base differs from checked round-1 bytes")
    case = args.artifacts / "case.opb"
    identical(rows(case), case_rows(), "R(7) case augmentation", 89717)
    identical(rows(args.artifacts / "in.opb", proof_input=True), full_input(args.cube, case),
              "retained PB input = Lean export plus R(7) case augmentation", TOTAL_ROWS)
    print(f"OK export SHA-256 {ROUND1_CUBE}; SMS SHA-256 {ROUND1_SMS}")
    print("OK 89,717 exact R(7) augmentation rows (apart from harmless labels/spacing)")
    print("OK 189,418 exact PB input rows match export + case")
    print("Pass establishes byte binding, not full-project export provenance or a SAT case closure.")


if __name__ == "__main__":
    main()
