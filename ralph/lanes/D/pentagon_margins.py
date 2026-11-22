"""Integer-checkable separators on the exterior ten-star incidence table alone."""
from itertools import combinations
from pathlib import Path
import json
import sys
import numpy as np
from scipy.optimize import linprog
from pentagon_transport import core_graph


def matrix_for(rows):
    core=core_graph(rows);weak={(1,4),(6,9)};masks=[]
    for mask in range(1024):
        sites=[site for site in range(10) if mask>>site&1]
        if all(not (core[first]>>last&1 or (first,last) in weak) for first,last in combinations(sites,2)):masks.append(mask)
    clauses=[(30,0,1),(-30,0,-1)]
    for site,neighbors in enumerate(core):
        need=9-neighbors.bit_count();clauses.extend([(need,1<<site,1),(-need,1<<site,-1)])
    for first,last in combinations(range(10),2):
        if core[first]>>last&1:continue
        low,high=(1,1) if (first,last) in weak else (2,3);used=(core[first]&core[last]).bit_count();key=(1<<first)|(1<<last);clauses.extend([(high-used,key,1),(used-low,key,-1)])
    matrix=np.array([[sign if mask&key==key else 0 for mask in masks] for _,key,sign in clauses],dtype=np.int64);bound=np.array([value for value,_,_ in clauses],dtype=np.int64);return matrix,bound


def run(folder):
    states=[]
    with (folder/'margins.jsonl').open('w') as output:
        for idx,text in enumerate((folder/'interfaces.tsv').read_text().splitlines()):
            rows=list(map(int,text.split()[:5]));matrix,bound=matrix_for(rows);n=matrix.shape[1];cost=np.zeros(n+1);cost[-1]=1;matrix2=np.column_stack((matrix,-np.ones(len(bound))));ans=linprog(cost,A_ub=matrix2,b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':6});assert ans.status==0
            if ans.fun<1e-8:
                for scale in (1,2,6,12,60,120,840,2520,27720,360360,12252240):
                    primal=np.rint(ans.x[:-1]*scale).astype(np.int64)
                    if min(primal)>=0 and (matrix@primal<=scale*bound).all():break
                else:scale=0
                data={'status':'rational-feasible' if scale else 'solver-feasible','scale':scale,'primal':{pos:int(num) for pos,num in enumerate(primal) if num} if scale else {}}
            else:
                for scale in (1000,100000,10000000):
                    dual=np.maximum(0,np.rint(-scale*ans.ineqlin.marginals)).astype(np.int64);margin=int(np.minimum(matrix.T@dual,0).sum()*30-dual@bound)
                    if margin>0:break
                assert margin>0;data={'status':'excluded','margin':margin,'dual':{pos:int(num) for pos,num in enumerate(dual) if num}}
            print(json.dumps(dict(index=idx,**data)),file=output);states.append(data['status'])
    print('all',len(states),{status:states.count(status) for status in sorted(set(states))})


if __name__=='__main__':run(Path(sys.argv[1]))
