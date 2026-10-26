# Codex r6: case R, some vertex 0 has two codegree-6 partners a=10, b=11 (h6(0)=2). Then N(a), N(b) meet H_0 in disjoint
# 3-sets (else |X|>=23, R(3,7)=23) and X = G - N[{0,a,b}] (22 vertices, alpha<=6) is one of the 191 R(3,7;22) graphs.
# Labels: N(0)=1..9; N(a)&N(0)=1..6; N(b)&N(0)={1..s} + {7..12-s} (s=|N(a)&N(b)&N(0)| in 3..6); N(a)-N(0)=12..14,
# N(b)-N(0)=15..17; X=18..39 fixed. Base: 9-regular, MTF, codeg<=7 (L6), alpha<=9 (lazy).
# Usage: kernel_h6.py x22.g6 outdir timeout workers [first_n_X] [s_list]
import sys, os, time, subprocess, networkx as nx
from multiprocessing import Pool
R='.'; SMSG=R+'/sms/sms-src/build/src/smsg'; n=40
XF,OUT=sys.argv[1],sys.argv[2]; TO=float(sys.argv[3]); W=int(sys.argv[4])
NX=int(sys.argv[5]) if len(sys.argv)>5 else 10**9; SL=[int(x) for x in sys.argv[6].split(',')] if len(sys.argv)>6 else [3,4,5,6]
os.makedirs(OUT,exist_ok=True)
def var(i,j):
    i,j=min(i,j),max(i,j); return i*n-i*(i+1)//2+(j-i)
base=f'{OUT}/base.cnf'
if not os.path.exists(base):
    subprocess.run(['python3',R+'/sms/gen_ramsey.py','-n','40','-k','10','--dmin','9','--dmax','9','--mtf','--codeg-max','7','-o',base],check=True)
hdr,body=open(base).read().split('\n',1); nv,nc=map(int,hdr.split()[2:4])
X=list(range(18,40))
def units(H,s):
    Na=set(range(1,7))|{12,13,14}; Nb=set(range(1,s+1))|set(range(7,13-s))|{15,16,17}
    U=[]
    for w in range(1,40): U.append(var(0,w) if w<=9 else -var(0,w))
    for w in range(40):
        if w!=10: U.append(var(10,w) if w in Na else -var(10,w))
        if w not in (10,11): U.append(var(11,w) if w in Nb else -var(11,w))
    for i in range(22):
        for j in range(i+1,22): U.append(var(X[i],X[j]) if H.has_edge(i,j) else -var(X[i],X[j]))
    return U
def cells(s):
    c=[1,s,6-s,6-s,s-3,1,1,3,3]+[1]*22
    return [str(x) for x in c if x>0]
def run(arg):
    idx,s,line=arg; U=units(nx.from_graph6_bytes(line.encode()),s); cnf=f'{OUT}/h{idx}_{s}.cnf'
    with open(cnf,'w') as f: f.write(f'p cnf {nv} {nc+len(U)}\n'); f.write(body); f.write(''.join(f'{u} 0\n' for u in U))
    t=time.time()
    try:
        p=subprocess.run([SMSG,'-v','40','--dimacs',cnf,'--forbid-independent-set','10','--cutoff','0','--initial-partition',*cells(s)],capture_output=True,text=True,timeout=TO)
        sols=[l for l in p.stdout.splitlines() if l.startswith('[(')]; st=f'rc={p.returncode} sols={len(sols)}'
    except subprocess.TimeoutExpired as e:
        out=e.stdout.decode() if isinstance(e.stdout,bytes) else (e.stdout or ''); sols=[l for l in out.splitlines() if l.startswith('[(')]; st=f'TIMEOUT sols={len(sols)}'
    os.remove(cnf)
    if sols: open(f'{OUT}/h{idx}_{s}.sol','w').write('\n'.join(sols)+'\n')
    return idx,s,st,time.time()-t
if __name__=='__main__':
    L=[l.strip() for l in open(XF) if l.strip()][:NX]
    with Pool(W) as P, open(f'{OUT}/res.txt','a') as R_:
        for idx,s,st,dt in P.imap_unordered(run,[(i,s,l) for i,l in enumerate(L) for s in SL]):
            R_.write(f'{idx} {s} {st} {dt:.1f}\n'); R_.flush()
    print('done',flush=True)
