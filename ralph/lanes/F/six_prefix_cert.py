from itertools import combinations,product
from pathlib import Path
import sys
from pysat.solvers import Cadical195
from cyclic_proof import proof
from exception_cover import verify_lrat
from orbit_extend import independent_sets
from six_branch import graph,decode

class ParityFormula:
    def __init__(self):self.variables=35;self.clauses=[];self.nodes={}
    def parity(self,word):
        assert 0<word<1<<35
        if word in self.nodes:return self.nodes[word]
        highest=word.bit_length();rest=word^(1<<(highest-1))
        if not rest:return highest
        left=self.parity(rest);right=highest;self.variables+=1;node=self.variables;self.nodes[word]=node
        for first,second in product((0,1),repeat=2):self.clauses.append([left*(-1 if first else 1),right*(-1 if second else 1),node*(1 if first^second else -1)])
        return node

def cycle_rows(mask,table):
    sites=[vertex for vertex in range(17) if mask>>vertex&1];components=[{site:0} for site in sites];cycles=[]
    for left,right in combinations(sites,2):
        if (left,right) not in table:continue
        first=next(group for group in components if left in group);second=next(group for group in components if right in group);offset=first[left]^second[right]^table[left,right]
        if first is second:
            if offset:cycles.append(offset)
        else:
            first.update({site:value^offset for site,value in second.items()});components.remove(second)
    return sorted(set(cycles))
def main(tag,create):
    where=Path('.');source=Path('../'+tag+'.rows');positive=[int(line.split()[0]) for line in source.read_text().splitlines()];prefix=int(Path('../'+tag+'.count').read_text().splitlines()[-1].split()[0])//32-1;assert positive and all(key>>16==prefix for key in positive);assert len(set(positive))==len(positive)
    table={(left,right):expr for left,right,expr in (tuple(map(int,line.split())) for line in Path('../columns.tsv').read_text().splitlines())};formula=ParityFormula();formula.clauses.extend([[pos+1 if prefix>>(pos-16)&1 else -pos-1] for pos in range(16,35)]);formula.clauses.extend([[-pos-1 if key>>pos&1 else pos+1 for pos in range(16)] for key in positive]);cuts=[]
    def add(mask):
        assert mask.bit_count()==10 and mask<1<<17 and mask not in cuts;cuts.append(mask);formula.clauses.append([formula.parity(row) for row in cycle_rows(mask,table)])
    if create:
        for line in Path('../bank.tsv').read_text().splitlines()[:576]:add(int(line.split()[0]))
        with Cadical195(bootstrap_with=formula.clauses) as engine:
            for turn in range(10000):
                engine.conf_budget(200000);answer=engine.solve_limited();assert answer is not None
                if not answer:break
                key=sum(1<<(variable-1) for variable in engine.get_model() if 0<variable<=35);assert key>>16==prefix and key not in positive
                adj=graph(decode(key));witness=next(independent_sets(adj,(1<<34)-1,10),None);assert witness is not None,(tag,key);mask=sum(1<<site for site in range(17) if witness>>(2*site)&3);oldcount=len(formula.clauses);add(mask)
                for clause in formula.clauses[oldcount:]:engine.add_clause(clause)
            else:raise ValueError('prefix control cap')
        Path(tag+'.cuts').write_text(''.join(f'{mask}\n' for mask in cuts))
    else:
        for line in Path(tag+'.cuts').read_text().splitlines():add(int(line))
    data=(f'p cnf {formula.variables} {len(formula.clauses)}\n'+''.join(' '.join(map(str,(*clause,0)))+'\n' for clause in formula.clauses)).encode();stem=Path(tag)
    if create:stem.with_suffix('.cnf').write_bytes(data);assert proof(stem)=='dual'
    assert data==stem.with_suffix('.cnf').read_bytes();verify_lrat(stem);print(tag,'19-bit prefix',prefix,'full words',1<<16,'listed bare',len(positive),'physically necessary singleton supports',len(cuts),'dual',flush=True)
if __name__=='__main__':main(sys.argv[1],sys.argv[2]=='create')
