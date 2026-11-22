from pathlib import Path
from collections import Counter
from datetime import datetime
import json,os,resource,subprocess,sys,time
from eight_chart import get
from six_five import encode
from orbit_extend import ROOT,to_graph6

def plan():
    residual={};processed=set()
    for file in sorted(Path('../chart').glob('*.jsonl')):
        for row in map(json.loads,file.read_text().splitlines()):
            assert row['status']=='complete'
            for values in row['rows']:
                key=int(values[0]);assert key not in processed;processed.add(key)
                if 'cap' in values:assert values[2:4]==['I4','cap'] and values[13:15]==['C5','empty'];residual[key]=int(values[1]);
                else:assert 'model' not in values and 'maskcap' not in values
    assert len(processed)==12285;data=[]
    for key,size in sorted(residual.items()):
        rows=[(key,lower,min(lower+16,size)) for lower in range(0,size,16)];data+=rows;Path(str(key)+'.tsv').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
    for slot in range(4):Path(f'slot{slot}.keys').write_text(''.join(f'{key}\n' for key in sorted(residual)[slot::4]));
    print('cap replacement signs',len(residual),'mask starts',sum(residual.values()),'disjoint intervals',len(data),'C5 already terminal on every input')
def worker(slot):
    keys=list(map(int,Path(f'slot{slot}.keys').read_text().split()));env={**os.environ,'F_PAIR_EXACT':'1'};last=0;done=0
    for key in keys:
        start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);src=Path(str(key)+'.rows');assert not src.exists();expected={tuple(map(int,line.split())) for line in Path(str(key)+'.tsv').read_text().splitlines()};states=[]
        with src.open('x') as output:run=subprocess.run(['timeout','500','prlimit','--cpu=450:455','--','../split/eight','2000000',str(key)+'.tsv'],input=encode(key,get(key),10,True),text=True,stdout=output,env=env)
        for line in src.read_text().splitlines():
            row=line.split();identity=tuple(map(int,row[:3]));expected.remove(identity);states.append(row[3]);assert row[3] in ('model','empty','cap')
            if row[3]=='model':
                adj=list(map(int,row[row.index('graph')+1:]));assert len(adj)==40;dest=Path(f'target_{key}_{row[1]}.g6');dest.write_text(to_graph6(adj)+'\n');gate=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',dest],capture_output=True,text=True,check=True);assert json.loads(gate.stdout)['graphs'][0]['ok'];dest.with_suffix('.gate').write_text(gate.stdout);(ROOT/f'ralph/found/F_chart_tail_{key}_{row[1]}.g6').write_bytes(dest.read_bytes())
        status='closed' if run.returncode==0 and not expected and set(states)=={'empty'} else 'open';after=resource.getrusage(resource.RUSAGE_CHILDREN);cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime);done+=status=='closed'
        with open(f'slot{slot}.jsonl','a') as out:print(json.dumps(dict(key=key,status=status,states=dict(Counter(states)),missing=len(expected),rc=run.returncode,cpu=round(cpu,5),wall=round(time.monotonic()-start,5))),file=out)
        if start-last>210:
            last=start;bytes_used=int(subprocess.check_output(['du','-sb','.']).split()[0]);
            with open(f'slot{slot}.meter','a') as out:print(datetime.now().astimezone().isoformat(timespec='seconds'),done,round(after.ru_utime+after.ru_stime,3),bytes_used,file=out)
    print('done slot',slot,'closed',done,'assigned',len(keys),flush=True)
if __name__=='__main__':plan() if sys.argv[1]=='plan' else worker(int(sys.argv[1]))
