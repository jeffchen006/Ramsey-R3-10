import sys, random, time
sys.path.insert(0,'./cert'); import sb
n=40; K=int(sys.argv[1]); random.seed(1)
S={}
while len(S)<K:
    G={(i,j) for i in range(n) for j in range(i+1,n) if random.random()<0.2}
    pi=list(range(n)); random.shuffle(pi)
    c=sb.lex_clause(n,G,pi)
    if c: S.setdefault(tuple(c),pi)
open('scratch/s40.wit','w').write(''.join('%s 0 | %s\n'%(' '.join(map(str,c)),' '.join(map(str,p))) for c,p in S.items()))
import subprocess
r=subprocess.run([sys.executable,'gen.py','tri','40','10'],capture_output=True,text=True).stdout
open('scratch/t40.cnf','w').write(r)
ncl=sb.cnf_to_opb('scratch/t40.cnf','scratch/t40.opb')
base=[l for l in r.splitlines() if l and not l.startswith(('c','p'))]
with open('scratch/t40o.cnf','w') as f:
    f.write('p cnf 780 %d\n'%(len(base)+len(S))); f.write('\n'.join(base)+'\n')
    for c in S: f.write(' '.join(map(str,c))+' 0\n')
sb.cnf_to_opb('scratch/t40o.cnf','scratch/t40o.opb')
sb.write_veripb('scratch/t40.pbp',n,ncl,[(list(c),p) for c,p in S.items()])
print('clauses',len(S),'avg len',sum(len(c) for c in S)/len(S))
