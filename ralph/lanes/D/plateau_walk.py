"""Reroot the local 15-cap rule at the two satellite deficient leaves."""
from itertools import product
from collections import Counter
from time import process_time
import json,sys
import numpy as np
from scipy.sparse import hstack,vstack,csr_matrix
from scipy.optimize import linprog
from book_strata import DEST
from book_controls import sites
from wing_star_cuts import prepare
from wing_plateau import restrict


def predicted(graph,root,partners):
    first,second=partners;assert graph[first]>>second&1;return [(point,1 if point in partners else 2 if graph[point]&(1<<first|1<<second) else 3) for point in range(len(graph)) if point!=root and not(graph[root]>>point&1)]


def cal():
    from book_controls import graph_masks
    from kernel_cnf import ROOT
    total=positive=negative=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if {row.bit_count() for row in graph}!={6} or max((row&other).bit_count() for i,row in enumerate(graph) for other in graph[:i])>3:continue
        for root,row in enumerate(graph):
            neighbors=[site for site,other in enumerate(graph) if site!=root and (other&row).bit_count()==1]
            if len(neighbors)!=2 or not(graph[neighbors[0]]>>neighbors[1]&1):continue
            for site,number in predicted(graph,root,neighbors):
                true=(graph[site]&row).bit_count();cover=(site in neighbors or (true==2)==bool(graph[site]&(1<<neighbors[0]|1<<neighbors[1])));assert (true==number)==cover;total+=1;positive+=true==number;negative+=true!=number
    assert positive and negative;print('C22 calibrated individual two-partner codegree predictions',total,positive,negative)


def explore(record,both):
    rows=record['rows'];graph,raw,base,rhs,names=prepare(record,False);which=restrict(raw,rows);masks=raw[which];base=base[:,which];lhs=3+next(i for i,row in enumerate(rows) if row.bit_count()==1);rhs_leaf=11+next(i for i in range(8) if sum(row>>i&1 for row in rows)==1);pairs=[(lhs,2),(rhs_leaf,1)];choices=[[point for point in sites(graph[anchor]) if point!=leaf and not graph[leaf]>>point&1] for leaf,anchor in pairs];
    if not both:choices[1]=[-1]
    for left,right in product(*choices):
        start=process_time();rules={};clash=False
        for (leaf,anchor),second in zip(pairs,(left,right)):
            if second<0:continue
            for site,number in predicted(graph,leaf,(anchor,second)):
                word=(1<<site)|(1<<leaf);want=number-(graph[leaf]&graph[site]).bit_count();clash|=want<0 or rules.setdefault(word,want)!=want
        output=dict(id=record['id'],second=[left,right],status='conflict' if clash else 'cap')
        if not clash:
            additional=[];limits=[];newnames=[]
            for word,count in sorted(rules.items()):
                row=((masks&word)==word).astype(np.int64);additional.extend((row,-row));limits.extend((count,-count));newnames.extend((('walk',word,count,0),('walk',word,count,1)))
            mat=vstack((base,csr_matrix(np.array(additional))),format='csc');bound=np.concatenate((rhs,np.array(limits)));tags=names+newnames;obj=np.zeros(len(masks)+1);obj[-1]=1;sol=linprog(obj,A_ub=hstack((mat,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':8})
            if not sol.status:
                if sol.fun<1e-8:output['status']='fractional'
                else:
                    for scale in (1000,100000,10000000):
                        dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);margin=21*int(min(mat.T@dual))-int(dual@bound)
                        if margin>0:break
                    assert margin>0;output.update(status='separated',dual=[(tags[pos],int(val)) for pos,val in enumerate(dual) if val],margin=margin)
        output['cpu']=process_time()-start;yield output


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        for record in map(json.loads,(DEST/'plat.jsonl').read_text().splitlines()):
            if record['status']=='fractional':
                for output in explore(record,sys.argv[1]=='both'):print(json.dumps(output,separators=(',',':')),flush=True)
