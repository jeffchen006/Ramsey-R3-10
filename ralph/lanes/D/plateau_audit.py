from collections import Counter,defaultdict
from functools import lru_cache
from itertools import combinations,product
import json,subprocess
import numpy as np
from book_strata import DEST
from book_controls import graph_masks
from kernel_cnf import ROOT
from wing_replay import sets,elems


def g6(rows):
    size=len(rows);digits=[(rows[v]>>u)&1 for v in range(size) for u in range(v)];digits.extend([0]*(-len(digits)%6));return chr(63+size)+''.join(chr(63+sum(value<<(5-idx) for idx,value in enumerate(digits[pos:pos+6]))) for pos in range(0,len(digits),6))


def canonical(lines):
    cmd=subprocess.run(['nice','-n','5','timeout','30','prlimit','--cpu=20',str(ROOT/'opt/bin/labelg'),'-q'],input='\n'.join(lines)+'\n',text=True,stdout=subprocess.PIPE,check=True);return set(cmd.stdout.splitlines())


def ridge():
    found={g6([0])};counts=Counter()
    for size in range(1,10):
        assert found==canonical((DEST/f's{size}.g6').read_text().splitlines());children=[]
        for label in sorted(found):
            graph=graph_masks(label);seeds=sets(graph);alpha=max(word.bit_count() for word in seeds);double=18-2*size
            if size<9:
                for hood in seeds:children.append(g6([row|((hood>>point&1)<<size) for point,row in enumerate(graph)]+[hood]))
            for bound in (14,15):
                lows=[max(0,24-bound-2*row.bit_count()) for row in graph];
                if any(low>min(double,8-row.bit_count()) for low,row in zip(lows,graph)) or sum(lows)>double*min(alpha,7):counts[bound,'mass']+=1;continue
                if any((a&b).bit_count()>3 for a,b in combinations(graph,2)) or any((a&b&c).bit_count()>=3 for a,b,c in combinations(graph,3)):counts[bound,'biclique']+=1;continue
                if size==2 and graph==[2,1]:counts[bound,'allowed']+=1;continue
                witness=False
                for first,second in combinations(range(size),2):
                    if graph[first]>>second&1:continue
                    shared=graph[first]&graph[second];occupied=max([0]+[lows[site] for site in elems(shared)]);forced=lows[first]+lows[second]-(double-occupied)
                    if forced>3-shared.bit_count():witness=True;break
                assert witness;counts[bound,'overlap']+=1
        if children:found=canonical(children)
    assert counts[14,'mass']==2479 and counts[15,'allowed']==1;print('PASS vertex-augmentation vs geng through order nine; 5 former SAT tests replaced by explicit forced pair overlaps',counts)


def data(name):return list(map(json.loads,(DEST/(name+'.jsonl')).read_text().splitlines()))


class Audit:
    def __init__(self,rows):
        self.graph=[0]*19;self.links=list(rows);self.pairs={};graph=self.graph
        def edge(a,b):graph[a]|=1<<b;graph[b]|=1<<a
        edge(0,1);edge(0,2)
        for i,word in enumerate(rows):
            edge(1,3+i);edge(2,11+i)
            for j in elems(word):edge(3+i,11+j)
        self.left=next(p for p in range(3,11) if graph[p].bit_count()==2);self.right=next(p for p in range(11,19) if graph[p].bit_count()==2)
        independent=sets(graph);maximum=[word for word in independent if word.bit_count()==9];forbid=[]
        for a,b in combinations(range(19),2):
            if graph[a]>>b&1:continue
            common=(graph[a]&graph[b]).bit_count();limits=(1-common,(1 if (a,b)==(1,2) else 3)-common);self.pairs[1<<a|1<<b]=limits
            if limits[1]==0:forbid.append(1<<a|1<<b)
        masks=[]
        for word in independent:
            if word&6 or word.bit_count()>9 or any(not(word&seed) for seed in maximum) or any((word&term)==term for term in forbid) or any((row&word).bit_count()>3 for row in graph):continue
            if (word&graph[1]).bit_count()+(word>>self.right&1)==3 and (word&graph[2]).bit_count()+(word>>self.left&1)==3:masks.append(word)
        self.masks=np.array(masks,dtype=np.int64);self.columns={}

    def test(self,entry,marked,choice):
        graph=self.graph;groups=defaultdict(set);chosen=None
        for a,b in marked:groups[a].add(b);groups[b].add(a)
        if choice:
            terminal,opt,mode=choice
            if mode=='in':groups[terminal].add(opt);groups[opt].add(terminal)
            if mode=='out':chosen=opt;groups[terminal].add(19)
        requirements={};clash=False;recipes=[]
        if marked:
            first_new,second_new=entry['second'];recipes=[(self.left,{2,first_new}),(self.right,{1,second_new})]
        if choice:
            recipes.extend([(1,{2,self.right}),(2,{1,self.left})]);terminal,opt,mode=choice
            if mode!='closed':recipes.append((terminal,groups[terminal]))
            else:recipes.extend((root,partners) for root,partners in groups.items() if len(partners)==2)
        for root,partners in recipes:
            assert len(partners)==2
            first,second=sorted(partners);far=(graph[second] if second<19 else chosen);assert far>>first&1
            for site in range(19):
                if root==site or graph[root]>>site&1:continue
                want=1 if site in partners else 2 if (graph[first]|far)>>site&1 else 3;term=(1<<site)|(1<<root);want-=(graph[root]&graph[site]).bit_count();clash|=want<0 or requirements.setdefault(term,want)!=want
        if entry['status']=='conflict':assert clash;return
        if entry['status']=='fractional':return
        assert entry['status']=='separated';total=np.zeros(len(self.masks),dtype=np.int64);rhs=0
        for tag,weight in entry['dual']:
            kind,term,*rest=tag;assert 0<weight<10**8
            if kind=='chosen':assert term==chosen;total-=(self.masks==term)*weight;rhs-=weight;continue
            if kind=='walk':low,sign=rest;assert requirements[term]==low;high=low
            else:
                assert kind=='basic';low,high,sign=rest
                if not term:expected=(21,21)
                elif term.bit_count()==1:expected=(9-graph[term.bit_length()-1].bit_count(),)*2
                else:expected=self.pairs[term]
                assert expected==(low,high)
            assert sign in (0,1);factor=weight*(-1 if sign else 1);rhs+=factor*(low if sign else high);mask_key=(term,sign)
            if term not in self.columns:self.columns[term]=((self.masks&term)==term).astype(np.int64)
            total+=factor*self.columns[term]
        assert 21*int(min(total))-rhs==entry['margin']>0


def classes(rows):
    graph=[word<<8 for word in rows]+[sum(1<<u for u,row in enumerate(rows) if row>>v&1) for v in range(8)];pool=set(range(16));path=[];cycles=[]
    while pool:
        frontier={min(pool)};component=set()
        while frontier:
            component|=frontier;frontier=set.union(set(),*(set(elems(graph[v])) for v in frontier))-component
        pool-=component;degrees=sorted(graph[v].bit_count() for v in component);assert degrees.count(1) in (0,2) and set(degrees)<={1,2};(path if degrees[0]==1 else cycles).append(len(component)//2)
    length,=path;return length,tuple(sorted(cycles))


def check():
    family={rec['id']:rec for rec in data('plat')};sequence=set()
    def parts(left,minimum):
        if not left:yield ()
        for value in range(minimum,left+1):
            for tail in parts(left-value,value):yield (value,*tail)
    expected={(length,partition) for length in range(1,9) for partition in parts(8-length,2)};assert len(expected)==15
    both={(r['id'],*r['second']):r for r in data('walk-both')};third={(r['id'],*r['second'],r['mode'],r['option']):r for r in data('third')};visited=set();visited3=set();last=[];hist=Counter()
    for idx,entry in family.items():
        shape=classes(entry['rows']);assert shape not in sequence;sequence.add(shape);audit=Audit(entry['rows']);graph=audit.graph;assert len(audit.masks)==entry['columns'];audit.test(entry,[],None);hist[0,entry['status']]+=1
        if entry['status']!='fractional':continue
        left,right=audit.left,audit.right;initial={(1,2),(2,left),(1,right)}
        for z,w in product(set(elems(graph[2]))-set(elems(graph[left])),set(elems(graph[1]))-set(elems(graph[right]))):
            key=idx,z,w;visited.add(key);rec=both[key];marked=initial|{(left,z),(right,w)}
            # At this stage only the four selected roots are used, not an optional closure at a fifth site.
            audit.test(rec,marked,None);hist[1,rec['status']]+=1
            if rec['status']!='fractional':continue
            active=defaultdict(set)
            for a,b in marked:active[a].add(b);active[b].add(a)
            loose=sorted(v for v in active if len(active[v])==1)
            if not loose:options={('closed',0)};terminal=-1
            else:
                terminal=loose[0];previous,=active[terminal];options={('in',site) for site in elems(graph[previous]) if site!=terminal and site not in elems(graph[terminal]) and len(active.get(site,()))<2};options|={('out',int(mask)) for mask in audit.masks if mask>>previous&1 and not(mask>>terminal&1) and (int(mask)&graph[terminal]).bit_count()<=1}
            for mode,opt in sorted(options):
                fullkey=(*key,mode,opt);visited3.add(fullkey);rec=third[fullkey];assert rec['terminal']==terminal;audit.test(rec,marked,(terminal,opt,mode));hist[2,rec['status']]+=1
                if rec['status']=='fractional':last.append(fullkey);assert set(active)=={0,1,2,left,right} and all(len(neigh)==2 for neigh in active.values());assert all(set(elems(graph[v]))&set(active)==set(active)-neigh-{v} for v,neigh in active.items())
    assert sequence==expected and visited==set(both) and visited3==set(third) and last==[(154435,0,0,'closed',0)];print('PASS path and cycle partitions, all physical choices, separate column catalogue and exact integer separators',hist,'only remaining',last)


if __name__=='__main__':ridge();check()
