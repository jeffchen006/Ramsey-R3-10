"""Independent set-based control and positive-certificate verifier. No use of the book encoders."""
from collections import Counter
from functools import lru_cache
from itertools import combinations,permutations,product
from pathlib import Path
import json,sys
import networkx as nx


def points(word):return {pos for pos in range(word.bit_length()) if word&(1<<pos)}


def matchings(graph,left,right):
    choices=[(a,b) for a in left for b in right if b in graph[a]]
    result={0:{0}}
    for a,b in choices:
        mask=(1<<a)|(1<<b)
        for size,patterns in sorted(list(result.items()),reverse=True):
            result.setdefault(size+1,set()).update(pat|mask for pat in patterns if not pat&mask)
    return result


def census(folder,root):
    positive={(h,a,b,c,d):tail for h,a,b,c,d,*tail in map(json.loads,(folder/'controls.jsonl').read_text().splitlines())};negative={(h,a,b,c,d):tail for h,a,b,c,d,*tail in map(json.loads,(folder/'mixed.jsonl').read_text().splitlines())};stats=Counter();ranks=Counter();answers={}
    for host,line in enumerate((root/'gluing/val/r3_7_22.g6').read_text().splitlines()):
        network=nx.from_graph6_bytes(line.encode());graph=[set(network[vertex]) for vertex in range(22)]
        if {len(row) for row in graph}!={6} or max(len(a&b) for a,b in combinations(graph,2))>3:continue
        stars={}
        for a,b in combinations(range(22),2):
            shared=graph[a]&graph[b]
            if len(shared)!=1:continue
            h,=shared;left=sorted(graph[a]-shared);right=sorted(graph[b]-shared);edges={tuple(sorted((x,y))) for x,y in product(left,right) if y in graph[x]};perms=[perm for perm in permutations(right) if all(y in graph[x] for x,y in zip(left,perm))];stars[a,b]=({a,b,h},left,right,edges,perms)
        for ((a,b),(path,left,right,edges,perms)),((c,d),(other,lhs,rhs,rest,orders)) in combinations(stars.items(),2):
            if path&other:continue
            key=host,a,b,c,d;shown=positive.pop(key);assert tuple(shown[:5]) in perms and tuple(shown[5:])in orders
            count=sum(not((path|set(edge))&(other|set(arc))) for edge,arc in product(edges,rest));stats.update(pairs=1,disjoint=count,matches=len(perms)*len(orders));
            if key in negative:
                x,y,p,q=negative.pop(key);assert x not in path|other and y not in path|other and graph[x]&(path|other)==graph[y]&(path|other)
                switch=lambda z:y if z==x else x if z==y else z
                assert any({p,q}=={u,v} for u,v in product(left,right)) and any({switch(p),switch(q)}=={u,v} for u,v in product(lhs,rhs));assert (p in graph[q])!=(switch(p) in graph[switch(q)]);stats['mixed']+=1
            leftpool=matchings(graph,set(left)-other,set(right)-other);rightpool=matchings(graph,set(lhs)-path,set(rhs)-path)
            rank=max(rank for rank in leftpool.keys()&rightpool.keys() if any(not(first&second) for first,second in product(leftpool[rank],rightpool[rank])));ranks[rank]+=1;answers[key]=rank
    assert not positive and not negative and stats==dict(pairs=1734,disjoint=67189,matches=2234,mixed=1106)
    for quota in [2,3]:
        for data in map(json.loads,(folder/f'counter-cal-{quota}.jsonl').read_text().splitlines()):assert (data['status']=='forces')==(answers[tuple(data['id'])]>=quota)
    (folder/'c22-balanced.tsv').write_text(''.join('\t'.join(map(str,(*key,rank)))+'\n' for key,rank in sorted(answers.items())))
    print('NetworkX C22',stats,'exact maximum common quota by independent partial-edge matching enumeration',ranks)


def replay(folder,root):
    originals=(root/'scratch/D/ind10/four-40.in').read_text().splitlines();source=(root/'scratch/D/flag12/disjoint102.in').read_text().splitlines();actual={originals.index(line):list(map(int,line.split())) for line in source};assert len(actual)==102
    claim={record['id']:record['certificate'] for record in map(json.loads,(folder/'seed-roots-4.jsonl').read_text().splitlines())};assert set(claim)==actual.keys();pending=[]; greedy=[];hashes=Counter();bound={}
    for idx,(fixed,*words) in actual.items():
        assert fixed==15;graph=[points(word) for word in words];ends=[(0,1),(2,3)];centres=[next(iter(graph[a]&graph[b])) for a,b in ends];paths=[set(pair)|{w} for pair,w in zip(ends,centres)];assert not(paths[0]&paths[1]);wings=[(graph[a]|graph[b])-{h} for (a,b),h in zip(ends,centres)];private=[wing-(paths[0]|paths[1]) for wing in wings]
        hit=[len(wing&paths[1-side]) for side,wing in enumerate(wings)];overlap=len(private[0]&private[1]);cross=sum(c in graph[a] for a,c in product(*ends));witness_hit=[int(bool(graph[h]&set(ends[1-side]))) for side,h in enumerate(centres)];assert overlap<=3*(4-cross)-2*sum(witness_hit)
        lost=2 if cross==2 else 0;multiple=(8-hit[0])*(8-hit[1])-(overlap-lost)
        if cross==1 and hit==[2,2]:multiple=min(6*7-overlap,6*6-(overlap-2))
        bound[cross]=min(multiple,bound.get(cross,100));
        if claim[idx]:
            seed0,side0,seed1,side1=map(points,claim[idx]);assert not(side0&side1)
            def forbidden(a,b):return a!=b and ((a<4 or b<4) and b not in graph[a] or bool(graph[a]&graph[b]&{0,1,2,3}))
            for side,(seed,pool) in enumerate(((seed0,side0),(seed1,side1))):
                assert pool<=private[side] and not(seed&pool) and len(pool)+len(seed)>=13
                assert all(forbidden(a,b) for a,b in combinations(seed,2)) and all(forbidden(a,b) for a,b in product(pool,seed))
            hashes['seed']+=1;continue
        for orientation in (0,1):
            left,right=8-hit[orientation],8-hit[1-orientation]
            if right>=8 and overlap<=2*(left-4)+right-4:greedy.append(idx);break
        else:pending.append(idx)
    assert len(greedy)==8 and sorted(pending)==[110,119,179];print('positive seed certificates',hashes,'greedy',greedy,'pending',pending,'disjoint interface lower bounds',bound)
    records=list(map(json.loads,(folder/'mate-cases.jsonl').read_text().splitlines()));seen={}
    for idx in pending:
        fixed,*words=actual[idx];graph=[points(word) for word in words];paths=[];groups=[]
        for a,b in [(0,1),(2,3)]:
            h,=graph[a]&graph[b];paths.append({a,b,h});groups.append((graph[a]-{h},graph[b]-{h}))
        marked=paths[0]|paths[1];options=[];excluded=[];pool=[]
        for side,wing in enumerate(groups):
            blocked,=(wing[0]|wing[1])&marked;excluded.append(blocked);far,=[sites for sites in wing if blocked not in sites];options.append({mate for mate in far if (mate>3 and blocked>3 or mate in graph[blocked]) and not(graph[mate]&graph[blocked])});pool.append((wing[0]|wing[1])-marked)
        listed=[rec for rec in records if rec['id']==idx];assert {tuple(rec['mates']) for rec in listed}==set(product(*options));rep=listed[0];
        for rec in listed:
            assert rec['blocked']==excluded;mates=rec['mates'];assert [points(x) for x in rec['private']]==[pool[i]-(pool[1-i]-{mates[1-i]}) for i in (0,1)]
            for x,y in zip(mates,rep['mates']):assert graph[x]==graph[y]
            assert not(set(options[0])&set(options[1]));
            if idx==110:
                forced=points(rec['I']);assert len(forced)==10
                for a,b in combinations(forced,2):assert a<4 and b not in graph[a] or b<4 and a not in graph[b] or graph[a]&graph[b] or any({a,b}<=points(mask) for mask in rec['private'])
        seen[idx]=(len(listed),rep['mates'])
    print('all ordered mate choices independently rebound; direct I10 on index 110; equal-colour transpositions fix the two other rosters',seen)


if __name__=='__main__':
    folder=Path(sys.argv[1]);root=Path(__file__).resolve().parents[3];census(folder,root);replay(folder,root)
