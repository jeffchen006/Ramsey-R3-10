from itertools import combinations
from pathlib import Path
import json,sys,subprocess
from six_branch import graph,decode,encode,EDGES
from orbit_extend import ROOT,parse_graph6,to_graph6

def verify():
    cap=set(Path('four/source_caps.keys').read_text().split());rows=Path('four/nine.rows').read_text().splitlines();assert {row.split()[0] for row in rows}==cap and len(rows)==len(cap)==9
    assert all(len(row.split())==4 and all(item.startswith('empty:') and int(item.split(':')[1])<100000000 for item in row.split()[1:]) for row in rows)
    source=ROOT/'scratch/F/r22/ext/6064_0-p1.g6';physical=parse_graph6(source.read_text().strip());assert len(physical)==37;switch=[None]*17;switch[0]=0;rows=Path('columns.tsv').read_text().splitlines()
    for line in rows:
        left,right,expr=map(int,line.split());
        if expr!=0:continue
        same=(physical[2*left]>>(2*right))&1
        if switch[left] is None:switch[left]=switch[right]^same
        else:switch[right]=switch[left]^same
    sites=[vertex^switch[vertex//2] if vertex<34 else vertex for vertex in range(37)];relabeled=[sum(1<<index for index,dest in enumerate(sites) if physical[src]>>dest&1) for src in sites];word=sum(1<<index for index,(left,right) in enumerate(EDGES) if relabeled[2*left]>>(2*right)&1);key=encode(word);assert decode(key)==word;old=graph(word)
    for left,right in combinations(range(34),2):
        if (left^1)!=right:assert bool(relabeled[left]>>right&1)==bool(old[left]>>right&1)
    dest=Path('sharp37.g6');dest.write_text(to_graph6(relabeled)+'\n');check=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',dest,'37','10'],capture_output=True,text=True,check=True);assert json.loads(check.stdout)['graphs'][0]['ok'];dest.with_suffix('.gate').write_text(check.stdout);print('exact tail set',len(cap),'all three four-vertex shapes exhaust. Rebound saturated-crossing chart and gated order37 witness, key',key,flush=True)
if __name__=='__main__':verify()
