// satcore: (3,k,n)-graph SAT solver on CaDiCaL (IPASIR-UP).
// Library API used by satcore.cpp; other agents may include it.
#pragma once
#include "cadical.hpp"
#include "tracer.hpp"
#include "core.hpp"
#include <chrono>
#include <cstring>
#include <string>
#include <unordered_map>

namespace satcore {

typedef std::vector<int> clause_t;

// ---------------------------------------------------------------- encoding
struct Section {        // a tagged part of the base CNF (for cert)
  std::string tag;      // e.g. "triangles", "fix-nbhd d=9", "card ..."
  size_t first, last;   // clause index range [first, last)
};

struct Encoding {
  int n, k, nv, maxvar;
  std::vector<clause_t> clauses;
  std::vector<Section> sections;
  std::vector<int> pvar;  // pair -> solver variable (identity unless --pairmap)
  std::vector<std::string> comments;  // "c case ..." lines

  Encoding (int n_, int k_) : n (n_), k (k_) {
    nv = n * (n - 1) / 2;
    maxvar = nv;
    pvar.resize (nv + 1);
    for (int p = 0; p <= nv; p++) pvar[p] = p;
  }
  void begin (const std::string &tag) {
    sections.push_back ({tag, clauses.size (), clauses.size ()});
  }
  void end () { sections.back ().last = clauses.size (); }
  void add (const clause_t &c) {
    for (int l : c) if (abs (l) > maxvar) maxvar = abs (l);
    clauses.push_back (c);
  }

  void triangles () {
    begin ("triangles");
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++)
        for (int l = j + 1; l < n; l++)
          {
            clause_t c = {-pvar[evar (i, j)], -pvar[evar (i, l)], -pvar[evar (j, l)]};
            std::sort (c.begin (), c.end ());
            c.erase (std::unique (c.begin (), c.end ()), c.end ());
            add (c);
          }
    end ();
  }

  // N(0) = {1..d}
  void fix_nbhd (int d) {
    begin ("fix-nbhd d=" + std::to_string (d) + " : N(0)={1.." +
           std::to_string (d) + "}");
    for (int j = 1; j < n; j++) add ({j <= d ? evar (0, j) : -evar (0, j)});
    end ();
  }

  // Codish-Miller-Prosser-Stuckey (2019) adjacent-row lex constraints:
  // for consecutive rows i, i+1 of the same block,
  //   row_i \ {i,i+1}  >=lex  row_{i+1} \ {i,i+1}   (columns in order 0..n-1).
  // Sound: the lex-leader of the orbit under the block stabilizer satisfies
  // all of them. Encoding: e_t <- prefix equal (only the forcing direction).
  // blocks: list of [lo,hi) vertex ranges in which rows may be swapped.
  void lex_rows (const std::vector<std::pair<int, int>> &blocks,
                 bool all_pairs = false) {
    for (auto &bl : blocks)
      for (int i = bl.first; i + 1 < bl.second; i++)
        for (int i2 = i + 1; i2 < (all_pairs ? bl.second : i + 2); i2++) {
          int first_aux = maxvar + 1;
          size_t c0 = clauses.size ();
          int e = 0;  // 0 = true (start)
          for (int j = 0; j < n; j++) {
            if (j == i || j == i2) continue;
            int x = evar (i, j), y = evar (i2, j);
            // e -> (x >= y): (-e | x | -y)
            clause_t c;
            if (e) c.push_back (-e);
            c.push_back (x), c.push_back (-y);
            add (c);
            bool last = true;
            for (int jj = j + 1; jj < n; jj++)
              if (jj != i && jj != i2) last = false;
            if (last) break;
            int ne = ++maxvar;  // ne <- e & (x == y)
            clause_t c1, c2;
            if (e) c1.push_back (-e), c2.push_back (-e);
            c1.push_back (-x), c1.push_back (-y), c1.push_back (ne);
            c2.push_back (x), c2.push_back (y), c2.push_back (ne);
            add (c1), add (c2);
            e = ne;
          }
          sections.push_back ({"lex rows " + std::to_string (i) + " >= " +
                                   std::to_string (i2) + " aux=" +
                                   std::to_string (first_aux) + ".." +
                                   std::to_string (maxvar),
                               c0, clauses.size ()});
        }
  }

  // Maximal triangle-free: every non-adjacent pair has a common neighbour.
  // y(i,j,m) -> x(i,m) & x(j,m);  x(i,j) | OR_m y(i,j,m).
  void mtf () {
    int first_aux = maxvar + 1;
    size_t c0 = clauses.size ();
    for (int j = 1; j < n; j++)
      for (int i = 0; i < j; i++) {
        clause_t big = {evar (i, j)};
        for (int m = 0; m < n; m++) {
          if (m == i || m == j) continue;
          int y = ++maxvar;
          add ({-y, evar (i, m)});
          add ({-y, evar (j, m)});
          big.push_back (y);
        }
        add (big);
      }
    sections.push_back ({"mtf aux=" + std::to_string (first_aux) + ".." +
                             std::to_string (maxvar) +
                             " order: pairs colex, m ascending",
                         c0, clauses.size ()});
  }

  // Co-degree bound: every pair {i,j} has at most C common neighbours.
  // y(i,j,m) <-> x(i,m) & x(j,m), then totalizer over the y's, sum <= C.
  // (Adjacent pairs have 0 common neighbours anyway, triangle-free.)
  void codegree_max (int C) {
    for (int j = 1; j < n; j++)
      for (int i = 0; i < j; i++) {
        int first_aux = maxvar + 1;
        size_t c0 = clauses.size ();
        std::vector<int> ys;
        for (int m = 0; m < n; m++) {
          if (m == i || m == j) continue;
          int y = ++maxvar;
          add ({-y, evar (i, m)});
          add ({-y, evar (j, m)});
          add ({y, -evar (i, m), -evar (j, m)});
          ys.push_back (y);
        }
        int def_last = maxvar;
        sections.push_back ({"codeg-def pair=" + std::to_string (i) + "," +
                                 std::to_string (j) + " y(m ascending)=" +
                                 std::to_string (first_aux) + ".." +
                                 std::to_string (def_last),
                             c0, clauses.size ()});
        cardinality (ys, 0, C, "codegree pair=" + std::to_string (i) + "," + std::to_string (j));
      }
  }

  // Totalizer (Bailleux-Boufkhad), both directions, outputs truncated to
  // cap: out[i] <-> (count >= i+1) for i < cap.
  std::vector<int> totalizer (const std::vector<int> &lits, size_t lo,
                              size_t hi, int cap) {
    if (hi - lo == 1) return {lits[lo]};
    size_t mid = (lo + hi) / 2;
    std::vector<int> A = totalizer (lits, lo, mid, cap);
    std::vector<int> B = totalizer (lits, mid, hi, cap);
    int m = (int) std::min (A.size () + B.size (), (size_t) cap);
    std::vector<int> O (m);
    for (int i = 0; i < m; i++) O[i] = ++maxvar;
    int na = A.size (), nb = B.size ();
    for (int a = 0; a <= na; a++)
      for (int b = 0; b <= nb; b++) {
        if (a + b >= 1) {  // A>=a & B>=b -> O>=min(a+b,m)
          clause_t c;
          if (a) c.push_back (-A[a - 1]);
          if (b) c.push_back (-B[b - 1]);
          c.push_back (O[std::min (a + b, m) - 1]);
          if (a + b <= m) add (c);
        }
        if (a + b < m) {  // A<=a & B<=b -> O<=a+b, i.e. not O[a+b]
          clause_t c;
          if (a < na) c.push_back (A[a]);
          if (b < nb) c.push_back (B[b]);
          c.push_back (-O[a + b]);
          add (c);
        }
      }
    return O;
  }

  // lo <= sum(lits) <= hi  (hi < 0: no upper bound)
  void cardinality (const std::vector<int> &lits, int lo, int hi,
                    const std::string &what) {
    int cap = std::max (hi + 1, lo);
    if (cap > (int) lits.size ()) cap = lits.size ();
    if (hi >= (int) lits.size ()) hi = -1;
    if (lo <= 0 && hi < 0) return;
    int first_aux = maxvar + 1;
    size_t c0 = clauses.size ();
    std::vector<int> O = totalizer (lits, 0, lits.size (), cap);
    if (lo > 0) add ({O[lo - 1]});
    if (hi >= 0) add ({-O[hi]});
    sections.push_back ({"card " + what + " lo=" + std::to_string (lo) +
                             " hi=" + std::to_string (hi) +
                             " encoding=totalizer(cap=" + std::to_string (cap) +
                             ") aux=" + std::to_string (first_aux) + ".." +
                             std::to_string (maxvar),
                         c0, clauses.size ()});
  }

  void degree_bounds (int lo, int hi) {
    for (int v = 0; v < n; v++) {
      std::vector<int> lits;
      for (int u = 0; u < n; u++) if (u != v) lits.push_back (evar (u, v));
      cardinality (lits, lo, hi, "degree vertex=" + std::to_string (v));
    }
  }
  // Local edge bound (GR Lemma, notes/cases.md L3): for every vertex v and
  // degree d in [dlo,dhi] with m = n-1-d in the table:
  //   deg(v) <= d  ->  e(H_v) >= L[m],   H_v = G - N[v].
  // y(v,a,b) <-> x(a,b) & -x(a,v) & -x(b,v) for pairs a<b != v (colex order),
  // then a totalizer over the y's (counts e(H_v)) and one over v's edges.
  // Sound for L[m] <= e(3,k-1,m) (H_v is triangle-free with alpha <= k-2).
  void local_edge_bounds (const std::vector<int> &L, int dlo, int dhi) {
    for (int v = 0; v < n; v++) {
      int capH = 0, capD = 0;
      for (int d = dlo; d <= dhi; d++) {
        int m = n - 1 - d;
        if (m >= 0 && m < (int) L.size () && L[m] > 0)
          capH = std::max (capH, L[m]), capD = std::max (capD, d + 1);
      }
      if (!capH) continue;
      std::string vs = std::to_string (v);
      int a0 = maxvar + 1;
      size_t c0 = clauses.size ();
      std::vector<int> ys;
      for (int b = 1; b < n; b++)
        for (int a = 0; a < b; a++) {
          if (a == v || b == v) continue;
          int y = ++maxvar, x = evar (a, b), xa = evar (a, v), xb = evar (b, v);
          add ({-y, x}), add ({-y, -xa}), add ({-y, -xb});
          add ({y, -x, xa, xb});
          ys.push_back (y);
        }
      sections.push_back ({"hv-def vertex=" + vs + " y=" + std::to_string (a0) +
                               ".." + std::to_string (maxvar) +
                               " order: pairs a<b colex, a,b != v",
                           c0, clauses.size ()});
      int a1 = maxvar + 1;
      c0 = clauses.size ();
      capH = std::min (capH, (int) ys.size ());
      std::vector<int> OH = totalizer (ys, 0, ys.size (), capH);
      sections.push_back ({"hv-count vertex=" + vs + " encoding=totalizer(cap=" +
                               std::to_string (capH) + ") aux=" + std::to_string (a1) +
                               ".." + std::to_string (maxvar),
                           c0, clauses.size ()});
      std::vector<int> lits;
      for (int u = 0; u < n; u++) if (u != v) lits.push_back (evar (u, v));
      int a2 = maxvar + 1;
      c0 = clauses.size ();
      capD = std::min (capD, (int) lits.size ());
      std::vector<int> OD = totalizer (lits, 0, lits.size (), capD);
      sections.push_back ({"hv-degree vertex=" + vs + " encoding=totalizer(cap=" +
                               std::to_string (capD) + ") aux=" + std::to_string (a2) +
                               ".." + std::to_string (maxvar),
                           c0, clauses.size ()});
      c0 = clauses.size ();
      std::string tab;
      for (int d = dlo; d <= dhi; d++) {
        int m = n - 1 - d;
        if (m < 0 || m >= (int) L.size () || L[m] <= 0) continue;
        int need = std::min (L[m], (int) ys.size ());
        // deg <= d is -OD[d] (OD[d] = deg >= d+1); if d+1 > |OD| it always holds
        clause_t c;
        if (d < (int) OD.size ()) c.push_back (OD[d]);
        c.push_back (OH[need - 1]);
        add (c);
        tab += " d" + std::to_string (d) + ":" + std::to_string (L[m]);
      }
      sections.push_back ({"hv-bound vertex=" + vs + " (deg<=d -> e(H_v)>=L)" + tab,
                           c0, clauses.size ()});
    }
  }

  // edges with both ends in [from, n)  (e.g. H_0 = G - N[0] when N(0)={1..from-1})
  void block_edge_bounds (int from, int lo, int hi) {
    std::vector<int> lits;
    for (int j = from + 1; j < n; j++)
      for (int i = from; i < j; i++) lits.push_back (evar (i, j));
    cardinality (lits, lo, hi, "edges-in-block from=" + std::to_string (from));
  }
  void edge_bounds (int lo, int hi) {
    std::vector<int> lits;
    for (int v = 1; v <= nv; v++) lits.push_back (v);
    cardinality (lits, lo, hi, "edges");
  }

  // DIMACS clauses (comments and p-line ignored).
  bool extra_file (const char *path) {
    FILE *f = fopen (path, "r");
    if (!f) return false;
    begin (std::string ("extra ") + path);
    clause_t c;
    char line[1 << 16];
    while (fgets (line, sizeof line, f)) {
      if (line[0] == 'c' || line[0] == 'p') continue;
      char *s = line, *e;
      for (;;) {
        long x = strtol (s, &e, 10);
        if (e == s) break;
        s = e;
        if (x == 0) add (c), c.clear ();
        else c.push_back ((int) x);
      }
    }
    if (!c.empty ()) add (c);
    fclose (f);
    end ();
    return true;
  }

  void write (const char *path) const {
    FILE *f = fopen (path, "w");
    fprintf (f, "c satcore base CNF: (3,%d,%d)-graphs, var(i,j)=j*(j-1)/2+i+1 (i<j, 0-based)\n", k, n);
    fprintf (f, "c lazy clauses (not here): all-positive independent %d-set clauses\n", k);
    for (auto &s : comments) fprintf (f, "c case %s\n", s.c_str ());
    fprintf (f, "p cnf %d %zu\n", maxvar, clauses.size ());
    size_t si = 0;
    for (size_t i = 0; i < clauses.size (); i++) {
      while (si < sections.size () && sections[si].first == i &&
             sections[si].last == i) {  // empty section
        fprintf (f, "c BEGIN %s\nc END\n", sections[si].tag.c_str ());
        si++;
      }
      if (si < sections.size () && sections[si].first == i)
        fprintf (f, "c BEGIN %s\n", sections[si].tag.c_str ());
      for (int l : clauses[i]) fprintf (f, "%d ", l);
      fprintf (f, "0\n");
      if (si < sections.size () && sections[si].last == i + 1)
        fprintf (f, "c END\n"), si++;
    }
    fclose (f);
  }
};

// ---------------------------------------------------------------- graphs
static inline std::string graph6 (int n, const set_t *adj) {
  std::string s (1, (char) (n + 63));
  int x = 0, nb = 0;
  for (int j = 1; j < n; j++)
    for (int i = 0; i < j; i++) {
      x = (x << 1) | (int) ((adj[i] >> j) & 1);
      if (++nb == 6) s += (char) (x + 63), x = 0, nb = 0;
    }
  if (nb) s += (char) ((x << (6 - nb)) + 63);
  return s;
}

static inline bool triangle_free (int n, const set_t *adj) {
  for (int u = 0; u < n; u++)
    for (set_t V = adj[u] & ~(bit (u + 1) - 1); V; V &= V - 1)
      if (adj[u] & adj[lowb (V)]) return false;
  return true;
}

// ---------------------------------------------------------------- propagator
struct Propagator : CaDiCaL::ExternalPropagator {
  Core core;
  bool forgettable_external = true;
  size_t model_batch = 64;
  clause_t rcl;
  size_t rpos = 0;
  bool in_reason = false;
  std::vector<clause_t> extq;
  std::vector<set_t> extq_set;
  set_t last_set = 0;  // k-set of the clause being handed to the solver
  size_t epos = 0;
  uint64_t model_checks = 0, model_fail = 0, ext_clauses = 0, reasons = 0;

  // optional decision order: list of solver vars, decided in this order with
  // sign decide_sign (+1 edge, -1 non-edge); empty = solver's own heuristic
  std::vector<int> decide_order;
  int decide_sign = 1;
  uint64_t decisions = 0;

  Propagator (int n, int k) : core (n, k) {}

  int cb_decide () override {
    for (int v : decide_order)
      if (!core.sval[v]) { decisions++; return decide_sign * v; }
    return 0;
  }

  void notify_assignment (const std::vector<int> &lits) override {
    for (int l : lits) core.assign (l);
  }
  void notify_new_decision_level () override { core.new_level (); }
  void notify_backtrack (size_t l) override { core.backtrack (l); }
  int cb_propagate () override { return core.next_prop (); }
  int cb_add_reason_clause_lit (int plit) override {
    if (!in_reason) {
      int t = abs (plit);
      core.clause_of (core.reason[t], rcl);
      // propagated literal first
      for (size_t i = 0; i < rcl.size (); i++)
        if (rcl[i] == t) std::swap (rcl[0], rcl[i]);
      rpos = 0, in_reason = true, reasons++;
      last_set = core.reason[t];
    }
    if (rpos < rcl.size ()) return rcl[rpos++];
    in_reason = false;
    return 0;
  }
  bool cb_check_found_model (const std::vector<int> &model) override {
    model_checks++;
    set_t adj[64] = {0};
    for (int l : model)
      if (l > 0 && l < (int) core.vpairs.size ())
        for (int p : core.vpairs[l]) {
          int a = core.eu[p], b = core.ev[p];
          adj[a] |= bit (b), adj[b] |= bit (a);
        }
    std::vector<set_t> sets;
    Core::find_indep (core.n, core.k, adj, model_batch, sets);
    if (sets.empty ()) return true;
    model_fail++;
    for (set_t S : sets) {
      extq.emplace_back ();
      extq_set.push_back (S);
      core.clause_of (S, extq.back ());
    }
    return false;
  }
  bool cb_has_external_clause (bool &forget) override {
    forget = forgettable_external;
    return !extq.empty ();
  }
  int cb_add_external_clause_lit () override {
    clause_t &c = extq.back ();
    last_set = extq_set.back ();
    if (epos < c.size ()) return c[epos++];
    extq.pop_back ();
    extq_set.pop_back ();
    epos = 0;
    ext_clauses++;
    return 0;
  }
};

// ---------------------------------------------------------------- proof capture
// Records the CaDiCaL clause id of every original clause: the first base_m are
// the base CNF (in order), later ones are lazy independent-set clauses (ext).
// CaDiCaL may derive clauses (root-level strengthening) while the base CNF is
// still being added, so base ids need not be 1..m.
struct Capture : CaDiCaL::Tracer {
  int64_t base_m = 0, seen_base = 0;
  bool id_mismatch = false, restored = false;
  FILE *ext = 0;
  FILE *sets = 0;               // vertex set of each ext clause (same order)
  const set_t *last_set = 0;    // points to the producer's current k-set
  std::vector<int64_t> base_ids, ext_ids;
  void add_original_clause (int64_t id, bool, const std::vector<int> &c,
                            bool rest) override {
    if (rest) restored = true;
    if ((int64_t) seen_base < base_m) {
      seen_base++;
      if (id != seen_base) id_mismatch = true;  // harmless: renumbered below
      base_ids.push_back (id);
      return;
    }
    ext_ids.push_back (id);
    if (ext) {
      for (int l : c) fprintf (ext, "%d ", l);
      fprintf (ext, "0\n");
    }
    if (sets) {
      set_t S = last_set ? *last_set : 0;
      for (set_t A = S; A; A &= A - 1) fprintf (sets, "%d ", lowb (A));
      fprintf (sets, "\n");
    }
  }
};

// Renumber CaDiCaL's ASCII LRAT so that the input formula is
// base (ids 1..m) followed by ext clauses (ids m+1..m+E, in ext.cnf order).
// Derived clause ids d become d + m + E (injective, order preserving, > m+E).
static inline bool renumber_lrat (const char *in, const char *out,
                                  const std::vector<int64_t> &base,
                                  const std::vector<int64_t> &ext) {
  std::unordered_map<int64_t, int64_t> omap;
  int64_t m = base.size (), E = ext.size ();
  for (size_t i = 0; i < base.size (); i++) omap[base[i]] = 1 + (int64_t) i;
  for (size_t i = 0; i < ext.size (); i++) omap[ext[i]] = m + 1 + (int64_t) i;
  auto map = [&] (int64_t id) -> int64_t {
    int64_t a = id < 0 ? -id : id, r;
    auto it = omap.find (a);
    r = it != omap.end () ? it->second : a + m + E;
    return id < 0 ? -r : r;
  };
  FILE *f = fopen (in, "r"), *g = fopen (out, "w");
  if (!f || !g) return false;
  std::vector<char> buf (1 << 20);
  std::string line;
  int ch;
  // token based: id [d ids 0 | lits 0 hints 0]
  auto rd = [&] (int64_t &x, bool &isd) -> bool {
    isd = false;
    int c;
    do c = getc (f); while (c == ' ' || c == '\n' || c == '\r');
    if (c == EOF) return false;
    if (c == 'd') { isd = true; return true; }
    bool neg = false;
    if (c == '-') neg = true, c = getc (f);
    x = 0;
    while (c >= '0' && c <= '9') x = 10 * x + (c - '0'), c = getc (f);
    if (neg) x = -x;
    return true;
  };
  (void) ch;
  int64_t x = 0;
  bool isd;
  while (rd (x, isd)) {
    int64_t id = x;
    fprintf (g, "%lld", (long long) map (id));
    if (!rd (x, isd)) break;
    if (isd) {
      fprintf (g, " d");
      while (rd (x, isd) && x != 0) fprintf (g, " %lld", (long long) map (x));
      fprintf (g, " 0\n");
      continue;
    }
    // literals
    while (x != 0) {
      fprintf (g, " %lld", (long long) x);
      rd (x, isd);
    }
    fprintf (g, " 0");
    while (rd (x, isd) && x != 0) fprintf (g, " %lld", (long long) map (x));
    fprintf (g, " 0\n");
  }
  fclose (f), fclose (g);
  return true;
}

// ---------------------------------------------------------------- terminator
struct Timer : CaDiCaL::Terminator {
  std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now ();
  double limit = 0;  // seconds, 0 = none
  double elapsed () const {
    return std::chrono::duration<double> (std::chrono::steady_clock::now () - t0).count ();
  }
  bool terminate () override { return limit > 0 && elapsed () > limit; }
};

}  // namespace satcore
