from collections import defaultdict
from pathlib import Path
from itertools import combinations
import json,math,sys,subprocess,os
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
from pysat.solvers import Minisat22
from cards24 import DIR,ROOT,parse_graph6,independent_sets,subgraph
from cyclic_proof import proof
from exception_cover import verify_lrat

def instance(name):
    if name.startswith('prom'):
        return parse_graph6(json.loads((DIR.parent/'transfer/promoted.json').read_text())[int(name[4:])]['core']),10
    if name=='control39':
        parent=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());return subgraph(parent,range(31)),10
    if name=='control6':return [2,1],3
    return parse_graph6(json.loads((DIR/'cards.json').read_text())[int(name)]['core']),10
def base_formula(adj,target):
    size=len(adj);base=[[-left-1,-right-1] for left,right in combinations(range(size),2) if adj[left]>>right&1];base += [[-vertex-1] for vertex,row in enumerate(adj) if row.bit_count()>=target-1];base += [[vertex+1 for vertex in range(size) if witness>>vertex&1] for witness in independent_sets(adj,(1<<size)-1,target-1)];return base
def block(mask,size):return [(-vertex-1 if mask>>vertex&1 else vertex+1) for vertex in range(size)]
def formula(adj,target,masks):
    rows=base_formula(adj,target)+[block(mask,len(adj)) for mask in masks];return f'p cnf {len(adj)} {len(rows)}\n'+''.join(' '.join(map(str,row))+' 0\n' for row in rows)
def census(adj,target):
    size=len(adj);masks=[]
    with Minisat22(bootstrap_with=base_formula(adj,target)) as sat:
        while sat.solve():
            bits=sum(1<<(lit-1) for lit in sat.get_model() if 0<lit<=size);masks.append(bits);sat.add_clause(block(bits,size))
    assert len(masks)==len(set(masks));return sorted(masks)
def hit(kind,word,mask):return bool(mask&word) if kind=='degree' else not bool(mask&word)
def allowed(adj,target,kind,word):
    if kind=='degree':assert word.bit_count()==1;return target-1-adj[word.bit_length()-1].bit_count()
    assert kind=='miss' and all(not adj[vertex]&word for vertex in range(len(adj)) if word>>vertex&1);return {2:2,3:5}[target-word.bit_count()]
def check(name):
    adj,target=instance(name);item=json.loads(Path(name+'.dual').read_text());masks=list(map(int,Path(name+'.masks').read_text().split()));assert masks==sorted(set(masks));rows=item['rows'];charges=[sum(weight for kind,word,weight in rows if hit(kind,word,mask)) for mask in masks];cost=sum(weight*allowed(adj,target,kind,word) for kind,word,weight in rows);assert rows and all(isinstance(weight,int) and weight>0 and 0<word<1<<len(adj) for kind,word,weight in rows);minimum=min(charges);assert cost==item['cost'] and minimum==item['min'] and cost<item['outside']*minimum;assert formula(adj,target,masks)==Path(name+'.cnf').read_text();verify_lrat(Path(name));print('dual verified',name,'strict masks',len(masks),'terms',len(rows),'integer upper via',cost,'/',minimum,'floor',cost//minimum,flush=True)
def solve(name):
    adj,target=instance(name);size=len(adj);masks=census(adj,target);outside=4 if name=='control6' else 8
    assert masks;catalogue=[];uppers=[];positions=[];indptr=[0];seen=set()
    for kind,words in [('degree',[1<<old for old in range(size)]),('miss',independent_sets(adj,(1<<size)-1,target-2)),('miss',independent_sets(adj,(1<<size)-1,target-3))]:
        for word in words:
            if not word:continue
            rhs=allowed(adj,target,kind,word);idx=tuple(pos for pos,mask in enumerate(masks) if hit(kind,word,mask));
            if not idx or (idx,rhs) in seen:continue
            seen.add((idx,rhs));catalogue.append((kind,word));uppers.append(rhs);positions.extend(idx);indptr.append(len(positions))
    matrix=csr_matrix((np.ones(len(positions)),positions,indptr),shape=(len(uppers),len(masks)));solution=linprog(-np.ones(len(masks)),A_ub=matrix,b_ub=np.array(uppers),bounds=(0,None),method='highs',options={'threads':1});assert solution.success;value=-solution.fun;print('LP',name,'masks',len(masks),'unique rows',len(uppers),'objective',value,flush=True)
    if name=='control39':assert value>=8-1e-7;return
    if value>=outside-1e-7:
        if name=='control6':raise AssertionError('negative control failed')
        return
    multiplicities=[math.ceil(max(0.,-float(price))*1000000) for price in solution.ineqlin.marginals];rows=[(kind,word,weight) for (kind,word),weight in zip(catalogue,multiplicities) if weight];cost=sum(weight*allowed(adj,target,kind,word) for kind,word,weight in rows);minimum=min(sum(weight for kind,word,weight in rows if hit(kind,word,mask)) for mask in masks);assert cost<outside*minimum and minimum>0;Path(name+'.dual').write_text(json.dumps(dict(rows=rows,cost=cost,min=minimum,outside=outside)));Path(name+'.masks').write_text(''.join(f'{mask}\n' for mask in masks));Path(name+'.cnf').write_text(formula(adj,target,masks));assert proof(Path(name))=='dual';check(name)
if __name__=='__main__':
    for name in sys.argv[2:]:check(name) if sys.argv[1]=='check' else solve(name)
