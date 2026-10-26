#!/usr/bin/env python3
"""Convert smsg output lines '[(0,1),(0,2),...]' to graph6. Usage: edges2g6.py N < log > out.g6"""
import sys
n = int(sys.argv[1])
for line in sys.stdin:
    line = line.strip()
    if not line.startswith("[("):
        continue
    adj = [[0] * n for _ in range(n)]
    for e in line[2:-2].split("),("):
        i, j = map(int, e.split(","))
        adj[i][j] = adj[j][i] = 1
    bits = [adj[u][j] for j in range(1, n) for u in range(j)]
    bits += [0] * (-len(bits) % 6)
    head = chr(n + 63) if n <= 62 else "~" + "".join(chr(((n >> s) & 63) + 63) for s in (12, 6, 0))
    body = "".join(chr(int("".join(map(str, bits[i:i + 6])), 2) + 63) for i in range(0, len(bits), 6))
    print(head + body)
