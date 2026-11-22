from pathlib import Path
from collections import Counter
from itertools import combinations
from random import Random
from datetime import datetime
import json,os,resource,subprocess,sys,time
from orbit_extend import ROOT,parse_graph6,to_graph6,independent_sets
from front24 import BASE

DIR=BASE/'fixed';LANE=ROOT/'ralph/lanes/F'
def subgraph(adj,vertices):return [sum(1<<idx for idx,right in enumerate(vertices) if adj[left]>>right&1) for left in vertices]
def gate(adj,target,path):
    path.write_text(to_graph6(adj)+'\n');test=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',path,str(len(adj)),str(target)],capture_output=True,text=True,check=True);assert json.loads(test.stdout)['graphs'][0]['ok'];path.with_suffix('.gate').write_text(test.stdout)
    if len(adj)==40 and target==10:(ROOT/f'ralph/found/F_cards24_{path.stem}.g6').write_bytes(path.read_bytes())
def run(tag,adj,target,shapes,limit,wall=65):
    assert all(len(shape)==8 for idx,shape in shapes);source=' '.join(map(str,[tag,len(adj),target,8,len(shapes),*adj]))+'\n'+''.join(' '.join(map(str,[idx,*shape]))+'\n' for idx,shape in shapes);before=resource.getrusage(resource.RUSAGE_CHILDREN);path=Path(tag+'.rows');assert not path.exists();real=time.monotonic()
    with path.open('x') as out:proc=subprocess.run(['timeout',str(wall),'prlimit','--cpu='+str(wall-5),'--',os.getenv('F_CARDS24_BIN',str(DIR/'fixed')),str(limit)],input=source,stdout=out,text=True)
    after=resource.getrusage(resource.RUSAGE_CHILDREN);rows=[line.split() for line in path.read_text().splitlines()];states=Counter();ids=set();assert all(row[0]==tag for row in rows);mask_count=int(rows[0][2]) if rows else -1;stage=rows[0][3] if rows else 'stage';wanted={idx for idx,shape in shapes}
    for row in rows[1:]:
        idx=int(row[1]);assert idx in wanted and idx not in ids;ids.add(idx);states[row[2]]+=1
        if row[2]=='model':
            physical=list(map(int,row[5:]));assert len(physical)==len(adj)+8 and [entry%(1<<len(adj)) for entry in physical[:len(adj)]]==adj and [entry>>len(adj) for entry in physical[len(adj):]]==dict(shapes)[idx];gate(physical,target,Path(f'{tag}_{idx}.g6'))
    record=dict(tag=tag,core=to_graph6(adj),rc=proc.returncode,masks=mask_count,stage=stage,states=states,missing=len(wanted-ids),cpu=round(after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,5),wall=round(time.monotonic()-real,5));print(json.dumps(record),flush=True);return record
def control():
    small=parse_graph6((ROOT/'scratch/F/r23/sixplant12.g6').read_text().strip());known=parse_graph6((LANE/'round1_seed39.g6').read_text().strip());
    for name,adj,target in [('small',small,5),('known39',known,10)]:
        size=len(adj)-8;state=run(name,subgraph(adj,range(size)),target,[(0,subgraph(adj,range(size,len(adj))))],4000000);assert state['states'].get('model')==1
    neg=run('neg',subgraph(small,range(4)),4,[(0,subgraph(small,range(4,12)))],2000000);assert neg['states'].get('empty')==1
def inventory():
    run=subprocess.run(['timeout','20',ROOT/'opt/bin/geng','-q','-t','8'],check=True,capture_output=True,text=True);shapes=run.stdout.splitlines();assert len(shapes)==410;(DIR/'shapes.g6').write_text(run.stdout);rng=Random(240039);seeds=[('fresh39',parse_graph6((LANE/'round1_seed39.g6').read_text().strip())),('exoo39',parse_graph6((ROOT/'scratch/F/r2/exoo39.canon.g6').read_text().strip())),('near178',parse_graph6((LANE/'round4_seed40_24.g6').read_text().strip())),('near179',parse_graph6((LANE/'round4_seed40_24_e179.g6').read_text().strip()))];cards=[]
    for name,adj in seeds:
        excludes=list(independent_sets(adj,(1<<len(adj))-1,10));seen=set();
        while len(seen)<128:
            omitted=tuple(sorted(rng.sample(range(len(adj)),len(adj)-32)));mask=sum(1<<point for point in omitted)
            if omitted in seen or any(not witness&mask for witness in excludes):continue
            seen.add(omitted);core=subgraph(adj,[vertex for vertex in range(len(adj)) if vertex not in omitted]);cards.append((name,omitted,to_graph6(core)))
    canonical=subprocess.run(['timeout','20',ROOT/'opt/bin/labelg','-q'],input=''.join(core+'\n' for name,om,core in cards),text=True,capture_output=True,check=True).stdout.splitlines();assert len(canonical)==len(cards) and len(set(canonical))==len(cards);(DIR/'cards.json').write_text(json.dumps([dict(tag=f'{name}_{idx}',omit=om,core=core,canon=can) for idx,((name,om,core),can) in enumerate(zip(cards,canonical))]));print('distinct fixed decks',len(cards),'external unlabeled shapes',len(shapes),'cards times shapes',len(cards)*len(shapes))
def wave(manifest,limit,wall):
    cards=json.loads((DIR/'cards.json').read_text());shapes=[parse_graph6(g) for g in (DIR/'shapes.g6').read_text().splitlines()]
    for line in manifest.read_text().splitlines():
        idx,first,last=map(int,line.split());card=cards[idx];run(f"{card['tag']}_{first}_{last}",parse_graph6(card['core']),10,list(enumerate(shapes))[first:last],limit,wall)
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    elif sys.argv[1]=='inventory':inventory()
    else:wave(Path(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
