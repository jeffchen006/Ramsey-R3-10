from itertools import combinations
from pathlib import Path
import subprocess,sys
from orbit_extend import ROOT,parse_graph6,to_graph6
from six_five import encode,check
from six_branch import graph,decode

def execute(source,tag):
    run=subprocess.run(['timeout','160','prlimit','--cpu=140:143','--','./four','2000000'],input=''.join(source),capture_output=True,text=True,check=True);Path(tag+'.rows').write_text(run.stdout);print(run.stdout,flush=True)
    for line in run.stdout.splitlines():
        row=line.split();
        if 'model' in row:check(row,10)
    return run.stdout
def control():
    adj=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip())[:38];group=next(group for group in combinations(range(38),4) if all(1<=sum(adj[left]>>right&1 for right in group)<=2 for left in group) and sum(sum(adj[left]>>right&1 for right in group) for left in group)==6);order=[vertex for vertex in range(38) if vertex not in group]+list(group);full=[sum(1<<idx for idx,dest in enumerate(order) if adj[src]>>dest&1) for src in order];mask=(1<<34)-1
    assert 'model' in execute([encode('known38',[row&mask for row in full[:34]],10,False,[row&mask for row in full[34:]])],'positive');neg=execute([encode('negative',[2,1],3,True)],'negative');assert neg.count('empty')==3
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else:execute([encode(key,graph(decode(int(key))),10,True) for key in Path(sys.argv[1]).read_text().split()],sys.argv[2])
