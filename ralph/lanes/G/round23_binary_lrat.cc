#include <cstdint>
#include <cstdio>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

struct Record {
    const uint8_t *data;
    int identifier;
    bool adding;
};

int token(const uint8_t *&position, const uint8_t *end) {
    uint64_t result = 0;
    for (unsigned shift = 0; shift < 35 && position < end; shift += 7) {
        const unsigned byte = *position++;
        result |= uint64_t(byte & 127) << shift;
        if (!(byte & 128)) {
            if ((result >> 1) > INT32_MAX || result == 1) throw std::runtime_error("invalid token");
            const int value = result >> 1;
            return result & 1 ? -value : value;
        }
    }
    throw std::runtime_error("unterminated token");
}

int main(int argc, char **argv) {
    try {
        if (argc < 4 || argc > 5) throw std::runtime_error("usage: binary_lrat clauses source output [all]");
        const int original = std::stoi(argv[1]);
        if (original <= 0) throw std::runtime_error("invalid clause count");
        const bool keep_all = argc == 5 && std::string(argv[4]) == "all";
        const int source = open(argv[2], O_RDONLY);
        struct stat info{};
        if (source < 0 || fstat(source, &info) || !info.st_size) throw std::runtime_error("proof unavailable");
        const auto *data = static_cast<const uint8_t *>(mmap(nullptr, info.st_size, PROT_READ, MAP_PRIVATE, source, 0));
        if (data == MAP_FAILED) throw std::runtime_error("mmap failed");
        const uint8_t *position = data, *end = data + info.st_size;
        std::vector<Record> rows;
        int previous = original, finish = 0;
        while (position < end) {
            const auto type = *position++;
            if (type == 'd') {
                rows.push_back({position, previous, false});
                while (token(position, end)) {}
            } else if (type == 'a') {
                const int identifier = token(position, end);
                if (identifier <= previous || identifier > 100000000) throw std::runtime_error("invalid line ID");
                previous = identifier;
                rows.push_back({position, identifier, true});
                const bool empty = *position == 0;
                while (token(position, end)) {}
                for (int hint = token(position, end); hint; hint = token(position, end)) {
                    if (hint < 1 || hint >= identifier) throw std::runtime_error("non-RUP or nonpreceding hint");
                }
                if (empty) {
                    finish = identifier;
                    if (position != end) throw std::runtime_error("unexpected trailing binary steps");
                }
            } else {
                throw std::runtime_error("unknown binary marker");
            }
        }
        if (!finish) throw std::runtime_error("no empty conclusion");
        std::vector<char> needed(static_cast<size_t>(finish) + 1, keep_all);
        needed[finish] = 1;
        for (auto row = rows.rbegin(); row != rows.rend(); ++row) {
            if (!row->adding || !needed[row->identifier]) continue;
            position = row->data;
            while (token(position, end)) {}
            for (int hint = token(position, end); hint; hint = token(position, end)) needed[hint] = 1;
        }
        FILE *output = fopen(argv[3], "w");
        if (!output) throw std::runtime_error("cannot write ASCII proof");
        size_t kept = 0;
        for (const auto &row : rows) {
            position = row.data;
            if (row.adding && needed[row.identifier]) {
                ++kept;
                std::fprintf(output, "%d ", row.identifier);
                for (int value = token(position, end); value; value = token(position, end))
                    std::fprintf(output, "%d ", value);
                std::fputs("0 ", output);
                for (int hint = token(position, end); hint; hint = token(position, end))
                    std::fprintf(output, "%d ", hint);
                std::fputs("0\n", output);
            } else if (!row.adding) {
                bool any = false;
                for (int value = token(position, end); value; value = token(position, end)) {
                    if (value <= 0 || value > row.identifier) throw std::runtime_error("invalid deletion");
                    if (value > original && !needed[value]) continue;
                    if (!any) std::fprintf(output, "%d d", row.identifier);
                    std::fprintf(output, " %d", value);
                    any = true;
                }
                if (any) std::fputs(" 0\n", output);
            }
        }
        if (ferror(output) || fclose(output)) throw std::runtime_error("writing failed");
        std::fprintf(stderr, "converted %zu binary records to LRAT with %zu retained additions\n", rows.size(), kept);
        munmap(const_cast<uint8_t *>(data), info.st_size);
        close(source);
        return 0;
    } catch (const std::exception &error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
