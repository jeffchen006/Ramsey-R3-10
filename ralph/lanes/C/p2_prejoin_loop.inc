if (prejoin_budget >= 0) {
    assert(!measure_base && !loose_wings);
    struct AssignedMap {
        std::vector<int> map;
        std::array<Mask, 6> forward, reverse;
    };
    std::array<AssignedMap, 720> assigned;
    PermutationSet candidate;
    const auto count = assign_columns(first, second, left_spec, assignment, 0, [&](const auto& map) {
        if (!column_test(first, second, map, left_spec)) return;
        ++stages.column_maps;
        auto [forward, reverse] = placements(second, map);
        const auto id = common_maps().id(forward);
        assert(!candidate.has(id));
        candidate.add(id);
        assigned[id] = {map, forward, reverse};
    });
    const unsigned candidate_count = candidate.size();
    for (std::size_t outer = 0; outer < first.packs.size(); ++outer) {
        for (std::size_t inner = 0; inner < second.packs.size(); ++inner) {
            const auto& keys = right_keys[right_index][inner];
            const auto retained = small_index[outer].filter(small_cache[outer], keys, candidate, indexed);
            stages.packs += candidate_count;
            assert(stages.packs <= expected_raw);
            stages.cached[static_cast<int>(Outcome::arc)] += candidate_count - retained.size();
            if (prejoin_audit) {
                candidate.visit([&](unsigned id) {
                    const auto& forward = assigned[id].forward;
                    const bool accept = retained.has(id);
                    const auto& image = common_maps().images[id];
                    for (Mask support = 0; support < 64; ++support)
                        assert(place_columns(support, forward) == image[support]);
                    const bool direct = std::all_of(keys.begin(), keys.end(), [&](auto key) {
                        return key.test(small_cache[outer], image);
                    });
                    assert(direct == accept);
                    if (!accept) assert(small_cache[outer].check(second_sides[inner], forward, propagate) < Outcome::pass);
                    ++indexed.audited;
                });
            }
            retained.visit([&](unsigned id) {
                const auto& [map, forward, reverse] = assigned[id];
                auto cached = small_cache[outer].check(second_sides[inner], forward, propagate);
                if (cached == Outcome::pass) {
                    if (!large_cache[inner]) large_cache[inner].emplace(second_sides[inner]);
                    cached = large_cache[inner]->check(first_sides[outer], reverse, propagate);
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
            });
        }
    }
    stages.raw_maps += count * pack_product;
    for (const auto& cache : large_cache) {
        if (!cache) continue;
        stages.domains_built += cache->domain_builds;
        stages.pairs_built += cache->pair_builds;
        stages.supports_built += cache->support_builds;
    }
    continue;
}
