from collections import Counter
from datetime import datetime,timedelta
from pathlib import Path
import gzip,json,os,resource,subprocess,sys,time
from six_branch import ROOT,to_graph6

HERE=Path.cwd();assert HERE.is_relative_to(ROOT/'scratch/F/r23');assert HERE.name=='r23'
def stamp():return datetime.now().astimezone().isoformat(timespec='seconds')
def cpu():
    self,child=(resource.getrusage(kind) for kind in (resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN));return sum(entry.ru_stime+entry.ru_utime for entry in (self,child))
def manifest(tag,roots,depth):
    size=1<<(35-depth-11);assert size>=256
    processed=set()
    for path in sorted([*HERE.glob('price*.count'),*HERE.glob('trial*.count'),*HERE.glob('strata*.count')]):
        fields=list(map(int,path.read_text().splitlines()[-1].split()));assert fields[1]==65536
        processed.update(range(fields[0]-32,fields[0]))
    previous=[]
    for path in sorted(HERE.glob('plan_*.tsv')):
        assert path.stem!='plan_'+tag
        previous.extend(tuple(map(int,line.split()[1:])) for line in path.read_text().splitlines())
    previous.sort();other=iter(previous);region=next(other,None);rows=[]
    for root in sorted(roots):
        step=min(size,2048 if tag=='all' else 256)
        for chunk in range(root*size,(root+1)*size,step):
            start=None
            for prefix in range(chunk,chunk+step):
                while region and region[1]<=prefix:region=next(other,None)
                eligible=prefix not in processed and not(region and region[0]<=prefix<region[1]);
                if eligible and start is None:start=prefix
                if not eligible and start is not None:rows.append((start,prefix));start=None
            if start is not None:rows.append((start,chunk+step))
    path=Path('plan_'+tag+'.tsv');path.write_text(''.join(f'{index}\t{start}\t{end}\n' for index,(start,end) in enumerate(rows)));print(tag,'leaves',len(rows),'fresh words',sum((end-start)*2048 for start,end in rows),'roots',roots,'prefix_bits',depth)

def worker(tag,slot):
    directory=Path('work_'+tag);directory.mkdir(exist_ok=True);log=directory/f'w{slot}.jsonl';latest=0
    prior=[json.loads(line) for line in log.read_text().splitlines()] if log.exists() else [];done={row['index'] for row in prior};assert len(prior)==len(done) and all(index%4==slot for index in done)
    rows=[tuple(map(int,line.split())) for line in Path('plan_'+tag+'.tsv').read_text().splitlines()];bytes_used=0;covered=0
    for index,start,end in rows[slot::4]:
        if index in done:continue
        if time.monotonic()-latest>=240:
            measure=subprocess.run(['du','-sb',str(HERE)],capture_output=True);assert measure.returncode==0 or (measure.returncode==1 and measure.stderr.splitlines() and all(b'.rows' in line and b'No such file or directory' in line for line in measure.stderr.splitlines()));used=int(measure.stdout.split()[0]);
            with (directory/f'meter{slot}.tsv').open('a') as out:print(stamp(),slot,index,round(cpu(),3),used,covered,file=out,flush=True)
            latest=time.monotonic();print(stamp(),'checkpoint',index,used,covered,flush=True)
            if used>500_000_000:print('staging guard');return
        base=directory/f's{index:05d}';trace=base.with_suffix('.count');raw=base.with_suffix('.rows');before=cpu();begin=time.monotonic();
        cmd=['timeout','200','prlimit','--cpu=150:155','--fsize=12000000','--','./six','2000000','11','576',str(start),str(end),str(trace)]
        with raw.open('xb') as stream:result=subprocess.run(cmd,stdout=stream)
        contents=raw.read_bytes();status='open';totals=[];counts=Counter();
        if result.returncode==0:
            totals=list(map(int,trace.read_text().splitlines()[-1].split()));assert totals[0]==end and totals[1]==2048*(end-start) and totals[2]==sum(totals[3:]);seen=set()
            for line in contents.splitlines():
                fields=line.split();key=int(fields[0]);assert start*2048<=key<end*2048 and key not in seen;seen.add(key);counts[fields[1]]+=1
                if fields[1]==b'model':
                    physical=list(map(int,fields[fields.index(b'graph')+1:]));path=base.with_suffix('.g6');path.write_text(to_graph6(physical)+'\n');run=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',path],capture_output=True,text=True);path.with_suffix('.gate').write_text(run.stdout+run.stderr);assert run.returncode==0 and json.loads(run.stdout)['graphs'][0]['ok'];(ROOT/f'ralph/found/F_six_{key}.g6').write_bytes(path.read_bytes());print('candidate staged for flow',key,flush=True)
            assert [counts[value] for value in (b'one',b'multi',b'model',b'cap')]==totals[4:];status='scanned';covered+=totals[1]-totals[-1]
        packed=gzip.compress(contents,compresslevel=4,mtime=0);base.with_suffix('.rows.gz').write_bytes(packed);assert gzip.decompress(packed)==contents;raw.unlink();bytes_used+=len(packed)
        entry=dict(time=stamp(),index=index,start=start,end=end,status=status,rc=result.returncode,totals=totals,cpu=round(cpu()-before,5),wall=round(time.monotonic()-begin,5),archive=len(packed));
        with log.open('a') as out:print(json.dumps(entry),file=out,flush=True)
    print(stamp(),'done',tag,slot,'covered',covered,'cpu',round(cpu(),3),'archive',bytes_used,flush=True)

if __name__=='__main__':
    if sys.argv[1]=='plan':manifest(sys.argv[2],list(map(int,sys.argv[4:])),int(sys.argv[3]))
    elif sys.argv[1]=='worker':worker(sys.argv[2],int(sys.argv[3]))
