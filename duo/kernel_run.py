# Codex r5 method 1: edge-kernel split of d-regular (3,k,n), then SMS completion per kernel.
# Kernel: u=0, v=1, A=N(u)-v = 2..d, B=N(v)-u = d+1..2d-1, F=G[A,B] from genbg (class1 -> A, class2 -> B).
# Base CNF: gen_ramsey -n n -k k --dmin d --dmax d --mtf --codeg-max M; kernel adds unit clauses.
# SMS partition: 2d singletons + one cell of n-2d (kernel labels fixed, rest permutable).
# Usage: kernel_run.py n d k M kernels.g6 outdir timeout_s workers
import sys, os, time, subprocess, networkx as nx
from multiprocessing import Pool
R='.'; SMSG=R+'/sms/sms-src/build/src/smsg'
n,d,k,M=map(int,sys.argv[1:5]); KF,OUT=sys.argv[5],sys.argv[6]; TO=float(sys.argv[7]); W=int(sys.argv[8])
os.makedirs(OUT,exist_ok=True)
def var(i,j):
    i,j=min(i,j),max(i,j); return i*n-i*(i+1)//2+(j-i)
base=f'{OUT}/base.cnf'
if not os.path.exists(base):
    subprocess.run(['python3',R+'/sms/gen_ramsey.py','-n',str(n),'-k',str(k),'--dmin',str(d),'--dmax',str(d),'--mtf','--codeg-max',str(M),'-o',base],check=True)
hdr,body=open(base).read().split('\n',1); nv,nc=map(int,hdr.split()[2:4])
A=list(range(2,d+1)); B=list(range(d+1,2*d)); X=list(range(2*d,n))
def units(F):
    E={(0,1)}|{(0,a) for a in A}|{(1,b) for b in B}|{(A[i],B[j-(d-1)]) for i,j in F.edges()}
    N={(0,b) for b in B}|{(1,a) for a in A}|{(0,x) for x in X}|{(1,x) for x in X}|{(a,b) for a in A for b in B if (a,b) not in E}
    return [var(*e) for e in E]+[-var(*e) for e in N]
def run(arg):
    idx,line=arg; F=nx.from_graph6_bytes(line.encode()); U=units(F)
    cnf=f'{OUT}/k{idx}.cnf'
    with open(cnf,'w') as f: f.write(f'p cnf {nv} {nc+len(U)}\n'); f.write(body); f.write(''.join(f'{u} 0\n' for u in U))
    cells=' '.join(['1']*(2*d)+[str(n-2*d)])
    t=time.time()
    try:
        p=subprocess.run([SMSG,'-v',str(n),'--dimacs',cnf,'--forbid-independent-set',str(k),'--cutoff','0','--initial-partition',*cells.split()],capture_output=True,text=True,timeout=TO)
        sols=[l for l in p.stdout.splitlines() if l.startswith('[(')]; st=f'rc={p.returncode} sols={len(sols)}'
    except subprocess.TimeoutExpired as e:
        out=e.stdout.decode() if isinstance(e.stdout,bytes) else (e.stdout or ''); sols=[l for l in out.splitlines() if l.startswith('[(')]; st=f'TIMEOUT sols={len(sols)}'
    os.remove(cnf)
    if sols: open(f'{OUT}/k{idx}.sol','w').write('\n'.join(sols)+'\n')
    return idx,line,st,time.time()-t
if __name__=='__main__':
    L=[l.strip() for l in open(KF) if l.strip()]
    done=set()
    if os.path.exists(f'{OUT}/res.txt'): done={int(l.split()[0]) for l in open(f'{OUT}/res.txt')}
    todo=[(i,l) for i,l in enumerate(L) if i not in done]
    print('kernels',len(L),'todo',len(todo),flush=True)
    with Pool(W) as P, open(f'{OUT}/res.txt','a') as R_:
        for idx,line,st,dt in P.imap_unordered(run,todo):
            R_.write(f'{idx} {line} {st} {dt:.1f}\n'); R_.flush()
    print('done',flush=True)
