import json,sys
n=14; data=json.load(open('../sms/proofs/r3_5_14_lazy.sym.json'))['sym_clauses']
pos=[(i,j) for i in range(n) for j in range(i+1,n)]
def test(lits,pmap,better):
    alpha={(i,j):(0 if sg>0 else 1) for sg,i,j in lits}
    for (i,j) in pos:
        a,b=pmap[i],pmap[j]; q=(min(a,b),max(a,b))   # H'(p) = H(q)
        if q==(i,j): continue
        x,y=alpha.get((i,j)),alpha.get(q)
        if x is None or y is None: return False
        if x==y: continue
        return (y>x) if better=='max' else (y<x)
    return False
for mode in ['perm','inv']:
    for better in ['max','min']:
        ok=0
        for lits,perm in data:
            pm=perm if mode=='perm' else [perm.index(v) for v in range(n)]
            ok+=test(lits,pm,better)
        print(mode,better,ok,len(data))
def trace(lits,pmap):
    alpha={(i,j):(0 if sg>0 else 1) for sg,i,j in lits}
    out=[]
    for (i,j) in pos:
        a,b=pmap[i],pmap[j]; q=(min(a,b),max(a,b))
        if q==(i,j): continue
        x,y=alpha.get((i,j)),alpha.get(q)
        out.append(((i,j),x,q,y))
        if x is None or y is None or x!=y: break
    return out
for lits,perm in data:
    if not test(lits,perm,'min'): print(lits,perm); print(trace(lits,perm))
