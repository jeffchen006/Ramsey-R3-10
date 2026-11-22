from itertools import combinations
import os,subprocess
from cards24 import DIR

def physical(adj,chosen):return all(not adj[left]>>right&1 for left,right in combinations(chosen,2))
def main():
    requests=[];expect={};draws=0
    for old_edge in (False,True):
        for code in range(64):
            outer=[0]*4;edges=list(combinations(range(4),2))
            for idx,(left,right) in enumerate(edges):
                if code>>idx&1:outer[left]|=1<<right;outer[right]|=1<<left
            if any(outer[left]>>right&1 and outer[left]&outer[right] for left,right in edges):continue
            viable=set()
            for crossing in range(256):
                adj=[2,1] if old_edge else [0,0];adj.extend(row<<2 for row in outer)
                for left in range(2):
                    for slot in range(4):
                        if crossing>>(4*left+slot)&1:adj[left]|=1<<(slot+2);adj[slot+2]|=1<<left
                if any(adj[left]>>right&1 and adj[left]&adj[right] for left,right in combinations(range(6),2)):continue
                draws+=1
                for target in (3,4,5):
                    if not any(physical(adj,group) for group in combinations(range(6),target)):viable.add(target)
            for target in (3,4,5):
                tag=f'{int(old_edge)}_{code}_{target}';expect[tag]='model' if target in viable else 'empty';requests.append(' '.join(map(str,[tag,2,target,4,1,2 if old_edge else 0,1 if old_edge else 0,0,*outer])))
    run=subprocess.run(['timeout','40','prlimit','--cpu=32','--',os.getenv('F_CARDS24_BIN',str(DIR/'fixed')),'1000000'],input='\n'.join(requests)+'\n',text=True,capture_output=True,check=True);obtained={}
    for line in run.stdout.splitlines():
        row=line.split();
        if row[1]!='masks':assert row[0] not in obtained;obtained[row[0]]=row[2]
    assert obtained==expect;print('fixed-rectangle brute calibrator',len(expect),'cases across all 2+4 crossings;',draws,'triangle-free physical inputs (before target split);',list(expect.values()).count('model'),'positives and',list(expect.values()).count('empty'),'negatives')
if __name__=='__main__':main()
