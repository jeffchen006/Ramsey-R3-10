#!/usr/bin/env python3
"""Combine pinned and newly certified upper bounds, keeping the exact witness."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from scan import case_model, verify
from fractions import Fraction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pinned", required=True, type=Path)
    parser.add_argument("--table", required=True, type=Path)
    parser.add_argument("--certificate-output", required=True, type=Path)
    parser.add_argument("logs", nargs="+", type=Path)
    args = parser.parse_args()
    baseline = {tuple(row["n"]): row["t9_U8"] for row in json.loads(args.pinned.read_text())["survivors"]
                if row["t9_U8"] > 87 and row["e"] < 180}
    best = {}
    for log in args.logs:
        with log.open() as stream:
            for line in stream:
                record = json.loads(line)
                if record["status"] != "cert":
                    continue
                key, threshold = tuple(record["n"]), record["threshold"]
                if key not in baseline or threshold >= baseline[key]:
                    continue
                if key in best and threshold >= best[key]["threshold"]:
                    continue
                model = case_model(key, record["family"], threshold)
                assert verify(model, {int(index): Fraction(value) for index, value in record["y"].items()}), record
                best[key] = record
    with args.table.open("w") as table, args.certificate_output.open("w") as certificates:
        writer = csv.writer(table, lineterminator="\n")
        writer.writerow(["e", "n6", "n7", "n8", "n9", "baseline_t9_U8", "certified_t9_upper", "evidence"])
        updated = Counter()
        for distribution, original in baseline.items():
            record = best.get(distribution)
            upper = record["threshold"] if record else original
            updated[upper] += 1
            edges = sum(degree * count for degree, count in zip(range(4, 10), distribution)) // 2
            writer.writerow([edges, *distribution[2:], original, upper, record["family"] if record else "pinned"])
            if record:
                print(json.dumps(record, separators=(",", ":")), file=certificates)
    print(f"Improved {len(best)}/{len(baseline)}; updated histogram {dict(sorted(updated.items()))}")
    for threshold in (87, 88, 89, 90, 91, 92):
        old = sum(count <= threshold for count in baseline.values())
        new = sum(count for upper, count in updated.items() if upper <= threshold)
        print(f"<= {threshold}: pinned {old}; updated {new}; additional {new - old}; remaining {len(baseline) - new}")


if __name__ == "__main__":
    main()
