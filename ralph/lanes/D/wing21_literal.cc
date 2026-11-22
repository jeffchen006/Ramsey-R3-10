#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <unordered_map>
#include <utility>
#include <vector>

using Mask = std::uint32_t;
using BoundMap = std::unordered_map<Mask,int>;

struct Background {
    std::array<Mask,31> compatible{}, wing{};
    BoundMap best;

    void independent(Mask next, Mask permitted, int size) {
        auto& known = best[permitted];
        known = std::max(known,size);
        while (next) {
            int vertex = __builtin_ctz(next);
            next &= next-1;
            independent(next & compatible[vertex], permitted & wing[vertex], size+1);
        }
    }
};

extern "C" void test_profiles(int order, int nrows, const Mask* rows, int ntypes, const Mask* types,
                              int nprofiles, const Mask* profiles, unsigned char* pass) {
    int count = order+nrows;
    assert(count < 32 && ntypes < 32);
    Background background;
    auto no_edge = [&](int first, int second) {
        if (second < order) return true;
        if (first < order) return !(rows[second-order] & (1u << first));
        return bool(rows[first-order] & rows[second-order]);
    };
    for (int vertex=0; vertex<count; ++vertex) {
        for (int other=vertex+1; other<count; ++other)
            if (no_edge(vertex,other)) background.compatible[vertex] |= 1u << other;
        for (int site=0; site<ntypes; ++site) {
            bool allowed = vertex<order ? !(types[site] & (1u << vertex)) : bool(types[site] & rows[vertex-order]);
            if (allowed) background.wing[vertex] |= 1u << site;
        }
    }
    background.independent((1u<<count)-1,(1u<<ntypes)-1,0);
    std::vector<std::pair<Mask,int>> constraints(background.best.begin(),background.best.end());
    std::sort(constraints.begin(),constraints.end(),[](auto left,auto right) {return left.second>right.second;});
    for (int index=0; index<nprofiles; ++index) {
        Mask seen = profiles[2*index], repeated = profiles[2*index+1];
        bool old_ok = true, new_ok = true;
        for (auto [family,size] : constraints) {
            if (!new_ok && size<order) break;
            int compatible = __builtin_popcount(seen & family)+__builtin_popcount(repeated & family);
            if (size>=order && compatible>=2) old_ok = false;
            if (size+compatible>=order+2) new_ok = false;
        }
        pass[index] = int(old_ok)+2*int(new_ok);
    }
}
