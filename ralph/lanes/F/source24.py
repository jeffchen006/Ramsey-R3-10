from pathlib import Path
from itertools import combinations
from collections import Counter
from random import Random
import json,os,subprocess,sys,resource,time
from front24 import BASE,ROOT,OLD,REGIONS,get,encode,outcome,readkeys
from eight_chart import roots
from cards24 import gate,subgraph
from orbit_extend import parse_graph6,independent_sets

DIR=BASE/'shape';R23=ROOT/'scratch/F/r23'
def cycle(size):return [1<<((idx-1)%size)|1<<((idx+1)%size) for idx in range(size)]
def shapes():
    bare=subprocess.run(['timeout','15',ROOT/'opt/bin/geng','-q','-t','6'],capture_output=True,text=True,check=True).stdout.splitlines();out={700:cycle(7)}
    for idx,entry in enumerate(bare):
        adj=parse_graph6(entry)
        if next(independent_sets(adj,63,4),None) is not None:continue
        if any(all(row.bit_count()==2 for row in subgraph(adj,group)) for group in combinations(range(6),5)):continue
        order=[]
        while len(order)<6:order.append(max(set(range(6))-set(order),key=lambda vertex:((adj[vertex]&sum(1<<old for old in order)).bit_count(),adj[vertex].bit_count(),-vertex)))
        out[600+idx]=subgraph(adj,order)
    return out
def solve(tag,adj,target,paired,masks,tests,limit,secs):
    shapes_data=' '.join(map(str,[len(tests),*(value for name,graph in tests for value in (name,len(graph),*graph))]));source=encode(tag,adj,target,paired,masks)+shapes_data+'\n';path=Path(tag+'.rows');assert not path.exists();start=resource.getrusage(resource.RUSAGE_CHILDREN);before=time.monotonic()
    with path.open('x') as output:proc=subprocess.run(['timeout',str(secs),'prlimit',f'--cpu={secs-4}','--',os.getenv('F_SOURCE24_BIN',str(DIR/'shape')),str(limit)],input=source,text=True,stdout=output)
    rows=[line.split() for line in path.read_text().splitlines()];assert [int(row[1]) for row in rows]==[idx for idx,graph in tests][:len(rows)] and all(row[0]==tag for row in rows);counts=Counter(row[2] for row in rows)
    for row in rows:
        if row[2]!='model':continue
        graph=list(map(int,row[6:]));shape=dict(tests)[int(row[1])];order=len(adj);assert [value>>order for value in graph[order:]]==shape;gate(graph,target,Path(f'{tag}_{row[1]}.g6'))
    end=resource.getrusage(resource.RUSAGE_CHILDREN);return dict(tag=tag,rc=proc.returncode,states=counts,missing=len(tests)-len(rows),cpu=round(end.ru_utime+end.ru_stime-start.ru_utime-start.ru_stime,5),wall=round(time.monotonic()-before,5))
def control():
    known=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());small=parse_graph6((R23/'sixplant12.g6').read_text().strip())
    def find(path):
        if len(path)==7:return path if subgraph(known,path)==cycle(7) else None
        for next_vertex in range(len(known)):
            if next_vertex in path or (path and not known[path[-1]]>>next_vertex&1) or any(known[old]>>next_vertex&1 for old in (path[1:-1] if len(path)==6 else path[:-1])):continue
            found=find(path+[next_vertex]);
            if found:return found
    outer=find([0]);assert outer;base=sorted(set(range(39))-set(outer));controls=[('C7_39',subgraph(known,base),10,False,[sum(1<<idx for idx,old in enumerate(base) if known[old]>>vertex&1) for vertex in outer],[(700,cycle(7))],'model'),('C7_7',[],4,False,[0],[(700,cycle(7))],'model'),('C7_neg',[],3,False,[0],[(700,cycle(7))],'empty')]
    for name,adj,target,paired,masks,patterns,expected in controls:
        result=solve(name,adj,target,paired,masks,patterns,1000000,35);assert result['states'][expected]==1;print(json.dumps(result),flush=True)
    seq=[0,1,2,3];outer=list(range(4,10));core=[row|1<<(idx^1) for idx,row in enumerate(subgraph(small,seq))];sample=solve('free_vertical10',core,5,True,None,[(1,subgraph(small,outer))],1000000,35);assert sample['states']['model']==1;print(json.dumps(sample))
def inputs(which):
    fixed=roots();oldfixed=(33854418671,6206451439,34327197559);conv=dict(zip(oldfixed,fixed));summaries={};bare=0;total=0
    def finish(row,tail):
        key=int(row[0]);i4=list(map(int,row[5:13]));pent=list(map(int,row[16:24]));assert row[2]=='I4' and row[13:15]==['C5','empty'];
        if row[3]=='cap':
            parts=[values.split() for line in tail for values in line.splitlines() if values.startswith(str(key)+' ')];parts.sort(key=lambda part:int(part[1]));limit=int(row[1]);assert [(int(part[1]),int(part[2]),part[3]) for part in parts]==[(lower,min(lower+16,limit),'empty') for lower in range(0,limit,16)];i4=[sum(int(part[6+depth]) for part in parts) for depth in range(8)]
        else:assert row[3]=='empty'
        return i4,pent
    sources=[(OLD,('pilot','wave0','wave1','wave2','wave3'))];
    if which=='all':sources += [(R23/'chart',('pilot','slot0','slot1','slot2','slot3'))]+[(BASE/f'slot{slot}',('w0','w1','w2')) for slot in range(4)]
    oldtails={path.stem:path for path in BASE.glob('slot*/*.rows') if path.stem.isdigit()}
    for folder,tags in sources:
        for tag in tags:
            for line in (folder/(tag+'.jsonl')).open():
                item=json.loads(line);assert item['status']=='complete' and item['rc']==0;total+=len(item['keys']);
                for row in item['rows']:
                    if row[1]=='bare':bare+=1;continue
                    path=(R23/'chart_tail'/(row[0]+'.rows')) if folder.name=='chart' else oldtails.get(row[0]);i4,pent=finish(row,[path.read_text()] if row[3]=='cap' else []);key=int(row[0]);assert key not in summaries;summaries[key]=(i4,pent)
    if which=='all':
        raw=[path.read_text() for path in [R23/'split/pilot.rows',*sorted((R23/'split').glob('slot*.rows'))]]
        for row in (line.split() for line in (R23/'wild/four.rows').read_text().splitlines()):
            key=int(row[0]);
            if key not in conv:continue
            i4,pent=finish(row,raw);assert conv[key] not in summaries;summaries[conv[key]]=(i4,pent);total+=1
    assert len(summaries)+bare==total==(786432 if which=='all' else 193658);return summaries,bare,total
def plan(which):
    summaries,bare,total=inputs(which);inventory=shapes();(DIR/'patterns.json').write_text(json.dumps(inventory));rows=[];reached=Counter();five=[];six=[];already=set()
    if which=='all':already={int(line.split()[0]) for line in (DIR/'pilot.tsv').read_text().splitlines()}
    for key,(i4,pent) in sorted(summaries.items()):
        reached['I4_7']+=int(bool(i4[6]));reached['C5_7']+=int(bool(pent[6]));reached['I4_6']+=int(bool(i4[5]));reached['C5_6']+=int(bool(pent[5]));
        if i4[4] or pent[4]:five.append(key)
        if i4[5] or pent[5]:six.append(key)
        requests=[]
        if i4[2] and pent[3]:requests.append(700)
        if i4[2]:requests.extend(name for name in inventory if name!=700)
        if requests:rows.append((key,*requests))
    if which=='pilot':
        random=Random(2467);strong=[row for row in rows if 700 in row];weak=[row for row in rows if 700 not in row];rows=sorted(random.sample(strong,min(len(strong),8))+random.sample(weak,min(len(weak),12)))
    else:rows=[row for row in rows if row[0] not in already];(DIR/'reach6.keys').write_text(''.join(f'{key}\n' for key in six));(DIR/'reach5.keys').write_text(''.join(f'{key}\n' for key in five))
    (DIR/(which+'.tsv')).write_text(''.join(' '.join(map(str,row))+'\n' for row in rows));print(which,'denominator',total,'bare',bare,'physical',len(summaries),'depths',reached,'reached five',len(five),'6-shapes',len(inventory)-1,'assigned rows',len(rows),'C7',sum(700 in row[1:] for row in rows),'6-shape signs',sum(any(value!=700 for value in row[1:]) for row in rows),'previous rows',len(already))
def run(manifest,cap):
    patterns={int(name):adj for name,adj in json.loads((DIR/'patterns.json').read_text()).items()};
    for line in manifest.read_text().splitlines():
        key,*ids=map(int,line.split());result=solve(str(key),get(key),10,True,None,[(idx,patterns[idx]) for idx in ids],cap,70);print(json.dumps(result),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    elif sys.argv[1]=='plan':plan(sys.argv[2])
    else:run(Path(sys.argv[2]),int(sys.argv[3]))
