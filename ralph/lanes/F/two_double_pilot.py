from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json
import subprocess
import sys

from one_double_pilot import ROOT, graph_build, to_graph6, tri_free, write
from round20_census import ADJ, load, totals
from marked_joint import count, read
from marked_replay import reverse_count
from two_double_check import board, verify


def prepare(tag,rows):
    size,target,edges=board(tag); edge_set=set(edges)
    text=chr(65+size)+''.join(str(int(left==right or (left,right) in edge_set)) for right in range(size) for left in range(right+1))
    sizes={target,target-1,target-2,target-4}
    if tag=='old':sizes.remove(target-4)
    bank=[mask for mask in range(1<<size) if mask.bit_count() in sizes] if tag!='pin' else [60]
    write(tag+'.q',[(text,)]);write(tag+'.bank',[(mask,) for mask in bank]);write(tag+'.rows',sorted(rows))


def small():
    for quotient in range(8):prepare('s'+str(quotient),[(occupied,doubled,1) for occupied in range(8) for doubled in (3,5,6) if occupied&doubled==doubled])
    prepare('old',[(3,3,1)]);prepare('pin',[(7,3,1)])


def literal():
    stats=Counter();examples={};five={size:list(combinations(range(size),5)) for size in (7,8)}
    for quotient in range(8):
        tag='s'+str(quotient);size,target,edges=board(tag);cuts=verify(tag);positives=set()
        for ends in product(range(4),repeat=size):
            if ends.count(3)!=2:continue
            row=sum(1<<idx for idx,ends_here in enumerate(ends) if ends_here),sum(1<<idx for idx,ends_here in enumerate(ends) if ends_here==3),1
            for signs in range(1<<len(edges)):
                for verticals in range(1<<(size+1)):
                    full=graph_build(size,edges,signs,verticals,ends)
                    for order in (7,8):
                        if order==7 and verticals>>3:continue
                        graph=[neighbors&((1<<order)-1) for neighbors in full[:order]]
                        good=tri_free(graph) and not any(all(not(graph[left]>>right&1) for left,right in combinations(subset,2)) for subset in five[order])
                        stats[order,good]+=1
                        if good:
                            assert row not in cuts;positives.add(row);examples.setdefault(order,(tag,ends,signs,verticals,graph))
        assert positives==set(read(tag+'.rows'))-cuts
    assert set(examples)=={7,8}
    for order,(tag,ends,signs,verticals,graph) in examples.items():
        name='positive'+str(order);Path(name+'.g6').write_text(to_graph6(graph)+'\n')
        result=json.loads(subprocess.check_output([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',name+'.g6',str(order),'5']))
        assert result['graphs'][0]['ok'];Path(name+'.gate').write_text(json.dumps(result,sort_keys=True)+'\n');print('physical positive',order,tag,ends,signs,verticals)
    assert not verify('old') and (3,3,1) in set(read('s0.checked'))
    assert verify('pin')=={(7,3,1)}
    print('physical classification',sorted(stats.items()),'old modes open on s0 row (3,3,1), four-endpoint mode closes it')


def mutations():
    def bad(tag,old,new,reason):
        trace=Path(tag+'.trace').read_text();assert old in trace
        try:verify(tag,trace.replace(old,new,1))
        except AssertionError as error:assert str(error)==reason;print('rejected',tag,reason,repr(old),'->',repr(new))
        else:raise ValueError('forgery accepted')
    bad('s0','begin 3 3 3 3 3','begin 3 3 3 3 5','missing vertical')
    bad('pin','step 1 0 60 56 60','step 1 0 60 60 56','endpoint pins')
    bad('s0','step 4 3 4 4 4','step 4 3 2 2 2','reused site')
    bad('s0','step 4 3 4 4 4 0','step 4 4 0','unbound step')
    bad('s0','step 4 3 4 4 4 0','step 4 3 4 4 4 2','projected equations')
    bad('s0','step 4 3 4 4 4','step 4 5 2 2 2','unjustified vertical')


def preflight():
    previous=ROOT/'scratch/F/r20';marked=load(previous/'mark.left');exterior=load(previous/'pole.left')
    roster={row for row in marked if row[1].bit_count()==2}
    assert marked<=exterior and totals(roster)==(14,23,5)
    prepare('pilot',roster);assert Path('pilot.q').read_bytes()==(previous/'pilot.q').read_bytes();print('only approved target rows',totals(roster))


def price():
    previous=ROOT/'scratch/F/r20';marked=load(previous/'mark.left');exterior=load(previous/'pole.left')
    domain=load('pilot.rows');cut=load('pilot.checked'); assert cut<=domain=={row for row in marked if row[1].bit_count()==2} and domain<=exterior
    for name,rows in [('pilot.open',domain-cut),('mark.left',marked-cut),('pole.left',exterior-cut),('two-double-exterior.untested',{row for row in exterior-domain if row[1].bit_count()==2})]:
        write(name,sorted(rows));print(name,totals(rows))
    print('sample cuts, both roles (not additive)',totals(cut))
    def pairs(first,second):return count(17,10,ADJ,first,second)
    old=pairs(marked,exterior);new=pairs(marked-cut,exterior-cut)
    hits=[pairs(cut,exterior),pairs(marked,cut),pairs(cut,cut)]
    def counts(res,mult):return [res[mult,unit] for unit in ('labels','fixed','orbits')]
    assert [counts(old,mult) for mult in range(3)]==[list(row[4:7]) for row in read(previous/'joint.tsv')]
    assert sum(old[mult,'orbits'] for mult in range(3))==1979210
    for mult,other_count in enumerate(reverse_count('mark.left','pole.left')):
        assert other_count==new[mult,'orbits']
        for unit in ('labels','fixed','orbits'):
            key=mult,unit;assert old[key]-new[key]==hits[0][key]+hits[1][key]-hits[2][key]
    write('joint.tsv',[(mult,*[num for res in [old,new,*hits] for num in counts(res,mult)]) for mult in range(3)])
    print('totals old, new, mark-hits, pole-hits, overlap',*[sum(res[mult,'orbits'] for mult in range(3)) for res in [old,new,*hits]])


if __name__=='__main__':
    {'small':small,'literal':literal,'mutations':mutations,'preflight':preflight,'verify':lambda:verify('pilot'),'price':price}[sys.argv[1]]()
