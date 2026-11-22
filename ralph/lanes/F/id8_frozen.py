"""Rebuild every physical arm from frozen masks; bind the guarded CNF without its builder."""
from collections import Counter
from pathlib import Path
import sys

from cyclic_proof import Formula
from id8_cnf_bank import supportbank
from id8_merge import checks
from id8_saturation_check import geometry,cyclelaw,audit
from orbit_extend import vertices
from relift_audit import encode


def frozen(strong=False):return Path(__file__).with_name('round16_id8_masks'+('_eight' if strong else '')+'.txt')


def export(eight=False):
    bank=supportbank('eight.trace' if eight else 'feet.trace');frozen(eight).write_text(''.join(' '.join(map(str,[foot,*sorted(bank[foot])]))+'\n' for foot in sorted(bank)))


def labels(foots,cap):
    unseen=set()
    for foot in range(1<<18):
        if foot.bit_count()<=cap and all(foot & sum(1<<((shift+idx)%18) for idx in range(7)) for shift in range(18)):unseen.add(foot)
    for foot in foots:
        group={sum(1<<((shift+sign*site)%18) for site in vertices(foot)) for shift in range(18) for sign in (-1,1)}
        assert group<=unseen and foot==min(group);unseen-=group
    assert not unseen


def direct(foot,masks):
    matrix=[[int(left==right or (max(left,right)==18 and (foot>>min(left,right)&1)) or (max(left,right)<18 and 6<=abs(left-right)<=12)) for right in range(19)] for left in range(19)]
    formula=Formula(encode(matrix),10)
    for mask in masks:
        assert mask.bit_count()==10 and mask<1<<19;formula.add((),tuple(vertices(mask)))
    return formula


def rebind(mode):
    lines=[tuple(map(int,line.split())) for line in frozen().read_text().splitlines()];assert len(lines)==1406 and lines==sorted(lines)
    if mode=='strong':
        lines=sorted(lines+[tuple(map(int,line.split())) for line in frozen(True).read_text().splitlines()]);assert len(lines)==2623
    labels([row[0] for row in lines],8 if mode=='strong' else 7);cyclelaw();audit(*geometry())
    if mode=='pilot':lines=lines[::109]
    stem=Path('id8_'+mode);arms=len(lines)+1;offset=arms;count=1
    with stem.with_suffix('.cnf').open() as merged:
        magic,fmt,rawvars,rawclauses=merged.readline().split();assert magic=='p' and fmt=='cnf'
        assert list(map(int,merged.readline().split()))==[*range(1,arms+1),0]
        def reads(guard,numvars,clauses):
            nonlocal offset,count
            for clause in clauses:
                actual=list(map(int,merged.readline().split()));assert actual[-2:]==[-guard,0]
                assert [lit-offset if lit>0 else lit+offset for lit in actual[:-2]]==list(clause);count+=1
            offset+=numvars
        rows=Path('no_blind_pole.cnf').read_text().splitlines();reads(1,25,[tuple(map(int,row.split()[:-1])) for row in rows[1:]])
        for index,(foot,*masks) in enumerate(lines,2):
            assert masks==sorted(set(masks));formula=direct(foot,masks);reads(index,formula.variables,formula.clauses)
            trace=(Path('bank')/f'f{foot}.trace').read_text().splitlines();actual=[row.split() for row in trace if row.startswith(('cut ','forestcut '))];assert all(row[1]=='0' for row in actual) and sorted(map(lambda row:int(row[2]),actual))==masks
        assert not merged.readline() and int(rawvars)==offset and int(rawclauses)==count
    print('frozen distances/roster =>',arms,'semantically bound disjuncts,',offset,'variables,',count,'clauses',flush=True);checks(stem)


if __name__=='__main__':
    if sys.argv[1] in ('export','export8'):export(sys.argv[1]=='export8')
    else:rebind(sys.argv[1])
