struct StarPolish {
    using Load = array<int,2>;
    struct Choice {
        unsigned mask;
        Load demand;
    };
    struct Group {
        vector<int> ids;
        vector<Choice> choices;
        unsigned old = 0;
    };
    vector<Group> groups;
    vector<Load> minimumLoad, maximumLoad;
    Load remaining{};
    vector<pair<u64,int>> representatives;
    array<unordered_map<u64,i64>,64> cached;
    u64 outside;
    u64 best[64];
    i64 minimum, baseCount;
    i64 nodes = 0, leaves = 0, misses = 0;
    bool expired = false;

    StarPolish(const vector<u64>& targets, const u64* incumbent, i64 threshold) : minimum(threshold) {
        u64 orbit = 0;
        for (u64 target : targets) orbit |= target;
        outside = ALLV & ~orbit;
        memcpy(best, incumbent, sizeof best);
        baseCount = recA(outside, K);
        for (size_t target = 0; target < targets.size(); ++target) {
            int rep = ctz(targets[target]);
            remaining[target] = pc(incumbent[rep]) - pc(adj[rep]);
        }
        for (u64 subset = orbit; subset; subset = (subset - 1) & orbit) {
            if (!isIndep(subset) || pc(subset) > K) continue;
            int orbitSize = 1;
            u64 shifted = step(subset);
            while (shifted != subset && shifted > subset) { shifted = step(shifted); ++orbitSize; }
            if (shifted == subset) representatives.push_back({subset, orbitSize});
        }
        for (int base = 0, cycle = 0; cycle < (int)P.symCycles.size(); ++cycle) {
            int length = P.symCycles[cycle];
            if (!(orbit >> base & 1)) {
                Group group;
                vector<Load> targetPerOrbit;
                vector<int> outsidePerOrbit;
                int outsideWanted = 0;
                Load targetWanted{};
                for (size_t target = 0; target < targets.size(); ++target) {
                    int root = ctz(targets[target]);
                    for (int vertex = base; vertex < base + length; ++vertex) {
                        int id = orbitOf[root][vertex];
                        if (find(group.ids.begin(), group.ids.end(), id) != group.ids.end()) continue;
                        Load contribution{};
                        int atBase = 0;
                        for (auto [first, second] : orbits[id]) {
                            atBase += first == base || second == base;
                            contribution[target] += first == root || second == root;
                        }
                        if (orbitPresent(id)) {
                            group.old |= 1u << group.ids.size();
                            outsideWanted += atBase;
                            targetWanted[target] += contribution[target];
                        }
                        group.ids.push_back(id);
                        outsidePerOrbit.push_back(atBase);
                        targetPerOrbit.push_back(contribution);
                    }
                }
                if (outsideWanted && pc(group.old) < (int)group.ids.size()) {
                    for (unsigned mask = 0; mask < (1u << group.ids.size()); ++mask) {
                        int load = 0;
                        Load demand{};
                        for (unsigned bits = mask; bits;) {
                            int offset = ctz(bits);
                            bits &= bits - 1;
                            load += outsidePerOrbit[offset];
                            for (size_t target = 0; target < targets.size(); ++target)
                                demand[target] += targetPerOrbit[offset][target];
                        }
                        if (load == outsideWanted) group.choices.push_back({mask, demand});
                    }
                }
                if (group.choices.size() > 1) {
                    for (size_t target = 0; target < targets.size(); ++target)
                        remaining[target] += targetWanted[target];
                    groups.push_back(move(group));
                }
            }
            base += length;
        }
        sort(groups.begin(), groups.end(), [](const auto& left, const auto& right) {
            return left.choices.size() < right.choices.size();
        });
        minimumLoad.resize(groups.size()+1);
        maximumLoad.resize(groups.size()+1);
        for (size_t index = groups.size(); index-- > 0;) {
            const auto& group = groups[index];
            for (size_t target = 0; target < targets.size(); ++target) {
                int smallest = 100, largest = 0;
                for (const auto& choice : group.choices) {
                    smallest = min(smallest, choice.demand[target]);
                    largest = max(largest, choice.demand[target]);
                }
                minimumLoad[index][target] = minimumLoad[index+1][target] + smallest;
                maximumLoad[index][target] = maximumLoad[index+1][target] + largest;
            }
            for (int id : group.ids) if (orbitPresent(id)) flip(id);
        }
    }

    static u64 step(u64 set) {
        u64 image = 0;
        while (set) {
            int vertex = ctz(set);
            set &= set - 1;
            image |= 1ULL << perm[vertex];
        }
        return image;
    }

    static void flip(int id) {
        for (auto [first, second] : orbits[id]) {
            adj[first] ^= 1ULL << second;
            adj[second] ^= 1ULL << first;
        }
    }

    i64 evaluate() {
        i64 count = baseCount;
        for (auto [subset, multiplicity] : representatives) {
            int size = K - pc(subset);
            u64 available = outside;
            while (subset) {
                int vertex = ctz(subset);
                subset &= subset - 1;
                available &= ~adj[vertex];
            }
            auto& memo = cached[size];
            auto iter = memo.find(available);
            i64 result;
            if (iter != memo.end()) result = iter->second;
            else {
                ++misses;
                result = recA(available, size);
                if (memo.size() < 200000) memo.emplace(available, result);
            }
            count += multiplicity * result;
            if (!P.symVerify && count >= minimum) return count;
        }
        if (P.symVerify && count != recA(ALLV, K)) throw logic_error("star count differs from full recount");
        return count;
    }

    void visit(size_t index) {
        ++nodes;
        if ((nodes & 127) == 0 && now() - t0 >= P.timelimit) expired = true;
        if (expired || minimum == 0) return;
        if (index == groups.size()) {
            if (remaining != Load{}) throw logic_error("bad degree balance");
            if (!attachmentLimit(adj)) return;
            ++leaves;
            i64 count = evaluate();
            if (count < minimum) { minimum = count; memcpy(best, adj, sizeof best); }
            return;
        }
        const auto& group = groups[index];
        for (const auto& choice : group.choices) {
            Load next = remaining;
            for (size_t target = 0; target < next.size(); ++target) next[target] -= choice.demand[target];
            if (next[0] < minimumLoad[index+1][0] || next[0] > maximumLoad[index+1][0] ||
                next[1] < minimumLoad[index+1][1] || next[1] > maximumLoad[index+1][1]) continue;
            bool legal = true;
            unsigned changed = 0;
            for (unsigned left = choice.mask; left;) {
                int offset = ctz(left);
                left &= left - 1;
                int id = group.ids[offset];
                flip(id);
                changed |= 1u << offset;
                auto [first, second] = orbits[id][0];
                if (adj[first] & adj[second]) { legal = false; break; }
            }
            if (legal) {
                swap(remaining, next);
                visit(index + 1);
                swap(remaining, next);
            }
            while (changed) {
                int offset = ctz(changed);
                changed &= changed - 1;
                flip(group.ids[offset]);
            }
            if (expired || minimum == 0) break;
        }
    }
};

static bool runStarPolish() {
    if (!cntK && !cntT) return checkFound();
    vector<u64> targets;
    for (int base = 0, cycle = 0; cycle < (int)P.symCycles.size(); ++cycle) {
        int length = P.symCycles[cycle];
        if (length > 1) targets.push_back(((1ULL << length) - 1) << base);
        base += length;
    }
    for (int pass = 1; now() - t0 < P.timelimit; ++pass) {
        i64 starting = cntK;
        for (size_t cycle = 0; cycle < targets.size(); ++cycle)
            for (size_t partner = P.symStar == 1 ? cycle : cycle + 1;
                 partner < (P.symStar == 1 ? cycle + 1 : targets.size()); ++partner) {
                int degree[64];
                for (int vertex = 0; vertex < N; ++vertex) degree[vertex] = pc(adj[vertex]);
                vector<u64> affected{targets[cycle]};
                if (partner != cycle) affected.push_back(targets[partner]);
                u64 original[64], incumbent[64];
                memcpy(original, adj, sizeof original);
                memcpy(incumbent, adj, sizeof incumbent);
                vector<int> interior;
                if (P.symStar == 3) {
                    u64 core = targets[cycle] | targets[partner];
                    for (u64 left = core; left; left &= left - 1)
                        for (u64 right = left & (left - 1); right; right &= right - 1) {
                            int id = orbitOf[ctz(left)][ctz(right)];
                            if (find(interior.begin(), interior.end(), id) == interior.end()) interior.push_back(id);
                        }
                }
                i64 minimum = cntK, nodes = 0, leaves = 0, misses = 0;
                unsigned tested = 0;
                bool expired = false;
                for (unsigned difference = 0; difference < (1u << interior.size()); ++difference) {
                    if (now() - t0 >= P.timelimit) { expired = true; break; }
                    memcpy(adj, original, sizeof original);
                    for (unsigned toggles = difference; toggles; toggles &= toggles - 1)
                        StarPolish::flip(interior[ctz(toggles)]);
                    StarPolish polish(affected, incumbent, minimum);
                    bool legal = true;
                    for (int id : interior) if (orbitPresent(id)) {
                        auto [first, second] = orbits[id][0];
                        if (adj[first] & adj[second]) { legal = false; break; }
                    }
                    if (legal && polish.remaining[0] >= polish.minimumLoad[0][0] && polish.remaining[0] <= polish.maximumLoad[0][0] &&
                        polish.remaining[1] >= polish.minimumLoad[0][1] && polish.remaining[1] <= polish.maximumLoad[0][1]) polish.visit(0);
                    ++tested;
                    nodes += polish.nodes;
                    leaves += polish.leaves;
                    misses += polish.misses;
                    minimum = polish.minimum;
                    memcpy(incumbent, polish.best, sizeof incumbent);
                    expired = polish.expired;
                    if (!minimum || expired) break;
                }
                memcpy(adj, incumbent, sizeof adj);
                fullCount();
                if (!isSymmetric() || cntK != minimum || cntT)
                    throw logic_error("invalid polished snapshot");
                for (int vertex = 0; vertex < N; ++vertex)
                    if (degree[vertex] != pc(adj[vertex])) throw logic_error("star polish changed degree");
                noteBest();
                saveBest("best");
                fprintf(LOG, "STAR pass=%d orbit=%zu partner=%zu inner=%u nodes=%lld legal=%lld counts=%lld K=%lld status=%s\n",
                        pass, cycle, partner, tested, (long long)nodes, (long long)leaves,
                        (long long)misses, (long long)cntK, expired ? "partial" : cntK ? "complete" : "zero");
                fflush(LOG);
                if (!cntK) return checkFound();
                if (expired || now() - t0 >= P.timelimit) return false;
            }
        if (cntK == starting) break;
    }
    return false;
}
