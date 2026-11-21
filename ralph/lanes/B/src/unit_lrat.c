#include <stdio.h>
#include <stdlib.h>

enum { MAX_VARS = 4096, MAX_CLAUSES = 12000, MAX_LITERALS = 100000 };
static int begin[MAX_CLAUSES+1];
static int literals[MAX_LITERALS];
static signed char assigned[MAX_VARS+1];
static int hints[MAX_VARS];

int main(int argc, char **argv)
{
    if (argc != 3) return 2;
    FILE *cnf = fopen(argv[1], "r");
    if (!cnf) return 2;
    int variables, clauses;
    if (fscanf(cnf, "p cnf %d %d", &variables, &clauses) != 2 ||
            variables < 0 || variables > MAX_VARS || clauses < 1 || clauses > MAX_CLAUSES) return 2;
    int used = 0;
    for (int clause = 0; clause < clauses; ++clause) {
        int literal;
        while (1) {
            if (fscanf(cnf, "%d", &literal) != 1 || literal < -variables || literal > variables) return 2;
            if (!literal) break;
            if (used == MAX_LITERALS) return 2;
            literals[used++] = literal;
        }
        begin[clause+1] = used;
    }
    if (fscanf(cnf, " %*1[^ \t\r\n]") != EOF) return 2;
    fclose(cnf);
    int hint_count = 0, previous;
    do {
        previous = hint_count;
        for (int clause = 0; clause < clauses; ++clause) {
            int unit = 0, skip = 0;
            for (int offset = begin[clause]; offset < begin[clause+1]; ++offset) {
                int literal = literals[offset];
                int value = assigned[abs(literal)] * (literal > 0 ? 1 : -1);
                if (value > 0 || (!value && unit)) { skip = 1; break; }
                if (!value) unit = literal;
            }
            if (skip) continue;
            if (!unit) {
                FILE *proof = fopen(argv[2], "w");
                if (!proof) return 2;
                fprintf(proof, "%d 0", clauses+1);
                for (int index = 0; index < hint_count; ++index) fprintf(proof, " %d", hints[index]);
                fprintf(proof, " %d 0\n", clause+1);
                return fclose(proof) ? 2 : 20;
            }
            hints[hint_count++] = clause+1;
            assigned[abs(unit)] = unit > 0 ? 1 : -1;
        }
    } while (hint_count != previous);
    return 10;
}
