// orbsolve: CaDiCaL + external propagator for (3,K)-graphs on orbit variables.
//
// Usage: orbsolve PROBLEM CNF [options]
//   PROBLEM: "n K nv", then n rows of n ints (var of pair {i,j}, 0 on the diagonal),
//            then "R r_1 .. r_R" (one vertex per vertex orbit of H).
//   CNF:     DIMACS base clauses (triangles, degree bounds, symmetry breaking) on vars >= 1;
//            vars 1..nv are the edge-orbit variables.
// Options: --sets FILE (log every independent K-set used for a clause, one per line)
//          --partial N (check partial assignments every N-th callback, 0 = off; default 1)
//          --nodes N (node limit of a partial check; default 20000)
//          --seed S, --tl SECONDS, --phase0 (initial phase false)
// Output: "s SATISFIABLE" + "v <edge pairs>" or "s UNSATISFIABLE" or "s UNKNOWN".
//
// Soundness: every clause the propagator adds is "some pair of this K-set is an edge" for an
// explicit K-set, valid for every graph with alpha < K. A model is accepted only after an
// exact search finds no independent K-set in it.
#include "cadical.hpp"
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>

typedef uint64_t u64;
static int n, K, nv;
static int pv[64][64];
static std::vector<int> reps;
static std::vector<std::vector<std::pair<int,int>>> pairs_of_var;

static inline int popc(u64 x) { return __builtin_popcountll(x); }

// ---- independent-set search on adjacency bitmasks -------------------------------------
struct IS {
  const u64 *A; int k; bool found; u64 best; unsigned rng; long nodes, limit;
  void rec(u64 P, u64 cur, int c) {
    if (found || (limit && nodes > limit)) return;
    nodes++;
    if (c >= k) { found = true; best = cur; return; }
    if (c + popc(P) < k) return;
    u64 iso = 0, Q = P; int bv = -1, bd = 1 << 30;
    while (Q) {
      int v = __builtin_ctzll(Q); Q &= Q - 1;
      int d = popc(A[v] & P);
      if (d == 0) { iso |= 1ULL << v; continue; }
      if (d < bd || (d == bd && ((rng = rng * 1103515245u + 12345u) >> 16) & 1)) { bd = d; bv = v; }
    }
    if (iso) {
      while (c < k && iso) { int v = __builtin_ctzll(iso); iso &= iso - 1; cur |= 1ULL << v; c++; P &= ~(1ULL << v); }
      if (c >= k) { found = true; best = cur; return; }
      P &= ~iso;
      if (!P) return;
    }
    u64 b = 1ULL << bv;
    rec(P & ~A[bv] & ~b, cur | b, c + 1);
    rec(P & ~b, cur, c);
  }
  // independent k-set containing `must` (independent), or 0
  u64 find(const u64 *adj, int kk, u64 must, unsigned seed, long lim) {
    A = adj; k = kk; found = false; best = 0; rng = seed; nodes = 0; limit = lim;
    u64 all = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
    u64 P = all & ~must; int c = 0; u64 m = must;
    while (m) { int v = __builtin_ctzll(m); m &= m - 1; P &= ~adj[v]; c++; }
    rec(P, must, c);
    return found ? best : 0;
  }
};

struct Prop : CaDiCaL::ExternalPropagator {
  std::vector<signed char> val;      // per var: 1 true, -1 false, 0 unassigned
  std::vector<int> trail;
  std::vector<size_t> lvl;
  std::vector<std::vector<int>> queue; size_t qpos = 0, lpos = 0;
  std::unordered_set<std::string> seen;
  FILE *setsf = nullptr;
  long nclauses = 0, nmodels = 0, npartial = 0, npartial_hits = 0, ncb = 0;
  int partial_every = 1; long node_limit = 20000; unsigned seed = 1;
  bool dirty = false;
  IS is;

  Prop() { val.assign(nv + 1, 0); }
  void notify_assignment(const std::vector<int> &lits) override {
    for (int l : lits) { int v = abs(l); if (v > nv) continue;
      if (val[v] == 0) { val[v] = l > 0 ? 1 : -1; trail.push_back(v); if (l < 0) dirty = true; } }
  }
  void notify_new_decision_level() override { lvl.push_back(trail.size()); }
  void notify_backtrack(size_t new_level) override {
    size_t to = lvl[new_level];
    while (trail.size() > to) { val[trail.back()] = 0; trail.pop_back(); }
    lvl.resize(new_level);
  }
  bool add_set(u64 m) {
    std::set<int> vs;
    std::vector<int> verts;
    for (int i = 0; i < n; i++) if ((m >> i) & 1) verts.push_back(i);
    for (size_t a = 0; a < verts.size(); a++) for (size_t b = a + 1; b < verts.size(); b++)
      vs.insert(pv[verts[a]][verts[b]]);
    std::string key; for (int v : vs) { key += std::to_string(v); key += ','; }
    if (!seen.insert(key).second) return false;
    std::vector<int> cl(vs.begin(), vs.end()); cl.push_back(0);
    queue.push_back(cl);
    if (setsf) { for (int v : verts) fprintf(setsf, "%d ", v); fprintf(setsf, "\n"); }
    nclauses++;
    return true;
  }
  void graph_of(std::vector<u64> &adj, bool possible) {
    // possible=false: edges = true vars (complete model); possible=true: edges = not-false vars
    adj.assign(n, 0);
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
      int v = pv[i][j]; bool e = possible ? (val[v] != -1) : (val[v] == 1);
      if (e) { adj[i] |= 1ULL << j; adj[j] |= 1ULL << i; }
    }
  }
  bool cb_check_found_model(const std::vector<int> &model) override {
    nmodels++;
    std::vector<signed char> mv(nv + 1, -1);
    for (int l : model) { int v = abs(l); if (v <= nv) mv[v] = l > 0 ? 1 : -1; }
    std::vector<u64> adj(n, 0);
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++)
      if (mv[pv[i][j]] == 1) { adj[i] |= 1ULL << j; adj[j] |= 1ULL << i; }
    int added = 0;
    for (int round = 0; round < 3; round++)
      for (int r : reps) {
        u64 m = is.find(adj.data(), K, 1ULL << r, seed = seed * 1664525u + 1013904223u, 0);
        if (m && add_set(m)) added++;
      }
    if (!added) {
      u64 m = is.find(adj.data(), K, 0, 1, 0);
      if (!m) return true;   // exact: no independent K-set
      if (!add_set(m)) { fprintf(stderr, "c internal error: repeated clause on model\n"); exit(3); }
    }
    return false;
  }
  bool cb_has_external_clause(bool &forgettable) override {
    forgettable = false;
    if (qpos < queue.size()) return true;
    queue.clear(); qpos = 0;
    if (partial_every && dirty && (++ncb % partial_every == 0)) {
      dirty = false; npartial++;
      std::vector<u64> adj; graph_of(adj, true);
      for (int r : reps) {
        u64 m = is.find(adj.data(), K, 1ULL << r, seed = seed * 1664525u + 1013904223u, node_limit);
        if (m && add_set(m)) { npartial_hits++; break; }
      }
    }
    return qpos < queue.size();
  }
  int cb_add_external_clause_lit() override {
    std::vector<int> &cl = queue[qpos];
    int l = cl[lpos++];
    if (l == 0) { qpos++; lpos = 0; }
    return l;
  }
  int cb_add_reason_clause_lit(int) override { return 0; }
};

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: orbsolve PROBLEM CNF [opts]\n"); return 1; }
  const char *setsfile = nullptr; int partial = 1; long nodes = 20000; unsigned seed = 1;
  double tl = 0; bool phase0 = false;
  for (int i = 3; i < argc; i++) {
    if (!strcmp(argv[i], "--sets")) setsfile = argv[++i];
    else if (!strcmp(argv[i], "--partial")) partial = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--nodes")) nodes = atol(argv[++i]);
    else if (!strcmp(argv[i], "--seed")) seed = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--tl")) tl = atof(argv[++i]);
    else if (!strcmp(argv[i], "--phase0")) phase0 = true;
    else { fprintf(stderr, "bad option %s\n", argv[i]); return 1; }
  }
  FILE *f = fopen(argv[1], "r");
  if (!f || fscanf(f, "%d %d %d", &n, &K, &nv) != 3) { fprintf(stderr, "bad problem\n"); return 1; }
  for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (fscanf(f, "%d", &pv[i][j]) != 1) return 1;
  int R; if (fscanf(f, "%d", &R) != 1) return 1;
  reps.resize(R); for (int i = 0; i < R; i++) if (fscanf(f, "%d", &reps[i]) != 1) return 1;
  fclose(f);
  CaDiCaL::Solver s;
  if (phase0) s.set("phase", 0);
  s.set("seed", (int)seed);
  // read CNF
  FILE *c = fopen(argv[2], "r");
  if (!c) { fprintf(stderr, "no cnf\n"); return 1; }
  int ch; int maxv = nv;
  while ((ch = fgetc(c)) != EOF) {
    if (ch == 'c' || ch == 'p') { while ((ch = fgetc(c)) != EOF && ch != '\n'); continue; }
    ungetc(ch, c);
    int lit;
    if (fscanf(c, "%d", &lit) != 1) break;
    if (abs(lit) > maxv) maxv = abs(lit);
    s.add(lit);
  }
  fclose(c);
  Prop p; p.partial_every = partial; p.node_limit = nodes; p.seed = seed;
  if (setsfile) p.setsf = fopen(setsfile, "w");
  s.connect_external_propagator(&p);
  for (int v = 1; v <= nv; v++) s.add_observed_var(v);
  auto t0 = std::chrono::steady_clock::now();
  struct Term : CaDiCaL::Terminator {
    double tl; std::chrono::steady_clock::time_point t0;
    bool terminate() override {
      return tl > 0 && std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() > tl;
    }
  } term; term.tl = tl; term.t0 = t0;
  s.connect_terminator(&term);
  int r = s.solve();
  double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  if (p.setsf) fclose(p.setsf);
  printf("c time %.2f models %ld clauses %ld partial_checks %ld partial_hits %ld\n", dt, p.nmodels,
         p.nclauses, p.npartial, p.npartial_hits);
  if (r == 10) {
    printf("s SATISFIABLE\nv");
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (s.val(pv[i][j]) > 0) printf(" %d-%d", i, j);
    printf("\n");
  } else if (r == 20) printf("s UNSATISFIABLE\n");
  else printf("s UNKNOWN\n");
  s.disconnect_external_propagator();
  return r == 10 ? 10 : r == 20 ? 20 : 0;
}
