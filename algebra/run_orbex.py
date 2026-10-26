"""Run exhaustive orbex on class files. usage: run_orbex.py node_limit file..."""
import sys, time
sys.path.insert(0, './algebra')
import orbex, ev
lim = int(sys.argv[1])
for fn in sys.argv[2:]:
    L = open(fn).read().split('\n'); n, k, M = map(int, L[0].split())
    orbs = []
    for line in L[1:1 + M]:
        a = list(map(int, line.split()))[2:]; orbs.append([(a[i], a[i + 1]) for i in range(0, len(a), 2)])
    t = time.time(); best, nodes, leaves = orbex.orbex(n, orbs, k, lim)
    if best is None:
        print(f"{fn} classes={M} TOO_BIG nodes>{lim} ({time.time()-t:.0f}s)", flush=True); continue
    g = orbex.adj_of(n, orbs, best[0][1]) if best else None
    print(f"{fn} classes={M} nodes={nodes} maximal_unions={leaves} best_c10={best[0][0] if best else None} "
          f"alpha={ev.alpha(g) if g else None} ({time.time()-t:.0f}s)", flush=True)
    if best and best[0][0] == 0: print('FOUND', ev.to_graph6(g), flush=True)
