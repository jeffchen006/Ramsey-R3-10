#include <stdio.h>
#include "nauty.h"

int main(void)
{
    enum { order = 10, words = SETWORDSNEEDED(order) };
    graph graph_data[order * words];
    int lab[order], ptn[order], orbits[order];
    statsblk stats;
    DEFAULTOPTIONS_GRAPH(options);
    EMPTYGRAPH(graph_data, words, order);
    for (int vertex = 0; vertex < 5; ++vertex) {
        ADDONEEDGE(graph_data, vertex, (vertex + 1) % 5, words);
        ADDONEEDGE(graph_data, vertex, vertex + 5, words);
        ADDONEEDGE(graph_data, vertex + 5, (vertex + 2) % 5 + 5, words);
    }
    nauty_check(WORDSIZE, words, order, NAUTYVERSIONID);
    densenauty(graph_data, lab, ptn, orbits, &options, &stats, words, order, NULL);
    printf("grpsize=%.0f\n", stats.grpsize1);
    return stats.errstatus || stats.grpsize1 != 120 || stats.grpsize2 != 0;
}
