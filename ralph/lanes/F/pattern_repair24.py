from pathlib import Path
from collections import Counter,defaultdict
from itertools import combinations
from datetime import datetime
import json,os,subprocess,sys,resource,time
from source24 import DIR,ROOT,get,gate,subgraph,parse_graph6,R23

REPAIR=DIR/'repair'
def work(tag,adj,target,paired,shapes,limit):
    size=len(shapes[0][1]);assert all(len(graph)==size for name,graph in shapes);source=' '.join(map(str,[tag,-len(adj) if paired else len(adj),target,size,len(shapes),*adj]))+'\n'+''.join(' '.join(map(str,[name,*graph]))+'\n' for name,graph in shapes);path=Path(tag+'.rows');assert not path.exists();before=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()
    with path.open('x') as output:run=subprocess.run(['timeout','160','prlimit','--cpu=140:145','--',os.getenv('F_PATTERN24_FIXED',str(REPAIR/'fixed')),str(limit)],input=source,stdout=output,text=True)
    rows=[line.split() for line in path.read_text().splitlines()];states=Counter();ids=set();wanted=dict(shapes)
    for row in rows[1:]:
        idx=int(row[1]);assert row[0]==tag and idx not in ids and idx in wanted;ids.add(idx);states[row[2]]+=1
        if row[2]=='model':
            model=list(map(int,row[5:]));assert len(model)==len(adj)+size and [value>>len(adj) for value in model[len(adj):]]==wanted[idx];assert all((model[vertex]&(1<<len(adj))-1)^adj[vertex] in ((0,1<<(vertex^1)) if paired else (0,)) for vertex in range(len(adj)));gate(model,target,Path(f'{tag}_{idx}.g6'))
    after=resource.getrusage(resource.RUSAGE_CHILDREN);return dict(tag=tag,rc=run.returncode,masks=rows[0][2:] if rows else None,states=states,missing=len(wanted)-len(ids),cpu=round(after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,5),wall=round(time.monotonic()-wall,5))
def control():
    small=parse_graph6((R23/'sixplant12.g6').read_text().strip());core=[value|1<<(idx^1) for idx,value in enumerate(subgraph(small,range(4)))];shape=subgraph(small,range(4,12));
    for tag,target,result in [('plant12',5,'model'),('neg12',4,'empty')]:
        answer=work(tag,core,target,True,[(0,shape)],200000);assert answer['states'][result]==1;print(json.dumps(answer),flush=True)
    known=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());answer=work('known39',subgraph(known,range(31)),10,False,[(0,subgraph(known,range(31,39)))],500000);assert answer['states']['model']==1;print(json.dumps(answer),flush=True)
def plan(tag):
    previous=set()
    for path in [*REPAIR.glob('*.tsv'),*REPAIR.glob('work*/manifest.tsv')]:
        for line in path.read_text().splitlines():
            key,*names=map(int,line.split());previous.update((key,name) for name in names)
    hits=defaultdict(set)
    for log in (DIR/'pilot.jsonl',DIR/'work0/seven/worker.jsonl',DIR/'work0/six.jsonl',DIR/'work1/six.jsonl'):
        if not log.exists():continue
        for line in log.open():
            if not line.endswith('\n'):break
            row=json.loads(line);key=int(row['tag']);assert row['rc']==row['missing']==0
            if not row['states'].get('cap'):continue
            for values in (log.parent/(str(key)+'.rows')).read_text().splitlines():
                fields=values.split();name=int(fields[1]);
                if fields[2]=='cap' and (key,name) not in previous:hits[key].add(name)
    ordered=[]
    for size in (7,6):
        for key,values in sorted(hits.items()):
            names=sorted(name for name in values if name//100==size);
            if names:ordered.append((key,*names))
    (REPAIR/(tag+'.tsv')).write_text(''.join(' '.join(map(str,row))+'\n' for row in ordered));print(tag,'word/size groups',len(ordered),'physical keys',sum(len(row)-1 for row in ordered),'C7',sum(700 in row[1:] for row in ordered))
def run(path,limit):
    inventory={int(name):graph for name,graph in json.loads((DIR/'patterns.json').read_text()).items()};
    for line in path.read_text().splitlines():
        key,*names=map(int,line.split());print(json.dumps(work(str(key)+'_'+str(names[0]//100),get(key),10,True,[(name,inventory[name]) for name in names],limit)),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    elif sys.argv[1]=='plan':plan(sys.argv[2])
    else:run(Path(sys.argv[2]),int(sys.argv[3]))
