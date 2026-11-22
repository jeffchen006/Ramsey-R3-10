#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

using Mask = uint32_t;

int size(Mask mask) { return __builtin_popcount(mask); }
int pop(Mask &mask) {
    int index = __builtin_ctz(mask);
    mask &= mask - 1;
    return index;
}

struct Scan {
    int width, privates, deleted, order = 0;
    bool paired, rooted;
    Mask universe = 0, other_forbidden = 0, other_hits = 0;
    std::array<Mask, 28> adj{};
    std::array<Mask, 28> compatible{};
    Mask candidates = 0, cached = 0;
    int touch_target = 0;
    std::string line;
    uint64_t rows = 0, independent = 0, undominated = 0, first_support = 0;
    uint64_t opposite = 0, marks = 0, matched_rows = 0;

    void decode() {
        order = line.at(0) - 63;
        if (order < 1 || order > 28 || (int)line.size() != 1 + (order*(order-1)/2+5)/6)
            throw std::runtime_error("bad graph6 order or length");
        universe = (Mask{1} << order) - 1;
        adj.fill(0);
        int index = 0;
        for (int right = 1; right < order; ++right)
            for (int left = 0; left < right; ++left, ++index) {
                int code = line[1 + index/6] - 63;
                if (code < 0 || code > 63) throw std::runtime_error("bad graph6 byte");
                if ((code >> (5-index%6)) & 1) {
                    adj[left] |= Mask{1} << right;
                    adj[right] |= Mask{1} << left;
                }
            }
    }

    bool support_ok(Mask anchors, Mask exterior) const {
        std::array<int, 28> singleton{};
        std::array<Mask, 28> doubles{};
        while (exterior) {
            Mask support = adj[pop(exterior)] & anchors;
            if (!support) return false;
            int first = pop(support);
            if (!support) {
                if (++singleton[first] > privates) return false;
            } else {
                if ((support & (support - 1)) || (doubles[first] & support)) return false;
                doubles[first] |= support;
            }
        }
        return true;
    }

    void emit(Mask anchors, Mask other) {
        if (paired && anchors > other) std::swap(anchors, other);
        ++marks;
        std::cout << rows << ' ' << anchors << ' ' << other << ' ' << line << '\n';
    }

    void leaf(Mask anchors, Mask touched) {
        ++independent;
        Mask uncovered = universe & ~(anchors | touched);
        if (size(uncovered) != (paired ? width-1 : 0)) return;
        ++undominated;
        if (!paired) {
            if (support_ok(anchors, touched)) {
                ++first_support;
                emit(anchors, 0);
            }
            return;
        }
        Mask hits = 0;
        if (uncovered & other_forbidden) return;
        for (Mask rest = uncovered; rest; ) hits |= adj[pop(rest)];
        if (hits & uncovered) return;
        Mask choices = touched & ~hits & ~other_forbidden;
        if (other_hits && !(uncovered & other_hits)) choices &= other_hits;
        while (choices) {
            int star = pop(choices);
            Mask star_bit = Mask{1} << star;
            if (size(adj[star] & anchors) != 1) continue;
            Mask other = uncovered | star_bit;
            if (!rooted && other <= anchors) continue;
            ++opposite;
            Mask exterior = touched ^ star_bit;
            if (!support_ok(anchors, exterior)) continue;
            ++first_support;
            if (support_ok(other, exterior)) emit(anchors, other);
        }
    }

    Mask peers(int vertex) {
        Mask vertex_bit = Mask{1} << vertex;
        if (cached & vertex_bit) return compatible[vertex];
        cached |= vertex_bit;
        Mask remaining = candidates & ~(vertex_bit | adj[vertex]);
        Mask matches = 0;
        while (remaining) {
            int peer = pop(remaining);
            if (size(adj[peer] & adj[vertex]) <= 1) matches |= Mask{1} << peer;
        }
        compatible[vertex] = matches;
        return matches;
    }

    void search(Mask options, int left, Mask anchors, Mask touched, Mask twice = 0) {
        int touched_count = size(touched);
        if (touched_count > touch_target || touched_count + left * (privates+width-1+paired) < touch_target) return;
        while (size(options) >= left) {
            int vertex = pop(options);
            if (adj[vertex] & twice) continue;
            Mask now = touched | adj[vertex], marks_now = anchors | (Mask{1} << vertex);
            if (left == 1) {
                if (size(now) == touch_target) leaf(marks_now, now);
                continue;
            }
            search(options & peers(vertex), left-1, marks_now, now, twice | (touched & adj[vertex]));
        }
    }

    void scan() {
        decode();
        if (order != width*(paired ? 2 : 1) + width*privates + width*(width-1)/2 - deleted)
            throw std::runtime_error("wrong order for mark parameters");
        candidates = 0;
        cached = 0;
        touch_target = order - width - (paired ? width-1 : 0);
        int base = privates + width-1;
        for (int vertex = 0; vertex < order; ++vertex) {
            int degree = size(adj[vertex]);
            if (degree >= base-deleted && degree <= base+paired) candidates |= Mask{1} << vertex;
        }
        uint64_t before = marks;
        if (!rooted) {
            search(candidates, width, 0, 0);
        } else {
            int root = order-1;
            Mask root_bit = Mask{1} << root;
            other_hits = 0;
            other_forbidden = 0;
            if (candidates & root_bit)
                search(peers(root), width-1, root_bit, adj[root]);
            other_forbidden = root_bit;
            other_hits = adj[root];
            for (Mask rest = adj[root]; rest; ) {
                int pivot = pop(rest);
                Mask pivot_bit = Mask{1} << pivot;
                if (candidates & pivot_bit)
                    search(peers(pivot) & ~other_forbidden, width-1, pivot_bit, adj[pivot]);
                other_forbidden |= pivot_bit;
            }
            other_forbidden = other_hits = 0;
        }
        matched_rows += marks != before;
    }
};

int main(int argc, char **argv) {
    if ((argc != 5 && argc != 6) || (std::string(argv[1]) != "pair" && std::string(argv[1]) != "single")) return 2;
    Scan scanner{};
    scanner.paired = std::string(argv[1]) == "pair";
    scanner.width = std::stoi(argv[2]);
    scanner.privates = std::stoi(argv[3]);
    scanner.deleted = std::stoi(argv[4]);
    scanner.rooted = argc == 6;
    if (scanner.rooted && (std::string(argv[5]) != "rooted" || !scanner.paired)) return 2;
    if (scanner.width < 2 || scanner.width > 5 || scanner.privates < 0 || scanner.deleted < 0 ||
        scanner.deleted > scanner.width*scanner.privates + scanner.width*(scanner.width-1)/2) return 2;
    while (std::getline(std::cin, scanner.line)) {
        if (!scanner.line.empty() && scanner.line.back() == '\r') scanner.line.pop_back();
        if (scanner.line == ">>graph6<<") continue;
        ++scanner.rows;
        scanner.scan();
    }
    std::cerr << "rows=" << scanner.rows << " independent=" << scanner.independent
              << " undominated=" << scanner.undominated << " opposite=" << scanner.opposite
              << " first_support=" << scanner.first_support << " marks=" << scanner.marks
              << " matched_rows=" << scanner.matched_rows << '\n';
}
