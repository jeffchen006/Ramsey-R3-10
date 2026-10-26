#!/usr/bin/env python3
"""mkjobs.py n K [maxf] [primes...] -> lines 'p f --n n --K K' for all prime p, f = n mod p, f <= n-p."""
import sys
n, K = int(sys.argv[1]), int(sys.argv[2])
maxf = int(sys.argv[3]) if len(sys.argv) > 3 else n
ps = [int(x) for x in sys.argv[4:]] or [p for p in range(2, n + 1) if all(p % d for d in range(2, p))]
for p in sorted(ps, reverse=True):
    for f in range(n % p, n - p + 1, p):
        if f <= maxf:
            print(f"{p} {f} --n {n} --K {K}")
