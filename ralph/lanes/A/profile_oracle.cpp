#define main panel16_archived_main
#include "../C/panel16.cpp"
#undef main

vector<Frame> load_frames(const char* path, vector<Host>& catalogue, Parameters par) {
    ifstream stream(path);
    require(bool(stream), "frame file open");
    vector<Frame> result;
    for (string line; getline(stream, line);) {
        istringstream row(line);
        Frame frame = read_frame(row, catalogue, par);
        int sum, neutral;
        require(bool(row >> sum >> neutral) && sum == frame.dsum &&
                neutral == pop(frame.host->adj[frame.neutral]), "frame margin");
        row >> ws;
        require(row.eof(), "extra frame fields");
        result.push_back(move(frame));
    }
    require(stream.eof() && !stream.bad() && !result.empty(), "frame file read");
    return result;
}

bool compatible_margins(const Frame& left, const Frame& right, Parameters par) {
    int difference = int(right.host->adj.size()) - int(left.host->adj.size());
    return left.dsum + par.degree * difference == right.dsum &&
           pop(left.host->adj[left.neutral]) + pop(right.host->adj[right.neutral]) == par.degree;
}

string group_bits(const Frame& source, const Frame& target, Parameters par) {
    target.host->build();
    string result;
    for (const auto& sites : source.groups)
        result += domain(source, target, sites, par, true).empty() ? '0' : '1';
    return result;
}

void emit(int left_id, int right_id, const Frame& left, const Frame& right, Parameters par) {
    cout << left_id << '\t' << right_id << '\t' << group_bits(left, right, par)
         << '\t' << group_bits(right, left, par) << '\n';
}

int main(int argc, char** argv) try {
    require(argc >= 2, "missing mode");
    string mode = argv[1];
    require((mode == "small" && argc == 6) || (mode == "pilot" && argc == 5),
            "usage: profile_oracle small CAT6 CAT7 FRAMES6 FRAMES7 | pilot CAT16 CAT17 CASES");
    Parameters par = mode == "small" ? Parameters{5, 4, 5, 2} : Parameters{9, 5, 9, 4};
    auto left_catalogue = read_graphs(argv[2]);
    auto right_catalogue = read_graphs(argv[3]);
    ios::sync_with_stdio(false);
    if (mode == "small") {
        auto left = load_frames(argv[4], left_catalogue, par);
        auto right = load_frames(argv[5], right_catalogue, par);
        for (int left_id = 0; left_id < int(left.size()); ++left_id)
            for (int right_id = 0; right_id < int(right.size()); ++right_id)
                if (compatible_margins(left[left_id], right[right_id], par))
                    emit(left_id, right_id, left[left_id], right[right_id], par);
    } else {
        ifstream stream(argv[4]);
        require(bool(stream), "pilot file open");
        for (string line; getline(stream, line);) {
            istringstream row(line);
            int left_id, right_id;
            require(bool(row >> left_id >> right_id), "pilot ID");
            auto left = read_frame(row, left_catalogue, par);
            auto right = read_frame(row, right_catalogue, par);
            row >> ws;
            require(row.eof() && compatible_margins(left, right, par), "bad pilot row");
            emit(left_id, right_id, left, right, par);
        }
        require(stream.eof() && !stream.bad(), "pilot file read");
    }
    require(bool(cout), "output failure");
    return 0;
} catch (const exception& error) {
    cerr << error.what() << '\n';
    return 2;
}
