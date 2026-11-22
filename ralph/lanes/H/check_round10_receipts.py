"""Check identities and stored trace hashes without regenerating proofs or roles."""

from hashlib import sha256
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]


def check_b():
    tranche = ROOT / "scratch/B/work/e108_r10_import"
    source = (tranche / "scout61.g6").read_text().splitlines()
    assert len(source) == len(set(source)) == 61
    assert (tranche / "scout61.g6").read_bytes() == (ROOT / "scratch/ideas/r009_N/handoff.g6").read_bytes()
    cliques = [int(line.split()[0]) for line in (tranche / "cliques.tsv").read_text().splitlines()]
    residual = {int(index): graph for index, graph in
                (line.split() for line in (tranche / "complement.tsv").read_text().splitlines())}
    assert sorted(cliques + list(residual)) == list(range(1, 62))
    assert len(cliques) == 57 and len(residual) == 4
    assert all(source[index - 1] == graph for index, graph in residual.items())
    receipts = [line.split() for line in (tranche / "replay.log").read_text().splitlines()
                if not line.startswith("counts ")]
    assert sorted(int(fields[0]) for fields in receipts) == sorted(residual)
    for index, cnf, proof, status in receipts:
        assert status == "replay" and re.fullmatch(r"[0-9a-f]{64}", cnf)
        assert sha256((tranche / "proofs" / f"{int(index):07d}.lrat").read_bytes()).hexdigest() == proof
    print(f"B: 61 scout keys partitioned into 57 clique receipts and proof IDs {sorted(residual)}, hashes match")


def check_g():
    strip = ROOT / "scratch/G/round10"
    from_a = (ROOT / "scratch/A/strip10/roles.26.9.keys").read_text().splitlines()
    from_g = (strip / "r26.d9.keys").read_text().splitlines()
    assert len(from_a) == len(set(from_a)) == 215 and sorted(from_a) == sorted(from_g)
    assert not (strip / "r26.d9.bound/unclosed.keys").read_text().strip()
    expected = {"_".join(line.split()[:-1]) for line in from_a}
    receipts = [line.split() for line in (strip / "r26.d9.bound/certificates.tsv").read_text().splitlines()]
    assert len(receipts) == 215 and {row[0] for row in receipts} == expected
    for key, cnf, proof, path, size in receipts:
        assert re.fullmatch(r"[0-9a-f]{64}", cnf)
        assert Path(path).name == key + ".lrat.gz"
        data = (strip / path).read_bytes()
        assert len(data) == int(size) and sha256(data).hexdigest() == proof
    print("G: all 215 complete ordered role rows match A, receipt IDs and proof hashes match")


if __name__ == "__main__":
    check_b()
    check_g()
