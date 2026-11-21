/* glue3.c - glue.c + per-input table of alpha(H[S]) for all S (GR 2013 Sec. 3; [Ang] 4.3), m <= TMAX.
 * Same interface and output set as glue.c. Changes: on each new set S_j, check every subset T of the
 * chosen sets that contains j: alpha(H - union T) <= K - |T| (table lookup, incremental unions);
 * the leaf alpha(G) <= K test is then implied (independent sets of G containing v are in H + v,
 * those without v are I_H + {u_i : i in T}), so no has_indep at the leaf.
 * Falls back to glue.c behaviour if m > TMAX.
 * glue5: + candidate index range limited by the edge budget (sets sorted by size);
 * glue4: + colouring bound (rem >= COLMIN) (clique search): split eligible sets into greedy classes of pairwise
 * incompatible sets; a valid completion takes <= 1 set per class, so prune if < rem classes, or if
 * edges + sum of the rem smallest class minima > EMAX (sets sorted by size). Skipped if a
 * self-compatible set is eligible (it may be repeated).
 * Based on glue.c - neighbourhood gluing extender (Goedgebeur-Radziszowski 2013, Sec. 3).
 *
 * Input (stdin): graph6 graphs H with alpha(H) <= K-1, triangle-free.
 * Output (stdout): graph6 graphs G = H + {u_1..u_d} + {v}, where v ~ u_i, u_i ~ S_i,
 *   S_i independent sets of H, such that G is triangle-free, alpha(G) <= K,
 *   EMIN <= e(G) <= EMAX, DMIN <= deg <= DMAX for all vertices.
 *   Vertex order of G: H = 0..m-1, u_i = m..m+d-1, v = m+d.
 *   No isomorphism rejection (pipe through nauty shortg).
 *
 * usage: glue -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX] [-q]
 *   defaults: EMAX=inf, EMIN=0, DMIN=D (v is a minimum degree vertex), DMAX=K.
 */
#include "gutil.h"
#include <getopt.h>
#include <time.h>
#ifndef COLMIN
#define COLMIN 3
#endif
#define CUT (void)0

static int K, D, EMAX = 1 << 30, EMIN = 0, DMIN = -1, DMAX = -1, quiet = 0;
static int skip5, skip6, skip7, use_profile, irreducible_only;
static int star_minimum, prefilter_overlap;
static int reverse_sizes, search_min, search_max;
static int minimum_degree, profile_order, maximum_sum[9], slack[16];
static int *base_slack;
static long long profile_rejected, ntested;
#ifdef COUNT_DEPTH
static uint64_t node_depth[16], attempt_depth[16], cap_depth[16], alpha_depth[16], empty_depth[16];
#define DEPTH_COUNT(w) ((void)++w[depth])
#else
#define DEPTH_COUNT(w) ((void)0)
#endif

static graph_t H;
static int m, eH, degH[64];
static set_t low_vertices;

/* candidates */
static int N, W;               /* number of candidates, words per bitset over candidates */
static set_t *cand;            /* cand[i] = vertex set */
static int *csz;
static uint64_t *comp;         /* comp[i*W..] compat bitset row */
static uint64_t *cont;
static uint64_t *selfc;        /* self-compatible candidates */
static uint64_t *Pbuf, *Qbuf;         /* cont[x*W..] candidates containing x */
static clock_t pair_time, search_time;

static long long nout, nleaf, nnodes;
static int chosen[64];
#define TMAX 26
static unsigned char *atab; static int use_tab;
static set_t uni_m[1 << 12];  /* uni_m[mask] = union of chosen sets in mask */
static void build_tab(void)
{
    size_t N2 = (size_t)1 << m;
    atab = realloc(atab, N2);
    atab[0] = 0;
    for (size_t S = 1; S < N2; S++) {
        int x = CTZ(S);
        unsigned char a = atab[S & (S - 1)], b = 1 + atab[S & ~H.adj[x] & ~BIT(x)];
        atab[S] = a > b ? a : b;
    }
}
static int cnt[64];

#ifdef BITPLANE_ATTACHMENTS
#if defined(CONVEX_STAR_BUDGET) || defined(STATIC_PROFILE_LOOKAHEAD) || defined(EXACT_SIZE_PLAN)
#error incompatible independent experiments
#endif
static set_t count_plane[16][3], capacity_plane[3];

static int count_at(int depth, int vertex)
{
    return (int)((count_plane[depth][0] >> vertex) & 1) +
           2 * (int)((count_plane[depth][1] >> vertex) & 1) +
           4 * (int)((count_plane[depth][2] >> vertex) & 1);
}

static void count_choice(int depth, set_t set)
{
    set_t low = count_plane[depth][0], middle = count_plane[depth][1];
    set_t carry = set & low;
    count_plane[depth+1][0] = low ^ set;
    count_plane[depth+1][1] = middle ^ carry;
    count_plane[depth+1][2] = count_plane[depth][2] ^ (carry & middle);
}
#define ACTIVE_COUNT(depth, vertex) count_at(depth, vertex)
#else
#define ACTIVE_COUNT(depth, vertex) cnt[vertex]
#endif

#ifdef CONVEX_STAR_BUDGET
#define UNATTAINABLE (-1000000)
static int convex_first_depth = 0;
static int star_upper[9][9][65];
static int convex_lower[16], convex_cap[16], convex_target, multiplier, free_count[64];
static set_t positive_penalty[16];
static long long convex_tested, convex_rejected;

static int convex_setup(int candidate_floor)
{
    convex_target = EMAX-eH-D;
    if (convex_target < 0 || convex_target > 64) return 0;
    int lower_bound = UNATTAINABLE;
    for (int price = 1; price <= 2*DMAX; ++price) {
        int bound = price * convex_target;
        for (int vertex = 0; vertex < m; ++vertex) {
            int smallest = minimum_degree - degH[vertex];
            if (smallest < 0) smallest = 0;
            int largest = DMAX - degH[vertex];
            if (largest > D) largest = D;
            int count = (price - degH[vertex] + 1) / 2;
            if (count < smallest) count = smallest;
            if (count > largest) count = largest;
            bound += count * (degH[vertex] + count - price);
        }
        if (bound > lower_bound) {
            multiplier = price;
            lower_bound = bound;
        }
    }
    positive_penalty[0] = 0;
    for (int vertex = 0; vertex < m; ++vertex) {
        int smallest = minimum_degree - degH[vertex];
        if (smallest < 0) smallest = 0;
        int largest = DMAX - degH[vertex];
        if (largest > D) largest = D;
        int count = (multiplier - degH[vertex] + 1) / 2;
        if (count < smallest) count = smallest;
        if (count > largest) count = largest;
        free_count[vertex] = count;
        if (count == 0) positive_penalty[0] |= BIT(vertex);
    }
    int present[9] = {0};
    for (int index = 0; index < N; ++index) present[csz[index]] = 1;
    for (int minimum = candidate_floor; minimum < DMAX; ++minimum) {
        for (int total = 0; total <= convex_target; ++total)
            star_upper[minimum][0][total] = total ? UNATTAINABLE : 0;
        for (int slots = 1; slots <= D; ++slots)
            for (int total = 0; total <= convex_target; ++total) {
                int best = UNATTAINABLE;
                for (int size = minimum; size < DMAX && size <= total; ++size)
                    if (present[size]) {
                        int previous = star_upper[minimum][slots-1][total-size];
                        if (previous == UNATTAINABLE) continue;
                        int bound = maximum_sum[size+1] + previous;
                        if (bound > best) best = bound;
                    }
                star_upper[minimum][slots][total] = best;
            }
    }
    convex_lower[0] = lower_bound + D*D;
    convex_cap[0] = 0;
    return star_upper[candidate_floor][D][convex_target] >= convex_lower[0];
}

static int convex_choice(int depth, int size, int edges, set_t neighbors)
{
    int remaining = D-depth-1;
    int total = EMAX-edges-size;
    if (total < 0) return 0;
    int cap = convex_cap[depth] + maximum_sum[size+1];
    int maximum = cap + star_upper[size][remaining][total];
    int lower = convex_lower[depth];
    for (set_t penalized = neighbors & positive_penalty[depth]; penalized; penalized &= penalized-1) {
        int vertex = CTZ(penalized);
        lower += degH[vertex] + 2*cnt[vertex] + 1 - multiplier;
    }
    ++convex_tested;
    if (depth >= convex_first_depth && lower > maximum) { ++convex_rejected; return 0; }
    set_t next = positive_penalty[depth];
    for (set_t vertices = neighbors & ~next; vertices; vertices &= vertices-1) {
        int vertex = CTZ(vertices);
        if (cnt[vertex] + 1 == free_count[vertex]) next |= BIT(vertex);
    }
    positive_penalty[depth+1] = next;
    convex_cap[depth+1] = cap;
    convex_lower[depth+1] = lower;
    return 1;
}
#endif

#ifdef STATIC_PROFILE_LOOKAHEAD
static int lookahead_depth = 4;
static long long lookahead_tested, lookahead_rejected;

static int degree_profile_possible(int depth)
{
    int remaining = D - depth;
    int final_sum = EMAX + eH - D;
    int star_floor = star_minimum > minimum_degree ? star_minimum : minimum_degree;
    int lower[64], upper[64], bonus[64] = {0};
    int sum_lower = 0, sum_upper = 0;
    for (int vertex = 0; vertex < m; ++vertex) {
        int partial = degH[vertex] + cnt[vertex];
        lower[vertex] = partial > minimum_degree ? partial : minimum_degree;
        upper[vertex] = partial + remaining < DMAX ? partial + remaining : DMAX;
        if (lower[vertex] > upper[vertex]) return 0;
        sum_lower += lower[vertex];
        sum_upper += upper[vertex];
    }
    if (sum_lower > final_sum || sum_upper < final_sum) return 0;
    for (int star = 0; star < depth; ++star) {
        set_t neighbors = cand[chosen[star]];
        int increment = 1 + POP(neighbors) - star_floor;
        if (increment)
            for (; neighbors; neighbors &= neighbors-1) bonus[CTZ(neighbors)] += increment;
    }
    for (int pass = 0; pass < 2; ++pass) {
        int changed = 0;
        for (int vertex = 0; vertex < m; ++vertex) {
            int requirement = bonus[vertex] - star_floor * degH[vertex];
            for (set_t neighbors = H.adj[vertex]; neighbors; neighbors &= neighbors-1)
                requirement += lower[CTZ(neighbors)];
            int old = lower[vertex], degree = old;
            while (degree <= upper[vertex] &&
                   maximum_sum[degree] - star_floor * degree < requirement) ++degree;
            if (degree > upper[vertex]) return 0;
            sum_lower += degree - old;
            if (sum_lower > final_sum) return 0;
            lower[vertex] = degree;
            changed |= degree != old;
        }
        if (!changed) break;
    }
    return 1;
}
#endif

static void output(void)
{
    graph_t G;
    memset(&G, 0, sizeof(G));
    G.n = m + D + 1;
    for (int x = 0; x < m; x++) G.adj[x] = H.adj[x];
    int v = m + D;
    for (int i = 0; i < D; i++) {
        int u = m + i;
        G.adj[u] |= BIT(v); G.adj[v] |= BIT(u);
        set_t s = cand[chosen[i]];
        G.adj[u] |= s;
        while (s) { int x = CTZ(s); s &= s - 1; G.adj[x] |= BIT(u); }
    }
    if (use_profile) {
        int degrees[64];
        for (int vertex = 0; vertex < G.n; ++vertex) degrees[vertex] = POP(G.adj[vertex]);
        for (int vertex = 0; vertex < G.n; ++vertex) {
            int total = 0;
            for (set_t remaining = G.adj[vertex]; remaining; remaining &= remaining-1)
                total += degrees[CTZ(remaining)];
            if (total > maximum_sum[degrees[vertex]]) return;
        }
    }
    nleaf++;
    if (!use_tab && !alpha_le(&G, K)) return;
    if (irreducible_only) {
        set_t vertices = BIT(G.n) - 1;
        for (int vertex = 0; vertex < G.n; ++vertex)
            for (set_t remaining = G.adj[vertex] & (BIT(vertex) - 1); remaining; remaining &= remaining-1) {
                int neighbor = CTZ(remaining);
                if (!has_indep(G.adj, vertices & ~(G.adj[vertex] | G.adj[neighbor]), K-1)) return;
            }
    }
    nout++;
    g6_write(stdout, &G);
}

static int first_bit_from(const uint64_t *b, int from)
{
    if (from >= N) return -1;
    int w = from >> 6;
    uint64_t x = b[w] & (~0ULL << (from & 63));
    for (;;) {
        if (x) return (w << 6) + CTZ(x);
        if (++w >= W) return -1;
        x = b[w];
    }
}

static int hix[65];            /* hix[s] = last candidate index with size <= s, -1 if none */
static uint64_t *nebuf[16];

static int first_bit_range(const uint64_t *b, int from, int to)
{
    if (from > to) return -1;
    int w = from >> 6, wt = to >> 6;
    uint64_t x = b[w] & (~0ULL << (from & 63));
    for (;;) {
        if (w == wt) { if ((to & 63) != 63) x &= (2ULL << (to & 63)) - 1; return x ? (w << 6) + CTZ(x) : -1; }
        if (x) return (w << 6) + CTZ(x);
        x = b[++w];
    }
}

#ifdef FAST_BOOLEAN_ROWS
typedef struct {
    const uint64_t *row;
    int current, end, endbit;
    uint64_t remaining;
} bit_cursor;

static bit_cursor start_cursor(const uint64_t *row, int from, int to)
{
    int word = from >> 6;
    bit_cursor cursor = {row, word, to >> 6, to & 63, row[word] & (UINT64_MAX << (from & 63))};
    if (cursor.current == cursor.end) cursor.remaining &= UINT64_MAX >> (63 - cursor.endbit);
    return cursor;
}

static int next_cursor(bit_cursor *cursor)
{
    while (!cursor->remaining) {
        if (cursor->current == cursor->end) return -1;
        cursor->remaining = cursor->row[++cursor->current];
        if (cursor->current == cursor->end) cursor->remaining &= UINT64_MAX >> (63 - cursor->endbit);
    }
    int result = 64 * cursor->current + CTZ(cursor->remaining);
    cursor->remaining &= cursor->remaining-1;
    return result;
}
#endif

static int independent_enough(set_t s, int depth)
{
    if (!use_tab || depth < 2) return 1;
    set_t full = BIT(m)-1;
    for (int mask = 3; mask < (1 << depth); ++mask) {
        int count = POP(mask);
        if (count < 2) continue;
        if (atab[full & ~(uni_m[mask] | s)] > K - 1 - count) return 0;
    }
    return 1;
}

#ifdef EXACT_SIZE_PLAN
static int planned[16], plan_order, group_count[9], plan_start[9], plan_end[9];
static uint16_t future_groups[16];
static long long size_plans;

static void search_plan(int depth, int first, const uint64_t *eligible)
{
    ++nnodes;
    DEPTH_COUNT(node_depth);
    if (depth == D) {
        for (int vertex = 0; vertex < m; ++vertex)
            if (degH[vertex] + cnt[vertex] < minimum_degree) return;
        int original[16];
        memcpy(original, chosen, D * sizeof *chosen);
        for (int index = 1; index < D; ++index) {
            int selected = chosen[index], position = index;
            while (position && chosen[position-1] > selected) {
                chosen[position] = chosen[position-1];
                --position;
            }
            chosen[position] = selected;
        }
        output();
        memcpy(chosen, original, D * sizeof *chosen);
        return;
    }
    int size = planned[depth], end = plan_end[size];
    uint64_t *next = nebuf[depth];
    for (int index = first_bit_range(eligible, first, end); index >= 0;
         index = first_bit_range(eligible, index + 1, end)) {
        DEPTH_COUNT(attempt_depth);
        set_t set = cand[index];
        int new_slack = use_profile ? base_slack[index] : 0, updated[16];
        if (use_profile) {
            ++ntested;
            int previous = 0;
            for (; previous < depth; ++previous) {
                int overlap = POP(set & cand[chosen[previous]]);
                updated[previous] = slack[previous] - overlap;
                new_slack -= overlap;
                if (updated[previous] < 0 || new_slack < 0) break;
            }
            if (previous < depth) { ++profile_rejected; DEPTH_COUNT(cap_depth); continue; }
        }
        const uint64_t *row = comp + (size_t)index * W;
        int next_first = 0;
        if (depth + 1 < D) {
            int next_size = planned[depth+1];
            next_first = next_size == size ? index : plan_start[next_size];
            set_t saturated = 0;
            for (set_t members = set; members; members &= members-1) {
                int vertex = CTZ(members);
                if (degH[vertex] + cnt[vertex] + 1 == DMAX) saturated |= BIT(vertex);
            }
            int valid = 1;
            unsigned groups = future_groups[depth];
            while (groups) {
                int group = (groups & (1u << next_size)) ? next_size : CTZ(groups);
                groups &= ~(1u << group);
                int from = group == size ? index : plan_start[group];
                int to = plan_end[group];
                uint64_t exists = 0;
                for (int word = from >> 6; word <= (to >> 6); ++word) {
                    uint64_t options = row[word] & eligible[word];
                    for (set_t vertices = saturated; vertices; vertices &= vertices-1)
                        options &= ~cont[(size_t)CTZ(vertices) * W + word];
                    next[word] = options;
                    if (word == (from >> 6)) options &= UINT64_MAX << (from & 63);
                    if (word == (to >> 6)) options &= UINT64_MAX >> (63 - (to & 63));
                    exists |= options;
                }
                if (!exists) { valid = 0; break; }
            }
            if (!valid) { DEPTH_COUNT(empty_depth); continue; }
        }
        if (!independent_enough(set, depth)) { DEPTH_COUNT(alpha_depth); continue; }
        if (!use_tab && depth >= 2) {
            set_t rest = (BIT(m) - 1) & ~(uni_m[(1 << depth)-1] | set);
            if (has_indep(H.adj, rest, K-depth)) continue;
        }
        for (set_t members = set; members; members &= members-1) ++cnt[CTZ(members)];
        int half = 1 << depth;
        for (int mask = 0; mask < half; ++mask) uni_m[half + mask] = uni_m[mask] | set;
        chosen[depth] = index;
        if (use_profile) {
            for (int previous = 0; previous < depth; ++previous) {
                int old = slack[previous];
                slack[previous] = updated[previous];
                updated[previous] = old;
            }
            slack[depth] = new_slack;
        }
        search_plan(depth + 1, next_first, next);
        if (use_profile)
            for (int previous = 0; previous < depth; ++previous) slack[previous] = updated[previous];
        for (set_t members = set; members; members &= members-1) --cnt[CTZ(members)];
    }
}

static void make_size_plans(int size, int remaining, int budget, const uint64_t *eligible)
{
    if (!remaining) {
        if (budget) return;
        ++size_plans;
        unsigned available = 0;
        for (int group = 0; group < DMAX; ++group)
            if (group_count[group]) available |= 1u << group;
        int depth = 0;
        while (available) {
            int group = CTZ(available);
            if (plan_order == 1) {
                for (unsigned choices = available; choices; choices &= choices-1) {
                    int alternative = CTZ(choices);
                    if (plan_end[alternative] - plan_start[alternative] < plan_end[group] - plan_start[group])
                        group = alternative;
                }
            } else if (plan_order == 2) {
                group = 31 - __builtin_clz(available);
            }
            for (int index = 0; index < group_count[group]; ++index) planned[depth++] = group;
            available &= ~(1u << group);
        }
        unsigned needed = 0;
        for (int index = D-1; index >= 0; --index) {
            future_groups[index] = needed;
            needed |= 1u << planned[index];
        }
        search_plan(0, plan_start[planned[0]], eligible);
        return;
    }
    if (size >= DMAX || budget < size*remaining || budget > (DMAX-1)*remaining) return;
    if (plan_end[size] < plan_start[size]) {
        make_size_plans(size+1, remaining, budget, eligible);
        return;
    }
    for (int count = 0; count <= remaining; ++count) {
        group_count[size] = count;
        make_size_plans(size+1, remaining-count, budget-count*size, eligible);
    }
    group_count[size] = 0;
}
#endif

static uint64_t intersect_middle(uint64_t *restrict child, const uint64_t *restrict parent,
                                 const uint64_t *restrict compatible, int first, int end)
{
    uint64_t present = 0;
    for (int word = first; word < end; ++word) {
        child[word] = parent[word] & compatible[word];
        present |= child[word];
    }
    return present;
}

/* elig is valid on candidate indices [start, hi]; indices > hi count as not eligible */
static void search(int depth, int start, const uint64_t *elig, int hi, int edges, set_t uni)
{
    nnodes++;
    DEPTH_COUNT(node_depth);
#ifdef STATIC_PROFILE_LOOKAHEAD
    if (use_profile && (depth == 0 || (depth >= lookahead_depth && depth < D))) {
        ++lookahead_tested;
        if (!degree_profile_possible(depth)) { ++lookahead_rejected; return; }
    }
#endif
    if (depth == D) {
        if (edges < search_min) return;
        for (int x = 0; x < m; x++) if (degH[x] + ACTIVE_COUNT(depth, x) < DMIN) return;
        output();
        return;
    }
    int rem = D - depth, B = search_max - edges;
    if (B < 0) return;
    int lim = hix[B / rem > 64 ? 64 : B / rem]; if (lim > hi) lim = hi;
    if (rem == 1 && search_min > edges) {
        int minimum = search_min - edges;
        if (minimum > 64) return;
        if (start <= hix[minimum - 1]) start = hix[minimum - 1]+1;
    }
    int f = first_bit_range(elig, start, lim);
    if (f < 0) return;
    if (edges + rem * (DMAX - 1) < search_min) return;
#ifdef CHECK_SIZE_SUPPORT
    if (search_min > edges) {
        int minimum_largest = (search_min - edges + rem-1) / rem;
        if (minimum_largest > 64) return;
        int boundary = hix[minimum_largest-1] + 1;
        if (boundary > start && first_bit_range(elig, boundary, hi) < 0) return;
    }
#endif
    for (set_t remaining = low_vertices; remaining; remaining &= remaining-1) {
        int x = CTZ(remaining);
        int need = minimum_degree - degH[x] - ACTIVE_COUNT(depth, x);
        if (need <= 0) continue;
        if (need > rem) return;
        const uint64_t *cx = cont + (size_t)x * W;
        int ok = 0;
        for (int w = start >> 6; w <= (hi >> 6); w++) {
            uint64_t t = elig[w] & cx[w];
            if (w == (start >> 6)) t &= ~0ULL << (start & 63);
            if (w == (hi >> 6) && (hi & 63) != 63) t &= (2ULL << (hi & 63)) - 1;
            if (t) { ok = 1; break; }
        }
        if (!ok) return;
    }
    if (!use_tab && depth >= 3) {
        set_t all = (BIT(m) - 1) & ~uni;
        if (has_indep(H.adj, all, K - depth + 1)) return;
    }
    if (rem >= COLMIN) {
        int w0 = start >> 6, w1 = hi >> 6, sc = 0;
#ifdef FAST_BOOLEAN_ROWS
        for (int word = w0; word <= w1; ++word) {
            uint64_t mask = elig[word] & selfc[word];
            if (word == w0) mask &= UINT64_MAX << (start & 63);
            if (word == w1) mask &= UINT64_MAX >> (63 - (hi & 63));
            if (mask) { sc = 1; break; }
        }
        if (!sc) {
            for (int word = w0; word <= w1; ++word) Pbuf[word] = elig[word];
            Pbuf[w0] &= UINT64_MAX << (start & 63);
            Pbuf[w1] &= UINT64_MAX >> (63 - (hi & 63));
        }
#else
        for (int w = w0; w <= w1; w++) {
            uint64_t t = elig[w]; if (w == w0) t &= ~0ULL << (start & 63);
            if (w == w1 && (hi & 63) != 63) t &= (2ULL << (hi & 63)) - 1;
            Pbuf[w] = t; if (t & selfc[w]) sc = 1;
        }
#endif
        if (!sc) {
            int e2 = edges, k = 0;
            while (k < rem) {
                int v = first_bit_range(Pbuf, start, hi);
                if (v < 0) break;
                e2 += csz[v]; k++;
                for (int w = w0; w <= w1; w++) Qbuf[w] = Pbuf[w];
                while (v >= 0) {
                    Pbuf[v >> 6] &= ~(1ULL << (v & 63));
                    const uint64_t *cr = comp + (size_t)v * W;
                    for (int w = v >> 6; w <= w1; w++) Qbuf[w] &= ~cr[w];
                    Qbuf[v >> 6] &= ~(1ULL << (v & 63));
                    v = first_bit_range(Qbuf, v + 1, hi);
                }
            }
            if (k < rem || e2 > search_max) { CUT; return; }
        }
    }
    uint64_t *ne = nebuf[depth];
#ifdef FAST_BOOLEAN_ROWS
    bit_cursor cursor = start_cursor(elig, f, lim);
    for (int c = next_cursor(&cursor); c >= 0; c = next_cursor(&cursor)) {
#else
    for (int c = f; c >= 0 && c <= lim; c = first_bit_range(elig, c + 1, lim)) {
#endif
        DEPTH_COUNT(attempt_depth);
        set_t s = cand[c];
        int bad = 0;
        int candidate_slack = 0, old[16];
        if (use_profile) {
            ++ntested;
            candidate_slack = base_slack[c];
            for (int previous = 0; previous < depth; ++previous) {
                int overlap = POP(s & cand[chosen[previous]]);
                if ((candidate_slack -= overlap) < 0 ||
                    (old[previous] = slack[previous] - overlap) < 0) { bad = 1; break; }
            }
            if (bad) { ++profile_rejected; DEPTH_COUNT(cap_depth); continue; }
        }
        if ((depth != 2 || rem == 1) && !independent_enough(s, depth)) { DEPTH_COUNT(alpha_depth); continue; }
        int r2 = rem - 1, B2 = B - csz[c], hi2 = -1;
        int child_start = c;
        if (r2 > 0) {
            int smax = B2 - (r2 - 1) * csz[c]; if (smax > 64) smax = 64;
            hi2 = hix[smax]; if (hi2 > hi) hi2 = hi;
            int s1 = B2 / r2; if (s1 > 64) s1 = 64;
            int lim1 = hix[s1]; if (lim1 > hi2) lim1 = hi2;
            #ifdef EXACT_LAST_SIZE
            if (r2 == 1 && search_min > edges + csz[c]) {
                int minimum = search_min-edges-csz[c];
                if (minimum > 64) continue;
                int boundary = hix[minimum-1]+1;
                if (boundary > child_start) child_start = boundary;
            }
            #endif
            if (lim1 < child_start) continue;
            const uint64_t *cr = comp + (size_t)c * W;
            int w0 = child_start >> 6, wl = lim1 >> 6, w2 = hi2 >> 6;
            uint64_t present = 0;
            ne[w0] = (elig[w0] & cr[w0]) & (~0ULL << (child_start & 63));
            if (w0 < wl) {
                present = ne[w0] | intersect_middle(ne, elig, cr, w0 + 1, wl);
                ne[wl] = elig[wl] & cr[wl];
            }
            present |= ne[wl] & (~0ULL >> (63 - (lim1 & 63)));
            if (!present) { DEPTH_COUNT(empty_depth); continue; }
            if (depth == 2 && !independent_enough(s, depth)) { DEPTH_COUNT(alpha_depth); continue; }
            (void)intersect_middle(ne, elig, cr, wl + 1, w2 + 1);
            #ifdef BITPLANE_ATTACHMENTS
            set_t saturated = s & ~((count_plane[depth][0] ^ capacity_plane[0]) |
                                    (count_plane[depth][1] ^ capacity_plane[1]) |
                                    (count_plane[depth][2] ^ capacity_plane[2]));
            #else
            set_t saturated = 0;
            for (set_t vertices = s; vertices; vertices &= vertices-1) {
                int vertex = CTZ(vertices);
                if (degH[vertex] + cnt[vertex] + 1 == DMAX) saturated |= BIT(vertex);
            }
            #endif
            for (; saturated; saturated &= saturated-1) {
                const uint64_t *cx = cont + (size_t)CTZ(saturated) * W;
                for (int w = w0; w <= w2; w++) ne[w] &= ~cx[w];
            }
        }
        #ifdef CONVEX_STAR_BUDGET
        if (use_profile && !convex_choice(depth, csz[c], edges, s)) continue;
        #endif
        #ifdef BITPLANE_ATTACHMENTS
        count_choice(depth, s);
        #else
        for (set_t vertices = s; vertices; vertices &= vertices-1) ++cnt[CTZ(vertices)];
        #endif
        if (use_tab) { int half = 1 << depth; for (int mk = 0; mk < half; mk++) uni_m[half + mk] = uni_m[mk] | s; }
        chosen[depth] = c;
        if (use_profile) {
            for (int previous = 0; previous < depth; ++previous) {
                int previous_slack = slack[previous];
                slack[previous] = old[previous];
                old[previous] = previous_slack;
            }
            slack[depth] = candidate_slack;
        }
        search(depth + 1, child_start, ne, hi2, edges + csz[c], uni | s);
        if (use_profile)
            for (int previous = 0; previous < depth; ++previous) slack[previous] = old[previous];
        #ifndef BITPLANE_ATTACHMENTS
        for (set_t vertices = s; vertices; vertices &= vertices-1) --cnt[CTZ(vertices)];
        #endif
    }
}

/* enumerate independent sets of H with size in [lo,hi] whose vertices have degH <= DMAX-1 */
static set_t *lst; static int nl, capl;
static void push(set_t s) {
    if (nl == capl) { capl = capl ? 2 * capl : 1024; lst = realloc(lst, sizeof(set_t) * capl); }
    lst[nl++] = s;
}
static void enum_indep(set_t cur, int sz, set_t allowed, int lo, int hi)
{
    if (sz >= lo) push(cur);
    if (sz == hi) return;
    while (allowed) {
        int x = CTZ(allowed); allowed &= allowed - 1;
        enum_indep(cur | BIT(x), sz + 1, allowed & ~H.adj[x], lo, hi);
    }
}
static int cmp_size(const void *a, const void *b)
{
    int pa = POP(*(const set_t *)a), pb = POP(*(const set_t *)b);
    if (pa != pb) return reverse_sizes ? pb - pa : pa - pb;
    set_t x = *(const set_t *)a, y = *(const set_t *)b;
    return x < y ? -1 : x > y;
}

static void process(void)
{
    m = H.n; eH = g_edges(&H);
    if (use_profile && m + D + 1 != profile_order) {
        fprintf(stderr, "unexpected output order in profile mode\n");
        exit(2);
    }
    if (use_profile && eH + D > EMAX) return;
    if (m + D + 1 > 64) { fprintf(stderr, "too big\n"); exit(1); }
    set_t allowed = 0;
    low_vertices = 0;
    #ifdef BITPLANE_ATTACHMENTS
    memset(capacity_plane, 0, sizeof capacity_plane);
    #endif
    for (int x = 0; x < m; x++) {
        degH[x] = POP(H.adj[x]);
        if (degH[x] > DMAX) return;
        if (degH[x] + D < minimum_degree) return;
        if (degH[x] < minimum_degree) low_vertices |= BIT(x);
        if (degH[x] <= DMAX - 1) allowed |= BIT(x);
        cnt[x] = 0;
        #ifdef BITPLANE_ATTACHMENTS
        unsigned capacity = (unsigned)(DMAX-degH[x]-1);
        for (int plane = 0; plane < 3; ++plane)
            if ((capacity >> plane)&1) capacity_plane[plane] |= BIT(x);
        #endif
    }
    if (eH + D + D * (DMIN - 1) > EMAX) return;
    /* critical sets: independent (K-1)-sets of H */
    nl = 0;
    enum_indep(0, 0, BIT(m) - 1, K - 1, K - 1);
    int nL = nl; set_t *L = malloc(sizeof(set_t) * (nL ? nL : 1)); memcpy(L, lst, sizeof(set_t) * nL);
    /* candidates */
    nl = 0;
    int lo = DMIN - 1 < 0 ? 0 : DMIN - 1;
    if (lo < minimum_degree-1) lo = minimum_degree-1;
    if (lo < star_minimum - 1) lo = star_minimum - 1;
    enum_indep(0, 0, allowed, lo, DMAX - 1);
    if (use_profile) {
        int kept = 0;
        for (int index = 0; index < nl; ++index) {
            int total = D;
            for (set_t vertices = lst[index]; vertices; vertices &= vertices-1)
                total += 1 + degH[CTZ(vertices)];
            if (total <= maximum_sum[1+POP(lst[index])]) lst[kept++] = lst[index];
        }
        nl = kept;
    }
    if (irreducible_only) {
        int kept = 0;
        for (int index = 0; index < nl; ++index) {
            int hits_all = 1;
            for (int witness = 0; witness < nL && hits_all; ++witness)
                hits_all = (lst[index] & L[witness]) != 0;
            if (!hits_all) lst[kept++] = lst[index];
        }
        nl = kept;
    }
    qsort(lst, nl, sizeof(set_t), cmp_size);
    N = nl; W = (N + 63) / 64; if (W == 0) W = 1;
    cand = lst; csz = malloc(sizeof(int) * (N ? N : 1));
    for (int i = 0; i < N; i++) csz[i] = POP(cand[i]);
    if (use_profile) {
        base_slack = malloc((N ? N : 1) * sizeof *base_slack);
        if (!base_slack) exit(1);
        for (int index = 0; index < N; ++index) {
            int total = D;
            for (set_t vertices = cand[index]; vertices; vertices &= vertices-1)
                total += 1 + degH[CTZ(vertices)];
            base_slack[index] = maximum_sum[1+csz[index]] - total;
        }
    }
    clock_t started = clock();
    cont = calloc((size_t)m * W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) {
        set_t s = cand[i];
        while (s) { int x = CTZ(s); s &= s - 1; cont[(size_t)x * W + (i >> 6)] |= 1ULL << (i & 63); }
    }
    uint64_t *hit = calloc((size_t)nL * W, sizeof *hit);
    comp = malloc((size_t)N * W * sizeof *comp);
    if ((nL && !hit) || (N && !comp)) { perror("compatibility rows"); exit(1); }
    for (int i = 0; i < nL; ++i) {
        uint64_t *restrict row = hit + (size_t)i*W;
        for (set_t mask = L[i]; mask; mask &= mask - 1) {
            const uint64_t *restrict col = cont + (size_t)CTZ(mask)*W;
            for (int word = 0; word < W; ++word) row[word] |= col[word];
        }
    }
    for (int i = 0; i < N; ++i) {
        uint64_t *restrict row = comp + (size_t)i*W;
        memset(row, 0xff, (size_t)W*sizeof *row);
        for (int j = 0; j < nL; ++j) if (!(cand[i] & L[j])) {
            const uint64_t *restrict col = hit + (size_t)j*W;
            for (int word = 0; word < W; ++word) row[word] &= col[word];
        }
        if (prefilter_overlap) {
            for (int word = 0; word < W; ++word) {
                uint64_t candidates = row[word];
                while (candidates) {
                    int index = 64*word + CTZ(candidates);
                    candidates &= candidates - 1;
                    if (index < N) {
                        int overlap = POP(cand[i] & cand[index]);
                        if (overlap <= base_slack[i] && overlap <= base_slack[index]) continue;
                    }
                    row[word] &= ~BIT(index & 63);
                }
            }
        }
    }
    free(hit);
    pair_time += clock() - started;
    use_tab = (m <= TMAX); if (use_tab) { build_tab(); uni_m[0] = 0; }
    selfc = calloc(W, sizeof(uint64_t)); Pbuf = calloc(W, sizeof(uint64_t)); Qbuf = calloc(W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) if (comp[(size_t)i * W + (i >> 6)] >> (i & 63) & 1) selfc[i >> 6] |= 1ULL << (i & 63);
    uint64_t *elig = calloc(W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) elig[i >> 6] |= 1ULL << (i & 63);
    search_min = EMIN;
    search_max = EMAX;
    if (reverse_sizes) {
        int base = 2*(eH+D) + D*(DMAX-1);
        search_min = base - EMAX;
        search_max = base - EMIN;
        for (int i = 0; i < N; ++i) csz[i] = DMAX-1-csz[i];
    }
    for (int sz = 0, i = -1; sz <= 64; sz++) { while (i + 1 < N && csz[i + 1] <= sz) i++; hix[sz] = i; }
    for (int dd = 0; dd <= D; dd++) nebuf[dd] = realloc(nebuf[dd], sizeof(uint64_t) * W);
    started = clock();
#ifdef CONVEX_STAR_BUDGET
    if (!use_profile || convex_setup(lo))
#endif
#ifdef EXACT_SIZE_PLAN
    for (int size = 0; size < DMAX; ++size) {
        plan_start[size] = size ? hix[size-1]+1 : 0;
        plan_end[size] = hix[size];
    }
    uni_m[0] = 0;
    make_size_plans(0, D, EMAX-eH-D, elig);
#else
    search(0, 0, elig, N - 1, eH + D, 0);
#endif
    search_time += clock() - started;
    free(base_slack);
    free(selfc); free(Pbuf); free(Qbuf);
    free(elig); free(cont); free(comp); free(csz); free(L);
}

int main(int argc, char **argv)
{
#ifdef CONVEX_STAR_BUDGET
    const char *convex_option = getenv("CONVEX_DEPTH");
    if (convex_option) convex_first_depth = atoi(convex_option);
    if (convex_first_depth < 0 || convex_first_depth > 8) return 2;
#endif
#ifdef EXACT_SIZE_PLAN
    const char *order_option = getenv("PLAN_ORDER");
    plan_order = order_option ? atoi(order_option) : 1;
    if (plan_order < 0 || plan_order > 2) return 2;
#endif
#ifdef STATIC_PROFILE_LOOKAHEAD
    const char *lookahead_option = getenv("LOOKAHEAD_DEPTH");
    if (lookahead_option) lookahead_depth = atoi(lookahead_option);
    if (lookahead_depth < 1 || lookahead_depth > 9) return 2;
#endif
    int c;
    while ((c = getopt(argc, argv, "k:d:e:E:m:M:qIPRA:B:C:S:")) != -1) {
        switch (c) {
        case 'k': K = atoi(optarg); break;
        case 'd': D = atoi(optarg); break;
        case 'e': EMAX = atoi(optarg); break;
        case 'E': EMIN = atoi(optarg); break;
        case 'm': DMIN = atoi(optarg); break;
        case 'M': DMAX = atoi(optarg); break;
        case 'q': quiet = 1; break;
        case 'I': irreducible_only = 1; break;
        case 'P': prefilter_overlap = 1; break;
        case 'R': reverse_sizes = 1; break;
        case 'A': use_profile = 1; skip5 = atoi(optarg); break;
        case 'B': use_profile = 1; skip6 = atoi(optarg); break;
        case 'C': use_profile = 1; skip7 = atoi(optarg); break;
        case 'S': star_minimum = atoi(optarg); break;
        default: fprintf(stderr, "usage: glue -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX]\n"); return 1;
        }
    }
    if (K <= 1 || D <= 0) { fprintf(stderr, "need -k and -d\n"); return 1; }
    if (DMIN < 0) DMIN = D;
    if (DMAX < 0) DMAX = K;
#ifdef BITPLANE_ATTACHMENTS
    if (DMAX > 8 || D > 7) return 2;
#endif
#ifdef CONVEX_STAR_BUDGET
    if (EMIN != EMAX || reverse_sizes || DMAX > 8 || D > 8) return 2;
#endif
#ifdef EXACT_SIZE_PLAN
    if (EMIN != EMAX || reverse_sizes || DMAX > 8 || D > 8) return 2;
#endif
    if (star_minimum < 0 || star_minimum > DMAX || (prefilter_overlap && !use_profile)) return 2;
    minimum_degree = DMIN;
    if (use_profile) {
        if (EMIN != EMAX || DMAX > K || DMIN < 0 || EMAX < 0 || EMAX > 99 ||
            skip5 < 0 || skip6 < 0 || skip7 < 0 ||
            skip5 >= EMAX || skip6 >= EMAX || skip7 >= EMAX) return 2;
        const int floors30[9] = {200, 200, 85, 73, 65, 56, 49, 42, 35};
        const int floors22[9] = {200, 200, 200, 200, 40, 32, 25, 200, 200};
        const int *floors;
        int absolute_minimum;
        if (K == 8 && EMAX == 88) {
            profile_order = 30;
            absolute_minimum = 3;
            floors = floors30;
        } else if (K == 6) {
            profile_order = 22;
            absolute_minimum = 4;
            floors = floors22;
        } else return 2;
        for (int degree = 0; degree <= 8; ++degree) maximum_sum[degree] = EMAX - floors[degree];
        if (skip5 >= floors[5]) maximum_sum[5] = EMAX - 1 - skip5;
        if (skip6 >= floors[6]) maximum_sum[6] = EMAX - 1 - skip6;
        if (skip7 >= floors[7]) maximum_sum[7] = EMAX - 1 - skip7;
        if (minimum_degree < absolute_minimum) minimum_degree = absolute_minimum;
    }
    if (D < minimum_degree) return 0;
    if (D > DMAX || D < DMIN) { return 0; }
    char line[4096];
    long long nin = 0;
    clock_t t0 = clock();
    while (fgets(line, sizeof line, stdin)) {
        if (line[0] == '\n' || line[0] == 0) continue;
        line[strcspn(line, "\r\n")] = 0;
        if (g6_read(line, &H)) { fprintf(stderr, "bad graph6: %s\n", line); continue; }
        nin++;
        process();
    }
    if (!quiet)
        fprintf(stderr, "glue K=%d d=%d e=[%d,%d] deg=[%d,%d]: in=%lld nodes=%lld leaves=%lld out=%lld cpu=%.2fs\n",
                K, D, EMIN, EMAX, DMIN, DMAX, nin, nnodes, nleaf, nout, (double)(clock() - t0) / CLOCKS_PER_SEC);
    if (!quiet)
        fprintf(stderr, "transposed pair CPU %.3fs search CPU %.3fs\n",
                (double)pair_time / CLOCKS_PER_SEC, (double)search_time / CLOCKS_PER_SEC);
    if (use_profile && !quiet)
        fprintf(stderr, "profile rejected %lld of %lld candidate attempts\n", profile_rejected, ntested);
#ifdef CONVEX_STAR_BUDGET
    if (use_profile && !quiet)
        fprintf(stderr, "convex(%d) rejected %lld of %lld attempts\n", convex_first_depth,
                convex_rejected, convex_tested);
#endif
#ifdef EXACT_SIZE_PLAN
    if (!quiet) fprintf(stderr, "size plans %lld order %d\n", size_plans, plan_order);
#endif
#ifdef STATIC_PROFILE_LOOKAHEAD
    if (use_profile && !quiet)
        fprintf(stderr, "lookahead(%d) rejected %lld of %lld nodes\n", lookahead_depth,
                lookahead_rejected, lookahead_tested);
#endif
#ifdef COUNT_DEPTH
    for (int depth = 0; depth <= D; ++depth)
        fprintf(stderr, "depth %d nodes %llu attempts %llu cap %llu alpha %llu nochild %llu\n", depth,
                (unsigned long long)node_depth[depth], (unsigned long long)attempt_depth[depth],
                (unsigned long long)cap_depth[depth], (unsigned long long)alpha_depth[depth],
                (unsigned long long)empty_depth[depth]);
#endif
    return 0;
}
