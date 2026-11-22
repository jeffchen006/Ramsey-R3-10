from collections import Counter
from itertools import combinations
from time import process_time
import json,sys
from book_strata import DEST
from wing_population import wings


def witness(rows,outside):
    width=len(rows);columns=[sum(1<<point for point,row in enumerate(rows) if row>>col&1) for col in range(width)];sides=rows+columns;weights=[width-row.bit_count() for row in sides];links=[row<<width for row in rows]+columns[:];square=None
    for offset in (0,width):
        for first,second in combinations(range(width),2):
            pair=sides[offset+first]&sides[offset+second]
            if pair.bit_count()<2:continue
            assert pair.bit_count()==2;links[offset+first]|=1<<(offset+second);links[offset+second]|=1<<(offset+first)
            if not offset:
                col1=(pair&-pair).bit_length()-1;col2=pair.bit_length()-1;group=(first,second,width+col1,width+col2)
                if sum(weights[point] for point in group)>outside:square=group
    if square:return 'square',sum(1<<point for point in square)
    def recurse(pool,mask,weight):
        if weight>outside:return mask
        if weight+pool.bit_count()*maxweight<=outside:return None
        while pool:
            one=pool&-pool;point=one.bit_length()-1;pool^=one;found=recurse(pool&links[point],mask|one,weight+weights[point])
            if found:return found
    maxweight=max(weights);return 'clique',recurse((1<<(2*width))-1,0,0)


def cal():
    count=0
    for rec in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines()):
        group=rec['y']+rec['z'];assert len(group)==9;assert witness(rec['rows'],len(group))[1] is None;count+=1
    print('PASS planted singleton-capacity clique test on C22 full wings',count)


def replay(record,word):
    width=len(record);points=[idx for idx in range(2*width) if word>>idx&1];neigh=[{width+col for col in range(width) if row>>col&1} for row in record]+[{idx for idx,row in enumerate(record) if row>>col&1} for col in range(width)];assert sum(width-len(neigh[point]) for point in points)>21
    for first,second in combinations(points,2):assert second in neigh[first] or (first//width==second//width and len(neigh[first]&neigh[second])==2)


if __name__=='__main__':
    cal();kept=[];rich=[];dead=[];counts=Counter();start=process_time()
    for line in (DEST/'all-wing-roots.tsv').read_text().splitlines():
        idx,edges,code=line.split();record=wings(code);kind,mask=witness(record,21)
        if mask:replay(record,mask);dead.append(f'{idx}\t{kind}\t{mask}\n');counts[kind]+=1;continue
        kept.append(line+'\n');
        if int(edges)>=16:rich.append(line+'\n')
    for name,roster in [('clique-all.tsv',kept),('clique-rich.tsv',rich),('clique-cuts.tsv',dead)]:(DEST/name).write_text(''.join(roster))
    print('Whole oriented wing roots after singleton-capacity cuts',counts,'all',len(kept),'rich',len(rich),'CPU',process_time()-start)
