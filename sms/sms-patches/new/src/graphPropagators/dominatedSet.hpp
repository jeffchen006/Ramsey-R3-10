#ifndef _DOMINATED_SET_CHECKER_H_
#define _DOMINATED_SET_CHECKER_H_

// Lazy propagator (agent sms): forbid an independent s-set S with at least m common
// non-neighbours outside S ("not A_s(m)" of notes/cases.md Sec 6.3). On a partial graph it searches
// S (pairs assigned non-edge) and m vertices X whose pairs to S are all assigned non-edges; it then
// adds the clause "some pair inside S or between S and X is an edge" (C(s,2) + s*m literals).
// Checked on every full assignment too, so it is exact.

#include "../useful.h"
#include "../graphChecker.hpp"
#include <cstdint>

class DominatedSetChecker : public PartiallyDefinedGraphChecker
{
  int s, m;
  vector<uint64_t> nonAdj;
  vector<int> chosen;
  uint64_t foundX = 0;
  bool search(uint64_t cand, uint64_t common, int depth);
  void checkProperty(const adjacency_matrix_t &matrix);

public:
  DominatedSetChecker(int s, int m, int frequency) : PartiallyDefinedGraphChecker(frequency), s(s), m(m)
  {
    name = "DominatedSetChecker";
  }
};

#endif
