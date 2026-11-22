"""Overlay the prejoin pilot on the unchanged round-7 incidence source."""

import argparse
from pathlib import Path


def splice(text, target, replacement):
    assert text.count(target) == 1, target
    return text.replace(target, replacement)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    lane = Path(__file__).parent
    request = (lane / 'p2_request_cache.hpp').read_text()
    request = splice(request, 'public:\n', 'public:\n#include "p2_prejoin_methods.hpp"\n')
    (args.output / 'p2_prejoin_request.inc').write_text(request)

    code = (lane / 'p2_incidence.cpp').read_text()
    code = splice(code, '#include "p2_request_cache.hpp"',
                  '#include "p2_prejoin_request.inc"\n#include "p2_prejoin_index.hpp"')
    code = splice(code, '    rhs.deficits.front() =',
                  '    control_prejoin(left_cache, rhs);\n    rhs.deficits.front() =')
    code = splice(code, '    Stages stages;', '    Stages stages;\n    PrejoinStats indexed;')
    code = splice(code, '        for (const Mark& first : lhs) {', '''        std::vector<std::vector<std::vector<TwoSiteKey>>> right_keys;
        if (prejoin_budget >= 0)
            for (const auto& sides : right_data) {
                auto& keys = right_keys.emplace_back();
                for (const auto& side : sides) keys.push_back(two_site_keys(side, prejoin_budget));
            }
        for (const Mark& first : lhs) {''')
    code = splice(code, '            for (std::size_t right_index',
                  '            std::vector<PrejoinIndex> small_index(prejoin_budget < 0 ? 0 : first.packs.size());\n'
                  '            for (std::size_t right_index')
    code = splice(code, '                std::vector<Outcome> relaxed;',
                  '#include "p2_prejoin_loop.inc"\n                std::vector<Outcome> relaxed;')
    code = splice(code, '    assert(stages.raw_maps == expected_raw);', '''    assert(stages.raw_maps == expected_raw);
    if (prejoin_budget >= 0)
        std::cout << "prejoin budget=" << prejoin_budget << " pruned=" << indexed.pruned
                  << " evaluated=" << indexed.evaluated << " reused=" << indexed.reused
                  << " queries=" << indexed.queries << " audited=" << indexed.audited
                  << " entries=" << indexed.entries << '\\n';''')
    code = splice(code, '    } else {\n        const std::string mode = argv[1];', '''    } else if (std::string(argv[1]) == "idx" || std::string(argv[1]) == "idx-audit") {
        assert(argc == 8);
        std::ifstream second(argv[3]);
        std::ofstream output(argv[4]);
        assert(second && output);
        prejoin_budget = std::stoi(argv[7]);
        prejoin_audit = std::string(argv[1]) == "idx-audit";
        assert(prejoin_budget >= 0 && prejoin_budget <= 91);
        pilot(input, second, 1, 1, 16000, false, true, std::stoull(argv[5]), nullptr,
              read_profile(argv[6]), &output);
        assert(output);
    } else {
        const std::string mode = argv[1];''')
    (args.output / 'p2_prejoin.generated.cpp').write_text(code)


if __name__ == '__main__':
    main()
