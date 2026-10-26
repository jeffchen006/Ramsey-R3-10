# For all graphs on n vertices: does the colex-lex-MIN labelling (MathCheck CAS canonical form)
# satisfy MathCheck's static "cubic" constraints row_i <=lex row_j (cols except i,j) for all i<j?
import itertools, sys
n=int(sys.argv[1])
pairs_colex=[(i,j) for j in range(n) for i in range(j)]
perms=list(itertools.permutations(range(n)))
def cubic_ok(A):
    for i in range(n):
        for j in range(i+1,n):
            ri=[A[i][c] for c in range(n) if c not in (i,j)]
            rj=[A[j][c] for c in range(n) if c not in (i,j)]
            if ri>rj: return False
    return True
seen=set(); bad=0; classes=0; ex=None
for mask in range(1<<len(pairs_colex)):
    E=[pairs_colex[k] for k in range(len(pairs_colex)) if mask>>k&1]
    best=None
    for p in perms:
        v=tuple(sorted(((min(p[a],p[b]),max(p[a],p[b])) for a,b in E)))
        vec=tuple(1 if pr in set(v) else 0 for pr in pairs_colex)
        if best is None or vec<best: best=vec
    if best in seen: continue
    seen.add(best); classes+=1
    A=[[0]*n for _ in range(n)]
    for k,pr in enumerate(pairs_colex):
        if best[k]: A[pr[0]][pr[1]]=A[pr[1]][pr[0]]=1
    if not cubic_ok(A):
        bad+=1
        if ex is None: ex=[pr for k,pr in enumerate(pairs_colex) if best[k]]
print("n=%d classes=%d colex-lexmin forms violating cubic: %d  example edges %s"%(n,classes,bad,ex))
