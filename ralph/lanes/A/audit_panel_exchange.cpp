#include <algorithm>
#include <array>
#include <charconv>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

extern "C" {
struct evp_md_ctx_st;
struct evp_md_st;
evp_md_ctx_st* EVP_MD_CTX_new();
void EVP_MD_CTX_free(evp_md_ctx_st*);
const evp_md_st* EVP_sha256();
int EVP_DigestInit_ex(evp_md_ctx_st*, const evp_md_st*, void*);
int EVP_DigestUpdate(evp_md_ctx_st*, const void*, std::size_t);
int EVP_DigestFinal_ex(evp_md_ctx_st*, unsigned char*, unsigned int*);
}

using Record = std::array<unsigned char, 8>;
using ID = std::array<int, 3>;

void demand(bool ok, const char* why) {
    if (!ok) throw std::runtime_error(why);
}

class Census {
    evp_md_ctx_st* ctx_ = EVP_MD_CTX_new();
    std::array<Record, 8192> buffer_;
    std::size_t used_ = 0;
    std::array<std::uint64_t, 2> counts_{};

    void flush() {
        demand(EVP_DigestUpdate(ctx_, buffer_.data(), used_ * sizeof(Record)) == 1, "SHA-256 update");
        used_ = 0;
    }

public:
    Census() { reset(); }
    Census(const Census&) = delete;
    Census& operator=(const Census&) = delete;
    ~Census() { EVP_MD_CTX_free(ctx_); }

    void reset() {
        demand(ctx_ && EVP_DigestInit_ex(ctx_, EVP_sha256(), nullptr) == 1, "SHA-256 init");
        used_ = 0;
        counts_ = {};
    }

    void add(const Record& row, int flip) {
        ++counts_[flip];
        buffer_[used_++] = row;
        if (used_ == buffer_.size()) flush();
    }

    void print(int low, int high, const char* kind) {
        flush();
        std::array<unsigned char, 32> digest{};
        unsigned int length = 0;
        demand(EVP_DigestFinal_ex(ctx_, digest.data(), &length) == 1 && length == digest.size(), "SHA-256 final");
        static constexpr char hex[] = "0123456789abcdef";
        std::string text;
        for (unsigned char byte : digest) {
            text.push_back(hex[byte >> 4]);
            text.push_back(hex[byte & 15]);
        }
        std::cout << low << ' ' << high << ' ' << kind << ' ' << counts_[0] << ' ' << counts_[1] << ' ' << text << '\n';
    }
};

template <typename Action>
void read_records(int size, int low, int high, Action action) {
    std::array<Record, 8192> buffer;
    ID previous{-1, -1, -1};
    while (auto bytes = std::fread(buffer.data(), 1, sizeof(buffer), stdin)) {
        demand(bytes % sizeof(Record) == 0, "truncated packed record");
        for (std::size_t index = 0; index < bytes / sizeof(Record); ++index) {
            const auto& row = buffer[index];
            const ID id{row[0] + 256 * row[1], row[2] + 256 * row[3], row[4]};
            demand(id[0] >= low && id[0] < high && id[1] < size && id[2] < 2 &&
                   row[5] == 0 && row[6] == 0 && row[7] == 0, "packed ID outside domain or nonzero padding");
            demand(previous < id, "duplicate or unordered packed ID");
            previous = id;
            action(id, row);
        }
    }
    demand(std::feof(stdin) && !std::ferror(stdin), "packed stream read error");
}

void upper(int size, int low, int high) {
    Census roster, diagonal;
    read_records(size, low, high, [&](const ID& id, const Record& row) {
        if (id[0] <= id[1]) roster.add(row, id[2]);
        if (id[0] == id[1]) diagonal.add(row, id[2]);
    });
    roster.print(low, high, "HHrep");
    diagonal.print(low, high, "HHdiag");
}

void full(int size, int cut, int step) {
    enum Kind { Ordered, LL, LH, HL, HH, Rep, Diag, HHL, LLup, LLdown, KindCount };
    constexpr std::array<const char*, KindCount> names{
        "ordered", "LL", "LH", "HL", "HH", "HHrep", "HHdiag", "HHlower", "LLupper", "LLlower"};
    std::array<Census, KindCount> shard;
    Census entire;
    struct References {
        std::vector<unsigned> pending;
        std::size_t cursor = 0;
    };
    std::vector<References> refs(size);
    int low = 0;
    auto next = [&](int start) {
        return start < cut ? std::min(start + 2 * step, cut) : std::min(start + step, size);
    };
    int high = next(low);
    auto finish_shard = [&] {
        for (int kind = 0; kind < KindCount; ++kind) {
            shard[kind].print(low, high, names[kind]);
            shard[kind].reset();
        }
        low = high;
        high = next(low);
    };
    auto match = [&](int owner, int source, int flip) {
        auto& ref = refs[owner];
        demand(ref.cursor < ref.pending.size() && ref.pending[ref.cursor] == unsigned(2 * source + flip),
               "wrong or skipped transposed reference");
        ++ref.cursor;
    };
    read_records(size, 0, size, [&](const ID& id, const Record& row) {
        const auto [left, right, flip] = id;
        while (left >= high) finish_shard();
        entire.add(row, flip);
        shard[Ordered].add(row, flip);
        if (left < cut && right < cut) {
            shard[LL].add(row, flip);
            if (left < right) shard[LLup].add(row, flip);
            if (right < left) shard[LLdown].add(row, flip);
        } else if (left < cut) {
            shard[LH].add(row, flip);
        } else if (right < cut) {
            shard[HL].add(row, flip);
        } else {
            shard[HH].add(row, flip);
            if (left <= right) shard[Rep].add(row, flip);
            if (left == right) shard[Diag].add(row, flip);
            if (left > right) shard[HHL].add(row, flip);
        }
        if (left < right) refs[left].pending.push_back(2 * right + flip);
        if (left > right) match(right, left, flip);
    });
    for (const auto& ref : refs) demand(ref.cursor == ref.pending.size(), "unconsumed transposed reference");
    while (low < size) finish_shard();
    entire.print(0, size, "full");
}

int parse(const std::string& token) {
    int value = -1;
    auto [end, code] = std::from_chars(token.data(), token.data() + token.size(), value);
    demand(code == std::errc{} && end == token.data() + token.size(), "invalid integer argument");
    return value;
}

int main(int argc, char** argv) try {
    demand(argc == 5, "usage: panel_exchange (full SIZE CUT STEP | upper SIZE LOW HIGH) < packed");
    const std::string mode = argv[1];
    const int size = parse(argv[2]), start = parse(argv[3]), end = parse(argv[4]);
    demand(size > 0 && size <= 65535, "invalid ID limit");
    if (mode == "full") {
        demand(0 < start && start < size && 0 < end && end <= size, "invalid cut/step");
        full(size, start, end);
    } else if (mode == "upper") {
        demand(0 <= start && start < end && end <= size, "invalid upper interval");
        upper(size, start, end);
    } else {
        demand(false, "unknown mode");
    }
    std::cout.flush();
    demand(bool(std::cout), "digest output error");
    return 0;
} catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 2;
}
