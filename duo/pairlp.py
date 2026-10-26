# codegree-typed pair LP for case R (9-regular, n=40). Vars: n_c (c=1..7), G_c = sum of g over pairs with codeg c, C4.
import numpy as np
from scipy.optimize import linprog
e38={21:35,22:42,23:49,24:56,25:65,26:73,27:85}
cs=range(1,8); nv=7+7+1
A_eq=[];b_eq=[]
def row(): return np.zeros(nv)
r=row(); r[:7]=1; A_eq.append(r); b_eq.append(600)
r=row(); r[:7]=list(cs); A_eq.append(r); b_eq.append(1440)
r=row(); r[7:14]=1; r[14]=4; A_eq.append(r); b_eq.append(11520)      # sum g = 11520 - 4 C4
r=row(); r[:7]=[c*(c-1)/2 for c in cs]; r[14]=-2; A_eq.append(r); b_eq.append(0)  # sum C(c,2) n_c = 2 C4
A_ub=[];b_ub=[]
for i,c in enumerate(cs):
    lo=max(9-c, e38[20+c]-18-9*c); hi=(9-c)**2
    r=row(); r[i]=lo; r[7+i]=-1; A_ub.append(r); b_ub.append(0)
    r=row(); r[i]=-hi; r[7+i]=1; A_ub.append(r); b_ub.append(0)
r=row(); r[0]=1; A_ub.append(r); b_ub.append(180)
for obj,name in [(14,'C4')]+[(i,'n%d'%(i+1)) for i in range(7)]:
    out=[]
    for s in (1,-1):
        cvec=row(); cvec[obj]=s
        res=linprog(cvec,A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,bounds=[(0,None)]*nv)
        out.append(s*res.fun if res.status==0 else res.status)
    print(name,'range',out)
