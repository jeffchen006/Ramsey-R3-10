"""Require exactly the requested #print axioms reports, with only standard axioms."""

from collections import Counter
from pathlib import Path
import re
import sys

STANDARD = {"propext", "Classical.choice", "Quot.sound"}
REPORT = re.compile(r"^'(\S+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$")


def check(script: Path, log: Path) -> None:
    expected = Counter(re.findall(r"^#print axioms (\S+)$", script.read_text(), re.M))
    seen = Counter()
    for line in log.read_text().splitlines():
        match = REPORT.fullmatch(line)
        if match is None:
            if line and not re.fullmatch(r"wall=\S+ user=\S+ sys=\S+ maxrss(?:_kib)?=\S+ exit=0", line):
                raise ValueError(f"unexpected output: {line}")
            continue
        theorem, axioms = match.groups()
        extra = set(axioms.split(", ") if axioms else ()) - STANDARD
        if extra:
            raise ValueError(f"{theorem} depends on {sorted(extra)}")
        seen[theorem] += 1
    if not expected or seen != expected:
        raise ValueError(f"missing {expected - seen}; unexpected {seen - expected}")
    print(f"PASS: {seen.total()} reports; only permitted standard axioms")


if __name__ == "__main__":
    check(Path(sys.argv[1]), Path(sys.argv[2]))
