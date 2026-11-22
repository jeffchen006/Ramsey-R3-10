#include <algorithm>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

struct Row {
    const char *first;
    const char *end;
    const char *current;

    void space() {
        while (current != end && (*current == ' ' || *current == '\t' || *current == '\r')) ++current;
    }

    int next() {
        space();
        bool minus = current != end && *current == '-';
        if (minus) ++current;
        if (current == end || *current < '0' || *current > '9') throw std::runtime_error("non-integer LRAT token");
        int64_t value = 0;
        do {
            value = 10 * value + (*current++ - '0');
            if (value > INT32_MAX) throw std::runtime_error("large LRAT token");
        } while (current != end && *current >= '0' && *current <= '9');
        return minus ? -value : value;
    }

    bool deletion() {
        space();
        if (current == end || *current != 'd') return false;
        ++current;
        return true;
    }
};

int main(int argc, char **argv) {
    try {
        if (argc != 4) throw std::runtime_error("usage: slice_lrat CLAUSE_COUNT ORIGINAL.lrat SLICED.lrat");
        const int initial = std::stoi(argv[1]);
        if (initial <= 0) throw std::runtime_error("invalid CNF clause count");
        struct stat input{};
        const int source = open(argv[2], O_RDONLY);
        if (source < 0 || fstat(source, &input) != 0 || !input.st_size) throw std::runtime_error("input unavailable");
        const char *data = static_cast<const char *>(mmap(nullptr, input.st_size, PROT_READ, MAP_PRIVATE, source, 0));
        if (data == MAP_FAILED) throw std::runtime_error("mmap failed");
        const char *end = data + input.st_size;
        const char *position = end;
        std::vector<char> necessary;
        int target = 0;
        size_t additions = 0, kept = 0;
        while (position > data) {
            while (position > data && position[-1] == '\n') --position;
            const char *last = position;
            while (position > data && position[-1] != '\n') --position;
            if (position == last || *position == 'c') continue;
            Row read{position, last, position};
            const int number = read.next();
            if (read.deletion()) continue;
            ++additions;
            if (!target) {
                if (read.next()) continue;
                target = number;
                if (target <= initial || target > 100000000) throw std::runtime_error("invalid last empty ID");
                necessary.resize(static_cast<size_t>(target) + 1);
                necessary[target] = 1;
                read.current = position;
                (void)read.next();
            }
            if (number <= initial || number > target || !necessary[number]) continue;
            ++kept;
            while (read.next()) {}
            for (int hint = read.next(); hint; hint = read.next()) {
                if (hint < 0) throw std::runtime_error("reachable RAT row; no trim");
                if (hint >= number) throw std::runtime_error("non-preceding LRAT reference");
                necessary[hint] = 1;
            }
        }
        if (!target) throw std::runtime_error("proof has no empty conclusion");
        FILE *output = fopen(argv[3], "w");
        if (!output) throw std::runtime_error("cannot open output");
        size_t deletions = 0;
        position = data;
        while (position < end) {
            const char *first = position;
            while (position < end && *position != '\n') ++position;
            const char *last = position;
            if (position != end) ++position;
            if (first == last || *first == 'c') continue;
            Row read{first, last, first};
            const int number = read.next();
            if (read.deletion()) {
                bool any = false;
                for (int deleted = read.next(); deleted; deleted = read.next()) {
                    if (deleted < 0) throw std::runtime_error("negative deletion");
                    if (deleted <= initial || (deleted <= target && necessary[deleted])) {
                        if (!any) std::fprintf(output, "%d d", number);
                        std::fprintf(output, " %d", deleted);
                        any = true;
                    }
                }
                if (any) {
                    std::fputs(" 0\n", output);
                    ++deletions;
                }
            } else if (number <= target && necessary[number]) {
                std::fwrite(first, 1, static_cast<size_t>(last - first), output);
                std::fputc('\n', output);
                if (number == target) break;
            }
        }
        if (ferror(output) || fclose(output) != 0) throw std::runtime_error("writing failed");
        munmap(const_cast<char *>(data), input.st_size);
        close(source);
        std::fprintf(stderr, "RUP-only retained %zu of %zu additions and %zu deletion lines\n", kept, additions, deletions);
        return 0;
    } catch (const std::exception &err) {
        std::fprintf(stderr, "%s\n", err.what());
        return 1;
    }
}
