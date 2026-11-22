from pathlib import Path
from itertools import combinations
import sys,subprocess
from orbit_extend import ROOT,parse_graph6,to_graph6,independent_sets
from cards24 import gate
from six_five import encode

def main():
    for name,path,target,expected in [('known39',ROOT/'ralph/lanes/F/round1_seed39.g6',10,0),('near40',ROOT/'ralph/lanes/F/round4_seed40_24.g6',10,24),('plant12',ROOT/'scratch/F/r23/sixplant12.g6',4,27)]:
        graph=parse_graph6(path.read_text().strip());value=sum(1 for witness in independent_sets(graph,(1<<len(graph))-1,target));assert value==expected;print('control',name,value,flush=True)
    known=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());low=(1<<31)-1;source=encode('restore39',[row&low for row in known[:31]],10,False,sorted({row&low for row in known[31:]}));restored=subprocess.run(['timeout','25','prlimit','--cpu=20','--',ROOT/'scratch/F/r24/near/score','200000','390008'],input=source,text=True,capture_output=True,check=True);row=[line.split() for line in restored.stdout.splitlines() if ' best ' in line and ' graph ' in line][-1];assert row[3]=='0';gate(list(map(int,row[6:])),10,Path('calibration39.g6'));print('withheld eight unordered contact masks, reconstructed 39 (no exterior edges given), draw',row[2],flush=True)
    keys=[33854418671,6206451439,34327197559];inputs=''.join((ROOT/f'scratch/F/r23/split/{key}.input').read_text() for key in keys);budget=int(sys.argv[1]);seed=int(sys.argv[2]);path=Path(f'{seed}.rows');assert not path.exists()
    with path.open('x') as out:proc=subprocess.run(['timeout','180','prlimit','--cpu=165:168','--',ROOT/'scratch/F/r24/near/score',str(budget),str(seed)],input=inputs,text=True,stdout=out);assert proc.returncode==0
    for key in keys:
        rows=[line.split() for line in path.read_text().splitlines() if line.startswith(str(key)+' ')];assert rows[-1][1]=='trials';print(*rows[-1],flush=True)
        if not rows[:-1]:continue
        last=rows[-2];score=int(last[3]);edges=int(last[4]);adj=list(map(int,last[6:]));assert len(adj)==40 and all(6<=row.bit_count()<=9 for row in adj) and sum(row.bit_count() for row in adj)==2*edges>=322;assert all(bool(adj[i]>>j&1)==bool(adj[j]>>i&1) and not (adj[i]>>j&1 and adj[i]&adj[j]) for i,j in combinations(range(40),2));exact=sum(1 for _ in independent_sets(adj,(1<<40)-1,10));assert score==exact;graph=Path(f'{seed}_{key}.g6');graph.write_text(to_graph6(adj)+'\n');print('recount',key,score,edges,flush=True)
        if score==0:gate(adj,10,graph)
if __name__=='__main__':main()
