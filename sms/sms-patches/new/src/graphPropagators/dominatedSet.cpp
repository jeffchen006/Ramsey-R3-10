#include "dominatedSet.hpp"
#include <stdexcept>

// cand: vertices that can extend S (non-adjacent to all chosen, higher index);
// common: vertices non-adjacent (assigned) to all chosen vertices of S, not in S.
bool DominatedSetChecker::search(uint64_t cand, uint64_t common, int depth)
{
  if (depth == s)
  {
    if (__builtin_popcountll(common) >= m)
    {
      foundX = common;
      return true;
    }
    return false;
  }
  while (cand)
  {
    if (__builtin_popcountll(cand) < s - depth)
      return false;
    int v = __builtin_ctzll(cand);
    cand &= ~(1ULL << v);
    // common non-neighbours after adding v: must keep >= m outside S; remaining S vertices come from
    // the same set, so |common & nonAdj[v]| >= m + (s - depth - 1) is necessary
    uint64_t nc = common & nonAdj[v];
    if (__builtin_popcountll(nc) < m + (s - depth - 1))
      continue;
    chosen[depth] = v;
    if (search(cand & nonAdj[v], nc, depth + 1))
      return true;
  }
  return false;
}

void DominatedSetChecker::checkProperty(const adjacency_matrix_t &matrix)
{
  int n = (int)matrix.size();
  if (n > 64)
    throw std::runtime_error("DominatedSetChecker supports at most 64 vertices");
  nonAdj.assign(n, 0);
  chosen.assign(s, -1);
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
      if (matrix[i][j] == truth_value_false)
      {
        nonAdj[i] |= 1ULL << j;
        nonAdj[j] |= 1ULL << i;
      }
  uint64_t all = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
  if (!search(all, all, 0))
    return;
  // foundX excludes S automatically (a vertex is not in its own nonAdj)
  forbidden_graph_t g;
  for (int a = 0; a < s; a++)
    for (int b = a + 1; b < s; b++)
      g.push_back({truth_value_false, {std::min(chosen[a], chosen[b]), std::max(chosen[a], chosen[b])}});
  int taken = 0;
  uint64_t X = foundX;
  while (X && taken < m)
  {
    int x = __builtin_ctzll(X);
    X &= ~(1ULL << x);
    taken++;
    for (int a = 0; a < s; a++)
      g.push_back({truth_value_false, {std::min(chosen[a], x), std::max(chosen[a], x)}});
  }
  throw g;
}
