from itertools import combinations
from pathlib import Path
from collections import Counter
import json,sys,subprocess,time,resource
from orbit_extend import ROOT,parse_graph6,to_graph6

EDGES=[pair for pair in combinations(range(17),2) if 6<=pair[1]-pair[0]<=12]
def basis(rows):
    pivots={}
    for value in rows:
        while value and value.bit_length()-1 in pivots:value^=pivots[value.bit_length()-1]
        if value:pivots[value.bit_length()-1]=value
    return pivots
def equations():
    rows=[];used=[]
    for index,(left,right) in enumerate(EDGES):
        col=1<<left|1<<right
        if len(basis(used+[col]))>len(used):used.append(col);rows.append(1<<index)
    for triple in combinations(range(17),3):
        pairs=list(combinations(triple,2))
        if all(pair in EDGES for pair in pairs):rows.append(sum(1<<EDGES.index(pair) for pair in pairs))
    assert len(rows)==21
    return basis(rows)
PIVOTS=equations();FREE=[index for index in range(len(EDGES)) if index not in PIVOTS]
def decode(key):
    word=sum(1<<edge for index,edge in enumerate(FREE) if key>>index&1)
    for pos,eq in sorted(PIVOTS.items()):
        if (word&eq).bit_count()%2:word|=1<<pos
    return word
def encode(word):return sum(1<<index for index,pos in enumerate(FREE) if word>>pos&1)
def graph(word):
    adj=[1<<(vertex^1) for vertex in range(34)]
    for pos,(left,right) in enumerate(EDGES):
        for side in (0,1):
            src=2*left+side;dest=2*right+(side^1^(word>>pos&1));adj[src]|=1<<dest;adj[dest]|=1<<src
    return adj
def record(key,adj,target=10,outer=6):return ' '.join(map(str,[key,len(adj),target,outer,*adj]))+'\n'
def gate(name,adj,target):
    path=Path(name+'.g6');path.write_text(to_graph6(adj)+'\n');run=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',path,str(len(adj)),str(target)],capture_output=True,text=True,check=True);assert json.loads(run.stdout)['graphs'][0]['ok'];path.with_suffix('.gate').write_text(run.stdout)
def go(data,timeout=50,cap=2000000):
    return subprocess.run(['timeout',str(timeout),'prlimit',f'--cpu={timeout-2}:{timeout-1}','--','./six',str(cap)],input=data,capture_output=True,text=True,check=True).stdout
def control():
    labels=[1,12,2,11,4,9,0,3,5,6,7,8];old=6;full=[sum(1<<index for index,dest in enumerate(labels) if (dest-src)%13 in (1,5,8,12)) for src in labels];gate('sixplant12',full,5)
    core=[(row%64)|1<<(vertex^1) for vertex,row in enumerate(full[:old])];assert any(row&3==3 for row in full[old:]);assert any(row&12==12 for row in full[old:]);
    smaller=core[:4];smaller=[row&15 for row in smaller]
    rows=go(record('plant',core,5,6)+record('one_positive',smaller,4,1)+record('six_negative',smaller,4,6));print(rows,end='');result=[row.split() for row in rows.splitlines()];assert result[0][1]==result[1][1]=='model' and result[2][1]=='multi';
    for row,target in zip(result[:2],(5,4)):gate('searched_'+row[0],list(map(int,row[row.index('graph')+1:])),target)
    ref=ROOT/'scratch/F/r22/wider/core34.signs';data=ref.read_text().splitlines();
    for line in data:
        signing,text=line.split();word=int(signing);assert decode(encode(word))==word and parse_graph6(text)==graph(word)
    print('signed graph6 roundtrip',len(data),'free bits',len(FREE),'first',encode(int(data[0].split()[0])))
def sample(keys,tag):
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();data=''.join(record(key,graph(decode(key))) for key in keys);out=go(data,150);Path(tag+'.rows').write_text(out);after=resource.getrusage(resource.RUSAGE_CHILDREN);print(tag,len(keys),dict(Counter(row.split()[1] for row in out.splitlines())), 'solver_cpu',after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall',time.monotonic()-start,flush=True)
def hard_keys():
    keys=[]
    for tag in ('3024','3032','6049','6064','14241'):
        raw=parse_graph6((ROOT/f'scratch/F/r22/ext/{tag}_0-p1.g6').read_text().strip());edgesign=sum(1<<index for index,(left,right) in enumerate(EDGES) if raw[2*left]>>(2*right)&1)
        coords={0:0}
        for index,(left,right) in enumerate(EDGES):
            if PIVOTS.get(index)!=1<<index:continue
            if left in coords:coords[right]=coords[left]^(edgesign>>index&1)
            elif right in coords:coords[left]=coords[right]^(edgesign>>index&1)
            else:raise ValueError('unexpected disconnected prefix')
        normalized=edgesign^sum(1<<index for index,(left,right) in enumerate(EDGES) if coords[left]^coords[right]);assert decode(encode(normalized))==normalized
        key=encode(normalized);print(tag,key);keys.append(key)
    return sorted(set(keys))
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    elif sys.argv[1]=='sample':
        ref=ROOT/'scratch/F/r22/wider/core34.signs';known=[encode(int(line.split()[0])) for line in ref.read_text().splitlines()];
        sample(known[:4],'four_known');sample([known[0]^i for i in range(32)],'siblings');sample([i*123456791%(1<<35) for i in range(128)],'spread')
    elif sys.argv[1]=='hard':sample(hard_keys(),'hard')
