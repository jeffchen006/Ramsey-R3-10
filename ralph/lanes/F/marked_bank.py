"""Round 18 fixed inventory, physical controls and arithmetic reprice."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

from marked_joint import count, read, reflection
from marked_replay import reverse_count
from orbit_extend import ROOT, independent_sets, to_graph6
from relift_audit import encode

OLD = ROOT/'scratch/F/r17'


def write(path, rows):
    Path(path).write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))


def control():
    labels=[0,4,1,5,2,6,3]
    actual=[sum(1<<dest for dest,other in enumerate(labels) if (other-site)%8 in (1,4,7)) for site in labels]
    for name,graph in [('positive',actual),('blind',[neighbors&63 for neighbors in actual[:6]]+[0])]:
        assert not any(graph[left]&graph[right] for left,right in combinations(range(7),2) if graph[left]>>right&1)
        Path(name+'.g6').write_text(to_graph6(graph)+'\n')
        gate=json.loads(subprocess.check_output([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',name+'.g6','7','4']))
        bad=next(independent_sets(graph,127,4),None)
        assert gate['graphs'][0]['ok']==(bad is None)==(name=='positive')
        footprint=sum(1<<site for site in range(3) if graph[6]&(3<<(2*site)))
        assert footprint=={'positive':5,'blind':0}[name]
        print(name,'literal labels',labels,'contact endpoint mask',graph[6],'footprint',footprint,'physical I4:',bad)
    write('small.q',[('D111011',)]);write('small.bank',[(7,)]);write('small.rows',[(5,0,1),(0,0,1)])


def prepare():
    seed={int(line.split()[3]) for line in (OLD/'pilot0.trace').read_text().splitlines() if ' step ' in line}
    assert len(seed)==125
    bank=set()
    for support in seed:
        assert support.bit_count() in (9,10)
        for reflected in (support,reflection(support,17)):
            shape=reflected//(reflected&-reflected)
            for shift in range(18-shape.bit_length()):bank.add(shape<<shift)
    write('frozen.bank',[(support,) for support in sorted(bank)])
    graph=[[int(left==right or 6<=abs(left-right)<=12) for left in range(17)] for right in range(17)]
    write('core.q',[(encode(graph),)]);assert Path('core.q').read_bytes()==(OLD/'pilot0.q').read_bytes()
    roster=[row for row in read(OLD/'finalpole.rows') if row[1]==0];assert len(set(roster))==len(roster)==7448
    write('target.rows',roster);write('pilot.rows',sorted(roster,key=lambda row:sha256(str(row).encode()).digest())[:128])
    print('seed',len(seed),'interval translation/reflection closure',sorted(Counter(s.bit_count() for s in bank).items()),'frozen digest',sha256(Path('frozen.bank').read_bytes()).hexdigest())


def extend():
    initial=set(read('target.checked'));left=sorted(set(read('target.rows'))-initial);assert len(left)==392
    write('rest.rows',left);write('restpilot.rows',sorted(left,key=lambda row:sha256(str(row).encode()).digest())[:32]);write('wider.bank',[(support,) for support in range(1<<17) if support.bit_count() in (9,10)])
    print('extension: every singleton transversal support of order 9 or 10, no sign assignment; rows',len(left),'digest',sha256(Path('wider.bank').read_bytes()).hexdigest())


def finish(extended=False):
    domain=set(read('target.rows')); before_mark=set(read(OLD/'finalmark.rows'));before_pole=set(read(OLD/'finalpole.rows'))
    rejects=set(read('target.checked'));assert rejects<=domain and len(rejects)==len(read('target.checked'))
    if extended:
        rest=set(read('rest.rows'));assert rest==domain-rejects
        extra=set(read('rest.checked'));assert extra<=rest and len(extra)==len(read('rest.checked'))
        rejects|=extra;print('extended bank additional',len(extra),'open',sorted(rest-extra) if len(rest-extra)<30 else len(rest-extra))
    assert domain=={row for row in before_pole if row[1]==0}
    oldpilot=[line.split() for line in (OLD/'pilot.results').read_text().splitlines()]
    pilotcuts={tuple(map(int,row[:3])) for row in oldpilot if row[3]=='I'}
    prisms={row[:3] for row in read(OLD/'prism.rejects')};premark=set(read(OLD/'wmark.rows'));prepole=set(read(OLD/'wpole.rows'))
    assert before_pole==prepole-prisms-pilotcuts and before_mark==((premark&before_pole)-{(sum(1<<i for i in range(5,12)),0,1)})
    assert not domain&(prisms|pilotcuts)
    print('old no-double census: before, prism, pilot, overlap, new denominator',*[sum(row[1]==0 for row in group) for group in (prepole,prisms,pilotcuts,prisms&pilotcuts,domain)])
    prefix='wide' if extended else ''
    for side,before in [('mark',before_mark),('pole',before_pole)]:
        for tag,rows in [('before',before),('cut',before&rejects),('left',before-rejects)]:
            fixed=sum((reflection(occ,17),reflection(full,17))==(occ,full) for occ,full,_ in rows)
            assert all((occ,full)<=(reflection(occ,17),reflection(full,17)) and weight==1+int((occ,full)!=(reflection(occ,17),reflection(full,17))) for occ,full,weight in rows)
            print(side,tag,'reps/labelled/fixed',len(rows),sum(row[2] for row in rows),fixed,'strata',sorted(Counter(row[1].bit_count() for row in rows).items()))
        write(prefix+side+'.left',sorted(before-rejects))
    adjacency=[sum(1<<col for col in range(17) if 6<=abs(row-col)<=12) for row in range(17)]
    census=count(17,10,adjacency,read(prefix+'mark.left'),read(prefix+'pole.left'));second=reverse_count(prefix+'mark.left',prefix+'pole.left')
    assert second==[census[num,'orbits'] for num in range(3)]
    print('forward labels/fixed/orbits',sorted(census.items()),'total representatives',sum(second),'reduction from 353474849',353474849-sum(second))
    if extended:
        mark=read('widemark.left');poles=read('widepole.left');table=[]
        for left in range(3):
            for right in range(4):
                cell=count(17,10,adjacency,[row for row in mark if row[1].bit_count()==left],[row for row in poles if row[1].bit_count()==right]);table.append((left,right,*[cell[num,'orbits'] for num in range(3)]))
        assert all(sum(row[2+num] for row in table)==second[num] for num in range(3))
        write('doubleprice.tsv',table);print('headers with exactly one double in at least one role',sum(sum(row[2:]) for row in table if 1 in row[:2]))


if __name__=='__main__':{'control':control,'prepare':prepare,'finish':finish,'extend':extend,'final':lambda:finish(True)}[sys.argv[1]]()
