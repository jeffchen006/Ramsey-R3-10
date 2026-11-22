struct PermutationSet {
    std::array<Wide, 12> block{};

    void add(unsigned index) { block[index >> 6] |= Wide(1) << (index & 63); }
    bool has(unsigned index) const { return (block[index >> 6] >> (index & 63)) & 1; }
    bool empty() const { return std::all_of(block.begin(), block.end(), [](Wide word) { return !word; }); }
    unsigned size() const {
        unsigned total = 0;
        for (auto part : block) total += std::popcount(part);
        return total;
    }
    template<class Visitor> void visit(Visitor&& visitor) const {
        for (unsigned part = 0; part < block.size(); ++part)
            for (Wide todo = block[part]; todo; todo &= todo - 1)
                visitor(64 * part + std::countr_zero(todo));
    }
};

struct CommonMaps {
    std::array<unsigned, 4096> ids{};
    std::array<std::array<Mask, 64>, 720> images{};

    CommonMaps() {
        std::array<Mask, 6> permutation{1, 2, 4, 8, 16, 32};
        unsigned index = 0;
        do {
            ids[key(permutation)] = index & ~1u;
            for (Mask support = 0; support < 64; ++support)
                images[index][support] = place_columns(support, permutation);
            ++index;
        } while (std::next_permutation(permutation.begin(), permutation.end()));
        assert(index == images.size());
    }

    static unsigned key(const std::array<Mask, 6>& permutation) {
        unsigned code = 0;
        for (unsigned index = 0; index < 4; ++index)
            code = (code << 3) | std::countr_zero(permutation[index]);
        return code;
    }

    unsigned id(const std::array<Mask, 6>& permutation) const {
        return ids[key(permutation)] + (permutation[4] > permutation[5]);
    }
};

static const CommonMaps& common_maps() {
    static const CommonMaps all_maps;
    return all_maps;
}

struct TwoSiteKey {
    unsigned first, second;
    int wing_union;
    bool adjacent;

    unsigned key() const {
        assert(first <= second && first < 4096 && second < 4096 && wing_union <= 3);
        return (first << 15) | (second << 3) | (wing_union << 1) | adjacent;
    }

    auto priority() const {
        return std::tuple((first >> 8) + (second >> 8), wing_union,
                          std::popcount((first | second) & 63), adjacent, first, second);
    }

    bool test(RequestCache& cache, const std::array<Mask, 64>& image) const {
        return cache.two_requests(first, second, wing_union, adjacent, image);
    }
};

static std::vector<TwoSiteKey> two_site_keys(const SideData& side, std::size_t budget) {
    std::vector<TwoSiteKey> keys;
    const auto type = [&](unsigned row) {
        return (unsigned(side.deficits[row]) << 8) | (unsigned(std::popcount(side.wing[row])) << 6) | side.common[row];
    };
    for (unsigned first = 0; first < side.edges.size(); ++first) {
        for (unsigned second = first + 1; second < side.edges.size(); ++second) {
            auto first_type = type(first), second_type = type(second);
            auto [low, high] = std::minmax(first_type, second_type);
            keys.push_back({low, high, std::popcount(side.wing[first] | side.wing[second]),
                            bool(side.edges[first] & (Mask(1) << second))});
        }
    }
    std::sort(keys.begin(), keys.end(), [](auto lhs, auto rhs) { return lhs.priority() < rhs.priority(); });
    keys.erase(std::unique(keys.begin(), keys.end(), [](auto lhs, auto rhs) { return lhs.key() == rhs.key(); }), keys.end());
    if (keys.size() > budget) keys.resize(budget);
    return keys;
}

struct PrejoinStats {
    Wide evaluated = 0, reused = 0, pruned = 0, queries = 0, audited = 0, entries = 0;
};

class PrejoinIndex {
    struct Entry { PermutationSet evaluated, yes; };
    std::unordered_map<unsigned, Entry> lookup;
public:
    PermutationSet filter(RequestCache& cache, const std::vector<TwoSiteKey>& keys,
                          PermutationSet candidates, PrejoinStats& stats) {
        for (auto key : keys) {
            ++stats.queries;
            auto [entry, inserted] = lookup.try_emplace(key.key());
            stats.entries += inserted;
            auto& [known, yes] = entry->second;
            for (unsigned part = 0; part < candidates.block.size(); ++part) {
                Wide old = candidates.block[part];
                if (!old) continue;
                Wide needed = old & ~known.block[part];
                stats.evaluated += std::popcount(needed);
                stats.reused += std::popcount(old & known.block[part]);
                known.block[part] |= needed;
                for (; needed; needed &= needed - 1) {
                    const unsigned local = std::countr_zero(needed);
                    if (key.test(cache, common_maps().images[64 * part + local])) yes.block[part] |= Wide(1) << local;
                }
                candidates.block[part] = old & yes.block[part];
                stats.pruned += std::popcount(old ^ candidates.block[part]);
            }
            if (candidates.empty()) break;
        }
        return candidates;
    }
};

static int prejoin_budget = -1;
static bool prejoin_audit = false;

static void control_prejoin(RequestCache& left_cache, const SideData& rhs) {
    PrejoinIndex index;
    PrejoinStats stats;
    PermutationSet sample;
    for (unsigned id = 0; id < 720; ++id) {
        const auto& image = common_maps().images[id];
        if (!(image[15] & ~Mask(15))) sample.add(id);
    }
    const auto keys = two_site_keys(rhs, 91);
    const auto accepted = index.filter(left_cache, keys, sample, stats);
    assert(accepted.has(0));
    sample.visit([&](unsigned id) {
        auto [first, last] = std::pair{keys.begin(), keys.end()};
        const auto& image = common_maps().images[id];
        std::array<Mask, 6> placement{};
        for (unsigned col = 0; col < placement.size(); ++col) placement[col] = image[1u << col];
        assert(common_maps().id(placement) == id);
        bool direct = std::all_of(first, last, [&](auto key) { return key.test(left_cache, image); });
        assert(direct == accepted.has(id));
        assert(direct || left_cache.check(rhs, placement, true) < Outcome::pass);
    });
    auto corrupted = rhs;
    corrupted.deficits.front() = 9;
    auto bad_keys = two_site_keys(corrupted, 91);
    const auto bad = index.filter(left_cache, bad_keys, sample, stats);
    assert(bad.empty());
}
