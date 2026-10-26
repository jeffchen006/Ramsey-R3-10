import sys, random, subprocess, time
sys.path.insert(0,'./cert'); import sb, mtf
n=40; K=int(sys.argv[1]); random.seed(5); d=8
M=mtf.MTF(n,"colex",781)
S={}
while len(S)<K:
    G={(i,j) for i in range(n) for j in range(i+1,n) if random.random()<0.22}
    pi=list(range(n)); a=list(range(1,d+1)); b=list(range(d+1,n)); random.shuffle(a); random.shuffle(b); pi=[0]+a+b
    c=sb.lex_clause(n,G,pi)
    if c: S.setdefault(tuple(c),pi)
inp=[l for l in open('demo/cubes40/cube_S8.opb') if not l.startswith('*')]
ncl=len(inp)
open('scratch/c40_in.opb','w').write('* #variable= %d #constraint= %d\n'%(M.nvars,ncl)+''.join(inp))
out=inp+[sb.opb_clause(list(c))+' ;\n' for c in S]
open('scratch/c40_out.opb','w').write('* #variable= %d #constraint= %d\n'%(M.nvars,len(out))+''.join(out))
sb.write_veripb('scratch/c40.pbp',n,ncl,[(list(c),p) for c,p in S.items()],aux_witness=M.aux_witness)
t=time.time(); r=subprocess.run(['./tools/bin/veripb','scratch/c40_in.opb','scratch/c40.pbp','scratch/c40_out.opb'],capture_output=True,text=True)
print(K,'clauses; VeriPB',[l for l in r.stdout.splitlines() if l.startswith('s ')], (r.stdout+r.stderr)[-300:] if 'VERIFIED OUTPUT' not in r.stdout else '', '%.1f s'%(time.time()-t))
