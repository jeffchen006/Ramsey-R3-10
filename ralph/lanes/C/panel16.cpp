#include <bits/stdc++.h>

using namespace std;
using Mask = uint32_t;
using Wide = uint64_t;
using Graph = vector<Wide>;
using Pack = array<Mask, 4>;
using Counts = array<uint64_t, 5>;

int pop(Wide word) { return __builtin_popcountll(word); }
int take(Wide& word) {
    int site = __builtin_ctzll(word);
    word &= word - 1;
    return site;
}
Wide bit(int site) { return Wide{1} << site; }
double cpu_ms() { return 1000.0 * clock() / CLOCKS_PER_SEC; }
void require(bool condition, const string& message) {
    if (!condition) throw runtime_error(message);
}

struct Host {
    vector<Mask> adj;
    vector<uint8_t> alpha;
    vector<vector<Mask>> rows;

    void build() {
        if (!alpha.empty()) return;
        alpha.resize(bit(adj.size()));
        rows.resize(adj.size() + 1);
        rows[0].push_back(0);
        for (Mask mask = 1; mask < alpha.size(); ++mask) {
            Mask rest = mask & (mask - 1);
            alpha[mask] = max<int>(alpha[rest], 1 + alpha[rest & ~adj[__builtin_ctz(mask)]]);
            if (alpha[mask] == pop(mask)) rows[alpha[mask]].push_back(mask);
        }
    }
};

vector<Host> read_graphs(const string& file) {
    ifstream stream(file);
    require(bool(stream), "catalogue open");
    vector<Host> result;
    string text;
    while (stream >> text) {
        int order = text[0] - 63;
        require(1 <= order && order <= 17 && int(text.size()) == 1 + (order * (order-1) + 11) / 12,
                "graph6 record");
        Host host;
        host.adj.resize(order);
        int index = 0;
        for (int high = 0; high < order; ++high)
            for (int low = 0; low < high; ++low, ++index)
                if (((text[1 + index / 6] - 63) >> (5 - index % 6)) & 1) {
                    host.adj[high] |= bit(low);
                    host.adj[low] |= bit(high);
                }
        result.push_back(move(host));
    }
    require(!result.empty(), "empty catalogue");
    return result;
}

struct Parameters { int degree, cap, alpha, roots; };

struct Frame {
    int index{}, neutral{}, dsum{};
    vector<Mask> marks;
    vector<vector<int>> groups;
    Host* host{};
    vector<int> labels;
    string shape;
};

Frame read_frame(istream& stream, vector<Host>& catalogue, Parameters par) {
    Frame frame;
    frame.marks.resize(par.roots);
    require(bool(stream >> frame.index >> frame.neutral), "frame fields");
    for (auto& mark : frame.marks) require(bool(stream >> mark), "mark fields");
    frame.host = &catalogue.at(frame.index);
    const auto& adj = frame.host->adj;
    int order = adj.size();
    require(0 <= frame.neutral && frame.neutral < order, "neutral position");
    require(is_sorted(frame.marks.begin(), frame.marks.end()), "mark order");
    Mask mass = 0;
    for (int root = 0; root < par.roots; ++root) {
        Mask mark = frame.marks[root];
        require(mark < bit(order) && pop(mark) == par.degree - par.roots, "mark size");
        Wide only = mark;
        for (int other = 0; other < par.roots; ++other) if (root != other) {
            require(pop(mark & frame.marks[other]) + par.roots <= par.cap, "mark intersections");
            only &= ~frame.marks[other];
        }
        if (only) {
            vector<int> group;
            while (only) group.push_back(take(only));
            require(group.size() <= 4, "oversized singleton group");
            frame.shape.push_back('0' + group.size());
            frame.groups.push_back(move(group));
        }
        mass |= mark;
    }
    sort(frame.shape.begin(), frame.shape.end());
    require(mass == ((bit(order)-1) ^ bit(frame.neutral)), "mark union");
    for (int site = 0; site < order; ++site) {
        if (site != frame.neutral) frame.dsum += pop(adj[site]);
        int mark_count = 0;
        for (Mask mark : frame.marks) {
            bool member = mark & bit(site);
            require(!member || !(adj[site] & mark), "non-independent mark");
            require(pop(adj[site] & mark) <= par.cap, "site/root codegree");
            mark_count += member;
        }
        require(pop(adj[site]) + mark_count <= par.degree, "known host degree");
        for (int other = 0; other < site; ++other) {
            int shared = pop(adj[site] & adj[other]);
            for (Mask mark : frame.marks) shared += pop(mark & (bit(site) | bit(other))) == 2;
            require(shared <= par.cap, "known host codegree");
        }
    }
    return frame;
}

struct Group { int side; vector<int> sites; vector<Pack> domain; };

int demand_type(const Frame& source, int site, Parameters par) {
    Mask known = source.host->adj[site];
    bool neutral = known & bit(source.neutral);
    return 2 * (par.degree - 1 - pop(known) + neutral) + neutral;
}

vector<Pack> domain(const Frame& source, const Frame& target, const vector<int>& sites, Parameters par,
                    bool first_only = false) {
    int bound = par.alpha - par.roots + 1;
    const auto& host = *target.host;
    Mask full = host.alpha.size() - 1;
    array<vector<Mask>, 4> candidates;
    for (size_t pos = 0; pos < sites.size(); ++pos) {
        int type = demand_type(source, sites[pos], par);
        bool on_neutral = type & 1;
        int size = (type - int(on_neutral)) / 2;
        if (size < 0 || size >= int(host.rows.size())) return {};
        for (Mask row : host.rows[size])
            if (bool(row & bit(target.neutral)) == on_neutral && host.alpha[full ^ row] <= bound - 1)
                candidates[pos].push_back(row);
    }
    vector<Pack> out;
    Pack package{};
    array<Mask, 16> united{};
    auto extend = [&](auto& recurse, size_t pos) -> void {
        if (pos == sites.size()) {
            require(out.size() < 200000, "per group domain cap");
            out.push_back(package);
            return;
        }
        unsigned end = 1u << pos;
        for (Mask row : candidates[pos]) {
            bool good = true;
            for (unsigned subset = 1; subset < end; ++subset) {
                Mask merged = row | united[subset];
                if (host.alpha[full ^ merged] > bound - 1 - pop(subset)) {
                    good = false;
                    break;
                }
                united[end | subset] = merged;
            }
            if (good) {
                package[pos] = row;
                united[end] = row;
                recurse(recurse, pos + 1);
                if (first_only && !out.empty()) return;
            }
        }
    };
    extend(extend, 0);
    return out;
}

using PreflightKey = tuple<int, int, int, vector<int>>;

bool preflight(const array<Frame,2>& frames, Parameters par, map<PreflightKey,bool>& cache, int& hits, int& misses) {
    vector<tuple<int,int,size_t>> checks;
    for (int side = 0; side < 2; ++side)
        for (size_t group = 0; group < frames[side].groups.size(); ++group)
            checks.emplace_back(-int(frames[side].groups[group].size()), side, group);
    sort(checks.begin(),checks.end());
    for (const auto& check : checks) {
        auto [negsize,side,index] = check;
        const auto& source = frames[side];
        const auto& target = frames[1-side];
        const auto& group = source.groups[index];
        vector<int> demands;
        for (int site : group) demands.push_back(demand_type(source,site,par));
        sort(demands.begin(),demands.end());
        auto [entry,created] = cache.try_emplace({side,target.index,target.neutral,move(demands)},false);
        if (created) {
            ++misses;
            entry->second = !domain(source,target,group,par,true).empty();
        } else ++hits;
        if (!entry->second) return false;
    }
    return true;
}

unsigned signature(const Group& left, const Group& right, const Pack& rows) {
    unsigned result = 0;
    for (size_t row = 0; row < left.sites.size(); ++row)
        for (size_t col = 0; col < right.sites.size(); ++col)
            if (rows[row] & bit(right.sites[col]))
                result |= 1u << (left.side == 0 ? 4*row+col : 4*col+row);
    return result;
}

void filter(vector<Group>& groups) {
    vector<pair<int,int>> arcs;
    for (int index = 0; index < int(groups.size()); ++index)
        for (int peer = index + 1; peer < int(groups.size()); ++peer) if (groups[index].side != groups[peer].side) {
            arcs.emplace_back(index, peer);
            arcs.emplace_back(peer, index);
        }
    if (any_of(groups.begin(), groups.end(), [](const Group& group){ return group.domain.empty(); })) return;
    bool changed;
    do {
        changed = false;
        for (auto [index, peer] : arcs) {
            auto& source = groups[index];
            const auto& target = groups[peer];
            if (source.domain.empty() || target.domain.empty()) return;
            bitset<65536> supported;
            for (const auto& pack : target.domain) supported.set(signature(target, source, pack));
            auto end = remove_if(source.domain.begin(), source.domain.end(), [&](const Pack& pack){
                return !supported.test(signature(source, target, pack));
            });
            if (end != source.domain.end()) {
                source.domain.erase(end, source.domain.end());
                if (source.domain.empty()) return;
                changed = true;
            }
        }
    } while (changed);
}

void edge(Graph& graph, int first, int second, bool included) {
    if (included) {
        graph[first] |= bit(second);
        graph[second] |= bit(first);
    } else {
        graph[first] &= ~bit(second);
        graph[second] &= ~bit(first);
    }
}

bool independent(const Graph& upper, Wide available, int need) {
    if (need == 0) return true;
    while (pop(available) >= need) {
        int site = take(available);
        if (independent(upper, available & ~upper[site], need - 1)) return true;
    }
    return false;
}

int terminal(Graph lower, Graph upper, Parameters par) {
    int order = lower.size();
    for (;;) {
        for (int site = 0; site < order; ++site)
            if ((lower[site] & ~upper[site]) || pop(lower[site]) > par.degree || pop(upper[site]) < par.degree) return 0;
        for (int site = 0; site < order; ++site)
            for (int other = 0; other < site; ++other)
                if ((lower[site] & bit(other)) && (lower[site] & lower[other])) return 1;
        for (int site = 0; site < order; ++site)
            for (int other = 0; other < site; ++other)
                if (pop(lower[site] & lower[other]) > par.cap) return 2;
        if (independent(upper, bit(order)-1, par.alpha+1)) return 3;
        Graph next_lower = lower, next_upper = upper;
        for (int site = 0; site < order; ++site) {
            for (Wide unknown = upper[site] & ~lower[site]; unknown;) {
                int other = take(unknown);
                if (pop(lower[site]) == par.degree || (lower[site] & lower[other]))
                    edge(next_upper, site, other, false);
                if (pop(upper[site]) == par.degree) edge(next_lower, site, other, true);
            }
        }
        if (next_lower == lower && next_upper == upper) return 4;
        lower.swap(next_lower);
        upper.swap(next_upper);
    }
}

pair<Graph, Graph> base(array<Frame, 2>& frames, Parameters par) {
    int extent = 0;
    for (auto& frame : frames) {
        frame.labels.resize(frame.host->adj.size());
        for (size_t site = 0; site < frame.labels.size(); ++site) {
            frame.labels[site] = 0;
            if (int(site) != frame.neutral) frame.labels[site] = ++extent;
        }
    }
    Graph lower(extent + 1 + 2*par.roots);
    int root_base = extent + 1;
    for (int side = 0; side < 2; ++side) {
        const auto& frame = frames[side];
        for (int site = 0; site < int(frame.labels.size()); ++site) {
            for (Wide within = frame.host->adj[site]; within;) edge(lower, frame.labels[site], frame.labels[take(within)], true);
            for (int root = 0; root < par.roots; ++root)
                if (frame.marks[root] & bit(site)) edge(lower, frame.labels[site], root_base+side*par.roots+root, true);
        }
    }
    for (int first = 0; first < par.roots; ++first)
        for (int last = 0; last < par.roots; ++last) edge(lower, root_base+first, root_base+par.roots+last, true);
    Graph upper = lower;
    for (int left : frames[0].labels) if (left)
        for (int right : frames[1].labels) if (right) edge(upper, left, right, true);
    return {lower, upper};
}

struct Answer {
    vector<pair<vector<Pack>,int>> fills;
    Counts counts{};
    uint64_t probes{};
    double term_ms{};
    string capped = "no";
};

Answer join(const vector<Group>& groups, const array<Frame,2>& frames, const pair<Graph,Graph>& bounds, Parameters par) {
    Answer answer;
    vector<Pack> assigned(groups.size());
    if (any_of(groups.begin(), groups.end(), [](const Group& group){ return group.domain.empty(); })) return answer;
    auto extend = [&](auto& recurse, size_t index) -> void {
        if (index == groups.size()) {
            auto start = cpu_ms();
            if (answer.fills.size() == 2048) {
                answer.capped = "fills";
                return;
            }
            auto [lower, upper] = bounds;
            for (size_t id = 0; id < groups.size(); ++id) {
                const auto& group = groups[id];
                const auto& origin = frames[group.side];
                const auto& opposite = frames[1-group.side];
                for (size_t pos = 0; pos < group.sites.size(); ++pos)
                    for (size_t other = 0; other < opposite.labels.size(); ++other) if (opposite.labels[other]) {
                        bool chosen = assigned[id][pos] & bit(other);
                        edge(lower, origin.labels[group.sites[pos]], opposite.labels[other], chosen);
                        edge(upper, origin.labels[group.sites[pos]], opposite.labels[other], chosen);
                    }
            }
            int result = terminal(move(lower), move(upper), par);
            ++answer.counts[result];
            answer.fills.push_back({assigned, result});
            answer.term_ms += cpu_ms() - start;
            return;
        }
        const auto& group = groups[index];
        for (const auto& pack : group.domain) {
            if (++answer.probes > 10000000) {
                answer.capped = "probes";
                return;
            }
            bool compatible = true;
            for (size_t peer = 0; peer < index && compatible; ++peer) if (groups[peer].side != group.side)
                for (size_t pos = 0; pos < group.sites.size() && compatible; ++pos)
                    for (size_t other = 0; other < groups[peer].sites.size(); ++other)
                        if (bool(pack[pos] & bit(groups[peer].sites[other])) != bool(assigned[peer][other] & bit(group.sites[pos]))) {
                            compatible = false;
                            break;
                        }
            if (!compatible) continue;
            assigned[index] = pack;
            recurse(recurse, index + 1);
            if (answer.capped != "no") return;
        }
    };
    extend(extend, 0);
    return answer;
}

int main(int argc, char** argv) try {
    require(argc == 10 || (argc == 11 && string(argv[10]) == "preflight"),
            "usage: panel16 CAT16 CAT17 CASES FILLS STATS DEGREE CAP ALPHA ROOTS [preflight]");
    bool pricing_preflight = argc == 11;
    Parameters par{stoi(argv[6]),stoi(argv[7]),stoi(argv[8]),stoi(argv[9])};
    array<vector<Host>,2> catalogues{read_graphs(argv[1]), read_graphs(argv[2])};
    ifstream cases(argv[3]);
    ofstream fillings(argv[4]), stats(argv[5]);
    require(cases && fillings && stats, "file open");
    if (pricing_preflight) stats << "left right atlas_ms preflight_ms survive hits misses\n";
    else stats << "left right shape_l shape_r atlas_ms domain_ms literal_ms copy_filter_ms filtered_ms literal_terminal_ms filtered_terminal_ms literal_probes filtered_probes literal_cap filtered_cap before after degree triangle codegree I live\n";
    map<PreflightKey,bool> cache;
    int left, right;
    while (cases >> left >> right) {
        string identity = to_string(left) + " " + to_string(right);
        try {
            array<Frame,2> frames{read_frame(cases,catalogues[0],par),read_frame(cases,catalogues[1],par)};
            require(frames[0].host->adj.size() < frames[1].host->adj.size(), "window order");
            if (par.degree == 9 && par.roots == 4) {
                require(frames[0].host->adj.size() == 16 && frames[1].host->adj.size() == 17, "target window order 16/17");
                require((frames[0].shape == "2233" || frames[0].shape == "2333") &&
                        (frames[1].shape == "2334" || frames[1].shape == "3333" || frames[1].shape == "3334"), "shape");
            }
            int delta = int(frames[1].host->adj.size()) - int(frames[0].host->adj.size());
            require(frames[0].dsum + par.degree*delta == frames[1].dsum, "header private total");
            require(pop(frames[0].host->adj[frames[0].neutral]) + pop(frames[1].host->adj[frames[1].neutral]) == par.degree,
                    "header neutral degree");
            double start = cpu_ms();
            for (auto& frame : frames) {
                frame.host->build();
                require(frame.host->alpha.back() <= par.alpha - par.roots, "window independence");
            }
            double atlas_ms = cpu_ms() - start;
            start = cpu_ms();
            if (pricing_preflight) {
                int hits = 0, misses = 0;
                bool survive = preflight(frames, par, cache, hits, misses);
                stats << identity << fixed << setprecision(3) << ' ' << atlas_ms << ' ' << cpu_ms()-start
                      << ' ' << survive << ' ' << hits << ' ' << misses << endl;
                continue;
            }
            auto bounds = base(frames, par);
            vector<Group> groups;
            for (size_t index = 0; index < max(frames[0].groups.size(),frames[1].groups.size()); ++index)
                for (int side = 0; side < 2; ++side) if (index < frames[side].groups.size()) {
                    const auto& sites = frames[side].groups[index];
                    groups.push_back({side, sites, domain(frames[side],frames[1-side],sites,par)});
                }
            double domain_ms = cpu_ms() - start;
            start = cpu_ms();
            auto literal = join(groups, frames, bounds, par);
            double literal_ms = cpu_ms() - start;
            start = cpu_ms();
            auto reduced = groups;
            filter(reduced);
            double filter_ms = cpu_ms() - start;
            start = cpu_ms();
            auto filtered = join(reduced, frames, bounds, par);
            double filtered_ms = cpu_ms() - start;
            auto common = min(literal.fills.size(),filtered.fills.size());
            require(equal(literal.fills.begin(),literal.fills.begin()+common,filtered.fills.begin()), "labelled prefix mismatch");
            if (literal.capped == "no") require(literal.fills.size() >= filtered.fills.size(),"literal too short");
            if (filtered.capped == "no") require(filtered.fills.size() >= literal.fills.size(),"filtered too short");
            for (const auto& [packages, result] : filtered.fills) {
                fillings << identity << ' ' << result;
                for (size_t id = 0; id < groups.size(); ++id)
                    for (size_t pos = 0; pos < groups[id].sites.size(); ++pos) fillings << ' ' << packages[id][pos];
                fillings << '\n';
            }
            stats << identity << ' ' << frames[0].shape << ' ' << frames[1].shape << fixed << setprecision(3)
                  << ' ' << atlas_ms << ' ' << domain_ms << ' ' << literal_ms << ' ' << filter_ms << ' ' << filtered_ms
                  << ' ' << literal.term_ms << ' ' << filtered.term_ms << ' ' << literal.probes << ' ' << filtered.probes
                  << ' ' << literal.capped << ' ' << filtered.capped;
            for (const auto* entry : {&groups, &reduced}) {
                stats << ' ';
                for (size_t index = 0; index < entry->size(); ++index) {
                    if (index) stats << ',';
                    stats << entry->at(index).domain.size();
                }
            }
            for (auto count : filtered.counts) stats << ' ' << count;
            stats << endl;
            fillings.flush();
        } catch (const exception& err) {
            cerr << identity << ": " << err.what() << '\n';
            return 1;
        }
    }
    require(cases.eof(), "cases parse");
    return 0;
} catch (const exception& err) {
    cerr << err.what() << '\n';
    return 1;
}
