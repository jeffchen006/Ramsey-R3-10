from itertools import combinations
from pathlib import Path
import json,subprocess,sys
from orbit_extend import ROOT,parse_graph6,to_graph6,independent_sets
from six_branch import decode,graph

def command(mode,args,adj,target,extra=''):
    return subprocess.run(['timeout','90','prlimit','--cpu=80:82','--','./near',mode,*args],input=' '.join(map(str,[len(adj),target,*adj]))+'\n'+extra,capture_output=True,text=True,check=True).stdout
def run():
    known=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());plant=parse_graph6(Path('../sixplant12.g6').read_text().strip());
    for name,adj,target in [('known39',known,10),('plant12',plant,5),('plant12/fours',plant,4)]:
        exact=sum(1 for _ in independent_sets(adj,(1<<len(adj))-1,target));assert int(command('count',[],adj,target))==exact;print('control',name,exact,flush=True)
    for entry in ('33854418671','6206451439','33855303407','34327197559'):
        adj=graph(decode(int(entry)));masks=Path('../receipts/'+entry+'.masks').read_text();report=command('score',['40000',entry[-8:]],adj,10,masks);Path(entry+'.log').write_text(report);print(entry,report.splitlines()[-1],flush=True)
        improvements=[line.split() for line in report.splitlines() if line.startswith('best ')];
        if not improvements:continue
        last=improvements[-1];score=int(last[2]);edges=int(last[3]);physical=list(map(int,last[5:]));assert len(physical)==40 and all(6<=row.bit_count()<=9 for row in physical) and sum(row.bit_count() for row in physical)==2*edges>=322
        assert not any(physical[left]&physical[right] for left,right in combinations(range(40),2) if physical[left]>>right&1);assert all((physical[left]>>right&1)==(physical[right]>>left&1) for left,right in combinations(range(40),2));assert not any(row>>vertex&1 for vertex,row in enumerate(physical));assert sum(1 for _ in independent_sets(physical,(1<<40)-1,10))==score
        dest=Path(entry+'.g6');dest.write_text(to_graph6(physical)+'\n');assert parse_graph6(dest.read_text().strip())==physical
        if not score:
            checked=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',dest],capture_output=True,text=True,check=True);assert json.loads(checked.stdout)['graphs'][0]['ok'];(ROOT/f'ralph/found/F_six_near_{entry}.g6').write_bytes(dest.read_bytes())
        print(entry,'independent recount',score,'edges',edges,flush=True)
if __name__=='__main__':run()
