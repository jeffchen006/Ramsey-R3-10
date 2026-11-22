"""Exact exterior total via the small sum of local degree deficits."""

from itertools import combinations
from pathlib import Path
import json
import sys

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

import round23_h5 as base
from round22_control import decode, unflatten
from round22_deep import projected_activity


def encode(top, locations, required):
    """Each location is (edge bits, activity bit or 0, [(cap, slack, selectors)])."""
    rows, flags = [], []

    def fresh():
        nonlocal top
        top += 1
        return top

    def cardinality(bits, count, lower, guard=()):
        nonlocal top
        if (lower and count > len(bits)) or (not lower and count < 0):
            rows.append(guard)
            return
        if (lower and count <= 0) or (not lower and count >= len(bits)):
            return
        direction = CardEnc.atleast if lower else CardEnc.atmost
        encoded = direction(lits=list(bits), bound=count, top_id=top, encoding=EncType.seqcounter)
        top = max(top, encoded.nv)
        rows.extend((*guard, *clause) for clause in encoded.clauses)

    for incident, active, cases in locations:
        wanted = [fresh() for _ in range(max(slack for _, slack, _ in cases))]
        flags.extend(wanted)
        if active:
            rows.extend((-flag, active) for flag in wanted)
        for cap, slack, selectors in cases:
            if selectors:
                held = fresh()
                rows.append((-held, *selectors))
                rows.extend((-gate, held) for gate in selectors)
                control = (-held,)
            else:
                assert not active
                control = ()
            for distance, flag in enumerate(wanted, 1):
                if distance > slack:
                    rows.append((*control, -flag))
                    continue
                cardinality(incident, cap - distance, False, (*control, -flag))
                cardinality(incident, cap - distance + 1, True, (*control, flag))
        rows.extend((-later, earlier) for earlier, later in zip(wanted, wanted[1:]))
    cardinality(flags, required, True)
    cardinality(flags, required, False)
    return top, rows


def places(fold, slack=True):
    grids = len(fold.grid)
    for loc in range(grids + len(fold.slots[0])):
        incident = [edge for endpoints, edge in fold.edges[0].items() if loc in endpoints]
        if slack and loc < grids:
            yield incident, 0, [(7, 2, ())]
        elif not slack:
            yield incident, 0, [(len(incident), len(incident), ())]
        else:
            groups = {}
            for (left, right), gate in fold.gates.items():
                if left + grids == loc:
                    cap = 9 - (fold.slots[0][left].bit_count() + fold.slots[1][right].bit_count())
                    groups.setdefault(cap, []).append(gate)
            assert groups and set(groups) <= {5, 6}
            yield incident, fold.activity[0][loc - grids], [(cap, 1, groups[cap]) for cap in sorted(groups)]


def extended(board, prefix, budget=False, **kwargs):
    assert budget is False and len(board) == 5
    fold, physical = original(board, prefix[:2], **kwargs)
    order = [(1, 0), (1, 1)] + [(side, slot) for slot in range(2, 10) for side in (0, 1)]
    assert len(prefix) <= 20 and all(sign in '01' for sign in prefix)
    for (shore, slot), sign in zip(order, prefix[2:]):
        fold.add(((1 if sign == '1' else -1) * fold.activity[shore][slot],), 'occupancy')
    fold.variables, rows = encode(fold.variables, places(fold), 8)
    for row in rows:
        fold.add(row, 'deficit-budget')
    return fold, physical


def controls(folder):
    unique = {}
    for line in (folder / 'n17.d3.placements.jsonl').open():
        sample = json.loads(line)
        unique.setdefault(sample['board'], sample)
    assert len(unique) == 16
    for name, sample in unique.items():
        fold, physical = original(unflatten(name, 3), '', target=False, bound=7)
        assignment = projected_activity(fold, sample)
        incident = list(places(fold, slack=False))
        exterior = sum(first >= physical.boundary for first, _ in decode(sample['graph']))
        demand = sum(len(bits) for bits, _, _ in incident) - 2 * exterior
        assumptions = [edge if edge in assignment else -edge for edge in physical.edges.values()]
        for offset in (-1, 0, 1):
            _, rows = encode(fold.variables, incident, demand + offset)
            with Solver(name='cadical195', bootstrap_with=rows) as solver:
                assert solver.solve(assumptions=assumptions) == (offset == 0)
    checked = 0
    for active, mask in ((False, 0), (True, 3), (True, 4)):
        for degree in range(8):
            for demand in range(3):
                if active and degree not in (8 - mask, 9 - mask):
                    continue
                if not active and degree:
                    continue
                top, clauses = encode(10, [(range(1, 8), 8, [(6, 1, [9]), (5, 1, [10])])], demand)
                assert top > 10
                assumed = [bit if bit <= degree else -bit for bit in range(1, 8)]
                assumed += [8 if active else -8, 9 if mask == 3 else -9, 10 if mask == 4 else -10]
                with Solver(name='cadical195', bootstrap_with=clauses) as solver:
                    assert solver.solve(assumptions=assumed) == (demand == (9 - mask - degree if active else 0))
                checked += 1
    print('degree-deficit equality: 48 smaller physical budget tests,', checked, 'guarded projections')


original = base.build

if __name__ == '__main__':
    if sys.argv[1] == 'deficit-control':
        controls(Path(sys.argv[2]))
    else:
        assert '--deficit' in sys.argv
        sys.argv.remove('--deficit')
        base.build = extended
        base.main()
