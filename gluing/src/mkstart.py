# Make start graphs: circulant C35(1,7,11,16) (unique (3,9;35,140)), delete vertices.
import sys
def g6(n, adj):
    bits=[]
    for j in range(1,n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    while len(bits)%6: bits.append(0)
    s=chr(63+n)
    for k in range(0,len(bits),6):
        x=0
        for b in bits[k:k+6]: x=2*x+b
        s+=chr(63+x)
    return s
N=35; D={1,7,11,16}
adj=[set() for _ in range(N)]
for i in range(N):
    for d in D:
        adj[i].add((i+d)%N); adj[(i+d)%N].add(i)
n=int(sys.argv[1])
dele=[]
# delete pairwise non-adjacent vertices greedily (keeps more edges removed predictable)
for v in range(N):
    if len(dele)==N-n: break
    if all(v not in adj[u] for u in dele): dele.append(v)
keep=[v for v in range(N) if v not in dele]
idx={v:i for i,v in enumerate(keep)}
nadj=[set(idx[u] for u in adj[v] if u in idx) for v in keep]
print(g6(n,nadj))
