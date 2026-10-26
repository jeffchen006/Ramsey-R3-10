"""critic: write test graphs (graph6, own encoder) to stdout.
Families: random G(n,p); random maximal triangle-free (greedy) at n=39,40;
all triangle-free circulants n=30..40 with degree 4..9 (sampled); long-form n>=63."""
import random, sys, itertools

def g6(n, edges):
    E = set((min(a, b), max(a, b)) for a, b in edges)
    bits = [1 if (i, j) in E else 0 for j in range(1, n) for i in range(j)]
    bits += [0] * (-len(bits) % 6)
    head = chr(63 + n) if n < 63 else '~' + ''.join(chr(63 + ((n >> s) & 63)) for s in (12, 6, 0))
    return head + ''.join(chr(63 + int(''.join(map(str, bits[i:i + 6])), 2)) for i in range(0, len(bits), 6))

def gnp(rnd, n, p):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if rnd.random() < p]

def greedy_tf(rnd, n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    N = [set() for _ in range(n)]
    E = []
    for a, b in pairs:
        if not (N[a] & N[b]):
            N[a].add(b); N[b].add(a); E.append((a, b))
    return E

def circ(n, S):
    D = set(S) | {n - s for s in S}
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) in D]

if __name__ == '__main__':
    rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    out = []
    for _ in range(400):
        n = rnd.randint(0, 45); out.append(g6(n, gnp(rnd, n, rnd.choice([0.05, 0.1, 0.2, 0.3, 0.5]))))
    for _ in range(60):
        n = rnd.choice([39, 40]); out.append(g6(n, greedy_tf(rnd, n)))
    for _ in range(10):
        n = rnd.randint(63, 80); out.append(g6(n, greedy_tf(rnd, n)))
    for n in range(30, 41):
        half = list(range(1, n // 2 + 1))
        for k in range(2, 6):
            for S in itertools.combinations(half, k):
                D = set(S) | {n - s for s in S}
                if not 4 <= len(D) <= 9: continue
                if any((a + b) % n in D for a in D for b in D): continue
                if rnd.random() < 0.15: out.append(g6(n, circ(n, S)))
    print('\n'.join(out))
