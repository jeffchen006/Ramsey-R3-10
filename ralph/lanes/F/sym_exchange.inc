static vector<array<unsigned char, 64>> orbitLoad;
static unordered_map<u64, vector<pair<int,int>>> exchangeClasses;
static i64 exchangeAttempts, exchangeTrials, exchangeAccepted;
static int exchangeAmax = -1;

static bool orbitPresent(int id) {
    auto [first, second] = orbits[id][0];
    return adj[first] >> second & 1;
}

static u64 exchangeKey(int first, int second = -1) {
    u64 key = 0;
    for (int index = 0, base = 0; index < (int)P.symCycles.size(); ++index) {
        int load = orbitLoad[first][base] + (second < 0 ? 0 : orbitLoad[second][base]);
        if (load) key = (key << 13) | ((index << 7) | load);
        base += P.symCycles[index];
    }
    return key;
}

static void prepareExchange() {
    orbitLoad.resize(orbits.size());
    for (size_t id = 0; id < orbits.size(); ++id) {
        for (auto [first, second] : orbits[id]) {
            ++orbitLoad[id][first];
            ++orbitLoad[id][second];
        }
        exchangeClasses[exchangeKey(id)].push_back({id, -1});
        for (size_t partner = 0; partner < id; ++partner)
            exchangeClasses[exchangeKey(id, partner)].push_back({id, partner});
    }
    fprintf(LOG, "exchange classes=%zu amax=%d\n", exchangeClasses.size(), exchangeAmax);
}

static bool attachmentLimit(const u64* graph) {
    if (exchangeAmax < 0) return true;
    u64 fixed = 0;
    for (int vertex = 0; vertex < N; ++vertex)
        if (perm[vertex] == vertex) fixed |= 1ULL << vertex;
    for (int vertex = 0; vertex < N; ++vertex)
        if (perm[vertex] != vertex && pc(graph[vertex] & fixed) > exchangeAmax) return false;
    return true;
}

static int samplePresent() {
    for (int attempt = 0; attempt < 24; ++attempt) {
        int id = rndi(orbits.size());
        if (orbitPresent(id)) return id;
    }
    return -1;
}

static i64 exchangeMove(bool bestEffort = false) {
    ++exchangeAttempts;
    mv.clear();
    int removed = samplePresent();
    if (removed < 0) return LLONG_MAX / 4;
    int partner = rndu() < 0.8 ? samplePresent() : -1;
    if (partner == removed) return LLONG_MAX / 4;
    const auto& choices = exchangeClasses.at(exchangeKey(removed, partner));
    if (choices.size() <= 1) return LLONG_MAX / 4;
    const int start = rndi(choices.size());
    const int examined = min<int>(choices.size(), bestEffort ? 32 : 8);
    for (int offset = 0; offset < examined; ++offset) {
        auto [added, other] = choices[(start + offset) % choices.size()];
        if ((partner < 0) != (other < 0) || orbitPresent(added) || (other >= 0 && orbitPresent(other))) continue;
        u64 trial[64]; memcpy(trial, adj, sizeof trial);
        for (int id : {removed, partner, added, other}) if (id >= 0) {
            for (auto [first, second] : orbits[id]) {
                trial[first] ^= 1ULL << second;
                trial[second] ^= 1ULL << first;
            }
        }
        bool good = true;
        for (int id : {added, other}) if (id >= 0) {
            auto [first, second] = orbits[id][0];
            good &= !(trial[first] & trial[second]);
        }
        if (!good || !attachmentLimit(trial)) continue;
        if (P.symVerify)
            for (int vertex = 0; vertex < N; ++vertex)
                if (pc(trial[vertex]) != pc(adj[vertex])) throw logic_error("exchange changed degree");
        ++exchangeTrials;
        i64 before = score();
        for (int id : {removed, partner, added, other}) if (id >= 0) toggleOrbit(id);
        if (cntT) throw logic_error("exchange introduced triangle");
        return score() - before;
    }
    return LLONG_MAX / 4;
}
