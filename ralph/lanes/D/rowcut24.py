import json
import subprocess
import sys
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from wing24 import OUT,ROOT,book,flags,graph_masks,reorder,bitset,sites
from high24 import HIGH

def problem(wing,points,words,added,degree):
    half=len(wing)//2;columns=tuple(bitset(idx for idx,mask in enumerate(words) if mask>>col&1) for col in range(len(points)));known=lambda lhs,rhs:-1 if wing[lhs]>>rhs&1 else (wing[lhs]&wing[rhs]).bit_count()+int((lhs<half)==(rhs<half));spent=sum(max(0,2-known(lhs,rhs)-(columns[first]&columns[second]).bit_count()) for first,lhs in enumerate(points) for second,rhs in enumerate(points[:first]) if known(lhs,rhs)>=0);return (len(words),len(points),degree-1-wing[added].bit_count(),spent,*columns,*[known(site,added) for site in points])

@lru_cache(maxsize=120000)
def possible(problem,budget=1):
    outer,width,demand,spent=problem[:4];columns=problem[4:4+width];known=problem[4+width:];groups=Counter(bitset(col for col,mask in enumerate(columns) if mask>>idx&1) for idx in range(outer));bounds=[(0,0) if count<0 else (2-count,3-count) for count in known];types=sorted(groups,key=lambda mask:(-mask.bit_count(),mask));sums=[0]*width
    def walk(idx,need):
        if idx==len(types):return not need and sum(max(0,low-used) for (low,upper),used in zip(bounds,sums))<=budget-spent
        word=types[idx];bits=list(sites(word));ceiling=min([need,groups[word],*[bounds[bit][1]-sums[bit] for bit in bits]]);remain=sum(groups[mask] for mask in types[idx+1:]);
        for qty in range(max(0,need-remain),ceiling+1):
            for bit in bits:sums[bit]+=qty
            good=walk(idx+1,need-qty)
            for bit in bits:sums[bit]-=qty
            if good:return True
        return False
    return walk(0,demand)

def calibrate():
    count=0;negative=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if {row.bit_count() for row in graph}!={6} or max((lhs&rhs).bit_count() for lhs,rhs in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);sequence=left+right;wing=reorder(graph,sequence);points=[0,1,2,5,6,7];added=3;outside=sorted(set(range(22))-set(sequence)-set(frame));words=tuple(bitset(col for col,site in enumerate(points) if graph[seq]>>sequence[site]&1) for seq in outside);instance=problem(wing,points,words,added,6);debit=sum((graph[sequence[lhs]]&graph[sequence[rhs]]).bit_count()==1 for lhs,rhs in combinations([*points,added],2) if not wing[lhs]>>rhs&1);assert possible(instance,debit);assert not possible((instance[0],instance[1],instance[0]+1,*instance[3:]),debit);count+=1;negative+=1
    assert count==125;print('125 C22 lifted row witnesses, 125 impossible occupancy mutations')

def run(edges):
    rows=json.loads((HIGH/f'spec{edges}.json').read_text());defects={};submitted={};free=[]
    for row in rows:
        wing=graph_masks(row['g6']);points=row['points'];added=sorted(set(range(16))-set(points));
        for idx,words in enumerate(row['decks']):
            key=f'h{edges}_{row["number"]}_{idx}'
            for site in added:
                data=problem(wing,points,words,site,9)
                if not possible(data):defects[key]=site;submitted[key]=data;break
            else:free.append(key)
    text=''.join(' '.join(map(str,(key,*data)))+'\n' for key,data in submitted.items());result=subprocess.run([OUT/'rowcut'],input=text,text=True,capture_output=True,check=True);found={key:int(count) for key,count,mask in map(str.split,result.stdout.splitlines())};assert set(found)==submitted.keys() and not any(found.values());(HIGH/f'rowcuts{edges}.tsv').write_text(''.join(f'{key}\t{site}\n' for key,site in sorted(defects.items())));(HIGH/f'aftercuts{edges}').write_text(''.join(key+'\n' for key in free));print('e',edges,'input',len(free)+len(defects),'literal exhausted row',len(defects),'survivors',len(free),'native witnesses matched',len(found),flush=True)

if __name__=='__main__':
    if sys.argv[1]=='cal':calibrate()
    else:run(int(sys.argv[1]))
