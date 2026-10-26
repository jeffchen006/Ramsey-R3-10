"""Check an input file of X graphs for R(6, f* <= 5) before use (untrusted data, e.g. data/graphs/angeltveit/).

Author: agent `cases`, 2026-10-25.  Run with: python3 -I cases/r6f_check_input.py FILE [FILE ...]
(-I: no imports from the data directory).  Reads graph6 lines only; never executes anything from the data.
Checks per graph: 26 vertices, triangle-free, alpha <= 7, e <= 77, no duplicate graph6 line.
Then compares the counts per edge level with the published numbers:
  e = 73: 62 (HoG / [GR] T13), and the [Ang] Sec 3.2 total R(3,8;26,<=77) = 1,767,543;
  levels 74..77 (1625, 23409, 216151, 1526296) as quoted in notes/cases_local.md (Lemma Mc, [D-C8*]).
Exit 0 only if all checks pass and all counts match.
"""
import sys

EXPECT = {73: 62, 74: 1625, 75: 23409, 76: 216151, 77: 1526296}
TOTAL = 1767543


def decode(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    if not 0 < n < 63:
        raise ValueError("bad size byte")
    need = (n * (n - 1) // 2 + 5) // 6
    if len(b) - 1 != need or any(not 0 <= v < 64 for v in b[1:]):
        raise ValueError("bad length or character")
    bits = [(v >> k) & 1 for v in b[1:] for k in range(5, -1, -1)]
    adj = [0] * n
    t = 0
    for j in range(1, n):
        for i in range(j):
            if bits[t]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            t += 1
    return n, adj


def alpha_gt(adj, cand, need):
    """True iff the vertex set `cand` (bitmask) contains an independent set of size >= need."""
    if need <= 0:
        return True
    if bin(cand).count("1") < need:
        return False
    v = (cand & -cand).bit_length() - 1
    return alpha_gt(adj, cand & ~adj[v] & ~(1 << v), need - 1) or alpha_gt(adj, cand & ~(1 << v), need)


def main():
    counts, seen, bad = {}, set(), 0
    for path in sys.argv[1:]:
        with open(path, "rb") as f:
            for ln, raw in enumerate(f, 1):
                s = raw.decode("ascii", "replace").strip()
                if not s or s.startswith(">>"):
                    continue
                try:
                    n, adj = decode(s)
                except ValueError as e:
                    print(f"{path}:{ln}: {e}"); bad += 1; continue
                e = sum(bin(a).count("1") for a in adj) // 2
                tri = any(adj[i] & adj[j] for i in range(n) for j in range(i + 1, n) if adj[i] >> j & 1)
                err = []
                if n != 26: err.append("n != 26")
                if tri: err.append("triangle")
                if e > 77: err.append("e > 77")
                if n == 26 and alpha_gt(adj, (1 << n) - 1, 8): err.append("alpha >= 8")
                if s in seen: err.append("duplicate line")
                seen.add(s)
                if err:
                    print(f"{path}:{ln}: {', '.join(err)}"); bad += 1
                counts[e] = counts.get(e, 0) + 1
    tot = sum(counts.values())
    print("counts per e:", dict(sorted(counts.items())), "total", tot)
    ok = bad == 0 and tot == TOTAL and all(counts.get(e, 0) == c for e, c in EXPECT.items())
    print("bad graphs:", bad, "| counts match published:", ok)
    print("NOTE: graph6 strings are not canonical here; isomorphic duplicates are not detected (counts check covers it).")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
