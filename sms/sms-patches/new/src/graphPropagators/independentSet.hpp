#ifndef _INDEPENDENT_SET_CHECKER_H_
#define _INDEPENDENT_SET_CHECKER_H_

// Lazy "no independent set of size k" propagator (added by agent sms, R(3,10) project).
// On a partially defined graph, search for k vertices whose pairs are all assigned non-edges.
// If found, throw that set of non-edges; SMS adds the clause "at least one of these pairs is an edge".
// The check on fully defined graphs is always done, so the result is exact.
// With propagate = true it also finds k-sets with all pairs non-edges except one unassigned pair;
// the thrown clause is then unit and forces that pair to be an edge (as the eager encoding would).

#include "../useful.h"
#include "../graphChecker.hpp"
#include <cstdint>

class IndependentSetChecker : public PartiallyDefinedGraphChecker
{
  int k;
  int n = 0;
  vector<uint64_t> nonAdj; // nonAdj[v]: bitset of vertices u with (u,v) assigned false
  vector<uint64_t> unk;    // unk[v]: bitset of vertices u with (u,v) unassigned
  vector<int> chosen;
  bool search(uint64_t cand, int depth);
  bool searchNear(uint64_t A, uint64_t B, int depth, bool used);
  void checkProperty(const adjacency_matrix_t &matrix);

public:
  bool propagate = false; // also report k-sets with exactly one unassigned pair (clause becomes unit)
  IndependentSetChecker(int k, int frequency, bool propagate = false) : PartiallyDefinedGraphChecker(frequency), k(k), propagate(propagate)
  {
    name = "IndependentSetChecker";
  }
};

#endif
