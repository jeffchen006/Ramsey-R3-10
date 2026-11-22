import json,resource,subprocess,sys,time
from collections import Counter
from datetime import datetime
from pathlib import Path
from six_five import sample

def cpu():
    return sum(record.ru_utime+record.ru_stime for record in [resource.getrusage(enum) for enum in (resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN)])
def plan():
    sources=set(map(int,Path('../five.keys').read_text().split()));done={};
    for name in ('fixed','price'):
        for line in Path(name+'.results').read_text().splitlines():
            key,status,*_=line.split();key=int(key);assert done.get(key,status)==status;done[key]=status
    assert set(done)<=sources;fresh=sorted(sources-set(done));assert not Path('manifest.tsv').exists();Path('manifest.tsv').write_text(''.join(f'{idx//64}\t{key}\n' for idx,key in enumerate(fresh)));print('5-cycle physical sources',len(sources),'pilot union',len(done),'fresh',len(fresh),'batches',(len(fresh)+63)//64)
def worker(slot):
    batches={}
    for line in Path('manifest.tsv').read_text().splitlines():
        idx,key=map(int,line.split());batches.setdefault(idx,[]).append(key)
    log=Path(f'job{slot}.jsonl');prior={row['id'] for row in map(json.loads,log.read_text().splitlines())} if log.exists() else set();last=0;keys_done=0
    for index,keys in batches.items():
        if index%4!=slot or index in prior:continue
        stem=f'b{index:04d}';start=cpu();now=time.monotonic()
        if now-last>=225:
            result=subprocess.run(['du','-sb','..'],capture_output=True);assert result.returncode==0 or result.returncode==1 and all(b'No such file or directory' in line for line in result.stderr.splitlines());size=int(result.stdout.split()[0]);last=now
            with open(f'meter{slot}.tsv','a') as stream:print(datetime.now().astimezone().isoformat(timespec='seconds'),slot,index,round(start,4),size,keys_done,file=stream)
            if size>480000000:print('archive guard');return
        try:
            sample(keys,stem);results=[line.split() for line in Path(stem+'.results').read_text().splitlines()];assert [int(row[0]) for row in results]==keys;status='scanned';keys_done+=len(keys)
        except (subprocess.SubprocessError,AssertionError) as error:
            print('open',index,repr(error),flush=True);results=[];status='open'
        with log.open('a') as stream:print(json.dumps(dict(id=index,status=status,count=len(results),cpu=round(cpu()-start,5),wall=round(time.monotonic()-now,5))),file=stream)
    print('finished',slot,'CPU',round(cpu(),3),flush=True)
def audit():
    sources=set(map(int,Path('../five.keys').read_text().split()));jobs={};outcomes={};stages=Counter();cpu_sum=0
    for line in Path('manifest.tsv').read_text().splitlines():
        index,key=map(int,line.split());jobs.setdefault(index,[]).append(key)
    def read(path,expected,duplicates=False):
        rows=[line.split() for line in path.read_text().splitlines()];assert [int(row[0]) for row in rows]==expected
        for row in rows:
            key=int(row[0]);assert key in sources and (key not in outcomes or duplicates and outcomes[key]==row[1]);outcomes[key]=row[1]
            if row[1]=='model':assert json.loads(Path(f'{key}.gate').read_text())['graphs'][0]['ok']
    for stem in ('fixed','price'):read(Path(stem+'.results'),list(map(int,Path(stem+'.keys').read_text().split())),True)
    seen=set()
    for path in Path('.').glob('job*.jsonl'):
        for line in path.read_text().splitlines():
            record=json.loads(line);index=record['id'];assert index not in seen;seen.add(index);cpu_sum+=record['cpu'];stages[record['status']]+=1
            if record['status']=='scanned':read(Path(f'b{index:04d}.results'),jobs[index]);assert len(jobs[index])==record['count']
    missing=sorted(sources-set(outcomes));caps=sorted(key for key,state in outcomes.items() if state in ('cap','maskcap'));models=sorted(key for key,state in outcomes.items() if state=='model');assert set(outcomes.values())<={'model','maskcap','cap','noC5','bipartite','no4'}
    for name,keys in [('missing',missing),('caps',caps),('models',models)]:Path('source_'+name+'.keys').write_text(''.join(f'{key}\n' for key in keys))
    print('source keys',len(sources),'scanned',len(outcomes),'jobs',dict(stages),'outcomes',dict(Counter(outcomes.values())),'missing',len(missing),'cap',len(caps),'cpu-s',round(cpu_sum,2))
if __name__=='__main__':plan() if sys.argv[1]=='plan' else audit() if sys.argv[1]=='audit' else worker(int(sys.argv[1]))
