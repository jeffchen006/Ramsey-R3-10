#include "gutil.h"

static graph_t graph;
static set_t full, closed[64];
static int maximum_size;
static unsigned sizes;

static int can_cover(set_t allowed, set_t dominated, int size)
{
    if (size > maximum_size) return 0;
    if (dominated == full) return !!(sizes & (1u << size));
    if (size == maximum_size || !allowed) return 0;
    set_t missing = full & ~dominated, choices = 0;
    int fewest = graph.n+1;
    while (missing) {
        int vertex = CTZ(missing);
        missing &= missing-1;
        set_t options = allowed & closed[vertex];
        int count = POP(options);
        if (!count) return 0;
        if (count < fewest) {
            choices = options;
            fewest = count;
            if (count == 1) break;
        }
    }
    while (choices) {
        int vertex = CTZ(choices);
        choices &= choices-1;
        allowed &= ~BIT(vertex);
        if (can_cover(allowed & ~closed[vertex], dominated | closed[vertex], size+1)) return 1;
    }
    return 0;
}

static int demand_supported(set_t demand)
{
    set_t dominated = 0;
    for (set_t left = demand; left; left &= left-1) {
        int vertex = CTZ(left);
        if (graph.adj[vertex] & demand) return 0;
        dominated |= closed[vertex];
    }
    return can_cover(full & ~dominated, dominated, POP(demand));
}

static int demand_valid(set_t demand)
{
    if (!demand || (demand & ~full)) return 0;
    if (POP(demand) == 1) return 1;
    if (POP(demand) != 2) return 0;
    int first = CTZ(demand), second = CTZ(demand & (demand-1));
    return !(graph.adj[first] & BIT(second)) && !(graph.adj[first] & graph.adj[second]);
}

int main(int argc, char **argv)
{
    if (argc < 2 || argc > 4) return 2;
    for (const char *digit = argv[1]; *digit; ++digit) {
        int size = *digit-'0';
        if (size < 1 || size > 9) return 2;
        sizes |= 1u << size;
        if (size > maximum_size) maximum_size = size;
    }
    if (!sizes) return 2;
    FILE *trace = argc >= 3 ? fopen(argv[2], "r") : NULL;
    if (argc >= 3 && !trace) return 2;
    int clique = argc == 4 ? atoi(argv[3]) : 0;
    if (argc == 4 && (clique < 2 || clique > 9)) return 2;
    long long item = 0;
    if (clique && fscanf(trace, "%lld", &item) != 1 && !feof(trace)) return 2;
    char line[1024];
    long long inputs = 0, witnesses = 0, pair_witnesses = 0;
    while (fgets(line, sizeof line, stdin)) {
        ++inputs;
        int order = line[0]-63;
        if (order < 1 || order > 62 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
            g6_read(line, &graph) || !g_trianglefree(&graph)) return 2;
        full = BIT(graph.n)-1;
        for (int vertex = 0; vertex < graph.n; ++vertex) closed[vertex] = graph.adj[vertex] | BIT(vertex);
        set_t demand = 0;
        if (clique) {
            if (!item || inputs < item) continue;
            if (inputs != item) return 2;
            set_t demands[9];
            for (int index = 0; index < clique; ++index) {
                unsigned long long value;
                if (fscanf(trace, "%llx", &value) != 1 || !demand_valid(value)) return 2;
                demands[index] = value;
                for (int other = 0; other < index; ++other) {
                    if (demands[other] == demands[index] || demand_supported(demands[other] | demands[index])) {
                        fprintf(stderr, "rejected clique witness at graph line %lld\n", inputs);
                        return 1;
                    }
                }
            }
            ++witnesses;
            if (fscanf(trace, "%lld", &item) != 1) {
                if (!feof(trace)) return 2;
                item = 0;
            } else if (item <= inputs) return 2;
            continue;
        } else if (trace) {
            unsigned long long value;
            if (fscanf(trace, "%llx", &value) != 1) return 2;
            demand = value;
            if (!demand_valid(demand) || demand_supported(demand)) {
                fprintf(stderr, "rejected witness at line %lld\n", inputs);
                return 1;
            }
        } else {
            for (int first = 0; !demand && first < graph.n; ++first) {
                set_t distant = full & ~closed[first];
                for (set_t left = graph.adj[first]; left; left &= left-1) distant &= ~closed[CTZ(left)];
                distant &= ~(BIT(first)-1);
                for (; distant; distant &= distant-1) {
                    set_t pair = BIT(first) | BIT(CTZ(distant));
                    if (!demand_supported(pair)) { demand = pair; break; }
                }
            }
            for (int vertex = 0; !demand && vertex < graph.n; ++vertex)
                if (!demand_supported(BIT(vertex))) demand = BIT(vertex);
            printf("%llx\n", (unsigned long long)demand);
        }
        witnesses += !!demand;
        pair_witnesses += POP(demand) == 2;
    }
    if (trace) {
        char trailing;
        if ((clique && item) || fscanf(trace, " %c", &trailing) != EOF || ferror(trace)) return 2;
        fclose(trace);
    }
    fprintf(stderr, "row support inputs=%lld witnessed=%lld pairs=%lld survivors=%lld\n",
            inputs, witnesses, pair_witnesses, inputs-witnesses);
    return ferror(stdin) || fflush(stdout) == EOF;
}
