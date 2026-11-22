#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

using Mask = uint32_t;

int pop_first(Mask& mask) {
    int vertex = std::countr_zero(mask);
    mask &= mask - 1;
    return vertex;
}

struct Scan {
    int first_width, second_width, singles;
    bool private_deficit;
    Mask universe;
    std::array<Mask, 31> adj{};
    uint64_t rows = 0, independent = 0, preliminary = 0, results = 0;
    std::string encoded;

    bool independent_set(Mask vertices) const {
        Mask copy = vertices;
        while (copy) if (adj[pop_first(copy)] & vertices) return false;
        return true;
    }

    bool supports(Mask side, Mask outside) const {
        std::array<int, 31> counted{};
        std::array<Mask, 31> doubles{};
        while (outside) {
            Mask hits = adj[pop_first(outside)] & side;
            if (!hits) return false;
            int first = pop_first(hits);
            if (!hits) {
                if (++counted[first] > singles) return false;
            } else {
                if ((hits & (hits - 1)) || (doubles[first] & hits)) return false;
                doubles[first] |= hits;
            }
        }
        return true;
    }

    void finish(Mask side, Mask reach) {
        ++independent;
        Mask untouched = universe & ~(side | reach);
        if (std::popcount(untouched) != second_width - 1 || !independent_set(untouched)) return;
        for (Mask choices = reach; choices;) {
            int cross = pop_first(choices);
            Mask smaller_contact = adj[cross] & side;
            if (std::popcount(smaller_contact) != 1 || (adj[cross] & untouched)) continue;
            if (private_deficit && std::popcount(adj[std::countr_zero(smaller_contact)]) != 6) continue;
            ++preliminary;
            Mask cross_bit = Mask{1} << cross;
            Mask outside = reach ^ cross_bit;
            if (!supports(side, outside) || !supports(untouched | cross_bit, outside)) continue;
            ++results;
            std::cout << rows << ' ' << side << ' ' << (untouched | cross_bit) << ' ' << encoded << '\n';
        }
    }

    void search(Mask candidates, Mask side, Mask reach, int needed) {
        while (std::popcount(candidates) >= needed) {
            int vertex = pop_first(candidates);
            Mask extended = side | (Mask{1} << vertex);
            Mask new_reach = reach | adj[vertex];
            if (needed == 1) finish(extended, new_reach);
            else search(candidates & ~adj[vertex], extended, new_reach, needed - 1);
        }
    }

    void graph() {
        int order = encoded.at(0) - 63;
        if (order < 1 || order > 30 || (int)encoded.size() != 1 + (order*(order-1)/2+5)/6)
            throw std::runtime_error("bad graph6");
        if (private_deficit && (order != 21 || first_width != 3 || second_width != 4 || singles != 4))
            throw std::runtime_error("invalid single-deficit scope");
        adj.fill(0);
        int index = 0;
        for (int right = 0; right < order; ++right) {
            for (int left = 0; left < right; ++left, ++index) {
                int code = encoded[1 + index/6] - 63;
                if (code < 0 || code > 63) throw std::runtime_error("bad graph6 bit");
                if ((code >> (5-index%6)) & 1) {
                    adj[left] |= Mask{1} << right;
                    adj[right] |= Mask{1} << left;
                }
            }
        }
        universe = (Mask{1} << order) - 1;
        Mask candidates = universe;
        if (private_deficit) {
            for (int vertex = 0; vertex < order; ++vertex) {
                if (std::popcount(adj[vertex]) < 5) candidates ^= Mask{1} << vertex;
            }
        }
        ++rows;
        search(candidates, 0, 0, first_width);
    }
};

int main(int argc, char** argv) {
    if (argc != 4 && argc != 5) return 2;
    Scan scan{};
    scan.first_width = std::stoi(argv[1]);
    scan.second_width = std::stoi(argv[2]);
    scan.singles = std::stoi(argv[3]);
    scan.private_deficit = argc == 5;
    if (scan.first_width < 1 || scan.second_width < 1 || scan.singles < 1 ||
        (scan.private_deficit && std::string(argv[4]) != "one-deficit")) return 2;
    while (std::getline(std::cin, scan.encoded)) scan.graph();
    std::cerr << "rows " << scan.rows << " independent " << scan.independent
              << " preliminary " << scan.preliminary << " results " << scan.results << '\n';
}
