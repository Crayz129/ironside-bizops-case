"""Measure check_recap.py against recaps labeled by hand (extra/labels.csv).

Usage: python3 extra/eval_checker.py [labels.csv]   (run from the case folder)
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_recap import run_checks  # noqa: E402

SHEET = "brain/knowledge/reference/accounts-sheet.csv"
SHEET_CHECK = "claims about the sheet match its columns"


def verdict(results, skip=()):
    return "pass" if all(ok for name, ok, _ in results if name not in skip) else "fail"


def score(rows, skip=()):
    cells = {"caught": 0, "missed": 0, "false alarm": 0, "passed": 0}
    misses = []
    for row in rows:
        got = verdict(row["results"], skip)
        if row["expected"] == "fail":
            cells["caught" if got == "fail" else "missed"] += 1
        else:
            cells["false alarm" if got == "fail" else "passed"] += 1
        if got != row["expected"]:
            failed = [name for name, ok, _ in row["results"] if not ok and name not in skip]
            misses.append(f"  {row['expected']:>4} -> {got:<4} {row['recap']}  ({'; '.join(failed) or row['why']})")
    return cells, misses


def main(labels="extra/labels.csv"):
    rows = list(csv.DictReader(open(labels)))
    for row in rows:
        row["why"] = row["why (read by hand)"]
        row["results"] = run_checks(row["recap"], row["transcript"] or None, SHEET)
    bad = sum(r["expected"] == "fail" for r in rows)
    print(f"{len(rows)} recaps labeled by hand: {bad} should fail, {len(rows) - bad} should pass\n")
    for title, skip in [("without the sheet rule", (SHEET_CHECK,)), ("with the sheet rule", ())]:
        cells, misses = score(rows, skip)
        print(f"{title}: caught {cells['caught']}/{bad} bad, false alarms {cells['false alarm']}/{len(rows) - bad} good")
        print("\n".join(misses) or "  no disagreements")
        print()


if __name__ == "__main__":
    main(*sys.argv[1:])
