#define main panel17_archived_main
#include "../C/panel17_weighted.cpp"
#undef main

int main(int argc, char** argv) try {
    require(argc == 6, "usage: slice_predicate CAT_L CAT_R DEGREE CAP ROOTS < sorted-queries");
    const array<vector<Graph>, 2> catalogues{graphs(argv[1]), graphs(argv[2])};
    const int degree = stoi(argv[3]), cap = stoi(argv[4]), roots = stoi(argv[5]);
    const Params params{degree, cap, degree, roots};
    unique_ptr<Atlas> atlas;
    unique_ptr<Gate> gate;
    Effort effort;
    effort.all_receipts = true;
    int order, host, neutral;
    string text;
    tuple<int, int, int, string> last;
    while (cin >> order >> host >> neutral >> text) {
        auto key = tuple{order, host, neutral, text};
        require(last < key, "query ordering or duplication");
        const int side = order == int(catalogues[0][0].size()) ? 0 : 1;
        const auto& graph = catalogues[side].at(host);
        require(order == int(graph.size()) && 0 <= neutral && neutral < order, "query destination");
        if (tie(order, host, neutral) != tie(get<0>(last), get<1>(last), get<2>(last))) {
            gate.reset();
            if (tie(order, host) != tie(get<0>(last), get<1>(last)))
                atlas = make_unique<Atlas>(graph, params);
            gate = make_unique<Gate>(*atlas, order, Rim{host, neutral}, params, effort);
        }
        vector<int> types;
        for (const auto& token : split(text, ',')) types.push_back(stoi(token));
        const auto code = packed(types);
        require(group_text(code) == text, "noncanonical group");
        cout << order << '\t' << host << '\t' << neutral << '\t' << text << '\t' << gate->group(code) << '\n';
        last = move(key);
    }
    require(cin.eof() && bool(cout), "query input or output failed");
    return 0;
} catch (const exception& error) {
    cerr << error.what() << '\n';
    return 2;
}
