"""Projected fixed-quotient SAT without a symmetry assumption on signs."""

from pathlib import Path
import argparse
from cyclic_proof import Formula, proof
from cyclic_check import check
from orbit_extend import to_graph6


class DihedralFormula(Formula):
    reflections=True
    def add_orbit(self, full, single):
        half = self.size//2
        for reflected in range(1+int(self.reflections)):
            for shift in range(half):
                def move(seq):
                    return tuple(sorted(((vertex//half)^reflected)*half +
                        ((-vertex if reflected else vertex)+shift)%half for vertex in seq))
                self.add(move(full), move(single))


def run(args):
    rows = Path(args.tag+'.q').read_text().splitlines()
    indices = list(map(int, Path(args.indices).read_text().split())) if args.indices else range(len(rows))
    folder=Path(args.out); folder.mkdir(exist_ok=True)
    for index in indices:
        stem=folder/f'{index:04}'
        formula=DihedralFormula(rows[index],args.target)
        formula.reflections=not args.rotation_only
        status, turns, graph=formula.search(args.rounds)
        checked='-'
        if status=='yes': stem.with_suffix('.g6').write_text(to_graph6(graph)+'\n')
        elif status=='no':
            formula.serialize(stem); checked=proof(stem)
            assert checked=='dual'; check(rows[index],args.target,stem)
        print(index,status,turns,checked,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag');parser.add_argument('target',type=int);parser.add_argument('out')
    parser.add_argument('--indices');parser.add_argument('--rounds',type=int,default=75)
    parser.add_argument('--rotation-only',action='store_true')
    run(parser.parse_args())
