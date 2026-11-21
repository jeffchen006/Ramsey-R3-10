#include "gutil.h"

static set_t independent_witness(const set_t *adj, set_t domain, int need)
{
    if (POP(domain) < need) return 0;
    set_t isolated = 0;
    int pivot = -1, score = -1;
    for (set_t pend = domain; pend; pend &= pend - 1) {
        int vertex = CTZ(pend);
        int degree = POP(adj[vertex] & domain);
        if (degree == 0) {
            isolated |= BIT(vertex);
            if (POP(isolated) == need) return isolated;
        } else if (degree > score) {
            pivot = vertex;
            score = degree;
        }
    }
    domain &= ~isolated;
    need -= POP(isolated);
    if (POP(domain) < need || pivot < 0) return 0;
    domain &= ~BIT(pivot);
    if (need == 1) return isolated | BIT(pivot);
    set_t witness = independent_witness(adj, domain & ~adj[pivot], need - 1);
    if (witness) return isolated | witness | BIT(pivot);
    witness = independent_witness(adj, domain, need);
    return witness ? isolated | witness : 0;
}

int m11_prove(int order, int alpha, int edge_target, const set_t *pinned, const set_t *eligible,
              set_t *steps, int *length, set_t *terminal)
{
    if (order < 1 || order > 32 || alpha < 2 || edge_target < 0) return -2;
    *length = 0;
    *terminal = 0;
    set_t full = BIT(order) - 1;
    graph_t lower = { .n = order }, upper = { .n = order };
    memcpy(lower.adj, pinned, order * sizeof(set_t));
    memcpy(upper.adj, eligible, order * sizeof(set_t));
    for (;;) {
        int low = g_edges(&lower);
        if (low > edge_target) return 2;
        if (!g_trianglefree(&lower)) return 3;
        int degree[32];
        for (int vertex = 0; vertex < order; ++vertex) {
            degree[vertex] = POP(lower.adj[vertex]);
            if (degree[vertex] > alpha) return 4;
        }
        if (low == edge_target) upper = lower;
        else {
            for (int left = 0; left < order; ++left) {
                set_t optional = upper.adj[left] & ~lower.adj[left] & ~(BIT(left + 1)-1);
                for (; optional; optional &= optional - 1) {
                    int right = CTZ(optional);
                    if (degree[left] == alpha || degree[right] == alpha || (lower.adj[left] & lower.adj[right])) {
                        upper.adj[left] ^= BIT(right);
                        upper.adj[right] ^= BIT(left);
                    }
                }
            }
        }
        if (g_edges(&upper) < edge_target) return 5;
        *terminal = independent_witness(upper.adj, full, alpha+1);
        if (*terminal) return 1;
        int forced = 0;
        for (int left = 0; left < order && !forced; ++left) {
            set_t optional = upper.adj[left] & ~lower.adj[left] & ~(BIT(left + 1)-1);
            for (; optional && !forced; optional &= optional - 1) {
                int right = CTZ(optional);
                set_t witness = independent_witness(upper.adj, full & ~(upper.adj[left] | upper.adj[right]), alpha-1);
                if (!witness) continue;
                witness |= BIT(left) | BIT(right);
                steps[(*length)++] = (witness << 10) | ((set_t)left << 5) | (set_t)right;
                lower.adj[left] |= BIT(right);
                lower.adj[right] |= BIT(left);
                forced = 1;
            }
        }
        if (!forced) return 0;
    }
}

static set_t two_edge_set(const set_t *lower, const set_t *upper, set_t pending, set_t picked,
                          int need, int edges)
{
    if (!need) return edges == 2 ? picked : 0;
    while (POP(pending) >= need) {
        int vertex = CTZ(pending);
        pending &= pending - 1;
        int next = edges + POP(upper[vertex] & picked);
        if (next > 2) continue;
        set_t witness = two_edge_set(lower, upper, pending & ~lower[vertex], picked | BIT(vertex), need - 1, next);
        if (witness) return witness;
    }
    return 0;
}

set_t m11_two_edge_set(int order, int alpha, const set_t *lower, const set_t *upper)
{
    return two_edge_set(lower, upper, BIT(order)-1, 0, alpha+1, 0);
}

set_t m11_upper_witness(int order, int alpha, const set_t *upper)
{
    return independent_witness(upper, BIT(order)-1, alpha+1);
}
