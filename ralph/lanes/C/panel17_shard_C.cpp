#define main panel17_r13_main
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#include "panel17.cpp"
#pragma GCC diagnostic pop
#undef main
#include "panel17_record.hpp"

int main(int argc, char** argv) {
    if (argc != 7 || string(argv[1]) != "shard") return 2;
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    read_hosts(argv[2]);
    read_input(argv[3], argv[4]);
    int first = stoi(argv[5]), last = stoi(argv[6]);
    if (first < 0 || first >= last || last > int(frames.size())) return 2;
    map<Header, vector<pair<int, int>>> right_buckets;
    for (int right = 0; right < int(frames.size()); ++right)
        for (int flip : {0, 1})
            right_buckets[oriented_header(frames[right], flip)].emplace_back(right, flip);
    map<Header, vector<pair<int, int>>> compatible;
    for (int left = first; left < last; ++left) {
        const auto& head = frames[left].header;
        auto [position, inserted] = compatible.try_emplace(head);
        auto& right_ids = position->second;
        if (inserted) {
            for (const auto& [other, members] : right_buckets)
                if (agrees(head, other)) right_ids.insert(right_ids.end(), members.begin(), members.end());
            sort(right_ids.begin(), right_ids.end());
            if (adjacent_find(right_ids.begin(), right_ids.end()) != right_ids.end())
                throw runtime_error("duplicate header ID");
        }
        for (const auto& [right, flip] : right_ids) {
            int depth = screen({left, right, flip}, [](const Domains&, const Domains&) {});
            if (depth < 1 || depth > 5) throw runtime_error("inconsistent header join");
            panel17_record(left, right, flip, depth);
        }
    }
    if (!cout.flush()) throw runtime_error("stage stream write failed");
}
