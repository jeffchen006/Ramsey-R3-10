#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using Mask = std::uint32_t;
using Graph = std::vector<Mask>;
using ID = std::array<int, 3>;
using Key = std::tuple<int, bool, int, int, int>;
constexpr int frame_count = 55055;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

Mask bit(int site) { return Mask{1} << site; }
int count(Mask row) { return std::popcount(row); }
Mask full(const Graph& graph) { return bit(static_cast<int>(graph.size())) - 1; }

std::vector<int> sites(Mask mask) {
    std::vector<int> result;
    while (mask) {
        result.push_back(std::countr_zero(mask));
        mask &= mask - 1;
    }
    return result;
}

std::vector<Graph> load_graphs(const std::string& path, int order, std::size_t expected) {
    std::ifstream stream(path);
    require(bool(stream), "cannot open graph6 input");
    std::set<std::string> seen;
    std::vector<Graph> result;
    const int bits = order * (order - 1) / 2;
    for (std::string line; std::getline(stream, line);) {
        require(line.size() == 1 + static_cast<unsigned>((bits + 5) / 6) &&
                line.front() == 63 + order, "bad graph6 length/order");
        require(std::all_of(line.begin(), line.end(), [](unsigned char chr) {
            return chr >= 63 && chr <= 126;
        }), "bad graph6 character");
        require(((line.back() - 63) & ((1 << ((6 - bits % 6) % 6)) - 1)) == 0,
                "bad graph6 pad bits");
        require(seen.insert(line).second, "duplicate literal graph6 host");
        Graph graph(order);
        int position = 0;
        for (int high = 0; high < order; ++high) for (int low = 0; low < high; ++low, ++position) {
            if ((line[1 + position / 6] - 63) & (1 << (5 - position % 6))) {
                graph[low] |= bit(high);
                graph[high] |= bit(low);
            }
        }
        result.push_back(std::move(graph));
    }
    require(stream.eof() && !stream.bad() && result.size() == expected, "graph6 stream/count");
    return result;
}

struct Frame {
    int cross_stubs;
    bool neutral_edge;
    std::array<int, 2> neutral_private_degrees;
    int neutral_codegree;

    Key destination(int flip) const {
        return {cross_stubs, neutral_edge, neutral_private_degrees[flip],
                neutral_private_degrees[1 - flip], neutral_codegree};
    }
};

Frame measure(const Graph& graph, const std::vector<Mask>& marks, int degree) {
    Mask private_sites = 0;
    for (Mask mark : marks) {
        require(!(mark & ~full(graph)) && count(mark) == degree - static_cast<int>(marks.size()),
                "bad mark mask/size");
        private_sites |= mark;
    }
    const auto neutral = sites(full(graph) ^ private_sites);
    require(neutral.size() == 2, "not two physical neutral sites");
    int stubs = 0;
    for (int site : sites(private_sites)) {
        int remaining = degree - count(graph[site]);
        for (Mask mark : marks) remaining -= bool(mark & bit(site));
        require(remaining >= 0, "negative private degree deficit");
        stubs += remaining;
    }
    return {stubs, bool(graph[neutral[0]] & bit(neutral[1])),
            {count(graph[neutral[0]] & private_sites), count(graph[neutral[1]] & private_sites)},
            count(graph[neutral[0]] & graph[neutral[1]] & private_sites)};
}

std::vector<Frame> load_frames(const std::string& path, const std::vector<Graph>& graphs) {
    std::ifstream stream(path);
    require(bool(stream), "cannot open frame input");
    std::set<std::array<int, 5>> seen;
    std::vector<Frame> roster;
    for (std::string line; std::getline(stream, line);) {
        std::istringstream fields(line);
        std::array<int, 5> frame{};
        for (int& value : frame) require(bool(fields >> value), "incomplete frame line");
        std::string extra;
        require(!(fields >> extra), "extra frame column");
        require(frame[0] >= 0 && frame[0] < static_cast<int>(graphs.size()), "invalid host ID");
        require(std::all_of(frame.begin() + 1, frame.end(), [](int value) { return value > 0; }),
                "nonpositive mark");
        auto canonical = frame;
        std::sort(canonical.begin() + 1, canonical.end());
        require(std::adjacent_find(canonical.begin() + 1, canonical.end()) == canonical.end(),
                "repeated frame mark");
        require(seen.insert(canonical).second, "repeated labelled frame ID");
        roster.push_back(measure(graphs[frame[0]], {frame.begin() + 1, frame.end()}, 9));
    }
    require(stream.eof() && !stream.bad() && roster.size() == frame_count, "frame stream/count");
    return roster;
}

template <typename Emit>
void enumerate(const std::vector<Frame>& frames, int low, int high, int degree, int cap, Emit emit) {
    std::map<Key, std::vector<std::array<int, 2>>> rights;
    for (int right = 0; right < static_cast<int>(frames.size()); ++right)
        for (int flip : {0, 1}) rights[frames[right].destination(flip)].push_back({right, flip});
    for (int left = low; left < high; ++left) {
        auto frame = frames.at(left);
        int remaining = degree - frame.neutral_edge;
        int first = remaining - frame.neutral_private_degrees[0];
        int second = remaining - frame.neutral_private_degrees[1];
        const Key low_key{frame.cross_stubs, frame.neutral_edge, first, second, 0};
        const Key high_key{frame.cross_stubs, frame.neutral_edge, first, second,
                           cap - frame.neutral_codegree};
        if (high_key < low_key) continue;
        using Cursor = std::vector<std::array<int, 2>>::const_iterator;
        std::array<std::pair<Cursor, Cursor>, 32> lists;
        std::size_t used = 0;
        for (auto bucket = rights.lower_bound(low_key); bucket != rights.end() && bucket->first <= high_key;
             ++bucket) lists.at(used++) = {bucket->second.begin(), bucket->second.end()};
        while (used > 0) {
            std::size_t best = 0;
            for (std::size_t index = 1; index < used; ++index)
                if (*lists[index].first < *lists[best].first) best = index;
            const auto [right, flip] = *lists[best].first++;
            emit(ID{left, right, flip});
            if (lists[best].first == lists[best].second) lists[best] = lists[--used];
        }
    }
}

Graph induced(const Graph& graph, const std::vector<int>& subset) {
    Graph sub(subset.size());
    for (unsigned hi = 0; hi < subset.size(); ++hi) for (unsigned lo = 0; lo < hi; ++lo) {
        if (graph[subset[hi]] & bit(subset[lo])) {
            sub[hi] |= bit(lo);
            sub[lo] |= bit(hi);
        }
    }
    return sub;
}

void small_control(const std::string& path) {
    std::vector<Frame> frames;
    std::vector<ID> planted;
    int regular = 0, squares = 0, nonempty_crossings = 0;
    for (const Graph& graph : load_graphs(path, 22, 191)) {
        if (!std::all_of(graph.begin(), graph.end(), [](Mask row) { return count(row) == 6; })) continue;
        ++regular;
        for (int one = 0; one < 22; ++one) for (int two = one + 1; two < 22; ++two) {
            const auto common = sites(graph[one] & graph[two]);
            for (unsigned first = 0; first < common.size(); ++first)
            for (unsigned second = first + 1; second < common.size(); ++second) {
                ++squares;
                const std::array<std::array<int, 2>, 2> roots{{{one, two}, {common[first], common[second]}}};
                std::array<Mask, 2> privates{};
                Mask exterior = full(graph);
                for (int side : {0, 1}) for (int root : roots[side]) exterior &= ~bit(root);
                for (int side : {0, 1})
                    privates[side] = exterior & (graph[roots[side][0]] | graph[roots[side][1]]);
                const auto neutral = sites(exterior & ~(privates[0] | privates[1]));
                if ((privates[0] & privates[1]) || neutral.size() != 2 ||
                    count(privates[0]) != 8 || count(privates[1]) != 8) continue;
                int crossings = 0;
                for (int site : sites(privates[0])) crossings += count(graph[site] & privates[1]);
                nonempty_crossings += crossings > 0;
                int left = static_cast<int>(frames.size());
                for (int side : {0, 1}) for (int swap : {0, 1}) {
                    auto window = sites(privates[side]);
                    window.push_back(neutral[swap]);
                    window.push_back(neutral[1 - swap]);
                    std::vector<Mask> marks(2);
                    for (int anchor : {0, 1}) for (unsigned site = 0; site < window.size(); ++site)
                        if (graph[roots[side][anchor]] & bit(window[site])) marks[anchor] |= bit(site);
                    frames.push_back(measure(induced(graph, window), marks, 6));
                    require(frames.back().cross_stubs == crossings, "planted private stubs");
                }
                planted.insert(planted.end(), {{left, left + 2, 0}, {left, left + 3, 1},
                                               {left + 1, left + 2, 1}, {left + 1, left + 3, 0}});
            }
        }
    }
    require(regular == 10 && squares == 2118 && nonempty_crossings > 0, "smaller control inventory");
    std::vector<ID> fast, direct;
    enumerate(frames, 0, static_cast<int>(frames.size()), 6, 4, [&](const ID& id) { fast.push_back(id); });
    for (int left = 0; left < static_cast<int>(frames.size()); ++left)
    for (int right = 0; right < static_cast<int>(frames.size()); ++right) for (int flip : {0, 1}) {
        auto source = frames[left];
        auto target = frames[right];
        if (source.neutral_edge != target.neutral_edge || source.cross_stubs != target.cross_stubs) continue;
        if (source.neutral_codegree + target.neutral_codegree > 4) continue;
        if (source.neutral_edge + source.neutral_private_degrees[0] + target.neutral_private_degrees[flip] != 6 ||
            source.neutral_edge + source.neutral_private_degrees[1] + target.neutral_private_degrees[1-flip] != 6)
            continue;
        direct.push_back({left, right, flip});
    }
    require(fast == direct, "grouped and literal smaller rosters differ");
    for (const auto& id : planted)
        require(std::binary_search(fast.begin(), fast.end(), id), "missing planted alignment");
    std::cout << "regular=" << regular << " oriented_squares=" << squares << " frames=" << frames.size()
              << " planted=" << planted.size() << " nonempty_planted_squares=" << nonempty_crossings
              << " exact_smaller_headers=" << fast.size() << '\n';
}

int main(int argc, char** argv) try {
    if (argc == 3 && std::string(argv[1]) == "control") {
        small_control(argv[2]);
        return 0;
    }
    const bool packed = argc == 6 && std::string(argv[5]) == "packed";
    require(argc == 5 || packed, "usage: headers GRAPH6 FRAMES LOW HIGH [packed] or headers control SMALL_GRAPH6");
    auto bound = [](const std::string& token) {
        int value = -1;
        const auto result = std::from_chars(token.data(), token.data() + token.size(), value);
        require(result.ec == std::errc{} && result.ptr == token.data() + token.size(), "invalid interval bound");
        return value;
    };
    int low = bound(argv[3]), high = bound(argv[4]);
    require(0 <= low && low < high && high <= frame_count, "invalid half-open shard");
    auto frames = load_frames(argv[2], load_graphs(argv[1], 17, 7));
    std::ios::sync_with_stdio(false);
    std::string buffer;
    buffer.reserve((1 << 20) + 64);
    std::array<std::uint64_t, 2> totals{};
    enumerate(frames, low, high, 9, 5, [&](const ID& id) {
        ++totals[id[2]];
        if (packed) {
            for (int value : {id[0], id[1], id[2], 0}) {
                buffer.push_back(static_cast<char>(value & 255));
                buffer.push_back(static_cast<char>((value >> 8) & 255));
            }
        } else {
            for (int index = 0; index < 3; ++index) {
                char digits[12];
                auto end = std::to_chars(digits, digits + sizeof(digits), id[index]).ptr;
                buffer.append(digits, end);
                buffer.push_back(index == 2 ? '\n' : ' ');
            }
        }
        if (buffer.size() >= 1 << 20) {
            std::cout.write(buffer.data(), buffer.size());
            buffer.clear();
        }
    });
    std::cout.write(buffer.data(), buffer.size());
    std::cout.flush();
    require(bool(std::cout), "roster output failure");
    std::cerr << low << ' ' << high << ' ' << totals[0] << ' ' << totals[1] << '\n';
    return 0;
} catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 2;
}
