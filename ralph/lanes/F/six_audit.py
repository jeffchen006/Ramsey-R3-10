from itertools import combinations
from pathlib import Path
from collections import Counter
import gzip,json,sys
from orbit_extend import parse_graph6,ROOT

def rank(words):
    remaining=list(words);result=0
    while any(remaining):
        lead=max(remaining);position=lead.bit_length()-1;remaining=[value^lead if value>>position&1 else value for value in remaining];result+=1
    return result
def bank():
    matrix={};active=[];base=[];forest=[]
    for line in Path('columns.tsv').read_text().splitlines():
        left,right,expr=map(int,line.split());assert (left,right) not in matrix and expr<1<<35;matrix[left,right]=expr;active.append(expr);boundary=1<<left|1<<right
        if rank(base+[boundary])>len(base):base.append(boundary);forest.append((left,right));assert expr==0
    edges=list(combinations(range(17),2));assert set(matrix)=={(left,right) for left,right in edges if 6<=right-left<=12};assert rank(active)==35
    equations=[1<<list(matrix).index(pair) for pair in forest]
    for triple in combinations(range(17),3):
        pairs=list(combinations(triple,2));
        if all(pair in matrix for pair in pairs):
            first,second,third=[matrix[pair] for pair in pairs];assert first^second^third==0;equations.append(sum(1<<list(matrix).index(pair) for pair in pairs))
    assert rank(equations)==len(matrix)-35
    for index,line in enumerate(Path('bank.tsv').read_text().splitlines()[:576]):
        support,count,*given=map(int,line.split());sites={vertex for vertex in range(17) if support>>vertex&1};assert support<1<<17 and len(sites)==10
        labels={};cycles=[]
        while set(labels)!=sites:
            root=min(sites-set(labels));labels[root]=0;stack=[root]
            while stack:
                left=stack.pop()
                for right in sites:
                    pair=tuple(sorted((left,right)))
                    if pair not in matrix:continue
                    if right not in labels:labels[right]=labels[left]^matrix[pair];stack.append(right)
                    else:cycles.append(labels[left]^labels[right]^matrix[pair])
        assert rank(given)==count==rank(cycles)==rank(given+cycles)
    assert index==575;print('rebound 56 physical matchings,16 forest and 5 triangle equations; full rank 35. All 576 active supports verified via endpoint labels.')
def summary():
    bytag={};entries=[];ranges=[];caps=[];deep=[];stages=Counter();seconds=0
    def add(tag,start,end,totals,source):
        assert 0<=start<end<=1<<24 and totals[0]==end and totals[1]==2048*(end-start) and totals[2]==sum(totals[3:]);ranges.append((start,end,str(source)));bytag.setdefault(tag,[0]*7)
        for axis,value in enumerate(totals[1:]):bytag[tag][axis]+=value
        data=source.read_bytes();data=gzip.decompress(data) if source.suffix=='.gz' else data
        checked=Counter();within=set()
        for line in data.splitlines():
            fields=line.split();key=int(fields[0]);assert start*2048<=key<end*2048 and key not in within;within.add(key);checked[fields[1]]+=1
            if fields[1]==b'cap':caps.append(key)
            elif fields[1]==b'multi':
                reached=[int(value) for value in fields[4:10]];depth=max(index+1 for index,value in enumerate(reached) if value);stages[depth]+=1
                if depth>=3:deep.append(key)
        assert [checked[value] for value in (b'one',b'multi',b'model',b'cap')]==totals[4:]
    for label in ('price','trial','strata'):
        for path in Path('.').glob(label+'*.count'):
            totals=list(map(int,path.read_text().splitlines()[-1].split()));add(label,totals[0]-32,totals[0],totals,path.with_suffix('.rows'));seconds+=sum(map(float,path.with_suffix('.time').read_text().split()[1:3]))
    for table in sorted(Path('.').glob('work_*/w*.jsonl')):
        label=table.parent.name.removeprefix('work_');plan=[tuple(map(int,line.split())) for line in Path('plan_'+label+'.tsv').read_text().splitlines()]
        for line in table.read_text().splitlines():
            row=json.loads(line);index=row['index'];assert plan[index]==(index,row['start'],row['end']);seconds+=row['cpu'];
            if row['status']=='scanned':
                direct=list(map(int,(table.parent/f's{index:05d}.count').read_text().splitlines()[-1].split()));assert row['rc']==0 and direct==row['totals'];add(label,row['start'],row['end'],direct,table.parent/f's{index:05d}.rows.gz');entries.append((label,index))
    assert len(set(entries))==len(entries);ranges.sort();assert all(ranges[index][1]<=ranges[index+1][0] for index in range(len(ranges)-1));assert len(caps)==len(set(caps));raw=sum(row[1]-row[0] for row in ranges)*2048
    values=[sum(row[index] for row in bytag.values()) for index in range(7)];assert values[0]==raw
    print('raw,sieve-pass,physical-bare,one,multi,model,cap',bytag,'total',values);print('disjoint leaves',len(ranges),'depth counts among multi',dict(stages),'cpu-s',round(seconds,2));print('unscanned normalized words',(1<<35)-raw)
    Path('residual.keys').write_text(''.join(f'{key}\n' for key in sorted(caps)));Path('deeper.keys').write_text(''.join(f'{key}\n' for key in sorted(deep)))
if __name__=='__main__':{'bank':bank,'summary':summary}[sys.argv[1]]()
