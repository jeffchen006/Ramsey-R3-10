import sys, subprocess
sys.path.insert(0,'./cert')
import sb, mtf
n,s=int(sys.argv[1]),int(sys.argv[2]); tag=sys.argv[3]
M=mtf.MTF(n)
r=subprocess.run([sys.executable,'gen.py',tag,str(n),str(s)],capture_output=True,text=True).stdout
base=[l for l in r.splitlines() if l and not l.startswith(('c','p'))]
open('scratch/m_in.cnf','w').write('p cnf %d %d\n'%(M.nvars,len(base))+'\n'.join(base)+'\n')
S=sb.static_clauses(n,1)
pre=M.proof_lines(); mc=M.clauses(); assert len(pre)==len(mc)
with open('scratch/m_out.cnf','w') as f:
    f.write('p cnf %d %d\n'%(M.nvars,len(base)+len(mc)+len(S))); f.write('\n'.join(base)+'\n')
    for c in mc: f.write(' '.join(map(str,c))+' 0\n')
    for c,_ in S: f.write(' '.join(map(str,c))+' 0\n')
ncl=sb.cnf_to_opb('scratch/m_in.cnf','scratch/m_in.opb'); sb.cnf_to_opb('scratch/m_out.cnf','scratch/m_out.opb')
sb.write_veripb('scratch/m.pbp',n,ncl,S,prefix=pre,aux_witness=M.aux_witness)
print('red steps',len(pre),'dom steps',len(S))
