// Unit tests for core.hpp against brute force.
// Simulates a solver: random assignments in levels, applies returned
// propagations, random backtracks; at each fixpoint checks soundness and
// completeness of conflicts and propagations by enumerating all k-sets.
#include "core.hpp"
#include <algorithm>
#include <random>

using namespace satcore;

static std::mt19937_64 rng (12345);
static int fails = 0;
#define CHECK(c, ...) do { if (!(c)) { fails++; fprintf (stderr, "FAIL %s:%d ", __FILE__, __LINE__); fprintf (stderr, __VA_ARGS__); fprintf (stderr, "\n"); if (fails > 10) exit (1); } } while (0)

static void kset_rec (int n, int k, int start, set_t S, int size,
                      std::vector<set_t> &out) {
  if (size == k) { out.push_back (S); return; }
  for (int v = start; v <= n - (k - size); v++)
    kset_rec (n, k, v + 1, S | bit (v), size + 1, out);
}

// count (#false pairs, #unassigned pairs, unassigned var) in S
static void classify (const Core &c, set_t S, int &nf, int &nu, int &uvar) {
  nf = nu = 0, uvar = 0;
  for (set_t A = S; A; A &= A - 1) {
    int a = lowb (A);
    for (set_t B = S & ~(bit (a + 1) - 1); B; B &= B - 1) {
      int v = evar (a, lowb (B));
      if (c.val[v] < 0) nf++;
      else if (c.val[v] == 0) nu++, uvar = v;
    }
  }
}

static void run (int n, int k, bool props, int rounds, bool orbits = false) {
  std::vector<set_t> ksets;
  kset_rec (n, k, 0, 0, 0, ksets);
  int pairs = k * (k - 1) / 2;
  uint64_t conflicts = 0, propsn = 0, fix = 0;
  for (int r = 0; r < rounds; r++) {
    Core c (n, k);
    c.use_props = props;
    int nvars = c.nv;
    if (orbits) {  // random map pair -> solver var, about 2-3 pairs per var
      nvars = std::max (1, c.nv / (2 + (int) (rng () % 2)));
      std::vector<int> m (c.nv + 1, 0);
      for (int p = 1; p <= c.nv; p++) m[p] = p <= nvars ? p : 1 + rng () % nvars;
      std::vector<int> perm (c.nv);
      for (int p = 0; p < c.nv; p++) perm[p] = m[p + 1];
      std::shuffle (perm.begin (), perm.end (), rng);
      for (int p = 0; p < c.nv; p++) m[p + 1] = perm[p];
      c.set_map (m);
    }
    double pfalse = 0.5 + 0.45 * (rng () % 1000) / 1000.0;
    std::vector<int> vars;
    for (int v = 1; v <= nvars; v++) vars.push_back (v);
    std::shuffle (vars.begin (), vars.end (), rng);
    size_t vi = 0;
    while (vi < vars.size ()) {
      // decide a batch at a new level
      c.new_level ();
      int batch = 1 + rng () % 4;
      for (int b = 0; b < batch && vi < vars.size (); vi++) {
        int v = vars[vi];
        if (c.sval[v]) continue;
        c.assign ((rng () % 1000) < pfalse * 1000 ? -v : v);
        b++;
      }
      // propagate to fixpoint
      bool conflict = false;
      for (;;) {
        int t = c.next_prop ();
        if (!t) break;
        set_t S = c.reason[t];
        CHECK (popc (S) == k, "reason size");
        int nf, nu, uv;
        classify (c, S, nf, nu, uv);
        int tin = 0, tun = 0;  // pairs of var t inside S, unassigned ones
        for (int p : c.vpairs[t])
          if (S & bit (c.eu[p]) && S & bit (c.ev[p])) tin++, tun += c.val[p] == 0;
        CHECK (tin > 0, "target not in S");
        if (c.sval[t] < 0) {
          CHECK (nf == pairs, "conflict set not all false");
          conflict = true;
          conflicts++;
          break;
        }
        CHECK (c.sval[t] == 0 && nu == tun && nf == pairs - tun && tun >= 1,
               "bad propagation");
        (void) uv;
        CHECK (props, "propagation in conflict-only mode");
        propsn++;
        c.assign (t);
      }
      if (!conflict) {
        fix++;
        // completeness at fixpoint
        for (set_t S : ksets) {
          int nf, nu, uv;
          classify (c, S, nf, nu, uv);
          CHECK (nf < pairs, "missed conflict n=%d k=%d", n, k);
          if (props) CHECK (!(nf == pairs - 1 && nu == 1), "missed propagation");
        }
      }
      if (conflict || rng () % 5 == 0) {
        if (c.level () > 0) {
          size_t nl = rng () % c.level ();
          c.backtrack (nl);
          // re-add vars for later
          vi = std::min (vi, (size_t) (rng () % (vi + 1)));
          // a solver re-propagates after backtrack: we must still be at a
          // consistent state; edges processed before stay processed.
          // To mimic re-notification of kept out-of-order literals, nothing.
          if (conflict) {
            // after a conflict, the remaining state is still a fixpoint of
            // earlier levels only if all their edges were processed; we
            // check again after the next batch.
          }
        }
      }
    }
  }
  printf ("n=%d k=%d props=%d rounds=%d fixpoints=%lu conflicts=%lu props=%lu\n",
          n, k, (int) props, rounds, (unsigned long) fix,
          (unsigned long) conflicts, (unsigned long) propsn);
}

static void test_find_indep () {
  for (int r = 0; r < 300; r++) {
    int n = 4 + rng () % 10, k = 2 + rng () % 4;
    if (k > n) k = n;
    set_t adj[64] = {0};
    double p = (rng () % 100) / 100.0;
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++)
        if ((rng () % 100) < p * 100) adj[i] |= bit (j), adj[j] |= bit (i);
    std::vector<set_t> ksets, out;
    kset_rec (n, k, 0, 0, 0, ksets);
    size_t brute = 0;
    for (set_t S : ksets) {
      bool ind = true;
      for (set_t A = S; A; A &= A - 1) if (adj[lowb (A)] & S) ind = false;
      brute += ind;
    }
    size_t got = Core::find_indep (n, k, adj, 1u << 30, out);
    CHECK (got == brute, "find_indep count %zu vs %zu (n=%d k=%d)", got, brute, n, k);
    for (set_t S : out)
      for (set_t A = S; A; A &= A - 1) CHECK (!(adj[lowb (A)] & S), "not independent");
  }
  printf ("find_indep ok\n");
}

int main () {
  setvbuf (stdout, 0, _IONBF, 0);
  // evar is a bijection onto 1..C(n,2) in colex order
  { int x = 1; for (int j = 1; j < 10; j++) for (int i = 0; i < j; i++) CHECK (evar (i, j) == x++, "evar"); }
  test_find_indep ();
  run (8, 3, true, 400);
  run (9, 4, true, 400);
  run (10, 4, false, 300);
  run (11, 5, true, 300);
  run (12, 5, true, 200);
  run (13, 6, true, 100);
  run (14, 4, true, 100);
  run (9, 4, true, 300, true);
  run (11, 5, true, 300, true);
  run (12, 4, true, 200, true);
  run (13, 6, true, 100, true);
  if (fails) { printf ("FAILED %d\n", fails); return 1; }
  printf ("all tests ok\n");
  return 0;
}
