#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <tuple>
#include <vector>

using Mask = std::uint32_t;
using Triple = std::array<int, 3>;
using Pack = std::array<Mask, 3>;
using Panel = std::array<std::array<bool, 3>, 3>;
using Graph = std::vector<Mask>;

int size(Mask mask) { return __builtin_popcount(mask); }
Mask bit(int site) { return Mask(1) << site; }
bool has(Mask mask, int site) { return (mask & bit(site)) != 0; }
Mask full(const Graph& graph) { return bit(graph.size()) - 1; }

std::vector<int> sites(Mask mask) {
    std::vector<int> result;
    while (mask) {
        result.push_back(__builtin_ctz(mask));
        mask &= mask - 1;
    }
    return result;
}

std::vector<Graph> catalogue(const std::string& file) {
    std::ifstream input(file);
    assert(input);
    std::vector<Graph> result;
    for (std::string line; std::getline(input, line);) {
        assert(!line.empty() && line.front() >= 'A' && line.front() <= 'U');
        const int order = line.front() - 63;
        assert(line.size() == 1u + (order * (order - 1) / 2 + 5) / 6);
        Graph graph(order);
        int index = 0;
        for (int col = 1; col < order; ++col) {
            for (int row = 0; row < col; ++row, ++index) {
                if (((line[1 + index / 6] - 63) >> (5 - index % 6)) & 1) {
                    graph[row] |= bit(col);
                    graph[col] |= bit(row);
                }
            }
        }
        result.push_back(graph);
    }
    assert(!result.empty());
    return result;
}

bool independent(const Graph& graph, Mask selected) {
    for (Mask todo = selected; todo; todo &= todo - 1) {
        if (graph[__builtin_ctz(todo)] & selected) return false;
    }
    return true;
}

bool has_independent(const Graph& graph, Mask remaining, int need) {
    if (!need) return true;
    while (size(remaining) >= need) {
        int next = __builtin_ctz(remaining);
        remaining ^= bit(next);
        if (has_independent(graph, remaining & ~graph[next], need - 1)) return true;
    }
    return false;
}

Mask antineighborhood(const Graph& graph, const std::vector<int>& anchors) {
    Mask result = full(graph);
    for (int anchor : anchors) result &= ~(graph[anchor] | bit(anchor));
    return result;
}

std::vector<int> alpha_table(const Graph& graph) {
    std::vector<int> table(full(graph) + 1);
    for (Mask mask = 1; mask <= full(graph); ++mask) {
        if (independent(graph, mask)) table[mask] = size(mask);
    }
    for (int site = 0; site < int(graph.size()); ++site) {
        for (Mask mask = bit(site); mask <= full(graph); ++mask) {
            if (has(mask, site)) table[mask] = std::max(table[mask], table[mask ^ bit(site)]);
        }
    }
    return table;
}

std::vector<std::vector<Mask>> atlas(const Graph& graph, int target, int spoke_count) {
    const auto alpha = alpha_table(graph);
    assert(alpha.back() < target);
    std::vector<Mask> options;
    for (Mask mask = 0; mask <= full(graph); ++mask) {
        if (size(mask) < target && alpha[mask] == size(mask) && alpha[full(graph) ^ mask] < target)
            options.push_back(mask);
    }
    auto fit_pair = [&](Mask first, Mask second) {
        return alpha[full(graph) ^ (first | second)] <= target - 2;
    };
    std::vector<std::vector<Mask>> entries;
    for (std::size_t first = 0; first < options.size(); ++first) {
        for (std::size_t second = first; second < options.size(); ++second) {
            if (!fit_pair(options[first], options[second])) continue;
            if (spoke_count == 2) {
                entries.push_back({options[first], options[second]});
                continue;
            }
            for (std::size_t third = second; third < options.size(); ++third) {
                const Mask united = options[first] | options[second] | options[third];
                if (alpha[full(graph) ^ united] <= target - 3 &&
                    fit_pair(options[first], options[third]) && fit_pair(options[second], options[third])) {
                    entries.push_back({options[first], options[second], options[third]});
                }
            }
        }
    }
    return entries;
}

Panel rectangle(const Pack& rows, const Triple& target) {
    Panel result{};
    for (int row = 0; row < 3; ++row)
        for (int col = 0; col < 3; ++col)
            result[row][col] = has(rows[row], target[col]);
    return result;
}

Panel transpose(const Panel& matrix) {
    Panel result{};
    for (int row = 0; row < 3; ++row)
        for (int col = 0; col < 3; ++col)
            result[row][col] = matrix[col][row];
    return result;
}

bool restrict_rectangle(std::map<Panel, std::vector<Pack>>& first,
                        std::map<Panel, std::vector<Pack>>& second) {
    for (auto item = first.begin(); item != first.end();) {
        if (!second.count(item->first)) item = first.erase(item);
        else ++item;
    }
    for (auto item = second.begin(); item != second.end();) {
        if (!first.count(item->first)) item = second.erase(item);
        else ++item;
    }
    return !first.empty();
}

struct Frame {
    int host;
    std::vector<Mask> marks;
    std::array<int, 2> zero;
    std::vector<Triple> groups;
    bool triple = false;
    int private_degree_sum = 0;
};

bool legal_frame(const Graph& graph, const std::vector<Mask>& marks, int degree, int cap, int zeros) {
    Mask joined = 0;
    for (std::size_t row = 0; row < marks.size(); ++row) {
        const Mask mark = marks[row];
        if (size(mark) != degree - int(marks.size()) || !independent(graph, mark)) return false;
        joined |= mark;
        for (std::size_t prev = 0; prev < row; ++prev) {
            if (size(mark & marks[prev]) + int(marks.size()) > cap) return false;
        }
    }
    if (int(graph.size()) - size(joined) != zeros) return false;
    for (int site = 0; site < int(graph.size()); ++site) {
        int degree_spent = size(graph[site]);
        for (Mask mark : marks) {
            degree_spent += has(mark, site);
            if (size(mark & graph[site]) > cap) return false;
        }
        if (degree_spent > degree) return false;
        for (int prev = 0; prev < site; ++prev) {
            int common = size(graph[site] & graph[prev]);
            for (Mask mark : marks) common += has(mark, site) && has(mark, prev);
            if (common > cap) return false;
        }
    }
    return true;
}

std::set<std::vector<Mask>> frames(const Graph& graph, int degree, int side, int cap, int zeros) {
    std::vector<Mask> masks;
    for (Mask mask = 1; mask <= full(graph); ++mask)
        if (size(mask) == degree - side && independent(graph, mask)) masks.push_back(mask);
    std::set<std::vector<Mask>> result;
    std::vector<Mask> picked;
    std::function<void(std::size_t, Mask)> enumerate = [&](std::size_t start, Mask used) {
        if (int(picked.size()) == side) {
            if (legal_frame(graph, picked, degree, cap, zeros)) result.insert(picked);
            return;
        }
        const int target = graph.size() - zeros;
        const int max_extra = (side - int(picked.size()) - 1) * (degree - side);
        for (std::size_t index = start; index < masks.size(); ++index) {
            const Mask mark = masks[index];
            const int covered = size(used | mark);
            if (covered > target || covered + max_extra < target) continue;
            if (std::any_of(picked.begin(), picked.end(), [&](Mask prev) { return size(prev & mark) > cap - side; }))
                continue;
            picked.push_back(mark);
            enumerate(index + 1, used | mark);
            picked.pop_back();
        }
    };
    enumerate(0, 0);
    return result;
}

Frame bind(int host, const Graph& graph, const std::vector<Mask>& marks) {
    Frame result{host, marks, {}, {}, false, 0};
    std::vector<int> multiplicity(graph.size());
    for (Mask mark : marks)
        for (int site : sites(mark)) ++multiplicity[site];
    int next = 0;
    for (int site = 0; site < int(graph.size()); ++site) {
        if (!multiplicity[site]) result.zero.at(next++) = site;
        else result.private_degree_sum += size(graph[site]);
        assert(multiplicity[site] <= 3);
        result.triple |= multiplicity[site] == 3;
    }
    assert(next == 2);
    for (Mask mark : marks) {
        std::vector<int> group;
        for (int site : sites(mark)) if (multiplicity[site] == 1) group.push_back(site);
        if (group.size() == 3) result.groups.push_back({group[0], group[1], group[2]});
    }
    assert(result.groups.size() == (result.triple ? 3u : 2u));
    return result;
}

struct Host {
    Graph graph;
    std::vector<Pack> atlas;
};

struct Signature {
    int degree;
    bool first, second;
    auto key() const { return std::tie(degree, first, second); }
    bool operator<(const Signature& other) const { return key() < other.key(); }
    bool operator==(const Signature& other) const { return key() == other.key(); }
};

Signature signature(Mask row, std::array<int, 2> zero) {
    return {size(row), has(row, zero[0]), has(row, zero[1])};
}

using Key = std::array<Signature, 3>;
using Index = std::map<Key, std::vector<Pack>>;
using Domains = std::vector<std::vector<Pack>>;

struct Window {
    const Host& host;
    const Frame& frame;
    std::array<int, 2> zero;
};

bool header(const Window& left, const Window& right) {
    const auto& left_graph = left.host.graph;
    const auto& right_graph = right.host.graph;
    if (left.frame.private_degree_sum != right.frame.private_degree_sum) return false;
    const bool shared_edge = has(left_graph[left.zero[0]], left.zero[1]);
    if (shared_edge != has(right_graph[right.zero[0]], right.zero[1])) return false;
    for (int site = 0; site < 2; ++site) {
        if (size(left_graph[left.zero[site]]) + size(right_graph[right.zero[site]]) - shared_edge != 9) return false;
    }
    return size(left_graph[left.zero[0]] & left_graph[left.zero[1]]) +
           size(right_graph[right.zero[0]] & right_graph[right.zero[1]]) <= 5;
}

Index make_index(const Host& host, std::array<int, 2> zero) {
    Index result;
    for (Pack pack : host.atlas) {
        do {
            Key key;
            for (int slot = 0; slot < 3; ++slot) key[slot] = signature(pack[slot], zero);
            result[key].push_back(pack);
        } while (std::next_permutation(pack.begin(), pack.end()));
    }
    return result;
}

bool local(const Window& source, const Window& target, const Triple& group, const Pack& pack) {
    const auto& old = source.host.graph;
    const auto& dest = target.host.graph;
    const Mask old_zero = bit(source.zero[0]) | bit(source.zero[1]);
    for (int slot = 0; slot < 3; ++slot) {
        const Mask neighbors = old[group[slot]];
        for (int site = 0; site < 2; ++site) {
            const Mask common = neighbors & old[source.zero[site]] & ~old_zero;
            if (size(common) + size(pack[slot] & dest[target.zero[site]]) > 5) return false;
        }
        for (Mask mark : target.frame.marks) {
            if (1 + size(pack[slot] & mark) > 5) return false;
        }
        for (int prev = 0; prev < slot; ++prev) {
            const Mask common = neighbors & old[group[prev]] & ~old_zero;
            if (1 + size(common) + size(pack[slot] & pack[prev]) > 5) return false;
        }
    }
    return true;
}

std::vector<const std::vector<Pack>*> signatures(const Window& source, const Index& index) {
    std::vector<const std::vector<Pack>*> result;
    for (const Triple& group : source.frame.groups) {
        Key key;
        for (int slot = 0; slot < 3; ++slot) {
            const auto own = signature(source.host.graph[group[slot]], source.zero);
            key[slot] = {8 - own.degree + own.first + own.second, own.first, own.second};
        }
        const auto found = index.find(key);
        if (found == index.end()) return {};
        result.push_back(&found->second);
    }
    return result;
}

Domains domains(const Window& source, const Window& target,
                const std::vector<const std::vector<Pack>*>& candidates) {
    Domains result;
    for (std::size_t group = 0; group < candidates.size(); ++group) {
        result.emplace_back();
        for (const Pack& pack : *candidates[group]) {
            if (local(source, target, source.frame.groups[group], pack)) result.back().push_back(pack);
        }
        if (result.back().empty()) return {};
    }
    return result;
}

bool reciprocal(const Frame& left, const Frame& right, Domains& rows, Domains& columns) {
    bool changed;
    do {
        changed = false;
        for (std::size_t row = 0; row < rows.size(); ++row) {
            for (std::size_t col = 0; col < columns.size(); ++col) {
                std::map<Panel, std::vector<Pack>> forward, reverse;
                for (const Pack& pack : rows[row]) forward[rectangle(pack, right.groups[col])].push_back(pack);
                for (const Pack& pack : columns[col]) reverse[transpose(rectangle(pack, left.groups[row]))].push_back(pack);
                if (!restrict_rectangle(forward, reverse)) return false;
                const auto old_rows = rows[row].size(), old_cols = columns[col].size();
                rows[row].clear();
                columns[col].clear();
                for (const auto& item : forward) rows[row].insert(rows[row].end(), item.second.begin(), item.second.end());
                for (const auto& item : reverse) columns[col].insert(columns[col].end(), item.second.begin(), item.second.end());
                changed |= old_rows != rows[row].size() || old_cols != columns[col].size();
            }
        }
    } while (changed);
    return true;
}

void controls(const std::string& root) {
    int small_atlas = 0, host = 0;
    for (const auto& graph : catalogue(root + "/r3_4_8.g6")) {
        const auto rows = atlas(graph, 4, 2);
        for (const auto& row : rows) std::cout << host << ' ' << row[0] << ' ' << row[1] << '\n';
        ++host;
        small_atlas += rows.size();
    }
    assert(host == 3 && small_atlas == 366);
    const auto repeat = atlas(Graph(3, 0), 4, 3);
    const std::vector<Mask> repeated_pack{7, 7, 7};
    assert(std::find(repeat.begin(), repeat.end(), repeated_pack) != repeat.end());
    Host repeated_host{Graph(3, 0), {{7, 7, 7}}};
    const auto repeat_index = make_index(repeated_host, {0, 1});
    const auto trait = signature(7, {0, 1});
    assert(repeat_index.at({trait, trait, trait}) == std::vector<Pack>({{7, 7, 7}}));
    int small_frames = 0;
    for (const auto& graph : catalogue(root + "/r3_5_10.g6")) small_frames += frames(graph, 6, 2, 4, 2).size();
    assert(small_frames == 3194);
    std::cerr << "small atlas=366 frames=3194 repeated-nonempty-pack=PASS\n";

    int regular = 0, oriented = 0, lifts = 0, panels = 0, mutants = 0;
    for (const auto& graph : catalogue(root + "/r3_7_22.g6")) {
        if (std::any_of(graph.begin(), graph.end(), [](Mask row) { return size(row) != 6; })) continue;
        ++regular;
        assert(!has_independent(graph, full(graph), 7));
        int cap = 0;
        for (int site = 0; site < 22; ++site) {
            assert(independent(graph, graph[site]));
            for (int prev = 0; prev < site; ++prev) cap = std::max(cap, size(graph[site] & graph[prev]));
        }
        const int start = oriented;
        for (int one = 0; one < 22; ++one) for (int two = one + 1; two < 22; ++two) {
            const auto opposite = sites(graph[one] & graph[two]);
            for (std::size_t first = 0; first < opposite.size(); ++first) for (std::size_t second = first + 1; second < opposite.size(); ++second) {
                const std::array<std::vector<int>, 2> anchors{{{one, two}, {opposite[first], opposite[second]}}};
                const std::array<Mask, 2> windows{antineighborhood(graph, anchors[0]), antineighborhood(graph, anchors[1])};
                const Mask shared = windows[0] & windows[1];
                std::array<std::vector<std::pair<Triple, Pack>>, 2> group_packs;
                for (int side = 0; side < 2; ++side) {
                    const Mask own = windows[1 - side], dest = windows[side];
                    for (int picked = 0; picked < 2; ++picked) {
                        const int root_site = anchors[side][picked], other = anchors[side][1 - picked];
                        const Mask group = graph[root_site] & own & ~graph[other];
                        const Mask lift = antineighborhood(graph, {other});
                        assert(lift == (dest | group | bit(root_site)));
                        assert((graph[root_site] & lift) == group && (lift & ~(graph[root_site] | bit(root_site))) == dest);
                        assert(independent(graph, group) && !has_independent(graph, lift, 6));
                        for (Mask subset = group;; subset = (subset - 1) & group) {
                            Mask homes = dest;
                            for (int site : sites(subset)) homes &= ~graph[site];
                            assert(!has_independent(graph, homes, 6 - size(subset)));
                            if (!subset) break;
                        }
                        ++lifts;
                        if (size(group) != 3) continue;
                        const auto coords = sites(group);
                        const Triple physical{coords[0], coords[1], coords[2]};
                        Pack pack{};
                        for (int slot = 0; slot < 3; ++slot) {
                            const Mask known = graph[coords[slot]] & own;
                            pack[slot] = graph[coords[slot]] & dest;
                            assert((pack[slot] & shared) == (known & shared));
                            assert(size(pack[slot]) == 5 - size(known & ~shared));
                            for (int site : sites(shared)) {
                                assert(size((known & ~shared) & graph[site]) + size(pack[slot] & graph[site]) <= cap);
                            }
                            for (int anchor : anchors[1 - side]) assert(1 + size(pack[slot] & graph[anchor]) <= cap);
                            for (int prev = 0; prev < slot; ++prev) {
                                assert(1 + size(known & graph[coords[prev]] & ~shared) + size(pack[slot] & pack[prev]) <= cap);
                            }
                        }
                        group_packs[side].emplace_back(physical, pack);
                    }
                }
                for (const auto& left : group_packs[0]) for (const auto& right : group_packs[1]) {
                    const auto forward = rectangle(left.second, right.first);
                    const auto reverse = rectangle(right.second, left.first);
                    std::map<Panel, std::vector<Pack>> row{{forward, {left.second}}}, col{{transpose(reverse), {right.second}}};
                    assert(restrict_rectangle(row, col));
                    ++panels;
                    for (int row_id = 0; row_id < 3; ++row_id) for (int col_id = 0; col_id < 3; ++col_id) {
                        Pack altered = right.second;
                        altered[col_id] ^= bit(left.first[row_id]);
                        std::map<Panel, std::vector<Pack>> fixed{{forward, {left.second}}};
                        std::map<Panel, std::vector<Pack>> corrupt{{transpose(rectangle(altered, left.first)), {altered}}};
                        assert(!restrict_rectangle(fixed, corrupt));
                        ++mutants;
                    }
                }
                ++oriented;
            }
        }
        assert(oriented > start);
        std::cerr << "regular control " << regular << " oriented=" << oriented - start << '\n';
    }
    assert(regular == 10 && oriented == 2118 && lifts == 8472 && panels == 3448 && mutants == 31032);
    std::cerr << "regular=" << regular << " oriented=" << oriented << " all four lifts=" << lifts
              << " panels=" << panels << " one-entry mutants rejected=" << mutants << '\n';
}

#include "panel17_record.hpp"

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    if (argc < 3) return 2;
    const std::string mode = argv[1], root = argv[2];
    if (mode == "controls" && argc == 3) {
        controls(root);
        return 0;
    }
    const bool shard = mode == "shard" && argc == 7;
    if (!shard && (mode != "slice" || (argc != 5 && argc != 6))) return 2;
    std::vector<Host> hosts;
    std::vector<std::set<std::vector<Mask>>> inventory;
    std::ofstream atlas_out(argv[4]);
    assert(atlas_out);
    for (const auto& graph : catalogue(root + "/r3_6_17.g6")) {
        assert(graph.size() == 17);
        assert(!has_independent(graph, full(graph), 6));
        for (Mask neighbors : graph) assert(independent(graph, neighbors));
        Host host{graph, {}};
        for (const auto& entry : atlas(graph, 6, 3)) {
            host.atlas.push_back({entry[0], entry[1], entry[2]});
            atlas_out << hosts.size() << ' ' << entry[0] << ' ' << entry[1] << ' ' << entry[2] << '\n';
        }
        inventory.push_back(frames(graph, 9, 4, 5, 2));
        std::cerr << "host=" << hosts.size() << " atlas=" << host.atlas.size() << " frames=" << inventory.back().size() << '\n';
        hosts.push_back(std::move(host));
    }
    assert(hosts.size() == 7);
    atlas_out.close();
    std::ifstream input(argv[3]);
    assert(input);
    std::vector<Frame> roster;
    int host_id;
    std::vector<Mask> marks(4);
    while (input >> host_id >> marks[0] >> marks[1] >> marks[2] >> marks[3]) {
        auto sorted = marks;
        std::sort(sorted.begin(), sorted.end());
        assert(inventory.at(host_id).erase(sorted) == 1);
        roster.push_back(bind(host_id, hosts.at(host_id).graph, marks));
    }
    assert(input.eof() && roster.size() == 55055);
    for (const auto& remaining : inventory) assert(remaining.empty());
    std::map<std::tuple<int, int, int>, Index> indices;
    auto index = [&](const Window& window) -> const Index& {
        const auto key = std::make_tuple(window.frame.host, window.zero[0], window.zero[1]);
        auto known = indices.find(key);
        if (known == indices.end()) known = indices.emplace(key, make_index(window.host, window.zero)).first;
        return known->second;
    };
    std::array<std::array<std::uint64_t, 6>, 2> counts{};
    int triple_count = 0;
    auto inspect = [&](int first, int second, int flip) {
        const Frame& left_frame = roster.at(first);
        const Frame& right_frame = roster.at(second);
        const Window left{hosts[left_frame.host], left_frame, left_frame.zero};
        Window right{hosts[right_frame.host], right_frame, right_frame.zero};
        if (flip) std::swap(right.zero[0], right.zero[1]);
        auto& stages = counts.at(flip);
        ++stages[0];
        if (!header(left, right)) return;
        ++stages[1];
        int depth = 1;
        const auto row_signatures = signatures(left, index(right));
        if (!row_signatures.empty()) {
            ++depth;
            ++stages[2];
            const auto col_signatures = signatures(right, index(left));
            if (!col_signatures.empty()) {
                ++depth;
                ++stages[3];
                auto rows = domains(left, right, row_signatures);
                auto columns = domains(right, left, col_signatures);
                if (!rows.empty() && !columns.empty()) {
                    ++depth;
                    ++stages[4];
                    if (reciprocal(left_frame, right_frame, rows, columns)) {
                        ++depth;
                        ++stages[5];
                    }
                }
            }
        }
        if (shard) panel17_record(first, second, flip, depth);
        else std::cout << first << ' ' << second << ' ' << flip << ' ' << depth << '\n';
    };
    if (shard) {
        const int start = std::stoi(argv[5]), stop = std::stoi(argv[6]);
        if (start < 0 || start >= stop || stop > int(roster.size())) return 2;
        for (int first = start; first < stop; ++first)
            for (int second = 0; second < int(roster.size()); ++second)
                for (int flip : {0, 1}) inspect(first, second, flip);
    } else if (argc == 6) {
        std::ifstream probe(argv[5]);
        assert(probe);
        int first, second, flip;
        while (probe >> first >> second >> flip) inspect(first, second, flip);
        assert(probe.eof());
    } else {
        for (int first = 0; first < int(roster.size()); ++first) {
            if (!roster[first].triple) continue;
            ++triple_count;
            for (int second = 0; second < int(roster.size()); ++second) {
                for (int flip : {0, 1}) inspect(first, second, flip);
            }
        }
        assert(triple_count == 200);
    }
    for (int flip : {0, 1}) {
        std::cerr << "flip=" << flip << " raw/header/fwd/rev/local/panel:";
        for (auto count : counts[flip]) std::cerr << ' ' << count;
        std::cerr << '\n';
    }
    if (!std::cout.flush()) throw std::runtime_error("stage stream write failed");
}
