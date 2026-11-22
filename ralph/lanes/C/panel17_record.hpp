#pragma once
#include <array>
#include <ostream>
#include <stdexcept>

inline void panel17_record(int left, int right, int flip, int depth) {
    std::array<unsigned char, 8> bytes{};
    const std::array<int, 4> values{left, right, flip, depth};
    for (unsigned index = 0; index < values.size(); ++index) {
        if (values[index] < 0 || values[index] >= 65536) throw std::runtime_error("record range");
        bytes[2 * index] = static_cast<unsigned char>(values[index]);
        bytes[2 * index + 1] = static_cast<unsigned char>(values[index] >> 8);
    }
    std::cout.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
}
