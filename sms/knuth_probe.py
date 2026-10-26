#!/usr/bin/env python3
"""Knuth-style random-probe estimate of SMS cube-and-conquer cost (agent sms).

One probe: F_0 = base CNF. At level l: lookahead-cube F_l with edge cutoff C_l (smsg
--assignment-cutoff C_l --cutoff-edge-vars-only --lookahead-only-edge-vars), giving b_l cubes and
cubing time c_l. Pick one cube at random. Try to solve F_l + cube units (time limit T). If solved in time t: stop.
Else F_{l+1} = F_l + the cube as unit clauses, next level (C_{l+1} = C_l + step).
Estimate of total CPU = c_0 + b_0 (c_1 + b_1 (c_2 + ... + b_L t)).
(The last solve attempt that timed out is counted only as its cubing replacement.)
Writes one JSON line per level and a final line to OUT.

usage: knuth_probe.py CPU SEED BASE.cnf N OUT C0 STEP T "smsg args"
"""
import json
import os
import random
import subprocess
import sys
import time

SMSG = "./sms/sms-src/build/src/smsg"


MEM_KB = int(os.environ.get("PROBE_MEM_KB", 4 * 1024 * 1024))  # hard cap per smsg (ulimit -v, KB); prlimit --as segfaults smsg here


def run(cpu, args, timeout):
    """Run smsg with a hard memory cap; stdout goes to a temp file, not to RAM.
    Returns (rc or None on timeout, wanted stdout lines joined, seconds). rc -9/-6/... on mem kill."""
    import tempfile
    t0 = time.time()
    with tempfile.TemporaryFile(mode="w+") as fo:
        try:
            p = subprocess.run(["bash", "-c", f'ulimit -v {MEM_KB} && exec "$@"', "smsg", "taskset", "-c", cpu, "nice", "-n", "5", SMSG] + args,
                               stdout=fo, stderr=subprocess.DEVNULL, timeout=timeout)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = None
        fo.seek(0)
        keep = [l for l in fo if l.startswith(("a ", "[(", "s "))]  # cubes, graphs, status only
    return rc, "".join(keep), time.time() - t0


def main():
    cpu, seed, base, n, out, c0, step, tlim, smargs = sys.argv[1:10]
    n, c0, step, tlim = int(n), int(c0), int(step), float(tlim)
    smargs = smargs.split()
    rnd = random.Random(int(seed))
    work = out + ".work"
    os.makedirs(work, exist_ok=True)
    cur = base
    level = 0
    levels = []
    log = open(out, "a")
    while True:
        C = c0 + level * step
        rc, so, ct = run(cpu, ["-v", str(n), "--dimacs", cur] + smargs +
                         ["--prerun", "20", "--assignment-cutoff", str(C), "--cutoff-edge-vars-only",
                          "--lookahead-only-edge-vars"], 4 * 3600)
        if any(l.startswith("[(") for l in so.splitlines()):
            log.write(json.dumps({"seed": seed, "level": level, "event": "GRAPH_FOUND_IN_CUBING"}) + "\n")
            open(out + ".FOUND_graph.txt", "w").write(so)
            return
        cubes = [l for l in so.splitlines() if l.startswith("a ")]
        rec = {"seed": seed, "level": level, "cutoff": C, "cubes": len(cubes), "cube_s": round(ct, 1), "rc": rc}
        if rc is None or rc != 0:
            rec["event"] = "CUBING_TIMEOUT" if rc is None else "CUBING_FAILED_RC%d" % rc
            log.write(json.dumps(rec) + "\n"); log.flush()
            return
        if not cubes:
            rec["event"] = "REFUTED_IN_CUBING"
            levels.append((ct, 0, 0.0))
            log.write(json.dumps(rec) + "\n"); log.flush()
            break
        k = rnd.randrange(len(cubes))
        lits = cubes[k].split()[1:-1]
        nxt = os.path.join(work, f"s{seed}_l{level + 1}.cnf")
        with open(cur) as f:
            head = f.readline().split()
            body = f.read()
        nv, nc = int(head[2]), int(head[3])
        with open(nxt, "w") as g:
            g.write(f"p cnf {nv} {nc + len(lits)}\n")
            g.write(body)
            for l in lits:
                g.write(f"{l} 0\n")
        # solve the cube as unit clauses (much faster than assumptions: CaDiCaL can simplify)
        rc2, so2, st = run(cpu, ["-v", str(n), "--dimacs", nxt] + smargs, tlim)
        rec.update({"pick": k + 1, "solve_s": round(st, 1), "solve_rc": rc2})
        if any(l.startswith("[(") for l in so2.splitlines()):
            rec["event"] = "GRAPH_FOUND"
            open(out + ".FOUND_graph.txt", "w").write(so2)
            log.write(json.dumps(rec) + "\n"); log.flush()
            return
        log.write(json.dumps(rec) + "\n"); log.flush()
        if rc2 is not None and rc2 not in (10, 20):
            rec["event"] = "SOLVE_FAILED_RC%d" % rc2
            log.write(json.dumps(rec) + "\n"); log.flush()
            return
        if rc2 is not None:
            levels.append((ct, len(cubes), st))
            break
        levels.append((ct, len(cubes), None))
        if level > 0:
            os.remove(cur)
        cur = nxt
        level += 1
    # estimate, bottom up
    est = 0.0
    for i in range(len(levels) - 1, -1, -1):
        ct, b, st = levels[i]
        if i == len(levels) - 1:
            est = ct + (b * st if b else 0.0)
        else:
            est = ct + b * est
    log.write(json.dumps({"seed": seed, "event": "ESTIMATE", "levels": len(levels), "est_cpu_s": est}) + "\n")
    log.flush()


if __name__ == "__main__":
    main()
