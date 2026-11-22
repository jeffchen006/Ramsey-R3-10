from itertools import combinations
from pathlib import Path
import json,subprocess,sys
from orbit_extend import ROOT,parse_graph6,to_graph6
from six_branch import graph,decode
from six_five import encode

def execute(lines,tag):
    run=subprocess.run(['timeout','150','prlimit','--cpu=125:130','--','./eight','300000'],input=''.join(lines),text=True,capture_output=True,check=True);Path(tag+'.rows').write_text(run.stdout);print(run.stdout,end='',flush=True)
    for line in run.stdout.splitlines():
        fields=line.split()
        if 'model' not in fields:continue
        adj=list(map(int,fields[fields.index('graph')+1:]));dest=Path(fields[0]+'.g6');dest.write_text(to_graph6(adj)+'\n');target=5 if fields[0]=='induced12' else 10;gate=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',dest,str(len(adj)),str(target)],capture_output=True,text=True,check=True);assert json.loads(gate.stdout)['graphs'][0]['ok'];dest.with_suffix('.gate').write_text(gate.stdout)
        if len(adj)==40:(ROOT/f'ralph/found/F_eight_{fields[0]}.g6').write_bytes(dest.read_bytes())
    return run.stdout
def control():
    known=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());size=31;mask=(1<<size)-1;contacts=[row&mask for row in known[size:]];rows=execute([encode('known39',[row&mask for row in known[:size]],10,False,contacts)],'known');assert 'model' in rows
    small=parse_graph6(Path('../sixplant12.g6').read_text().strip());core=[row%16|1<<(vertex^1) for vertex,row in enumerate(small[:4])];assert any(row%4==3 for row in small[4:]);rows=execute([encode('induced12',core,5,True),encode('neg',[6,9,9,6],4,True)],'plant');first,second=rows.splitlines();assert 'model' in first and second.count('empty')==2
    gener=subprocess.run([ROOT/'opt/bin/geng','-q','-t','8'],capture_output=True,text=True,check=True);types=[0,0,0,0]
    for text in gener.stdout.splitlines():
        adj=parse_graph6(text);four=any(all(not adj[left]>>right&1 for left,right in combinations(group,2)) for group in combinations(range(8),4));cyclic=any(all(sum(adj[src]>>dest&1 for dest in group)==2 for src in group) for group in combinations(range(8),5));types[int(four)+2*int(cyclic)]+=1
    assert types[0]==0;print('geng 8 trianglefree: neither, I4 only, C5 only, both',types,flush=True)
def pilot():
    data=[]
    for key in [33854418671,6206451439,33855303407,34327197559]:
        old=graph(decode(key));data.append(encode(str(key),[row% (1<<32) for row in old[:32]],10,True))
    execute(data,'four')
if __name__=='__main__':control() if sys.argv[1]=='control' else pilot()
