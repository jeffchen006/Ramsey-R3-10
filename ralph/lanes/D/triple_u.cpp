#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Mask = uint32_t;

int size(Mask mask) { return __builtin_popcount(mask); }
int lowest(Mask mask) { return __builtin_ctz(mask); }
Mask bit(int vertex) { return 1u << vertex; }

struct Partition {
    const int order;
    const Mask whole;
    const std::array<Mask, 3> groups;
    std::vector<Mask> adj, saturated;
    std::vector<int> slack;
    std::array<std::array<int, 15>, 15> pair_budget{};
    std::vector<uint8_t> indep, alpha;

    Partition(int order, std::array<Mask, 3> groups, const std::string& graph)
        : order(order), whole(bit(order) - 1), groups(groups), adj(order), saturated(order),
          slack(order), indep(whole + 1), alpha(whole + 1) {
        if (graph.size() != static_cast<size_t>(1 + (order * (order - 1) / 2 + 5) / 6) ||
            graph.front() != order + 63 || (groups[0] | groups[1] | groups[2]) != whole ||
            size(groups[0]) + size(groups[1]) + size(groups[2]) != order ||
            std::any_of(graph.begin(), graph.end(), [](char ch) { return ch < 63 || ch > 126; }))
            throw std::runtime_error("invalid graph6 or partition");
        int next = 0;
        for (int right = 1; right < order; ++right) {
            for (int left = 0; left < right; ++left, ++next) {
                if (((graph[1 + next / 6] - 63) >> (5 - next % 6)) & 1) {
                    adj[left] |= bit(right);
                    adj[right] |= bit(left);
                }
            }
        }
        for (int left = 0; left < order; ++left) {
            int own = 0;
            while (!(groups[own] & bit(left))) ++own;
            slack[left] = 8 - size(adj[left]);
            for (int right = 0; right < order; ++right) {
                if (right == left) continue;
                int budget = 4 - size(adj[left] & adj[right]) - bool(groups[own] & bit(right));
                if (budget < 0) throw std::runtime_error("negative codegree budget");
                pair_budget[left][right] = budget;
                if (budget == 0) saturated[left] |= bit(right);
            }
        }
        indep[0] = 1;
        for (Mask mask = 1; mask <= whole; ++mask) {
            const int vertex = lowest(mask);
            const Mask tail = mask ^ bit(vertex);
            indep[mask] = indep[tail] && !(tail & adj[vertex]);
            alpha[mask] = std::max<int>(alpha[tail], 1 + alpha[tail & ~adj[vertex]]);
        }
    }

    std::vector<Mask> candidates(int alpha_u) const {
        std::vector<Mask> result;
        for (Mask mask = 0; mask <= whole; ++mask) {
            if (!indep[mask] || size(mask) > alpha_u) continue;
            if (std::any_of(groups.begin(), groups.end(), [mask](Mask group) { return size(group & mask) > 3; }))
                continue;
            bool valid = true;
            for (int vertex = 0; valid && vertex < order; ++vertex) {
                if ((mask & bit(vertex)) && (slack[vertex] <= 0 || (saturated[vertex] & mask))) valid = false;
                if (size(adj[vertex] & mask) > 4) valid = false;
            }
            if (valid) result.push_back(mask);
        }
        std::sort(result.begin(), result.end(), [](Mask left, Mask right) {
            if (size(left) != size(right)) return size(left) > size(right);
            return left < right;
        });
        return result;
    }

    bool respect_budget(Mask mask, int count) const {
        for (Mask members = mask; members; members &= members - 1) {
            const int left = lowest(members);
            if (slack[left] < count) return false;
            for (Mask tail = members & (members - 1); tail; tail &= tail - 1) {
                if (pair_budget[left][lowest(tail)] < count) return false;
            }
        }
        return true;
    }

    bool matching_type(int want) const {
        std::array<std::vector<int>, 3> vertices;
        for (size_t group = 0; group < groups.size(); ++group) {
            for (Mask members = groups[group]; members; members &= members - 1)
                vertices[group].push_back(lowest(members));
        }
        auto second = vertices[1];
        do {
            bool valid = true;
            for (size_t idx = 0; idx < second.size(); ++idx)
                valid &= bool(adj[vertices[0][idx]] & bit(second[idx]));
            if (!valid) continue;
            auto third = vertices[2];
            do {
                valid = true;
                for (size_t idx = 0; idx < third.size(); ++idx)
                    valid &= bool(adj[vertices[0][idx]] & bit(third[idx]));
                if (!valid) continue;
                std::vector<int> perm(third.size());
                for (size_t idx = 0; idx < third.size(); ++idx) perm[idx] = idx;
                do {
                    Mask orbit = 0;
                    int current = 0;
                    do {
                        orbit |= bit(current);
                        current = perm[current];
                    } while (current != 0);
                    if ((size(orbit) == static_cast<int>(perm.size())) != bool(want)) continue;
                    valid = true;
                    for (size_t idx = 0; idx < third.size(); ++idx)
                        valid &= bool(adj[second[idx]] & bit(third[perm[idx]]));
                    if (valid) return true;
                } while (std::next_permutation(perm.begin(), perm.end()));
            } while (std::next_permutation(third.begin(), third.end()));
        } while (std::next_permutation(second.begin(), second.end()));
        return false;
    }
};

int main(int argc, char** argv) {
    if (argc != 4) throw std::runtime_error("usage: triple_u group_size work_cap count_all (0 or 1)");
    const int group_size = std::stoi(argv[1]);
    const uint64_t work_cap = std::stoull(argv[2]);
    const bool count_all = std::stoi(argv[3]);
    if ((group_size != 4 && group_size != 5) || !work_cap)
        throw std::runtime_error("invalid group size or cap");
    uint64_t rows = 0, rejected = 0, viable = 0, capped = 0, work = 0;
    uint64_t total_candidates = 0;
    std::array<uint64_t, 4> types{};
    std::string line;
    while (std::getline(std::cin, line)) {
        std::istringstream row(line);
        uint64_t graph_id;
        std::array<Mask, 3> groups{};
        std::string graph;
        if (!(row >> graph_id >> groups[0] >> groups[1] >> groups[2] >> graph) ||
            std::any_of(groups.begin(), groups.end(), [group_size](Mask group) { return size(group) != group_size; }))
            throw std::runtime_error("malformed row");
        const Partition part(3 * group_size, groups, graph);
        if (part.alpha[part.whole] != group_size) throw std::runtime_error("incorrect alpha");
        const auto candidates = part.candidates(group_size);
        total_candidates += candidates.size();
        std::vector<std::vector<size_t>> compatible(candidates.size());
        for (size_t left = 0; left < candidates.size(); ++left) {
            for (size_t right = left; right < candidates.size(); ++right) {
                const Mask overlap = candidates[left] & candidates[right];
                const Mask residual = part.whole ^ (candidates[left] | candidates[right]);
                if (size(overlap) <= 3 && part.alpha[residual] <= group_size - 1 && part.respect_budget(overlap, 2))
                    compatible[left].push_back(right);
            }
        }
        uint64_t count = 0, checked = 0;
        std::array<Mask, 3> witness{};
        int status = 0;
        for (size_t left = 0; left < candidates.size() && !status; ++left) {
            for (const auto middle : compatible[left]) {
                auto scan = std::lower_bound(compatible[left].begin(), compatible[left].end(), middle);
                auto other = std::lower_bound(compatible[middle].begin(), compatible[middle].end(), middle);
                const Mask two = candidates[left] | candidates[middle];
                const Mask common = candidates[left] & candidates[middle];
                while (scan != compatible[left].end() && other != compatible[middle].end()) {
                    if (*scan < *other) { ++scan; continue; }
                    if (*other < *scan) { ++other; continue; }
                    if (checked == work_cap) { status = -1; break; }
                    ++checked;
                    const Mask last = candidates[*scan];
                    ++scan;
                    ++other;
                    if (part.alpha[part.whole ^ (two | last)] > group_size - 2 ||
                        !part.respect_budget(common & last, 3)) continue;
                    if (count++ == 0) witness = {candidates[left], candidates[middle], last};
                    if (!count_all) { status = 1; break; }
                }
                if (status) break;
            }
        }
        if (status != -1 && count) status = 1;
        const int matching = (part.matching_type(1) ? 1 : 0) + (part.matching_type(0) ? 2 : 0);
        if (!matching) throw std::runtime_error("missing matching witness");
        ++types[matching];
        if (status < 0) ++capped;
        if (status == 0) ++rejected;
        if (status == 1) ++viable;
        ++rows;
        work += checked;
        std::cout << graph_id << '\t' << groups[0] << '\t' << groups[1] << '\t' << groups[2] << '\t'
                  << status << '\t' << count << '\t' << checked << '\t' << candidates.size() << '\t'
                  << matching << '\t' << witness[0] << '\t' << witness[1] << '\t' << witness[2] << '\n';
    }
    std::cerr << "rows=" << rows << " viable=" << viable << " rejected=" << rejected << " capped=" << capped
              << " candidates=" << total_candidates << " triples_tested=" << work << " matching_types="
              << types[1] << ',' << types[2] << ',' << types[3] << '\n';
}
