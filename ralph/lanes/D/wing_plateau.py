"""Closed neighbourhood of the two defect partners in the t<=15 plateau."""
from collections import Counter
from itertools import combinations
from time import process_time
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack
from book_strata import DEST,standard
from book_controls import bitset,sites,graph_masks
from kernel_cnf import ROOT
from wing_population import wings
from wing_star_cuts import prepare,Oracle


def samples():
    for idx,line in enumerate((DEST/'wing8.g6').open()):
        rows=wings(line.strip());deg=[word.bit_count() for word in rows];cols=[sum(row>>site&1 for row in rows) for site in range(8)]
        if sorted(deg)==sorted(cols)==[1]+[2]*7:yield idx,rows


def restrict(masks,rows,top=3):
    width=len(rows);lhs=((1<<width)-1)<<3;rhs=lhs<<width;left=next(i+3 for i,word in enumerate(rows) if word.bit_count()==1);right=next(3+width+i for i in range(width) if sum(word>>i&1 for word in rows)==1)
    return [idx for idx,mask in enumerate(masks) if ((int(mask)&(lhs|1)).bit_count()==top-(int(mask)>>right&1) and (int(mask)&(rhs|1)).bit_count()==top-(int(mask)>>left&1))]


def solve(idx,rows,mode):
    start=process_time();graph,masks,mat,rhs,names=prepare(dict(rows=rows),False);kept=restrict(masks,rows);mat=mat[:,kept];masks=masks[kept];obj=np.zeros(len(kept)+1);obj[-1]=1;record=dict(id=idx,rows=rows,columns=len(kept),status='cap');oracle=Oracle(graph,masks,9,21) if mode=='star' else None;seen=set()
    for step in range(60 if oracle else 1):
        sol=linprog(obj,A_ub=hstack((mat,-np.ones((len(rhs),1))),format='csc'),b_ub=rhs,bounds=(0,None),method='highs',options={'threads':1,'time_limit':8});
        if sol.status:break
        if sol.fun>1e-8:
            for scale in (1000,100000,10000000):
                dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);margin=21*int(min(mat.T@dual))-int(dual@rhs)
                if margin>0:break
            assert margin>0;record.update(status='separated',dual=[(names[pos],int(val)) for pos,val in enumerate(dual) if val],margin=margin);break
        if not oracle:record['status']='fractional';break
        adds=[row for row in oracle.violated(sol.x[:-1]) if row not in seen]
        if not adds:record['status']='fractional';break
        from scipy.sparse import vstack,csr_matrix
        seen.update(adds);mat=vstack((mat,csr_matrix(np.array([oracle.row(key) for key in adds]))),format='csc');rhs=np.concatenate((rhs,np.array([key[-1] for key in adds])));names.extend(adds)
    record.update(cpu=process_time()-start,iteration=step+1);return record


def calibration():
    # Test the combinatorial contact identity on the literal span of a closed two-part neighbourhood.
    total=0;actual=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {row.bit_count() for row in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for centre,hood in enumerate(graph):
            partners=[site for site,word in enumerate(graph) if site!=centre and (word&hood).bit_count()==1]
            if len(partners)!=2 or not(graph[partners[0]]>>partners[1]&1):continue
            others=[idx for idx in range(22) if idx not in [centre,*partners] and not(hood>>idx&1)];two={idx for idx in others if (graph[idx]&hood).bit_count()==2};touched={idx for idx in others if graph[idx]&(1<<partners[0]|1<<partners[1])};pred=all((graph[idx]&hood).bit_count()==3-int(bool(graph[idx]&(1<<partners[0]|1<<partners[1]))) for idx in others);assert pred==(two==touched);total+=1;actual+=pred
    print('C22 centres with two adjacent partners',total,'having exact cover of double sites',actual)


if __name__=='__main__':
    if sys.argv[1]=='cal':calibration()
    else:
        for idx,rows in samples():print(json.dumps(solve(idx,rows,sys.argv[1]),separators=(',',':')),flush=True)
