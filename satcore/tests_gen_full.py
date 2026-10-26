# Generate the full eager CNF for (3,k,n) (for comparison only).
import itertools, sys
n, k, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
ev = lambda i, j: j*(j-1)//2 + i + 1
cl = [[-ev(a,b), -ev(a,c), -ev(b,c)] for a,b,c in itertools.combinations(range(n),3)]
cl += [[ev(a,b) for a,b in itertools.combinations(S,2)] for S in itertools.combinations(range(n),k)]
with open(out, 'w') as f:
    f.write("p cnf %d %d\n" % (n*(n-1)//2, len(cl)))
    for c in cl: f.write(" ".join(map(str,c)) + " 0\n")
