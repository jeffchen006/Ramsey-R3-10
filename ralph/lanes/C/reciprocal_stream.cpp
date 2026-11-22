#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <unordered_map>
#include <vector>

using Mask = uint64_t;
using Host = std::vector<Mask>;
using Mark = std::array<Mask, 3>;
using Key = std::array<uint32_t, 10>;

int size(Mask mask) { return std::popcount(mask); }
Mask bit(int vertex) { return Mask(1) << vertex; }
Mask full(int count) { return bit(count) - 1; }
int take(Mask& mask) { auto vertex = std::countr_zero(mask); mask &= mask - 1; return vertex; }
std::vector<int> sites(Mask mask) {
    std::vector<int> vertices;
    while (mask) vertices.push_back(take(mask));
    return vertices;
}

template<class Visit>
void subsets(Mask avail, int count, Mask picked, const Host* conflicts, const Visit& visit) {
    if (!count) { visit(picked); return; }
    while (size(avail) >= count) {
        auto vertex = take(avail);
        subsets(conflicts ? avail & ~(*conflicts)[vertex] : avail,
                count - 1, picked | bit(vertex), conflicts, visit);
    }
}

Host decode(const std::string& line, int order) {
    assert(!line.empty() && line.front() - 63 == order);
    assert(line.size() == size_t(1 + (order * (order - 1) / 2 + 5) / 6));
    Host adj(order);
    for (int right = 1, wire = 0; right < order; ++right)
        for (int left = 0; left < right; ++left, ++wire)
            if (((line[1 + wire/6] - 63) >> (5-wire%6)) & 1) {
                adj[left] |= bit(right); adj[right] |= bit(left);
            }
    return adj;
}

struct Params { int degree, cap, roots, core; int width() const { return degree-roots; } };
struct Card { int host; Mask core; std::vector<Mark> marks; };

template<class Admit>
std::map<Mask, std::vector<Mark>> cards(const Host& adj, Params params, const Admit& admit,
                                       uint64_t& local, uint64_t& local_cards) {
    const int order = adj.size(), width = params.width(), cap = params.cap;
    const int target = order - params.core, max_overlap = cap - params.roots;
    assert(params.roots == 2 || params.roots == 3);
    std::array<Host, 3> spent{Host(order), Host(order), Host(order)};
    for (int right = 1; right < order; ++right)
        for (int left = 0; left < right; ++left) {
            int common = size(adj[left] & adj[right]);
            for (int level = 0; level < 3; ++level) if (common >= cap-level) {
                spent[level][left] |= bit(right); spent[level][right] |= bit(left);
            }
        }
    auto clear = [](Mask picked, const Host& conflicts) {
        for (Mask rest = picked; rest; ) if (conflicts[take(rest)] & rest) return false;
        return true;
    };
    std::vector<Mask> independent;
    subsets(full(order), width, 0, &adj, [&](Mask picked) {
        if (!clear(picked, spent[0])) return;
        for (auto neighbors : adj) if (size(neighbors & picked) > cap) return;
        independent.push_back(picked);
    });
    struct Decision { bool feasible, selected; };
    std::unordered_map<Mask, Decision> checked;
    std::map<Mask, std::vector<Mark>> result;
    auto place = [&](Mask first, Mask second, Mask third) {
        Mask private_sites = first | second | third, core = full(order) ^ private_sites;
        auto [decision, fresh] = checked.try_emplace(core, Decision{true, false});
        if (fresh) {
            for (Mask rest = core; rest;) {
                int vertex = take(rest), desired = params.degree - size(adj[vertex] & private_sites);
                if (desired < 0 || desired > width) { decision->second.feasible = false; break; }
            }
            if (decision->second.feasible) decision->second.selected = admit(core);
        }
        if (!decision->second.feasible) return;
        for (Mask rest = private_sites; rest;) {
            int vertex = take(rest);
            int anchors = bool(first & bit(vertex)) + bool(second & bit(vertex)) + bool(third & bit(vertex));
            if (size(adj[vertex]) + anchors > params.degree ||
                size(adj[vertex] & private_sites) + anchors < params.degree - width) return;
        }
        ++local;
        auto& verdict = decision->second;
        if (verdict.selected) {
            Mark mark{first,second,third};
            std::sort(mark.begin(), mark.begin()+params.roots);
            auto& group = result[core];
            if (group.empty()) ++local_cards;
            group.push_back(mark);
        }
    };
    const int min_overlap = params.roots == 2 ? 2*width-target : 3*width-target-2*max_overlap;
    auto pair_ok = [&](Mask intersection) {
        int both = size(intersection);
        return min_overlap <= both && both <= max_overlap && clear(intersection, spent[1]);
    };
    std::vector<std::vector<int>> linked(independent.size());
    for (size_t first = 0; first < independent.size(); ++first) {
        for (size_t second = 0; second < first; ++second) {
            Mask first_mask = independent[first], second_mask = independent[second];
            if (!pair_ok(first_mask & second_mask)) continue;
            if (params.roots == 2) {
                if (size(first_mask | second_mask) == target) place(first_mask, second_mask, 0);
                continue;
            }
            for (int third : linked[second]) {
                Mask third_mask = independent[third];
                if (size(first_mask | second_mask | third_mask) != target ||
                    !pair_ok(first_mask & third_mask) ||
                    !clear(first_mask & second_mask & third_mask, spent[2])) continue;
                place(first_mask,second_mask,third_mask);
            }
            linked[first].push_back(second);
        }
    }
    return result;
}

Key fingerprint(const Host& adj, Mask core, Params params, bool ask) {
    Key key{};
    std::array<unsigned,22> colors{};
    for (int vertex : sites(core)) {
        int internal = size(adj[vertex] & core);
        int degree = size(adj[vertex]);
        colors[vertex] = 1+8*internal+(ask ? params.degree+internal-degree : degree);
        assert(colors[vertex] && colors[vertex] <= 31 && internal <= 3);
    }
    int index = 0;
    for (int vertex : sites(core)) {
        std::array<unsigned,3> neighbors{};
        int cursor = 0;
        for (Mask rest = adj[vertex] & core; rest;) neighbors.at(cursor++) = colors[take(rest)];
        std::sort(neighbors.begin(),neighbors.end());
        uint32_t code = colors[vertex];
        for (auto color : neighbors) code = code*32 + color;
        key[index++] = code;
    }
    std::sort(key.begin(),key.end());
    return key;
}

template<class Visit>
void align(const Host& from, Mask first, const Host& to, Mask second, Params params, const Visit& visit) {
    std::array<Mask, 22> domains{};
    auto ordering = sites(first);
    for (int left : ordering) {
        int internal = size(from[left] & first);
        for (Mask rest = second; rest;) {
            int right = take(rest);
            if (size(to[right] & second) == internal && size(from[left])+size(to[right]) == params.degree+internal)
                domains[left] |= bit(right);
        }
        if (!domains[left]) return;
    }
    std::sort(ordering.begin(), ordering.end(), [&](int aa,int bb){ return size(domains[aa]) < size(domains[bb]); });
    std::array<int,22> mapping{};
    auto recurse = [&](auto self, size_t position, Mask unused) -> void {
        if (position == ordering.size()) { visit(mapping); return; }
        int left = ordering[position];
        for (Mask rest = domains[left] & unused; rest;) {
            int right = take(rest);
            bool agrees = true;
            for (size_t earlier = 0; earlier < position; ++earlier) {
                int other = ordering[earlier];
                if (bool(from[left] & bit(other)) != bool(to[right] & bit(mapping[other]))) { agrees = false; break; }
            }
            if (agrees) { mapping[left] = right; self(self, position+1, unused ^ bit(right)); }
        }
    };
    recurse(recurse,0,second);
}

void edge(Host& graph, int first, int second) { graph[first] |= bit(second); graph[second] |= bit(first); }
struct Matched { Host lower; int left, right; };
Matched merge(const Host& from, const Card& first, const Mark& first_mark,
              const Host& to, const Card& second, const Mark& second_mark,
              const std::array<int,22>& mapping, Params params) {
    int left = from.size()-params.core, right = to.size()-params.core;
    int neutral = left+right, roots = neutral+params.core;
    Host partial(roots+2*params.roots);
    std::array<int,22> left_names{}, right_names{};
    int cursor = 0;
    for (int vertex : sites(full(from.size()) ^ first.core)) left_names[vertex] = cursor++;
    for (int vertex : sites(full(to.size()) ^ second.core)) right_names[vertex] = cursor++;
    for (int same : sites(first.core)) { left_names[same] = cursor; right_names[mapping[same]] = cursor++; }
    auto insert = [&](const Host& source, const Mark& mark, const auto& names, int root_offset) {
        for (int vertex = 0; vertex < (int)source.size(); ++vertex) {
            for (int neighbor : sites(source[vertex] & full(vertex))) edge(partial,names[vertex],names[neighbor]);
            for (int role = 0; role < params.roots; ++role)
                if (mark[role] & bit(vertex)) edge(partial,names[vertex],root_offset+role);
        }
    };
    insert(from,first_mark,left_names,roots);
    insert(to,second_mark,right_names,roots+params.roots);
    for (int aa = 0; aa < params.roots; ++aa)
        for (int bb = 0; bb < params.roots; ++bb) edge(partial,roots+aa,roots+params.roots+bb);
    return {std::move(partial),left,right};
}

Mask independent(const Host& graph, Mask remaining, int count, Mask picked=0) {
    if (!count) return picked;
    while (size(remaining) >= count) {
        int vertex = take(remaining);
        if (auto witness = independent(graph, remaining & ~graph[vertex], count-1, picked | bit(vertex))) return witness;
    }
    return 0;
}

struct Verdict { std::string reason; Mask witness = 0; };
Verdict evaluate(const Matched& matched, Params params) {
    const auto& lower = matched.lower;
    const int split = matched.left + matched.right, order = lower.size();
    const Mask left = full(matched.left), right = full(split)^left, fixed = full(order)^full(split);
    for (int vertex = 0; vertex < order; ++vertex) {
        if (size(lower[vertex]) > params.degree || (vertex >= split && size(lower[vertex]) != params.degree))
            return {"degree", bit(vertex)};
        for (int other = 0; other < vertex; ++other)
            if (size(lower[vertex] & lower[other]) > params.cap) return {"cap",bit(vertex)|bit(other)};
            else if (other >= split && !(lower[vertex]&bit(other)) && !(lower[vertex]&lower[other]))
                return {"fixed-undominated",bit(vertex)|bit(other)};
    }
    auto upper = lower;
    for (int aa : sites(left)) for (int bb : sites(right))
        if (!(lower[aa] & lower[bb])) edge(upper,aa,bb);
    Mask all = full(order);
    if (auto witness = independent(upper,all,params.degree+1)) return {"upper-IS",witness};
    std::vector<std::vector<Mask>> domains(split);
    for (int vertex = 0; vertex < split; ++vertex) {
        Mask other = vertex < matched.left ? right : left;
        int need = params.degree-size(lower[vertex]);
        std::vector<Mask> hits;
        for (int endpoint : sites(fixed))
            if (!(lower[vertex] & bit(endpoint)) && !(lower[vertex] & lower[endpoint])) hits.push_back(lower[endpoint]&other);
        subsets(upper[vertex]&other,need,0,&lower,[&](Mask pattern) {
            for (auto hit : hits) if (!(hit & pattern)) return;
            for (int endpoint : sites(fixed)) if (size((lower[vertex]|pattern) & lower[endpoint]) > params.cap) return;
            domains[vertex].push_back(pattern);
        });
        if (domains[vertex].empty()) return {"row-empty",bit(vertex)};
    }
    std::vector<Mask> possible(split), required(split);
    while (true) {
        for (int vertex = 0; vertex < split; ++vertex) {
            possible[vertex] = 0; required[vertex] = all;
            for (auto pattern : domains[vertex]) { possible[vertex] |= pattern; required[vertex] &= pattern; }
        }
        bool changed = false;
        for (int vertex = 0; vertex < split; ++vertex) {
            Mask allowed = 0, forced = 0;
            for (int other : sites(vertex < matched.left ? right : left)) {
                if (possible[other] & bit(vertex)) allowed |= bit(other);
                if (required[other] & bit(vertex)) forced |= bit(other);
            }
            auto removed = std::erase_if(domains[vertex], [&](Mask pattern) { return (pattern & ~allowed) || (forced & ~pattern); });
            if (domains[vertex].empty()) return {"row-column",bit(vertex)};
            changed |= removed != 0;
        }
        if (changed) continue;
        auto envelope = lower;
        for (int vertex = 0; vertex < split; ++vertex) envelope[vertex] |= possible[vertex];
        if (auto witness = independent(envelope,all,params.degree+1)) return {"domain-IS",witness};
        std::vector<Mask> mandatory(split);
        for (int aa : sites(left)) for (int bb : sites(possible[aa] & ~required[aa])) {
            envelope[aa] ^= bit(bb); envelope[bb] ^= bit(aa);
            if (independent(envelope,all,params.degree+1)) { mandatory[aa] |= bit(bb); mandatory[bb] |= bit(aa); }
            envelope[aa] ^= bit(bb); envelope[bb] ^= bit(aa);
        }
        for (int vertex = 0; vertex < split; ++vertex) {
            auto removed = std::erase_if(domains[vertex], [&](Mask pattern) { return (mandatory[vertex] & ~pattern) != 0; });
            if (domains[vertex].empty()) return {"forced-domain",bit(vertex)};
            changed |= removed != 0;
        }
        if (!changed) return {"live"};
    }
}

double cpu() { return double(std::clock())/CLOCKS_PER_SEC; }

int main(int argc, char** argv) {
    assert(argc == 11);
    std::string mode = argv[1];
    assert(mode == "indexed" || mode == "direct" || mode == "cards" || mode == "planted");
    std::ifstream from_file(argv[2]), to_file(argv[3]);
    const int from_order = std::stoi(argv[4]), to_order = std::stoi(argv[5]);
    const Params params{std::stoi(argv[6]),std::stoi(argv[7]),std::stoi(argv[8]),std::stoi(argv[9])};
    std::ofstream journal(argv[10]);
    assert(from_file && to_file && journal);
    std::string line;
    std::vector<Host> from_hosts;
    std::map<Key,std::vector<Card>> index;
    std::vector<Card> unindexed;
    uint64_t from_local = 0, from_cards = 0, to_local = 0, to_kept = 0;
    while (from_file >> line) {
        int row = from_hosts.size();
        const auto& from = from_hosts.emplace_back(decode(line,from_order));
        auto groups = cards(from,params,[](Mask) { return true; },from_local,from_cards);
        for (auto& [core,marks] : groups) {
            if (mode == "cards") journal << row << ' ' << core << ' ' << marks.size() << '\n';
            else if (mode != "direct") index[fingerprint(from,core,params,true)].push_back({row,core,std::move(marks)});
            else unindexed.push_back({row,core,std::move(marks)});
        }
    }
    std::cout << "left hosts " << from_hosts.size() << " marks " << from_local << " cards " << from_cards
              << " indexed keys " << index.size() << " cpu " << cpu() << std::endl;
    if (mode == "cards") return 0;
    uint64_t pairs = 0, marked_pairs = 0, card_maps = 0, role_maps = 0, total_hosts = 0, hosts_matched = 0;
    double mark_cpu = 0, map_cpu = 0;
    std::map<std::string,uint64_t> outcomes;
    auto counts = [&]() {
        std::cout << "right hosts " << total_hosts << " marks " << to_local << " kept cards " << to_kept
                  << " matched hosts " << hosts_matched << " card pairs " << pairs << " marked pairs " << marked_pairs
                  << " card maps " << card_maps << " role maps " << role_maps << " marks CPU covered " << mark_cpu
                  << " maps CPU covered " << map_cpu << " total CPU " << cpu();
        for (auto& [reason,count] : outcomes) std::cout << ' ' << reason << ' ' << count;
        std::cout << std::endl;
    };
    while (to_file >> line) {
        int row = total_hosts++;
        double start = cpu();
        auto to = decode(line,to_order);
        auto groups = cards(to,params,[&](Mask core) {
            return mode == "direct" || index.contains(fingerprint(to,core,params,false));
        },to_local,to_kept);
        mark_cpu += cpu()-start;
        start = cpu();
        if (!groups.empty()) ++hosts_matched;
        for (auto& [core,marks] : groups) {
            Card second{row,core,std::move(marks)};
            const auto& eligible = mode == "direct" ? unindexed : index.at(fingerprint(to,core,params,false));
            for (const auto& first : eligible) {
                if (mode == "planted" && first.host != second.host) continue;
                const auto& from = from_hosts[first.host];
                ++pairs; marked_pairs += first.marks.size()*second.marks.size();
                align(from,first.core,to,second.core,params,[&](const auto& mapping) {
                    ++card_maps;
                    std::string mapping_text;
                    for (int vertex : sites(first.core)) mapping_text += ' ' + std::to_string(mapping[vertex]);
                    for (const auto& first_mark : first.marks) for (const auto& second_mark : second.marks) {
                        ++role_maps;
                        auto matched = merge(from,first,first_mark,to,second,second_mark,mapping,params);
                        auto verdict = evaluate(matched,params);
                        ++outcomes[verdict.reason];
                        journal << first.host << ' ' << first.core;
                        for (auto roots : first_mark) journal << ' ' << roots;
                        journal << ' ' << second.host << ' ' << second.core;
                        for (auto roots : second_mark) journal << ' ' << roots;
                        journal << mapping_text << ' ' << verdict.reason << ' ' << verdict.witness << '\n';
                    }
                });
            }
        }
        map_cpu += cpu()-start;
        if (total_hosts%2048 == 0) counts();
    }
    counts();
}
