"""One more D-walk step: exact choice of a boundary site or one exterior contact mask."""
from itertools import combinations
from time import process_time
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import vstack,csr_matrix,hstack
from book_strata import DEST,standard
from book_controls import sites
from wing_plateau import restrict
from wing_star_cuts import prepare
from plateau_walk import predicted


def partners(rows,offsets):
    left=3+next(i for i,row in enumerate(rows) if row.bit_count()==1);right=11+next(i for i in range(8) if sum(row>>i&1 for row in rows)==1);edges={(1,2),tuple(sorted((1,right))),tuple(sorted((2,left))),tuple(sorted((left,offsets[0]))),tuple(sorted((right,offsets[1])))};result={}
    for first,second in edges:result.setdefault(first,set()).add(second);result.setdefault(second,set()).add(first)
    return result


def more(record,rows):
    graph,raw,base,rhs,names=prepare(dict(rows=rows),False);which=restrict(raw,rows);masks=raw[which];base=base[:,which];known=partners(rows,record['second']);base_rules={};terminals=[]
    for vertex,neighborhood in sorted(known.items()):
        if len(neighborhood)==2:
            first,second=sorted(neighborhood)
            if not graph[first]>>second&1:yield dict(status='forced-triangle-rule',vertex=vertex);return
            for site,value in predicted(graph,vertex,(first,second)):
                term=(1<<vertex)|(1<<site);target=value-(graph[vertex]&graph[site]).bit_count()
                if target<0 or base_rules.setdefault(term,target)!=target:yield dict(status='forced-clash',vertex=vertex);return
        else:assert len(neighborhood)==1;terminals.append((vertex,next(iter(neighborhood))))
    terminal,previous=terminals[0] if terminals else (-1,-1);possible=[('in',site) for site in sites(graph[previous]) if site!=terminal and not(graph[terminal]>>site&1) and (site not in known or len(known[site])<2)] if terminals else [('closed',0)]
    if terminals:possible += [('out',int(mask)) for mask in masks if mask>>previous&1 and not(mask>>terminal&1) and (int(mask)&graph[terminal]).bit_count()<=1]
    for kind,option in possible:
        start=process_time();rules=base_rules.copy();clash=False
        if kind!='closed':
            for site in range(len(graph)):
                if site==terminal or graph[terminal]>>site&1:continue
                value=3-int(bool(graph[previous]>>site&1))-int(bool((graph[option] if kind=='in' else option)>>site&1))-(site==previous)-(kind=='in' and site==option);term=1<<site|1<<terminal;count=value-(graph[site]&graph[terminal]).bit_count();clash|=count<0 or rules.setdefault(term,count)!=count
        out=dict(terminal=terminal,mode=kind,option=option,status='conflict' if clash else 'cap')
        if not clash:
            add=[];threshold=[];tags=names[:]
            for term,value in sorted(rules.items()):
                row=((masks&term)==term).astype(np.int64);add.extend((row,-row));threshold.extend((value,-value));tags.extend((('walk',term,value,0),('walk',term,value,1)))
            if kind=='out':add.append(-(masks==option).astype(np.int64));threshold.append(-1);tags.append(('chosen',option))
            mat=vstack((base,csr_matrix(np.array(add))),format='csc');bound=np.concatenate((rhs,np.array(threshold)));obj=np.zeros(len(masks)+1);obj[-1]=1;sol=linprog(obj,A_ub=hstack((mat,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':8})
            if not sol.status:
                if sol.fun<1e-8:out['status']='fractional'
                else:
                    for scale in (1000,100000,10000000):
                        dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);margin=21*int(min(mat.T@dual))-int(dual@bound)
                        if margin>0:break
                    assert margin>0;out.update(status='separated',margin=margin,dual=[(tags[pos],int(val)) for pos,val in enumerate(dual) if val])
        out['cpu']=process_time()-start;yield out


if __name__=='__main__':
    family={rec['id']:rec['rows'] for rec in map(json.loads,(DEST/'plat.jsonl').read_text().splitlines())}
    for record in map(json.loads,(DEST/'walk-both.jsonl').read_text().splitlines()):
        if record['status']!='fractional':continue
        for case in more(record,family[record['id']]):print(json.dumps(dict(id=record['id'],second=record['second'],**case),separators=(',',':')),flush=True)
