from pathlib import Path
from collections import Counter
from datetime import datetime
import json, os, resource, subprocess, sys, time
from eight_chart import get, run
from six_five import encode
from orbit_extend import ROOT, to_graph6

BASE=ROOT/'scratch/F/r24'
OLD=ROOT/'scratch/F/r23/front'
BIN=OLD/'eight'
REGIONS=(3640,3643,4035)
RETIRED=(232982,233198,258295)
def readkeys(path):return list(map(int,path.read_text().split()))
def outcome(row):
    if row[1]=='bare':return 'bare'
    if row[1]=='maskcap':return 'maskcap'
    if 'model' in row:return 'model'
    assert len(row)==24 and row[2]=='I4' and row[13]=='C5' and set((row[3],row[14]))<={'empty','cap'}
    return f'{row[3]}/{row[14]}'
def scan(path,keys):
    done=0
    for item in map(json.loads,path.open()):
        chunk=item['keys'];assert item['start']==done and keys[done:done+len(chunk)]==chunk;done+=len(chunk)
        if item['status']=='complete':
            assert item['rc']==0 and [int(row[0]) for row in item['rows']]==chunk
            for row in item['rows']:yield int(row[0]),outcome(row),row
        else:
            for key in chunk:yield key,'stage',[]
    assert done==len(keys)
def dump(path,rows):path.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
def plan():
    used=set();caps=[];counts=Counter();fresh=set()
    for tag in ('pilot',*(f'wave{i}' for i in range(4))):
        for key,status,row in scan(OLD/(tag+'.jsonl'),readkeys(OLD/(tag+'.keys'))):
            assert key not in used;used.add(key);counts[status]+=1
            if status=='cap/empty':caps.append((key,int(row[1])))
    print('old',counts,len(used),'I4-only tails',len(caps));assert len(used)==193658
    for slot in range(4):
        pool=readkeys(OLD/f'slot{slot}.keys');keys=[key for key in pool if key not in used];assert len(keys)==len(set(keys)) and not fresh.intersection(keys);fresh.update(keys)
        work=BASE/f'slot{slot}';dump(work/'oldtail.tsv',sorted(caps)[slot::4]);
        for stage in range(3):dump(work/f'w{stage}.keys',((key,) for key in keys[stage::3]))
        (work/'eight').symlink_to(BIN)
    domain={key for region in REGIONS for key in range(region<<18,(region+1)<<18) if key>>12 not in RETIRED};assert used|fresh==domain and len(fresh)==580486
    print('untouched',len(fresh),'minus retired',len(domain),'anti-join OK')
def tails(path):
    for key,size in (map(int,line.split()) for line in path.read_text().splitlines()):
        name=str(key);ranges=[(key,start,min(start+16,size)) for start in range(0,size,16)];dump(Path(name+'.tsv'),ranges);before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic()
        with open(name+'.rows','x') as out:proc=subprocess.run(['timeout','510','prlimit','--cpu=450:455','--',BIN,'2000000',name+'.tsv'],stdout=out,input=encode(name,get(key),10,True),text=True,env={**os.environ,'F_PAIR_EXACT':'1'})
        seen=set();states=Counter()
        for line in Path(name+'.rows').read_text().splitlines():
            row=line.split();identity=tuple(map(int,row[:3]));assert identity not in seen and identity in ranges;seen.add(identity);states[row[3]]+=1
            if row[3]=='model':
                adj=list(map(int,row[row.index('graph')+1:]));assert len(adj)==40;graph=Path('target_'+name+'.g6');graph.write_text(to_graph6(adj)+'\n');gate=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',graph],check=True,capture_output=True,text=True);assert json.loads(gate.stdout)['graphs'][0]['ok'];graph.with_suffix('.gate').write_text(gate.stdout);(ROOT/f'ralph/found/F_32eight_{key}.g6').write_bytes(graph.read_bytes())
        after=resource.getrusage(resource.RUSAGE_CHILDREN);cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
        with open('tail.jsonl','a') as log:print(json.dumps(dict(key=key,rc=proc.returncode,size=size,states=states,missing=len(ranges)-len(seen),cpu=round(cpu,4),wall=round(time.monotonic()-start,4))),file=log)
def worker():
    tails(Path('oldtail.tsv'))
    for stage in range(3):
        tag=f'w{stage}';run(tag);rows=[(key,int(row[1])) for key,status,row in scan(Path(tag+'.jsonl'),readkeys(Path(tag+'.keys'))) if status=='cap/empty'];dump(Path(tag+'.tail'),rows);tails(Path(tag+'.tail'))
    print('finished all stages',flush=True)
if __name__=='__main__':plan() if sys.argv[1]=='plan' else worker()
