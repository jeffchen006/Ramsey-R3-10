#include <array>
#include <ctime>
#include <map>
#include <sstream>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main wing_windows_main
#include "p2_wing_windows.cpp"
#undef main
#pragma GCC diagnostic pop

using Wide = std::uint64_t;
using Profile = std::array<int, 6>;
using Profiles = std::map<int, std::vector<Profile>>;

static std::string encode(const Graph& graph) {
    std::string text(1 + (graph.size() * (graph.size() - 1) / 2 + 5) / 6, '?');
    text[0] += graph.size();
    int bit = 0;
    for (std::size_t high = 1; high < graph.size(); ++high)
        for (std::size_t low = 0; low < high; ++low, ++bit)
            if (graph[high] & (Mask(1) << low)) text[1 + bit / 6] += 1 << (5 - bit % 6);
    return text;
}

static bool size_then_mask(Mask first, Mask second) {
    if (std::popcount(first) != std::popcount(second)) return std::popcount(first) < std::popcount(second);
    return first < second;
}

struct Search {
    const Graph& core;
    int side, lower, upper;
    Mask universe;
    std::vector<unsigned char> alpha;
    std::vector<Mask> cand, wing_rows;
    std::array<Mask, 6> chosen{}, expected{};
    std::array<Mask, 64> unions{};
    std::array<Mask, 4> saturation{};
    std::vector<Wide> compatible;
    std::array<std::array<Wide, 6>, 6> allowed_profile{};
    unsigned words = 0;
    bool use_profiles = false;
    Wide nodes = 0, leaves = 0, output = 0;
    bool check_control = false, seen_control = false;

    Search(const Graph& graph, int side_size)
        : core(graph), side(side_size), lower(2 * int(core.size()) - 6), upper(lower + 2),
          universe(all(core)), alpha(universe + 1) {}

    void finish(Mask once) {
        ++leaves;
        if (std::ranges::any_of(chosen, [&](Mask column) { return std::popcount(column & once) > 1; })) return;
        const int core_size = core.size(), root = core_size + chosen.size();
        Graph graph = core;
        graph.resize(root + 1);
        const Mask common = ((Mask(1) << root) - 1) & ~universe;
        graph[root] = common;
        for (int index = 0; index < int(chosen.size()); ++index) {
            const int column = core_size + index;
            graph[column] = chosen[index] | (Mask(1) << root);
            for (Mask rest = chosen[index]; rest; rest &= rest - 1)
                graph[std::countr_zero(rest)] |= Mask(1) << column;
        }
        if (!compatible_columns(graph, common, universe)) return;
        WingRules rules = wing_rules(graph, common, universe, 6, 2);
        for (std::size_t first = 0; first < wing_rows.size(); ++first) {
            for (std::size_t second = first + 1; second < wing_rows.size(); ++second) {
                if (std::popcount(wing_rows[first] & wing_rows[second]) > 1) continue;
                Mask used = wing_rows[first] | wing_rows[second];
                for (std::size_t third = second + 1; third < wing_rows.size(); ++third) {
                    Mask last = wing_rows[third];
                    if (std::popcount(wing_rows[first] & last) > 1 || std::popcount(wing_rows[second] & last) > 1 ||
                        std::popcount(used | last) != side ||
                        !admissible(graph, wing_rows[first], wing_rows[second], last, 9, &rules)) continue;
                    ++output;
                    if (!check_control) std::cout << encode(graph) << '\n';
                    else seen_control |= expected == chosen;
                    return;
                }
            }
        }
    }

    void dfs(int depth, const Wide* entries, int used_degree, int excess, Mask ones, Mask twos, Mask threes,
             Mask fours, Wide profiles) {
        ++nodes;
        if (depth == 6) {
            assert(lower <= used_degree && used_degree <= upper && unions[63] == universe);
            finish(ones ^ twos);
            return;
        }
        const int slots = 6 - depth;
        if (used_degree + 5 * slots < lower) return;
        Mask once = ones ^ twos;
        int missing = std::popcount(universe ^ ones) + std::popcount(once);
        for (int index = 0; index < depth; ++index) missing -= bool(chosen[index] & once);
        if (used_degree + missing > upper) return;
        Mask saturated = (ones & saturation[0]) | (twos & saturation[1]) |
                         (threes & saturation[2]) | (fours & saturation[3]);
        std::array<Wide, 40> next_entries;
        assert(words <= next_entries.size());
        for (unsigned word = 0; word < words; ++word) {
          for (Wide rest = entries[word]; rest; rest &= rest - 1) {
            unsigned next = 64 * word + std::countr_zero(rest);
            Mask column = cand[next];
            int size = std::popcount(column);
            if (used_degree + size * slots > upper) return;
            if (slots == 1 && used_degree + size < lower) continue;
            Wide profiles_next = use_profiles ? profiles & allowed_profile[depth][size] : profiles;
            if (use_profiles && !profiles_next) continue;
            int new_excess = excess + std::popcount(column & twos);
            if (new_excess > 2 || (column & saturated)) continue;
            bool alpha_ok = true;
            const int existing = 1 << depth;
            for (int subset = existing - 1; subset; --subset) {
                Mask united = column | unions[subset];
                if (!std::has_single_bit(static_cast<unsigned>(subset)) &&
                    alpha[universe ^ united] >= 6 - std::popcount(static_cast<unsigned>(subset))) {
                    alpha_ok = false;
                    break;
                }
                unions[existing | subset] = united;
            }
            if (!alpha_ok) continue;
            chosen[depth] = column;
            unions[existing] = column;
            const Wide* restrict_to = compatible.data() + std::size_t(next) * words;
            for (unsigned group = 0; group < words; ++group) next_entries[group] = entries[group] & restrict_to[group];
            dfs(depth + 1, next_entries.data(), used_degree + size, new_excess, ones | column,
                twos | (ones & column), threes | (twos & column), fours | (threes & column), profiles_next);
          }
        }
    }

    void run(const Profiles* profiles = nullptr) {
        int total = 0;
        for (Mask row : core) {
            int degree = std::popcount(row);
            if (degree >= 6) return;
            total += degree;
        }
        if (profiles) {
            auto found = profiles->find(total / 2);
            if (found == profiles->end()) return;
            use_profiles = true;
            assert(found->second.size() <= 64);
            for (std::size_t index = 0; index < found->second.size(); ++index)
                for (int depth = 0; depth < 6; ++depth)
                    allowed_profile[depth][found->second[index][depth]] |= Wide(1) << index;
        }
        independent_sets(core, universe, 5, 0, wing_rows);
        if (wing_rows.size() < 3) return;
        bool feasible = false;
        for (std::size_t first = 0; first < wing_rows.size() && !feasible; ++first)
            for (std::size_t second = first + 1; second < wing_rows.size() && !feasible; ++second) {
                if (std::popcount(wing_rows[first] & wing_rows[second]) > 1) continue;
                for (std::size_t third = second + 1; third < wing_rows.size() && !feasible; ++third)
                    feasible = std::popcount(wing_rows[first] & wing_rows[third]) <= 1 &&
                               std::popcount(wing_rows[second] & wing_rows[third]) <= 1 &&
                               std::popcount(wing_rows[first] | wing_rows[second] | wing_rows[third]) == side;
            }
        if (!feasible) return;
        for (Mask subset = 1; subset <= universe; ++subset) {
            int vertex = std::countr_zero(subset);
            Mask reduced = subset & (subset - 1);
            alpha[subset] = std::max<int>(alpha[reduced], 1 + alpha[reduced & ~core[vertex]]);
        }
        assert(alpha[universe] <= 5);
        for (int size = 2; size <= 5; ++size) independent_sets(core, universe, size, 0, cand);
        std::sort(cand.begin(), cand.end(), size_then_mask);
        words = (cand.size() + 63) / 64;
        compatible.resize(cand.size() * words);
        std::vector<Wide> initial(words);
        for (unsigned first = 0; first < cand.size(); ++first) {
            initial[first / 64] |= Wide(1) << (first % 64);
            for (unsigned second = first; second < cand.size(); ++second)
                if (std::popcount(cand[first] & cand[second]) <= 4 &&
                    alpha[universe ^ (cand[first] | cand[second])] < 5)
                    compatible[std::size_t(first) * words + second / 64] |= Wide(1) << (second % 64);
        }
        for (int vertex = 0; vertex < int(core.size()); ++vertex) {
            int capacity = 6 - std::popcount(core[vertex]);
            if (capacity <= 4) saturation[capacity - 1] |= Mask(1) << vertex;
        }
        dfs(0, initial.data(), 0, 0, 0, 0, 0, 0, ~Wide(0));
    }
};

static Mask project_row(Mask row, Mask keep) {
    Mask result = 0;
    for (Mask rest = keep; rest; rest &= rest - 1)
        if (row & (rest & -rest)) result |= Mask(1) << (std::popcount(keep) - std::popcount(rest));
    return result;
}

static void control_extensions(std::ifstream& input, int count) {
    int passed = 0;
    Wide nodes = 0;
    for (std::string line; passed < count && std::getline(input, line);) {
        std::istringstream stream(line);
        unsigned source;
        int root;
        std::string text;
        assert(stream >> source >> root >> text);
        Graph graph = decode(text), core;
        Mask common = graph[root], kept = all(graph) & ~(common | (Mask(1) << root));
        for (Mask rest = kept; rest; rest &= rest - 1) core.push_back(project_row(graph[std::countr_zero(rest)], kept));
        if (std::popcount(kept) != 14) continue;
        std::array<Mask, 6> expected{};
        int column_index = 0;
        for (Mask rest = common; rest; rest &= rest - 1)
            expected[column_index++] = project_row(graph[std::countr_zero(rest)], kept);
        if (std::ranges::any_of(expected, [&](Mask column) { return std::popcount(column) < 2; })) continue;
        std::sort(expected.begin(), expected.end(), size_then_mask);
        bool found = false;
        for (int side = 12; side <= 14 && !found; ++side) {
            Search search(core, side);
            search.check_control = true;
            search.expected = expected;
            search.run();
            nodes += search.nodes;
            found = search.seen_control;
        }
        assert(found);
        ++passed;
    }
    assert(passed == count);
    std::cerr << "PASS H21 planted extensions=" << passed << " nodes=" << nodes << '\n';
}

int main(int argc, char** argv) {
    assert(argc >= 4 && argc <= 6);
    std::string mode = argv[1];
    std::ifstream input(argv[2]);
    assert(input);
    const int side = std::stoi(argv[3]);
    if (mode == "control") {
        control_extensions(input, side);
    } else {
        assert(mode == "glue" && (argc == 5 || argc == 6));
        const int stride = std::stoi(argv[4]);
        assert(stride > 0 && side >= 12 && side <= 14);
        Profiles profiles;
        if (argc == 6) {
            std::ifstream profile_file(argv[5]);
            assert(profile_file);
            for (std::string line; std::getline(profile_file, line);) {
                std::istringstream fields(line);
                int edges;
                Profile profile;
                assert(fields >> edges);
                for (int& size : profile) {
                    assert(fields >> size);
                    assert(size >= 2 && size <= 5);
                }
                profiles[edges].push_back(profile);
            }
            assert(!profiles.empty());
        }
        Wide inputs = 0, picked = 0, nodes = 0, leaves = 0, output = 0;
        for (std::string text; std::getline(input, text); ++inputs) {
            if (inputs % stride) continue;
            Graph core = decode(text);
            assert(core.size() >= 12 && core.size() <= 14 && int(core.size()) >= side);
            Search search(core, side);
            search.run(argc == 6 ? &profiles : nullptr);
            ++picked;
            nodes += search.nodes;
            leaves += search.leaves;
            output += search.output;
        }
        assert(std::cout);
        std::cerr << "side=" << side << " inputs=" << inputs << " stride=" << stride << " picked=" << picked
                  << " nodes=" << nodes << " leaves=" << leaves << " out=" << output
                  << " cpu=" << double(std::clock()) / CLOCKS_PER_SEC << '\n';
    }
    return 0;
}
