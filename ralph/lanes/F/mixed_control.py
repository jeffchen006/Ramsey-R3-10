"""Independent direct mixed-cycle calibration from physical 10-vertex lifts."""

from itertools import combinations,product,repeat
from pathlib import Path

from relift_audit import explicit_lift,encode,decode,pairs,walk_score,independent
from block_audit import support_total


def run():
    size=5;rot=[1,0,3,2,4];slots={};where={};domains=[]
    for left,right in pairs(size):
        key=min((left,right),tuple(sorted((rot[left],rot[right]))))
        if key not in slots: slots[key]=len(domains);domains.append(range(2+(left!=right)))
        where[left,right]=where[right,left]=slots[key]
    result={}
    for weights in product(*domains):
        base=[[weights[where[left,right]] for right in range(size)] for left in range(size)]
        graph=explicit_lift(base,repeat(1))
        if not all(row.bit_count()==3 and independent(row,graph) for row in graph): continue
        count=sum(base[left][right]==1 for left,right in combinations(range(size),2));scores=[]
        for signs in product(range(2),repeat=count):
            graph=explicit_lift(base,iter(signs))
            if all(independent(row,graph) for row in graph):scores.append(walk_score(graph,5))
        result[encode(base)]=min(scores)
    reached=set();rows=Path('small.rows').read_text().splitlines();status=Path('small.sat').read_text().splitlines();bounds=Path('small.fcert').read_text().splitlines();assert len(rows)==len(status)==len(bounds)
    for index,(line,log,bound) in enumerate(zip(rows,status,bounds)):
        raw,mult,text=line.split();assert int(raw)==index;matrix=decode(text);orbit=set()
        for first,second in product(range(2),repeat=2):
            perm=[first,1-first,2+second,3-second,4];orbit.add(encode([[matrix[left][right] for right in perm] for left in perm]))
        assert orbit<=set(result)
        reached.update(orbit);logical=int(log.split()[0]);assert logical==index and log.split()[1]==('yes' if result[text]==0 else 'no')
        ident,*entries=bound.split();assert int(ident)==index and support_total(matrix,5,entries)<=result[text]
    assert reached==set(result) and len(reached)==sum(int(row.split()[1]) for row in rows)
    wheel=[[0]*5 for _ in range(5)]
    for vertex in range(4):
        for other in ((vertex+1)%4,4):wheel[vertex][other]=wheel[other][vertex]=1
    assert support_total(wheel,4,['0:15:2'])==2
    wheel[0][4]=wheel[4][0]=0
    try: support_total(wheel,4,['0:15:2'])
    except AssertionError: pass
    else: raise RuntimeError('rank-blind square accepted')
    print('PASS',len(result),'raw labelled cubic quotients;',len(rows),'rows; exact minima',sorted(set(result.values())),';',sum(line.split()[1]=='yes' for line in status),'positive rows; broken triangle-span dependency rejected')


if __name__=='__main__':run()
