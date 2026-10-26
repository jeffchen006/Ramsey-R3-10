"""Independent cross-check of one-vertex extension via SAT (pysat), own 9-set enumeration.
Usage: sat_ext.py FILE.g6 [K]   (prints n9 and SAT/UNSAT per graph)"""
import sys
sys.path.insert(0, './tools')
from check_graph import parse_graph6
from pysat.solvers import Cadical153
K = int(sys.argv[2]) if len(sys.argv) > 2 else 9

def indep_sets(adj, k):
    n = len(adj); out = []
    def rec(start, chosen, forb, need):
        if need == 0:
            out.append(list(chosen)); return
        for v in range(start, n):
            if not (forb >> v) & 1:
                chosen.append(v); rec(v + 1, chosen, forb | adj[v], need - 1); chosen.pop()
    rec(0, [], 0, k)
    return out

def main():
  for line in open(sys.argv[1]):
      if not line.strip() or line[0] in '#>': continue
      adj = parse_graph6(line.split()[-1] if ' ' in line.strip() else line.strip())
      n = len(adj)
      T = indep_sets(adj, K)
      s = Cadical153()
      for u in range(n):
          for w in range(u + 1, n):
              if adj[u] >> w & 1: s.add_clause([-(u + 1), -(w + 1)])
      for t in T: s.add_clause([v + 1 for v in t])
      r = s.solve()
      S = [v for v in range(n) if r and s.get_model()[v] > 0]
      print(n, len(T), 'SAT' if r else 'UNSAT', S if r else '')


if __name__ == '__main__':
    main()
