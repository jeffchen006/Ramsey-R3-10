#include <bits/stdc++.h>

using namespace std;
using Mask = uint32_t;
using Group = uint32_t;
using Weight = uint64_t;
using Profile = array<Group, 4>;
using Graph = vector<Mask>;
using Rim = pair<int, int>;
using Stratum = pair<int, int>;
constexpr int shapes_max = 8;
using Histogram = array<Weight, shapes_max>;

void require(bool value, const string& message) {
    if (!value) throw runtime_error(message);
}
int pop(Mask mask) { return __builtin_popcount(mask); }
Mask bit(int site) { return Mask{1} << site; }
struct Params { int degree, cap, alpha, roots; };

vector<Graph> graphs(const string& filename) {
    ifstream input(filename);
    require(bool(input), "catalogue open");
    vector<Graph> out;
    for (string text; input >> text;) {
        int order = text[0] - 63;
        require(1 <= order && order <= 17 && text.size() == size_t(1+(order*(order-1)+11)/12), "graph6 order");
        require(out.empty() || out.front().size() == size_t(order), "mixed catalogue order");
        for (char ch : text) require(ch >= 63 && ch <= 126, "graph6 character");
        Graph graph(order);
        int cursor = 0;
        for (int high = 0; high < order; ++high)
            for (int low = 0; low < high; ++low, ++cursor)
                if ((text[1+cursor/6]-63) & bit(5-cursor%6)) {
                    graph[high] |= bit(low);
                    graph[low] |= bit(high);
                }
        for (int site = 0; site < order; ++site)
            for (Mask peers = graph[site]; peers; peers &= peers-1)
                require(!(graph[site] & graph[__builtin_ctz(peers)]), "host triangle");
        out.push_back(move(graph));
    }
    require(!out.empty() && input.eof(), "catalogue parse");
    return out;
}

Group packed(vector<int> types) {
    require(!types.empty() && types.size() <= 4, "group size");
    sort(types.begin(), types.end());
    Group out = 1;
    for (int type : types) {
        require(0 <= type && type < 32, "row type");
        out = (out << 5) | Group(type);
    }
    return out;
}

vector<int> unpack(Group group) {
    vector<int> types;
    for (; group > 1; group >>= 5) types.push_back(group & 31);
    require(group == 1, "invalid group code");
    reverse(types.begin(), types.end());
    return types;
}

string group_text(Group group) {
    string out;
    for (int type : unpack(group)) {
        if (!out.empty()) out += ',';
        out += to_string(type);
    }
    return out;
}

vector<string> split(const string& text, char delimiter) {
    vector<string> out;
    string part;
    istringstream input(text);
    while (getline(input, part, delimiter)) out.push_back(part);
    require(!out.empty() && text.back() != delimiter, "empty token");
    return out;
}

struct Atlas {
    vector<uint8_t> alpha;
    vector<Mask> independent;
    Mask full;

    explicit Atlas(const Graph& graph, Params params) : alpha(bit(graph.size())), full(alpha.size()-1) {
        independent.push_back(0);
        for (Mask mask = 1; mask <= full; ++mask) {
            Mask rest = mask & (mask-1);
            alpha[mask] = max<int>(alpha[rest], 1+alpha[rest & ~graph[__builtin_ctz(mask)]]);
            if (alpha[mask] == pop(mask)) independent.push_back(mask);
        }
        require(alpha[full] <= params.alpha-params.roots, "host independence");
    }
};

struct Effort {
    uint64_t hosts = 0, profiles = 0, lookups = 0;
    array<uint64_t, 5> distinct{}, positive{}, probes{};
    vector<tuple<int,int,int,Group,bool>> samples;
    bool all_receipts = false;
};

struct Gate {
    const Atlas& atlas;
    int order;
    Rim rim;
    int bound;
    Effort& effort;
    array<vector<Mask>, 32> options;
    unordered_map<Group, bool> seen;

    Gate(const Atlas& atlas, int order, Rim rim, Params params, Effort& effort)
      : atlas(atlas), order(order), rim(rim), bound(params.alpha-params.roots+1), effort(effort) {
        ++effort.hosts;
        for (Mask row : atlas.independent)
            if (atlas.alpha[atlas.full ^ row] <= bound-1)
                options[2*pop(row)+bool(row & bit(rim.second))].push_back(row);
    }

    bool group(Group code) {
        ++effort.lookups;
        auto found = seen.find(code);
        if (found != seen.end()) return found->second;
        auto types = unpack(code);
        int size = types.size();
        array<Mask, 16> unions{};
        vector<const vector<Mask>*> rows;
        for (int type : types) rows.push_back(&options[type]);
        stable_sort(rows.begin(), rows.end(), [](auto first, auto second) { return first->size() < second->size(); });
        uint64_t probes = 0;
        auto dfs = [&](auto& self, int index) -> bool {
            if (index == size) return true;
            Mask end = bit(index);
            for (Mask row : *rows[index]) {
                ++probes;
                unions[end] = row;
                Mask subset = 1;
                for (; subset < end; ++subset) {
                    Mask merged = row | unions[subset];
                    if (atlas.alpha[atlas.full ^ merged] > bound-1-pop(subset)) break;
                    unions[end | subset] = merged;
                }
                if (subset == end && self(self, index+1)) return true;
            }
            return false;
        };
        bool pass = !rows.front()->empty() && dfs(dfs, 0);
        seen.emplace(code, pass);
        uint64_t index = effort.distinct[size]++;
        effort.positive[size] += pass;
        effort.probes[size] += probes;
        if (effort.all_receipts || index < 12 || index % 2048 == 0)
            effort.samples.emplace_back(order, rim.first, rim.second, code, pass);
        return pass;
    }

    bool profile(const Profile& profile) {
        ++effort.profiles;
        for (auto it = profile.rbegin(); it != profile.rend() && *it; ++it)
            if (!group(*it)) return false;
        return true;
    }
};

struct Weighted { Profile profile; Weight weight; size_t shape; };
struct Roster { vector<Weighted> rows; Histogram all{}; };
using Side = map<Stratum, map<Rim, Roster>>;

pair<Stratum, const Graph*> labelled_host(const vector<Graph>& cat, Rim rim) {
    const auto& graph = cat.at(rim.first);
    require(0 <= rim.second && rim.second < int(graph.size()), "neutral range");
    int neutral = pop(graph[rim.second]), sum = 0;
    for (Mask row : graph) sum += pop(row);
    return {{sum-neutral, neutral}, &graph};
}

pair<Profile, string> weight_profile(const string& text, Params params, int order) {
    Profile profile{};
    auto parts = split(text, ';');
    require(parts.size() <= size_t(params.roots), "group count");
    string shape;
    vector<vector<int>> serial;
    for (size_t index = 0; index < parts.size(); ++index) {
        vector<int> types;
        for (auto& part : split(parts[index], ',')) {
            int type = stoi(part);
            require(to_string(type) == part && type/2 <= params.degree-1, "row type text");
            types.push_back(type);
        }
        require(is_sorted(types.begin(), types.end()), "unsorted row types");
        serial.push_back(types);
        profile[index] = packed(types);
        shape += '0'+int(types.size());
    }
    require(is_sorted(serial.begin(), serial.end()), "unsorted demand groups");
    sort(profile.begin(), profile.end());
    sort(shape.begin(), shape.end());
    if (params.roots == 4) {
        require((order == 16 && (shape == "2233" || shape == "2333")) ||
                (order == 17 && (shape == "2334" || shape == "3333" || shape == "3334")), "target shape");
    }
    return {profile,shape};
}

struct Counts {
    Weight raw = 0, forward = 0, reverse = 0, both = 0;
    void add(Weight left, Weight right, Weight forward_pass, Weight reverse_pass) {
        require(forward_pass <= left && reverse_pass <= right, "weighted subtotal exceeds bucket");
        raw += left*right;
        forward += forward_pass*right;
        reverse += left*reverse_pass;
        both += forward_pass*reverse_pass;
    }
};

Weight total(const Histogram& hist) { return accumulate(hist.begin(), hist.end(), Weight{0}); }
Histogram directed(const Roster& source, Gate& gate) {
    Histogram out{};
    for (const auto& row : source.rows)
        if (gate.profile(row.profile)) out[row.shape] += row.weight;
    return out;
}

void print_counts(ostream& stream, const Counts& counts) {
    const auto& [raw, forward, reverse, both] = counts;
    require(forward+reverse <= raw+both && both <= min(forward,reverse), "invalid intersection");
    stream << ' ' << raw << ' ' << forward << ' ' << reverse << ' ' << both << ' ' << raw+both-forward-reverse << '\n';
}

void emit_effort(const Effort& effort, const string& receipt) {
    ofstream out(receipt);
    require(bool(out), "receipt open");
    out << "order host neutral group pass\n";
    for (const auto& [order, host, neutral, group, pass] : effort.samples)
        out << order << ' ' << host << ' ' << neutral << ' ' << group_text(group) << ' ' << pass << '\n';
    cout << "effort " << effort.hosts << ' ' << effort.profiles << ' ' << effort.lookups << '\n';
    for (int size = 1; size <= 4; ++size)
        cout << "group " << size << ' ' << effort.distinct[size] << ' ' << effort.positive[size] << ' ' << effort.probes[size] << '\n';
}

void count(const array<vector<Graph>,2>& cats, Params params, const string& weights, const string& receipt,
           const string& buckets, optional<Stratum> only) {
    array<Side,2> inventory;
    array<map<string,size_t>,2> shapes;
    array<int,2> orders{int(cats[0][0].size()), int(cats[1][0].size())};
    require(orders[0]+1 == orders[1], "nonconsecutive window orders");
    ifstream input(weights);
    require(bool(input), "weights open");
    string header;
    getline(input, header);
    istringstream fields(header);
    vector<string> names{istream_iterator<string>(fields), {}};
    require(names == vector<string>{"order", "D", "d", "host", "neutral", "profile", "count"}, "weight schema");
    array<Weight,2> seen_mass{}, seen_rows{}, max_weight{};
    int order;
    while (input >> order) {
        Stratum stratum;
        Rim rim;
        string text;
        Weight weight;
        require(bool(input >> stratum.first >> stratum.second >> rim.first >> rim.second >> text >> weight), "weight fields");
        require(order == orders[0] || order == orders[1], "weight order");
        int side = order == orders[1];
        require(weight > 0 && weight <= 10000000, "weight range");
        seen_mass[side] += weight;
        require(seen_mass[side] <= 10000000, "mass range");
        ++seen_rows[side];
        if (only && stratum != (side ? Stratum{only->first+params.degree,params.degree-only->second} : *only)) continue;
        auto [actual, graph] = labelled_host(cats[side], rim);
        require(actual == stratum, "weight host/stratum mismatch");
        auto [profile, shape] = weight_profile(text,params,order);
        auto found = shapes[side].emplace(shape, shapes[side].size()).first;
        size_t shape_id = found->second;
        require(shape_id < shapes_max, "shape capacity");
        auto& roster = inventory[side][stratum][rim];
        roster.rows.push_back({profile, weight, shape_id});
        roster.all[shape_id] += weight;
        max_weight[side] = max(max_weight[side],weight);
    }
    require(input.eof(), "weight parse");
    for (int side = 0; side < 2; ++side) {
        Weight kept_mass = 0, kept_rows = 0, kept_hosts = 0;
        for (auto& [stratum, rims] : inventory[side])
            for (auto& [rim, roster] : rims) {
                sort(roster.rows.begin(), roster.rows.end(), [](const auto& a, const auto& b) { return a.profile < b.profile; });
                require(adjacent_find(roster.rows.begin(), roster.rows.end(), [](const auto& a, const auto& b) {
                    return a.profile == b.profile;
                }) == roster.rows.end(), "duplicate weight cell");
                kept_mass += total(roster.all);
                kept_rows += roster.rows.size();
                ++kept_hosts;
            }
        cout << "inventory " << orders[side] << ' ' << seen_mass[side] << ' ' << seen_rows[side] << ' '
             << kept_mass << ' ' << kept_rows << ' ' << kept_hosts << ' ' << max_weight[side] << '\n';
    }
    Effort effort;
    effort.all_receipts = params.roots == 2;
    ofstream host_file(buckets);
    require(bool(host_file), "host bucket output");
    host_file << "D d left_host left_neutral right_host right_neutral raw forward reverse both\n";
    Counts aggregate;
    uint64_t paired = 0, positive = 0, largest_raw = 0, largest_both = 0;
    for (const auto& [stratum, left] : inventory[0]) {
        auto found = inventory[1].find({stratum.first+params.degree, params.degree-stratum.second});
        if (found == inventory[1].end()) continue;
        const auto& right = found->second;
        Counts stratum_counts;
        array<array<Counts,shapes_max>,shapes_max> shape_counts{};
        vector<const pair<const Rim,Roster>*> left_items, right_items;
        for (const auto& entry : left) left_items.push_back(&entry);
        for (const auto& entry : right) right_items.push_back(&entry);
        require(left.size()*right.size() <= 1000000, "host-pair matrix cap");
        vector<vector<Histogram>> forward(left.size(), vector<Histogram>(right.size()));
        int prev_host = -1;
        unique_ptr<Atlas> atlas;
        for (size_t ri = 0; ri < right_items.size(); ++ri) {
            const auto& [rim, roster] = *right_items[ri];
            if (rim.first != prev_host) {
                atlas = make_unique<Atlas>(cats[1][rim.first],params);
                prev_host = rim.first;
            }
            Gate gate(*atlas,orders[1],rim,params,effort);
            for (size_t li = 0; li < left_items.size(); ++li)
                forward[li][ri] = directed(left_items[li]->second,gate);
        }
        prev_host = -1;
        uint64_t stratum_positive = 0, stratum_raw_max = 0, stratum_both_max = 0;
        for (size_t li = 0; li < left_items.size(); ++li) {
            const auto& [rim, roster] = *left_items[li];
            if (rim.first != prev_host) {
                atlas = make_unique<Atlas>(cats[0][rim.first],params);
                prev_host = rim.first;
            }
            Gate gate(*atlas,orders[0],rim,params,effort);
            for (size_t ri = 0; ri < right_items.size(); ++ri) {
                const auto& [other_rim, other] = *right_items[ri];
                const Histogram& fwd = forward[li][ri];
                Histogram rev = directed(other,gate);
                Weight lm = total(roster.all), rm = total(other.all);
                Weight fm = total(fwd), vm = total(rev);
                aggregate.add(lm,rm,fm,vm);
                stratum_counts.add(lm,rm,fm,vm);
                stratum_raw_max = max(stratum_raw_max,lm*rm);
                stratum_both_max = max(stratum_both_max,fm*vm);
                stratum_positive += fm && vm;
                host_file << stratum.first << ' ' << stratum.second << ' ' << rim.first << ' ' << rim.second << ' '
                          << other_rim.first << ' ' << other_rim.second << ' ' << lm*rm << ' ' << fm*rm << ' '
                          << lm*vm << ' ' << fm*vm << '\n';
                for (size_t lshape = 0; lshape < shapes[0].size(); ++lshape)
                    for (size_t rshape = 0; rshape < shapes[1].size(); ++rshape)
                        shape_counts[lshape][rshape].add(roster.all[lshape],other.all[rshape],fwd[lshape],rev[rshape]);
            }
        }
        paired += left.size()*right.size();
        positive += stratum_positive;
        largest_raw = max(largest_raw,stratum_raw_max);
        largest_both = max(largest_both,stratum_both_max);
        cout << "stratum " << stratum.first << ' ' << stratum.second << ' ' << left.size() << ' ' << right.size()
             << ' ' << left.size()*right.size() << ' ' << stratum_positive << ' ' << stratum_raw_max << ' ' << stratum_both_max;
        print_counts(cout,stratum_counts);
        for (const auto& [lname,lid] : shapes[0]) for (const auto& [rname,rid] : shapes[1]) {
            if (!shape_counts[lid][rid].raw) continue;
            cout << "shape " << stratum.first << ' ' << stratum.second << ' ' << lname << ' ' << rname;
            print_counts(cout,shape_counts[lid][rid]);
        }
    }
    require(paired, "no compatible host pairs");
    host_file.flush();
    require(bool(host_file), "host bucket write failure");
    cout << "total " << paired << ' ' << positive << ' ' << largest_raw << ' ' << largest_both;
    print_counts(cout,aggregate);
    emit_effort(effort,receipt);
}

struct CaseFrame { Rim rim; Stratum stratum; Profile profile; };

CaseFrame case_frame(istream& input, const vector<Graph>& cat, Params params) {
    Rim rim;
    require(bool(input >> rim.first >> rim.second), "case rim");
    auto [stratum, graph] = labelled_host(cat,rim);
    vector<Mask> marks(params.roots);
    Mask covered = 0;
    for (auto& mark : marks) {
        require(bool(input >> mark) && mark < bit(graph->size()) && pop(mark) == params.degree-params.roots, "case mark");
        covered |= mark;
    }
    require(is_sorted(marks.begin(), marks.end()) && (covered | bit(rim.second)) == bit(graph->size())-1 &&
            !(covered & bit(rim.second)), "case mark labels");
    Profile profile{};
    for (size_t index = 0; index < marks.size(); ++index) {
        Mask only = marks[index];
        for (size_t other = 0; other < marks.size(); ++other) if (index != other) {
            require(pop(marks[index] & marks[other])+params.roots <= params.cap,"case mark intersection");
            only &= ~marks[other];
        }
        vector<int> types;
        for (; only; only &= only-1) {
            Mask row = graph->at(__builtin_ctz(only));
            bool neutral = row & bit(rim.second);
            types.push_back(2*(params.degree-1-pop(row)+neutral)+neutral);
        }
        if (!types.empty()) profile[index] = packed(types);
    }
    sort(profile.begin(), profile.end());
    return {rim,stratum,profile};
}

void cases(const array<vector<Graph>,2>& cats, Params params, const string& path, const string& receipt) {
    ifstream input(path);
    require(bool(input), "cases open");
    Effort effort;
    using Query = tuple<int, Rim, Profile>;
    map<Query,bool> cached;
    int lid, rid;
    set<pair<int,int>> ids;
    Counts counts;
    cout << "left right forward reverse both\n";
    while (input >> lid >> rid) {
        require(ids.emplace(lid,rid).second, "duplicate case id");
        auto left = case_frame(input,cats[0],params), right = case_frame(input,cats[1],params);
        require(right.stratum == Stratum{left.stratum.first+params.degree, params.degree-left.stratum.second}, "case stratum mismatch");
        auto accepts = [&](int dest, Rim rim, const Profile& profile) {
            Query query{dest,rim,profile};
            auto found = cached.find(query);
            if (found != cached.end()) return found->second;
            const Graph& graph = cats[dest].at(rim.first);
            Atlas atlas(graph,params);
            Gate gate(atlas,graph.size(),rim,params,effort);
            bool pass = gate.profile(profile);
            cached.emplace(query,pass);
            return pass;
        };
        bool fw = accepts(1,right.rim,left.profile), rv = accepts(0,left.rim,right.profile);
        counts.add(1,1,fw,rv);
        cout << lid << ' ' << rid << ' ' << fw << ' ' << rv << ' ' << (fw && rv) << '\n';
    }
    require(input.eof() && !ids.empty(), "cases parse");
    cout << "total";
    print_counts(cout,counts);
    emit_effort(effort,receipt);
}

int main(int argc, char** argv) try {
    require(argc >= 10, "usage: panel17 CASES|COUNT CAT_L CAT_R INPUT RECEIPT DEGREE CAP ALPHA ROOTS [BUCKETS [D d]]");
    const string mode = argv[1];
    Params params{stoi(argv[6]),stoi(argv[7]),stoi(argv[8]),stoi(argv[9])};
    require(params.degree > 0 && params.degree <= 9 && (params.roots == 2 || params.roots == 4), "parameters");
    array<vector<Graph>,2> cats{graphs(argv[2]),graphs(argv[3])};
    if (mode == "CASES" && argc == 10) cases(cats,params,argv[4],argv[5]);
    else if (mode == "COUNT" && (argc == 11 || argc == 13)) {
        optional<Stratum> only;
        if (argc == 13) only = Stratum{stoi(argv[11]),stoi(argv[12])};
        count(cats,params,argv[4],argv[5],argv[10],only);
    } else require(false,"mode/argument mismatch");
    return 0;
} catch (const exception& error) {
    cerr << error.what() << '\n';
    return 1;
}
