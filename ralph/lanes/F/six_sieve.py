from itertools import combinations
from collections import Counter
from six_branch import EDGES,FREE,decode,basis,hard_keys
from pathlib import Path
import sys

def events(edges,sites,target,columns):
    where={edge:index for index,edge in enumerate(edges)};output={}
    for subset in combinations(range(sites),target):
        pivots={};cycles=[]
        for left,right in combinations(subset,2):
            if (left,right) not in where:continue
            inc=(1<<left)|(1<<right);vec=columns[where[left,right]]
            while inc and inc.bit_length() in pivots:
                old,expression=pivots[inc.bit_length()];inc^=old;vec^=expression
            if inc:pivots[inc.bit_length()]=inc,vec
            else:cycles.append(vec)
        base=basis(cycles)
        for pos in sorted(base):
            for other in base:
                if other>pos and base[other]>>pos&1:base[other]^=base[pos]
        rows=tuple(sorted(base.values()));output.setdefault(rows,sum(1<<index for index in subset))
    return output
def make():
    columns=[sum(1<<index for index in range(len(FREE)) if decode(1<<index)>>edge&1) for edge in range(len(EDGES))];rows=events(EDGES,17,10,columns);print('all',len(rows),sorted(Counter(map(len,rows)).items()),flush=True)
    Path('columns.tsv').write_text(''.join(f'{left} {right} {value}\n' for (left,right),value in zip(EDGES,columns)))
    lines=sorted(rows.items(),key=lambda item:(len(item[0]),item[1]));Path('bank.tsv').write_text(''.join(' '.join(map(str,(mask,len(vals),*vals)))+'\n' for vals,mask in lines));
if __name__=='__main__':make()
