"""Bind the cover, strict second-role partition, every seed cut and every regenerated labelled formula."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,permutations
from math import perm
from pathlib import Path
import json,sys
import networkx as nx
import numpy as np
from arc_edges import profiles,make as arc_form
from octo_edges import populations,make as octo_form
from equal_roles import DEST,SHAPES,build,shape,verify
from hex_fibers import masks
from hex_edges import encode
from hex_oneproof import literal
from hex_hub import make as hub_form
from book_controls import bitset,sites
from book_contacts import standard


def records(pattern):return [json.loads(line) for path in sorted(DEST.glob(pattern)) for line in path.read_text().splitlines()]


def roles():
    for count,parts in enumerate(SHAPES):
        rows,_=shape(parts);graph=standard(rows);network=nx.Graph();network.add_edges_from((site,other) for site in range(3,19) for other in range(3,site) if graph[site]>>other&1);aut=[]
        for mapping in nx.isomorphism.GraphMatcher(network,network).isomorphisms_iter():
            swap={bool(site<11)!=bool(other<11) for site,other in mapping.items()}
            if len(swap)!=1:continue
            flipped=swap.pop();mapping.update({0:0,1:1+int(flipped),2:2-int(flipped)});aut.append(mapping)
        allrows=records(f'roster{count}.jsonl');seen=set();total=live=0
        for record in allrows:
            first,second,hub=record['path'];physical=set()
            for mapping in aut:
                ends=sorted(mapping.get(site,19) for site in (first,second));physical.add((*ends,mapping.get(hub,19)))
            assert not seen&physical and len(physical)==record['orbit'];seen|=physical
            for loc in physical:
                outside=loc.count(19);weight=perm(21,outside)//(2 if loc[0]==loc[1]==19 else 1);total+=weight;lhs,rhs,witness=loc;bad=False
                for left,right,expected in ((lhs,rhs,0),(lhs,witness,1),(rhs,witness,1)):
                    if right<19 and left<19:bad|=bool(graph[left]>>right&1)!=bool(expected)
                if rhs<19:bad|=bool(graph[lhs]&graph[rhs]&~(1<<witness))
                assert bad==bool(record['reason']);live+=weight*(not bad)
        assert total==23310
        priced=records(f'role{count}.jsonl');assert {tuple(row['path']) for row in priced}=={tuple(row['path']) for row in allrows if not row['reason']}
        for row in priced:
            if row['status']=='fractional':continue
            assert row['status']=='separated';data=build(rows,40,tuple(row['path']),2);dual=np.zeros(len(data[1]),dtype=np.int64)
            for position,value in row['dual'].items():dual[int(position)]=value
            assert min(dual)>=0 and verify(data,dual)==row['margin']>0
        print('PASS fixed-book colored automorphisms, path roles, placements, LP',parts,len(aut),len(allrows),len(priced),live,total,Counter(row['status'] for row in priced))


def catalog(destination):
    roles()
    for width,rows in ((6,profiles()),(8,populations())):
        independent=[tuple(map(int,line.split())) for line in (destination/f'ind-{width}.pop').read_text().splitlines()];assert len(set(independent))==len(independent)==len(rows) and set(independent)=={words for idx,words in rows};print('PASS independent full catalog',width,len(rows))
    words=masks();seen=set();roster=records('hex-seven.jsonl');keys={tuple(row['profile']) for row in roster};types=list(dict.fromkeys(words))
    for selected in combinations(range(21),7):
        hist=Counter(words[point] for point in selected)
        if any(not 1<=sum(count for word,count in hist.items() if word>>site&1)<=2 for site in range(6)):continue
        profile=tuple(hist[word] for word in types)
        if profile in seen:continue
        orbit=set()
        for sign in (-1,1):
            for offset in range(6):
                remap={bitset((offset+sign*site)%6 for site in sites(word)):value for word,value in hist.items()};orbit.add(tuple(remap.get(word,0) for word in types))
        seen.update(orbit);assert min(orbit) in keys
    for row in roster:
        seven=row['seven'];assert len(set(seven))==len(seven)==7;assert tuple(sum(words[point]==word for point in seven) for word in types)==tuple(row['profile']) and tuple(row['profile']) in seen
    assert len(keys)==len(roster)==71;print('PASS all 116280 labelled hub subsets, independent D6 mask action')


def seed_ok(width,words,seed,subset,hub=None):
    if seed.bit_count()+subset.bit_count()!=10:return False
    points=set(sites(seed));edges={(0,1),(0,2),*((1+site%2,3+site) for site in range(width)),*((3+site,3+(site+1)%width) for site in range(width))};return not any({lhs,rhs}<=points for lhs,rhs in edges) and all(not(word<<3&seed) and not(hub is not None and seed&1 and pos in hub) for pos,word in enumerate(words) if subset>>pos&1)


def formulas(folder,shard,mod):
    lists=[];hexrows=sorted(records('edges[0-3].jsonl'),key=lambda row:row['id']);assert [row['id'] for row in hexrows]==list(range(71));seven=records('hex-seven.jsonl')
    for row in hexrows:
        assert row['status']=='False';idx=row['id'];lists.append(('hex-edge-'+str(idx),('hex',idx,seven[idx]['seven'],row['cuts'])))
    octaves=dict(populations());first=records('octo[0-3].jsonl');last,=records('oct-last.jsonl');assert len(first)==len(octaves)==123 and {row['id'] for row in first}==set(octaves) and [row['id'] for row in first if row['status']!='False']==[last['id']]
    for row in sorted([row for row in first if row['status']=='False']+[last],key=lambda row:row['id']):
        idx=row['id'];assert row['status']=='False';lists.append((f"oct-{idx}-{row['mode']}",('oct',row['mode'],octaves[idx],row.get('cuts',[]))))
    arcs=dict(profiles());short=records('arc8.*.jsonl');long=records('arc16.*.jsonl');tail,=records('arc-last.jsonl');assert set(arcs)=={row['id'] for row in short} and len(short)==93 and {row['id'] for row in short if row['status']!='False'}=={row['id'] for row in long} and [row['id'] for row in long if row['status']!='False']==[tail['id']]
    accepted=[row for row in short+long if row['status']=='False']+[tail];assert len(accepted)==len(set(row['id'] for row in accepted))==93
    for row in sorted(accepted,key=lambda row:row['id']):
        idx,span=row['id'],row['span'];assert row['status']=='False';lists.append((f'arc-{idx}-{span}',('arc',arcs[idx],span)))
    also,=records('one-1-0-1-1.jsonl');assert also['status']=='False';lists.append((also['tag'],('unsplit',also['cuts'])))
    for tag,info in lists[shard::mod]:
        if info[0]=='arc':form=arc_form(*info[1:])
        elif info[0]=='hex':
            _,idx,hub,clauses=info;form=encode(idx)
            for subset in clauses:
                assert any(seed_ok(6,masks(),seed,subset,hub) for seed in range(1<<9));form.add(*[form.edge(lhs,rhs) for lhs,rhs in combinations(sites(subset),2) if form.edge(lhs,rhs) is not False])
        else:
            if info[0]=='oct':_,mode,words,clauses=info;form=octo_form(words,mode);width=8
            else:width=6;words=masks();clauses=info[1];form=hub_form(1,0,1,1)
            for seed,subset in clauses:assert seed_ok(width,words,seed,subset);form.add(*literal(form,seed,subset))
        path=folder/f'{tag}.cnf';form.write(path);digest=sha256(path.read_bytes()).hexdigest();assert digest==sha256((DEST/path.name).read_bytes()).hexdigest();print(tag,digest,flush=True)


if __name__=='__main__':
    directory=Path(sys.argv[2]);catalog(directory) if sys.argv[1]=='catalog' else formulas(directory,*map(int,sys.argv[3:5]))
