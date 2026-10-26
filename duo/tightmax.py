# max |X_S| over independent s-sets vs bound R(3,a+1-s)-1 (a = alpha bound)
import sys, networkx as nx
R={1:1,2:3,3:6,4:9,5:14,6:18,7:23,8:28,9:36}  # R(3,k)
a=int(sys.argv[2])
for line in open(sys.argv[1]):
    G=nx.from_graph6_bytes(line.strip().encode()); n=G.number_of_nodes()
    adj=[sum(1<<j for j in G[i]) for i in range(n)]
    best={}
    def rec(start,S,cov,cand):
        s=len(S)
        if s: 
            m=n-bin(cov).count('1')
            if m>best.get(s,(-1,0))[0]: best[s]=(m,1)
            elif m==best[s][0]: best[s]=(m,best[s][1]+1)
        if s==a-1: return
        for i in range(start,n):
            if cand>>i&1: rec(i+1,S+[i],cov|adj[i]|(1<<i),cand&~adj[i]&~((1<<(i+1))-1))
    rec(0,[],0,(1<<n)-1)
    print(n, {s:(best[s][0], R[a+1-s]-1, best[s][1]) for s in sorted(best)})
