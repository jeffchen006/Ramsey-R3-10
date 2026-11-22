from pathlib import Path
from itertools import combinations
import json,os,resource,subprocess,sys,time
from datetime import datetime
from orbit_extend import ROOT,parse_graph6,to_graph6
from six_branch import decode,graph
from six_five import encode

KEYS=(33854418671,6206451439,34327197559)
def prepare():
    whole=[];pilot=[];fresh=[]
    for key in KEYS:
        masks=list(map(int,Path(f'old32_{key}.masks').read_text().split()));assert masks==sorted(set(masks));adj=[row%(1<<32) for row in graph(decode(key))[:32]];Path(f'{key}.input').write_text(encode(str(key),adj,10,True,masks));intervals=[(key,lower,min(lower+16,len(masks))) for lower in range(0,len(masks),16)];whole+=intervals;pick={0,len(intervals)//2,len(intervals)-1};pilot.extend(row for index,row in enumerate(intervals) if index in pick);fresh.extend(row for index,row in enumerate(intervals) if index not in pick)
    def save(name,rows):Path(name).write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
    save('whole.tsv',whole);save('pilot.tsv',pilot)
    for slot in range(4):save(f'slot{slot}.tsv',fresh[slot::4]);
    small=parse_graph6(Path('../sixplant12.g6').read_text().strip());adj=[row%16|1<<(vertex^1) for vertex,row in enumerate(small[:4])];Path('control.input').write_text(encode('induced12',adj,5,True)+encode('negative',[6,9,9,6],4,True));save('control.tsv',[(tag,start,start+1) for tag in ('induced12','negative') for start in range(9)]);print('disjoint minimum-first-mask slices',len(whole),'first masks',sum(end-start for _,start,end in whole),'pilot',len(pilot),'fresh',len(fresh))
def run(tag):
    selected=[tuple(line.split()) for line in Path(tag+'.tsv').read_text().splitlines()];keys=sorted(set(row[0] for row in selected));input_data=Path('control.input').read_text() if tag=='control' else ''.join(Path(key+'.input').read_text() for key in keys);expected={(key,int(start),int(end)) for key,start,end in selected};src=Path(tag+'.rows');assert not src.exists();env={**os.environ,'F_PAIR_EXACT':'1'}
    args=['timeout','5100','prlimit','--cpu=4900:4950','--','./eight','2000000',tag+'.tsv'] if tag.startswith('slot') else ['./eight','2000000',tag+'.tsv'];before=time.monotonic();feed=Path(tag+'.feed');feed.write_text(input_data)
    with feed.open() as stream:proc=subprocess.Popen(args,stdin=stream,stdout=subprocess.PIPE,text=True,env=env)
    feed.unlink();states=[];previous=0
    with src.open('x') as out:
        for line in proc.stdout:
            row=line.split();key,start,end=row[:3];expected.remove((key,int(start),int(end)));state=row[3];assert state in ('model','empty','cap');states.append(state);out.write(line);out.flush()
            if time.monotonic()-previous>210:
                with open(tag+'.meter','a') as meter:print(datetime.now().astimezone().isoformat(timespec='seconds'),proc.pid,len(states),len(expected),src.stat().st_size,file=meter)
                previous=time.monotonic()
            if state=='model':
                adj=list(map(int,row[row.index('graph')+1:]));path=Path(f'model_{key}_{start}.g6');path.write_text(to_graph6(adj)+'\n');target=5 if key=='induced12' else 10;checked=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',path,str(len(adj)),str(target)],capture_output=True,text=True,check=True);assert json.loads(checked.stdout)['graphs'][0]['ok'];path.with_suffix('.gate').write_text(checked.stdout)
                if len(adj)==40:(ROOT/f'ralph/found/F_split_{key}_{start}.g6').write_bytes(path.read_bytes())
    assert proc.wait()==0 and not expected
    if tag=='control':assert states.count('model') and all(row.split()[3]=='empty' for row in src.read_text().splitlines() if row.startswith('negative '))
    print(tag,'intervals',len(states),{state:states.count(state) for state in set(states)},'wall',round(time.monotonic()-before,3),flush=True)
if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else run(sys.argv[1])
