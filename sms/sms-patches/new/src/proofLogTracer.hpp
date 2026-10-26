#ifndef _PROOF_LOG_TRACER_H_
#define _PROOF_LOG_TRACER_H_

// Proof log with antecedents that also records clauses the solver did not derive itself
// (input clauses and clauses from the external propagator: symmetry breaking, other checkers,
// solution blocking). Added by agent sms (R(3,10) project). Text format, one event per line:
//   o ID lit... 0                 original clause (input or external), with its CaDiCaL ID
//   r ID lit... 0                 restored original clause
//   a ID lit... 0 hint... 0       derived clause with LRAT antecedents
//   d ID                          deletion
//   w ID                          weakened (moved to reconstruction stack)
// sms/lratlog2lrat.py converts this to a DIMACS file (input + external clauses) and an LRAT proof.

#include "../cadical_sms/src/tracer.hpp"
#include <cstdio>
#include <vector>
#include <cstdint>
#include <string>

class ProofLogTracer : public CaDiCaL::Tracer
{
  FILE *f;

  void lits(const std::vector<int> &c)
  {
    for (int l : c)
      fprintf(f, " %d", l);
    fputs(" 0", f);
  }

public:
  ProofLogTracer(const std::string &path)
  {
    f = fopen(path.c_str(), "w");
    if (!f)
      throw std::runtime_error("cannot open proof log file");
    setvbuf(f, nullptr, _IOFBF, 1 << 24);
  }
  ~ProofLogTracer() { close(); }
  void flush()
  {
    if (f)
      fflush(f);
  }
  void close()
  {
    if (f)
    {
      fclose(f);
      f = nullptr;
    }
  }

  void add_original_clause(uint64_t id, bool, const std::vector<int> &c, bool restored = false) override
  {
    fprintf(f, "%c %lu", restored ? 'r' : 'o', (unsigned long)id);
    lits(c);
    fputc('\n', f);
  }
  void add_derived_clause(uint64_t id, bool, const std::vector<int> &c, const std::vector<uint64_t> &chain) override
  {
    fprintf(f, "a %lu", (unsigned long)id);
    lits(c);
    for (auto h : chain)
      fprintf(f, " %lu", (unsigned long)h);
    fputs(" 0\n", f);
  }
  void delete_clause(uint64_t id, bool, const std::vector<int> &) override { fprintf(f, "d %lu\n", (unsigned long)id); }
  void weaken_minus(uint64_t id, const std::vector<int> &) override { fprintf(f, "w %lu\n", (unsigned long)id); }
  void report_status(int status, uint64_t) override
  {
    fprintf(f, "s %d\n", status);
    fflush(f);
  }
};

#endif
