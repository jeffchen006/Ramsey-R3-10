"""Independently check a sample of pinned independent-domination cuts."""

import argparse
from pathlib import Path
import random

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153

from cal_mtf import parse_graph6


def supports(rows, demand, size):
    with Cadical153() as solver:
        order = len(rows)
        for vertex, neighbors in enumerate(rows):
            solver.add_clause([vertex + 1] + [other + 1 for other in range(order) if neighbors >> other & 1])
            for other in range(vertex):
                if neighbors >> other & 1:
                    solver.add_clause([-vertex-1, -other-1])
            if demand >> vertex & 1:
                solver.add_clause([vertex + 1])
        solver.append_formula(CardEnc.equals(lits=list(range(1, order+1)), bound=size,
                                              encoding=EncType.seqcounter).clauses)
        return solver.solve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('count', type=int)
    args = parser.parse_args()
    lines = args.source.read_text().splitlines()
    masks = args.trace.read_text().splitlines()
    assert len(lines) == len(masks)
    assert supports([2, 1, 0], 5, 2) and not supports([2, 1, 0], 5, 1)
    assert not supports([2, 1, 0], 3, 2)
    for index in random.Random(162107).sample(range(len(lines)), args.count):
        rows = parse_graph6(lines[index])
        demand = int(masks[index], 16)
        tips = [vertex for vertex in range(len(rows)) if demand >> vertex & 1]
        assert len(tips) == 2 and not (rows[tips[0]] >> tips[1] & 1) and not rows[tips[0]] & rows[tips[1]]
        assert not supports(rows, demand, 6) and not supports(rows, demand, 7), index
    print(f'{args.count}/{args.count} independent forced-row SAT checks UNSAT for both sizes; three mixed controls pass')
