from collections import Counter
from pathlib import Path
from random import Random
import json,sys,subprocess,time
from cards24 import DIR,ROOT,subgraph,gate
from pattern_repair24 import work
from orbit_extend import parse_graph6,to_graph6

STORE=DIR.parent/'transfer'
def canonical(graphs):
    encoded=[to_graph6(graph) for graph in graphs];rows=subprocess.run(['timeout','30',ROOT/'opt/bin/labelg','-q'],input=''.join(value+'\n' for value in encoded),text=True,capture_output=True,check=True).stdout.splitlines();assert len(rows)==len(encoded);return rows
def control():
    parent=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());record=work('hold7',subgraph(parent,range(32)),10,False,[(0,subgraph(parent,range(32,39)))],1000000);assert record['states'].get('model')==1;print(json.dumps(record),flush=True)
def source(indices):
    cards=json.loads((DIR/'cards.json').read_text());shapes=[parse_graph6(row) for row in subprocess.run(['timeout','20',ROOT/'opt/bin/geng','-q','-t','7'],capture_output=True,text=True,check=True).stdout.splitlines()];assert len(shapes)==107
    for idx in indices:
        parent=cards[idx];adj=parse_graph6(parent['core']);
        for first in range(0,107,16):
            record=work(f'source{idx}_{first}',adj,10,False,list(enumerate(shapes))[first:first+16],100000);print(json.dumps(record),flush=True)
def promote():
    cards=json.loads((DIR/'cards.json').read_text());seen_cores={value['canon'] for value in cards};prior=set((ROOT/'scratch/F/r2/closure39fresh/all.labelg.g6').read_text().splitlines());prior.update(canonical([parse_graph6(path.read_text().strip()) for path in (ROOT/'ralph/lanes/F/round1_seed39.g6',ROOT/'scratch/F/r2/exoo39.canon.g6')]));seen_sources=set();jobs=[];sources=[]
    for task in sorted(STORE.glob('src*')):
        if not task.is_dir():continue
        paths=sorted(task.glob('source*.g6'));physical=[parse_graph6(path.read_text().strip()) for path in paths];canonical_list=canonical(physical)
        for path,adj,normalized in zip(paths,physical,canonical_list):
            assert len(adj)==39 and path.with_suffix('.gate').is_file();
            if normalized in seen_sources:continue
            seen_sources.add(normalized);sources.append((str(path.relative_to(STORE)),normalized,normalized in prior));rng=Random('F24:'+normalized);deleted=rng.sample(range(32),7);keep=[vertex for vertex in range(39) if vertex not in deleted];target=subgraph(adj,keep);can=canonical([target])[0];
            if can in seen_cores:continue
            seen_cores.add(can);jobs.append(dict(source=str(path.relative_to(STORE)),source_canon=normalized,seen_in_local_prior=normalized in prior,remove=sorted(deleted),core=to_graph6(target),canon=can))
    jobs.sort(key=lambda entry:(entry['seen_in_local_prior'],entry['source']));(STORE/'promoted.json').write_text(json.dumps(jobs));(STORE/'sources.json').write_text(json.dumps(sources));print('distinct gated 39 sources',len(sources),'not in finite prior of',len(prior),sum(not entry[2] for entry in sources),'new canonical order32 decks',len(jobs),'all seven exterior vertices retained; no Exoo-component inference')
def target(first,last,subset):
    jobs=json.loads((STORE/'promoted.json').read_text());shapes=[parse_graph6(row) for row in (DIR/'shapes.g6').read_text().splitlines()];
    for idx in range(first,min(last,len(jobs))):
        core=parse_graph6(jobs[idx]['core']);names=list(range(410));pilot={0,1,7,23,53,103,153,203,253,303,353,403};names=[name for name in names if subset=='all' or ((name in pilot)==(subset=='pilot'))];
        for offset in range(0,len(names),16):
            portion=names[offset:offset+16];record=work(f'target{idx}_{subset}_{offset}',core,10,False,[(name,shapes[name]) for name in portion],200000);print(json.dumps(record),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    elif sys.argv[1]=='source':source(list(map(int,sys.argv[2:])))
    elif sys.argv[1]=='promote':promote()
    else:target(int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
