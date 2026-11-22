"""Exhaust all restrictions to a full left wing and four right sites (marked only by side)."""
from collections import Counter
from itertools import combinations,permutations
from time import process_time
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack
from book_strata import DEST,independent_sets,TYPES
from book_controls import bitset,sites
from book_outside import instance
from kernel_cnf import decode


def rectangle_graph(rows,short):
    wide=len(rows);graph=[0]*(3+wide+short)
    def connect(left,right):graph[left]|=1<<right;graph[right]|=1<<left
    connect(0,1);connect(0,2)
    for point,word in enumerate(rows):
        connect(1,3+point)
        for col in sites(word):connect(3+point,3+wide+col)
    for col in range(short):connect(2,3+wide+col)
    return graph


def census(wide,short):
    mapping=(DEST/'dict.bin').read_bytes();bad=set(map(int,(DEST/'bad.in').read_text().split()));output=[]
    for idx,text in enumerate((DEST/f'half{wide}.g6').read_text().splitlines()):
        edges=decode(text);rows=[bitset(right-wide for left,right in edges if left==point) for point in range(wide)];assert all(left<wide<=right for left,right in edges);kinds=set();reason='live'
        if any((first&second).bit_count()>2 for first,second in combinations(rows,2)):reason='cap'
        elif short==4:
            for quad in combinations(rows,4):
                number=mapping[sum(word<<(4*pos) for pos,word in enumerate(quad))]-1
                if number>=0:kinds.add(number)
            if not kinds:reason='no-mark'
            elif kinds&bad:reason='forbidden-minor'
        output.append(dict(id=idx,rows=rows,types=sorted(kinds),status=reason))
    return output


def system(rows,short,degree,order):
    graph=rectangle_graph(rows,short);rules,masks,matrix,bound=instance(graph,degree,order,{(1,2)},True);maximum=[word for word in independent_sets(graph) if word.bit_count()==degree];valid=[idx for idx,mask in enumerate(masks) if not(mask&2) and all(mask&word for word in maximum)];return graph,rules,[masks[idx] for idx in valid],matrix[:,valid],bound


def cal():
    raw=census(5,2);perms=[[0,1],[1,0]];lookup={tuple(sorted(bitset(pos for pos,col in enumerate(perm) if word>>col&1) for word in record['rows'])):record['id'] for record in raw for perm in perms};total=0;systems=set()
    for row in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines()):
        full=row['rows'];width=len(full)
        for chosen in combinations(range(width),2):
            partial=[bitset(pos for pos,site in enumerate(chosen) if word>>site&1) for word in full];idx=lookup[tuple(sorted(partial))];assert raw[idx]['status']=='live';total+=1
            if idx in systems:continue
            systems.add(idx);hist=Counter();graph,_,masks,matrix,bound=system(partial,2,6,22)
            for site in set(range(width))-set(chosen):hist[4|bitset(3+point for point,word in enumerate(full) if word>>site&1)]+=1
            for centre,group in ((1,'y'),(0,'z')):
                for mask in row[group]:hist[centre|((mask&31)<<3)|bitset(3+width+pos for pos,site in enumerate(chosen) if mask>>(width+site)&1)]+=1
            assert set(hist)<=set(masks) and np.all(matrix@np.array([hist[mask] for mask in masks])<=bound)
    print('PASS C22 rectangular census, literal 5x2 root choices',total,'occupied classes and physical integer mask witnesses',len(systems))


def solve(record):
    start=process_time();rows=record['rows'];graph,rules,masks,matrix,bound=system(rows,4,9,40);pop=40-len(graph);obj=np.zeros(len(masks)+1);obj[-1]=1;sol=linprog(obj,A_ub=hstack((matrix,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':8});record.update(status='cap' if sol.status else 'fractional',columns=len(masks))
    if not sol.status and sol.fun>1e-8:
        for scale in (1000,100000,10000000):
            dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);margin=pop*int(min(matrix.T@dual))-int(dual@bound)
            if margin>0:break
        assert margin>0;record.update(status='separated',dual=[[*rules[pos//2],pos%2,int(num)] for pos,num in enumerate(dual) if num],margin=margin)
    record['cpu']=process_time()-start;return record


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        shard,mod=map(int,sys.argv[1:3]);
        for record in census(8,4)[shard::mod]:print(json.dumps(solve(record) if record['status']=='live' else record,separators=(',',':')),flush=True)
