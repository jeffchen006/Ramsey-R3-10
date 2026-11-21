#!/usr/bin/env python3
"""Find numerical Farkas multipliers; accept only after a rational box check."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
from time import process_time
from typed_lp import PRESENT, baseline, build

HIGHS_OPTIONS = {"threads": 1}


def verify(model, multiplier):
    if not multiplier or any(not 0 <= index < len(model.rows) or value <= 0
                            for index, value in multiplier.items()):
        return False
    weighted_rhs = Fraction(0)
    weighted_col = {key: Fraction(0) for key in model.bounds}
    for index, weight in multiplier.items():
        row, rhs, _ = model.rows[index]
        weighted_rhs += weight * rhs
        for key, coefficient in row.items():
            weighted_col[key] += weight * coefficient
    box_min = sum(weight * model.bounds[key] for key, weight in weighted_col.items() if weight < 0)
    return box_min > weighted_rhs


def solve(model):
    from warnings import filterwarnings

    import numpy as np
    from scipy.optimize import OptimizeWarning, linprog
    from scipy.sparse import csr_matrix, eye, hstack, vstack

    filterwarnings("ignore", message=r"Unrecognized options detected: .*threads", category=OptimizeWarning)
    columns = {key: index for index, key in enumerate(model.bounds)}
    data, row_index, col_index, rhs = [], [], [], []
    for index, (row, bound, _) in enumerate(model.rows):
        rhs.append(bound)
        for key, coefficient in row.items():
            row_index.append(index)
            col_index.append(columns[key])
            data.append(coefficient)
    matrix = csr_matrix((data, (row_index, col_index)), shape=(len(rhs), len(columns)))
    result = linprog(np.zeros(len(columns)), A_ub=matrix, b_ub=rhs,
                     bounds=list(zip([0] * len(columns), model.bounds.values())), method="highs",
                     options=HIGHS_OPTIONS)
    if result.status == 0:
        return "feasible", None
    if result.status != 2:
        return f"solver_status_{result.status}", None
    for normalise in (True, False):
        dual = -matrix.T.tocsr()
        dual_rhs = np.zeros(len(columns))
        if normalise:
            dual = vstack((dual, csr_matrix(np.ones((1, len(rhs))))), format="csr")
            dual_rhs = np.append(dual_rhs, 1)
        result = linprog(rhs, A_ub=dual, b_ub=dual_rhs,
                         bounds=(0, None if normalise else 1), method="highs", options=HIGHS_OPTIONS)
        if result.status != 0 or result.fun >= 0:
            continue
        for denominator in (10**3, 10**6, 10**9):
            multiplier = {index: Fraction(float(value)).limit_denominator(denominator)
                          for index, value in enumerate(result.x) if value > 0}
            multiplier = {index: value for index, value in multiplier.items() if value}
            if verify(model, multiplier):
                return "cert", {str(index): str(value) for index, value in multiplier.items()}
    dual = vstack((-matrix.T, csr_matrix(np.ones((1, len(rhs))))), format="csr")
    bound_columns = vstack((-eye(len(columns), format="csr"),
                            csr_matrix((1, len(columns)))), format="csr")
    result = linprog(rhs + list(model.bounds.values()), A_ub=hstack((dual, bound_columns), format="csr"),
                     b_ub=np.append(np.zeros(len(columns)), 1), bounds=(0, None), method="highs",
                     options=HIGHS_OPTIONS)
    if result.status == 0 and result.fun < 0:
        multiplier = {index: Fraction(float(value)).limit_denominator(10**8)
                      for index, value in enumerate(result.x[:len(rhs)]) if value > 0}
        multiplier = {index: value for index, value in multiplier.items() if value}
        if verify(model, multiplier):
            return "cert", {str(index): str(value) for index, value in multiplier.items()}
    return "not_certified", None


def case_model(distribution, family, threshold):
    counts = dict(zip(baseline.DEGS, distribution))
    lower = {degree: baseline.e9(degree) for degree in baseline.DEGS}
    lower[8], lower[9] = 97, threshold + 1
    return build(counts, lower, 40, 9, True, PRESENT[family])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--sample", type=int)
    parser.add_argument("--families", nargs="+", choices=PRESENT, default=list(PRESENT))
    parser.add_argument("--threshold", type=int, default=87)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--retarget", action="store_true")
    mode.add_argument("--tighten", action="store_true")
    args = parser.parse_args()
    if args.verify:
        count = 0
        for line in args.output.read_text().splitlines():
            record = json.loads(line)
            if record["status"] == "cert":
                model = case_model(record["n"], record["family"], record["threshold"])
                assert verify(model, {int(key): Fraction(value) for key, value in record["y"].items()}), record
                count += 1
        print(f"exact verification: {count} certificates, 0 failures for {args.output}")
        return
    rows = [row for row in json.loads(args.baseline.read_text())["survivors"]
            if row["t9_U8"] > args.threshold and row["e"] < 180]
    if args.sample:
        rows = rows[::max(1, len(rows) // args.sample)][:args.sample]
    summary = {}
    started = process_time()
    with args.output.open("w") as stream:
        for family in args.families:
            stats = summary[family] = {}
            for row in rows:
                def trial(threshold):
                    model = case_model(row["n"], family, threshold)
                    status, multiplier = solve(model)
                    record = {"n": row["n"], "e": row["e"], "family": family,
                              "threshold": threshold, "status": status}
                    if multiplier:
                        record["y"] = multiplier
                    print(json.dumps(record, separators=(",", ":")), file=stream)
                    stats[status] = stats.get(status, 0) + 1
                    return status == "cert"

                if not args.tighten:
                    trial(row["t9_U8"] - 1 if args.retarget else args.threshold)
                    continue
                high = row["t9_U8"]
                if trial(high - 1):
                    high -= 1
                    low = args.threshold
                    while low < high:
                        mid = (low + high) // 2
                        if trial(mid):
                            high = mid
                        else:
                            low = mid + 1
            stream.flush()
            print(f"{family}: {stats}; cumulative CPU seconds {process_time() - started:.2f}", flush=True)


if __name__ == "__main__":
    main()
