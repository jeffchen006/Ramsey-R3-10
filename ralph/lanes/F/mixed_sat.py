"""Signed lift feasibility; translate supports within the three designated cycles only."""

import argparse
from pathlib import Path

from cyclic_proof import Formula, proof
from cyclic_check import check
from orbit_extend import to_graph6


class MixedFormula(Formula):
    def add_orbit(self, full, single):
        long=2*self.size//5
        assert self.size==5*long//2 and long%2==0
        for shift in range(long):
            def move(labels):
                result=[]
                for vertex in labels:
                    start=min(vertex//long,2)*long
                    result.append(start+(vertex-start+shift)%(long if start<2*long else long//2))
                return tuple(sorted(result))
            self.add(move(full), move(single))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source');parser.add_argument('target',type=int);parser.add_argument('folder',type=Path);parser.add_argument('--ids',type=Path);parser.add_argument('--rounds',type=int,default=96);args=parser.parse_args()
    rows=Path(args.source).read_text().splitlines();args.folder.mkdir(exist_ok=True)
    for index in (map(int,args.ids.read_text().split()) if args.ids else range(len(rows))):
        text=rows[index];stem=args.folder/f'{index:06}';formula=MixedFormula(text,args.target)
        status,turns,witness=formula.search(args.rounds)
        if status=='yes': stem.with_suffix('.g6').write_text(to_graph6(witness)+'\n')
        if status=='no': formula.serialize(stem);assert proof(stem)=='dual';check(text,args.target,stem)
        print(index,status,turns,flush=True)
