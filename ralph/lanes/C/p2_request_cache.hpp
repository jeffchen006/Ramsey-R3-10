struct SideData {
    std::vector<Mask> edges, common, wing;
    std::vector<int> deficits;
    int width, cap, degree;
};

static SideData side_data(const Mark& mark, const Pack& pack, const Rules& spec) {
    assert(mark.shared.empty());
    const auto core = vertices(all(mark.graph) & ~(mark.graph[mark.root] | (Mask(1) << mark.root)));
    SideData data{{}, {}, {}, {}, spec.width, spec.cap, spec.degree};
    for (int vertex : core) {
        auto compress = [](Mask neighbors, const std::vector<int>& labels) {
            Mask mask = 0;
            for (std::size_t index = 0; index < labels.size(); ++index)
                if (neighbors & (Mask(1) << labels[index])) mask |= Mask(1) << index;
            return mask;
        };
        data.edges.push_back(compress(mark.graph[vertex], core));
        data.common.push_back(compress(mark.graph[vertex], mark.columns));
        Mask wing_mask = 0;
        for (int index = 0; index < spec.width; ++index)
            if (pack[index] & (Mask(1) << vertex)) wing_mask |= Mask(1) << index;
        data.wing.push_back(wing_mask);
        data.deficits.push_back(spec.degree - degree(mark.graph, vertex) - std::popcount(wing_mask));
        assert(data.deficits.back() >= 0 && data.deficits.back() <= 9);
    }
    return data;
}

struct LocalSubset {
    Mask mask, common, wing;
};

static Mask place_columns(Mask mask, const std::array<Mask, 6>& permutation) {
    Mask result = 0;
    for (; mask; mask &= mask - 1) result |= permutation[std::countr_zero(mask)];
    return result;
}

class RequestCache {
    SideData side;
    std::vector<std::vector<LocalSubset>> subsets;
    std::unordered_map<unsigned, std::vector<Mask>> witness_cache, domain_cache;
    std::unordered_map<Wide, bool> pair_cache;
    using Choice = std::pair<unsigned, const std::vector<Mask>*>;
    struct Supports {
        std::vector<Wide> forward, reverse;
    };
    std::unordered_map<Wide, Supports> support_cache;

    void enumerate(Mask rest, LocalSubset subset, int size) {
        subsets[size].push_back(subset);
        while (rest) {
            const int next = std::countr_zero(rest);
            const Mask bit = Mask(1) << next;
            rest ^= bit;
            enumerate(rest & ~side.edges[next], {subset.mask | bit, subset.common | side.common[next],
                                                 subset.wing | side.wing[next]}, size + 1);
        }
    }

    const std::vector<Mask>& witnesses(Mask forbidden, int wing_used, int goal) {
        const unsigned key = (unsigned(goal) << 8) | (unsigned(wing_used) << 6) | forbidden;
        auto [entry, fresh] = witness_cache.try_emplace(key);
        if (fresh) {
            for (std::size_t size = 0; size < subsets.size(); ++size) {
                for (const LocalSubset& subset : subsets[size]) {
                    const int common = side.cap - std::popcount(subset.common | forbidden);
                    const int wing = side.width - std::min(std::popcount(subset.wing), wing_used);
                    const int boundary_alpha = std::max(2, std::max(1, common) + wing);
                    if (int(size) + boundary_alpha >= goal)
                        entry->second.push_back(subset.mask);
                }
            }
        }
        return entry->second;
    }

    static bool hits(Mask choice, const std::vector<Mask>& witnesses) {
        for (Mask witness : witnesses)
            if (!(choice & witness)) return false;
        return true;
    }

    Choice request(Mask support, int wing_used, int deficit) {
        const unsigned key = (unsigned(deficit) << 8) | (unsigned(wing_used) << 6) | support;
        auto [entry, fresh] = domain_cache.try_emplace(key);
        if (fresh && deficit < int(subsets.size())) {
            ++domain_builds;
            const auto& requirements = witnesses(support, wing_used, side.degree);
            for (const LocalSubset& subset : subsets[deficit])
                if (!(support & subset.common) && hits(subset.mask, requirements))
                    entry->second.push_back(subset.mask);
        }
        return {key, &entry->second};
    }

    static Wide pair_key(Choice first, Choice second, int wing_used, bool adjacent) {
        assert(first.first <= second.first);
        return (Wide(first.first) << 16) | (Wide(second.first) << 4) | (wing_used << 1) | adjacent;
    }

    bool compatible(Choice first, Choice second, int wing_used, bool adjacent) {
        if (first.first > second.first) std::swap(first, second);
        const Wide key = pair_key(first, second, wing_used, adjacent);
        auto [entry, fresh] = pair_cache.try_emplace(key, false);
        if (!fresh) return entry->second;
        ++pair_builds;
        const auto& requirements = adjacent ? empty : witnesses((first.first | second.first) & 63,
                                                                 wing_used, side.degree - 1);
        if (first.second->size() > second.second->size()) std::swap(first, second);
        for (Mask left : *first.second) {
            for (Mask right : *second.second) {
                if (adjacent ? !(left & right) : hits(left | right, requirements)) {
                    entry->second = true;
                    return true;
                }
            }
        }
        return false;
    }

    const std::vector<Wide>& supports(Choice first, Choice second, int wing_used, bool adjacent) {
        const bool swapped = first.first > second.first;
        if (swapped) std::swap(first, second);
        const Wide key = pair_key(first, second, wing_used, adjacent);
        auto [entry, fresh] = support_cache.try_emplace(key);
        Supports& lists = entry->second;
        if (fresh) {
            ++support_builds;
            const auto& requirements = adjacent ? empty : witnesses((first.first | second.first) & 63,
                                                                     wing_used, side.degree - 1);
            assert(first.second->size() <= 64 && second.second->size() <= 64);
            lists.forward.resize(first.second->size());
            lists.reverse.resize(second.second->size());
            for (std::size_t left = 0; left < first.second->size(); ++left) {
                for (std::size_t right = 0; right < second.second->size(); ++right) {
                    const Mask left_set = (*first.second)[left], right_set = (*second.second)[right];
                    if (adjacent ? !(left_set & right_set) : hits(left_set | right_set, requirements)) {
                        lists.forward[left] |= Wide(1) << right;
                        lists.reverse[right] |= Wide(1) << left;
                    }
                }
            }
        }
        return swapped ? lists.reverse : lists.forward;
    }

    const std::vector<Mask> empty{};
    bool valid_base;

public:
    Wide domain_builds = 0, pair_builds = 0, support_builds = 0;

    explicit RequestCache(SideData own) : side(std::move(own)), subsets(side.edges.size() + 1) {
        assert(side.cap <= 6 && side.width <= 3 && side.edges.size() <= 14);
        enumerate((Mask(1) << side.edges.size()) - 1, {0, 0, 0}, 0);
        valid_base = witnesses(0, 0, side.degree + 1).empty();
    }

    Outcome check(const SideData& opposite, const std::array<Mask, 6>& placement, bool propagate = false,
                  const std::vector<Mask>* planted = nullptr, bool loose_wings = false) {
        if (!valid_base) return Outcome::base;
        std::array<Choice, 14> choices{};
        std::array<int, 14> order{};
        const int count = opposite.edges.size();
        for (int row = 0; row < count; ++row) {
            const Mask support = place_columns(opposite.common[row], placement);
            choices[row] = request(support, std::popcount(opposite.wing[row]), opposite.deficits[row]);
            const auto& options = *choices[row].second;
            if (planted) assert(std::find(options.begin(), options.end(), (*planted)[row]) != options.end());
            if (options.empty()) return Outcome::single;
            order[row] = row;
        }
        std::sort(order.begin(), order.begin() + count, [&](int first, int second) {
            return std::pair(choices[first].second->size(), first) < std::pair(choices[second].second->size(), second);
        });
        auto used_wings = [&](int first, int second) {
            if (!loose_wings) return std::popcount(opposite.wing[first] | opposite.wing[second]);
            return std::min(side.width, std::popcount(opposite.wing[first]) + std::popcount(opposite.wing[second]));
        };
        for (int first = 0; first < count; ++first) {
            const int row = order[first];
            for (int second = first + 1; second < count; ++second) {
                const int other = order[second];
                const int wing_used = used_wings(row, other);
                const bool adjacent = opposite.edges[row] & (Mask(1) << other);
                if (!compatible(choices[row], choices[other], wing_used, adjacent)) return Outcome::arc;
            }
        }
        if (!propagate) return Outcome::pass;
        std::array<Wide, 14> active{};
        for (int row = 0; row < count; ++row) {
            const auto size = choices[row].second->size();
            if (size > 64) return Outcome::defer;
            active[row] = ~Wide(0) >> (64 - size);
        }
        std::array<std::array<const std::vector<Wide>*, 14>, 14> support{};
        bool changed;
        do {
            changed = false;
            for (int outer = 0; outer < count; ++outer) {
                const int row = order[outer];
                for (int inner = 0; inner < count; ++inner) {
                    if (outer == inner) continue;
                    const int other = order[inner];
                    if (!support[row][other]) {
                        const int used = used_wings(row, other);
                        const bool adjacent = opposite.edges[row] & (Mask(1) << other);
                        support[row][other] = &supports(choices[row], choices[other], used, adjacent);
                    }
                    const auto& choices_supported = *support[row][other];
                    for (Wide todo = active[row]; todo; todo &= todo - 1) {
                        if (choices_supported[std::countr_zero(todo)] & active[other]) continue;
                        active[row] ^= todo & -todo;
                        changed = true;
                    }
                    if (!active[row]) return Outcome::arc;
                }
            }
        } while (changed);
        if (planted) {
            for (int row = 0; row < count; ++row) {
                const auto& options = *choices[row].second;
                const auto index = std::find(options.begin(), options.end(), (*planted)[row]) - options.begin();
                assert(index < 64 && (active[row] & (Wide(1) << index)));
            }
        }
        return Outcome::pass;
    }
};
