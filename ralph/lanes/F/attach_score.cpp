#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using Mask = std::uint64_t;
using Graph = std::vector<Mask>;

static Mask bit(int vertex) { return Mask{1} << vertex; }

static int pop_vertex(Mask& mask) {
    int vertex = std::countr_zero(mask);
    mask &= mask - 1;
    return vertex;
}

static Graph decode(const std::string& line) {
    if (line.empty() || line[0] < '?' || line[0] > '}') throw std::runtime_error("bad graph6 order");
    int order = line[0] - '?';
    if (line.size() != 1 + (order * (order - 1) / 2 + 5) / 6u)
        throw std::runtime_error("bad graph6 size");
    Graph graph(order);
    unsigned offset = 0;
    for (int end = 1; end < order; ++end)
        for (int start = 0; start < end; ++start, ++offset) {
            int word = line[1 + offset / 6] - '?';
            if (word < 0 || word > 63) throw std::runtime_error("bad graph6 digit");
            if ((word >> (5 - offset % 6)) & 1) {
                graph[start] |= bit(end);
                graph[end] |= bit(start);
            }
        }
    return graph;
}

static std::string encode(const Graph& graph, Mask neighborhood) {
    int order = graph.size();
    std::string line(1 + (order * (order + 1) / 2 + 5) / 6, '?');
    line[0] += order + 1;
    unsigned offset = 0;
    for (int end = 1; end <= order; ++end)
        for (int start = 0; start < end; ++start, ++offset)
            if (((end == order ? neighborhood : graph[end]) & bit(start)) != 0)
                line[1 + offset / 6] += 1 << (5 - offset % 6);
    return line;
}

static void get_independent(const Graph& graph, Mask remaining, int size, std::vector<Mask>& output, Mask chosen = 0) {
    if (!size) { output.push_back(chosen); return; }
    while (std::popcount(remaining) >= size) {
        int vertex = pop_vertex(remaining);
        get_independent(graph, remaining & ~graph[vertex], size - 1, output, chosen | bit(vertex));
    }
}

struct Optimum {
    const Graph& graph;
    std::vector<Mask> constraints;
    int floor;
    std::uint64_t leaves = 0;
    unsigned best = std::numeric_limits<unsigned>::max();
    Mask chosen = 0;

    void eval(Mask neighborhood) {
        if (std::popcount(neighborhood) < floor) return;
        ++leaves;
        unsigned misses = 0;
        for (Mask constraint : constraints)
            if (!(neighborhood & constraint) && ++misses >= best) return;
        best = misses;
        chosen = neighborhood;
    }

    void maximal(Mask neighborhood, Mask free, Mask excluded) {
        if (!(free | excluded)) { eval(neighborhood); return; }
        if (std::popcount(neighborhood | free) < floor) return;
        Mask pivots = free | excluded;
        Mask branches = free;
        int best_width = 65;
        while (pivots) {
            int vertex = pop_vertex(pivots);
            Mask candidate = free & (graph[vertex] | bit(vertex));
            int width = std::popcount(candidate);
            if (width < best_width) { best_width = width; branches = candidate; }
            if (!best_width) return;
        }
        while (branches) {
            int vertex = pop_vertex(branches);
            Mask compatible = ~(graph[vertex] | bit(vertex));
            maximal(neighborhood | bit(vertex), free & compatible, excluded & compatible);
            free &= ~bit(vertex);
            excluded |= bit(vertex);
        }
    }

    void exhaustive(Mask neighborhood, Mask free, int cap) {
        eval(neighborhood);
        if (std::popcount(neighborhood) >= cap) return;
        while (free) {
            int vertex = pop_vertex(free);
            exhaustive(neighborhood | bit(vertex), free & ~graph[vertex], cap);
        }
    }
};

int main(int argc, char** argv) {
    if (argc < 6 || argc > 9) {
        std::cerr << "usage: attach_score BASE.g6 K MIND MAXD OUTPUT.tsv [verify] [--min-edges E]\n";
        return 2;
    }
    int forbidden = std::stoi(argv[2]), minimum = std::stoi(argv[3]), maximum = std::stoi(argv[4]);
    bool verify = false;
    int min_edges = 0;
    for (int arg = 6; arg < argc; ++arg) {
        const std::string flag = argv[arg];
        if (flag == "verify") verify = true;
        else if (flag == "--min-edges" && arg + 1 < argc) min_edges = std::stoi(argv[++arg]);
        else return 2;
    }
    if (forbidden < 2 || minimum < 0 || maximum != forbidden - 1 || minimum > maximum || min_edges < 0)
        return 2;
    std::ifstream input(argv[1]);
    std::ofstream output(argv[5]);
    if (!input || !output) return 2;
    output << "idx\tbaseslack\tI_k\tmandatory_misses\tleaves\tattached_degree\tgraph6\n";
    std::string line;
    unsigned record = std::numeric_limits<unsigned>::max();
    std::size_t feasible = 0, index = 0;
    while (std::getline(input, line)) {
        Graph graph = decode(line);
        int order = graph.size();
        if (order < forbidden || order >= 62) return 2;
        Mask allowed = 0, required = 0, universe = bit(order) - 1;
        bool eligible = true;
        int old_degree_sum = 0;
        for (int vertex = 0; vertex < order; ++vertex) {
            int degree = std::popcount(graph[vertex]);
            old_degree_sum += degree;
            Mask neighbors = graph[vertex];
            while (neighbors)
                if (graph[pop_vertex(neighbors)] & graph[vertex]) throw std::runtime_error("base contains triangle");
            if (degree > maximum || degree < minimum - 1) eligible = false;
            if (degree < maximum) allowed |= bit(vertex);
            if (degree == minimum - 1) required |= bit(vertex);
        }
        std::vector<Mask> independent;
        get_independent(graph, universe, forbidden - 1, independent);
        for (Mask set : independent) {
            Mask outside = universe & ~set;
            for (Mask vertices = set; vertices;) outside &= ~graph[pop_vertex(vertices)];
            if (outside) throw std::runtime_error("base contains a forbidden independent set");
        }
        Mask free = allowed & ~required;
        for (Mask vertices = required; vertices;) {
            Mask neighbors = graph[pop_vertex(vertices)];
            if (neighbors & required) eligible = false;
            free &= ~neighbors;
        }
        const int attachment_floor = std::max(minimum, min_edges - old_degree_sum / 2);
        if (attachment_floor > maximum) eligible = false;
        Optimum answer{graph, {}, attachment_floor};
        unsigned mandatory_misses = 0;
        for (Mask set : independent)
            if (!(set & required)) {
                Mask projected = set & free;
                answer.constraints.push_back(projected);
                mandatory_misses += projected == 0;
            }
        if (eligible) answer.maximal(required, free, 0);
        if (verify && eligible) {
            Optimum reference{graph, answer.constraints, attachment_floor};
            reference.exhaustive(required, free, maximum);
            if (reference.best != answer.best) throw std::runtime_error("optimizer disagrees with exhaustive search");
        }
        output << index << '\t' << std::popcount(allowed) << '\t';
        if (answer.best == std::numeric_limits<unsigned>::max()) output << "NA\t" << mandatory_misses << "\t0\tNA\tNA\n";
        else {
            ++feasible;
            output << answer.best << '\t' << mandatory_misses << '\t' << answer.leaves << '\t'
                   << std::popcount(answer.chosen) << '\t' << encode(graph, answer.chosen) << '\n';
            if (answer.best < record) {
                record = answer.best;
                std::cout << "record idx=" << index << " I_k=" << record
                          << " attached_degree=" << std::popcount(answer.chosen) << std::endl;
            }
            if (!answer.best) {
                std::ofstream found(std::string(argv[5]) + ".found.g6", std::ios::app);
                found << encode(graph, answer.chosen) << '\n';
            }
        }
        ++index;
    }
    if (!output || !index || !input.eof()) return 2;
    std::cout << "complete inputs=" << index << " feasible=" << feasible << " best=" << record << '\n';
}
