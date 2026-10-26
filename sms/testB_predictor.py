import re, itertools, math, sys
n=36; E={}; k=0
for i in range(n):
    for j in range(i+1,n): k+=1; E[(i,j)]=k
NE=k; tri=[(E[a,b],E[a,c],E[b,c]) for a,b,c in itertools.combinations(range(n),3)]
def feats(lits):
    s={int(x) for x in lits if abs(int(x))<=NE}
    val={abs(x):(x>0) for x in s}
    free=NE-len(val); nbin=0; ntrue=sum(val.values())
    for t in tri:
        v=[val.get(e) for e in t]
        if v.count(True)==1 and v.count(None)==2: nbin+=1
    # free vertex pairs: vertices whose rows are fully assigned
    return free,nbin,ntrue
def rank(x):
    o=sorted(range(len(x)),key=lambda i:x[i]); r=[0]*len(x)
    for p,i in enumerate(o): r[i]=p
    return r
def sp(x,y):
    rx,ry=rank(x),rank(y); m=len(x); mx=sum(rx)/m; my=sum(ry)/m
    c=sum((a-mx)*(b-my) for a,b in zip(rx,ry)); return c/math.sqrt(sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))
def run(cf,times,name):
    cubes=[l.split()[1:-1] for l in open(cf) if l.startswith("a ")]
    F=[feats(c) for c in cubes]; t=times[:len(F)]
    print(f"{name}: {len(F)} cubes, total {sum(t):.0f}s, max {max(t):.0f}s, median {sorted(t)[len(t)//2]:.2f}s")
    for i,nm in enumerate(["free_edges","binary_tri","true_edges"]):
        print(f"  spearman({nm}, time) = {sp([f[i] for f in F],t):+.2f}")
    # top-5% by predictor (#free edges) vs top-5% by time
    for i,nm in [(0,"free_edges"),(1,"binary_tri")]:
        q=max(1,len(F)//20); top=sorted(range(len(F)),key=lambda j:-F[j][i])[:q]
        print(f"  top {q} by {nm}: hold {sum(t[j] for j in top)/sum(t):.0%} of time; hardest cube in it: {max(range(len(t)),key=lambda j:t[j]) in top}")
tl=[float(re.search(r"Time for cube ([\d.]+)",l).group(1)) for l in open("../runs/sms/cubes_r936_L250.txt") if "Time for cube" in l]
run("cubes/r936_L250.cubes",tl,"L250")
ts=[float(x) for x in re.findall(r"Time for cube ([\d.]+)",open("../runs/sms/cubesolve_r936_S160.log").read())]
run("cubes/r936_S160.cubes",ts,"S160")
for cf,t,name in [("cubes/r936_L250.cubes",tl,"L250"),("cubes/r936_S160.cubes",ts,"S160")]:
    F=[feats(l.split()[1:-1]) for l in open(cf) if l.startswith("a ")]
    h=max(range(len(t)),key=lambda j:t[j]); r=sorted(range(len(F)),key=lambda j:F[j][2]).index(h)
    for frac in (0.05,0.2):
        q=max(1,int(len(F)*frac)); top=sorted(range(len(F)),key=lambda j:F[j][2])[:q]
        print(f"{name} fewest-true-edges {frac:.0%} ({q}): hold {sum(t[j] for j in top)/sum(t):.0%} of time; hardest cube rank {r+1}/{len(F)}")
