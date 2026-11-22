"""One finite CNF assembled only from ten-singleton receipt supports."""
from itertools import combinations
from pathlib import Path
import subprocess
import sys

from cyclic_check import check
from cyclic_proof import Formula, proof
from orbit_extend import ROOT, vertices
from relift_audit import encode


def control():
    for size,step,expected in [(3,1,20),(4,1,10)]:
        base=[[int(left==right or (left-right)%size in (step,size-step)) for right in range(size)] for left in range(size)]
        text=encode(base);formula=Formula(text,size);formula.add((),tuple(range(size)));stem=Path('lratctl'+str(size));formula.serialize(stem)
        if expected==20:
            assert proof(stem)=='dual' and check(text,size,stem)==1
        else:
            result=subprocess.run([ROOT/'opt/bin/cadical','-q',stem.with_suffix('.cnf')],capture_output=True,text=True);assert result.returncode==10 and 's SATISFIABLE' in result.stdout.splitlines()
            model=[int(token) for line in result.stdout.splitlines() if line.startswith('v ') for token in line.split()[1:] if token!='0'];graph=formula.lift(model)
            assert all(not any(graph[left]>>right&1 for left,right in combinations([site for site in range(8) if graph[root]>>site&1],2)) for root in range(8))
            assert all(any(graph[left]>>right&1 for left,right in combinations(subset,2)) for subset in combinations(range(8),4))
        print('physical quotient cycle size',size,'expected',expected,'verified')


def batch():
    text=Path('../r13/max.q').read_text().splitlines()[21];assert text==Path('../r14/old21.q').read_text().strip();formula=Formula(text,10)
    receipts=sorted(Path().glob('branch4.*.proof'))+sorted(Path().glob('restored4.*.proof'));assert len(receipts)==128;points=set();masks=set()
    for path in receipts:
        header,steps,final=path.read_text().splitlines();state,raw=header.split();assert state in ('rank0','xor');points.add(int(raw));masks.update(map(int,(steps+' '+final).split()))
    assert points==set(range(128)) and len(masks)==297
    prove(formula,text,masks,Path('id21'))


def frozen():
    text=encode([[int(min((left-right)%18,(right-left)%18) in (0,5,6,8,9)) for right in range(18)] for left in range(18)])
    masks=set(map(int,Path(__file__).with_name('round15_id21_masks.txt').read_text().split()));assert len(masks)==297
    prove(Formula(text,10),text,masks,Path('id21_frozen'))


def prove(formula,text,masks,stem):
    for mask in sorted(masks):assert mask.bit_count()==10 and mask<1<<18;formula.add((),tuple(vertices(mask)))
    formula.serialize(stem);print('18-site ID21; full-pair supports: zero; singleton supports',len(masks),'vars/clauses',formula.variables,len(formula.clauses),flush=True)
    status=proof(stem);print('producer proof status',status,flush=True);assert status=='dual'
    assert check(text,10,stem)==len(masks);print('independent trace/CNF reconstruction + LRAT with lrat-check and cake_lpr: PASS')


if __name__=='__main__':{'control':control,'batch':batch,'frozen':frozen}[sys.argv[1]]()
