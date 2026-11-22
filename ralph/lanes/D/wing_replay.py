"""Independent literal-mask verification for all half cuts and sparse-wing closure."""
from collections import Counter
from itertools import combinations,product
import json,sys
from book_strata import DEST,standard
from half_wing import rectangle_graph
from kernel_cnf import decode


def elems(word):return [idx for idx in range(word.bit_length()) if word>>idx&1]


def sets(rows):
    found=[0]
    for site,hood in enumerate(rows):found+= [word|1<<site for word in found if not word&hood]
    return found


def verify_dual(record,short):
    rows=record['rows'];B=rectangle_graph(rows,short);order=len(B);pop=40-order;allsets=sets(B);upper=[mask for mask in allsets if mask.bit_count()==9];assert max(mask.bit_count() for mask in allsets)==9;weak=6
    def expected(mask):
        if not mask:return pop,pop
        points=elems(mask)
        if len(points)==1:return (9-B[points[0]].bit_count(),)*2
        first,second=points;assert not(B[first]>>second&1);used=(B[first]&B[second]).bit_count();return 1-used,(1 if mask==weak else 3)-used
    critical=[]
    for first,second in combinations(range(order),2):
        word=1<<first|1<<second
        if not B[first]>>second&1 and expected(word)[1]==0:critical.append(word)
    saturated=sum(1<<point for point,hood in enumerate(B) if hood.bit_count()==9);weights=[];right=0
    for row in record['dual']:
        if len(row)==6:
            kind,mask,low,high,sign,weight=row;assert kind in ('total','deg','pair')
        else:mask,low,high,sign,weight=row
        assert expected(mask)==(low,high) and weight>0 and sign in (0,1);weights.append((mask,-weight if sign else weight));right+=weight*(-low if sign else high)
    count=0;minimum=None
    for mask in allsets:
        if mask.bit_count()>9 or mask&saturated or any((mask&hood).bit_count()>3 for hood in B) or any(mask&pair==pair for pair in critical) or any(not(mask&fixed) for fixed in upper):continue
        value=sum(value for term,value in weights if term&mask==term);minimum=value if minimum is None else min(minimum,value);count+=1
    assert count==record['columns'] and pop*minimum-right==record['margin']>0


def literal_return(rows):
    n=len(rows);full=(1<<n)-1;maximum=[]
    for mask in range(1<<n):
        near=0
        for point in elems(mask):near|=rows[point]
        opposite=full^near
        if mask.bit_count()+opposite.bit_count()==n:maximum.append(mask|opposite<<n)
    pair=[(left,right) for left,right in product(range(n),repeat=2) if not(rows[left]>>right&1) and all(seed&(1<<left|1<<(n+right)) for seed in maximum)]
    accepted=[mask for mask in range(1,1<<n) if mask.bit_count()<=3];ret_min=10000
    for mask in range(1<<n):
        cost=sum(n-rows[point].bit_count() for point in elems(mask));return_arcs=Counter(b for a,b in pair if not mask>>a&1)
        for b,number in return_arcs.items():cost+=min(n-sum(row>>b&1 for row in rows),3*number)
        ret_min=min(ret_min,cost)
    # Independently check the separator implication on all same-site labelled choices.
    for left in accepted:
        occupied=0
        for point in elems(left):occupied|=rows[point]
        for right in accepted:
            if right&occupied or any(not(seed&(left|right<<n)) for seed in maximum):continue
            assert any(left>>a&1 and right>>b&1 for a,b in pair)
    return len(pair),ret_min


def main():
    if sys.argv[1]=='half':
        count=0
        for row in map(json.loads,(DEST/'half.jsonl').read_text().splitlines()):
            if row['status']=='separated':verify_dual(row,4);count+=1
        print('PASS half-15 exterior duals, separate masks and bounds',count);return
    limit=int(sys.argv[1]);docs={row['id']:row for path in DEST.glob('pop-*.jsonl') for row in map(json.loads,path.read_text().splitlines()) if row['edges']<=limit};stats=Counter();weights={int(line.split()[0]):int(line.split()[-1]) for line in (DEST/'orbit.tsv').read_text().splitlines()};dups=set()
    for line,scan in zip((DEST/'wing8.g6').open(),(DEST/'wing8.scan').open(),strict=True):
        rank,edges,status,*parts=scan.split();rank=int(rank);edges=int(edges)
        if edges>limit or status=='pre':continue
        assert rank in weights;dups.add(rank);raw=decode(line.strip());rows=[sum(1<<(v-8) for u,v in raw if u==point) for point in range(8)]
        if status=='minor':
            from book_contacts import scores
            found=False
            for left,right in product(combinations(range(8),4),repeat=2):
                subset=[sum(1<<idx for idx,site in enumerate(right) if rows[point]>>site&1) for point in left];score=max(scores(standard(subset),9)) if all(subset) and all(any(row>>col&1 for row in subset) for col in range(4)) else 0
                if score>29:found=True;break
            assert found
        elif status=='return':
            pairs,cut=literal_return(rows);assert (pairs,cut)==tuple(map(int,parts[-2:])) and cut<14
        else:
            record=docs[rank];assert rows==record['rows'];status=record['status']
            if status=='separated':verify_dual(record,8)
            else:
                tags=[tag for tag in ('edge','full') if (DEST/f'wing-{rank}-{tag}.cake_lpr.log').exists() and 'VERIFIED UNSAT' in (DEST/f'wing-{rank}-{tag}.cake_lpr.log').read_text() and 'c VERIFIED' in (DEST/f'wing-{rank}-{tag}.lrat-check.log').read_text()];assert tags;status='dual-LRAT'
        stats[edges,status]+=1
    assert dups==set(weights);print('PASS all sparse classes, with literal checked return-pair cuts, exterior multipliers and checked local proof receipts',dict(sorted(stats.items())))


if __name__=='__main__':main()
