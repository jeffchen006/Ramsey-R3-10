"""Fixed nested sparse-to-dense panels; check exact integer dual on a separate mask enumeration."""
from itertools import combinations,product
from pathlib import Path
from time import process_time
import json,random,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack
from book_outside import example,instance
from book_join import allowed


def valid(rows):
    if max(word.bit_count() for word in rows)>9 or any(rows[a]&rows[b] and rows[a]>>b&1 or (rows[a]&rows[b]).bit_count()>3 for a,b in combinations(range(22),2)):return False
    if any((rows[a]&rows[b]).bit_count()!=1 for a,b in ((1,2),(12,13))):return False
    for a,b in product(range(4),repeat=2):
        left=(0,1,3+a,7+a,2);right=(11,12,14+b,18+b,13);word=sum(((rows[site]>>other)&1)<<(5*i+j) for i,site in enumerate(left)for j,other in enumerate(right))
        if word not in allowed('two'):return False
    return True


def deck():
    rows=example();yield 5,rows[:];choices=list(product(range(11),range(11,22)));random.Random(132240).shuffle(choices);count=5
    for left,right in choices:
        if rows[left]>>right&1:continue
        staged=rows[:];staged[left]|=1<<right;staged[right]|=1<<left
        if valid(staged):
            count+=1;rows=staged
            if count in (8,12,16,20):yield count,rows[:]
            if count==20:break


def check(rows,general,dual):
    neighbors=[{v for v in range(22) if word>>v&1} for word in rows];weak={(1,2),(12,13)};labels=[(frozenset(),18,18)]
    for point,hood in enumerate(neighbors):labels.append((frozenset([point]),9-len(hood),9-len(hood)))
    forbidden={tuple(sorted(pair)) for pair in combinations(range(22),2) if pair[0] in neighbors[pair[1]]}
    for a,b in combinations(range(22),2):
        if (a,b)in forbidden:continue
        count=len(neighbors[a]&neighbors[b]);bottom,top=(1,1)if(a,b)in weak else ((1 if general else 2),3);labels.append((frozenset((a,b)),bottom-count,top-count));
        if count>=top:forbidden.add((a,b))
    multipliers=[(labels[i//2][0],value if i%2==0 else -value) for i,value in dual.items()];rhs=sum(value*(labels[i//2][2] if i%2==0 else -labels[i//2][1])for i,value in dual.items());lo=10**18;count=0
    def options(first):
        sites=list(range(first,first+11));return [frozenset(subset) for size in range(6) for subset in combinations(sites,size) if all(tuple(sorted(pair)) not in forbidden for pair in combinations(subset,2))]
    for left,right in product(options(0),options(11)):
        joined=left|right
        if len(joined)>9 or any((a,b)in forbidden for a,b in product(left,right)) or any(len(hood&joined)>3 for hood in neighbors):continue
        count+=1;score=sum(coeff for subset,coeff in multipliers if subset<=joined);lo=min(lo,score)
    assert 18*lo-rhs>0;return count,18*lo-rhs


def main():
    for cross,rows in deck():
        for general in (True,False):
            start=process_time();_,masks,A,bound=instance(rows,9,40,{(1,2),(12,13)},general);cost=np.zeros(len(masks)+1);cost[-1]=1;sol=linprog(cost,A_ub=hstack((A,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':12});record=dict(cross=cross,general=general,rows=rows,column_count=len(masks),status='cap' if sol.status else 'fractional')
            if sol.status==0 and sol.fun>1e-8:
                for scale in (1000,100000,10000000):
                    dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);lo=int(np.min(A.T@dual));margin=18*lo-int(dual@bound)
                    if margin>0:break
                assert margin>0;weights={i:int(v)for i,v in enumerate(dual)if v};assert check(rows,general,weights)==(len(masks),margin);record.update(status='exact-separation',dual=weights,margin=margin)
            record['cpu']=process_time()-start;print(json.dumps(record,separators=(',',':')),flush=True)


if __name__=='__main__':main()
