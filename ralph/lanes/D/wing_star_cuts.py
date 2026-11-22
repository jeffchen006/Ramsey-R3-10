"""Separate neighborhood/seed, Ramsey avoidance, and common-four occupancy inequalities."""
from itertools import combinations
from time import process_time
import json,sys
import numpy as np
from scipy.sparse import csr_matrix,hstack,vstack
from scipy.optimize import linprog
from book_strata import DEST,independent_sets
from book_controls import sites
from half_wing import system,rectangle_graph
from wing_follow import inputs
from wing_population import system as complete


def prepare(record,half,degree=9,order=40):
    rows=record['rows'];width=len(rows)
    if half:
        graph,rules,masks,matrix,bound=system(rows,4,degree,order);names=[('basic',term,low,cap,sign) for term,low,cap in rules for sign in (0,1)]
    else:
        graph,rules,masks,base=complete(rows,order,'basic');interleave=np.column_stack((np.arange(len(rules)),np.arange(len(rules))+len(rules))).ravel();matrix=vstack((base,-base),format='csc')[interleave,:];bound=np.array([num for _,_,low,cap in rules for num in (cap,-low)],dtype=np.int64);names=[('basic',term,low,cap,sign) for _,term,low,cap in rules for sign in (0,1)]
    return graph,np.array(masks,dtype=np.int64),matrix,bound,names


class Oracle:
    def __init__(self,graph,masks,degree,pop):
        self.masks=masks;self.width=len(graph);self.pop=pop;self.domain=1<<self.width;self.degree=degree;words=independent_sets(graph);self.seeds=np.array(words,dtype=np.int64);closure=np.array([word|self.union(graph,word) for word in words]);sizes=np.array([word.bit_count() for word in words]);self.avoid=np.array([{0:0,1:2,2:5,3:8,4:13,5:17,6:22,7:27,8:35}.get(degree-size,pop) for size in sizes]);self.stars=[]
        for site,hood in enumerate(graph):
            cap=degree-sizes-np.array([(hood&~int(word)).bit_count() for word in closure]);self.stars.append(cap)
        self.fours=np.array([word for word in words if word.bit_count()==4],dtype=np.int64)

    @staticmethod
    def union(graph,word):
        result=0
        for site in sites(word):result|=graph[site]
        return result

    def violated(self,weights):
        down=np.zeros(self.domain);down[self.masks]=weights;up=down.copy()
        for idx in range(self.width):
            stride=1<<idx;layer=down.reshape((-1,2*stride));layer[:,stride:]+=layer[:,:stride];other=up.reshape((-1,2*stride));other[:,:stride]+=other[:,stride:]
        miss=down[self.domain-1-self.seeds];cuts=[]
        def add(values,kind,words,bounds,site):
            positions=np.flatnonzero(values>1e-7)
            if len(positions)>80:positions=positions[np.argsort(values[positions],kind='stable')[-80:]]
            for pos in positions:cuts.append((float(values[pos]),(kind,int(words[pos]),site,int(bounds[pos]))))
        add(miss-self.avoid,'avoid',self.seeds,self.avoid,-1)
        for site,cap in enumerate(self.stars):
            add(miss-down[self.domain-1-(self.seeds|(1<<site))]-cap,'star',self.seeds,cap,site)
        add(up[self.fours]-1,'four',self.fours,np.ones(len(self.fours),dtype=int),-1)
        return [key for _,key in sorted(cuts,reverse=True)[:80]]

    def row(self,key):
        kind,word,site,_=key;hit=self.masks&word
        if kind=='avoid':return (hit==0).astype(np.int64)
        if kind=='four':return (hit==word).astype(np.int64)
        assert kind=='star';return ((hit==0)&((self.masks&(1<<site))!=0)).astype(np.int64)


def solve(record,half,limit):
    start=process_time();graph,masks,mat,rhs,names=prepare(record,half);pop=40-len(graph);oracle=Oracle(graph,masks,9,pop);seen=set();obj=np.zeros(len(masks)+1);obj[-1]=1;out=dict(id=record['id'],rows=record['rows'],columns=len(masks),half=half,status='round-cap');base=len(names)
    for iteration in range(limit):
        sol=linprog(obj,A_ub=hstack((mat,-np.ones((len(rhs),1))),format='csc'),b_ub=rhs,bounds=(0,None),method='highs',options={'threads':1,'time_limit':10})
        if sol.status:out['status']='lp-cap';break
        if sol.fun>1e-8:
            for scale in (1000,100000,10000000):
                dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);margin=pop*int(min(mat.T@dual))-int(dual@rhs)
                if margin>0:break
            assert margin>0;out.update(status='separated',dual=[(names[idx],int(value)) for idx,value in enumerate(dual) if value],margin=margin);break
        cuts=[key for key in oracle.violated(sol.x[:-1]) if key not in seen]
        if not cuts:out['status']='fractional';break
        seen.update(cuts);mat=vstack((mat,csr_matrix(np.array([oracle.row(key) for key in cuts]))),format='csc');rhs=np.concatenate((rhs,np.array([key[-1] for key in cuts])));names.extend(cuts)
    out.update(iterations=iteration+1,extra_rows=len(names)-base,cpu=process_time()-start);return out


def cal():
    from collections import Counter
    from book_strata import plants
    from book_outside import instance
    for key,truth,width in plants():
        core=(1<<width)-1;graph=[row&core for row in truth[:width]];_,masks,_,_=instance(graph,6,22,{(1,2),(8,9)},True);oracle=Oracle(graph,np.array(masks,dtype=np.int64),6,22-width);hist=Counter(row&core for row in truth[width:]);assert not oracle.violated(np.array([hist[mask] for mask in masks],dtype=float))
    print('PASS all 18 integer C22 populations; every seed, star and common four')


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        scope=sys.argv[1];part,mod,limit=map(int,sys.argv[2:5]);half=scope in ('half','rare');records=([r for r in map(json.loads,(DEST/'half.jsonl').read_text().splitlines()) if r['status']=='fractional' and (scope!='rare' or 33 in r['types'])] if half else inputs(int(scope),int(scope)))
        for record in records[part::mod]:print(json.dumps(solve(record,half,limit),separators=(',',':')),flush=True)
