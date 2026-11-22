bool two_requests(unsigned first, unsigned second, int wing_union, bool adjacent,
                  const std::array<Mask, 64>& image) {
    if (!valid_base) return false;
    auto first_choice = request(image[first & 63], (first >> 6) & 3, first >> 8);
    auto second_choice = request(image[second & 63], (second >> 6) & 3, second >> 8);
    return !first_choice.second->empty() && !second_choice.second->empty() &&
           compatible(first_choice, second_choice, wing_union, adjacent);
}
