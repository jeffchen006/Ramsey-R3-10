from pathlib import Path
from collections import Counter
from random import Random
from datetime import datetime
import json,os,resource,subprocess,sys,time
from front24 import BASE,OLD,BIN,REGIONS,get,encode,ROOT,to_graph6,outcome

GLOBAL=BASE/'global'
def stamp():return datetime.now().astimezone().isoformat(timespec='seconds')
def cpu():return sum(entry.ru_utime+entry.ru_stime for entry in (resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)))
def setup():
    random=Random(240032);probes=random.sample([code for code in range(1<<19) if code>>7 not in REGIONS],24);adjacent=[(region^1)*128+74 for region in REGIONS];assert len(set(probes+adjacent))==27
    (GLOBAL/'pilot.tsv').write_text(''.join(f'{prefix} {prefix+1}\n' for prefix in probes+adjacent))
def run(tag,manifest,cap=300000):
    startcpu=cpu();lastcpu=startcpu;lastwall=0;keys=0;finished=0;reserves=180000000
    for idx,(first,last) in enumerate(tuple(map(int,line.split())) for line in manifest.read_text().splitlines()):
        begin=cpu();start=time.monotonic();name=f'{tag}_{idx}';assert not Path(name+'.count').exists();proc=subprocess.run(['timeout','80','prlimit','--cpu=70:72','--',GLOBAL/'sieve','768',str(first),str(last),str(Path.cwd()/(name+'.count'))],cwd=GLOBAL,capture_output=True,text=True);assert proc.returncode==0;counts=list(map(int,Path(name+'.count').read_text().split()));assert counts[:3]==[first,last,(last-first)*2048];live=list(map(int,proc.stdout.split()));assert len(live)==counts[-1] and sorted(set(live))==live and all(first*2048<=key<last*2048 for key in live)
        stages=Counter();complete=True;batchcpu=0
        with open(name+'.rows','x') as out:
            for offset in range(0,len(live),4):
                chunk=live[offset:offset+4];src=''.join(encode(str(key),get(key),10,True) for key in chunk);before=cpu();work=subprocess.run(['timeout','115','prlimit','--cpu=95:100','--',BIN,str(cap)],input=src,text=True,capture_output=True,env={**os.environ,'F_PAIR_EXACT':'1'});batchcpu+=cpu()-before
                if work.returncode!=0:
                    for key in chunk:print(key,'stage',work.returncode,file=out);stages['stage']+=1
                    continue
                rows=[row.split() for row in work.stdout.splitlines()];assert [int(row[0]) for row in rows]==chunk
                for row in rows:
                    state=outcome(row);assert state!='bare';stages[state]+=1;print(*row,file=out)
                    if state=='model':
                        graph=Path('target_'+row[0]+'.g6');adj=list(map(int,row[row.index('graph')+1:]));assert len(adj)==40;graph.write_text(to_graph6(adj)+'\n');gate=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',graph],check=True,capture_output=True,text=True);assert json.loads(gate.stdout)['graphs'][0]['ok'];graph.with_suffix('.gate').write_text(gate.stdout);(ROOT/f'ralph/found/F_global32_{row[0]}.g6').write_bytes(graph.read_bytes())
        assert sum(stages.values())==len(live);keys+=counts[2];finished+=counts[2]-counts[4]+stages['empty/empty'];
        with open(tag+'.jsonl','a') as out: print(json.dumps(dict(idx=idx,first=first,last=last,counts=counts,stages=stages,cpu=round(cpu()-begin,5),physical_cpu=round(batchcpu,5),wall=round(time.monotonic()-start,5))),file=out)
        if time.monotonic()-lastwall>=235:
            used=subprocess.run(['du','-sb',BASE],capture_output=True,text=True);size=int(used.stdout.split()[0]);now=cpu();
            with open(tag+'.meter','a') as out:print(stamp(),keys,finished,round(now-lastcpu,4),size,reserves,file=out)
            lastwall=time.monotonic();lastcpu=now
            if size>300000000:print('size guard',size,flush=True);return
    print(tag,'scanned',keys,'terminal without tail',finished,'cpu',round(cpu()-startcpu,3),flush=True)
if __name__=='__main__':setup() if sys.argv[1]=='setup' else run(sys.argv[1],Path(sys.argv[2]))
