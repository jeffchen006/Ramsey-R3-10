#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using Mask = uint64_t;
using Count = uint64_t;

static int size(Mask mask) { return std::popcount(mask); }
static Mask bit(int vertex) { return Mask{1} << vertex; }
static Mask below(int order) { return bit(order) - 1; }
static int take(Mask &mask) {
    const int vertex = std::countr_zero(mask);
    mask &= mask - 1;
    return vertex;
}

static std::vector<Mask> parse(const std::string &line) {
    if (line.empty() || line[0] < '?' || line[0] > '|') throw std::runtime_error("bad graph6 order");
    const int order = line[0] - '?';
    if (order < 1 || static_cast<int>(line.size()) != 1 + (order * (order - 1) / 2 + 5) / 6)
        throw std::runtime_error("bad graph6 size");
    for (char ch : line) if (ch < '?' || ch > '~') throw std::runtime_error("bad graph6 byte");
    const int padding = (6 - (order * (order - 1) / 2) % 6) % 6;
    if ((line.back() - '?') & ((1 << padding) - 1)) throw std::runtime_error("bad graph6 padding");
    std::vector<Mask> graph(order);
    int index = 0;
    for (int right = 0; right < order; ++right) for (int left = 0; left < right; ++left, ++index) {
        if (((line[1 + index / 6] - '?') >> (5 - index % 6)) & 1) {
            graph[left] |= bit(right);
            graph[right] |= bit(left);
        }
    }
    return graph;
}

static std::string encode(const std::vector<Mask> &graph) {
    const int order = static_cast<int>(graph.size());
    std::string line(1, static_cast<char>('?' + order));
    int index = 0;
    for (int right = 0; right < order; ++right) for (int left = 0; left < right; ++left, ++index) {
        if (index % 6 == 0) line.push_back('?');
        if (graph[right] & bit(left)) line.back() += 1 << (5 - index % 6);
    }
    return line;
}

static void edge(std::vector<Mask> &graph, int left, int right) {
    graph[left] |= bit(right);
    graph[right] |= bit(left);
}

struct Config {
    int alpha, min_degree;
    std::vector<int> sizes, floors;
    bool no_isolate, least_anchor;
};

static Config config(const std::string &name) {
    if (name == "petersen") return {4, 3, {1, 1, 1}, {1, 1, 1}, false, true};
    if (name == "32-1") return {9, 5, {5, 6, 5, 5}, {85, 73, 85, 85}, true, true};
    throw std::runtime_error("unrecognized configuration");
}

struct Sieve {
    const Config &spec;
    const std::vector<Mask> graph;
    const int order, parts;
    const Mask all;
    int anchor_edges = 0;
    std::vector<int> degree, floor, cap, load, needs;
    std::vector<Mask> groups, chosen, candidates;
    Mask rem = 0, usable = 0;
    Count partitions = 0, degree_pass = 0, alpha_pass = 0, candidate_masks = 0, nodes = 0, windows = 0;
    std::unordered_set<Mask> tried_rem;
    std::string witness;
    bool window_control;

    Sieve(const Config &conf, std::vector<Mask> adj, bool control) : spec(conf), graph(std::move(adj)),
        order(static_cast<int>(graph.size())), parts(static_cast<int>(spec.sizes.size())), all(below(order)),
        degree(order), floor(spec.floors), cap(order), load(order), needs(parts), groups(parts), window_control(control) {
        const int expected_order = spec.alpha == 4 ? 3 : 27;
        if ((!control && order != expected_order) || (control && order != 15))
            throw std::runtime_error("unexpected anchor order");
        for (int vertex = 0; vertex < order; ++vertex) {
            for (Mask others = graph[vertex]; others;)
                if (graph[vertex] & graph[take(others)]) throw std::runtime_error("triangle in anchor");
            degree[vertex] = size(graph[vertex]);
            anchor_edges += degree[vertex];
        }
        anchor_edges /= 2;
        if (control) return;
        if (anchor_edges < floor[0] || has_ind(all, spec.alpha - 1))
            throw std::runtime_error("invalid anchor");
        if (spec.least_anchor) for (int part = 1; part < parts; ++part)
            if (spec.sizes[part] == spec.sizes[0]) floor[part] = std::max(floor[part], anchor_edges);
    }

    bool has_ind(Mask pool, int want) const {
        if (want <= 0) return true;
        if (want == 1) return pool != 0;
        while (size(pool) >= want) {
            const int vertex = take(pool);
            if (has_ind(pool & ~graph[vertex], want - 1)) return true;
        }
        return false;
    }

    bool enumerate(Mask pool, Mask prefix, int want, const std::function<bool(Mask)> &visit) const {
        if (want == 0) return visit(prefix);
        while (size(pool) >= want) {
            const int vertex = take(pool);
            if (enumerate(pool & ~graph[vertex], prefix | bit(vertex), want - 1, visit)) return true;
        }
        return false;
    }

    bool partition(int part, Mask pool, Mask fixed_rem = 0) {
        if (part == parts) return extend(pool | fixed_rem);
        return enumerate(pool, 0, spec.sizes[part], [&](Mask group) {
            if (part > 1 && spec.sizes[part] == spec.sizes[part - 1] && group <= groups[part - 1])
                return false;
            if (fixed_rem && has_ind(fixed_rem | group, spec.alpha - parts + 2)) return false;
            groups[part] = group;
            return partition(part + 1, pool ^ group, fixed_rem);
        });
    }

    bool window(Mask pool, Mask core, Mask has_neighbor, Mask costly, Mask nonseven, int budget, int to_add) {
        if (!to_add) {
            if (core != has_neighbor || !tried_rem.insert(core).second) return false;
            if (has_ind(core, 6)) return false;
            ++windows;
            if (window_control) {
                std::cout << budget << ' ' << nonseven << ' ' << core << '\n';
                return false;
            }
            return partition(1, all ^ core, core);
        }
        if (size(costly) == budget) {
            pool &= ~nonseven;
            for (Mask scan = has_neighbor & ~costly; scan;) pool &= ~graph[take(scan)];
        }
        for (Mask isolated = core & ~has_neighbor; isolated;)
            if (!(graph[take(isolated)] & pool)) return false;
        while (size(pool) >= to_add) {
            const int vertex = take(pool);
            const Mask singleton = bit(vertex);
            const Mask neighbors = graph[vertex] & core;
            const Mask cost = costly | (neighbors & has_neighbor) |
                ((size(neighbors) >= 2 || (singleton & nonseven)) ? singleton : 0);
            if (size(cost) <= budget &&
                window(pool, core | singleton, has_neighbor | neighbors | (neighbors ? singleton : 0),
                       cost, nonseven, budget, to_add - 1)) return true;
        }
        return false;
    }

    bool cycles(Mask path, int start, int second, int tip, int length, Mask nonseven, int budget) {
        for (Mask scan = graph[tip] & ~path & ~below(start + 1); scan;) {
            const int next = take(scan);
            const Mask seen = graph[next] & path;
            const Mask longer = path | bit(next);
            if (seen == (bit(tip) | bit(start))) {
                if (next <= second || ((length + 1) != 5 && (length + 1) != 7)) continue;
                Mask pool = all ^ longer;
                if (budget == 5) for (Mask scan_cycle = longer; scan_cycle;)
                    pool &= ~graph[take(scan_cycle)];
                if (window(pool, longer, longer, longer, nonseven, budget, 11 - (length + 1))) return true;
            } else if (seen == bit(tip) && length + 1 < budget && length + 1 < 7) {
                if (cycles(longer, start, second, next, length + 1, nonseven, budget)) return true;
            }
        }
        return false;
    }

    bool scan_windows(Mask nonseven, int bound) {
        if (bound < 5 || bound > 8) throw std::runtime_error("anchor outside W-first cover");
        tried_rem.clear();
        for (int start = 0; start < order; ++start) {
            for (Mask scan = graph[start] & ~below(start + 1); scan;) {
                const int second = take(scan);
                if (cycles(bit(start) | bit(second), start, second, second, 2, nonseven, bound)) return true;
            }
        }
        return false;
    }

    bool window_first() {
        const int bound = (345 - (anchor_edges + floor[1] + floor[2] + floor[3])) / 2;
        Mask nonseven = 0;
        for (int vertex = 0; vertex < order; ++vertex)
            if (degree[vertex] < 7) nonseven |= bit(vertex);
        return scan_windows(nonseven, bound);
    }

    bool extension_alpha(Mask pool, int max_alpha, Mask current, int cursor = 0) const {
        if (has_ind(pool & ~current, max_alpha)) return false;
        for (int index = cursor; index < static_cast<int>(chosen.size()); ++index)
            if (!extension_alpha(pool, max_alpha - 1, current | chosen[index], index + 1)) return false;
        return true;
    }

    bool alpha_ok(Mask candidate) const {
        return extension_alpha(all, spec.alpha, candidate) &&
               extension_alpha(rem, spec.alpha - parts + 1, candidate) &&
               [&] {
                   for (int part = 1; part < parts; ++part)
                       if (!extension_alpha(all ^ groups[part], spec.alpha - 2, candidate)) return false;
                   return true;
               }();
    }

    std::string materialize() const {
        const int fixed = order + spec.sizes[0];
        std::vector<Mask> whole = graph;
        whole.resize(fixed + 2 * parts);
        for (int index = 0; index < spec.sizes[0]; ++index) {
            for (Mask neighbors = chosen[index]; neighbors;)
                edge(whole, order + index, take(neighbors));
        }
        for (int left = 0; left < parts; ++left) {
            for (int right = left + 1; right < parts; ++right) {
                edge(whole, fixed + 2 * left, fixed + 2 * right + 1);
                edge(whole, fixed + 2 * left + 1, fixed + 2 * right);
            }
            for (Mask group = left ? groups[left] : below(fixed) ^ all; group;) {
                const int vertex = take(group);
                edge(whole, fixed + 2 * left, vertex);
                edge(whole, fixed + 2 * left + 1, vertex);
            }
        }
        return encode(whole);
    }

    bool choose(size_t first) {
        ++nodes;
        const int remaining = spec.sizes[0] - static_cast<int>(chosen.size());
        std::vector<int> possible(parts);
        for (int vertex = 0; vertex < order; ++vertex) {
            const int min_load = std::max(0, spec.min_degree - degree[vertex] - ((rem & bit(vertex)) ? 0 : 2));
            const int extra = std::min(remaining, cap[vertex] - load[vertex]);
            if (load[vertex] + extra < min_load) return false;
            for (int part = 1; part < parts; ++part)
                if (!(groups[part] & bit(vertex))) possible[part] += extra;
        }
        for (int part = 1; part < parts; ++part)
            if (std::min(possible[part], remaining * (spec.alpha - 2)) < needs[part]) return false;
        if (!remaining) {
            witness = materialize();
            return true;
        }
        for (size_t index = first; index < candidates.size(); ++index) {
            const Mask candidate = candidates[index];
            bool viable = true;
            for (Mask mask = candidate; mask;) {
                const int vertex = take(mask);
                if (load[vertex] == cap[vertex]) { viable = false; break; }
            }
            if (!viable || (!chosen.empty() && !alpha_ok(candidate))) continue;
            chosen.push_back(candidate);
            for (Mask mask = candidate; mask;) ++load[take(mask)];
            for (int part = 1; part < parts; ++part) needs[part] -= size(candidate & ~groups[part]);
            if (choose(index)) return true;
            for (int part = 1; part < parts; ++part) needs[part] += size(candidate & ~groups[part]);
            for (Mask mask = candidate; mask;) --load[take(mask)];
            chosen.pop_back();
        }
        return false;
    }

    bool extend(Mask leftover) {
        ++partitions;
        rem = leftover;
        const int attachment_cap = spec.alpha - 2;
        const int new_edge_cap = attachment_cap * spec.sizes[0];
        int required_sum = 0;
        for (int part = 1; part < parts; ++part) {
            int deleted = 0;
            for (Mask mask = groups[part]; mask;) deleted += degree[take(mask)];
            needs[part] = floor[part] - anchor_edges + deleted;
            if (needs[part] > new_edge_cap) return false;
            required_sum += needs[part];
        }
        int rem_cap = 0;
        usable = 0;
        for (int vertex = 0; vertex < order; ++vertex) {
            const bool in_rem = rem & bit(vertex);
            if (in_rem && spec.no_isolate && !(graph[vertex] & rem)) return false;
            int upper = (in_rem ? spec.alpha : attachment_cap) - degree[vertex];
            for (int part = 1; part < parts; ++part) {
                if (!(groups[part] & bit(vertex)))
                    upper = std::min(upper, attachment_cap - degree[vertex] + size(graph[vertex] & groups[part]));
            }
            cap[vertex] = std::min(spec.sizes[0], upper);
            if (cap[vertex] < 0) return false;
            if (in_rem) rem_cap += cap[vertex];
            if (cap[vertex] > 0) usable |= bit(vertex);
        }
        if (required_sum > (parts - 2) * new_edge_cap + rem_cap) return false;
        ++degree_pass;
        if (has_ind(rem, spec.alpha - parts + 1)) return false;
        for (int part = 1; part < parts; ++part)
            if (has_ind(rem | groups[part], spec.alpha - parts + 2)) return false;
        ++alpha_pass;
        candidates.clear();
        for (int count = std::max(0, spec.min_degree - 2); count <= attachment_cap; ++count)
            enumerate(usable, 0, count, [&](Mask candidate) {
                if (alpha_ok(candidate)) candidates.push_back(candidate);
                return false;
            });
        candidate_masks += candidates.size();
        return !candidates.empty() && choose(0);
    }
};

int main(int argc, char **argv) {
    if (argc != 2) { std::cerr << "usage: crown_sieve petersen|32-1|32-1-direct|window-control < anchors.g6\n"; return 2; }
    try {
        const std::string mode = argv[1];
        const bool control = mode == "window-control";
        const Config spec = config(mode == "32-1-direct" || control ? "32-1" : mode);
        std::string line;
        int anchor = 0;
        while (std::getline(std::cin, line)) {
            Sieve sieve(spec, parse(line), control);
            if (control) {
                std::cout << "control " << ++anchor << '\n';
                for (int bound : {5, 7, 8}) for (Mask nonseven : {Mask{0}, bit(0) | bit(3) | bit(12)})
                    sieve.scan_windows(nonseven, bound);
                continue;
            }
            const bool survives = mode == "32-1" ? sieve.window_first() : sieve.partition(1, sieve.all);
            std::cout << ++anchor << ' ' << sieve.anchor_edges << ' ' << sieve.partitions << ' '
                      << sieve.degree_pass << ' ' << sieve.alpha_pass << ' ' << sieve.candidate_masks
                      << ' ' << sieve.nodes << ' ' << sieve.windows << ' ' << (survives ? "SAT" : "EMPTY") << std::endl;
            if (survives) std::cout << "witness " << sieve.witness << std::endl;
        }
        if (!anchor) throw std::runtime_error("no anchors");
    } catch (const std::exception &ex) {
        std::cerr << ex.what() << '\n';
        return 1;
    }
}
