import random, itertools, sys
sys.path.insert(0,'./critic/src')
from gen_tests import g6, gnp
rnd=random.Random(11); out=[]; exp=[]
for _ in range(1500):
    n=rnd.randint(1,15); E=gnp(rnd,n,rnd.choice([0.1,0.3,0.5,0.7])); Es=set(E)
    adj=lambda a,b:(min(a,b),max(a,b)) in Es
    al=max((s for s in range(n+1) for S in [next((S for S in itertools.combinations(range(n),s) if all(not adj(a,b) for a,b in itertools.combinations(S,2))),None)] if S is not None),default=0)
    tf=int(not any(adj(a,b) and adj(b,c) and adj(a,c) for a,b,c in itertools.combinations(range(n),3)))
    out.append(g6(n,E)); exp.append((n,len(E),tf,al))
open(sys.argv[1],'w').write('\n'.join(out)+'\n'); open(sys.argv[2],'w').write('\n'.join('%d %d %d %d'%x for x in exp)+'\n')
