# Codex r5, (35,8) codegree-5 branch: u=0,v=1 non-adjacent, C=2..6 common nbrs, A'=7..9, B'=10..12,
# X=13..34 = G - N[u] - N[v] fixed to a (3,7,22)-graph with 60/61 edges (e(X)=52+e(A',B'), e(3,7,22)=60 [GR Table 12]).
# Base: gen_ramsey -n 35 -k 9 --dmin 8 --dmax 8 --mtf --codeg-max 5. SMS cells: 1 1 5 3 3 + 22 singletons.
# Usage: kernel_x.py x.g6 outdir timeout_s workers   (reuses kernel_run's res.txt format)
import sys, os, time, subprocess, networkx as nx
from multiprocessing import Pool
R='.'; SMSG=R+'/sms/sms-src/build/src/smsg'
n,k=35,9; XF,OUT=sys.argv[1],sys.argv[2]; TO=float(sys.argv[3]); W=int(sys.argv[4]); os.makedirs(OUT,exist_ok=True)
def var(i,j):
    i,j=min(i,j),max(i,j); return i*n-i*(i+1)//2+(j-i)
base=f'{OUT}/base.cnf'
if not os.path.exists(base):
    subprocess.run(['python3',R+'/sms/gen_ramsey.py','-n','35','-k','9','--dmin','8','--dmax','8','--mtf','--codeg-max','5','-o',base],check=True)
hdr,body=open(base).read().split('\n',1); nv,nc=map(int,hdr.split()[2:4])
C=range(2,7); A=range(7,10); B=range(10,13); X=list(range(13,35))
def units(H):
    U=[-var(0,1)]
    for w in range(2,35):
        U.append(var(0,w) if w in C or w in A else -var(0,w)); U.append(var(1,w) if w in C or w in B else -var(1,w))
    for i in range(22):
        for j in range(i+1,22): U.append(var(X[i],X[j]) if H.has_edge(i,j) else -var(X[i],X[j]))
    return U
def run(arg):
    idx,line=arg; U=units(nx.from_graph6_bytes(line.encode())); cnf=f'{OUT}/x{idx}.cnf'
    with open(cnf,'w') as f: f.write(f'p cnf {nv} {nc+len(U)}\n'); f.write(body); f.write(''.join(f'{u} 0\n' for u in U))
    t=time.time()
    try:
        p=subprocess.run([SMSG,'-v','35','--dimacs',cnf,'--forbid-independent-set','9','--cutoff','0','--initial-partition',*'1 1 5 3 3'.split(),*['1']*22],capture_output=True,text=True,timeout=TO)
        sols=[l for l in p.stdout.splitlines() if l.startswith('[(')]; st=f'rc={p.returncode} sols={len(sols)}'
    except subprocess.TimeoutExpired as e:
        out=e.stdout.decode() if isinstance(e.stdout,bytes) else (e.stdout or ''); sols=[l for l in out.splitlines() if l.startswith('[(')]; st=f'TIMEOUT sols={len(sols)}'
    os.remove(cnf)
    if sols: open(f'{OUT}/x{idx}.sol','w').write('\n'.join(sols)+'\n')
    return idx,line,st,time.time()-t
if __name__=='__main__':
    L=[l.strip() for l in open(XF) if l.strip()]
    with Pool(W) as P, open(f'{OUT}/res.txt','a') as R_:
        for idx,line,st,dt in P.imap_unordered(run,list(enumerate(L))):
            R_.write(f'{idx} {line} {st} {dt:.1f}\n'); R_.flush()
    print('done',flush=True)
