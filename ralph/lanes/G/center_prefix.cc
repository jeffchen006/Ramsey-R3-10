#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>

using Mask = uint32_t;
using Row = std::vector<Mask>;
constexpr Mask bit(int index) { return Mask{1} << index; }
int pop(Mask &mask) { int index = std::countr_zero(mask); mask &= mask - 1; return index; }
int count(Mask mask) { return std::popcount(mask); }

struct Hall {
    const Row &support;
    const Row &palettes;
    int alpha;

    bool augment(int vertex, Mask palette, Mask &visited, std::array<int, 32> &mates) const {
        Mask candidates = support[vertex] & palette & ~visited;
        while (candidates) {
            int index = pop(candidates);
            if (visited & bit(index)) continue;
            visited |= bit(index);
            if (mates[index] < 0 || augment(mates[index], palette, visited, mates)) {
                mates[index] = vertex;
                return true;
            }
        }
        return false;
    }

    bool matching(Mask clique, Mask palette) const {
        int spare = alpha - count(palette);
        if (count(clique) <= spare) return true;
        std::array<int, 32> mates;
        mates.fill(-1);
        while (clique) {
            Mask visited = 0;
            if (!augment(pop(clique), palette, visited, mates) && --spare < 0) return false;
        }
        return true;
    }

    bool cliques(const Row &conflict, Mask clique, Mask options, Mask skipped = 0) const {
        if (!(options | skipped)) {
            return std::all_of(palettes.begin(), palettes.end(), [&](Mask palette) { return matching(clique, palette); });
        }
        Mask pivot = 0;
        int largest = -1;
        for (Mask candidates = options | skipped; candidates; ) {
            Mask neighbours = conflict[pop(candidates)];
            int degree = count(neighbours & options);
            if (degree > largest) { pivot = neighbours; largest = degree; }
        }
        for (Mask candidates = options & ~pivot; candidates; ) {
            int vertex = pop(candidates);
            Mask neighbours = conflict[vertex];
            if (!cliques(conflict, clique | bit(vertex), options & neighbours, skipped & neighbours)) return false;
            options ^= bit(vertex);
            skipped |= bit(vertex);
        }
        return true;
    }

    bool infer(Row &forbid, Row &force) const {
        bool changed = true;
        Mask all = bit(support.size()) - 1;
        while (changed) {
            changed = false;
            for (size_t vertex = 0; vertex < support.size(); ++vertex) {
                Mask extra = 0;
                for (Mask rest = force[vertex]; rest; ) extra |= force[pop(rest)];
                extra &= ~(bit(vertex) | forbid[vertex]);
                if (extra & force[vertex]) return false;
                if (extra) changed = true;
                forbid[vertex] |= extra;
                while (extra) forbid[pop(extra)] |= bit(vertex);
            }
            if (!cliques(forbid, 0, all)) return false;
            for (size_t left = 0; left < support.size(); ++left) {
                for (Mask options = (bit(left) - 1) & ~(force[left] | forbid[left]); options; ) {
                    int right = pop(options);
                    if (!cliques(forbid, bit(left) | bit(right), forbid[left] & forbid[right])) {
                        changed = true;
                        force[left] |= bit(right);
                        force[right] |= bit(left);
                    }
                }
            }
        }
        return true;
    }
};

Row conflicts(const Row &support) {
    Row result(support.size());
    for (size_t left = 0; left < support.size(); ++left) for (size_t right = 0; right < left; ++right) {
        if (support[left] & support[right]) { result[left] |= bit(right); result[right] |= bit(left); }
    }
    return result;
}

struct Prefix {
    static constexpr Mask full = 31, star = 1, centre = 2;
    static constexpr int width = 5;
    const Row palettes{1023 ^ star, 1023 ^ (star << width)};
    const Row first{centre, centre, centre, centre, centre | 8, centre | 16};
    Row support, clash, second;
    std::array<int, 32> left{}, right{};
    std::array<uint64_t, 13> visits{}, bad_hall{};
    uint64_t roots{}, selected{}, leaves{}, bad_force{}, bad_cross{}, bad_budget[2]{}, high[2][2]{};
    uint64_t skip{}, cap{};
    int shared_filter;

    explicit Prefix(int shared, uint64_t offset, uint64_t limit) : skip(offset), cap(limit), shared_filter(shared) {
        for (int label = 0; label < width; ++label) left[bit(label)] = 4;
        for (int right_label = 0; right_label < width; ++right_label) {
            for (int left_label = 0; left_label < right_label; ++left_label) {
                Mask mask = bit(left_label) | bit(right_label);
                if (mask != (star | centre) && mask != (centre | 4)) left[mask] = 1;
            }
        }
        right = left;
        for (Mask mask : first) --left[mask];
    }

    bool push(Mask edge) {
        int size = support.size();
        Mask neighbours = 0;
        for (int index = 0; index < size; ++index) if (support[index] & edge) {
            neighbours |= bit(index);
            clash[index] |= bit(size);
        }
        support.push_back(edge);
        clash.push_back(neighbours);
        ++visits[size + 1];
        if (Hall{support, palettes, 9}.cliques(clash, bit(size), neighbours)) return true;
        ++bad_hall[size + 1];
        undo();
        return false;
    }

    void undo() {
        Mask earlier = bit(support.size() - 1) - 1;
        support.pop_back();
        clash.pop_back();
        for (auto &mask : clash) mask &= earlier;
    }

    bool leaf(int shared) {
        ++leaves;
        Row forbidden = clash, forced(support.size());
        if (!Hall{support, palettes, 9}.infer(forbidden, forced)) { ++bad_force; return false; }
        Mask left_only = 0;
        for (size_t vertex = 0; vertex < first.size(); ++vertex) {
            if (!(support[vertex] & (centre << width))) left_only |= bit(vertex);
        }
        Mask right_only = (bit(support.size()) - 1) ^ (bit(first.size()) - 1);
        int cross_cap = 0;
        for (Mask rest = left_only | right_only; rest; ) {
            int vertex = pop(rest);
            Mask opposite = left_only & bit(vertex) ? right_only : left_only;
            int choices = count(opposite & ~forbidden[vertex]);
            if (!choices) { ++bad_cross; return false; }
            if (opposite == right_only) cross_cap += choices;
        }
        int singles = 0, mark_lb[2]{8, 8};
        std::array<int, 10> degrees{8, 0, 7, 7, 7, 8, 0, 7, 7, 7};
        for (Mask mask : support) {
            Mask side_a = mask & full, side_b = mask >> width;
            bool in_a = side_a & centre, in_b = side_b & centre;
            if (count(mask) == 2) ++singles;
            if (!in_a) for (Mask rest = side_a; rest; ) --degrees[pop(rest)];
            if (!in_b) for (Mask rest = side_b; rest; ) --degrees[width + pop(rest)];
        }
        for (int label = 0; label < 10; ++label) if (label % width != 1) {
            mark_lb[label / width] = std::min(mark_lb[label / width], degrees[label]);
        }
        for (int profile = 0; profile < 2; ++profile) {
            int twos = std::min(singles, 6 - profile);
            int ones = std::min(static_cast<int>(support.size()) - twos, 2 * profile);
            int max_deficit = 2 * twos + ones;
            int edge_floor = shared == 1 ? 65 : 73;
            if (49 + 9 * shared + max_deficit + cross_cap < edge_floor) { ++bad_budget[profile]; continue; }
            if (std::min(mark_lb[0], mark_lb[1]) >= shared + 2) ++high[shared - 1][profile];
        }
        return true;
    }

    void row_b(size_t index, Mask previous, Mask covered, int shared) {
        if (index == second.size()) {
            if (covered == full) leaf(shared);
            return;
        }
        Mask minimum = index && second[index - 1] == second[index] ? previous : 1;
        for (Mask mask = minimum; mask <= full; ++mask) {
            if (!left[mask] || ((mask & star) && (second[index] & star))) continue;
            --left[mask];
            if (push(mask | (second[index] << width))) {
                row_b(index + 1, mask, covered | mask, shared);
                undo();
            }
            ++left[mask];
        }
    }

    void row_a(size_t index, Mask previous, Mask covered, int shared, Mask union_a) {
        if (index == first.size()) {
            if (covered != full || shared != shared_filter) return;
            ++roots;
            if (roots <= skip || selected >= cap) return;
            ++selected;
            second.clear();
            for (Mask mask = 1; mask <= full; ++mask) if (mask & centre) {
                for (int repeat = 0; repeat < right[mask]; ++repeat) second.push_back(mask);
            }
            row_b(0, 0, union_a, shared);
            return;
        }
        Mask minimum = index && first[index - 1] == first[index] ? previous : 1;
        for (Mask mask = minimum; mask <= full; ++mask) {
            bool overlap = mask & centre;
            int now = shared + overlap;
            if (!right[mask] || now > shared_filter || now + first.size() - index - 1 < static_cast<size_t>(shared_filter)) continue;
            --right[mask];
            if (push(first[index] | (mask << width))) {
                row_a(index + 1, mask, covered | mask, now, union_a | (overlap ? first[index] : 0));
                undo();
            }
            ++right[mask];
        }
    }

    void run() {
        row_a(0, 0, 0, 0, 0);
        for (size_t index = 1; index < visits.size(); ++index) if (visits[index]) {
            std::cout << "depth " << index << ' ' << visits[index] << " hall_reject " << bad_hall[index] << '\n';
        }
        std::cout << "shared " << shared_filter << " offset " << skip << " first " << roots << " selected " << selected
                  << " centre_tables " << leaves << " force_reject " << bad_force << " cross_reject " << bad_cross << '\n';
        for (size_t profile = 0; profile < 2; ++profile) {
            std::cout << "profile " << profile << " budget_reject " << bad_budget[profile]
                      << " marks_high_min " << high[shared_filter - 1][profile] << '\n';
        }
    }
};

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "control") {
        int order, alpha, count_palettes;
        while (std::cin >> order >> alpha >> count_palettes) {
            if (order < 0 || order >= 32 || count_palettes < 0) return 2;
            Row support(order), palettes(count_palettes), forced(order);
            for (auto &mask : support) std::cin >> mask;
            for (auto &mask : palettes) std::cin >> mask;
            Row forbidden = conflicts(support);
            bool ok = Hall{support, palettes, alpha}.infer(forbidden, forced);
            std::cout << ok;
            if (ok) {
                for (Mask mask : forced) std::cout << ' ' << mask;
                for (Mask mask : forbidden) std::cout << ' ' << mask;
            }
            std::cout << '\n';
        }
        return 0;
    }
    if (argc != 4) return 2;
    int shared = std::atoi(argv[1]);
    if (shared != 1 && shared != 2) return 2;
    Prefix(shared, std::strtoull(argv[2], nullptr, 10), std::strtoull(argv[3], nullptr, 10)).run();
}
