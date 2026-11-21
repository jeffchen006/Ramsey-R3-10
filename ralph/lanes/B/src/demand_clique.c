#include "gutil.h"

enum { MAX_DEMANDS = 528, MAX_WORDS = (MAX_DEMANDS+63)/64 };
typedef struct { set_t words[MAX_WORDS]; } bits_t;

static bits_t incompatible[MAX_DEMANDS];
static int width, picked[64];
static graph_t graph;
static set_t demands[MAX_DEMANDS], full_vertices;
static int count, row_sizes, max_size;

static int below(bits_t remaining)
{
    for (int word = 0; word < width; ++word)
        if (remaining.words[word]) return word*64+CTZ(remaining.words[word]);
    return -1;
}

static void remove_bit(bits_t *bits, int item)
{
    bits->words[item/64] &= ~BIT(item%64);
}

static void add_bit(bits_t *bits, int item)
{
    bits->words[item/64] |= BIT(item%64);
}

static void clear_covered(set_t row)
{
    bits_t cover = {0};
    int covered[MAX_DEMANDS], ncovered = 0;
    for (int demand = 0; demand < count; ++demand)
        if ((row & demands[demand]) == demands[demand]) {
            add_bit(&cover, demand);
            covered[ncovered++] = demand;
        }
    for (int index = 0; index < ncovered; ++index)
        for (int word = 0; word < width; ++word)
            incompatible[covered[index]].words[word] &= ~cover.words[word];
}

static void list_rows(set_t remaining, set_t chosen, set_t dominated, int size)
{
    if (dominated == full_vertices) {
        if (row_sizes & (1 << size)) clear_covered(chosen);
        return;
    }
    if (size == max_size) return;
    while (remaining) {
        int vertex = CTZ(remaining);
        remaining &= remaining-1;
        list_rows(remaining & ~graph.adj[vertex], chosen | BIT(vertex), dominated | BIT(vertex) | graph.adj[vertex], size+1);
    }
}

static int find_clique(bits_t remaining, int needed, int depth)
{
    int start = below(remaining);
    if (start < 0) return 0;
    if (needed == 1) { picked[depth] = start; return 1; }
    int items[MAX_DEMANDS], bounds[MAX_DEMANDS], count = 0;
    bits_t uncolored = remaining;
    for (int color = 1; start >= 0; ++color, start = below(uncolored)) {
        bits_t choices = uncolored;
        for (int item = start; item >= 0; item = below(choices)) {
            items[count] = item;
            bounds[count++] = color;
            remove_bit(&choices, item);
            remove_bit(&uncolored, item);
            for (int word = 0; word < width; ++word) choices.words[word] &= ~incompatible[item].words[word];
        }
    }
    while (count) {
        if (bounds[--count] < needed) return 0;
        int item = items[count];
        remove_bit(&remaining, item);
        bits_t restricted = {0};
        for (int word = 0; word < width; ++word)
            restricted.words[word] = remaining.words[word] & incompatible[item].words[word];
        if (find_clique(restricted, needed-1, depth+1)) { picked[depth] = item; return 1; }
    }
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2 || argc > 3) return 2;
    int order = atoi(argv[1]);
    if (order < 2 || order > 9) return 2;
    if (argc == 3) {
        for (const char *digit = argv[2]; *digit; ++digit) {
            int size = *digit-'0';
            if (size < 1 || size > 9) return 2;
            row_sizes |= 1 << size;
            if (size > max_size) max_size = size;
        }
        if (!row_sizes) return 2;
    }
    char line[1024];
    long long inputs = 0, cliques = 0;
    while (fgets(line, sizeof line, stdin)) {
        int vertices = line[0]-63;
        if (vertices < 1 || vertices > 32 || strlen(line) != (size_t)(2+(vertices*(vertices-1)/2+5)/6) ||
                g6_read(line, &graph) || !g_trianglefree(&graph)) return 2;
        ++inputs;
        full_vertices = BIT(vertices)-1;
        set_t opens[MAX_DEMANDS];
        count = 0;
        for (int vertex = 0; vertex < vertices; ++vertex) {
            set_t distant = full_vertices & ~(graph.adj[vertex] | BIT(vertex));
            for (set_t left = graph.adj[vertex]; left; left &= left-1) distant &= ~graph.adj[CTZ(left)];
            if (!distant) { demands[count] = BIT(vertex); opens[count++] = graph.adj[vertex]; }
            for (distant &= ~(BIT(vertex)-1); distant; distant &= distant-1) {
                int other = CTZ(distant);
                demands[count] = BIT(vertex) | BIT(other);
                opens[count++] = graph.adj[vertex] | graph.adj[other];
            }
        }
        width = (count+63)/64;
        for (int item = 0; item < count; ++item)
            for (int word = 0; word < width; ++word) incompatible[item].words[word] = 0;
        bits_t allowed = {0};
        for (int item = 0; item < count; ++item) {
            add_bit(&allowed, item);
            for (int other = 0; other < item; ++other) {
                if (!row_sizes && !(demands[item] & opens[other])) continue;
                add_bit(&incompatible[item], other);
                add_bit(&incompatible[other], item);
            }
        }
        if (row_sizes) list_rows(full_vertices, 0, 0, 0);
        if (find_clique(allowed, order, 0)) {
            ++cliques;
            printf("%lld\t", inputs);
            for (int index = 0; index < order; ++index)
                printf("%llx%c", (unsigned long long)demands[picked[index]], index+1 == order ? '\n' : ' ');
        }
    }
    fprintf(stderr, "demand cliques: in=%lld witnesses=%lld remainder=%lld\n", inputs, cliques, inputs-cliques);
    return ferror(stdin) || fflush(stdout) == EOF;
}
