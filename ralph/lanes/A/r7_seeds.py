#!/usr/bin/env python3
"""Bind the published four-element R(3,8;27,85) class to replay inputs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from check_graph import alpha, parse_graph6, triangle_free


def fingerprint(adj):
    degrees = [mask.bit_count() for mask in adj]
    return tuple(sorted(
        (degrees[vertex], tuple(sorted(
            (degrees[other], (neighbors & row).bit_count())
            for other, row in enumerate(adj)
        ))) for vertex, neighbors in enumerate(adj)
    ))


def verify(proof_dir):
    lines = (proof_dir / "r38_27_e85.g6").read_text().splitlines()
    if len(lines) != 4:
        raise ValueError("expected four X seeds")
    seen = set()
    for index, line in enumerate(lines):
        adj = parse_graph6(line)
        if (len(adj) != 27 or sum(row.bit_count() for row in adj) != 170
                or not triangle_free(adj) or alpha(adj) > 7):
            raise ValueError(f"invalid R(3,8;27,85) seed {index}")
        signature = fingerprint(adj)
        if signature in seen:
            raise ValueError(f"nonisomorphism not established for seed {index}")
        seen.add(signature)
        with (proof_dir / f"R7_full.{index}.txt").open() as source:
            header = source.readline().split()
            masks = list(map(int, source.readline().split()))
        if header != ["9", "7", "27"] or masks != adj:
            raise ValueError(f"mismatched R7 seed {index}")
    print("PASS all four valid, pairwise nonisomorphic e85 graph6 seeds bind to the replay")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
