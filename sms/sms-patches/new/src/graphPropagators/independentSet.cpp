#include "independentSet.hpp"
#include <stdexcept>

// Greedy colouring bound: number of colour classes needed for cand in the non-edge graph.
// A clique (= independent set of G) inside cand has at most that many vertices.
static int colourBound(const vector<uint64_t> &nonAdj, uint64_t cand, int need)
{
  int colours = 0;
  while (cand)
  {
    colours++;
    if (colours >= need)
      return colours; // bound is already large enough; stop early
    uint64_t q = cand;
    while (q)
    {
      int v = __builtin_ctzll(q);
      q &= ~(1ULL << v);
      q &= ~nonAdj[v]; // vertices in the same colour class must be pairwise non-adjacent in nonAdj
      cand &= ~(1ULL << v);
    }
  }
  return colours;
}

bool IndependentSetChecker::search(uint64_t cand, int depth)
{
  if (depth == k)
    return true;
  int need = k - depth;
  while (cand)
  {
    if (__builtin_popcountll(cand) < need)
      return false;
    if (colourBound(nonAdj, cand, need) < need)
      return false;
    int v = __builtin_ctzll(cand);
    cand &= ~(1ULL << v);
    chosen[depth] = v;
    if (search(cand & nonAdj[v], depth + 1))
      return true;
  }
  return false;
}

// A: vertices joined by assigned non-edges to all chosen vertices.
// B: (only if !used) vertices joined to the chosen ones by non-edges except exactly one unassigned pair.
bool IndependentSetChecker::searchNear(uint64_t A, uint64_t B, int depth, bool used)
{
  if (depth == k)
    return true;
  int need = k - depth;
  while (A | B)
  {
    if (__builtin_popcountll(A | B) < need)
      return false;
    // colour bound on A; one extra vertex may come from B (it uses the single unknown pair)
    if (colourBound(nonAdj, A, need) + (B ? 1 : 0) < need)
      return false;
    if (A)
    {
      int v = __builtin_ctzll(A);
      A &= ~(1ULL << v);
      chosen[depth] = v;
      uint64_t nA = A & nonAdj[v];
      uint64_t nB = used ? 0 : ((B & nonAdj[v]) | (A & unk[v]));
      if (searchNear(nA, nB, depth + 1, used))
        return true;
    }
    else
    {
      int v = __builtin_ctzll(B);
      B &= ~(1ULL << v);
      chosen[depth] = v;
      if (searchNear(A & nonAdj[v], 0, depth + 1, true))
        return true;
    }
  }
  return false;
}

void IndependentSetChecker::checkProperty(const adjacency_matrix_t &matrix)
{
  n = (int)matrix.size();
  if (n > 64)
    throw std::runtime_error("IndependentSetChecker supports at most 64 vertices");
  nonAdj.assign(n, 0);
  unk.assign(n, 0);
  chosen.assign(k, -1);
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
      if (matrix[i][j] == truth_value_false)
      {
        nonAdj[i] |= 1ULL << j;
        nonAdj[j] |= 1ULL << i;
      }
      else if (matrix[i][j] == truth_value_unknown)
      {
        unk[i] |= 1ULL << j;
        unk[j] |= 1ULL << i;
      }

  uint64_t all = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
  if (!search(all, 0) && !(propagate && searchNear(all, 0, 0, false)))
    return;

  // forbidden partial graph: all pairs of the k-set are non-edges (the clause says: one is an edge)
  forbidden_graph_t g;
  for (int a = 0; a < k; a++)
    for (int b = a + 1; b < k; b++)
      g.push_back({truth_value_false, {std::min(chosen[a], chosen[b]), std::max(chosen[a], chosen[b])}});
  throw g;
}
