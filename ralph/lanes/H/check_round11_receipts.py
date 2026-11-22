"""Bind lane B's round-11 supply and proof receipts, not their proof semantics."""

from hashlib import sha256
from heapq import merge
from itertools import zip_longest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "scratch/B/work"
OLD = WORK / "e108_r10_micro"
NEW = WORK / "e108_r11"


def ordered_rows(stream):
    previous = b""
    for row in stream:
        assert previous < row and row.endswith(b"\n")
        yield row
        previous = row


def check_delta(prior, delta, current, expected_count):
    count = 0
    with prior.open("rb") as old, delta.open("rb") as extra, current.open("rb") as updated:
        independent_union = merge(ordered_rows(old), ordered_rows(extra))
        for lhs, rhs in zip_longest(independent_union, ordered_rows(updated)):
            assert lhs is not None and lhs == rhs, (count, lhs, rhs)
            count += 1
    assert count == expected_count
    print(f"{current.name}: exact ordered disjoint union, {count} rows")


def read_proof_log(filename, replay):
    receipts = {}
    for line in filename.read_text().splitlines():
        index, *digests, mode = line.split()
        if index == "counts":
            continue
        assert len(digests) == 2
        assert mode in ({"replay"} if replay else {"rup", "cadical"})
        assert int(index) not in receipts
        receipts[int(index)] = digests
    return receipts


def main():
    delta = (NEW / "novel.g6").read_bytes().splitlines()
    assert len(set(delta)) == len(delta) == 47
    check_delta(OLD / "critical1828.g6", NEW / "novel.g6", NEW / "critical.g6", 1875)
    check_delta(OLD / "union.g6", NEW / "novel.g6", NEW / "union.g6", 2104146)
    cliques = (NEW / "cliques.tsv").read_text().splitlines()
    clique_ids = {int(row.split("\t")[0]) for row in cliques}
    assert len(cliques) == len(clique_ids) == 37
    complements = {int(index): graph.encode("ascii") for index, graph in
                   (row.split("\t") for row in (NEW / "complement.tsv").read_text().splitlines())}
    assert len(complements) == 10
    assert not clique_ids & complements.keys()
    assert clique_ids | complements.keys() == set(range(1, 48))
    production = read_proof_log(NEW / "production.log", False)
    replay = read_proof_log(NEW / "replay.log", True)
    assert production.keys() == complements.keys() and production == replay
    for index, graph in complements.items():
        assert graph == delta[index - 1]
        artifact = NEW / "proofs" / f"{index:07d}.lrat"
        assert sha256(artifact.read_bytes()).hexdigest() == production[index][1]
    print("No semantic replay: 37 clique indices + 10 matching residual graph/digest receipts")


if __name__ == "__main__":
    main()
