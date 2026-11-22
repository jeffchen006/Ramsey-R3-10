from itertools import combinations,permutations
from pathlib import Path
import subprocess,sys,json,resource,collections,time
from orbit_extend import ROOT,to_graph6,parse_graph6
from six_branch import decode,graph

def cycle(adj):
    def extend(seq):
        if len(seq)==5:
            return seq if all(bool(adj[seq[left]]>>seq[right]&1)==((right-left)%5 in (1,4)) for left,right in combinations(range(5),2)) else None
        for nxt in range(len(adj)):
            if nxt not in seq and (not seq or adj[seq[-1]]>>nxt&1):
                found=extend(seq+[nxt]);
                if found:return found
    selected=extend([]);assert selected;return selected
def encode(tag,adj,target,paired,masks=None):return ' '.join(map(str,[tag,len(adj),target,int(paired),-1 if masks is None else len(masks),*adj,*(masks or [])]))+'\n'
def execute(data,stem):
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();run=subprocess.run(['timeout','160','prlimit','--cpu=150:152','--','./five','2000000'],input=data,text=True,capture_output=True,check=True);Path(stem+'.results').write_text(run.stdout);after=resource.getrusage(resource.RUSAGE_CHILDREN);stats=collections.Counter(line.split()[1] for line in run.stdout.splitlines());print(stem,len(run.stdout.splitlines()),dict(stats),'child_cpu',round((after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime),4),'wall',round(time.monotonic()-start,4),flush=True);return [line.split() for line in run.stdout.splitlines()]
def check(row,target):
    adj=list(map(int,row[row.index('graph')+1:]));dest=Path(row[0]+'.g6');dest.write_text(to_graph6(adj)+'\n');run=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',dest,str(len(adj)),str(target)],capture_output=True,text=True,check=True);assert json.loads(run.stdout)['graphs'][0]['ok'];dest.with_suffix('.gate').write_text(run.stdout)
def control():
    for tag,adj,target in [('seed39',parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip()),10),('small12',parse_graph6(Path('../sixplant12.g6').read_text().strip()),5)]:
        outer=cycle(adj);order=[vertex for vertex in range(len(adj)) if vertex not in outer]+outer;size=len(order)-5;relabeled=[sum(1<<idx for idx,dest in enumerate(order) if adj[src]>>dest&1) for src in order];base=[row% (1<<size) for row in relabeled[:size]];contacts=[row%(1<<size) for row in relabeled[size:]];row=execute(encode(tag,base,target,False,contacts),tag)[0];assert row[1]=='model';check(row,target)
    fixture=[6,9,9,6];single=execute(encode('negative',fixture,4,True), 'negative')[0];assert single[1] in ('noC5','bipartite');print('small unmatched 4+5 target=4 negative and known C5 addbacks pass',flush=True)
def sample(keys,tag):
    rows=execute(''.join(encode(str(key),graph(decode(key)),10,True) for key in keys),tag)
    for row in rows:
        if row[1]=='model':check(row,10)
if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else:sample([int(key) for key in Path(sys.argv[1]).read_text().split()],sys.argv[2])
