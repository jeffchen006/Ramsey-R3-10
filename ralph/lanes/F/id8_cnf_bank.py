"""Represent an arbitrary single pole and its mate as a nineteenth paired site."""
from collections import defaultdict
from pathlib import Path
import sys

from cyclic_check import check,read_base
from cyclic_proof import Formula,proof
from orbit_extend import vertices
from relift_audit import encode


def supportbank(source='feet.trace'):
    result=defaultdict(set)
    for line in Path(source).read_text().splitlines():
        group,command,*rest=line.split()
        if command=='step':
            pole,sites,_=map(int,rest); assert pole in (0,1) and (sites.bit_count()+pole)==10
            result[int(group)].add(sites|(pole<<18))
    return result


def augmented(base,mask):
    last=[mask>>site&1 for site in range(len(base))]
    return encode([row+[flag] for row,flag in zip(base,last)]+[last+[1]])


def build(base,foot,rows,dirpath):
    text=augmented(base,foot);formula=Formula(text,10)
    for mask in sorted(rows):formula.add((),tuple(vertices(mask)))
    stem=dirpath/f'f{foot}'; formula.serialize(stem);return text,stem


def run(mode,step):
    base=read_base(Path('id8.q').read_text().strip());bank=supportbank('eight.trace' if mode=='eight' else 'feet.trace');out=Path('bank');out.mkdir(exist_ok=True)
    for index,foot in enumerate(sorted(bank)):
        if index%step:continue
        text,stem=build(base,foot,bank[foot],out);result=proof(stem);print(index,foot,len(bank[foot]),result,flush=True)
        if result!='dual':break
        assert check(text,10,stem)==len(bank[foot])


if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]))
