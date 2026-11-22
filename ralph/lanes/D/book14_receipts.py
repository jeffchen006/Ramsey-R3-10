from collections import Counter
from itertools import combinations
from pathlib import Path
from time import process_time
import json,subprocess,sys
from book_strata import DEST,OLD,gates,root_fits
from book_controls import sites
from plateau_audit import canonical,g6


def read(name):return list(map(json.loads,(DEST/(name+'.jsonl')).read_text().splitlines()))


def panel():
    totals=Counter();examples=[];frames={};family=set();rootkeys=set();totalcpu=Counter();matched=[]
    for deck,lp in [('boundaries','dense'),('holdout','holdlp')]:
        inputs=read(deck);results={tuple(row['id']):row for row in read(lp)};used=set()
        for rec in inputs:
            key=(*rec['pair'],rec['cross'],rec['rep']);family.add(tuple(rec['pair']));rows=rec['rows'];totals[deck,'attempt']+=1
            if not rows:assert rec['tries']==100;totals[deck,'generator cap']+=1;continue
            rootkeys.update(rec['roots']);assert rec['roots'];examples.append(g6(rows));frames[key]=rows;start=process_time();direct,foot=gates(rows,9,40);totalcpu['cheap gates']+=process_time()-start;assert (direct is None)==(rec['direct'] is None) and (foot is None)==(rec['foot'] is None);totals[deck,'generated']+=1
            if direct:
                left,right=direct;word=left|(right<<11);assert word.bit_count()==10 and all(not(rows[point]&word) for point in sites(word));totals[deck,'I10']+=1
            elif foot:totals[deck,'footprint']+=1
            else:
                result=results[key];used.add(key);totals[deck,result['status']]+=1;totalcpu['occupancy decision']+=result['decision_cpu'];totalcpu['occupancy with replay']+=result['cpu']
                if result['status']=='fractional':matched.append(key)
        assert used==set(results)
    assert len(examples)==len(set(examples))==len(canonical(examples))==84
    for rec in read('edgesat'):
        key=tuple(rec['id']);assert key in matched
        if rec['status']!='True':continue
        rows=frames[key][:];outer=rec['Q'];mask=(1<<22)-1;contacts=[word&mask for word in outer]
        for point in range(22):
            rows[point]|=sum(1<<(22+idx) for idx,word in enumerate(contacts) if word>>point&1);assert rows[point].bit_count()==9
        for idx in range(18):rows.append(outer[idx] if rec['edges'] else contacts[idx]);
        for first,second in combinations(range(22),2):
            shared=(rows[first]&rows[second]).bit_count();assert shared==0 if rows[first]>>second&1 else 1<=shared<=(1 if (first,second) in ((1,2),(12,13)) else 3)
        if rec['edges']:
            assert all(word.bit_count()==9 for word in rows) and all(first!=second or not(row>>second&1) for first,row in enumerate(rows) for second in range(40));assert all(((rows[first]>>second)&1)==((rows[second]>>first)&1) and not(rows[first]>>second&1 and rows[first]&rows[second]) for first,second in combinations(range(40),2));assert sum((row>>22).bit_count() for row in rows[22:])==sum((row&mask).bit_count() for row in rows[:22])-36
        totals['sat edge' if rec['edges'] else 'sat mask','replayed models']+=1
    past=[rec['rows'] for rec in map(json.loads,(OLD/'outside-panel.jsonl').read_text().splitlines()) if rec['general']];print('Old five nested boundaries have direct and footprint flags',[(gates(rows,9,40)[0] is not None,gates(rows,9,40)[1] is not None) for rows in past]);print('PANEL',dict(totals),'uncoloured distinct',len(examples),'root union',len(rootkeys),'internal pairs',len(family),'CPU',dict(totalcpu))


def export():
    known={}
    for path in ['pop-11','pop-12-13.0','pop-12-13.1','pop-24','rare-price']:
        known.update({rec['id']:rec['status'] for rec in read(path)})
    hist=Counter();rich=[];general=[]
    with (DEST/'wing8.g6').open() as db,(DEST/'half-joined.tsv').open() as joining:
        for idx,(text,line) in enumerate(zip(db,joining,strict=True)):
            record=line.split();assert idx==int(record[0]);
            if record[1]!='live':continue
            edges=int(record[3]);
            if edges<13 or known.get(idx)=='separated':continue
            general.append(f'{idx}\t{edges}\t{text.strip()}\n');hist[edges]+=1
            if edges>=16:rich.append(general[-1]);
    (DEST/'all-wing-roots.tsv').write_text(''.join(general));(DEST/'rich-wing-roots.tsv').write_text(''.join(rich));print('all/rich oriented full wing roots',len(general),len(rich),'edge totals',dict(sorted(hist.items())))


if __name__=='__main__':
    panel()
    if '--readonly' not in sys.argv:export()
