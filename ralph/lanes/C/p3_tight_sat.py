"""Bounded fixed-layout LRAT pilot with the rounded-witness slack rows."""

import argparse
from collections import Counter
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from kernel_projection import bits, decode
from p3_common_cover import cases
from p3_e63 import lex_order, twin_groups
from p3_minimal import formula_minimal
from p3_zero_conditioned import verify
from path_three_top import plant


def pin(clauses, edges, core, common, degree, zero_masks, zero_count, rounded):
    def atmost(literals, count):
        clauses.extend(CardEnc.atmost(list(literals), count, top_id=clauses.nv, encoding=EncType.seqcounter))

    zeros = []
    for row, neighbours in enumerate(core):
        attachments = [edges[row, outer] for outer in bits(common)]
        if rounded:
            atmost(attachments, 2)
        eligible = [mask for mask in zero_masks if degree - neighbours.bit_count() == mask.bit_count()]
        if not eligible:
            clauses.append(attachments)
            continue
        is_zero = clauses.nv + 1
        zeros.append(is_zero)
        clauses.append([is_zero, *attachments])
        for literal in attachments:
            clauses.append([-is_zero, -literal])
        selectors = []
        for mask in eligible:
            selector = clauses.nv + 1 if len(eligible) > 1 else is_zero
            if len(eligible) > 1:
                clauses.append([-selector, is_zero])
                selectors.append(selector)
            for (inner, outer), literal in edges.items():
                if inner == row:
                    clauses.append([-selector, literal if mask >> outer & 1 else -literal])
        if selectors:
            clauses.append([-is_zero, *selectors])
    atmost(zeros, zero_count)
    atmost([-literal for literal in zeros], len(zeros) - zero_count)


def raw_slack(rotated, common, zero_mask, masks, boundary, rows, goal, witness):
    numerator, scale = verify(rows, goal, 19, witness)
    budget = numerator - 18 * scale
    caps = {}
    unpadded = {}
    raw_total = 0
    for name, weight in witness['weights'].items():
        if name.startswith('deg:'):
            outer = int(name.split(':')[1])
            assert rows[name][0] == 9 - boundary[outer].bit_count() - (zero_mask >> outer & 1)
            unpadded[outer] = weight
            raw_total += weight * rows[name][0]
            continue
        assert name.startswith('avoid:')
        block = int(name.split(':')[1])
        assert (block & common).bit_count() == 3 and block & zero_mask
        outside = block & ~common
        cap = 1 if block.bit_count() == 8 else 3
        assert block.bit_count() in (6, 8)
        for kept in bits(common):
            blockers = outside | (common ^ (1 << kept))
            assert blockers in rotated[block.bit_count()]
            assert blockers not in caps
            caps[blockers] = cap, weight
        assert rows[name][0] == 4 * cap
        raw_total += 4 * weight * cap
    assert raw_total == numerator
    margins = Counter()
    for mask in masks:
        if not mask & common:
            continue
        if mask & zero_mask and any(not (mask | zero_mask) & block for block in rotated[8]):
            continue
        coefficient = sum(weight for outer, weight in unpadded.items() if mask >> outer & 1)
        coefficient += sum(weight for block, (_, weight) in caps.items() if not mask & block)
        margin = coefficient - scale * ((mask & common).bit_count() == 1)
        assert margin >= 0
        margins[margin] += 1
    return caps, budget, margins


def slack(clauses, edges, order, caps, budget):
    missing = []
    for blockers, (cap, weight) in caps.items():
        misses = []
        for inner in range(order):
            hit = [edges[inner, vertex] for vertex in bits(blockers)]
            avoid = clauses.nv + 1
            clauses.append([avoid, *hit])
            for literal in hit:
                clauses.append([-avoid, -literal])
            misses.append(avoid)
        clauses.extend(CardEnc.atmost(misses, cap, top_id=clauses.nv, encoding=EncType.seqcounter))
        missing.extend(misses)
        for _ in range(weight - 1):
            for literal in misses:
                copied = clauses.nv + 1
                clauses.append([-copied, literal])
                clauses.append([copied, -literal])
                missing.append(copied)
    cap_total = sum(cap * weight for cap, weight in caps.values())
    clauses.extend(CardEnc.atmost([-literal for literal in missing], len(missing) - cap_total + budget,
                                  top_id=clauses.nv, encoding=EncType.seqcounter))


def calibrate():
    from p3_singleton_cover import independent_levels

    core, boundary, known = plant()
    clauses, edges = formula_minimal(core, boundary, 6, 4, 6, True)
    common = boundary[-1] & boundary[-2] & boundary[-3]
    actual = [known[vertex] >> len(core) for vertex in range(len(core))]
    zero = [mask for mask in actual if not mask & common]
    assert len(zero) == 2
    assignment = [literal if actual[inner] >> outer & 1 else -literal for (inner, outer), literal in edges.items()]
    pin(clauses, edges, core, common, 6, zero, len(zero), True)
    with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
        assert solver.solve(assumptions=assignment)
    pin(clauses, edges, core, common, 6, zero, 1, True)
    with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
        assert not solver.solve(assumptions=assignment)
    print('C21 formula: exact q=2 control accepted; q=1 mutation rejected')
    blockers = [block for block in independent_levels(boundary)[5] if not block >> (len(boundary) - 3)][:3]
    assert len(blockers) == 3
    caps, budget = {}, 0
    for index, blocker in enumerate(blockers):
        count = sum(not mask & blocker for mask in actual)
        pad = 1 if index == 0 else 0
        weight = index + 1
        caps[blocker] = count + pad, weight
        budget += weight * pad
    for allowed in (budget, budget - 1):
        clauses, _ = formula_minimal(core, boundary, 6, 4, 6, True)
        slack(clauses, edges, len(core), caps, allowed)
        with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
            assert solver.solve(assumptions=assignment) == (allowed == budget)
    print('C21 weighted-deficit encoding: measured budget accepted; budget minus one rejected')


def main():
    from p3_singleton_cover import independent_levels

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'pin', 'rounded', 'tight'))
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--out', type=Path, default=Path('tight'))
    args = parser.parse_args()
    if args.mode == 'control':
        calibrate()
        return
    args.out.mkdir(exist_ok=True)
    original = json.loads(Path('../r8/zero-all.json').read_text())
    witness = json.loads(Path('rounded.json').read_text())['1:0:1:1:1/0']
    label, count, boundary, _, masks, common, _, chosen, rows, goal = next(cases(original, '1:0:1:1:1'))
    catalogue = Path('../../../gluing/val/r3_7_22.g6').read_text().splitlines()
    assert len(chosen) == 1
    rotated = independent_levels(boundary)
    caps, budget, margins = raw_slack(rotated, common, chosen[0], masks, boundary, rows, goal, witness)
    print('Raw exact slack audit', 'budget', budget, 'mask margins', dict(sorted(margins.items())), flush=True)
    assert args.row
    for row in args.row:
        core = decode(catalogue[row])
        assert sum(mask.bit_count() for mask in core) == 2 * count
        clauses, edges = formula_minimal(core, boundary, 9, 6, 6, True)
        for group in twin_groups(boundary):
            for first, second in zip(group, group[1:]):
                lex_order(clauses, [edges[inner, first] for inner in range(len(core))],
                          [edges[inner, second] for inner in range(len(core))])
        pin(clauses, edges, core, common, 9, chosen, 1, args.mode != 'pin')
        if args.mode == 'tight':
            slack(clauses, edges, len(core), caps, budget)
        state = args.out / f'{args.mode}-{row}.cnf'
        clauses.to_file(state)
        print(label, row, args.mode, clauses.nv, len(clauses.clauses), state, flush=True)


if __name__ == '__main__':
    main()
