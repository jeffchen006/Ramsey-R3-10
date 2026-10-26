// satcore: solver-independent logic of the "no independent k-set" propagator.
//
// Graph on n <= 64 vertices, one Boolean variable per edge,
// var(i,j) = j*(j-1)/2 + i + 1 for i < j (colex, graph6 bit order).
// Literal +var: edge present; -var: edge absent.
//
// A k-set S is "bad" if all C(k,2) pairs of S are absent (S independent).
// Clause for S: OR of all +var(a,b), a<b in S (all-positive, C(k,2) literals).
//  - conflict:    all pairs of S assigned false
//  - propagation: all pairs but one false, last pair unassigned -> it must be true
//
// Every new false edge (u,v) is processed once: we search all k-sets that
// contain u and v and are cliques in the "false or unassigned" graph with at
// most one unassigned pair (bitset branch and bound, greedy colouring bound).
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <vector>

namespace satcore {

typedef uint64_t set_t;

static inline int evar (int i, int j) {
  if (i > j) { int t = i; i = j; j = t; }
  return j * (j - 1) / 2 + i + 1;
}
static inline int popc (set_t x) { return __builtin_popcountll (x); }
static inline int lowb (set_t x) { return __builtin_ctzll (x); }
static inline set_t bit (int i) { return (set_t) 1 << i; }

struct CoreStats {
  uint64_t processed = 0, nodes = 0, conflicts = 0, props = 0, stale = 0;
};

class Core {
public:
  int n, k, nv;
  // Pair id p = evar(i,j) in 1..nv. Solver variable of pair p: pvar[p]
  // (identity by default; several pairs may share one solver variable,
  // e.g. edge orbits of a group). vpairs[sv] = pairs of solver variable sv.
  std::vector<int> eu, ev;     // pair -> endpoints (eu < ev)
  std::vector<int> pvar;
  std::vector<std::vector<int>> vpairs;
  std::vector<int8_t> val;     // pair -> 0 unassigned, +1 true, -1 false
  std::vector<int8_t> sval;    // solver var -> value
  set_t F[64], T[64], all;     // F[v]: false neighbours, T[v]: true neighbours
  std::vector<int> trail;      // assigned solver vars
  std::vector<size_t> lim;     // trail size at each decision level
  std::vector<int> pend;       // false edges not yet processed
  std::vector<char> inpend;
  std::vector<int> pq;         // found propagations (target pair), with
  std::vector<set_t> pq_set;   // their k-sets
  size_t pq_head = 0;
  std::vector<set_t> reason;   // solver var -> k-set of last returned propagation
  bool use_props = true;       // false: conflicts only
  size_t max_props_per_edge = 1000;
  CoreStats st;

  Core (int n_, int k_) : n (n_), k (k_) {
    if (n < 2 || n > 64 || k < 2 || k > n) {
      fprintf (stderr, "satcore: need 2 <= k <= n <= 64\n");
      exit (1);
    }
    nv = n * (n - 1) / 2;
    eu.assign (nv + 1, -1);
    ev.assign (nv + 1, -1);
    for (int j = 1; j < n; j++)
      for (int i = 0; i < j; i++) eu[evar (i, j)] = i, ev[evar (i, j)] = j;
    val.assign (nv + 1, 0);
    inpend.assign (nv + 1, 0);
    std::vector<int> id (nv + 1);
    for (int p = 0; p <= nv; p++) id[p] = p;
    set_map (id);
    all = n == 64 ? ~(set_t) 0 : bit (n) - 1;
    for (int v = 0; v < 64; v++) F[v] = T[v] = 0;
  }

  // m[p] = solver variable of pair p (p = 1..nv, m[0] ignored), all >= 1.
  void set_map (const std::vector<int> &m) {
    pvar = m;
    int mx = 0;
    for (int p = 1; p <= nv; p++) mx = std::max (mx, pvar[p]);
    vpairs.assign (mx + 1, {});
    for (int p = 1; p <= nv; p++) vpairs[pvar[p]].push_back (p);
    sval.assign (mx + 1, 0);
    reason.assign (mx + 1, 0);
  }
  bool identity () const {
    for (int p = 1; p <= nv; p++) if (pvar[p] != p) return false;
    return true;
  }

  int level () const { return (int) lim.size (); }

  // Clause (solver variables, positive) of k-set S, duplicates removed.
  void clause_of (set_t S, std::vector<int> &out) const {
    out.clear ();
    for (set_t A = S; A; A &= A - 1) {
      int a = lowb (A);
      for (set_t B = S & ~(bit (a + 1) - 1); B; B &= B - 1)
        out.push_back (pvar[evar (a, lowb (B))]);
    }
    std::sort (out.begin (), out.end ());
    out.erase (std::unique (out.begin (), out.end ()), out.end ());
  }

  void assign (int lit) {
    int v = abs (lit);
    if (v < 1 || v >= (int) vpairs.size () || vpairs[v].empty ()) return;
    int8_t s = lit > 0 ? 1 : -1;
    if (sval[v] == s) return;  // re-notification
    if (sval[v] == -s) {
      fprintf (stderr, "satcore: inconsistent notification of %d\n", lit);
      abort ();
    }
    sval[v] = s;
    trail.push_back (v);
    for (int p : vpairs[v]) {
      val[p] = s;
      int a = eu[p], b = ev[p];
      if (s > 0) T[a] |= bit (b), T[b] |= bit (a);
      else {
        F[a] |= bit (b), F[b] |= bit (a);
        if (!inpend[p]) inpend[p] = 1, pend.push_back (p);
      }
    }
  }

  void new_level () { lim.push_back (trail.size ()); }

  void backtrack (size_t new_level) {
    if (new_level >= lim.size ()) return;
    size_t keep = lim[new_level];
    while (trail.size () > keep) {
      int v = trail.back ();
      trail.pop_back ();
      for (int p : vpairs[v]) {
        int a = eu[p], b = ev[p];
        if (val[p] > 0) T[a] &= ~bit (b), T[b] &= ~bit (a);
        else F[a] &= ~bit (b), F[b] &= ~bit (a);
        val[p] = 0;
      }
      sval[v] = 0;
    }
    lim.resize (new_level);
    // pending props are re-validated when popped
  }

  // Is S still a valid reason for target pair t: every pair of S whose
  // solver variable differs from pvar[t] is false?
  // Returns +1 propagation, 0 invalid/satisfied, -1 conflict (t false too).
  int check_set (set_t S, int t) const {
    int tv = pvar[t];
    for (set_t A = S; A; A &= A - 1) {
      int a = lowb (A);
      for (set_t B = S & ~(bit (a + 1) - 1); B; B &= B - 1) {
        int p = evar (a, lowb (B));
        if (val[p] > 0) return 0;
        if (val[p] == 0 && pvar[p] != tv) return 0;
      }
    }
    return val[t] == 0 ? 1 : -1;
  }

  // Next literal to propagate (positive: an edge forced true; or an already
  // false edge = conflict). Reason via reason[var]. 0 = nothing.
  int next_prop () {
    for (;;) {
      while (pq_head < pq.size ()) {
        int t = pq[pq_head];
        set_t S = pq_set[pq_head];
        pq_head++;
        int r = check_set (S, t);
        if (r == 0) { st.stale++; continue; }
        reason[pvar[t]] = S;
        if (r > 0) st.props++; else st.conflicts++;
        return pvar[t];  // if false: falsified propagation = conflict
      }
      pq.clear (), pq_set.clear (), pq_head = 0;
      if (pend.empty ()) return 0;
      int v = pend.back ();
      pend.pop_back ();
      inpend[v] = 0;
      if (val[v] < 0) process (v);
    }
  }

  // Search k-sets through false edge v.
  void process (int v) {
    st.processed++;
    int a = eu[v], b = ev[v];
    set_t S = bit (a) | bit (b);
    set_t U[64];
    for (int x = 0; x < n; x++) U[x] = all & ~F[x] & ~T[x] & ~bit (x);
    Ucur = U;
    set_t P0 = F[a] & F[b] & ~S;
    set_t P1 = use_props ? ((F[a] & U[b]) | (U[a] & F[b])) & ~S : 0;
    found_conflict = false;
    found_props = 0;
    search (2, S, P0, P1, use_props ? 0 : 1);
  }

  // Greedy colouring bound: number of colour classes of P in the F graph
  // (each class has no F edge inside), stop when it exceeds lim.
  int colour_bound (set_t P, int limit) const {
    int c = 0;
    while (P) {
      if (++c > limit) return c;
      set_t R = P;
      while (R) {
        int x = lowb (R);
        R &= ~F[x] & ~bit (x);
        P &= ~bit (x);
      }
    }
    return c;
  }

  // used = number of unassigned pairs inside S (0 or 1).
  // P0: F-adjacent to all of S. P1 (used==0 only): adjacent to all of S by
  // F or U, with exactly one U pair.
  bool found_conflict;
  size_t found_props;
  const set_t *Ucur;
  void search (int size, set_t S, set_t P0, set_t P1, int used) {
    st.nodes++;
    if (size == k) { report (S, used); return; }
    int need = k - size;
    while (P0 | P1) {
      if (found_conflict || found_props >= max_props_per_edge) return;
      int extra = used ? 0 : 1;
      if (popc (P0) + extra < need) return;
      if (colour_bound (P0, need - extra) + extra < need) return;
      set_t C = P0 | P1;
      int w = lowb (C);
      if (P0 & bit (w)) {
        set_t nP0 = P0 & F[w];
        set_t nP1 = used ? 0 : ((P1 & F[w]) | (P0 & Ucur[w]));
        search (size + 1, S | bit (w), nP0 & ~bit (w), nP1 & ~bit (w), used);
      } else {
        search (size + 1, S | bit (w), P0 & F[w] & ~bit (w), 0, 1);
      }
      P0 &= ~bit (w);
      P1 &= ~bit (w);
    }
  }

  void report (set_t S, int used) {
    (void) used;
    int t = 0;
    for (set_t A = S; A && !t; A &= A - 1) {
      int a = lowb (A);
      set_t u = Ucur[a] & S;
      if (u) t = evar (a, lowb (u));
    }
    if (!t) {
      // conflict: pick any false pair of S as falsified propagation
      int a = lowb (S), b = lowb (S & ~bit (a));
      pq.insert (pq.begin () + pq_head, evar (a, b));
      pq_set.insert (pq_set.begin () + pq_head, S);
      found_conflict = true;
      return;
    }
    if (!use_props) {
      fprintf (stderr, "satcore: unassigned pair in conflict-only mode\n");
      abort ();
    }
    pq.push_back (t);
    pq_set.push_back (S);
    found_props++;
  }

  // ---- full-graph check (used for found models and CEGAR) ----
  // adj[v] = neighbours in a complete graph. Finds up to `limit` independent
  // k-sets, appends them to out. Returns number found.
  static size_t find_indep (int n, int k, const set_t *adj, size_t limit,
                            std::vector<set_t> &out) {
    set_t all = n == 64 ? ~(set_t) 0 : bit (n) - 1;
    set_t nonadj[64];
    for (int v = 0; v < n; v++) nonadj[v] = all & ~adj[v] & ~bit (v);
    size_t cnt = 0;
    rec_indep (k, nonadj, 0, 0, all, limit, cnt, out);
    return cnt;
  }
  static void rec_indep (int k, const set_t *na, int size, set_t S, set_t P,
                         size_t limit, size_t &cnt, std::vector<set_t> &out) {
    if (size == k) { out.push_back (S); cnt++; return; }
    while (P && cnt < limit) {
      if (size + popc (P) < k) return;
      // colouring bound in the non-adjacency graph
      int c = 0;
      set_t Q = P;
      while (Q && c < k - size) {
        c++;
        set_t R = Q;
        while (R) { int x = lowb (R); R &= ~na[x] & ~bit (x); Q &= ~bit (x); }
      }
      if (!Q && size + c < k) return;
      int w = lowb (P);
      rec_indep (k, na, size + 1, S | bit (w), P & na[w], limit, cnt, out);
      P &= ~bit (w);
    }
  }
};

}  // namespace satcore
