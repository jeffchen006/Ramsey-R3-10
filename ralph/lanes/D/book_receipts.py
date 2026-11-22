"""Semantic controls for the table CNF, independent rooted view keys, and saved partial models."""
from collections import Counter,defaultdict
from itertools import combinations,product
from pathlib import Path
import json,sys
from pysat.solvers import Cadical195
from book_controls import sites,book,bitset
from book_seedpack import upper
from book_obstructions import prepare
from book_reroot import catalogue
from book_select import allowed_templates


def tables(folder):
    gold={tuple(map(int,fields[:-1])):int(fields[-1]) for fields in (line.split() for line in (folder/'c22-balanced.tsv').read_text().splitlines())};summary=Counter()
    for key,frame,truth in map(json.loads,(folder/'cal.in').read_text().splitlines()):
        may=upper(frame);record={'lo':frame[1:],'ban':[((1<<len(truth))-1)&~(row|1<<point) for point,row in enumerate(may)]};sys,_=prepare(frame,record,3,'general');form=sys.form;solver=Cadical195(bootstrap_with=form.clauses);res=solver.solve(assumptions=[form.edge(left,right,False)*(1 if truth[left]>>right&1 else -1) for left,right in combinations(range(len(truth)),2)]);solver.delete();assert res==(gold[tuple(key)]<3);summary[res]+=1
    print('Pruned all-partitions formula on planted labelled C22, quota three',summary)


def reroot(folder):
    frames={key:frame[1:] for key,frame,_ in map(json.loads,(folder/'roots.in').read_text().splitlines())};high=[key for key,rows in frames.items() if all(rows[first]>>second&1 or (rows[first]&rows[second]).bit_count()==3 for first,second in product((0,1),(2,3)))];assert high==[119,121,122,175,178,179,191]
    for group in ((119,179),tuple(high)):
        common=defaultdict(set);anchors=defaultdict(set)
        for key in group:
            stars=[set(sites(row)) for row in frames[key]]
            for first,second in [(0,2),(2,0)]:
                for a in [first,first+1]:
                    for c in [second,second+1]:
                        b=first+(a==first);d=second+(c==second);assert len({a,b,c,d})==4
                        cent,=stars[a]&stars[b];opp,=stars[c]&stars[d];bits=tuple(int(t in stars[s]) for s,t in [(a,c),(a,d),(b,c),(b,d)]);flag=int(c in stars[cent])+2*int(d in stars[cent]);pattern=tuple(int(s in stars[opp]) for s in [a,b])+tuple(len(stars[s]&stars[t]) for s,t in [(a,c),(a,d),(b,c),(b,d)]);common[bits,flag].add(pattern)
                        order=[a,b,c,d];inside=tuple(int(t in stars[s]) for s,t in combinations(order,2));sizes=[];contacts=[]
                        for cell in range(8):
                            points={site for site in range(4,40) if all(bool((cell>>i)&1)==(site in stars[vertex]) for i,vertex in enumerate([a,c,d]))};sizes.append(len(points));contacts.append(len(points&stars[b]))
                        anchors[inside,tuple(sizes)].add(tuple(contacts))
        source=[(frames[key],(0,1),(2,3)) for key in group];assert common==allowed_templates(source) and anchors==catalogue(source);print('independent two-template compilations',group,'witness-patterns',sum(map(len,common.values())),'three-star histograms',sum(map(len,anchors.values())))


def export(folder):
    source=(folder.parent/'ind10/four-40.in').read_text().splitlines();roots=(folder.parent/'flag12/disjoint102.in').read_text().splitlines();kept=[row for row in roots if source.index(row)!=179];assert len(kept)==101;(folder/'four-star101.in').write_text(''.join(row+'\n' for row in kept))
    tested=list(map(json.loads,(folder/'single-types.jsonl').read_text().splitlines()));counts={}
    for flag,name in [(True,'general'),(False,'K2')]:
        ids=[row['id'] for row in tested if row['general']==flag and row['status']!='excluded'];pairs=[(left,right) for left in ids for right in ids if left<=right];(folder/('pairs-'+name+'.tsv')).write_text(''.join(f'{left}\t{right}\n'for left,right in pairs));counts[name]=len(pairs)
    assert counts==dict(general=528,K2=465);print('Export: 101 original-coordinate roots and abstract type pairs',counts)


def models(folder):
    original=folder.parent/'flag12';full=[tuple(map(int,line.split()[:5])) for line in (original/'interfaces.tsv').read_text().splitlines()];lookup={}
    for idx,word in enumerate(full):
        arcs={(row,col) for row in range(5) for col in range(5) if word[row]>>col&1}
        for source in (arcs,{(col,row) for row,col in arcs}):
            for x,y in product((1,-1),repeat=2):lookup[frozenset((a*x%5,b*y%5) for a,b in source)]=idx
    assert len(lookup)==12278;summary=Counter()
    for name,file in [('parent','parent-price'),('front','general-panel-price')]:
        inputs={str(key):frame for key,frame,_ in map(json.loads,(folder/(file+'.in')).read_text().splitlines())}
        for mode in ('one','all','allpack'):
            result=folder/(f'pack-{file}.jsonl' if mode=='allpack' else f'fixed-parent-{mode}.jsonl' if name=='parent' else f'fixed-general-panel-price-{mode}.jsonl');records=[json.loads(line)for line in result.read_text().splitlines()];assert len(records)==len(inputs)
            for record in records:
                assert record['status']=='compatible';fixed,*base=inputs[str(record['id'])];rows=record['adj'];found=[]
                for point,row in enumerate(rows):
                    if fixed>>point&1:assert row==base[point]
                    for other in range(len(rows)):assert (row>>other)&1==(rows[other]>>point)&1
                for side,ends in enumerate(((0,1),(2,3))):
                    path,(left,right)=book(rows,ends);picks=record['picks'][side];assert len({pair[0] for pair in picks})==len({pair[1] for pair in picks})==len(picks)==(1 if mode=='one' else 8)
                    for a,b in picks:assert a in left and b in right and rows[a]>>b&1
                    fill=picks if mode=='one' else [(a,b) for a,b in product(left,right) if rows[a]>>b&1];found.append([(path[0],path[1],a,b,path[2])for a,b in fill])
                if mode=='allpack':
                    taken={site for ends in ((0,1),(2,3)) for site in book(rows,ends)[0]}
                    for group,ends in zip(record['bouquet'],((0,1),(2,3)),strict=True):
                        assert len(group)==4;_,(lhs,rhs)=book(rows,ends)
                        for a,b in group:assert a in lhs and b in rhs and rows[a]>>b&1 and not({a,b}&taken);taken.update((a,b))
                    assert len(taken)==22
                counted=0
                for left,right in product(*found):
                    if set(left)&set(right):continue
                    mask=frozenset((a,b) for a,v in enumerate(left) for b,w in enumerate(right) if rows[v]>>w&1);assert mask in lookup;counted+=1
                assert counted==record['interfaces'] and counted>0;summary[name,mode]+=1
    print('Replayed physical assignment, selector size and every realized disjoint interface',summary)


if __name__=='__main__':
    folder=Path(sys.argv[1]);tables(folder);reroot(folder);models(folder);export(folder)
