"""Fractional row-multiplicity coupling on exterior membership cells of frozen stars."""

import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, linprog, milp


def read_domains(path):
    domains = {}
    for text in path.open():
        fields = list(text.split())
        if fields[0] == 'rows':
            domains[int(fields[1])] = list(map(int, fields[2:]))
        else:
            assert fields[1] == '0'
            yield domains
            domains = {}


def model(graph, fixed, domains, mono=False, planted=None, quotas=None, integrals=0):
    size = len(graph)
    remaining = [point for point in range(size) if not fixed >> point & 1]
    labels = sorted({graph[point] & fixed for point in remaining})
    cells = [[point for point in remaining if graph[point] & fixed == label] for label in labels]
    masks = [sum(1 << point for point in cell) for cell in cells]
    center = graph[0] & graph[1] if mono else 0
    if mono: assert center == graph[2] & graph[3] and center.bit_count() == 1 and center & fixed
    assert {min(cell) for cell in cells} == domains.keys()
    if quotas is not None:
        exceptional, squares=quotas
        for cell in cells:
            point=min(cell);domains[point]=[row for row in domains[point] if all((row&graph[anchor]).bit_count() in ((0,) if row>>anchor&1 else (1,) if exceptional[point]>>anchor&1 else (2,3)) for anchor in range(size) if fixed>>anchor&1)]
    counts = [np.array([[(row & mask).bit_count() for mask in masks] for row in domains[min(cell)]], dtype=np.int16) for cell in cells]
    if any(not len(block) for block in counts): return 'empty', {}
    number = len(cells)
    offsets = np.cumsum([0]+[len(block) for block in counts]); cols = offsets[-1]
    matrices = []; sides = []
    def put(blocks, rhs, equal=False):
        row = sparse.hstack([sparse.csr_matrix(block, shape=(1,len(domain))) if block is not None else sparse.csr_matrix((1,len(domain))) for block,domain in zip(blocks,counts,strict=True)],format='csr')
        matrices.append(row); sides.append(rhs)
        if equal:matrices.append(-row);sides.append(-rhs)
    for idx,cell in enumerate(cells):
        blocks=[None]*number;blocks[idx]=np.ones(len(counts[idx]),dtype=np.int16);put(blocks,len(cell),True)
    for left,right in itertools.combinations(range(number),2):
        blocks=[None]*number;blocks[left]=counts[left][:,right];blocks[right]=-counts[right][:,left];put(blocks,0,True)
    for left,right in itertools.combinations_with_replacement(range(number),2):
        diagonal=left==right
        pop=len(cells[left])*(len(cells[right])-int(diagonal))
        if not pop:continue
        common=(labels[left]&labels[right]).bit_count()
        # Count ordered pairs inside a single cell, and one orientation across distinct cells.
        moments=[arr[:,left]*(arr[:,right]-int(diagonal)) for arr in counts]
        for sign,threshold in [(1,3),(-1,2 if quotas or (mono and not (labels[left]&labels[right]&center)) else 1)]:
            blocks=[sign*moment for moment in moments];blocks[left]=blocks[left]+sign*threshold*counts[left][:,right]
            put(blocks,sign*(threshold-common)*pop)
    if quotas is not None:
        anchors=[point for point in range(size) if fixed>>point&1];degree=graph[anchors[0]].bit_count()
        for anchor in anchors:
            star=graph[anchor];weights=[np.array([(row&star).bit_count() for row in domains[min(cell)]],dtype=np.int16) for cell in cells]
            for idx,mask in enumerate(masks):
                if not star&mask:continue
                assert star&mask==mask
                target=sum(squares[max(anchor,point),min(anchor,point)]+2*degree-1 for point in cells[idx]);target-=sum((graph[a]&star).bit_count()*(graph[a]&mask).bit_count() for a in anchors)
                put([weight*arr[:,idx] for weight,arr in zip(weights,counts)],target,True)
            for other in anchors:
                if other>=anchor or not star>>other&1:continue
                target=squares[anchor,other]+2*degree-1-sum((graph[a]&star).bit_count()*int(bool(graph[a]&(1<<other))) for a in anchors)
                put([weight if label>>other&1 else None for weight,label in zip(weights,labels)],target,True)
    matrix=sparse.vstack(matrices,format='csr');bounds=np.asarray(sides,dtype=np.int64)
    ceiling=np.repeat([len(cell) for cell in cells],np.diff(offsets))
    if planted:
        values=np.zeros(cols,dtype=np.int64)
        for idx,cell in enumerate(cells):
            lookup={tuple(coords):offsets[idx]+key for key,coords in enumerate(counts[idx])}
            for point in cell:values[lookup[tuple((planted[point]&mask).bit_count() for mask in masks)]]+=1
        assert max(matrix@values-bounds)<=0
    if integrals:
        parity=sparse.block_diag([domain[:,idx].reshape(1,-1) for idx,domain in enumerate(counts)],format='csr');parity=sparse.hstack([parity,-2*sparse.eye(number)],format='csr')
        augmented=sparse.vstack([sparse.hstack([matrix,sparse.csr_matrix((len(bounds),number))]),parity,-parity],format='csc');upper=np.concatenate([bounds,np.zeros(2*number)])
        maximum=np.concatenate([ceiling,[len(cell)*(len(cell)-1)//2 for cell in cells]])
        result=milp(np.zeros(len(maximum)),integrality=np.ones(len(maximum)),bounds=Bounds(np.zeros(len(maximum)),maximum),constraints=LinearConstraint(augmented,-np.inf,upper),options={'time_limit':integrals,'threads':1})
        info={'cols':int(cols),'constraints':len(upper),'mip_status':result.status}
        if result.x is not None:
            values=np.rint(result.x).astype(np.int64);assert max(augmented@values-upper)<=0 and min(values)>=0 and max(values-maximum)<=0
            info['multiplicities']={int(idx):int(val) for idx,val in enumerate(values) if val};return 'integer-relaxation',info
        return ('mip-infeasible' if result.status==2 else 'undecided'),info
    slack=sparse.hstack([matrix,-np.ones((len(bounds),1))],format='csc')
    costs=np.zeros(cols+1);costs[-1]=1
    result=linprog(costs,A_ub=slack,b_ub=bounds,bounds=(0,None),method='highs',options={'time_limit':15,'threads':1})
    info={'cols':int(cols),'constraints':len(bounds),'nz':matrix.nnz}
    if result.status!=0:return 'undecided',info
    if result.fun<1e-7:return 'fractional',info
    for scale in (1000,100000,10000000):
        multiplier=np.maximum(0,np.rint(-scale*result.ineqlin.marginals)).astype(np.int64)
        assert max(multiplier)<=scale+1 and matrix.shape[0]*max(multiplier)*100<2**62
        weights=matrix.T@multiplier
        margin=int(np.minimum(weights,0)@ceiling-multiplier@bounds)
        if margin>0:
            info.update(margin=margin,dual={idx:int(val) for idx,val in enumerate(multiplier) if val});return 'separated',info
    return 'inexact',info


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('roots',type=Path);parser.add_argument('domains',type=Path);parser.add_argument('--mono',action='store_true');parser.add_argument('--plant',type=Path);parser.add_argument('--quota',type=Path);parser.add_argument('--integer',type=int,default=0);args=parser.parse_args()
    plants={} if args.plant is None else json.loads(args.plant.read_text())
    quotas=args.quota.read_text().splitlines() if args.quota else None
    for idx,(line,domains) in enumerate(zip(args.roots.open(),read_domains(args.domains),strict=True)):
        fixed,*graph=map(int,line.split());start=time.process_time()
        quota=None
        if quotas:
            size=len(graph);data=list(map(int,quotas[idx].split()));ex=data[size+1:2*size+1];assert data[:size+1]==[fixed,*graph];square=dict(zip(((a,b)for a in range(size)for b in range(a)),data[2*size+1:],strict=True));quota=(ex,square)
        if not domains:status,info='preclosed',{}
        else:status,info=model(graph,fixed,domains,args.mono,plants.get(str(idx)),quota,args.integer)
        print(json.dumps(dict(index=idx,status=status,cpu=round(time.process_time()-start,6),**info)),flush=True)


if __name__=='__main__':main()
