#include "gutil.h"
#include <algorithm>
#include <cassert>
#include <vector>

using Bits = std::vector<set_t>;

static bool hit(const Bits &left, const Bits &right) {
    for (size_t word = 0; word < left.size(); ++word)
        if (left[word] & right[word]) return true;
    return false;
}

static void set(Bits &bits, int index) { bits[index / 64] |= BIT(index % 64); }

static void clear(Bits &bits, int index) { bits[index / 64] &= ~BIT(index % 64); }

static void enumerate(const graph_t &graph, set_t chosen, set_t possible, set_t done,
                      std::vector<set_t> &rows) {
    if (!(possible | done)) {
        rows.push_back(chosen);
        return;
    }
    while (possible) {
        int vertex = CTZ(possible);
        possible ^= BIT(vertex);
        enumerate(graph, chosen | BIT(vertex), possible & ~graph.adj[vertex],
                  done & ~graph.adj[vertex], rows);
        done |= BIT(vertex);
    }
}

static void solve(const graph_t &graph, int alpha, int root, int minimum, int mode, int index) {
    const int private_size = alpha + 1 - root;
    const set_t universe = BIT(graph.n) - 1;
    set_t capped = 0;
    std::vector<set_t> demands, maximum, rows;
    std::vector<set_t> distant(graph.n);
    enumerate(graph, 0, universe, 0, rows);
    std::sort(rows.begin(), rows.end());
    for (set_t row : rows) if (POP(row) == alpha - 1) maximum.push_back(row);
    if (mode > 0)
        rows.erase(std::remove_if(rows.begin(), rows.end(), [&](set_t row) {
            return POP(row) < std::max(minimum - 1, private_size) || POP(row) > private_size + root - 1;
        }), rows.end());
    for (int site = 0; site < graph.n; ++site) {
        demands.push_back(BIT(site));
        if (POP(graph.adj[site]) == alpha - 1) capped |= BIT(site);
        for (int other = 0; other < site; ++other) {
            if (graph.adj[site] & BIT(other) || graph.adj[site] & graph.adj[other]) continue;
            demands.push_back(BIT(site) | BIT(other));
            distant[site] |= BIT(other);
            distant[other] |= BIT(site);
        }
    }
    int width = (rows.size() + 63) / 64;
    std::vector<Bits> avoid(rows.size(), Bits((maximum.size() + 63) / 64));
    std::vector<Bits> compatible(rows.size(), Bits(width)), cover(demands.size(), Bits(width));
    std::vector<Bits> site_rows(graph.n, Bits(width));
    std::vector<std::vector<int>> outside(rows.size());
    for (int index = 0; index < int(rows.size()); ++index) {
        set_t row = rows[index];
        for (int witness = 0; witness < int(maximum.size()); ++witness)
            if (!(maximum[witness] & row)) set(avoid[index], witness);
        for (int demand = 0; demand < int(demands.size()); ++demand) {
            if ((row & demands[demand]) == demands[demand]) set(cover[demand], index);
            else outside[index].push_back(demand);
        }
        for (set_t rest = row; rest; rest &= rest - 1) set(site_rows[CTZ(rest)], index);
        for (int previous = 0; previous < index; ++previous) {
            set_t shared = row & rows[previous];
            if (shared & capped || (mode > 0 && POP(shared) > 1) || hit(avoid[previous], avoid[index])) continue;
            if (mode > 1 && shared && (distant[CTZ(shared)] & ~(row | rows[previous]))) continue;
            set(compatible[previous], index);
            set(compatible[index], previous);
        }
    }
    int waves = 0, current = rows.size();
    std::vector<bool> dead(rows.size());
    while (true) {
        std::vector<int> removed;
        for (int index = 0; index < int(rows.size()); ++index) {
            if (dead[index]) continue;
            bool fails = false;
            for (int demand : outside[index]) {
                if (!hit(compatible[index], cover[demand])) { fails = true; break; }
            }
            if (mode > 1 && !fails) {
                set_t row = rows[index];
                int needed = POP(row) - private_size, may_share = 0, must_share = 0;
                for (set_t rest = row; rest; rest &= rest - 1) {
                    int site = CTZ(rest);
                    may_share += hit(compatible[index], site_rows[site]);
                    must_share += bool(distant[site] & ~row);
                }
                fails = needed < must_share || needed > may_share;
            }
            if (fails) removed.push_back(index);
        }
        if (removed.empty()) break;
        ++waves;
        current -= removed.size();
        for (int removed_index : removed) {
            dead[removed_index] = true;
            for (auto &domain : cover) clear(domain, removed_index);
            for (auto &site : site_rows) clear(site, removed_index);
        }
    }
    set_t obstruction = 0;
    for (int index = 0; index < int(demands.size()); ++index) {
        if (std::none_of(cover[index].begin(), cover[index].end(), [](set_t word) { return word; })) {
            obstruction = demands[index];
            break;
        }
    }
    printf("%d\t%zu\t%zu\t%zu\t%d\t%d\t%llx\n", index, rows.size(), maximum.size(), demands.size(),
           waves, current, (unsigned long long)obstruction);
    fflush(stdout);
}

int main(int argc, char **argv) {
    if (argc != 6) return 2;
    int alpha = atoi(argv[1]), root = atoi(argv[2]), minimum = atoi(argv[3]);
    int edge_pin = atoi(argv[4]), mode = atoi(argv[5]), count = 0;
    char line[1024];
    graph_t graph;
    while (fgets(line, sizeof(line), stdin)) {
        if (g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha - 1)) return 3;
        if (edge_pin && edge_pin != g_edges(&graph) + root + 2 * graph.n - root * (alpha + 1 - root)) return 4;
        solve(graph, alpha, root, minimum, mode, ++count);
    }
}
