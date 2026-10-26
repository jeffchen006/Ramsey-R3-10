// satcore CLI: search for (3,k,n)-graphs (triangle-free, no independent k-set).
// See notes/status/satcore.md for usage.
#include "ramsey.hpp"
#include <csignal>

using namespace satcore;

static void usage () {
  printf (
      "usage: satcore -n N -k K [options]\n"
      "  --mode up|cegar      lazy clauses by user propagator (default) or CEGAR loop\n"
      "  --fix-nbhd D         N(0) = {1..D}\n"
      "  --pairmap FILE       lines 'i j v': pair {i,j} (0-based) has solver variable v\n"
      "                       (several pairs may share v; all pairs required). Default:\n"
      "                       v = j*(j-1)/2+i+1. Not combinable with lex/mtf/fix-nbhd/card.\n"
      "  --lex                adjacent-row lex symmetry breaking (Codish et al. 2019);\n"
      "                       with --fix-nbhd only inside blocks {1..D} and {D+1..n-1}\n"
      "  --lex-all            as --lex, but for all pairs i<j of a block (Codish sb*_l)\n"
      "  --mtf                maximal triangle-free (WLOG for existence questions)\n"
      "  --deg-min A --deg-max B   degree bounds for every vertex (totalizer)\n"
      "  --edges-min A --edges-max B  edge count bounds (totalizer)\n"
      "  --h-edges-min A --h-edges-max B  edges of H_0 = G - N[0] (needs --fix-nbhd)\n"
      "  --hv-min m:L,..      local edge bound: deg(v)<=d -> e(G-N[v]) >= L for m=n-1-d\n"
      "                       (L must be a proven lower bound for e(3,k-1,m)); d in deg range\n"
      "  --codeg-max C        every pair has <= C common neighbours (totalizer)\n"
      "  --extra FILE         extra DIMACS clauses (repeatable)\n"
      "  --case TEXT          case assumption text, written as 'c case' in base.cnf\n"
      "  --out FILE           append found graphs (graph6)\n"
      "  --max-sol M          enumerate up to M solutions (blocks each labelled graph)\n"
      "  --proof PREFIX       write PREFIX.base.cnf, PREFIX.ext.cnf (+ .ext.sets: vertex set\n"
      "                       of each ext clause), PREFIX.full.cnf and\n"
      "                       PREFIX.drat (or PREFIX.lrat with --lrat)\n"
      "  --lrat               LRAT proof (renumbered to PREFIX.full.cnf)\n"
      "  --write-cnf FILE     write base CNF and exit\n"
      "  --time SEC           wall-clock limit\n"
      "  --no-props           propagator: conflicts only, no propagation\n"
      "  --keep-lazy          lazy clauses irredundant (default: forgettable)\n"
      "  --cegar-batch B      sets added per model in CEGAR / model check (64)\n"
      "  --gen-cubes D FILE   write lookahead cubes (depth D) of the base CNF to FILE, exit\n"
      "  --decide ORDER       row+|row-|colex+|colex-: propagator picks decisions (pairs in\n"
      "                       row-major (0,1),(0,2).. or colex order; sign = edge/non-edge)\n"
      "  --phase-graph FILE   initial phases from the first graph6 graph in FILE\n"
      "  --config NAME        CaDiCaL configuration (default, plain, sat, unsat)\n"
      "  --set NAME=VAL       CaDiCaL option (repeatable)\n"
      "  --seed S             CaDiCaL seed\n"
      "  --report SEC         progress line every SEC seconds (default 60)\n"
      "  -q                   quiet\n");
}

static Timer timer;
static double report_every = 60, next_report = 60;
static Propagator *gprop = 0;
static CaDiCaL::Solver *gsolver = 0;
static bool quiet = false;

struct ReportingTimer : CaDiCaL::Terminator {
  bool terminate () override {
    double t = timer.elapsed ();
    if (!quiet && t >= next_report) {
      next_report = t + report_every;
      if (gprop)
        printf ("c [%.0fs] processed=%lu nodes=%lu props=%lu confl=%lu "
                "model_fail=%lu conflicts=%ld\n",
                t, (unsigned long) gprop->core.st.processed,
                (unsigned long) gprop->core.st.nodes,
                (unsigned long) gprop->core.st.props,
                (unsigned long) gprop->core.st.conflicts,
                (unsigned long) gprop->model_fail,
                (long) gsolver->get_statistic_value ("conflicts"));
      else
        printf ("c [%.0fs]\n", t);
      fflush (stdout);
    }
    return timer.terminate ();
  }
};

static volatile sig_atomic_t interrupted = 0;
static void on_sig (int) {
  interrupted = 1;
  if (gsolver) gsolver->terminate ();
}

int main (int argc, char **argv) {
  setvbuf (stdout, 0, _IOLBF, 0);
  int n = 0, k = 0, fixd = -1, dmin = 0, dmax = -1, emin = 0, emax = -1, hmin = 0, hmax = -1, codeg = -1;
  long max_sol = 1;
  std::string mode = "up", out, proof, writecnf, pairmap;
  std::vector<std::string> extras, sets, cases;
  std::string config, cubefile, decide, phasegraph, hvmin;
  int cubedepth = 0;
  bool lex = false, mtf = false, lexall = false;
  bool lrat = false, no_props = false, keep_lazy = false;
  int seed = -1;
  size_t batch = 64;
  for (int i = 1; i < argc; i++) {
    std::string a = argv[i];
    auto nxt = [&] () -> const char * {
      if (i + 1 >= argc) { fprintf (stderr, "missing value for %s\n", a.c_str ()); exit (1); }
      return argv[++i];
    };
    if (a == "-n") n = atoi (nxt ());
    else if (a == "-k") k = atoi (nxt ());
    else if (a == "--mode") mode = nxt ();
    else if (a == "--fix-nbhd") fixd = atoi (nxt ());
    else if (a == "--pairmap") pairmap = nxt ();
    else if (a == "--lex") lex = true;
    else if (a == "--lex-all") lex = lexall = true;
    else if (a == "--mtf") mtf = true;
    else if (a == "--deg-min") dmin = atoi (nxt ());
    else if (a == "--deg-max") dmax = atoi (nxt ());
    else if (a == "--edges-min") emin = atoi (nxt ());
    else if (a == "--edges-max") emax = atoi (nxt ());
    else if (a == "--codeg-max") codeg = atoi (nxt ());
    else if (a == "--hv-min") hvmin = nxt ();
    else if (a == "--h-edges-min") hmin = atoi (nxt ());
    else if (a == "--h-edges-max") hmax = atoi (nxt ());
    else if (a == "--extra") extras.push_back (nxt ());
    else if (a == "--case") cases.push_back (nxt ());
    else if (a == "--out") out = nxt ();
    else if (a == "--max-sol") max_sol = atol (nxt ());
    else if (a == "--proof") proof = nxt ();
    else if (a == "--lrat") lrat = true;
    else if (a == "--write-cnf") writecnf = nxt ();
    else if (a == "--time") timer.limit = atof (nxt ());
    else if (a == "--no-props") no_props = true;
    else if (a == "--keep-lazy") keep_lazy = true;
    else if (a == "--cegar-batch") batch = atol (nxt ());
    else if (a == "--set") sets.push_back (nxt ());
    else if (a == "--config") config = nxt ();
    else if (a == "--decide") decide = nxt ();
    else if (a == "--phase-graph") phasegraph = nxt ();
    else if (a == "--gen-cubes") cubedepth = atoi (nxt ()), cubefile = nxt ();
    else if (a == "--seed") seed = atoi (nxt ());
    else if (a == "--report") report_every = next_report = atof (nxt ());
    else if (a == "-q") quiet = true;
    else if (a == "-h" || a == "--help") { usage (); return 0; }
    else { fprintf (stderr, "unknown option %s\n", a.c_str ()); usage (); return 1; }
  }
  if (n < 2 || k < 2 || n > 62) { usage (); return 1; }

  // ---- pair -> variable map
  Core pm (n, k);
  if (!pairmap.empty ()) {
    if (lex || mtf || codeg >= 0 || !hvmin.empty () || fixd >= 0 || dmin > 0 || dmax >= 0 || emin > 0 || emax >= 0) {
      fprintf (stderr, "--pairmap: lex/mtf/fix-nbhd/degree/edge options not supported\n");
      return 1;
    }
    std::vector<int> m (pm.nv + 1, 0);
    FILE *f = fopen (pairmap.c_str (), "r");
    if (!f) { fprintf (stderr, "cannot read %s\n", pairmap.c_str ()); return 1; }
    char line[256];
    while (fgets (line, sizeof line, f)) {
      int i, j, v;
      if (line[0] == '#' || line[0] == 'c') continue;
      if (sscanf (line, "%d %d %d", &i, &j, &v) != 3) continue;
      if (i == j || i < 0 || j < 0 || i >= n || j >= n || v < 1) { fprintf (stderr, "bad pairmap line %s", line); return 1; }
      m[evar (i, j)] = v;
    }
    fclose (f);
    for (int p = 1; p <= pm.nv; p++)
      if (!m[p]) { fprintf (stderr, "pairmap: pair %d,%d missing\n", pm.eu[p], pm.ev[p]); return 1; }
    pm.set_map (m);
  }
  const int nsv = pm.vpairs.size ();  // solver vars of pairs are < nsv

  // ---- encoding
  Encoding enc (n, k);
  enc.pvar = pm.pvar;
  enc.maxvar = std::max (enc.maxvar, nsv - 1);
  for (auto &c : cases) enc.comments.push_back (c);
  if (fixd >= 0)
    enc.comments.push_back ("vertex 0 has degree " + std::to_string (fixd) +
                            ", relabelled so that N(0)={1.." + std::to_string (fixd) + "}");
  enc.triangles ();
  if (fixd >= 0) enc.fix_nbhd (fixd);
  for (auto &e : extras)
    if (!enc.extra_file (e.c_str ())) { fprintf (stderr, "cannot read %s\n", e.c_str ()); return 1; }
  if (lex) {
    if (fixd >= 0) enc.lex_rows ({{1, fixd + 1}, {fixd + 1, n}}, lexall);
    else enc.lex_rows ({{0, n}}, lexall);
  }
  if (mtf) enc.mtf ();
  if (dmin > 0 || dmax >= 0) enc.degree_bounds (dmin, dmax);
  if (emin > 0 || emax >= 0) enc.edge_bounds (emin, emax);
  if (codeg >= 0) enc.codegree_max (codeg);
  if (!hvmin.empty ()) {
    std::vector<int> L (n, 0);
    std::string t = hvmin;
    for (char &c : t) if (c == ',') c = ' ';
    char *q = &t[0], *e;
    for (;;) {
      long m = strtol (q, &e, 10);
      if (e == q || *e != ':') break;
      long l = strtol (e + 1, &q, 10);
      if (m >= 0 && m < n) L[m] = (int) l;
    }
    enc.comments.push_back ("local edge bound table (m:L) " + hvmin);
    enc.local_edge_bounds (L, std::max (dmin, 0), dmax >= 0 ? dmax : n - 1);
  }
  if (hmin > 0 || hmax >= 0) {
    if (fixd < 0) { fprintf (stderr, "--h-edges-* needs --fix-nbhd\n"); return 1; }
    enc.block_edge_bounds (fixd + 1, hmin, hmax);
  }
  if (!writecnf.empty ()) { enc.write (writecnf.c_str ()); return 0; }

  printf ("c satcore n=%d k=%d mode=%s vars=%d base_clauses=%zu\n", n, k,
          mode.c_str (), enc.maxvar, enc.clauses.size ());

  // ---- solver
  CaDiCaL::Solver solver;
  gsolver = &solver;
  signal (SIGINT, on_sig);
  signal (SIGTERM, on_sig);
  if (!config.empty () && !solver.configure (config.c_str ())) { fprintf (stderr, "bad config %s\n", config.c_str ()); return 1; }
  for (auto &s : sets) {
    std::string arg = "--" + s;
    if (!solver.set_long_option (arg.c_str ())) { fprintf (stderr, "bad CaDiCaL option %s\n", s.c_str ()); return 1; }
  }
  if (seed >= 0) solver.set ("seed", seed);
  if (quiet) solver.set ("quiet", 1);

  if (cubedepth > 0) {
    // cubes from CaDiCaL lookahead on the base CNF (no lazy clauses needed:
    // any set of cubes whose disjunction is a tautology over the base is a split)
    for (auto &c : enc.clauses) solver.clause (c);
    auto res = solver.generate_cubes (cubedepth);
    FILE *f = fopen (cubefile.c_str (), "w");
    size_t nc = 0;
    for (auto &cube : res.cubes) {
      for (int l : cube) fprintf (f, "%d ", l);
      fprintf (f, "0\n");
      nc++;
    }
    fclose (f);
    printf ("c gen-cubes status=%d cubes=%zu file=%s\n", res.status, nc, cubefile.c_str ());
    return 0;
  }

  Capture cap;
  FILE *extf = 0;
  std::string rawproof;
  if (!proof.empty ()) {
    enc.write ((proof + ".base.cnf").c_str ());
    extf = fopen ((proof + ".ext.cnf").c_str (), "w");
    cap.ext = extf;
    cap.sets = fopen ((proof + ".ext.sets").c_str (), "w");
    cap.base_m = enc.clauses.size ();
    if (lrat) {
      solver.set ("lrat", 1);
      solver.set ("binary", 0);
      rawproof = proof + ".raw.lrat";
    } else {
      solver.set ("binary", 0);
      rawproof = proof + ".drat";
    }
    solver.trace_proof (rawproof.c_str ());
    solver.connect_proof_tracer (&cap, lrat);
  }

  Propagator *prop = 0;
  if (mode == "up") {
    prop = new Propagator (n, k);
    prop->core.use_props = !no_props;
    prop->forgettable_external = !keep_lazy;
    prop->are_reasons_forgettable = !keep_lazy;
    prop->model_batch = batch;
    gprop = prop;
    solver.connect_external_propagator (prop);
    prop->core.set_map (pm.pvar);
    if (!decide.empty ()) {
      std::vector<char> seen (nsv, 0);
      auto push = [&] (int i, int j) {
        int v = pm.pvar[evar (i, j)];
        if (!seen[v]) seen[v] = 1, prop->decide_order.push_back (v);
      };
      if (decide.rfind ("row", 0) == 0) {
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) push (i, j);
      } else if (decide.rfind ("colex", 0) == 0) {
        for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) push (i, j);
      } else { fprintf (stderr, "bad --decide\n"); return 1; }
      prop->decide_sign = decide.back () == '-' ? -1 : 1;
    }
    for (int v = 1; v < nsv; v++)
      if (!pm.vpairs[v].empty ()) solver.add_observed_var (v);
  } else if (mode == "cegar") {
    for (int v = 1; v < nsv; v++)
      if (!pm.vpairs[v].empty ()) solver.freeze (v);  // no elimination of edge vars
  } else { fprintf (stderr, "bad mode\n"); return 1; }

  for (auto &c : enc.clauses) solver.clause (c);

  if (!phasegraph.empty ()) {
    FILE *f = fopen (phasegraph.c_str (), "r");
    char line[1 << 12];
    if (!f || !fgets (line, sizeof line, f)) { fprintf (stderr, "cannot read %s\n", phasegraph.c_str ()); return 1; }
    fclose (f);
    // graph6, n < 63: bits in colex order = our pair order
    const char *q = line;
    int gn = *q++ - 63;
    if (gn != n) { fprintf (stderr, "--phase-graph: graph has %d vertices\n", gn); return 1; }
    int bitpos = 0;
    for (int p = 1; p <= pm.nv; p++, bitpos++) {
      int c = q[bitpos / 6] - 63;
      int b = (c >> (5 - bitpos % 6)) & 1;
      solver.phase (b ? pm.pvar[p] : -pm.pvar[p]);
    }
  }

  ReportingTimer rt;
  solver.connect_terminator (&rt);

  FILE *outf = out.empty () ? 0 : fopen (out.c_str (), "a");
  long nsol = 0;
  uint64_t cegar_iter = 0, cegar_clauses = 0;
  set_t cegar_set = 0;
  cap.last_set = prop ? &prop->last_set : &cegar_set;
  int res = 0;
  for (;;) {
    res = solver.solve ();
    if (res != 10) break;
    set_t adj[64] = {0};
    for (int p = 1; p <= enc.nv; p++)
      if (solver.val (pm.pvar[p]) > 0) {
        int a = pm.eu[p], b = pm.ev[p];
        adj[a] |= bit (b), adj[b] |= bit (a);
      }
    std::vector<set_t> sets;
    Core::find_indep (n, k, adj, batch, sets);
    if (!sets.empty ()) {
      if (mode != "cegar") { fprintf (stderr, "satcore: BUG: model has independent %d-set\n", k); return 2; }
      cegar_iter++;
      for (set_t S : sets) {
        clause_t c;
        pm.clause_of (S, c);
        cegar_set = S;
        solver.clause (c);
        cegar_clauses++;
      }
      if (!quiet && cegar_iter % 100 == 0)
        printf ("c cegar iter=%lu clauses=%lu t=%.1f\n", (unsigned long) cegar_iter,
                (unsigned long) cegar_clauses, timer.elapsed ());
      continue;
    }
    if (!triangle_free (n, adj)) { fprintf (stderr, "satcore: BUG: triangle\n"); return 2; }
    std::string g6 = graph6 (n, adj);
    int e = 0, dlo = n, dhi = 0;
    for (int v = 0; v < n; v++) {
      int d = popc (adj[v]);
      e += d, dlo = std::min (dlo, d), dhi = std::max (dhi, d);
    }
    printf ("s GRAPH %s\nc graph n=%d e=%d deg=[%d,%d] t=%.2f\n", g6.c_str (), n, e / 2, dlo, dhi, timer.elapsed ());
    if (outf) fprintf (outf, "%s\n", g6.c_str ()), fflush (outf);
    if (++nsol >= max_sol) break;
    clause_t block;
    for (int v = 1; v < nsv; v++)
      if (!pm.vpairs[v].empty ()) block.push_back (solver.val (v) > 0 ? -v : v);
    solver.clause (block);  // note: not a valid proof step; enumeration runs only
  }
  double t = timer.elapsed ();
  const char *rs = res == 10 ? "SATISFIABLE" : res == 20 ? "UNSATISFIABLE" : "UNKNOWN";
  if (nsol > 0 && res != 10) rs = res == 20 ? "SATISFIABLE (enumeration complete)" : "SATISFIABLE (enumeration stopped)";
  printf ("s %s\nc solutions=%ld time=%.2f conflicts=%ld\n", rs, nsol, t,
          (long) solver.get_statistic_value ("conflicts"));
  if (prop)
    printf ("c prop processed=%lu nodes=%lu props=%lu confl=%lu stale=%lu "
            "reasons=%lu model_checks=%lu model_fail=%lu ext_clauses=%lu\n",
            (unsigned long) prop->core.st.processed, (unsigned long) prop->core.st.nodes,
            (unsigned long) prop->core.st.props, (unsigned long) prop->core.st.conflicts,
            (unsigned long) prop->core.st.stale, (unsigned long) prop->reasons,
            (unsigned long) prop->model_checks, (unsigned long) prop->model_fail,
            (unsigned long) prop->ext_clauses);
  if (mode == "cegar")
    printf ("c cegar iterations=%lu clauses=%lu\n", (unsigned long) cegar_iter,
            (unsigned long) cegar_clauses);
  if (outf) fclose (outf);

  if (!proof.empty ()) {
    solver.close_proof_trace ();
    solver.disconnect_proof_tracer (&cap);
    cap.ext = 0;
    if (cap.sets) fclose (cap.sets), cap.sets = 0;
    if (extf) fclose (extf);
    if (cap.id_mismatch) printf ("c note: base clause ids not 1..m (root-level derivations during input); renumbered\n");
    if (cap.restored) printf ("c WARNING: restored clauses seen in proof\n");
    if (nsol > 1) printf ("c WARNING: enumeration blocking clauses are not in the formula; proof invalid\n");
    size_t E = cap.ext_ids.size ();
    // full.cnf = base + ext
    {
      FILE *f = fopen ((proof + ".full.cnf").c_str (), "w");
      fprintf (f, "p cnf %d %zu\n", enc.maxvar, enc.clauses.size () + E);
      for (auto &c : enc.clauses) { for (int l : c) fprintf (f, "%d ", l); fprintf (f, "0\n"); }
      FILE *g = fopen ((proof + ".ext.cnf").c_str (), "r");
      char buf[1 << 16];
      while (fgets (buf, sizeof buf, g)) fputs (buf, f);
      fclose (g), fclose (f);
    }
    if (lrat) {
      if ((int64_t) cap.base_ids.size () != (int64_t) enc.clauses.size ())
        printf ("c WARNING: captured %zu base clauses, expected %zu\n", cap.base_ids.size (), enc.clauses.size ());
      renumber_lrat (rawproof.c_str (), (proof + ".lrat").c_str (), cap.base_ids, cap.ext_ids);
      remove (rawproof.c_str ());
    }
    printf ("c proof: %s.full.cnf (%zu base + %zu lazy clauses), %s\n", proof.c_str (),
            enc.clauses.size (), E, (proof + (lrat ? ".lrat" : ".drat")).c_str ());
  }
  if (prop) solver.disconnect_external_propagator ();
  return res;
}
