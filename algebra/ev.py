"""Python wrapper for libev.so (fast triangle / independent-set counting, n <= 64)."""
import ctypes, os
_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libev.so'))
_A = ctypes.POINTER(ctypes.c_uint64)
_L.count_indep.argtypes = [_A, ctypes.c_int, ctypes.c_int, ctypes.c_longlong]; _L.count_indep.restype = ctypes.c_longlong
_L.count_tri.argtypes = [_A, ctypes.c_int]; _L.count_tri.restype = ctypes.c_longlong
_L.alpha.argtypes = [_A, ctypes.c_int]; _L.alpha.restype = ctypes.c_int
_L.count_indep_pv.argtypes = [_A, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_longlong)]; _L.count_indep_pv.restype = ctypes.c_longlong

def _arr(adj):
    return (ctypes.c_uint64 * len(adj))(*adj)

def tri(adj): return _L.count_tri(_arr(adj), len(adj))
def indep(adj, k, cap=1 << 62): return _L.count_indep(_arr(adj), len(adj), k, cap)
def alpha(adj): return _L.alpha(_arr(adj), len(adj))
def indep_pv(adj, k):
    pv = (ctypes.c_longlong * len(adj))()
    c = _L.count_indep_pv(_arr(adj), len(adj), k, pv)
    return c, list(pv)

def from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        if u != v:
            adj[u] |= 1 << v; adj[v] |= 1 << u
    return adj

def to_graph6(adj):
    n = len(adj); bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append((adj[i] >> j) & 1)
    while len(bits) % 6: bits.append(0)
    s = chr(n + 63)
    for i in range(0, len(bits), 6):
        x = 0
        for b in bits[i:i + 6]: x = 2 * x + b
        s += chr(x + 63)
    return s

def from_graph6(line):
    data = [ord(c) - 63 for c in line.strip()]
    n = data[0]; data = data[1:]; bits = []
    for x in data:
        for s in range(5, -1, -1): bits.append((x >> s) & 1)
    adj = [0] * n; i = 0
    for j in range(1, n):
        for u in range(j):
            if bits[i]: adj[u] |= 1 << j; adj[j] |= 1 << u
            i += 1
    return adj

def score(adj, k=10):
    """(triangles, #indep k-sets, #indep (k-1)-sets)."""
    return tri(adj), indep(adj, k), indep(adj, k - 1)

_L.greedy_fill.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), _A]
def greedy(n, order, start=None):
    """order: list of pairs (u,v). Returns maximal triangle-free graph (greedy, first come first served)."""
    pu = (ctypes.c_int * len(order))(*[p[0] for p in order]); pv = (ctypes.c_int * len(order))(*[p[1] for p in order])
    a = (ctypes.c_uint64 * n)(*(start or [0] * n))
    _L.greedy_fill(n, len(order), pu, pv, a)
    return list(a)
