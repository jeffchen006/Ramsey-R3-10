from itertools import combinations
from pathlib import Path
from random import Random
import json,os,resource,subprocess,sys,time
from datetime import datetime
from six_branch import graph,decode,basis
from six_five import encode
from orbit_extend import ROOT,to_graph6

ED=[pair for pair in combinations(range(16),2) if 6<=pair[1]-pair[0]<=12];forest=[];cols=[]
for index,(left,right) in enumerate(ED):
    inc=1<<left|1<<right
    if len(basis(cols+[inc]))>len(cols):cols.append(inc);forest.append(index)
tri=[sum(1<<ED.index(pair) for pair in combinations(group,2)) for group in combinations(range(16),3) if all(pair in ED for pair in combinations(group,2))];pivots=basis([1<<i for i in forest]+tri);free=[i for i in range(len(ED)) if i not in pivots];assert len(ED)==49 and len(forest)==15 and len(tri)==4 and len(free)==30
def get(key):
    word=sum(1<<edge for j,edge in enumerate(free) if key>>j&1)
    for pos,form in sorted(pivots.items()):
        if (word&form).bit_count()%2:word|=1<<pos
    adj=[1<<(vertex^1) for vertex in range(32)]
    for pos,(left,right) in enumerate(ED):
        for side in (0,1):
            src=2*left+side;dst=2*right+(side^1^(word>>pos&1));adj[src]|=1<<dst;adj[dst]|=1<<src
    return adj
def roots():
    out=[]
    for parent in (33854418671,6206451439,34327197559):
        adj=[row%(1<<32) for row in graph(decode(parent))[:32]];flips={0:0}
        for index in forest:
            left,right=ED[index];parity=adj[2*left]>>(2*right)&1
            if left in flips:flips[right]=flips[left]^parity
            else:flips[left]=flips[right]^parity
        perm=[vertex^flips[vertex//2] for vertex in range(32)];normalized=[sum(1<<idx for idx,dest in enumerate(perm) if adj[src]>>dest&1) for src in perm];key=sum(1<<j for j,index in enumerate(free) if normalized[2*ED[index][0]]>>(2*ED[index][1])&1);assert normalized==get(key);out.append(key)
    assert len(set(out))==3;return out
def plan():
    rs=roots();centers=sorted({r>>12 for r in rs});rng=Random(230032);print('roots',rs,'prefixes',centers);raw=sorted({j for prefix in centers for j in range(prefix<<12,(prefix+1)<<12)}-set(rs));pilot=set()
    for root in rs:pilot.update(root^v for v in (1,2,4,8));pilot.update(rng.sample([j for j in raw if j>>12==root>>12],12))
    pilot-=set(rs);pilot=sorted(pilot);fresh=sorted(set(raw)-set(pilot));Path('pilot.keys').write_text(''.join(f'{key}\n' for key in pilot));Path('roots.keys').write_text(''.join(f'{key}\n' for key in rs))
    for slot in range(4):Path(f'slot{slot}.keys').write_text(''.join(f'{key}\n' for key in fresh[slot::4]));
    print('raw',len(raw)+len(rs),'fixed completed',len(rs),'pilot',len(pilot),'fresh',len(fresh))
def run(tag):
    keys=list(map(int,Path(tag+'.keys').read_text().split()));assert not Path(tag+'.jsonl').exists();env={**os.environ,'F_PAIR_EXACT':'1'};latest=0;attempted=closed=0
    for offset in range(0,len(keys),8):
        chunk=keys[offset:offset+8];start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);source=''.join(encode(str(key),get(key),10,True) for key in chunk);cmd=['timeout','125','prlimit','--cpu=105:110','--','./eight','300000'];run=subprocess.run(cmd,input=source,capture_output=True,text=True,env=env);rows=[line.split() for line in run.stdout.splitlines()];status='complete' if run.returncode==0 else 'stage_open'
        if status=='complete':assert [int(row[0]) for row in rows]==chunk
        else:rows=[]
        for row in rows:
            if 'model' in row:
                adj=list(map(int,row[row.index('graph')+1:]));assert len(adj)==40;dest=Path('target_'+row[0]+'.g6');dest.write_text(to_graph6(adj)+'\n');gate=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',dest],capture_output=True,text=True,check=True);assert json.loads(gate.stdout)['graphs'][0]['ok'];dest.with_suffix('.gate').write_text(gate.stdout);(ROOT/f'ralph/found/F_eight_chart_{row[0]}.g6').write_bytes(dest.read_bytes())
        after=resource.getrusage(resource.RUSAGE_CHILDREN);spent=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
        with open(tag+'.jsonl','a') as log:print(json.dumps(dict(start=offset,keys=chunk,rows=rows,status=status,rc=run.returncode,cpu=round(spent,4),wall=round(time.monotonic()-start,4))),file=log)
        attempted+=len(chunk);closed+=sum('cap' not in row and 'maskcap' not in row and 'model' not in row for row in rows)
        if start-latest>210:
            size=int(subprocess.check_output(['du','-sb','.']).split()[0]);allcpu=resource.getrusage(resource.RUSAGE_CHILDREN);latest=start
            with open(tag+'.meter','a') as out:print(datetime.now().astimezone().isoformat(timespec='seconds'),attempted,closed,round(allcpu.ru_utime+allcpu.ru_stime,3),size,file=out)
            if size>50000000:return
    print(tag,'attempted',attempted,'terminal negatives',closed,flush=True)
if __name__=='__main__':plan() if sys.argv[1]=='plan' else run(sys.argv[1])
