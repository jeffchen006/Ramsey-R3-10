from itertools import combinations
from pathlib import Path
import json,subprocess,sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT/'tools'))
from check_graph import parse_graph6

def run(tag):
    record=json.loads((HERE/(tag+'.patch')).read_text());paid=record['paid'];assert len(paid)==len(set(paid)) and all(0<=vertex<32 for vertex in paid);present={tuple(pair) for pair in record['present']};absent={tuple(pair) for pair in record['absent']};assert not present&absent and all(0<=left<right<32 for left,right in present|absent)
    rows=[[-vertex-1] for vertex in paid];lower,higher=[parse_graph6((HERE/(tag+'.'+name+'.g6')).read_text().strip()) for name in ('low','high')];assert len(lower)==len(higher)==32 and all(not first&~last for first,last in zip(lower,higher));assert all(lower[left]>>right&1 for left,right in present) and all(not higher[left]>>right&1 for left,right in absent)
    for kind,points in record['terms']:
        assert points==sorted(set(points)) and all(0<=point<32 for point in points)
        if kind=='iset':assert len(points)==9 and all(pair in absent for pair in combinations(points,2));rows.append([point+1 for point in points]);continue
        if kind=='edge':assert len(points)==2 and tuple(points) in present
        else:assert kind=='full' and len(points)==1 and sum(points[0] in pair for pair in present)>=9
        rows.append([-point-1 for point in points])
    bound=sum(9-sum(vertex in pair for pair in present) for vertex in paid);assert bound==record['maximum_outside'];data=f'p cnf 32 {len(rows)}\n'+''.join(' '.join(map(str,row))+' 0\n' for row in rows);cnf=HERE/(tag+'.cnf');lrat=HERE/(tag+'.lrat');assert data==cnf.read_text()
    for checker,opts,answer in [('lrat-check',[],'c VERIFIED'),('cake_lpr',['--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32'],'s VERIFIED UNSAT')]:
        result=subprocess.run(['timeout','30','prlimit','--cpu=24:26','--',ROOT/'opt/bin'/checker,*opts,cnf,lrat],text=True,capture_output=True,check=True);assert answer in result.stdout.splitlines()
    for side in ('low','high'):
        result=subprocess.run(['timeout','30','prlimit','--cpu=24:26','--',sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',HERE/(tag+'.'+side+'.g6'),'32','10'],text=True,capture_output=True,check=True);assert json.loads(result.stdout)['graphs'][0]['ok']
    witness=HERE/(tag+'.witness39.g6');
    if witness.exists():
        graph=parse_graph6(witness.read_text().strip());assert len(graph)==39 and all(graph[left]>>right&1 for left,right in present) and all(not graph[left]>>right&1 for left,right in absent);result=subprocess.run(['timeout','30',sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',witness,'39','10'],text=True,capture_output=True,check=True);assert json.loads(result.stdout)['graphs'][0]['ok'] and 32+bound==39
    width=sum((first^last).bit_count() for first,last in zip(lower,higher))//2;print(tag,'fixed edges/nonedges',len(present),len(absent),'partial-card order upper bound',32+bound,'strict labelled cube',width,1<<width,'verified',('sharp at 39' if witness.exists() else ''))
if __name__=='__main__':
    for tag in ('391','128'):run(tag)
