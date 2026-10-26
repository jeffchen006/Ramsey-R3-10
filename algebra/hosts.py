"""Build host graphs (adjacency matrix files) for subtabu."""
import sys, itertools
sys.path.insert(0, '.')
import ev

def golay_octads():
    g = [1,0,1,0,1,1,1,0,0,0,1,1]  # x^11+x^9+x^7+x^6+x^5+x+1 (coeffs low->high)
    gp = sum(b << i for i, b in enumerate(g))
    words = set()
    for msg in range(1 << 12):
        w = 0
        for i in range(12):
            if msg >> i & 1: w ^= gp << i
        w |= (bin(w).count('1') & 1) << 23
        words.add(w)
    oct_ = [w for w in words if bin(w).count('1') == 8]
    return oct_

def higman_sims():
    octs = golay_octads()
    assert len(octs) == 759, len(octs)
    hex_ = [w & ~(3 << 22) for w in octs if (w >> 22) & 3 == 3]
    assert len(hex_) == 77
    n = 100; A = [[0] * n for _ in range(n)]
    def e(a, b): A[a][b] = A[b][a] = 1
    for p in range(22): e(0, 1 + p)
    for bi, h in enumerate(hex_):
        for p in range(22):
            if h >> p & 1: e(1 + p, 23 + bi)
        for bj in range(bi + 1, 77):
            if h & hex_[bj] == 0: e(23 + bi, 23 + bj)
    return A

def write(A, fn):
    with open(fn, 'w') as f:
        f.write(f"{len(A)}\n")
        for r in A: f.write(''.join(map(str, r)) + '\n')

if __name__ == '__main__':
    A = higman_sims()
    degs = set(sum(r) for r in A); print('HS degrees', degs)
    tri = sum(1 for a, b, c in itertools.combinations(range(100), 3) if A[a][b] and A[a][c] and A[b][c]); print('HS triangles', tri)
    write(A, 'orb/host_hs.txt')
