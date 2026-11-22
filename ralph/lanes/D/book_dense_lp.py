"""Price joint boundary occupancy; exact integer dual checked with set-valued columns."""
import json,sys
from time import process_time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack
from book_strata import DEST
from book_outside import instance
from book_outside_panel import check


def run(record):
    start=process_time();rows=record['rows'];_,masks,matrix,bound=instance(rows,9,40,{(1,2),(12,13)},True);obj=np.zeros(len(masks)+1);obj[-1]=1
    solution=linprog(obj,A_ub=hstack((matrix,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':12});out=dict(status='cap' if solution.status else 'fractional',columns=len(masks),solver=solution.message);out['decision_cpu']=process_time()-start
    if not solution.status and solution.fun>1e-8:
        for scale in (1000,100000,10000000):
            dual=np.maximum(0,np.rint(-solution.ineqlin.marginals*scale)).astype(np.int64);margin=18*int(min(matrix.T@dual))-int(dual@bound)
            if margin>0:break
        assert margin>0;weights={idx:int(value) for idx,value in enumerate(dual) if value};assert check(rows,True,weights)==(len(masks),margin);out.update(status='exact-separation',margin=margin,dual=weights)
    return dict(id=[*record['pair'],record['cross'],record['rep']],cpu=process_time()-start,**out)


if __name__=='__main__':
    source=DEST/(sys.argv[1] if len(sys.argv)>1 else 'boundaries.jsonl')
    for record in map(json.loads,source.read_text().splitlines()):
        if record['rows'] and record['roots'] and not (record['direct'] or record['foot']):print(json.dumps(run(record),separators=(',',':')),flush=True)
