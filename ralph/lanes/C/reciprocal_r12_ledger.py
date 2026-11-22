from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys

from pysat.formula import CNF

from reciprocal_audit import ROOT, SOURCE22, decode
from reciprocal_r12_projection import Projection


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def to_mask(vertices):
    return sum(1 << vertex for vertex in vertices)


def from_mask(mask):
    return {vertex for vertex in range(mask.bit_length()) if (mask >> vertex) & 1}


def valid_cap_clause(clause, base, var, cap):
    if len(clause) != len(set(clause)) or not clause or any(-lit not in var for lit in clause):
        return False
    used = {var[-lit] for lit in clause}
    expanded = [row.copy() for row in base]
    for first, second in used:
        expanded[first].add(second)
        expanded[second].add(first)
    return any(len(first & second) > cap for first, second in combinations(expanded, 2))


def expected_keys(hosts, tight_file):
    keys = [tuple(map(int, line.split())) for line in tight_file.read_text().splitlines()]
    assert len(set(keys)) == len(keys) == 1307
    e20 = [key for key in keys if sum(map(len, hosts[key[0]])) == 130]
    assert len(e20) == 9 and Counter(key[0] for key in e20) == {8: 6, 10: 2, 28: 1}
    expected = set()
    memberships = [(28 + index, frozenset(root for root in range(3) if (kind >> root) & 1))
                   for index, kind in enumerate((1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6))]
    classes = [tuple(site for site, membership in memberships if membership == target)
               for target in sorted({membership for _, membership in memberships}, key=lambda row: to_mask(row))]
    outside = tuple(site for site, _ in memberships)
    roots = [{site for site, membership in memberships if root in membership} for root in range(3)]
    for key in e20:
        local = set()
        row, core, *bits = key
        masks = [from_mask(mask) for mask in bits]
        shared = set.intersection(*masks)
        assert len(shared) == 2 and all(first & second == shared for first, second in combinations(masks, 2))
        assert set(range(22)) - set.union(*masks) == from_mask(core)
        first, second = sorted(shared)
        host = hosts[row]
        for left, right in product(combinations(outside, 6 - len(host[first])),
                                   combinations(outside, 6 - len(host[second]))):
            left, right = set(left), set(right)
            if len(left & right) + len(host[first] & host[second]) > 2:
                continue
            if any(len(row & fixed) > 2 for row in (left, right) for fixed in roots):
                continue
            mapped_left, mapped_right = set(), set()
            for block in classes:
                codes = [(site in left, site in right) for site in block]
                for site, (flag_left, flag_right) in zip(block, sorted(codes, reverse=True), strict=True):
                    if flag_left:
                        mapped_left.add(site)
                    if flag_right:
                        mapped_right.add(site)
            local.add((key, (to_mask(mapped_left), to_mask(mapped_right))))
        assert len(local) == 36
        expected.update(local)
    return expected


def main(folder, tight_file, recheck):
    hosts = [decode(line) for line in SOURCE22.read_text().splitlines()]
    expected = expected_keys(hosts, tight_file)
    templates = (1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6)
    checked, cap_axioms = 0, 0
    for line in (folder / 'projection.jsonl').read_text().splitlines():
        receipt = json.loads(line)
        index, key, wings = receipt['index'], tuple(receipt['key']), tuple(receipt['wings'])
        assert checked == index and receipt['result'] == 'dual-LRAT' and receipt['edges'] == 20 and not receipt['model']
        expected.remove((key, wings))
        prefix = folder / f'pilot-{index:02d}'
        cnf_path, proof_path = prefix.with_suffix('.cnf'), prefix.with_suffix('.lrat')
        assert [digest(cnf_path), digest(proof_path)] == receipt['receipt']
        cnf = CNF(from_file=str(cnf_path))
        projection = Projection([to_mask(row) for row in hosts[key[0]]], key[2:], 9, 5, templates, wings)
        assert projection.target == 20 and cnf.nv == projection.formula.nv
        clauses = projection.formula.clauses
        assert cnf.clauses[:len(clauses)] == clauses
        assert set(receipt['counts']) <= {'cap'}
        extras = cnf.clauses[len(clauses):]
        assert len(extras) == receipt['counts'].get('cap', 0)
        graph = [from_mask(mask) for mask in projection.lower]
        variables = {literal: endpoints for endpoints, literal in projection.vars.items()}
        assert all(valid_cap_clause(clause, graph, variables, 5) for clause in extras)
        assert not valid_cap_clause([1], graph, variables, 5)
        cap_axioms += len(extras)
        for checker, signature in [('cake_lpr', 's VERIFIED UNSAT'), ('lrat-check', 'c VERIFIED')]:
            assert signature in prefix.with_suffix('.' + checker).read_text()
            if recheck:
                command = ['timeout', '8', 'prlimit', '--cpu=6:7', str(ROOT / 'opt/bin' / checker),
                           str(cnf_path), str(proof_path)]
                proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                assert proc.returncode == 0 and signature in proc.stdout
        checked += 1
    assert not expected and checked == 324
    print('9 independently enumerated marks, 324 independently enumerated wings; every ordered key and hash matches')
    print(checked, 'reconstructed CNF prefixes;', cap_axioms, 'locally verified cap axioms; no other lazy clauses')
    print('fresh dual checker runs' if recheck else 'archived dual checker receipts', 2 * checked)


if __name__ == '__main__':
    assert len(sys.argv) in (3, 4)
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:] == ['recheck'])
