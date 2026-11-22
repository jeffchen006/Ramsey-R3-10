from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import subprocess
import sys

from marked_joint import count, read, reflection
from marked_replay import reverse_count
from orbit_extend import ROOT, to_graph6
from one_double_check import edges_for, verify

BASE=ROOT/'scratch/F/r18'
SMALL=['c3_'+str(number) for number in range(8)]+['c4_45']


def write(name,rows):Path(name).write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))


def bank(tag):
    size,goal,edges=edges_for(tag);sides=set(edges)
    text=chr(65+size)+''.join(str(int(left==right or (left,right) in sides)) for right in range(size) for left in range(right+1))
    write(tag+'.q',[(text,)]);write(tag+'.bank',[(mask,) for mask in range(1<<size) if goal-2<=mask.bit_count()<=goal])


def prepare_small():
    for tag in SMALL:
        bank(tag);size=edges_for(tag)[0];write(tag+'.rows',[(occ,1<<site,1) for site in range(size) for occ in range(1<<size) if occ>>site&1])


def pilot():
    bank('pilot');assert Path('pilot.q').read_bytes()==(BASE/'core.q').read_bytes()
    poles=set(read(BASE/'widepole.left'));marks=set(read(BASE/'widemark.left'));domain=sorted(row for row in poles if row[1].bit_count()==1)
    assert len(domain)==3709 and len(set(domain)&marks)==1050 and marks<=poles
    strata=defaultdict(list)
    def key(row):return sha256(('F19:'+','.join(map(str,row))).encode()).digest()
    for row in domain:
        occ,full,weight=row
        assert full&occ==full and (occ,full)<=(reflection(occ,17),reflection(full,17))
        assert weight==1+int((occ,full)!=(reflection(occ,17),reflection(full,17)))
        strata[full.bit_length(),int(weight==1),occ.bit_count()+1,int(row in marks)].append(row)
    chosen=sorted((min(bucket,key=key) for bucket in strata.values()),key=key);assert len(chosen)==117
    remaining=set(domain)-set(chosen);chosen+=sorted(remaining,key=key)[:128-len(chosen)]
    assert len(set(chosen))==len(chosen)==128
    write('pilot.rows',chosen);write('strata.tsv',[(*bucket,len(rows),len(set(chosen)&set(rows))) for bucket,rows in sorted(strata.items())]);write('unexamined.rows',sorted(set(domain)-set(chosen)))
    for file in ['pilot.q','pilot.bank','pilot.rows','strata.tsv','unexamined.rows']:
        print(sha256(Path(file).read_bytes()).hexdigest(),file)


def tri_free(graph):return not any(graph[left]>>right&1 and graph[left]&graph[right] for right in range(len(graph)) for left in range(right))


def graph_build(size,edges,sign,verts,ends):
    graph=[0]*(2*size+2)
    def edge(left,right):graph[left]|=1<<right;graph[right]|=1<<left
    for site in range(size+1):
        if verts>>site&1:edge(2*site,2*site+1)
    for serial,(left,right) in enumerate(edges):
        for bit in (0,1):edge(2*left+bit,2*right+(bit^(sign>>serial&1)))
    for site,pair in enumerate(ends):
        for bit in (0,1):
            if pair>>bit&1:edge(2*site+bit,2*size);edge(2*site+(bit^1),2*size+1)
    return graph


def valid(graph):
    if not tri_free(graph):return False
    for left in range(len(graph)):
        for right in range(left+1,len(graph)):
            if graph[left]>>right&1:continue
            avail=((1<<len(graph))-(2<<right))&~(graph[left]|graph[right])
            while avail:
                bit=avail&-avail;avail^=bit
                if avail&~graph[bit.bit_length()-1]:return False
    return True


def calibration():
    combined=Counter()
    for tag in SMALL:
        cuts=set(verify(tag));size,_target,edges=edges_for(tag);stats=Counter();quot=1<<(size*2+1)
        for ends in product(range(4),repeat=size):
            if ends.count(3)!=1:continue
            row=sum(1<<idx for idx,pair in enumerate(ends) if pair),1<<ends.index(3),1
            for sign in range(1<<len(edges)):
                for verts in range(1<<(size+1)):
                    graph=graph_build(size,edges,sign,verts,ends)
                    if verts>>size&1==0:
                        good=valid([neighbors&(quot-1) for neighbors in graph[:-1]])
                        assert not(good and row in cuts);stats['exterior',good]+=1
                    good=valid(graph);assert not(good and row in cuts);stats['marked',good]+=1
        print(tag,sorted(stats.items()));combined.update(stats)
    print('all literal physical small classifications',sorted(combined.items()))
    labels=[1,4,2,3,7,6,0,5];known=[sum(1<<idx for idx,other in enumerate(labels) if (other-label)%8 in (1,4,7)) for label in labels]
    assert valid(known);Path('positive.g6').write_text(to_graph6(known)+'\n');gate=json.loads(subprocess.check_output([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check','positive.g6','8','4']))
    assert gate['graphs'][0]['ok'];Path('positive.gate').write_text(json.dumps(gate,sort_keys=True)+'\n')
    assert all(known[idx]&63==mask for idx,mask in [(6,19),(7,35)])
    size,_target,edges=edges_for('c3_5');assert any(graph_build(size,edges,sign,verts,(3,0,1))==known for sign in range(4) for verts in range(16))
    assert (5,1,1) not in set(read('c3_5.checked'));print('known marked C8(1,4), both pole contacts',known[6]&63,known[7]&63,'positive under literal and gate checks')


def tamper():
    tag='c3_5';original=Path(tag+'.trace').read_text();header='begin 5 1 5 1\n'
    assert header in original
    for name,wrong in [('drop first double endpoint','begin 5 1 4 1\n'),('drop second double endpoint','begin 5 1 5 0\n'),('wrong physical site','begin 5 4 5 4\n'),('pole uses doubled site',header+'step 1 7 4 0\n'),('restore next to matching',header+'step 2 6 0 0\n')]:
        try:verify(tag,original.replace(header,wrong),False)
        except AssertionError:print('rejected:',name)
        else:raise AssertionError('forgery accepted: '+name)


def price():
    pilotrows=set(read('pilot.rows'));cuts=set(read('pilot.checked'));assert cuts<=pilotrows
    marks=set(read(BASE/'widemark.left'));poles=set(read(BASE/'widepole.left'));assert len(marks)==1327 and len(poles)==4411 and marks<=poles
    strata=defaultdict(list)
    for row in pilotrows:
        occ,full,weight=row;strata[full.bit_length(),int(weight==1),occ.bit_count()+1,int(row in marks)].append(row)
    write('outcomes.tsv',[(*key,len(rows),len(set(rows)&cuts)) for key,rows in sorted(strata.items())]);print('roles: all and marked subset')
    for title,rows in [('pole',poles),('mark',marks)]:
        for tag,bucket in [('pilot',rows&pilotrows),('cut',rows&cuts),('remaining',rows-cuts)]:
            print(title,tag,'reps labels fixed',len(bucket),sum(row[2] for row in bucket),sum(row[2]==1 for row in bucket))
        write(title+'.left',sorted(rows-cuts))
    adj=[sum(1<<col for col in range(17) if 6<=abs(col-site)<=12) for site in range(17)]
    old=count(17,10,adj,marks,poles);new=count(17,10,adj,marks-cuts,poles-cuts);bits=reverse_count('mark.left','pole.left');assert bits==[new[num,'orbits'] for num in range(3)]
    assert sum(old[num,'orbits'] for num in range(3))==16182483
    print('old',sorted(old.items()),'new',sorted(new.items()),'delta',sorted((old-new).items()));print('joint remaining',sum(bits),'simultaneous orbits cut',16182483-sum(bits))
    write('joint.tsv',[(num,*[counts[num,tag] for counts in (old,new) for tag in ('labels','fixed','orbits')]) for num in range(3)])
    for mult in range(3):assert all(2*counts[mult,'orbits']==counts[mult,'labels']+counts[mult,'fixed'] for counts in (old,new))
    parts=[count(17,10,adj,marks&cuts,poles),count(17,10,adj,marks,poles&cuts),count(17,10,adj,marks&cuts,poles&cuts)]
    assert all(old[key]-new[key]==parts[0][key]+parts[1][key]-parts[2][key] for key in old)
    print('joint impact from marked, exterior and overlap',[sum(part[num,'orbits'] for num in range(3)) for part in parts])


def estimate():
    calls={tuple(map(int,line.split()[:2])):float(line.split()[2]) for line in Path('pilotrun.stdout').read_text().splitlines()}
    probes=read('pilot.rows');marks=set(read(BASE/'widemark.left'));sizes={row[:4]:row[4] for row in read('strata.tsv')}
    by=defaultdict(list)
    for occ,full,weight in probes:by[full.bit_length(),int(weight==1),occ.bit_count()+1,int((occ,full,weight) in marks)].append(calls[occ,full])
    assert sum(sizes.values())==3709 and sizes.keys()==by.keys() and len(calls)==128
    measure=sum(sizes[key]*sum(values)/len(values) for key,values in by.items());print('stratum-weighted CPU-s rows only for all 3709',round(measure,3),'measured sample',round(sum(calls.values()),4),'max',max(calls.values()))
    print('unexamined 3581 row variable CPU-s estimate',round(measure-sum(calls.values()),3),'3709 times max observed (not a bound)',round(3709*max(calls.values()),2))


def adverse():
    text=Path('pilot.trace').read_text();first=next(line for line in text.splitlines() if line.startswith('step 1 ') and int(line.split()[3]))
    sign=next(line for line in text.splitlines() if line.startswith('step ') and int(line.split()[4])>0)
    for label,prior,index in [('physical survivor pin',first,3),('flipped affine residual',sign,4)]:
        words=prior.split();words[index]=str(int(words[index])^1);forged=text.replace(prior,' '.join(words),1)
        try:verify('pilot',forged,False)
        except AssertionError:print('rejected target mutation:',label)
        else:raise AssertionError('forged target step accepted: '+label)


if __name__=='__main__':{'small':prepare_small,'pilot':pilot,'calibrate':calibration,'tamper':tamper,'price':price,'estimate':estimate,'adverse':adverse}[sys.argv[1]]()
