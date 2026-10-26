"""Combine mcount outputs: per-level ratios g(e+1)/g(e) = <a>_e / <r>_{e+1}.

usage: python3 combine.py ANCHOR_E ANCHOR_COUNT file1.out [file2.out ...]
Prints ln g(e) - ln g(anchor) and estimated iso-class counts (labelled ratio x anchor
count; assumes trivial automorphism groups at both levels), per seed and pooled.
"""
import sys, math

def load(fn):
    d = {}
    for line in open(fn):
        if line.startswith('#') or not line.strip():
            continue
        e, ns, ma, sa, mr, sr, lw = line.split()
        d[int(e)] = (int(ns), float(ma), float(mr), float(lw))
    return d

def curve(levels):
    es = sorted(levels)
    lg = {es[0]: 0.0}
    for e in es[:-1]:
        ns0, a0, _, _ = levels[e]
        ns1, _, r1, _ = levels[e + 1]
        if ns0 == 0 or ns1 == 0 or a0 <= 0 or r1 <= 0:
            lg[e + 1] = float('nan')
        else:
            lg[e + 1] = lg[e] + math.log(a0) - math.log(r1)
    return lg

def main():
    ae, ac = int(sys.argv[1]), float(sys.argv[2])
    files = sys.argv[3:]
    data = [load(f) for f in files]
    curves = [curve(d) for d in data]
    # pooled: sample-weighted means
    pool = {}
    for e in data[0]:
        ns = sum(d[e][0] for d in data)
        if ns == 0:
            pool[e] = (0, 0, 0, 0)
            continue
        ma = sum(d[e][0] * d[e][1] for d in data) / ns
        mr = sum(d[e][0] * d[e][2] for d in data) / ns
        pool[e] = (ns, ma, mr, 0)
    pc = curve(pool)
    es = sorted(pc)
    print("e  samples  ratio(e/e-1)  lnG-lnG(anchor) per seed ...  | pooled est. count")
    cum_pool = 0.0
    for e in es:
        per = [c[e] - c[ae] for c in curves]
        lp = pc[e] - pc[ae]
        est = ac * math.exp(lp)
        if e >= ae:
            cum_pool += est
        rat = math.exp(pc[e] - pc[e - 1]) if e - 1 in pc else float('nan')
        sd = (sum((x - sum(per) / len(per)) ** 2 for x in per) / max(1, len(per) - 1)) ** 0.5
        print(f"{e:4d} {pool[e][0]:9d} {rat:8.3f}  " + " ".join(f"{x:8.3f}" for x in per)
              + f"  sd={sd:.3f} | {est:.4g}  cum(>=anchor)={cum_pool:.4g}")

main()
