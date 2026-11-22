#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

using Mask = uint32_t;

int take(Mask& mask) {
    int vertex = std::countr_zero(mask);
    mask &= mask - 1;
    return vertex;
}

struct Contact {
    Mask forced, possible;
};

struct Core {
    Mask all, anchors, exterior;
    int alpha, edges = 0;
    std::vector<Mask> adj;
    std::vector<Mask> maximal;
    std::unordered_map<uint64_t, bool> cache;
    std::unordered_map<Mask, Contact> contacts;

    Core(const std::string& encoded, Mask marks, int alpha_cap)
        : all((Mask{1} << (encoded.at(0) - 63)) - 1), anchors(marks), exterior(all ^ marks), alpha(alpha_cap),
          adj(encoded.at(0) - 63) {
        assert(encoded.size() == 1 + (adj.size() * (adj.size() - 1) / 2 + 5) / 6);
        int index = 0;
        for (int right = 0; right < (int)adj.size(); ++right) {
            for (int left = 0; left < right; ++left, ++index) {
                if (((encoded[1 + index/6] - 63) >> (5 - index%6)) & 1) {
                    adj[left] |= Mask{1} << right;
                    adj[right] |= Mask{1} << left;
                    ++edges;
                }
            }
        }
        maximal_independent(all, 0, 0);
        std::ranges::sort(maximal, [](Mask left, Mask right) {
            return std::popcount(left) > std::popcount(right);
        });
        assert(!maximal.empty() && std::popcount(maximal.front()) <= alpha);
    }

    void maximal_independent(Mask allowed, Mask earlier, Mask selected) {
        if (!allowed && !earlier) {
            maximal.push_back(selected);
            return;
        }
        int pivot = std::countr_zero(allowed | earlier);
        for (Mask candidates = allowed & (adj[pivot] | (Mask{1} << pivot)); candidates;) {
            const int vertex = take(candidates);
            const Mask bit = Mask{1} << vertex;
            const Mask compatible = all ^ (adj[vertex] | bit);
            maximal_independent(allowed & compatible, earlier & compatible, selected | bit);
            allowed ^= bit;
            earlier |= bit;
        }
    }

    bool has_independent(Mask allowed, int count) {
        if (count <= 0) return true;
        if (count > alpha || std::popcount(allowed) < count) return false;
        uint64_t key = allowed | (uint64_t{static_cast<unsigned>(count)} << 32);
        if (auto found = cache.find(key); found != cache.end()) return found->second;
        for (Mask set : maximal) {
            if (std::popcount(set) < count) break;
            if (std::popcount(set & allowed) >= count) {
                cache.emplace(key, true);
                return true;
            }
        }
        cache.emplace(key, false);
        return false;
    }

    Contact contact(Mask forced) {
        if (auto found = contacts.find(forced); found != contacts.end()) return found->second;
        Mask forbidden = 0;
        for (Mask scan = forced; scan;) forbidden |= adj[take(scan)];
        Contact contact{forced, forced & forbidden ? 0 : forced | (exterior & ~forbidden)};
        contacts.emplace(forced, contact);
        return contact;
    }
};

struct Shell {
    std::array<Contact, 6> placed{};
    std::array<Mask, 64> reach{};
    int size = 0;
};

struct Run {
    Core& core;
    std::vector<Mask> slots;
    std::array<Mask, 2> doubles;
    int first, second, common, floor_first, floor_second, edge_first, edge_second;
    int unpaired_floor;
    Mask rooted_side;
    std::array<Shell, 2> group{};
    Mask old_slot = 0, old_support = 0;
    uint64_t tested = 0, both = 0, joint = 0;
    bool has_witness = false;
    std::array<std::array<Mask, 6>, 2> witness{};
    Mask witness_common = 0;

    bool add(Shell& shell, Contact contact) {
        if (!contact.possible) return false;
        for (int subset = 0; subset < (1 << shell.size); ++subset) {
            Mask reach = shell.reach[subset] | contact.possible;
            if (core.has_independent(core.all ^ reach, core.alpha + 1 - std::popcount((unsigned)subset)))
                return false;
            shell.reach[subset | (1 << shell.size)] = reach;
        }
        shell.placed[shell.size++] = contact;
        return true;
    }

    int max_contacts(Contact contact) {
        int fixed = std::popcount(contact.forced);
        Mask optional = contact.possible ^ contact.forced;
        int extra = core.alpha - fixed;
        while (extra > 0 && !core.has_independent(optional, extra)) --extra;
        return fixed + extra;
    }

    int degree_cap(const Shell& shell, int floor) {
        int contacts = 0;
        for (int vertex = 0; vertex < (int)core.adj.size(); ++vertex) {
            const Mask bit = Mask{1} << vertex;
            int low = std::popcount(core.adj[vertex]), high = low;
            for (int idx = 0; idx < shell.size; ++idx) {
                low += bool(shell.placed[idx].forced & bit);
                high += bool(shell.placed[idx].possible & bit);
            }
            if (low > core.alpha + 1 || high < floor) return -1;
        }
        for (int idx = 0; idx < shell.size; ++idx) {
            int bound = max_contacts(shell.placed[idx]);
            if (bound + 1 < floor) return -1;
            contacts += bound;
        }
        return contacts;
    }

    bool joint_ok(Contact center, int contacts) {
        using std::popcount;
        const bool have_center = common != 0;
        if (have_center && !center.possible) return false;
        int edge_cap = core.edges + contacts + first + second;
        if (have_center) edge_cap += 2 + max_contacts(center);
        if (rooted_side) edge_cap += popcount(rooted_side) + 2;
        for (int lidx = 0; lidx < first; ++lidx)
            for (int ridx = 0; ridx < second; ++ridx)
                edge_cap += !(group[0].placed[lidx].forced & group[1].placed[ridx].forced);
        if (edge_cap < unpaired_floor) return false;
        for (unsigned left = 0; left < (1U << first); ++left) {
            for (unsigned right = 0; right < (1U << second); ++right) {
                const int size = popcount(left) + popcount(right);
                if (size + common < (rooted_side ? 2 : 3)) continue;
                bool forced_independent = true;
                for (Mask left_copy = left; left_copy && forced_independent;) {
                    const Contact from = group[0].placed[take(left_copy)];
                    for (Mask right_copy = right; right_copy;) {
                        if (!(from.forced & group[1].placed[take(right_copy)].forced)) {
                            forced_independent = false;
                            break;
                        }
                    }
                }
                if (!forced_independent) continue;
                Mask reach = group[0].reach[left] | group[1].reach[right];
                if (core.has_independent(core.all ^ reach, core.alpha + 3 - size)) return false;
                if (rooted_side && core.has_independent(core.all & ~(reach | rooted_side), core.alpha + 2 - size))
                    return false;
                if (have_center && core.has_independent(core.all ^ (reach | center.possible), core.alpha + 2 - size))
                    return false;
                if (have_center && rooted_side &&
                    core.has_independent(core.all & ~(reach | center.possible | rooted_side), core.alpha + 1 - size))
                    return false;
            }
        }
        return true;
    }

    bool place(int idx, Mask used_first, Mask used_second, int single_first, int single_second, bool price_all) {
        if (idx == first + second) {
            ++tested;
            int cap_first = degree_cap(group[0], floor_first);
            int cap_second = degree_cap(group[1], floor_second);
            if (cap_first < 0 || cap_second < 0 || core.edges + first + cap_first < edge_first ||
                core.edges + second + cap_second < edge_second)
                return false;
            ++both;
            Mask center = common ? slots.back() : 0;
            if (!joint_ok(core.contact(center), cap_first + cap_second)) return false;
            ++joint;
            if (!has_witness) {
                for (auto side : {0, 1})
                    for (auto nbr = 0; nbr < group[side].size; ++nbr)
                        witness[side][nbr] = group[side].placed[nbr].forced;
                witness_common = center;
                has_witness = true;
            }
            return !price_all;
        }
        const bool side = idx >= first;
        const Mask used = side ? used_second : used_first;
        const int singles = side ? single_second : single_first;
        const Mask opp = slots[idx];
        const bool tied = idx && idx != first && slots[idx - 1] == opp;
        const Mask smallest = tied ? group[side].placed[group[side].size-1].forced ^ opp : 0;
        const auto try_support = [&](Mask support) {
            if (support < smallest || !add(group[side], core.contact(opp | support))) return false;
            bool stop = place(idx + 1, used_first | (side ? 0 : support), used_second | (side ? support : 0),
                              single_first + (!side && !support), single_second + (side && !support), price_all);
            --group[side].size;
            return stop;
        };
        if (singles < 4 && try_support(0)) return true;
        for (Mask choices = doubles[side] & ~used; choices;) {
            if (try_support(Mask{1} << take(choices))) return true;
        }
        return false;
    }

    void go(bool price_all) {
        assert(first > 0 && second > 0 && first <= 5 && second <= 5 && (common == 0 || common == 1));
        assert((int)slots.size() == first + second + common);
        assert(std::ranges::is_sorted(slots));
        const std::vector<Mask> sorted = slots;
        const int count = sorted.size();
        for (Mask selected = 0; selected < (Mask{1} << count); ++selected) {
            if (std::popcount(selected) != first) continue;
            bool canonical = true;
            int idx = 0;
            for (int pos = 0; pos < count; ++pos) {
                if ((selected >> pos) & 1) {
                    if (pos && sorted[pos] == sorted[pos - 1] && !((selected >> (pos - 1)) & 1)) {
                        canonical = false;
                        break;
                    }
                    slots[idx++] = sorted[pos];
                }
            }
            if (!canonical) continue;
            std::vector<Mask> rest;
            for (int pos = 0; pos < count; ++pos)
                if (!((selected >> pos) & 1)) rest.push_back(sorted[pos]);
            int center_count = common ? rest.size() : 1;
            for (int center = 0; center < center_count; ++center) {
                if (common && center && rest[center] == rest[center - 1]) continue;
                idx = first;
                for (int pos = 0; pos < (int)rest.size(); ++pos)
                    if (!common || pos != center) slots[idx++] = rest[pos];
                if (common) slots.back() = rest[center];
                if (place(0, 0, 0, 0, 0, price_all)) return;
            }
        }
    }
};

int main(int argc, char** argv) {
    assert(argc <= 2 && (argc == 1 || std::string(argv[1]) == "--all"));
    const bool price_all = argc == 2;
    int alpha;
    while (std::cin >> alpha) {
        std::string origin, encoded;
        Mask smaller, larger;
        size_t jobs;
        std::cin >> origin >> smaller >> larger >> encoded >> jobs;
        assert(std::cin);
        Core core(encoded, smaller | larger, alpha);
        for (size_t idx = 0; idx < jobs; ++idx) {
            std::string type, key, variant;
            int first, second, common, num, first_floor, second_floor, first_edge, second_edge, unpaired_floor;
            bool rooted;
            Mask one, two;
            std::cin >> type >> key >> variant >> first >> second >> common >> one >> two >> num
                     >> first_floor >> second_floor >> first_edge >> second_edge >> unpaired_floor >> rooted;
            assert(std::cin && !(smaller & larger) && !(one & ~smaller) && !(two & ~smaller));
            std::vector<Mask> slots(num);
            for (auto& item : slots) {
                std::cin >> item;
                assert(item && !(item & ~larger) && std::popcount(item) <= 2);
            }
            Run scan{core, slots, {one, two}, first, second, common, first_floor, second_floor,
                     first_edge, second_edge, unpaired_floor, rooted ? smaller : 0};
            scan.go(price_all);
            std::cout << type << ' ' << key << ' ' << variant << ' ' << scan.tested << ' '
                      << scan.both << ' ' << scan.joint;
            if (scan.has_witness) {
                for (int side : {0, 1}) {
                    std::cout << ' ';
                    for (int slot = 0; slot < (side ? second : first); ++slot) {
                        if (slot) std::cout << ',';
                        std::cout << scan.witness[side][slot];
                    }
                }
                std::cout << ' ' << scan.witness_common;
            }
            std::cout << '\n';
        }
    }
    assert(std::cin.eof());
}
