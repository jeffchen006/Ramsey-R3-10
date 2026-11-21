#include <limits>
#include <numeric>
#include <optional>

#include "p2_window_join_r7.inc"

static Wide wide_mask(const std::vector<int>& labels) {
    Wide result = 0;
    for (int label : labels) result |= Wide(1) << label;
    return result;
}

struct ArcWork {
    Wide checks = 0, cap = std::numeric_limits<Wide>::max();
};

struct Request {
    int vertex;
    Wide blocked;
    std::vector<Wide> domain;
};

enum class Outcome : int { base, single, arc, pass, defer };

#include "p2_request_cache.hpp"

static void extensions(const std::vector<Wide>& fixed, Wide rest, int deficit, Wide chosen,
                       Wide base, int need, std::vector<Wide>& domain) {
    if (deficit == 0) {
        if (avoid_ten(fixed, base & ~chosen, need)) domain.push_back(chosen);
        return;
    }
    while (std::popcount(rest) >= deficit) {
        const int next = std::countr_zero(rest);
        const Wide bit = Wide(1) << next;
        rest ^= bit;
        extensions(fixed, rest & ~fixed[next], deficit - 1, chosen | bit, base, need, domain);
    }
}

static bool pair_legal(const std::vector<Wide>& fixed, Wide base, int goal, const Request& first,
                       const Request& second, Wide first_choice, Wide second_choice) {
    if (fixed[first.vertex] & (Wide(1) << second.vertex))
        return !((first.blocked | first_choice) & (second.blocked | second_choice));
    return avoid_ten(fixed, base & ~(first.blocked | second.blocked | first_choice | second_choice),
                     goal - 2);
}

static Outcome incidence(const Boundary& boundary, const std::vector<int>& out, int goal, ArcWork& work,
                         const std::vector<Wide>* planted = nullptr, Wide ignored = 0) {
    const Wide base = ((Wide(1) << boundary.fixed.size()) - 1) & ~(wide_mask(out) | ignored);
    if (!avoid_ten(boundary.fixed, base, goal)) return Outcome::base;
    std::vector<Request> requests;
    for (int vertex : out) {
        auto& request = requests.emplace_back(Request{vertex, boundary.fixed[vertex] & base, {}});
        const int deficit = boundary.deficit[vertex];
        const Wide possible = boundary.undecided[vertex] & base;
        assert(possible == boundary.undecided[vertex]);
        if (deficit < 0) return Outcome::single;
        if (!avoid_ten(boundary.fixed, base & ~(request.blocked | possible), goal - 1))
            return Outcome::single;
        extensions(boundary.fixed, possible, deficit, 0, base & ~request.blocked, goal - 1,
                   request.domain);
        if (request.domain.empty()) return Outcome::single;
    }
    auto plant_check = [&]() {
        if (!planted) return;
        for (const auto& request : requests) {
            const Wide actual = (*planted)[request.vertex] & base & ~request.blocked;
            assert(std::find(request.domain.begin(), request.domain.end(), actual) != request.domain.end());
        }
    };
    plant_check();
    bool changed;
    do {
        changed = false;
        std::stable_sort(requests.begin(), requests.end(), [](const Request& first, const Request& second) {
            return first.domain.size() < second.domain.size();
        });
        for (auto& first : requests) {
            for (const auto& second : requests) {
                if (first.vertex == second.vertex) continue;
                const auto old_size = first.domain.size();
                std::size_t survivors = 0;
                for (Wide first_choice : first.domain) {
                    bool found = false;
                    for (Wide second_choice : second.domain) {
                        if (work.checks == work.cap) return Outcome::defer;
                        ++work.checks;
                        if (pair_legal(boundary.fixed, base, goal, first, second, first_choice, second_choice)) {
                            found = true;
                            break;
                        }
                    }
                    if (found) first.domain[survivors++] = first_choice;
                }
                first.domain.resize(survivors);
                if (!survivors) return Outcome::arc;
                changed |= old_size != survivors;
            }
        }
    } while (changed);
    plant_check();
    return Outcome::pass;
}

static Boundary planted_boundary(const std::vector<Wide>& graph, std::vector<int> rows,
                                 std::vector<int> columns) {
    Boundary result{graph, std::vector<Wide>(graph.size()), std::move(rows), std::move(columns),
                    std::vector<int>(graph.size())};
    const auto row_mask = wide_mask(result.rows), column_mask = wide_mask(result.columns);
    for (int row : result.rows) result.fixed[row] &= ~column_mask;
    for (int column : result.columns) result.fixed[column] &= ~row_mask;
    for (int row : result.rows)
        for (int column : result.columns)
            if (!(result.fixed[row] & result.fixed[column])) result.add_possible(row, column);
    for (std::size_t vertex = 0; vertex < graph.size(); ++vertex) {
        result.deficit[vertex] = std::popcount(graph[vertex] & ~result.fixed[vertex]);
        assert(!(graph[vertex] & ~(result.fixed[vertex] | result.undecided[vertex])));
    }
    return result;
}

static void cache_control(const Graph& graph, Mask common, Mask left, Mask right, Mask first_wing,
                          Mask second_wing) {
    const auto shared = vertices(common);
    const auto make = [&](Mask own, Mask wing, Mask opposite) {
        SideData side{{}, {}, {}, {}, 2, 4, 6};
        std::vector<Mask> planted;
        const auto private_labels = vertices(own), wing_labels = vertices(wing);
        const auto other_labels = vertices(opposite);
        auto compress = [&](int vertex, const std::vector<int>& labels) {
            Mask result = 0;
            for (std::size_t bit = 0; bit < labels.size(); ++bit)
                if (graph[vertex] & (Mask(1) << labels[bit])) result |= Mask(1) << bit;
            return result;
        };
        for (int vertex : private_labels) {
            side.edges.push_back(compress(vertex, private_labels));
            side.common.push_back(compress(vertex, shared));
            side.wing.push_back(compress(vertex, wing_labels));
            planted.push_back(compress(vertex, other_labels));
            side.deficits.push_back(std::popcount(planted.back()));
        }
        return std::pair{side, planted};
    };
    auto [lhs, planted_left] = make(left, first_wing, right);
    auto [rhs, planted_right] = make(right, second_wing, left);
    RequestCache left_cache(lhs), right_cache(rhs);
    const std::array<Mask, 6> identity{1, 2, 4, 8, 0, 0};
    assert(left_cache.check(rhs, identity, true, &planted_right) == Outcome::pass);
    assert(right_cache.check(lhs, identity, true, &planted_left) == Outcome::pass);
    rhs.deficits.front() = int(lhs.edges.size());
    assert(left_cache.check(rhs, identity, true) == Outcome::single);
}

static void controls(std::ifstream& input) {
    unsigned tests = 0, graph_count = 0, stripped_ten = 0, exact_cache = 0;
    for (std::string text; std::getline(input, text);) {
        const Graph graph = decode(text);
        assert(graph.size() == 22);
        ++graph_count;
        const std::vector<Wide> wide_graph(graph.begin(), graph.end());
        assert(avoid_ten(wide_graph, all(graph), 7));
        for (int first = 0; first < 22; ++first) {
            for (int second = first + 1; second < 22; ++second) {
                const Mask common = graph[first] & graph[second];
                if (std::popcount(common) != 4) continue;
                const Mask first_wing = graph[first] & ~common, second_wing = graph[second] & ~common;
                const Mask core = all(graph) & ~(common | first_wing | second_wing | (Mask(1) << first)
                                                 | (Mask(1) << second));
                auto wing_core = [&](Mask wing) {
                    Mask used = 0;
                    for (int vertex : vertices(wing)) used |= graph[vertex] & core;
                    return used;
                };
                const auto wing_vertices = vertices(first_wing);
                if (!std::all_of(wing_vertices.begin(), wing_vertices.end(),
                                 [&](int vertex) { return (graph[vertex] & second_wing) == second_wing; }))
                    continue;
                const Mask left = wing_core(first_wing), right = wing_core(second_wing);
                assert(!(left & right));
                Boundary boundary = planted_boundary(wide_graph, vertices(left), vertices(right));
                ArcWork full;
                for (const auto* side : {&boundary.rows, &boundary.columns})
                    assert(incidence(boundary, *side, 7, full, &wide_graph) == Outcome::pass);
                if ((left | right) == core) {
                    cache_control(graph, common, left, right, first_wing, second_wing);
                    ++exact_cache;
                }
                stripped_ten += !avoid_ten(boundary.fixed, all(graph), 7);
                ++tests;
            }
        }
    }
    assert(graph_count == 10 && tests == 7 && exact_cache == 7);
    Boundary control{std::vector<Wide>(5), std::vector<Wide>(5), {0, 1, 2}, {3, 4}, {2, 0, 0, 1, 1}};
    control.add_possible(0, 3);
    control.add_possible(0, 4);
    assert(flow(control));
    ArcWork exact;
    assert(incidence(control, control.columns, 4, exact) == Outcome::arc);
    ArcWork limited{0, 0};
    assert(incidence(control, control.columns, 4, limited) == Outcome::defer);
    control.add_possible(1, 4);
    assert(incidence(control, control.columns, 4, exact) == Outcome::pass);
    control.remove(0, 3);
    assert(incidence(control, control.columns, 4, exact) == Outcome::single);
    std::cout << "PASS reg6 graphs=" << graph_count << " planted full-wing pairs=" << tests
              << " alpha>=7 after cross deletion=" << stripped_ten
              << " cached controls in both orientations=" << exact_cache
              << " ; simultaneous-only, singleton, and capped toy controls passed\n";
}

using Profile = std::pair<int, Key>;

struct ProfileCount {
    Wide marks = 0, packs = 0;
};

static std::array<int, 7> profile_fields(Profile key) {
    auto [edges, signature] = key;
    std::array<int, 7> fields{};
    for (int index = 1; index <= 6; ++index) {
        fields[index] = 8 - (signature & 63);
        edges -= fields[index] + 1;
        signature >>= 6;
    }
    assert(!signature && std::is_sorted(fields.begin() + 1, fields.end()));
    fields.front() = edges;
    return fields;
}

static Profile read_profile(std::string input) {
    std::replace(input.begin(), input.end(), ',', ' ');
    std::istringstream stream(input);
    int edges;
    std::array<int, 6> support{};
    assert(stream >> edges);
    for (int& count : support) {
        assert(stream >> count);
        assert(2 <= count && count <= 5);
        edges += count + 1;
    }
    assert(std::is_sorted(support.begin(), support.end()));
    Key signature = 0;
    for (auto it = support.rbegin(); it != support.rend(); ++it) signature = (signature << 6) | (8 - *it);
    return {edges, signature};
}

static Wide map_multiplier(Profile key) {
    const auto fields = profile_fields(key);
    Wide multiplier = 1;
    for (int index = 2, run = 1; index <= 6; ++index) {
        run = fields[index] == fields[index - 1] ? run + 1 : 1;
        multiplier *= run;
    }
    return multiplier;
}

static int edge_count(const Mark& mark) {
    int result = 0;
    for (Mask row : mark.graph) result += std::popcount(row);
    assert(result % 2 == 0);
    return result / 2;
}

static Outcome no_columns(Boundary boundary, const Rules& spec, ArcWork& work) {
    const Wide ignored = ((Wide(1) << spec.cap) - 1) << 2;
    for (int first : boundary.rows)
        for (int second : boundary.columns)
            if (!(boundary.fixed[first] & boundary.fixed[second] & ~ignored))
                boundary.add_possible(first, second);
    auto outcome = incidence(boundary, boundary.columns, spec.degree + 1, work, nullptr, ignored);
    if (outcome == Outcome::pass)
        outcome = incidence(boundary, boundary.rows, spec.degree + 1, work, nullptr, ignored);
    return outcome;
}

static std::pair<std::array<Mask, 6>, std::array<Mask, 6>> placements(const Mark& right,
                                                                      const std::vector<int>& assignment) {
    std::array<Mask, 6> forward{}, reverse{};
    for (std::size_t index = 0; index < assignment.size(); ++index) {
        auto where = std::find(right.columns.begin(), right.columns.end(), assignment[index]);
        assert(where != right.columns.end());
        const auto position = where - right.columns.begin();
        forward[position] = Mask(1) << index;
        reverse[index] = Mask(1) << position;
    }
    return {forward, reverse};
}

struct Stages {
    Wide graph_pairs = 0, raw_maps = 0, column_maps = 0, packs = 0;
    Wide baseline_reject = 0;
    std::array<Wide, 5> outcomes{};
    Wide work = 0, old_pass = 0, old_pass_incidence_reject = 0;
    Wide no_columns_cases = 0, no_columns_cut = 0, no_columns_defer = 0, no_columns_mapped_cut = 0;
    std::array<Wide, 5> cached{};
    Wide domains_built = 0, pairs_built = 0, supports_built = 0, cached_right_cuts = 0;
};

static Wide profile_table(const std::map<Profile, ProfileCount>& left, const std::map<Profile, ProfileCount>& right,
                          std::ostream* file) {
    Wide total_maps = 0;
    if (file) *file << "core_edges\tc1\tc2\tc3\tc4\tc5\tc6\th19_marks\th19_packs\th21_marks\th21_packs\tC_maps\traw_maps\n";
    for (const auto& [key, count] : left) {
        assert(right.contains(key));
        const auto other = right.at(key);
        const Wide multiplier = map_multiplier(key);
        const Wide maps = count.packs * other.packs * multiplier;
        total_maps += maps;
        if (file) {
            for (int field : profile_fields(key)) *file << field << '\t';
            *file << count.marks << '\t' << count.packs << '\t' << other.marks << '\t' << other.packs << '\t'
                  << multiplier << '\t' << maps << '\n';
        }
    }
    return total_maps;
}

static void pilot(std::ifstream& small, std::ifstream& large, int left_step, int right_step, Wide cap,
                  bool measure_base, bool propagate, Wide map_limit, std::ostream* counts = nullptr,
                  std::optional<Profile> required = std::nullopt, std::ostream* pins = nullptr,
                  bool loose_wings = false) {
    const Rules left_spec{9, 6, 3, 26, 12}, right_spec{9, 6, 3, 26, 14};
    using Bucket = std::map<Profile, std::vector<Mark>>;
    Bucket left, right;
    std::map<Profile, ProfileCount> count_left, count_right;
    Wide left_roots = 0, right_roots = 0, left_packs = 0, right_packs = 0;
    for (std::string text; std::getline(small, text); ++left_roots) {
        if (left_roots % left_step) continue;
        auto graph = decode(text);
        assert(graph.size() == 19);
        std::vector<Mark> marks;
        add_marks(marks, graph, left_roots, 18, left_spec, left_packs);
        assert(marks.size() == 1);
        auto& mark = marks.front();
        assert(mark.shared.empty());
        const Profile key{edge_count(mark), signature(mark, left_spec, true, true)};
        if (required && key != *required) continue;
        ++count_left[key].marks;
        count_left[key].packs += mark.packs.size();
        if (!counts) left[key].push_back(std::move(mark));
    }
    for (std::string line; std::getline(large, line); ++right_roots) {
        if (right_roots % right_step) continue;
        std::size_t source;
        int root;
        std::string text;
        std::istringstream fields(line);
        assert(fields >> source >> root >> text);
        auto graph = decode(text);
        assert(graph.size() == 21);
        std::vector<Mark> marks;
        add_marks(marks, graph, source, root, right_spec, right_packs);
        for (auto& mark : marks) {
            assert(mark.shared.empty());
            int column_sum = 0;
            for (int column : mark.columns) column_sum += degree(mark.graph, column);
            const Profile key{edge_count(mark) - column_sum + 18, signature(mark, right_spec, false, true)};
            if (!count_left.contains(key)) continue;
            ++count_right[key].marks;
            count_right[key].packs += mark.packs.size();
            if (!counts) right[key].push_back(std::move(mark));
        }
    }
    std::erase_if(count_left, [&](const auto& entry) { return !count_right.contains(entry.first); });
    const Wide expected_raw = profile_table(count_left, count_right, counts);
    std::cout << "expected raw maps=" << expected_raw << " left input=" << left_roots << " right input="
              << right_roots << " profiles=" << count_left.size() << '\n' << std::flush;
    if (counts) return;
    if (required) {
        const auto fields = profile_fields(*required);
        std::cout << "required profile";
        for (int field : fields) std::cout << ' ' << field;
        std::cout << '\n';
    }
    if (expected_raw > map_limit) {
        std::cerr << "refusing raw map count " << expected_raw << " above limit " << map_limit << '\n';
        std::exit(3);
    }
    Stages stages;
    for (const auto& [key, lhs] : left) {
        if (!right.contains(key)) continue;
        const auto& right_bucket = right.at(key);
        std::vector<std::vector<SideData>> right_data;
        for (const auto& mark : right_bucket) {
            auto& sides = right_data.emplace_back();
            for (const auto& pack : mark.packs) sides.push_back(side_data(mark, pack, right_spec));
        }
        for (const Mark& first : lhs) {
            std::vector<SideData> first_sides;
            std::vector<RequestCache> small_cache;
            for (const auto& pack : first.packs) {
                first_sides.push_back(side_data(first, pack, left_spec));
                small_cache.emplace_back(first_sides.back());
            }
            for (std::size_t right_index = 0; right_index < right_bucket.size(); ++right_index) {
                const Mark& second = right_bucket[right_index];
                const auto& second_sides = right_data[right_index];
                ++stages.graph_pairs;
                std::vector<std::optional<RequestCache>> large_cache(second.packs.size());
                std::vector<int> assignment;
                const auto pack_product = first.packs.size() * second.packs.size();
                std::vector<Outcome> relaxed;
                const auto count = assign_columns(first, second, left_spec, assignment, 0, [&](const auto& map) {
                    if (!column_test(first, second, map, left_spec)) return;
                    ++stages.column_maps;
                    const auto [forward, reverse] = placements(second, map);
                    if (measure_base && relaxed.empty()) {
                        for (const auto& first_pack : first.packs)
                            for (const auto& second_pack : second.packs) {
                                ArcWork work{0, cap};
                                auto result = no_columns(combine(first, second, map, first_pack, second_pack, left_spec),
                                                         left_spec, work);
                                relaxed.push_back(result);
                                ++stages.no_columns_cases;
                                stages.no_columns_cut += result < Outcome::pass;
                                stages.no_columns_defer += result == Outcome::defer;
                            }
                    }
                    std::size_t pack_index = 0;
                    for (std::size_t outer = 0; outer < first.packs.size(); ++outer) {
                        for (std::size_t inner = 0; inner < second.packs.size(); ++inner) {
                            ++stages.packs;
                            assert(stages.packs <= expected_raw);
                            auto cached = small_cache[outer].check(second_sides[inner], forward, propagate, nullptr, loose_wings);
                            if (cached == Outcome::pass) {
                                if (!large_cache[inner]) large_cache[inner].emplace(second_sides[inner]);
                                cached = large_cache[inner]->check(first_sides[outer], reverse, propagate, nullptr, loose_wings);
                                stages.cached_right_cuts += cached < Outcome::pass;
                            }
                            ++stages.cached[static_cast<int>(cached)];
                            if (cached >= Outcome::pass && pins) {
                                *pins << first.source << '\t' << first.root << '\t' << second.source << '\t'
                                      << second.root << '\t' << static_cast<int>(cached);
                                for (int column : map) *pins << '\t' << column;
                                for (Mask row : first.packs[outer]) *pins << '\t' << row;
                                for (Mask row : second.packs[inner]) *pins << '\t' << row;
                                *pins << '\n';
                            }
                            if (!measure_base) continue;
                            stages.no_columns_mapped_cut += relaxed[pack_index++] < Outcome::pass;
                            Boundary boundary = combine(first, second, map, first.packs[outer], second.packs[inner], left_spec);
                            assert(sum_deficits(boundary, boundary.rows) == sum_deficits(boundary, boundary.columns));
                            Boundary old = boundary;
                            const bool old_pass = cross_filter(old, left_spec, true) == 5;
                            stages.old_pass += old_pass;
                            if (!local_degree(boundary)) {
                                ++stages.baseline_reject;
                                continue;
                            }
                            ArcWork work{0, cap};
                            auto result = incidence(boundary, boundary.columns, 10, work);
                            if (result == Outcome::pass) result = incidence(boundary, boundary.rows, 10, work);
                            assert(cached >= Outcome::pass || result < Outcome::pass || result == Outcome::defer);
                            assert(cached != Outcome::pass || result != Outcome::base);
                            if (propagate && cached != Outcome::defer && result != Outcome::defer)
                                assert((cached == Outcome::pass) == (result == Outcome::pass));
                            stages.work += work.checks;
                            ++stages.outcomes[static_cast<int>(result)];
                            stages.old_pass_incidence_reject += old_pass && result < Outcome::pass;
                        }
                    }
                });
                stages.raw_maps += count * pack_product;
                for (const auto& cache : large_cache) {
                    if (!cache) continue;
                    stages.domains_built += cache->domain_builds;
                    stages.pairs_built += cache->pair_builds;
                    stages.supports_built += cache->support_builds;
                }
            }
            for (const auto& cache : small_cache) {
                stages.domains_built += cache.domain_builds;
                stages.pairs_built += cache.pair_builds;
                stages.supports_built += cache.support_builds;
            }
        }
    }
    if (measure_base)
        assert(stages.packs == stages.baseline_reject + std::accumulate(stages.outcomes.begin(), stages.outcomes.end(), Wide(0)));
    assert(stages.packs == std::accumulate(stages.cached.begin(), stages.cached.end(), Wide(0)));
    assert(stages.raw_maps == expected_raw);
    std::cout << "left-roots=" << left_roots << " stride=" << left_step << " packs=" << left_packs
              << " right-roots=" << right_roots << " stride=" << right_step << " packs=" << right_packs
              << " matched profiles=" << right.size() << " mark pairs=" << stages.graph_pairs << '\n'
              << "token-compatible pack maps=" << stages.raw_maps << " column-compatible mark maps="
              << stages.column_maps << " tested pack maps=" << stages.packs << '\n';
    if (measure_base)
        std::cout << "direct degree rejects=" << stages.baseline_reject << " base rejects=" << stages.outcomes[0]
                  << " singleton rejects=" << stages.outcomes[1] << " arc rejects=" << stages.outcomes[2]
                  << " pass=" << stages.outcomes[3] << " defer=" << stages.outcomes[4] << '\n'
                  << "pair choice checks=" << stages.work << " cap/map=" << cap << " old filter pass="
                  << stages.old_pass << " new removals of old pass=" << stages.old_pass_incidence_reject << '\n'
                  << "column-free requests=" << stages.no_columns_cases << " rejections=" << stages.no_columns_cut
                  << " deferred=" << stages.no_columns_defer << " mapped rejections=" << stages.no_columns_mapped_cut << '\n';
    std::cout << "cached base=" << stages.cached[0] << " single=" << stages.cached[1] << " pair=" << stages.cached[2]
              << " pass=" << stages.cached[3] << " defer=" << stages.cached[4]
              << " reverse-side cuts=" << stages.cached_right_cuts << " domains built=" << stages.domains_built
              << " pair keys built=" << stages.pairs_built << " support matrices=" << stages.supports_built
              << " relaxed wing counts=" << loose_wings << '\n';
}

int main(int argc, char** argv) {
    const std::clock_t started = std::clock();
    assert(argc >= 3);
    std::ifstream input(argv[2]);
    assert(input);
    if (std::string(argv[1]) == "control") {
        assert(argc == 3);
        controls(input);
    } else if (std::string(argv[1]) == "count" || std::string(argv[1]) == "cover" ||
               std::string(argv[1]) == "cover-audit") {
        const std::string mode = argv[1];
        const bool count = mode == "count";
        assert(argc == (count ? 5 : 7));
        std::ifstream second(argv[3]);
        std::ofstream output(argv[4]);
        assert(second && output);
        if (count) pilot(input, second, 1, 1, 0, false, false, 0, &output);
        else pilot(input, second, 1, 1, 16000, mode == "cover-audit", true, std::stoull(argv[5]), nullptr,
                   read_profile(argv[6]), &output);
        assert(output);
    } else {
        const std::string mode = argv[1];
        const bool measure_base = mode == "pilot" || mode == "audit";
        const bool propagate = mode == "audit" || mode == "arc" || mode == "loose";
        assert((measure_base || mode == "bench" || propagate) && (argc == 7 || argc == 8));
        std::ifstream second(argv[3]);
        assert(second);
        const int left_step = std::stoi(argv[4]), right_step = std::stoi(argv[5]);
        assert(left_step > 0 && right_step > 0);
        pilot(input, second, left_step, right_step, std::stoull(argv[6]), measure_base, propagate,
              argc == 8 ? std::stoull(argv[7]) : 500000, nullptr, std::nullopt, nullptr, mode == "loose");
    }
    std::cout << "cpu_s=" << double(std::clock() - started) / CLOCKS_PER_SEC << '\n';
    return 0;
}
