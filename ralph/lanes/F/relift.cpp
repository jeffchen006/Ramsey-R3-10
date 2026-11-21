#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using Mask = uint64_t;
using Form = __uint128_t;
constexpr Form RHS = Form(1) << 127;
constexpr int MAXF = 24;

Mask bit(int index) { return Mask(1) << index; }
Form var(int index) { return Form(1) << index; }
int take(Mask& mask) {
    int index = std::countr_zero(mask);
    mask &= mask - 1;
    return index;
}
int top(Form form) {
    auto hi = Mask(form >> 64);
    return hi ? 127 - std::countl_zero(hi) : 63 - std::countl_zero(Mask(form));
}
bool parity(Form form) {
    return (std::popcount(Mask(form)) ^ std::popcount(Mask(form >> 64))) & 1;
}

struct Basis {
    std::array<Form, 127> rows{};
    int rank = 0;
    Form reduce(Form form) const {
        Form pending = form & ~RHS;
        while (pending) {
            int pivot = top(pending);
            if (rows[pivot]) {
                form ^= rows[pivot];
                pending ^= rows[pivot] & ~RHS;
            } else pending ^= var(pivot);
        }
        return form;
    }
    void insert_reduced(Form form) {
        if (form & ~RHS) {
            rows[top(form & ~RHS)] = form;
            ++rank;
        } else if (form) throw std::logic_error("inconsistent basis");
    }
    void insert(Form form) { insert_reduced(reduce(form)); }
    Form point(Form free_assignment = 0) const {
        Form result = RHS | free_assignment;
        for (int index = 0; index < 127; ++index)
            if (parity(result & rows[index])) result |= var(index);
        return result;
    }
};

struct Pair { int left, right; Form mark; };

struct Quotient {
    int size, edges = 0, triangle_rows = 0;
    std::array<Mask, MAXF> simple{}, occupied{};
    std::array<std::array<Form, MAXF>, MAXF> marks{};
    std::vector<Pair> singles;
    std::array<Mask, 2 * MAXF> frozen{};
    Basis structural;

    void edge(int left, int right) {
        frozen[left] |= bit(right);
        frozen[right] |= bit(left);
        ++edges;
    }
    Quotient(const std::string& text, int min_deg, int max_deg, int min_edges, int max_edges) {
        if (text.empty()) throw std::invalid_argument("empty quotient");
        size = text[0] - 'A';
        if (size < 1 || size > MAXF || int(text.size()) != 1 + size * (size + 1) / 2)
            throw std::invalid_argument("bad quotient order or length");
        int offset = 1;
        std::vector<Mask> doubles(size);
        for (int right = 0; right < size; ++right) {
            for (int left = 0; left < right; ++left) {
                int weight = text[offset++] - '0';
                if (weight < 0 || weight > 2) throw std::invalid_argument("bad weight");
                if (!weight) continue;
                occupied[left] |= bit(right);
                occupied[right] |= bit(left);
                if (weight == 1) {
                    if (singles.size() == 127) throw std::invalid_argument("too many single edges");
                    Form mark = var(int(singles.size()));
                    singles.push_back({left, right, mark});
                    marks[left][right] = marks[right][left] = mark;
                    simple[left] |= bit(right);
                    simple[right] |= bit(left);
                } else {
                    doubles[right] |= bit(left);
                    for (int side = 0; side < 4; ++side)
                        edge(2 * left + (side & 1), 2 * right + (side >> 1));
                }
            }
            char vertical = text[offset++];
            if (vertical == '1') edge(2 * right, 2 * right + 1);
            else if (vertical != '0') throw std::invalid_argument("bad vertical weight");
        }
        edges += 2 * int(singles.size());
        if (edges < min_edges || edges > max_edges) throw std::invalid_argument("edge filter");
        for (int right = 0; right < size; ++right) {
            int deg = std::popcount(frozen[2 * right]) + std::popcount(simple[right]);
            if (deg < min_deg || deg > max_deg) throw std::invalid_argument("degree filter");
            Mask doubles_here = doubles[right];
            while (doubles_here) {
                int left = take(doubles_here);
                if ((occupied[left] & occupied[right]) || (frozen[2 * left] & bit(2 * left + 1)) ||
                    (frozen[2 * right] & bit(2 * right + 1)))
                    throw std::invalid_argument("double-edge triangle");
            }
        }
        Mask roots = bit(size) - 1;
        while (roots) {
            Mask todo = bit(take(roots));
            while (todo) {
                int left = take(todo);
                Mask fresh = simple[left] & roots;
                roots ^= fresh;
                todo |= fresh;
                while (fresh) structural.insert(marks[left][take(fresh)]);
            }
        }
        for (auto [left, right, mark] : singles) {
            Mask thirds = simple[left] & simple[right] & ~(bit(right + 1) - 1);
            while (thirds) {
                int third = take(thirds);
                structural.insert(mark ^ marks[left][third] ^ marks[right][third]);
                ++triangle_rows;
            }
        }
    }

    auto lift(Form point) const {
        auto result = frozen;
        for (auto [left, right, mark] : singles) {
            int crossing = !(point & mark);
            for (int side = 0; side < 2; ++side) {
                int fst = 2 * left + side;
                int snd = 2 * right + (side ^ crossing);
                result[fst] |= bit(snd);
                result[snd] |= bit(fst);
            }
        }
        return result;
    }
};

std::string graph6(const std::array<Mask, 2 * MAXF>& graph, int size) {
    std::string result(1, char(size + 63));
    int used = 0, value = 0;
    for (int right = 1; right < size; ++right) {
        for (int left = 0; left < right; ++left) {
            value = (value << 1) + bool(graph[right] & bit(left));
            if (++used == 6) {
                result += char(63 + value);
                used = value = 0;
            }
        }
    }
    if (used) result += char(63 + (value << (6 - used)));
    return result;
}

struct Support {
    int weight;
    std::vector<Form> eq;
};

struct Search {
    const Quotient& quotient;
    int order, k, ceiling;
    uint64_t cap, nodes = 0, lifts = 0, cuts = 0;
    std::vector<Support> known;
    std::unordered_set<Mask> keys;
    std::array<Mask, 2 * MAXF> nonadj{};
    Form witness = 0;
    int best = -1;

    Search(const Quotient& source, int target, int limit, uint64_t node_limit)
        : quotient(source), order(2 * source.size), k(target), ceiling(limit), cap(node_limit) {}

    int learn(Mask indep) {
        constexpr Mask even = UINT64_C(0x5555555555555555);
        Mask side0 = indep & even, side1 = (indep >> 1) & even;
        Mask support = side0 | side1, full = side0 & side1;
        if (!keys.insert(support | (full << 1)).second) return 0;
        Mask unseen = 0, scan = side0 ^ side1;
        while (scan) unseen |= bit(take(scan) / 2);
        std::array<Form, MAXF> path{};
        Basis cycles;
        int components = 0;
        while (unseen) {
            ++components;
            Mask todo = bit(take(unseen));
            while (todo) {
                int left = take(todo);
                Mask fresh = quotient.simple[left] & unseen;
                unseen ^= fresh;
                todo |= fresh;
                while (fresh) {
                    int right = take(fresh);
                    path[right] = path[left] ^ quotient.marks[left][right];
                }
            }
        }
        scan = side0 ^ side1;
        while (scan) {
            int left = take(scan) / 2;
            Mask neighbors = quotient.simple[left];
            while (neighbors) {
                int right = take(neighbors);
                if ((scan & bit(2 * right)))
                    cycles.insert(quotient.structural.reduce(path[left] ^ path[right] ^ quotient.marks[left][right]));
            }
        }
        Support result{1 << components, {}};
        for (Form row : cycles.rows) if (row) result.eq.push_back(row);
        known.push_back(std::move(result));
        return known.back().weight;
    }

    void discover(Mask remain, Mask chosen, int need, int& score) {
        if (need == 0) {
            score += learn(chosen);
            return;
        }
        for (int count = std::popcount(remain); count >= need && score <= ceiling; --count) {
            int next = take(remain);
            discover(remain & nonadj[next], chosen | bit(next), need - 1, score);
        }
    }

    enum Outcome { no, yes, capped };
    int direct_count(const std::array<Mask, 2 * MAXF>& graph, Mask remain, int need, int budget) {
        if (!need) return 1;
        int sum = 0;
        for (int count = std::popcount(remain); count >= need && sum <= budget; --count) {
            int next = take(remain);
            sum += direct_count(graph, remain & ~graph[next], need - 1, budget - sum);
        }
        return sum;
    }

    Outcome flat(Form assignment, const std::vector<Form>& free, std::size_t index = 0) {
        if (index != free.size()) {
            auto status = flat(assignment, free, index + 1);
            return status == no ? flat(assignment | free[index], free, index + 1) : status;
        }
        if (nodes == cap) return capped;
        ++nodes;
        ++lifts;
        Form point = quotient.structural.point(assignment);
        int score = direct_count(quotient.lift(point), bit(order) - 1, k, ceiling);
        if (score > ceiling) return no;
        witness = point;
        best = score;
        return yes;
    }

    Outcome solve(const Basis& decision) {
        if (nodes == cap) return capped;
        ++nodes;
        Form point = decision.point();
        int score = 0, forced = 0;
        Form split = 0;
        int priority = -1;
        auto inspect = [&](const Support& support) {
            for (Form eq : support.eq) if (parity(point & eq)) return;
            score += support.weight;
            int width = 0;
            Form choice = 0;
            for (Form eq : support.eq) {
                Form reduced = decision.reduce(eq);
                if (reduced) {
                    ++width;
                    choice = reduced;
                }
            }
            if (!width) forced += support.weight;
            else {
                int value = 256 * (support.weight > ceiling) + 4 * std::bit_width(unsigned(support.weight)) - width + 128;
                if (value > priority) {
                    split = choice;
                    priority = value;
                }
            }
        };
        for (const Support& support : known) {
            inspect(support);
            if (forced > ceiling) { ++cuts; return no; }
        }
        if (score <= ceiling) {
            ++lifts;
            auto graph = quotient.lift(point);
            for (int vertex = 0; vertex < order; ++vertex) nonadj[vertex] = ~graph[vertex];
            auto old_size = known.size();
            int discovered = score;
            discover(bit(order) - 1, 0, k, discovered);
            if (discovered <= ceiling) {
                witness = point;
                best = discovered;
                return yes;
            }
            for (auto index = old_size; index < known.size(); ++index) {
                inspect(known[index]);
                if (forced > ceiling) { ++cuts; return no; }
            }
            if (score != discovered) throw std::logic_error("support arithmetic mismatch");
        }
        if (!split || split == RHS) throw std::logic_error("no nonconstant split at overbudget point");
        Basis child = decision;
        child.insert_reduced(split ^ RHS);
        auto status = solve(child);
        if (status != no) return status;
        child = decision;
        child.insert_reduced(split);
        return solve(child);
    }
};

int main(int argc, char** argv) {
    bool flat = argc == 11 && std::string(argv[10]) == "--flat";
    if (argc != 10 && !flat) {
        std::cerr << "usage: relift quotients k ceiling min_deg max_deg min_e max_e node_cap output.tsv [--flat]\n";
        return 2;
    }
    std::ifstream input(argv[1]);
    std::ofstream output(argv[9]);
    if (!input || !output) return 2;
    int target = std::stoi(argv[2]), limit = std::stoi(argv[3]);
    int min_deg = std::stoi(argv[4]), max_deg = std::stoi(argv[5]);
    int min_e = std::stoi(argv[6]), max_e = std::stoi(argv[7]);
    uint64_t cap = std::stoull(argv[8]);
    if (target < 1 || target > 24 || limit < 0 || limit > 1000000000) return 2;
    output << "idx\tscore\tg6\n";
    std::string text;
    int index = 0;
    std::array<int, 4> total{};
    while (std::getline(input, text)) {
        try {
            const Quotient quotient(text, min_deg, max_deg, min_e, max_e);
            Search search(quotient, target, limit, cap);
            std::vector<Form> free;
            if (flat)
                for (int variable = 0; variable < int(quotient.singles.size()); ++variable)
                    if (!quotient.structural.rows[variable]) free.push_back(var(variable));
            auto status = flat ? search.flat(0, free) : search.solve(quotient.structural);
            ++total[status];
            std::cout << "row=" << index << " status=" << (status == Search::yes ? "yes" : status == Search::no ? "no" : "cap")
                      << " e=" << quotient.edges << " triangles=" << quotient.triangle_rows
                      << " free=" << int(quotient.singles.size()) - quotient.structural.rank
                      << " nodes=" << search.nodes << " lifts=" << search.lifts << " cuts=" << search.cuts
                      << " terms=" << search.known.size() << " score=" << search.best << std::endl;
            if (status == Search::yes)
                output << index << '\t' << search.best << '\t' << graph6(quotient.lift(search.witness), search.order) << std::endl;
        } catch (const std::invalid_argument& exc) {
            ++total[3];
            std::cout << "row=" << index << " status=filter reason=" << exc.what() << std::endl;
        }
        ++index;
    }
    std::cout << "END rows=" << index << " no=" << total[0] << " yes=" << total[1] << " cap=" << total[2]
              << " filter=" << total[3] << std::endl;
}
