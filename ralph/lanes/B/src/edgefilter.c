#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
    if (argc < 3) return 2;
    int order = atoi(argv[1]), cap = atoi(argv[2]);
    int width = 2+(order*(order-1)/2+5)/6;
    char line[1024];
    unsigned char pop[256];
    memset(pop, 63, sizeof pop);
    for (int c = 63; c <= 126; ++c) pop[c] = __builtin_popcount(c-63);
    for (int idx = 3; idx < argc; ++idx) {
        FILE *input = fopen(argv[idx], "r");
        if (!input) { perror(argv[idx]); return 1; }
        while (fgets(line, sizeof line, input)) {
            if (line[0] != order+63 || line[width-1] != '\n') return 1;
            int edges = 0;
            for (int pos = 1; pos < width-1; ++pos) edges += pop[(unsigned char)line[pos]];
            if (edges <= cap && fwrite(line, 1, width, stdout) != (size_t)width) return 1;
        }
        if (ferror(input)) { perror(argv[idx]); return 1; }
        fclose(input);
    }
    return fflush(stdout) == EOF;
}
