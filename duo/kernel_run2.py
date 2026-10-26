# Corrected edge-kernel runner (fixes of kernel_run.py from the desktop lead's review, codex_strategy_3.md Sec 1):
#  - smsg -a (--all-graphs): enumerate ALL completions per kernel (kernel_run.py found only the first);
#  - resume: only finished (non-TIMEOUT) kernels count as done;
#  - optional kernel-automorphism symmetry breaking (--aut): for sigma in Aut(kernel) (u,v,A,B,F; rest fixed pointwise),
#    static lex-leader clauses x <=lex x o sigma over the SMS order (lex-MIN of the row-wise edge vector, var 1..m;
#    notes/cert_design.md 1.3). Valid with SMS's dynamic check over the free cell: the orbit-min graph under
#    <Aut(kernel), Sym(rest)> satisfies both. Truncation to the first L moved positions and a subset of sigma stay valid.
# Kernel: u=0, v=1, A=2..d, B=d+1..2d-1 (genbg class1 -> A, class2 -> B), rest 2d..n-1 (one SMS cell).
# Usage: kernel_run2.py n d k M kernels.g6 outdir timeout workers aut(0/1) [cap=300] [L=400]
import sys, os, time, subprocess, networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from multiprocessing import Pool
R='.'; SMSG=R+'/sms/sms-src/build/src/smsg'
n,d,k,M=map(int,sys.argv[1:5]); KF,OUT=sys.argv[5],sys.argv[6]; TO=float(sys.argv[7]); W=int(sys.argv[8]); AUT=int(sys.argv[9])
CAP=int(sys.argv[10]) if len(sys.argv)>10 else 300; LL=int(sys.argv[11]) if len(sys.argv)>11 else 400
os.makedirs(OUT,exist_ok=True)
def var(i,j):
    i,j=min(i,j),max(i,j); return i*n-i*(i+1)//2+(j-i)
base=f'{OUT}/base.cnf'
if not os.path.exists(base):
    subprocess.run(['python3',R+'/sms/gen_ramsey.py','-n',str(n),'-k',str(k),'--dmin',str(d),'--dmax',str(d),'--mtf','--codeg-max',str(M),'-o',base],check=True)
hdr,body=open(base).read().split('\n',1); nv,nc=map(int,hdr.split()[2:4])
A=list(range(2,d+1)); B=list(range(d+1,2*d)); X=list(range(2*d,n))
POS=[(i,j) for i in range(n) for j in range(i+1,n)]   # SMS order = var order
def kernel(F):
    E={(0,1)}|{(0,a) for a in A}|{(1,b) for b in B}|{(A[i],B[j-(d-1)]) for i,j in F.edges()}
    N={(0,b) for b in B}|{(1,a) for a in A}|{(0,x) for x in X}|{(1,x) for x in X}|{(a,b) for a in A for b in B if (a,b) not in E}
    return E,N
def symclauses(E,nvar):
    K=nx.Graph(); K.add_nodes_from(range(2*d)); K.add_edges_from(E)
    C=[]; cnt=0
    for m in GraphMatcher(K,K).isomorphisms_iter():
        if all(m[i]==i for i in m): continue
        cnt+=1
        if cnt>CAP: break
        s=lambda x: m.get(x,x)
        prev=None; L=0
        for (i,j) in POS:
            p=var(i,j); q=var(s(i),s(j))
            if p==q: continue
            L+=1
            if L>LL: break
            # x_p <= y_p while equal so far (y_p = x_q): clause (-eq_prev v -x_p v x_q)
            pre=[] if prev is None else [-prev]
            C.append(pre+[-p,q])
            nvar+=1; e=nvar   # eq so far after this position: prev & (x_p == x_q) -> e
            C.append(pre+[p,q,e]); C.append(pre+[-p,-q,e])
            prev=e
    return C,nvar,cnt
def cells(): return [str(x) for x in [1]*(2*d)+[n-2*d]]
def run(arg):
    idx,line=arg; F=nx.from_graph6_bytes(line.encode()); E,N=kernel(F)
    U=[[var(*e)] for e in E]+[[-var(*e)] for e in N]; nvar=nv; S=[]; na=0
    if AUT: S,nvar,na=symclauses(E,nvar)
    cnf=f'{OUT}/k{idx}.cnf'
    with open(cnf,'w') as f:
        f.write(f'p cnf {nvar} {nc+len(U)+len(S)}\n'); f.write(body)
        f.write(''.join(' '.join(map(str,c))+' 0\n' for c in U+S))
    t=time.time()
    try:
        p=subprocess.run([SMSG,'-v',str(n),'--dimacs',cnf,'--forbid-independent-set',str(k),'--cutoff','0','-a','--initial-partition',*cells()],capture_output=True,text=True,timeout=TO)
        sols=[l for l in p.stdout.splitlines() if l.startswith('[(')]; st=f'rc={p.returncode} sols={len(sols)}'
    except subprocess.TimeoutExpired as e:
        out=e.stdout.decode() if isinstance(e.stdout,bytes) else (e.stdout or ''); sols=[l for l in out.splitlines() if l.startswith('[(')]; st=f'TIMEOUT sols={len(sols)}'
    os.remove(cnf)
    if sols: open(f'{OUT}/k{idx}.sol','w').write('\n'.join(sols)+'\n')
    return idx,line,st,time.time()-t,na
if __name__=='__main__':
    L=[l.strip() for l in open(KF) if l.strip()]
    done=set()
    if os.path.exists(f'{OUT}/res.txt'): done={int(l.split()[0]) for l in open(f'{OUT}/res.txt') if 'TIMEOUT' not in l}
    todo=[(i,l) for i,l in enumerate(L) if i not in done]
    print('kernels',len(L),'todo',len(todo),'aut',AUT,flush=True)
    with Pool(W) as P, open(f'{OUT}/res.txt','a') as R_:
        for idx,line,st,dt,na in P.imap_unordered(run,todo):
            R_.write(f'{idx} {line} {st} {dt:.1f} aut={na}\n'); R_.flush()
    print('done',flush=True)
