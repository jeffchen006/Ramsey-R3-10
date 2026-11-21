#include "gutil.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

using Masks = std::vector<set_t>;

static void list_independent(const graph_t &graph, set_t allowed, set_t selected,
                             int needed, Masks &result)
{
    if (!needed) { result.push_back(selected); return; }
    while (POP(allowed) >= needed) {
        int vertex = CTZ(allowed);
        allowed ^= BIT(vertex);
        list_independent(graph, allowed & ~graph.adj[vertex], selected | BIT(vertex), needed - 1, result);
    }
}

struct Transversals {
    const graph_t &graph;
    const Masks &witnesses;
    int minimum, maximum;
    std::array<Masks, 64> by_size;

    void supersets(set_t selected, set_t allowed, int size)
    {
        if (size >= minimum) by_size[size].push_back(selected);
        if (size == maximum) return;
        while (allowed && size + POP(allowed) >= minimum) {
            int vertex = CTZ(allowed);
            allowed ^= BIT(vertex);
            supersets(selected | BIT(vertex), allowed & ~graph.adj[vertex], size + 1);
        }
    }

    void search(set_t selected, set_t allowed, int size)
    {
        if (size + POP(allowed) < minimum) return;
        for (set_t witness : witnesses) {
            if (witness & selected) continue;
            if (size == maximum) return;
            set_t choices = witness & allowed;
            while (choices) {
                int vertex = CTZ(choices);
                choices ^= BIT(vertex);
                allowed ^= BIT(vertex);
                search(selected | BIT(vertex), allowed & ~graph.adj[vertex], size + 1);
            }
            return;
        }
        supersets(selected, allowed, size);
    }
};

static graph_t assemble(const graph_t &source, int first, int second,
                        set_t left, set_t right, int joined)
{
    graph_t result = source;
    for (int vertex = 0; vertex < source.n; ++vertex) {
        result.adj[vertex] &= ~(BIT(first) | BIT(second));
        if (left & BIT(vertex)) result.adj[vertex] |= BIT(first);
        if (right & BIT(vertex)) result.adj[vertex] |= BIT(second);
    }
    result.adj[first] = left | (joined ? BIT(second) : 0);
    result.adj[second] = right | (joined ? BIT(first) : 0);
    return result;
}

static long replace(const graph_t &source, long source_id, int first, int second,
                    int alpha, int min_edges, int max_edges, int min_deg,
                    const Masks &all_top, const Masks &all_next, bool require_original)
{
    set_t removed = BIT(first) | BIT(second);
    set_t exterior = (BIT(source.n) - 1) & ~removed;
    int base_edges = g_edges(&source) - POP(source.adj[first]) - POP(source.adj[second])
                     + bool(source.adj[first] & BIT(second));
    int trans_min = std::max({0, min_deg - 1, min_edges - base_edges - alpha});
    int trans_max = std::min(alpha, max_edges - base_edges - std::max(0, min_deg - 1));
    if (trans_min > trans_max) return 0;
    Masks top, next;
    for (set_t mask : all_top) if (!(mask & removed)) top.push_back(mask);
    for (set_t mask : all_next) if (!(mask & removed)) next.push_back(mask);
    Transversals transversals{source, top, trans_min, trans_max, {}};
    set_t saturated = 0, high = 0, deficit = 0, two_deficit = 0;
    for (set_t remaining = exterior; remaining; remaining &= remaining - 1) {
        int vertex = CTZ(remaining), degree = POP(source.adj[vertex] & exterior);
        if (degree + 2 < min_deg) return 0;
        if (degree >= alpha) saturated |= BIT(vertex);
        if (degree >= alpha - 1) high |= BIT(vertex);
        if (degree < min_deg) deficit |= BIT(vertex);
        if (degree < min_deg - 1) two_deficit |= BIT(vertex);
    }
    transversals.search(0, exterior & ~saturated, 0);
    long emitted = 0;
    bool original = false;
    for (int left_size = trans_min; left_size <= trans_max; ++left_size)
        for (set_t left : transversals.by_size[left_size]) {
            Masks missed;
            for (set_t mask : next) if (!(mask & left)) missed.push_back(mask);
            for (int joined = 0; joined <= 1; ++joined) {
                if (left_size + joined < min_deg || left_size + joined > alpha) continue;
                int low = std::max({trans_min, min_deg - joined, min_edges - base_edges - left_size - joined});
                int high_size = std::min({trans_max, alpha - joined, max_edges - base_edges - left_size - joined});
                for (int right_size = std::max(left_size, low); right_size <= high_size; ++right_size)
                    for (set_t right : transversals.by_size[right_size]) {
                        if (right_size == left_size && right < left) continue;
                        if ((left | right) & saturated || (left & right) & high) continue;
                        if ((deficit & ~(left | right)) || (two_deficit & ~(left & right))) continue;
                        if (joined ? bool(left & right) :
                            std::any_of(missed.begin(), missed.end(), [right](set_t mask){ return !(mask & right); })) continue;
                        set_t orig_left = source.adj[first] & exterior, orig_right = source.adj[second] & exterior;
                        if (joined == bool(source.adj[first] & BIT(second)) &&
                            ((left == orig_left && right == orig_right) || (left == orig_right && right == orig_left))) original = true;
                        graph_t result = assemble(source, first, second, left, right, joined);
                        std::printf("%ld\t%d\t%d\t", source_id, first, second);
                        g6_write(stdout, &result);
                        ++emitted;
                    }
            }
        }
    if (require_original && !original) {
        std::fprintf(stderr, "original replacement missing: %ld,%d,%d\n", source_id, first, second);
        std::exit(3);
    }
    return emitted;
}

static unsigned pair_flags(set_t earlier, set_t later, const Masks &missed)
{
    return unsigned(!(earlier & later)) * 2U
         | unsigned(std::none_of(missed.begin(), missed.end(), [later](set_t mask){ return !(mask & later); }));
}

static long triple(const graph_t &source, long source_id, std::array<int,3> marked,
                   int alpha, int min_edges, int max_edges, int min_deg,
                   const Masks &all_top, const Masks &all_next, const Masks &all_third, bool require_original)
{
    set_t removed = BIT(marked[0]) | BIT(marked[1]) | BIT(marked[2]);
    set_t exterior = (BIT(source.n) - 1) & ~removed;
    int removed_stubs = 0;
    for (int vertex : marked)
        removed_stubs += 2 * POP(source.adj[vertex] & exterior) + POP(source.adj[vertex] & removed);
    int base_edges = g_edges(&source) - removed_stubs / 2;
    int trans_min = std::max({0, min_deg - 2, min_edges - base_edges - 2 * alpha});
    int trans_max = std::min(alpha, max_edges - base_edges - 2 * std::max(0, min_deg - 2));
    if (trans_min > trans_max) return 0;

    set_t saturated = 0, upper1 = 0, upper2 = 0, deficit1 = 0, deficit2 = 0, deficit3 = 0;
    for (set_t remaining = exterior; remaining; remaining &= remaining - 1) {
        int vertex = CTZ(remaining), degree = POP(source.adj[vertex] & exterior);
        if (degree + 3 < min_deg) return 0;
        if (degree >= alpha) saturated |= BIT(vertex);
        if (degree >= alpha - 1) upper1 |= BIT(vertex);
        if (degree >= alpha - 2) upper2 |= BIT(vertex);
        if (degree < min_deg) deficit1 |= BIT(vertex);
        if (degree < min_deg - 1) deficit2 |= BIT(vertex);
        if (degree < min_deg - 2) deficit3 |= BIT(vertex);
    }
    Masks top, next, third;
    for (set_t mask : all_top) if (!(mask & removed)) top.push_back(mask);
    for (set_t mask : all_next) if (!(mask & removed)) next.push_back(mask);
    for (set_t mask : all_third) if (!(mask & removed)) third.push_back(mask);
    Transversals transversals{source, top, trans_min, trans_max, {}};
    transversals.search(0, exterior & ~saturated, 0);
    long emitted = 0;
    bool original_found = false;
    std::array<set_t,3> original{};
    unsigned original_shape = 0;
    for (int slot = 0; slot < 3; ++slot) original[slot] = source.adj[marked[slot]] & exterior;
    if (source.adj[marked[0]] & BIT(marked[1])) original_shape |= 1U;
    if (source.adj[marked[0]] & BIT(marked[2])) original_shape |= 2U;
    if (source.adj[marked[1]] & BIT(marked[2])) original_shape |= 4U;
    for (int left_size = trans_min; left_size <= trans_max; ++left_size)
        for (set_t left : transversals.by_size[left_size]) {
            Masks missed_left;
            for (set_t mask : next) if (!(mask & left)) missed_left.push_back(mask);
            for (int middle_size = left_size; middle_size <= trans_max; ++middle_size) {
                int low = std::max(middle_size, min_edges - base_edges - left_size - middle_size - 2);
                int high = std::min(trans_max, max_edges - base_edges - left_size - middle_size);
                if (low > high) continue;
                for (set_t middle : transversals.by_size[middle_size]) {
                    if (middle_size == left_size && middle < left) continue;
                    set_t both = left & middle, united = left | middle;
                    if ((both & upper1) || (deficit3 & ~both) || (deficit2 & ~united)) continue;
                    unsigned lm = pair_flags(left, middle, missed_left);
                    if (!lm) continue;
                    Masks missed_middle, missed_both;
                    for (set_t mask : next) if (!(mask & middle)) missed_middle.push_back(mask);
                    if (lm & 1U) for (set_t mask : third) if (!(mask & united)) missed_both.push_back(mask);
                    set_t need_right = deficit3 | (deficit2 & ~both) | (deficit1 & ~united);
                    set_t forbidden_right = (united & upper1) | (both & upper2);
                    if (need_right & forbidden_right) continue;
                    for (int right_size = low; right_size <= high; ++right_size)
                        for (set_t right : transversals.by_size[right_size]) {
                            if (right_size == middle_size && right < middle) continue;
                            if ((need_right & ~right) || (forbidden_right & right)) continue;
                            unsigned lr = pair_flags(left, right, missed_left);
                            if (!lr) continue;
                            unsigned mr = pair_flags(middle, right, missed_middle);
                            if (!mr) continue;
                            std::array<set_t,3> attach{left, middle, right};
                            for (unsigned shape = 0; shape < 7; ++shape) {
                                if (!(lm & (1U << (shape & 1U))) || !(lr & (1U << ((shape >> 1U) & 1U)))
                                    || !(mr & (1U << ((shape >> 2U) & 1U)))) continue;
                                int edges = base_edges + left_size + middle_size + right_size + POP(shape);
                                if (edges < min_edges || edges > max_edges) continue;
                                std::array<int,3> degrees{left_size + POP(shape & 3U), middle_size + POP(shape & 5U),
                                                          right_size + POP(shape & 6U)};
                                if (*std::min_element(degrees.begin(), degrees.end()) < min_deg
                                    || *std::max_element(degrees.begin(), degrees.end()) > alpha) continue;
                                if (!shape && std::any_of(missed_both.begin(), missed_both.end(),
                                                          [right](set_t witness){ return !(right & witness); })) continue;
                                graph_t result = source;
                                for (int vertex = 0; vertex < source.n; ++vertex) result.adj[vertex] &= ~removed;
                                for (int slot = 0; slot < 3; ++slot) {
                                    result.adj[marked[slot]] = attach[slot];
                                    for (set_t remaining = attach[slot]; remaining; remaining &= remaining - 1)
                                        result.adj[CTZ(remaining)] |= BIT(marked[slot]);
                                }
                                std::array<int,3> permutation{0,1,2};
                                do {
                                    if (attach[0] != original[permutation[0]] || attach[1] != original[permutation[1]]
                                        || attach[2] != original[permutation[2]]) continue;
                                    auto adjacent = [&](int first, int second) {
                                        int fst = marked[permutation[first]], snd = marked[permutation[second]];
                                        return unsigned(bool(source.adj[fst] & BIT(snd)));
                                    };
                                    if (shape == (adjacent(0,1) | adjacent(0,2) * 2U | adjacent(1,2) * 4U)) original_found = true;
                                } while (std::next_permutation(permutation.begin(), permutation.end()));
                                if (shape & 1U) { result.adj[marked[0]] |= BIT(marked[1]); result.adj[marked[1]] |= BIT(marked[0]); }
                                if (shape & 2U) { result.adj[marked[0]] |= BIT(marked[2]); result.adj[marked[2]] |= BIT(marked[0]); }
                                if (shape & 4U) { result.adj[marked[1]] |= BIT(marked[2]); result.adj[marked[2]] |= BIT(marked[1]); }
                                std::printf("%ld\t%d\t%d\t%d\t", source_id, marked[0], marked[1], marked[2]);
                                g6_write(stdout, &result);
                                ++emitted;
                            }
                        }
                }
            }
        }
    if (require_original && !original_found) {
        std::fprintf(stderr, "original triple missing: %ld,%d,%d,%d shape=%u\n", source_id, marked[0], marked[1], marked[2], original_shape);
        std::exit(3);
    }
    return emitted;
}

int main(int argc, char **argv)
{
    if (argc != 5 && (argc != 6 || std::strcmp(argv[5], "triple"))) return 2;
    bool triples = argc == 6;
    int alpha = std::atoi(argv[1]), minimum = std::atoi(argv[2]), maximum = std::atoi(argv[3]);
    int min_deg = std::atoi(argv[4]);
    if (alpha < 2 || alpha >= 63 || minimum < 0 || maximum < minimum || min_deg < 0 || min_deg > alpha) return 2;
    long source_id = 0;
    char line[4096];
    while (std::fgets(line, sizeof line, stdin)) {
        graph_t source;
        if (g6_read(line, &source) || !g_trianglefree(&source) || !alpha_le(&source, alpha)) return 2;
        ++source_id;
        Masks top, next, third;
        list_independent(source, BIT(source.n) - 1, 0, alpha, top);
        list_independent(source, BIT(source.n) - 1, 0, alpha - 1, next);
        if (triples) list_independent(source, BIT(source.n) - 1, 0, alpha - 2, third);
        int edges = g_edges(&source);
        bool recover = edges >= minimum && edges <= maximum;
        for (int vertex = 0; vertex < source.n; ++vertex) recover &= POP(source.adj[vertex]) >= min_deg;
        long emitted = 0;
        int tags = 0;
        for (int first = 0; first < source.n; ++first)
            for (int second = first + 1; second < source.n; ++second) {
                if (!triples) {
                    emitted += replace(source, source_id, first, second, alpha, minimum, maximum, min_deg, top, next, recover);
                    ++tags;
                } else for (int last = second + 1; last < source.n; ++last) {
                    emitted += triple(source, source_id, {first, second, last}, alpha, minimum, maximum,
                                      min_deg, top, next, third, recover);
                    ++tags;
                }
            }
        std::fprintf(stderr, "%ld e=%d tags=%d emitted=%ld recovery=%s\n", source_id, edges, tags, emitted, recover ? "pass" : "n/a");
    }
    return std::ferror(stdin) || std::ferror(stdout) ? 2 : 0;
}
