int main(int argc, char** argv) {
    assert(argc == 11);
    std::string mode = argv[1];
    assert(mode == "indexed" || mode == "direct" || mode == "cards" || mode == "planted" || mode == "batch");
    std::ifstream from_file(argv[2]), to_file(argv[3]);
    const int from_order = std::stoi(argv[4]), to_order = std::stoi(argv[5]);
    const Params params{std::stoi(argv[6]),std::stoi(argv[7]),std::stoi(argv[8]),std::stoi(argv[9])};
    std::ofstream journal(argv[10]);
    assert(from_file && to_file && journal);
    std::string line;
    std::vector<Host> from_hosts;
    std::map<Key,std::vector<Card>> index;
    std::vector<Card> unindexed;
    uint64_t from_local = 0, from_cards = 0, to_local = 0, to_kept = 0;
    while (from_file >> line) {
        int row = from_hosts.size();
        const auto& from = from_hosts.emplace_back(decode(line,from_order));
        auto groups = cards(from,params,[](Mask) { return true; },from_local,from_cards);
        for (auto& [core,marks] : groups) {
            if (mode == "cards") journal << row << ' ' << core << ' ' << marks.size() << '\n';
            else if (mode != "direct") index[fingerprint(from,core,params,true)].push_back({row,core,std::move(marks)});
            else unindexed.push_back({row,core,std::move(marks)});
        }
    }
    std::cout << "left hosts " << from_hosts.size() << " marks " << from_local << " cards " << from_cards
              << " indexed keys " << index.size() << " cpu " << cpu() << std::endl;
    if (mode == "cards") return 0;
    auto scan = [&](std::istream& input, std::ostream& output, uint64_t offset) {
    uint64_t pairs = 0, marked_pairs = 0, card_maps = 0, role_maps = 0, total_hosts = 0, hosts_matched = 0;
    double mark_cpu = 0, map_cpu = 0;
    std::map<std::string,uint64_t> outcomes;
    auto counts = [&]() {
        std::cout << "right hosts " << total_hosts << " marks " << to_local << " kept cards " << to_kept
                  << " matched hosts " << hosts_matched << " card pairs " << pairs << " marked pairs " << marked_pairs
                  << " card maps " << card_maps << " role maps " << role_maps << " marks CPU covered " << mark_cpu
                  << " maps CPU covered " << map_cpu << " total CPU " << cpu();
        for (auto& [reason,count] : outcomes) std::cout << ' ' << reason << ' ' << count;
        std::cout << std::endl;
    };
    while (input >> line) {
        int row = offset + total_hosts++;
        double start = cpu();
        auto to = decode(line,to_order);
        auto groups = cards(to,params,[&](Mask core) {
            return mode == "direct" || index.contains(fingerprint(to,core,params,false));
        },to_local,to_kept);
        mark_cpu += cpu()-start;
        start = cpu();
        if (!groups.empty()) ++hosts_matched;
        for (auto& [core,marks] : groups) {
            Card second{row,core,std::move(marks)};
            const auto& eligible = mode == "direct" ? unindexed : index.at(fingerprint(to,core,params,false));
            for (const auto& first : eligible) {
                if (mode == "planted" && first.host != second.host) continue;
                const auto& from = from_hosts[first.host];
                ++pairs; marked_pairs += first.marks.size()*second.marks.size();
                align(from,first.core,to,second.core,params,[&](const auto& mapping) {
                    ++card_maps;
                    std::string mapping_text;
                    for (int vertex : sites(first.core)) mapping_text += ' ' + std::to_string(mapping[vertex]);
                    for (const auto& first_mark : first.marks) for (const auto& second_mark : second.marks) {
                        ++role_maps;
                        auto matched = merge(from,first,first_mark,to,second,second_mark,mapping,params);
                        auto verdict = evaluate(matched,params);
                        ++outcomes[verdict.reason];
                        output << first.host << ' ' << first.core;
                        for (auto roots : first_mark) output << ' ' << roots;
                        output << ' ' << second.host << ' ' << second.core;
                        for (auto roots : second_mark) output << ' ' << roots;
                        output << mapping_text << ' ' << verdict.reason << ' ' << verdict.witness << '\n';
                    }
                });
            }
        }
        map_cpu += cpu()-start;
        if (total_hosts%2048 == 0) counts();
    }
    counts();
    output.flush();
    assert(input.eof() && output);
    return total_hosts;
    };
    if (mode != "batch") {
        scan(to_file,journal,0);
    } else {
        uint64_t lo, hi;
        std::string source, destination;
        while (to_file >> lo >> hi >> source >> destination) {
            assert(lo < hi);
            std::ifstream shard(source);
            std::ofstream output(destination);
            assert(shard && output);
            auto start = cpu();
            auto received = scan(shard,output,lo);
            assert(received == hi-lo);
            journal << lo << '\t' << hi << '\t' << destination << '\t' << cpu()-start << std::endl;
            assert(journal);
        }
        assert(to_file.eof());
    }
}
