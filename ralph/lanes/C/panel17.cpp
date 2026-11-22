#include <bits/stdc++.h>

using namespace std;
using Mask = uint32_t;
using Count = uint64_t;
using Pack = array<Mask, 3>;
using Group = array<int, 3>;
using Signature = array<int, 3>;
using Header = array<int, 5>;
using ID = array<int, 3>;
using Domains = vector<vector<Pack>>;

constexpr int order = 17;
constexpr Mask universe = (1u << order) - 1;
int size_of(Mask mask) { return __builtin_popcount(mask); }
vector<int> sites(Mask mask) {
    vector<int> result;
    for (; mask; mask &= mask - 1) result.push_back(__builtin_ctz(mask));
    return result;
}

struct Host {
    array<Mask, order> adj{};
    vector<Pack> atlas;
};
struct Frame {
    int host;
    array<Mask, 4> marks;
    array<int, 2> holes;
    vector<Group> groups;
    Header header;
};
vector<Host> hosts;
vector<Frame> frames;

void read_hosts(const string& path) {
    ifstream input(path);
    string line;
    while (input >> line) {
        if (line.size() != 24 || line.front() - 63 != order) throw runtime_error("host graph6");
        Host host;
        int index = 0;
        for (int col = 0; col < order; ++col) {
            for (int row = 0; row < col; ++row, ++index) {
                if (((line[1 + index / 6] - 63) >> (5 - index % 6)) & 1) {
                    host.adj[row] |= 1u << col;
                    host.adj[col] |= 1u << row;
                }
            }
        }
        hosts.push_back(host);
    }
    if (hosts.size() != 7) throw runtime_error("host count");
}

void read_input(const string& atlas_path, const string& frame_path) {
    ifstream atlas_file(atlas_path), frame_file(frame_path);
    int host_id;
    Pack pack;
    size_t atlas_count = 0;
    while (atlas_file >> host_id >> pack[0] >> pack[1] >> pack[2]) {
        if (!is_sorted(pack.begin(), pack.end()) || pack.back() > universe)
            throw runtime_error("atlas format");
        hosts.at(host_id).atlas.push_back(pack);
        ++atlas_count;
    }
    if (atlas_count != 9959) throw runtime_error("atlas count");

    Frame frame;
    auto& marks = frame.marks;
    while (frame_file >> frame.host >> marks[0] >> marks[1] >> marks[2] >> marks[3]) {
        const auto& adj = hosts.at(frame.host).adj;
        Mask united = 0;
        for (auto mark : marks) united |= mark;
        auto holes = sites(universe ^ united);
        if (holes.size() != 2) throw runtime_error("holes");
        frame.holes = {holes[0], holes[1]};
        frame.groups.clear();
        for (unsigned anchor = 0; anchor < marks.size(); ++anchor) {
            Mask only = marks[anchor];
            for (unsigned other = 0; other < marks.size(); ++other)
                if (anchor != other) only &= ~marks[other];
            auto row = sites(only);
            if (row.size() == 3) frame.groups.push_back({row[0], row[1], row[2]});
        }
        if (frame.groups.size() < 2 || frame.groups.size() > 3)
            throw runtime_error("singleton dimensions");
        int total = 0;
        for (int vertex : sites(united)) total += size_of(adj[vertex]);
        frame.header = {total, int((adj[holes[0]] >> holes[1]) & 1),
                        size_of(adj[holes[0]]), size_of(adj[holes[1]]),
                        size_of(adj[holes[0]] & adj[holes[1]])};
        frames.push_back(frame);
    }
    if (frames.size() != 55055) throw runtime_error("frame count");
}

Header oriented_header(const Frame& frame, int flip) {
    auto result = frame.header;
    if (flip) swap(result[2], result[3]);
    return result;
}
bool agrees(Header left, Header right) {
    return left[0] == right[0] && left[1] == right[1] &&
           left[2] + right[2] == 9 + left[1] && left[3] + right[3] == 9 + left[1] &&
           left[4] + right[4] <= 5;
}

using AtlasIndex = map<Signature, vector<Pack>>;
map<array<int, 3>, AtlasIndex> index_cache;
int row_type(Mask house_row, array<int, 2> holes, int degree) {
    return 4 * degree + 2 * ((house_row >> holes[0]) & 1) + ((house_row >> holes[1]) & 1);
}
const AtlasIndex& atlas_index(int host, array<int, 2> holes) {
    auto [entry, created] = index_cache.try_emplace({host, holes[0], holes[1]});
    if (created) {
        for (auto pack : hosts.at(host).atlas) {
            do {
                Signature key;
                for (int row = 0; row < 3; ++row)
                    key[row] = row_type(pack[row], holes, size_of(pack[row]));
                entry->second[key].push_back(pack);
            } while (next_permutation(pack.begin(), pack.end()));
        }
    }
    return entry->second;
}

using Choices = vector<const vector<Pack>*>;
Choices signatures(const Frame& origin, array<int, 2> origin_holes,
                   const Frame& target, array<int, 2> target_holes) {
    const auto& index = atlas_index(target.host, target_holes);
    const auto& adj = hosts[origin.host].adj;
    Mask holes = (1u << origin_holes[0]) | (1u << origin_holes[1]);
    Choices choices;
    for (const auto& group : origin.groups) {
        Signature key;
        for (int row = 0; row < 3; ++row) {
            auto neighbors = adj[group[row]];
            key[row] = row_type(neighbors, origin_holes, 8 - size_of(neighbors & ~holes));
        }
        auto match = index.find(key);
        if (match == index.end()) return {};
        choices.push_back(&match->second);
    }
    return choices;
}

Domains local_domains(const Choices& choices, const Frame& origin, array<int, 2> origin_holes,
                      const Frame& target, array<int, 2> target_holes) {
    const auto& origin_adj = hosts[origin.host].adj;
    const auto& target_adj = hosts[target.host].adj;
    Mask origin_private = universe ^ ((1u << origin_holes[0]) | (1u << origin_holes[1]));
    Domains result;
    for (size_t group_id = 0; group_id < choices.size(); ++group_id) {
        const auto& group = origin.groups[group_id];
        result.emplace_back();
        for (const auto& pack : *choices[group_id]) {
            bool valid = true;
            for (int row = 0; row < 3 && valid; ++row) {
                Mask private_neighbors = origin_adj[group[row]] & origin_private;
                for (int hole = 0; hole < 2; ++hole) {
                    int shared = size_of(private_neighbors & origin_adj[origin_holes[hole]]) +
                                 size_of(pack[row] & target_adj[target_holes[hole]]);
                    valid &= shared <= 5;
                }
                for (Mask mark : target.marks) valid &= size_of(pack[row] & mark) <= 4;
                for (int other = 0; other < row; ++other) {
                    int shared = size_of(private_neighbors & origin_adj[group[other]]) +
                                 size_of(pack[row] & pack[other]) + 1;
                    valid &= shared <= 5;
                }
            }
            if (valid) result.back().push_back(pack);
        }
        if (result.back().empty()) return {};
    }
    return result;
}

using Matrix = array<array<bool, 3>, 3>;
Matrix forward_matrix(const Pack& rows, const Group& destination) {
    Matrix matrix{};
    for (int row = 0; row < 3; ++row)
        for (int col = 0; col < 3; ++col)
            matrix[row][col] = (rows[row] & (1u << destination[col])) != 0;
    return matrix;
}
Matrix transposed_matrix(const Pack& cols, const Group& destination) {
    Matrix matrix{};
    for (int col = 0; col < 3; ++col)
        for (int row = 0; row < 3; ++row)
            matrix[row][col] = (cols[col] & (1u << destination[row])) != 0;
    return matrix;
}
bool panels(const vector<Group>& left, const vector<Group>& right,
            Domains& rows, Domains& cols) {
    bool changed;
    do {
        changed = false;
        for (size_t row = 0; row < left.size(); ++row) {
            for (size_t col = 0; col < right.size(); ++col) {
                set<Matrix> forward, backward;
                for (auto pack : rows[row]) forward.insert(forward_matrix(pack, right[col]));
                for (auto pack : cols[col]) backward.insert(transposed_matrix(pack, left[row]));
                changed |= erase_if(rows[row], [&](const Pack& pack) {
                    return !backward.count(forward_matrix(pack, right[col]));
                }) != 0;
                if (rows[row].empty()) return false;
                changed |= erase_if(cols[col], [&](const Pack& pack) {
                    return !forward.count(transposed_matrix(pack, left[row]));
                }) != 0;
                if (cols[col].empty()) return false;
            }
        }
    } while (changed);
    return true;
}

int screen(const ID& id, const auto& accept) {
    auto [left_id, right_id, flip] = id;
    const auto& left = frames.at(left_id);
    const auto& right = frames.at(right_id);
    if (!agrees(left.header, oriented_header(right, flip))) return 0;
    auto right_holes = right.holes;
    if (flip) swap(right_holes[0], right_holes[1]);
    auto left_choices = signatures(left, left.holes, right, right_holes);
    if (left_choices.empty()) return 1;
    auto right_choices = signatures(right, right_holes, left, left.holes);
    if (right_choices.empty()) return 2;
    auto rows = local_domains(left_choices, left, left.holes, right, right_holes);
    if (rows.empty()) return 3;
    auto cols = local_domains(right_choices, right, right_holes, left, left.holes);
    if (cols.empty()) return 3;
    if (!panels(left.groups, right.groups, rows, cols)) return 4;
    accept(rows, cols);
    return 5;
}

void panel_controls() {
    Group left, right;
    Pack rows, cols;
    int positive = 0, negative = 0;
    while (cin >> left[0] >> left[1] >> left[2] >> rows[0] >> rows[1] >> rows[2] >>
                  right[0] >> right[1] >> right[2] >> cols[0] >> cols[1] >> cols[2]) {
        Domains left_domain{{rows}}, right_domain{{cols}};
        if (!panels({left}, {right}, left_domain, right_domain)) throw runtime_error("plant");
        ++positive;
        for (int row : left) {
            for (int col = 0; col < 3; ++col) {
                right_domain = {{cols}};
                right_domain[0][0][col] ^= 1u << row;
                left_domain = {{rows}};
                if (panels({left}, {right}, left_domain, right_domain))
                    throw runtime_error("one-entry mutant");
                ++negative;
            }
        }
    }
    if (positive != 3448 || negative != 31032) throw runtime_error("control count");
    cout << "panel positives " << positive << " single-entry negatives " << negative << '\n';
}

void print_id(ID id) { cout << id[0] << ' ' << id[1] << ' ' << id[2] << '\n'; }
Count key_id(const ID& id) {
    return (static_cast<Count>(id[0]) * frames.size() + id[1]) * 2 + id[2];
}

const auto ignore_domains = [](const Domains&, const Domains&) {};

void screen_ids(istream& input, bool stages) {
    array<Count, 6> counts{};
    Count total = 0;
    ID id;
    while (input >> id[0] >> id[1] >> id[2]) {
        int stage = screen(id, ignore_domains);
        if (stages) cout << id[0] << ' ' << id[1] << ' ' << id[2] << ' ' << stage << '\n';
        else if (stage == 5) print_id(id);
        for (int index = 0; index <= stage; ++index) ++counts[index];
        ++total;
    }
    if (!input.eof()) throw runtime_error("malformed roster");
    cerr << "submitted header forward-signature reciprocal-signature local-domains transpose";
    for (Count count : counts) cerr << ' ' << count;
    cerr << '\n';
    if (total != counts[0]) throw runtime_error("count");
}

using Wide = uint64_t;
using Graph = vector<Wide>;
using FullPack = array<pair<int, Wide>, 3>;

int population(Wide mask) { return __builtin_popcountll(mask); }
int unpack(Wide& mask) {
    int vertex = __builtin_ctzll(mask);
    mask &= mask - 1;
    return vertex;
}
Wide bit(int vertex) { return Wide{1} << vertex; }
bool independent_set(const Graph& graph, Wide remaining, int target) {
    if (target == 0) return true;
    while (population(remaining) >= target) {
        int vertex = unpack(remaining);
        if (independent_set(graph, remaining & ~graph[vertex], target - 1)) return true;
    }
    return false;
}

enum Result { bad_degree, bad_triangle, bad_codegree, bad_alpha, unresolved, result_count };
const array<string, result_count> result_names{"degree", "triangle", "codegree", "independent-set", "unresolved"};
Result propagate(Graph lower, Graph upper, int degree, int cap) {
    const int vertex_count = lower.size();
    do {
        for (int vertex = 0; vertex < vertex_count; ++vertex) {
            if (lower[vertex] & ~upper[vertex] || population(lower[vertex]) > degree ||
                population(upper[vertex]) < degree) return bad_degree;
        }
        for (int vertex = 0; vertex < vertex_count; ++vertex) {
            for (Wide neighbors = lower[vertex]; neighbors;) {
                if (lower[vertex] & lower[unpack(neighbors)]) return bad_triangle;
            }
        }
        for (int vertex = 0; vertex < vertex_count; ++vertex) {
            for (int other = vertex + 1; other < vertex_count; ++other) {
                if (population(lower[vertex] & lower[other]) > cap) return bad_codegree;
            }
        }
        if (independent_set(upper, bit(vertex_count) - 1, 1 + degree)) return bad_alpha;

        bool changed = false;
        Graph next_lower = lower, next_upper = upper;
        for (int vertex = 0; vertex < vertex_count; ++vertex) {
            bool forbid_rest = population(lower[vertex]) == degree;
            bool require_rest = population(upper[vertex]) == degree;
            for (Wide unknown = upper[vertex] & ~lower[vertex]; unknown;) {
                int other = unpack(unknown);
                if (forbid_rest || (lower[vertex] & lower[other])) {
                    next_upper[vertex] &= ~bit(other);
                    next_upper[other] &= ~bit(vertex);
                    changed = true;
                }
                if (require_rest) {
                    next_lower[vertex] |= bit(other);
                    next_lower[other] |= bit(vertex);
                    changed = true;
                }
            }
        }
        if (!changed) return unresolved;
        lower.swap(next_lower);
        upper.swap(next_upper);
    } while (true);
}

Wide physical(Mask mask, const array<int, order>& labels) {
    Wide result = 0;
    for (; mask; mask &= mask - 1) result |= bit(labels[__builtin_ctz(mask)]);
    return result;
}
void edge(Graph& graph, int vertex, int other) {
    graph[vertex] |= bit(other);
    graph[other] |= bit(vertex);
}
bool consistent(const FullPack& left, const FullPack& right) {
    for (const auto& [vertex, neighbors] : left) {
        for (const auto& [other, opposite] : right) {
            bool adjacent = (neighbors & bit(other)) != 0;
            if (adjacent != ((opposite & bit(vertex)) != 0)) return false;
            if (population(neighbors & opposite) > (adjacent ? 0 : 5)) return false;
        }
    }
    return true;
}

array<Count, result_count> terminal(const ID& id, const Domains& left, const Domains& right) {
    const array<const Frame*, 2> paired{&frames.at(id[0]), &frames.at(id[1])};
    const array<const Domains*, 2> options{&left, &right};
    array<array<int, order>, 2> labels{};
    Graph lower(40);
    for (int side = 0; side < 2; ++side) {
        int private_label = 15 * side;
        auto holes = paired[side]->holes;
        if (side == 1 && id[2]) swap(holes[0], holes[1]);
        for (int vertex = 0; vertex < order; ++vertex) {
            labels[side][vertex] = vertex == holes[0] ? 30 : vertex == holes[1] ? 31 : private_label++;
        }
        const auto& host = hosts[paired[side]->host];
        for (int vertex = 0; vertex < order; ++vertex) {
            int actual = labels[side][vertex];
            lower[actual] |= physical(host.adj[vertex], labels[side]);
            for (int anchor = 0; anchor < 4; ++anchor) {
                if (paired[side]->marks[anchor] & (1u << vertex)) edge(lower, actual, 32 + 4 * side + anchor);
            }
        }
    }
    for (int first = 32; first < 36; ++first)
        for (int second = 36; second < 40; ++second) edge(lower, first, second);
    Graph upper = lower;
    for (int first = 0; first < 15; ++first)
        for (int second = 15; second < 30; ++second)
            if (!(lower[first] & lower[second])) edge(upper, first, second);

    vector<vector<FullPack>> all_domains;
    for (int side = 0; side < 2; ++side) {
        const auto& groups = paired[side]->groups;
        for (size_t group = 0; group < groups.size(); ++group) {
            auto& domain = all_domains.emplace_back();
            for (const auto& candidate : options[side]->at(group)) {
                FullPack pack;
                bool valid = true;
                for (int row = 0; row < 3; ++row) {
                    int vertex = labels[side][groups[group][row]];
                    Wide neighbors = lower[vertex] | physical(candidate[row], labels[1 - side]);
                    pack[row] = {vertex, neighbors};
                    if (neighbors & ~upper[vertex]) valid = false;
                    for (int other = 0; other < 40 && valid; ++other) {
                        if (other == vertex) continue;
                        int common = population(neighbors & lower[other]);
                        if (common > 5 || (common && (neighbors & bit(other)))) valid = false;
                    }
                    for (int prev = 0; prev < row; ++prev)
                        if (population(neighbors & pack[prev].second) > 5) valid = false;
                }
                if (valid) domain.push_back(pack);
            }
        }
    }
    array<Count, result_count> counts{};
    vector<FullPack> picked;
    auto enumerate = [&](auto&& self, vector<vector<FullPack>> domains) -> void {
        if (domains.empty()) {
            Graph lo = lower, hi = upper;
            for (const auto& pack : picked) {
                for (const auto& [vertex, neighbors] : pack) {
                    for (int other = 0; other < 40; ++other) {
                        if (neighbors & bit(other)) edge(lo, vertex, other);
                        else hi[other] &= ~bit(vertex);
                    }
                    lo[vertex] = hi[vertex] = neighbors;
                }
            }
            ++counts[propagate(move(lo), move(hi), 9, 5)];
            return;
        }
        auto least = min_element(domains.begin(), domains.end(), [](const auto& first, const auto& second) {
            return first.size() < second.size();
        });
        auto frontier = move(*least);
        domains.erase(least);
        for (const auto& head : frontier) {
            auto compatible = domains;
            for (auto& domain : compatible)
                erase_if(domain, [&](const auto& pack) { return !consistent(head, pack); });
            picked.push_back(head);
            self(self, move(compatible));
            picked.pop_back();
        }
    };
    enumerate(enumerate, move(all_domains));
    return counts;
}

void close_ids(istream& input) {
    ID id;
    while (input >> id[0] >> id[1] >> id[2]) {
        auto start = clock();
        array<Count, result_count> counts{};
        int stage = screen(id, [&](const Domains& rows, const Domains& cols) {
            counts = terminal(id, rows, cols);
        });
        if (stage != 5) throw runtime_error("non-panel ID in terminal roster");
        cout << id[0] << ' ' << id[1] << ' ' << id[2];
        for (Count count : counts) cout << ' ' << count;
        double milliseconds = (clock() - start) * 1000.0 / CLOCKS_PER_SEC;
        cout << ' ' << fixed << setprecision(3) << milliseconds << '\n';
    }
    if (!input.eof()) throw runtime_error("malformed terminal roster");
}

void terminal_controls(istream& input) {
    int degree, cap, vertex_count;
    int count = 0;
    while (input >> degree >> cap >> vertex_count) {
        Graph lower(vertex_count), upper(vertex_count);
        for (auto& row : lower) if (!(input >> row)) throw runtime_error("control lower");
        for (auto& row : upper) if (!(input >> row)) throw runtime_error("control upper");
        if (propagate(lower, upper, degree, cap) != unresolved) throw runtime_error("terminal destroyed plant");
        ++count;
    }
    if (count != 2118) throw runtime_error("planted terminal count");
    cout << "terminal positives " << count << '\n';
}

void old_ids(Count seed, Count draws) {
    mt19937_64 rng(seed);
    Count count = 0;
    for (Count rep = 0; rep < draws; ++rep) {
        int left = rng() % frames.size(), right = rng() % frames.size(), flip = rng() & 1;
        if (!agrees(frames[left].header, oriented_header(frames[right], flip))) continue;
        print_id({left, right, flip});
        ++count;
    }
    cerr << "old header seed " << seed << " draws " << draws << " pass " << count << '\n';
}

struct Bucket {
    int host;
    Header header;
    int flip;
    vector<int> frame_ids;
};
using BucketKey = tuple<int, Header, int>;

Count spread(Count value) {
    value ^= value >> 30;
    value *= 0xbf58476d1ce4e5b9ULL;
    value ^= value >> 27;
    value *= 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

void roster(const string& old_path, const string& strata_path, bool triple_slice) {
    ifstream old_input(old_path);
    if (!old_input) throw runtime_error("legacy roster missing");
    unordered_set<Count> old;
    ID id;
    while (old_input >> id[0] >> id[1] >> id[2]) {
        old.insert(key_id(id));
        old.insert(key_id({id[1], id[0], id[2]}));
    }
    if (!old_input.eof()) throw runtime_error("legacy roster format");
    map<BucketKey, vector<int>> grouped;
    for (int frame = 0; frame < static_cast<int>(frames.size()); ++frame)
        for (int flip = 0; flip < 2; ++flip)
            grouped[{frames[frame].host, oriented_header(frames[frame], flip), flip}].push_back(frame);
    vector<Bucket> buckets;
    for (auto& [key, ids] : grouped) {
        auto [host, header, flip] = key;
        buckets.push_back({host, header, flip, move(ids)});
    }
    map<BucketKey, vector<int>> compatible_buckets;
    for (const auto& [key, ids] : grouped) {
        auto [host, header, flip] = key;
        if (flip) continue;
        auto& compatible = compatible_buckets[key];
        for (size_t bucket = 0; bucket < buckets.size(); ++bucket)
            if (agrees(header, buckets[bucket].header)) compatible.push_back(bucket);
    }
    struct Stats { Count header{}, left_triple{}, right_only_triple{}, old{}, fresh{}, selected{}; };
    map<pair<BucketKey, int>, Stats> counts;
    Count all = 0, left_triple = 0, right_only_triple = 0, overlap = 0, fresh = 0, selected = 0;
    for (int left = 0; left < static_cast<int>(frames.size()); ++left) {
        const auto& frame = frames[left];
        BucketKey key{frame.host, frame.header, 0};
        for (int bucket_index : compatible_buckets.at(key)) {
            const auto& bucket = buckets[bucket_index];
            auto& count = counts[{key, bucket_index}];
            for (int right : bucket.frame_ids) {
                ID candidate{left, right, bucket.flip};
                ++all;
                ++count.header;
                if (frame.groups.size() == 3) {
                    ++left_triple;
                    ++count.left_triple;
                    if (triple_slice) print_id(candidate);
                    continue;
                }
                if (frames[right].groups.size() == 3) {
                    ++right_only_triple;
                    ++count.right_only_triple;
                    continue;
                }
                if (old.count(key_id(candidate))) {
                    ++overlap;
                    ++count.old;
                    continue;
                }
                Count rank = count.fresh++;
                ++fresh;
                if (triple_slice || rank % 100 != spread(rank / 100) % 100) continue;
                print_id(candidate);
                ++selected;
                ++count.selected;
            }
        }
    }
    ofstream strata(strata_path);
    if (!strata) throw runtime_error("strata output");
    strata << "left_host left_header(5) right_host right_header(5) flip header left_triple "
              "right_only_triple old fresh selected\n";
    for (const auto& [pair, count] : counts) {
        auto [key, bucket_index] = pair;
        auto [host, head, flip] = key;
        const auto& bucket = buckets[bucket_index];
        strata << host;
        for (int value : head) strata << ' ' << value;
        strata << ' ' << bucket.host;
        for (int value : bucket.header) strata << ' ' << value;
        strata << ' ' << bucket.flip << ' ' << count.header << ' ' << count.left_triple
               << ' ' << count.right_only_triple << ' ' << count.old << ' ' << count.fresh
               << ' ' << count.selected << '\n';
        if (!triple_slice && (count.selected < count.fresh / 100 ||
                              count.selected > (count.fresh + 99) / 100))
            throw runtime_error("stratum sample count");
    }
    cerr << "strata " << counts.size() << " all " << all << " left-triple " << left_triple
         << " right-only-triple " << right_only_triple << " legacy " << overlap << " fresh "
         << fresh << " selected " << selected << '\n';
    if (all != 157472001 || left_triple != 498668) throw runtime_error("header census");
}

int main(int argc, char** argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    if (argc == 2 && string(argv[1]) == "controls") { panel_controls(); return 0; }
    if (argc == 2 && string(argv[1]) == "terminal-controls") { terminal_controls(cin); return 0; }
    if (argc < 5) return 2;
    read_hosts(argv[2]);
    read_input(argv[3], argv[4]);
    string action = argv[1];
    if ((action == "screen" || action == "stages") && argc == 5) screen_ids(cin, action == "stages");
    else if (action == "terminal" && argc == 5) close_ids(cin);
    else if (action == "legacy" && argc == 7) old_ids(stoull(argv[5]), stoull(argv[6]));
    else if ((action == "pilot" || action == "triple") && argc == 7)
        roster(argv[5], argv[6], action == "triple");
    else return 2;
}
