# exact labelled counts per edge level from countg --ea output: L(e) = sum n!/|Aut|
import sys, math, subprocess
from collections import defaultdict
fn=sys.argv[1]; n=int(sys.argv[2])
out=subprocess.run(['../tools/bin/countg','-q','--ea','-1',fn],capture_output=True,text=True).stdout
L=defaultdict(float); I=defaultdict(int)
for line in out.split('\n'):
    if not line.strip(): continue
    e,a,c=map(int,line.split()); L[e]+=c*math.factorial(n)/a; I[e]+=c
es=sorted(L)
for e in es:
    r = L[e]/L[e-1] if e-1 in L else float('nan')
    ri = I[e]/I[e-1] if e-1 in I else float('nan')
    print(e, I[e], f"L={L[e]:.6g}", f"lab.ratio {r:.4f}", f"iso ratio {ri:.4f}", f"lnL-lnL0 {math.log(L[e]/L[es[0]]):.3f}", f"L/n! {L[e]/math.factorial(n):.1f}")
