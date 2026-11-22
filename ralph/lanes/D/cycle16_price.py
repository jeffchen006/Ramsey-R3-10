"""Exactly two deficient pairs: price the seven equality-case wing matrices."""
from collections import Counter
from itertools import combinations
from time import process_time
import json
import numpy as np
from scipy.sparse import bmat,coo_matrix,csr_matrix,hstack,vstack
from scipy.optimize import linprog
from book_strata import DEST
from wing_population import system


def assemble(rows,order,remaining,endpoint_low):
    graph,rules,masks,matrix=system(rows,order,'basic');keep=[idx for idx,word in enumerate(masks) if all((word&graph[point]).bit_count()>=endpoint_low for point in (1,2))];masks=[masks[idx] for idx in keep];matrix=matrix[:,keep];pairs=[idx for idx,row in enumerate(rules) if row[0]=='pair'];slacks=coo_matrix(([-1]*len(pairs),(pairs,range(len(pairs)))),shape=(len(rules),len(pairs))).tocsr();negative=[-(row[2]+int(row[0]=='pair')) for row in rules];positive=[row[3] for row in rules];out=bmat([[matrix,None],[-matrix,slacks],[csr_matrix((1,len(masks))),csr_matrix(np.ones((1,len(pairs)),dtype=int))]],format='csc');return graph,rules,masks,pairs,out,np.array([*positive,*negative,remaining],dtype=np.int64)


def cal():
    checked=0
    for record in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines()):
        if checked>=20:break
        counts=Counter((word<<3)|1 for word in record['y']);counts.update(word<<3 for word in record['z']);graph,rules,masks,pairs,matrix,bound=assemble(record['rows'],22,0,1);assert set(counts)<=set(masks);relax=[]
        for idx in pairs:
            _,word,low,high=rules[idx];used=1-low;relax.append(int(used+sum(n for mask,n in counts.items() if mask&word==word)==1))
        bound[-1]=sum(relax);assert np.all(matrix@np.array([*[counts[word] for word in masks],*relax])<=bound);checked+=1
    print('PASS actual finite deficiency debit in',checked,'C22 exterior vectors')


def run():
    for parts in ((8,),(6,2),(5,3),(4,4),(4,2,2),(3,3,2),(2,2,2,2)):
        rows=[];start=process_time()
        for width in parts:
            base=len(rows);rows.extend((1<<(base+site))|(1<<(base+(site+1)%width)) for site in range(width))
        graph,rules,masks,pairs,matrix,bound=assemble(rows,40,1,2);objective=np.zeros(matrix.shape[1]+1);objective[-1]=1;result=linprog(objective,A_ub=hstack((matrix,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':12});record=dict(parts=parts,columns=len(masks),defect_slacks=len(pairs),status='cap' if result.status else 'fractional')
        if not result.status and result.fun>1e-8:
            # Exact separation allowing one total slack and nonnegative (unbounded individually) deficit variables.
            for scale in (1000,100000,10000000):
                dual=np.maximum(0,np.rint(-result.ineqlin.marginals*scale)).astype(np.int64);cost=matrix.T@dual;floor=21*int(min(cost[:len(masks)]))+min(0,int(min(cost[len(masks):])));margin=floor-int(dual@bound)
                if margin>0:break
            assert margin>0;record.update(status='separated',margin=margin,dual={idx:int(n) for idx,n in enumerate(dual) if n})
        print(json.dumps(dict(**record,cpu=process_time()-start)),flush=True)


if __name__=='__main__':cal();run()
