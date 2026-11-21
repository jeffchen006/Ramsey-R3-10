#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>

using Mask = uint32_t;

int take(Mask& mask) {
    int vertex = std::countr_zero(mask);
    mask &= mask - 1;
    return vertex;
}

class Replay {
public:
    Replay(int width, int privates, int deleted)
        : width(width), privates(privates), order(2 * width + width * privates + width * (width - 1) / 2 - deleted) {
        if (width < 2 || width > 5 || privates < 0 || privates > 10 || deleted < 0 || order <= 2 * width || order > 28)
            throw std::logic_error("bad mark dimensions");
        all = (Mask{1} << order) - 1;
    }

    void read(const std::string& line) {
        if (line.size() != size_t(1 + (order * (order - 1) / 2 + 5) / 6) || line[0] != 63 + order)
            throw std::runtime_error("wrong graph6 order or length");
        neighbors.fill(0);
        int position = 0;
        for (size_t index = 1; index < line.size(); ++index)
            if (line[index] < 63 || line[index] > 126) throw std::runtime_error("bad graph6 byte");
        for (int right = 1; right < order; ++right) {
            for (int left = 0; left < right; ++left, ++position) {
                if ((line[1 + position / 6] - 63) & (32 >> (position % 6))) {
                    neighbors[left] |= Mask{1} << right;
                    neighbors[right] |= Mask{1} << left;
                }
            }
        }
        if (position % 6 && ((line.back() - 63) & ((1 << (6 - position % 6)) - 1)))
            throw std::runtime_error("bad graph6 padding");
        ++count_rows;
        found.clear();
        independent(all, 2 * width - 1, 0);
        for (const auto& [first, second] : found)
            std::cout << count_rows << ' ' << first << ' ' << second << ' ' << line << '\n';
        count_marks += found.size();
        count_matched += !found.empty();
    }

    void summary() const {
        std::cerr << "rows=" << count_rows << " independent=" << count_independent << " endpoints=" << count_endpoint
                  << " marks=" << count_marks << " matched_rows=" << count_matched << '\n';
    }

private:
    int width, privates, order;
    Mask all;
    std::array<Mask, 28> neighbors{};
    std::set<std::pair<Mask, Mask>> found;
    uint64_t count_rows = 0, count_independent = 0, count_endpoint = 0, count_marks = 0, count_matched = 0;

    bool signatures(Mask side, Mask outside) const {
        std::array<int, 28> single{};
        std::array<Mask, 28> pairs{};
        while (outside) {
            Mask contact = neighbors[take(outside)] & side;
            int size = std::popcount(contact);
            if (size == 0 || size > 2) return false;
            int anchor = take(contact);
            if (size == 1) {
                if (++single[anchor] > privates) return false;
            } else {
                if (pairs[anchor] & contact) return false;
                pairs[anchor] |= contact;
            }
        }
        return true;
    }

    void split(Mask independent_set, int endpoint, Mask options, int remaining, Mask first) {
        if (!remaining) {
            Mask other = (independent_set ^ first) | (Mask{1} << endpoint);
            if (first > other) return;
            Mask outside = all ^ (first | other);
            if (signatures(first, outside) && signatures(other, outside))
                found.emplace(first, other);
            return;
        }
        while (std::popcount(options) >= remaining) {
            int vertex = take(options);
            split(independent_set, endpoint, options, remaining - 1, first | (Mask{1} << vertex));
        }
    }

    void visit(Mask independent_set) {
        ++count_independent;
        Mask singleton = 0;
        for (Mask outside = all ^ independent_set; outside;) {
            int vertex = take(outside);
            int contacts = std::popcount(neighbors[vertex] & independent_set);
            if (!contacts || contacts > 4) return;
            if (contacts == 1) singleton |= Mask{1} << vertex;
        }
        for (Mask options = singleton; options;) {
            int endpoint = take(options);
            Mask incident = Mask{1} << endpoint;
            if ((singleton ^ incident) & ~neighbors[endpoint]) continue;
            ++count_endpoint;
            Mask partner = neighbors[endpoint] & independent_set;
            split(independent_set, endpoint, independent_set ^ partner, width - 1, partner);
        }
    }

    void independent(Mask options, int remaining, Mask selected) {
        if (!remaining) {
            visit(selected);
            return;
        }
        while (std::popcount(options) >= remaining) {
            int vertex = take(options);
            independent(options & ~neighbors[vertex], remaining - 1, selected | (Mask{1} << vertex));
        }
    }
};

int main(int argc, char** argv) {
    if (argc != 4) return 2;
    try {
        std::ios::sync_with_stdio(false);
        std::cin.tie(nullptr);
        Replay replay(std::stoi(argv[1]), std::stoi(argv[2]), std::stoi(argv[3]));
        std::string line;
        while (std::getline(std::cin, line)) replay.read(line);
        replay.summary();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
