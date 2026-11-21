#include "gutil.h"

#define MAXHITS (1u << 17)
#define MAXSUPPORTS (1u << 17)

static graph_t base;
static set_t full, hits[MAXHITS], supports[10][MAXSUPPORTS];
static unsigned int hit_count, support_count[10];
static unsigned long inputs, lifted, eligible;
static int alpha;

static void targets(set_t pending, set_t picked, int count)
{
    if (count == 0) {
        if (hit_count == MAXHITS) exit(3);
        hits[hit_count++] = picked;
        return;
    }
    while (POP(pending) >= count) {
        int vertex = CTZ(pending);
        pending &= pending - 1;
        targets(pending & ~base.adj[vertex], picked | BIT(vertex), count - 1);
    }
}

static void supports_rec(set_t available, set_t chosen, int need, int degree)
{
    if (POP(available) < need) return;
    int fewest = 64;
    set_t critical = 0;
    for (unsigned int index = 0; index < hit_count; ++index) {
        if (chosen & hits[index]) continue;
        set_t next = available & hits[index];
        int choices = POP(next);
        if (!choices || !need) return;
        if (choices < fewest) {
            critical = next;
            fewest = choices;
        }
    }
    if (!need) {
        unsigned int at = support_count[degree]++;
        if (at == MAXSUPPORTS) exit(4);
        supports[degree][at] = chosen;
        return;
    }
    if (!critical) critical = available;
    while (critical) {
        int vertex = CTZ(critical);
        critical &= critical - 1;
        available &= ~BIT(vertex);
        supports_rec(available & ~base.adj[vertex], chosen | BIT(vertex), need - 1, degree);
    }
}

static void lift(int edge, set_t first, set_t second)
{
    if (edge ? !!(first & second) : has_indep(base.adj, full & ~(first | second), alpha - 1)) return;
    graph_t graph = base;
    int left = graph.n++, right = graph.n++;
    graph.adj[left] = first | (edge ? BIT(right) : 0);
    graph.adj[right] = second | (edge ? BIT(left) : 0);
    for (set_t pending = first; pending; pending &= pending - 1) graph.adj[CTZ(pending)] |= BIT(left);
    for (set_t pending = second; pending; pending &= pending - 1) graph.adj[CTZ(pending)] |= BIT(right);
    g6_write(stdout, &graph);
    ++lifted;
}

int main(int argc, char **argv)
{
    if (argc < 2 || argc > 3) return 2;
    alpha = atoi(argv[1]);
    if (alpha < 2 || alpha > 9) return 2;
    int target = argc == 3 ? atoi(argv[2]) : -1;
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        int order = line[0] - 63;
        if (order < 1 || order > 60 || strlen(line) != (size_t)(2 + (order * (order - 1) / 2 + 5) / 6) ||
                g6_read(line, &base) || !g_trianglefree(&base) || !alpha_le(&base, alpha)) return 2;
        ++inputs;
        int gap = target < 0 ? -1 : target - g_edges(&base);
        if (target >= 0 && (gap < 0 || gap > 2 * alpha)) continue;
        memset(support_count, 0, sizeof support_count);
        full = BIT(order) - 1;
        hit_count = 0;
        targets(full, 0, alpha);
        for (int degree = 0; degree <= alpha; ++degree) {
            if (gap != -1 && (degree > gap || degree + alpha < gap)) continue;
            supports_rec(full, 0, degree, degree);
        }
        for (int edge = 0; edge <= 1; ++edge) {
            for (int first = 0; first <= alpha - edge; ++first) {
                for (int second = first; second <= alpha - edge; ++second) {
                    if (gap != -1 && first + second + edge != gap) continue;
                    for (unsigned int left = 0; left < support_count[first]; ++left) {
                        for (unsigned int right = (first == second ? left : 0); right < support_count[second]; ++right) {
                            ++eligible;
                            lift(edge, supports[first][left], supports[second][right]);
                        }
                    }
                }
            }
        }
    }
    fprintf(stderr, "pair lift: inputs=%lu eligible=%lu labeled outputs=%lu\n", inputs, eligible, lifted);
    return ferror(stdin) || fflush(stdout) == EOF;
}
