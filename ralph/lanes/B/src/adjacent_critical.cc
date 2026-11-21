#include "gutil.h"

#include <algorithm>
#include <array>
#include <vector>

using Masks = std::vector<set_t>;

static void list_independent(const graph_t &base, set_t available, set_t selected,
                             int needed, Masks &result)
{
    if (!needed) { result.push_back(selected); return; }
    while (POP(available) >= needed) {
        int vertex = CTZ(available);
        available &= available-1;
        list_independent(base, available & ~base.adj[vertex], selected | BIT(vertex),
                         needed-1, result);
    }
}

struct PairSearch {
    const graph_t &base;
    Masks witnesses;
    std::array<Masks, 10> rows{};
    set_t full, required = 0, allowed = 0;
    int alpha, low, high, budget;
    long long nodes = 0, joins = 0, emitted = 0;

    void search(set_t selected, set_t available, int size)
    {
        ++nodes;
        if (size + POP(available) < low) return;
        set_t private_edges = 0, branch = 0;
        int least = 64;
        for (set_t witness : witnesses) {
            set_t hit = witness & selected;
            if (hit) {
                if (!(hit & (hit-1))) private_edges |= hit;
            } else {
                set_t choices = witness & available;
                if (!choices || size == high) return;
                int count = POP(choices);
                if (count < least) { least = count; branch = choices; }
            }
        }
        if (private_edges != selected) return;
        if (!branch) {
            if (size >= low) rows[size].push_back(selected);
            return;
        }
        while (branch) {
            int vertex = CTZ(branch);
            branch &= branch-1;
            available &= ~BIT(vertex);
            search(selected | BIT(vertex), available & ~base.adj[vertex], size+1);
        }
    }

    bool extend(int minimum)
    {
        if (low > high) return true;
        for (int vertex = 0; vertex < base.n; ++vertex) {
            int degree = POP(base.adj[vertex]);
            if (degree < minimum-1) return true;
            if (degree == minimum-1) required |= BIT(vertex);
            if (degree < alpha) allowed |= BIT(vertex);
        }
        list_independent(base, full, 0, alpha, witnesses);
        search(0, allowed, 0);
        struct Demands { int first, second; set_t forest; };
        std::vector<Demands> missing;
        for (int vertex = 0; vertex < base.n; ++vertex)
            for (set_t later = base.adj[vertex] & ~(BIT(vertex+1)-1); later; later &= later-1) {
                int other = CTZ(later);
                set_t forest = full & ~(base.adj[vertex] | base.adj[other]);
                if (!has_indep(base.adj, forest, alpha-1)) {
                    if (!has_indep(base.adj, forest, alpha-2)) return true;
                    missing.push_back({vertex, other, forest});
                }
            }
        if (missing.size() > 128) return false;
        using Cover = std::array<set_t, 2>;
        Cover target{};
        for (size_t index = 0; index < missing.size(); ++index)
            target[index/64] |= BIT(index%64);
        auto covers = [&](set_t row) {
            Cover cover{};
            for (size_t index = 0; index < missing.size(); ++index) {
                const auto &demand = missing[index];
                if (!(row & (BIT(demand.first) | BIT(demand.second))) &&
                    has_indep(base.adj, demand.forest & ~row, alpha-2))
                    cover[index/64] |= BIT(index%64);
            }
            return cover;
        };
        for (int left_size = low; left_size <= budget/2 && left_size <= high; ++left_size) {
            int right_size = budget-left_size;
            if (right_size > high || right_size < low) continue;
            const auto &right_rows = rows[right_size];
            std::vector<Cover> right_cover(right_rows.size());
            std::vector<bool> checked(right_rows.size());
            for (size_t left_index = 0; left_index < rows[left_size].size(); ++left_index) {
                set_t left = rows[left_size][left_index];
                Cover left_cover{};
                bool left_checked = false;
                for (size_t right_index = left_size == right_size ? left_index : 0;
                     right_index < right_rows.size(); ++right_index) {
                    set_t right = right_rows[right_index];
                    if ((left & right) || (required & ~(left | right))) continue;
                    ++joins;
                    if (!has_indep(base.adj, full & ~(left | right), alpha-1)) continue;
                    if (!left_checked) { left_cover = covers(left); left_checked = true; }
                    if (!checked[right_index]) {
                        right_cover[right_index] = covers(right);
                        checked[right_index] = true;
                    }
                    const auto &cover = right_cover[right_index];
                    if ((left_cover[0] | cover[0]) != target[0] ||
                        (left_cover[1] | cover[1]) != target[1]) continue;
                    set_t first_row = left, second_row = right;
                    if (left_size == right_size && first_row > second_row)
                        std::swap(first_row, second_row);
                    graph_t result = base;
                    int first = base.n, second = base.n+1;
                    result.n += 2;
                    result.adj[first] = first_row | BIT(second);
                    result.adj[second] = second_row | BIT(first);
                    for (set_t rest = first_row; rest; rest &= rest-1) result.adj[CTZ(rest)] |= BIT(first);
                    for (set_t rest = second_row; rest; rest &= rest-1) result.adj[CTZ(rest)] |= BIT(second);
                    g6_write(stdout, &result);
                    ++emitted;
                }
            }
        }
        return true;
    }
};

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    int alpha = atoi(argv[1]), minimum = atoi(argv[2]), edges = atoi(argv[3]);
    if (alpha < 2 || alpha > 9 || minimum < 0 || minimum > alpha || edges < 1 || edges > 128)
        return 2;
    long long bases = 0, nodes = 0, joins = 0, emitted = 0;
    graph_t base;
    char line[1024];
    while (fgets(line, sizeof(line), stdin)) {
        int order = line[0]-63;
        if (order < 1 || order > 60 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
            g6_read(line, &base) || !g_trianglefree(&base) || !alpha_le(&base, alpha)) return 2;
        int budget = edges-g_edges(&base)-1;
        int low = std::max({0, minimum-1, budget-(alpha-1)});
        int high = std::min(alpha-1, budget-std::max(0, minimum-1));
        PairSearch work{base, {}, {}, BIT(order)-1, 0, 0, alpha, low, high, budget};
        if (!work.extend(minimum)) return 2;
        ++bases;
        nodes += work.nodes;
        joins += work.joins;
        emitted += work.emitted;
    }
    fprintf(stderr, "Adjacent critical bases=%lld nodes=%lld joins=%lld outputs=%lld\n",
            bases, nodes, joins, emitted);
    return ferror(stdin) || fflush(stdout) == EOF;
}
