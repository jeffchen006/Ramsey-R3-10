from collections import Counter,defaultdict
from functools import lru_cache
from itertools import combinations,permutations
import json
import os
from pathlib import Path
import sys

from closure22 import ROOT,bits,digest,stage
from m14queue22 import BASE,data
from rebind import physical
from shadow import decode,Cadical195
from audit import type_words
from triple18_price import shore_words
from wing19 import index_long

TARGET=BASE/'prefix'


@lru_cache(None)
def profiles(degrees):
    return type_words(list(degrees),sum(degrees)-8)


def inventory(key):
    support,first,ranks=data(key);part=key[0];second=first if part=='D' else [2]*7 if part=='S' else [2,1,2,2,2,2,2]
    left=profiles(tuple(first));right=profiles(tuple(second));edges=list(combinations(range(7),2));pairs=[1<<a|1<<b for a,b in edges];histo=lambda word:tuple(word.count(pair) for pair in pairs)
    leftcols=list(map(histo,left));rightcols=list(map(histo,right))
    assert set(leftcols)==set(map(tuple,shore_words(edges,first,len(ranks)-ranks.count(1)))) and set(rightcols)==set(map(tuple,shore_words(edges,second,sum(second)-8)))
    index=index_long(rightcols);used=[sum(mask&pair==pair for mask in support) for pair in pairs];columns=[table[value] for table,value in zip(index,used)]
    groups=[];host=Counter(support)
    for perm in permutations(range(7)):
        if any(first[site]!=first[dst] or second[site]!=second[dst] for site,dst in enumerate(perm)):continue
        images={mask:sum(1<<dst for src,dst in enumerate(perm) if mask>>src&1) for mask in set(support)|set(pairs)|{1<<site for site in range(7)}}
        if Counter(images[mask] for mask in support)==host:groups.append((perm,images))
    full=(1<<len(right))-1;total=Counter();fixed=defaultdict(Counter)
    for perm,images in groups:
        identity=perm==tuple(range(7));scope=full if identity else sum(1<<offset for offset,word in enumerate(right) if Counter(map(images.get,word))==Counter(word));tag=''.join(map(str,perm));total[tag]+=0
        for word,counts in zip(left,leftcols):
            if not identity and Counter(map(images.get,word))!=Counter(word):continue
            possible=scope
            for column,number in zip(columns,counts):possible&=column[number]
            fixed[word[0]][tag]+=possible.bit_count();total[tag]+=possible.bit_count()
    assert sum(total.values())%len(groups)==0
    heads=sorted({word[0] for word in left});assert set(fixed)==set(heads)
    return dict(key=key,sorted_short=len(left),sorted_long=len(right),heads=heads,per_head_profiles=dict(Counter(word[0] for word in left)),per_head_fixed={mark:{tag:counts[tag] for tag in total} for mark,counts in sorted(fixed.items())},fixed=total,orbits=sum(total.values())//len(groups),group=len(groups))


def cal():
    count=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        stars=decode(line)
        if any(star.bit_count()!=6 for star in stars) or max((left&right).bit_count() for left,right in combinations(stars,2))>3:continue
        for first in range(22):
            for second in range(22):
                common=stars[first]&stars[second]
                if common.bit_count()!=1 or stars[first]>>second&1:continue
                middle=common.bit_length()-1;poles=list(bits(stars[middle]&~((1<<first)|(1<<second))));ys=sorted(set(range(22))-{first,second,middle}-set(bits(stars[first]|stars[second]|stars[middle])))
                def mask(site):return sum(1<<index for index,pole in enumerate(poles) if stars[site]>>pole&1)
                wing=sorted(bits(stars[first]&~common),key=lambda site:(mask(site).bit_count(),mask(site)),reverse=True)
                labels=poles+ys+wing;head=mask(wing[0]);ranks=[mask(site).bit_count() for site in wing];degrees=lambda left,right:[sum(stars[site]>>other&1 for other in right) for site in left];bounds=lambda values:(min(values),max(values))
                wy=degrees(wing,ys);yw=degrees(ys,wing);yy=degrees(ys,ys);cards=[sum(1<<site for site in chosen) for sites,width in [(len(labels),6),(len(poles)+len(ys),5)] for chosen in combinations(range(sites),width)]
                for mark,wanted in [(head,True),(head^1,False)]:
                    formula,_,edge=physical(list(map(mask,ys)),[mark],ranks,degrees(poles,wing),bounds([rank+deg for rank,deg in zip(ranks,wy)]),bounds(yw),bounds([mask(site).bit_count()+a+b for site,a,b in zip(ys,yw,yy)]),sum(yw),sum(yy)//2,6,cards)
                    pins=[edge(left,right)*(1 if stars[labels[left]]>>labels[right]&1 else -1) for left,right in combinations(range(len(labels)),2)]
                    with Cadical195(bootstrap_with=formula.clauses) as solver:assert solver.solve(assumptions=pins)==wanted
                count+=1
    assert count==250;print('250 C22 directed physical sorted-head controls; 250 adverse flipped prefix labels rejected')


def bind(key,head):
    support,hits,ranks=data(key);path=BASE/key/'cards';formula,count,_=physical(support,[head],ranks,hits,(5,6),(2,3),(6,7),64-17-sum(hits),14,9,map(int,path.read_text().splitlines()));formula.to_file('input.cnf');print(count,formula.nv,len(formula.clauses))


def leaf(key,head):
    directory=TARGET/f'{key}-{head}';directory.mkdir();os.chdir(directory)
    results=[];status='open';files={}
    try:
        for name,args,cap,limit,rc,marker in [
            ('bind',[sys.executable,'-B',__file__,'bind',key,head],30,24000000,0,None),('solve',[ROOT/'opt/bin/cadical','--lrat','--no-binary','input.cnf','raw.lrat'],80,120000000,20,'s UNSATISFIABLE'),('trim',[BASE/'lrat-trim','-a','input.cnf','raw.lrat','proof.lrat'],80,120000000,20,'s VERIFIED'),('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],80,4000000,0,'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],110,4000000,0,'s VERIFIED UNSAT'),('compress',['zstd','--single-thread','-4','-q','proof.lrat','-o','proof.zst'],60,60000000,0,None),('integrity',['zstd','-tq','proof.zst'],40,4000000,0,None)]:
            result=stage(name,args,cap,limit,rc,marker);results.append(result)
            if not result['ok']:status=f'{name}:{result["rc"]}';break
            if name=='trim':Path('raw.lrat').unlink()
        else:
            files={name:[digest(path),path.stat().st_size] for name,path in [('cards',BASE/key/'cards'),('input.cnf',Path('input.cnf')),('proof.lrat',Path('proof.lrat')),('proof.zst',Path('proof.zst'))]};status='dual_checked'
    finally:
        for name in ['raw.lrat','input.cnf','proof.lrat']:Path(name).unlink(missing_ok=True)
        if status!='dual_checked':Path('proof.zst').unlink(missing_ok=True)
        Path('result.json').write_text(json.dumps(dict(key=key,head=head,status=status,checks=results,files=files),sort_keys=True)+'\n');print(key,head,status,flush=True)


def work(keys):
    TARGET.mkdir(exist_ok=True)
    for key in keys:
        entry=inventory(key);(TARGET/(key+'.json')).write_text(json.dumps(entry,sort_keys=True)+'\n')
        for head in entry['heads']:
            if sum(path.stat().st_size for path in TARGET.glob('*/proof.zst'))>420000000:print('PREFIX_ARCHIVE_GUARD',flush=True);return
            if not (TARGET/f'{key}-{head}').exists():leaf(key,head)


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    elif sys.argv[1]=='bind':bind(sys.argv[2],int(sys.argv[3]))
    elif sys.argv[1]=='inventory':print(json.dumps(inventory(sys.argv[2]),sort_keys=True))
    else:work(sys.argv[2:])
