"""Independent projected-rank checker: add a fresh vertex variable for every selected site."""
from collections import Counter,defaultdict
from itertools import combinations,combinations_with_replacement
from pathlib import Path
import json
import subprocess
import sys

from cyclic_check import read_base
from orbit_extend import ROOT, independent_sets,to_graph6,vertices


def put(name,rows):
    Path(name).write_text(''.join(f'{row}\n' for row in rows))


def normal(space,row):
    for pivot in sorted(space,reverse=True):
        if row & pivot:row ^= space[pivot]
    return row


def insert(space,row):
    row=normal(space,row)
    if row:space[1<<(row.bit_length()-1)]=row


def parse_request(row):
    name,count,edges,*data=row.split();feet=list(map(int,data[::2]));tops=list(map(int,data[1::2]));assert len(feet)==len(tops)==int(count)
    return name,int(edges),feet,tops


def replay(basepath,order,request,trace):
    graph=read_base(Path(basepath).read_text().strip());size=len(graph);assert all(graph[site][site]==1 for site in range(size))
    pairs=[(left,right) for right in range(size) for left in range(right) if graph[left][right]]
    keys={edge:2<<index for index,edge in enumerate(pairs)};triangles={}
    for triangle in combinations(range(size),3):
        sides=list(combinations(triangle,2))
        if all(edge in keys for edge in sides):insert(triangles,sum(keys[edge] for edge in sides))
    traces=defaultdict(list)
    for line in Path(trace).read_text().splitlines():
        name,*word=line.split();traces[name].append(word)
    result=Counter();steps=Counter()
    for line in Path(request).read_text().splitlines():
        name,edges,feet,tops=parse_request(line);basis=triangles.copy();columns=[];overlap=False;used=set()
        for foot,high in zip(feet,tops):
            column={(site,(high>>site)&1) for site in vertices(foot)};assert high&~foot==0
            overlap|=bool(used&column);used|=column;columns.append(column)
            for (left,first),(right,second) in combinations(sorted(column),2):
                if (left,right) in keys:insert(basis,keys[left,right]^first^second)
        events=traces.pop(name);end,status,nsteps=events.pop();assert end=='end' and int(nsteps)==len(events);result[status]+=1
        if overlap:assert status=='collision';continue
        if 1 in basis:assert status=='triangles';continue
        assert status in ('I','open');stopped=False
        for typ,rawp,raws,rawrow in events:
            assert typ=='step' and not stopped
            poles=list(vertices(int(rawp)));support=list(vertices(int(raws)));advertised=int(rawrow)
            assert len(support)+len(poles)==order and all(not(edges>>(right*(right-1)//2+left)&1) for left,right in combinations(poles,2))
            lifted={}
            for left,right in combinations(support,2):
                if (left,right) in keys:insert(lifted,(1<<(64+left))^(1<<(64+right))^keys[left,right])
            for pole in poles:
                for site,value in columns[pole]:
                    if site in support:insert(lifted,(1<<(64+site))^(1-value))
            residual={}
            for pivot,row in lifted.items():
                if pivot<(1<<64):insert(residual,normal(basis,row))
            assert len(residual)<=1 and 1 not in residual
            if not residual:assert not advertised;stopped=True
            else:
                only=next(iter(residual.values()));assert not normal(basis,only^advertised);insert(basis,only^1)
            steps[len(poles),bool(advertised)]+=1
        assert (status=='I')==stopped
    assert not traces
    print('independent projected-rank replay:',request,sorted(result.items()),'steps',sorted(steps.items()))


def control():
    order=4;perm=[0,4,1,5,2,6,3,7]
    graph=[sum(1<<other for other,dest in enumerate(perm) if (dest-src)%8 in (1,4,7)) for src in perm]
    polar=sum(1<<(right*(right-1)//2+left) for left,right in combinations(range(4),2) if graph[4+left]>>(4+right)&1)
    put('control.q',['C111']);requests=[];gates=[]
    for mutation in range(-1,4):
        actual=graph.copy();name='positive' if mutation==-1 else f'cut{mutation}'
        if mutation!=-1:
            end=4+mutation;left=(actual[end]&15).bit_length()-1;actual[end]^=1<<left;actual[left]^=1<<end
        raw=[]
        for row in actual[4:]:
            mask=row&15;foot=sum(1<<(site//2) for site in vertices(mask));high=sum(1<<(site//2) for site in vertices(mask) if site%2);raw.extend([foot,high])
        requests.append(' '.join(map(str,[name,4,polar,*raw])))
        put(f'{name}.g6',[to_graph6(actual)]);literal=json.loads(subprocess.check_output([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',f'{name}.g6','8','4']))
        put(f'{name}.gate',[json.dumps(literal,sort_keys=True)]);assert literal['graphs'][0]['ok']==(mutation==-1)
        bad=next(independent_sets(actual,255,4),None);assert (bad is None)==(mutation==-1);gates.append((name,bad))
    put('control.request',requests);subprocess.run(['./join','control.q','4','control.request','control.trace','4'],check=True)
    statuses=[row.split()[2] for row in Path('control.trace').read_text().splitlines() if ' end ' in row];assert statuses==['open']+['I']*4
    replay('control.q',order,'control.request','control.trace');print('M8: two shared sites, four disjoint physical columns; gate and direct I4 masks',gates)


def orbit(mask):
    return {sum(1<<((shift+unit*site)%18) for site in vertices(mask)) for shift in range(18) for unit in (1,-1)}


def roster():
    source=Path('../r13/col15.q').read_text().strip();base=read_base(source);assert all(base[left][right]==int(min((left-right)%18,(right-left)%18) in (0,5,7,8,9)) for left in range(18) for right in range(18))
    put('target.q',[source]);pool=sorted({single for full,single,size,stage in (map(int,row.split()) for row in Path('../r13/col15.rows').read_text().splitlines()) if not full and size<=7 and stage==3})
    assert Counter(map(int.bit_count,pool))=={6:99,7:594};reps=sorted({min(orbit(mask)) for mask in pool});assert set.union(*(orbit(rep) for rep in reps))==set(pool)
    put('rep.counts',[f'{rep} {len(orbit(rep))}' for rep in reps]);put('single.request',[f'{mask} 1 0 {mask} 0' for mask in reps]);put('pilot.request',Path('single.request').read_text().splitlines()[::7]);print('693 columns ->',len(reps),'D18 reps, pilot every seventh')
    pairs=[]
    for pos,left in enumerate(reps[::7]):
        for right in (left,pool[100+pos*5],pool[400+pos*8]):
            pairs.append(f'{left}_{right} 2 1 {left} 0 {right} {left&right}')
    put('pilotpair.request',pairs)


def choices():
    pool=sorted(set.union(*(orbit(int(row.split()[0])) for row in Path('single.result').read_text().splitlines() if row.split()[1]=='open')))
    assert len(pool)==3 and all(mask.bit_count()==6 for mask in pool) and not any(first&second for first,second in combinations(pool,2))
    pairs=[];quartets=[];roles=Counter()
    for count,output in ((2,pairs),(4,quartets)):
        for feet in combinations_with_replacement(pool,count):
            if max(Counter(feet).values())>2:continue
            used=0;data=[]
            for mask in feet:data.extend([mask,mask&used]);used|=mask
            for internal in range(1<<(count*(count-1)//2)):
                def edge(left,right):return (internal>>(right*(right-1)//2+left))&1
                if any(edge(left,right) and edge(left,mid) and edge(mid,right) for left,mid,right in combinations(range(count),3)):continue
                name='_'.join(map(str,(*feet,internal)));output.append(' '.join(map(str,(name,count,internal,*data))));roles[count]+=1
    put('pair.request',pairs);put('quartet.request',quartets);print('survivor site masks',pool,'roles',dict(roles))


if __name__=='__main__':
    if sys.argv[1]=='replay':replay(sys.argv[2],int(sys.argv[3]),*sys.argv[4:])
    else:{'control':control,'roster':roster,'choices':choices}[sys.argv[1]]()
