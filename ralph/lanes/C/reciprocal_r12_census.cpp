#define main reciprocal_stream_main
#include "reciprocal_stream.cpp"
#undef main

using Profile = std::array<int, 5>;

Profile profile(const Mark& mark) {
    Profile result{size(mark[0] | mark[1] | mark[2]), size(mark[0] & mark[1]),
                   size(mark[1] & mark[2]), size(mark[0] & mark[2]),
                   size(mark[0] & mark[1] & mark[2])};
    std::sort(result.begin() + 1, result.begin() + 4);
    return result;
}

int main(int argc, char** argv) {
    assert(argc == 3 || argc == 4);
    if (std::string(argv[1]) == "control") {
        assert(argc == 4);
        std::ifstream source(argv[2]), planted(argv[3]);
        assert(source && planted);
        int count = 0;
        std::string line;
        while (source >> line) {
            int row, core;
            Mark mark;
            assert(planted >> row >> core >> mark[0] >> mark[1] >> mark[2]);
            std::string rest;
            std::getline(planted, rest);
            assert(row == count && profile(mark) == Profile({7, 0, 0, 1, 0}));
            uint64_t number = 0, groups = 0;
            auto result = cards(decode(line, 10), Params{6, 6, 2, 3},
                                [](Mask) { return true; }, number, groups);
            assert(std::ranges::count(result.at(core), mark) == 1);
            number = groups = 0;
            auto too_wide = cards(decode(line, 10), Params{6, 6, 2, 2},
                                  [](Mask) { return true; }, number, groups);
            assert(std::ranges::none_of(too_wide, [&](const auto& record) {
                return std::ranges::find(record.second, mark) != record.second.end();
            }));
            ++count;
        }
        int extra;
        assert(count == 395 && !(planted >> extra));
        std::cout << "395 planted width-four two-mask controls, union 7 and intersection 1; all found\n";
        return 0;
    }
    assert(argc == 4 && std::string(argv[1]) == "target");
    std::ifstream source(argv[2]);
    std::ofstream tight(std::string(argv[3]) + ".tight"), old(std::string(argv[3]) + ".old");
    std::ofstream histogram(std::string(argv[3]) + ".hist"), hosts(std::string(argv[3]) + ".hosts");
    assert(source && tight && old && histogram && hosts);
    std::string line;
    int row = 0;
    int limit = 191;
    if (const char* env = std::getenv("R310_C_LIMIT")) limit = std::stoi(env);
    std::map<Profile, std::array<uint64_t, 3>> totals;
    std::array<uint64_t, 3> kept{};
    for (; row < limit && source >> line; ++row) {
        auto graph = decode(line, 22);
        std::map<Profile, std::array<uint64_t, 3>> local;
        uint64_t host_kept = 0, cards_kept = 0;
        for (int coverage = 12; coverage <= 18; ++coverage) {
            uint64_t number = 0, groups = 0, recovered = 0;
            auto result = cards(graph, Params{9, 5, 3, 22 - coverage},
                                [](Mask) { return true; }, number, groups);
            assert(groups == result.size());
            if (coverage >= 14) cards_kept += groups;
            for (auto& [core, marks] : result) {
                if (coverage == 13) old << row << ' ' << core << ' ' << marks.size() << '\n';
                std::map<Profile, uint64_t> by_card;
                for (auto& mark : marks) {
                    auto type = profile(mark);
                    assert(type[0] == coverage);
                    ++by_card[type];
                    if (type == Profile{14, 2, 2, 2, 2})
                        tight << row << ' ' << core << ' ' << mark[0] << ' ' << mark[1] << ' ' << mark[2] << '\n';
                }
                recovered += marks.size();
                for (auto [type, count] : by_card) {
                    local[type][0] += count;
                    ++local[type][1];
                }
            }
            assert(recovered == number);
            if (coverage >= 14) host_kept += number;
        }
        for (auto [type, entries] : local) {
            totals[type][0] += entries[0];
            totals[type][1] += entries[1];
            ++totals[type][2];
            hosts << row;
            for (int count : type) hosts << '\t' << count;
            hosts << '\t' << entries[0] << '\t' << entries[1] << '\n';
        }
        kept[0] += host_kept;
        kept[1] += cards_kept;
        kept[2] += (host_kept != 0);
    }
    assert(row == limit);
    histogram << "union\tpair01(sorted)\tpair02(sorted)\tpair12(sorted)\ttriple\tmarks\tcards\thosts\n";
    for (auto [type, entries] : totals) {
        for (int count : type) histogram << count << '\t';
        histogram << entries[0] << '\t' << entries[1] << '\t' << entries[2] << '\n';
    }
    std::cout << "hosts processed " << row << "; union >= 14 " << kept[0] << " marks " << kept[1]
              << " distinct cards " << kept[2] << " distinct hosts; CPU " << cpu() << '\n';
}
