"""Rebuild the recap-within-1h number per pod from calls.csv and check it against adoption.csv.

Usage: python3 analysis/pod_numbers.py [calls.csv] [adoption.csv]
"""
import csv
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta

PODS = ["North", "East", "South", "West"]


def minutes_to_post(row):
    if not row["recap_posted_at"]:
        return None
    end = datetime.fromisoformat(row["call_end"])
    posted = datetime.fromisoformat(row["recap_posted_at"])
    return (posted - end).total_seconds() / 60


def main(calls_path="calls.csv", adoption_path="adoption.csv"):
    calls = list(csv.DictReader(open(calls_path)))
    dashboard = {r["pod"]: r for r in csv.DictReader(open(adoption_path))}

    by_pod = defaultdict(list)
    for row in calls:
        by_pod[row["pod"]].append(row)

    dates = sorted(r["date"] for r in calls)
    print(f"calls.csv: {len(calls)} calls, {dates[0]} to {dates[-1]}\n")

    print("pod     held  recorded  posted  <=1h   share  | dashboard  | by AM <=1h  by agent <=1h")
    results = []
    for pod in PODS:
        rows = by_pod[pod]
        held = len(rows)
        recorded = sum(r["recorded"] == "yes" for r in rows)
        posted = [r for r in rows if r["recap_posted_at"]]
        on_time = [r for r in posted if minutes_to_post(r) <= 60]
        share = len(on_time) / held
        d = dashboard[pod]
        counts_match = (int(d["client_calls_held"]), int(d["calls_recorded"]),
                        int(d["recaps_posted_within_1hr"])) == (held, recorded, len(on_time))
        # The share is checked on its own: the counts can match while the share was divided by the wrong column.
        share_match = d["share_of_calls_with_recap_within_1hr"] == f"{share:.0%}"
        same = counts_match and share_match
        am = sum(r["posted_by"] == "AM" for r in on_time)
        agent = sum(r["posted_by"] == "agent" for r in on_time)
        results.append((share, pod))
        print(f"{pod:<7} {held:>4}  {recorded:>8}  {len(posted):>6}  {len(on_time):>4}  {share:>5.0%}  | "
              f"{d['share_of_calls_with_recap_within_1hr']:>4} {'ok' if same else 'DIFF':>4}  | {am:>10}  {agent:>13}")

    print("\nRank:", " > ".join(f"{pod} {share:.0%}" for share, pod in sorted(results, reverse=True)))

    print("\nMinutes from call end to recap, by who posted it:")
    for who in ["agent", "AM"]:
        mins = sorted(minutes_to_post(r) for r in calls if r["posted_by"] == who)
        within = sum(m <= 60 for m in mins)
        print(f"  {who:<5} n={len(mins):>2}  min={mins[0]:.0f}  median={statistics.median(mins):.0f}  "
              f"max={mins[-1]:.0f}  within 1h: {within}/{len(mins)} ({within / len(mins):.0%})")

    print("\nAgent delay, what it does and doesn't depend on:")
    agent_rows = [r for r in calls if r["posted_by"] == "agent"]
    mins = [minutes_to_post(r) for r in agent_rows]
    print(f"  p95 {statistics.quantiles(mins, n=20)[-1]:.0f} min, floor {min(mins):.0f} min")
    for pod in PODS:
        pod_mins = [minutes_to_post(r) for r in agent_rows if r["pod"] == pod]
        within = sum(m <= 60 for m in pod_mins)
        print(f"  {pod:<6} n={len(pod_mins):>2}  median {statistics.median(pod_mins):.0f}  within 1h {within}/{len(pod_mins)}")
    # A queue would make a recap slower when other recorded calls ended shortly before it.
    recorded_ends = [datetime.fromisoformat(r["call_end"]) for r in calls if r["recorded"] == "yes"]
    load = defaultdict(list)
    for r in agent_rows:
        end = datetime.fromisoformat(r["call_end"])
        busy = sum(1 for e in recorded_ends if timedelta(0) < end - e <= timedelta(minutes=60))
        load[min(busy, 2)].append(minutes_to_post(r))
    print("  by other recorded calls ended in the hour before:  " + "  ".join(
        f"{k}{'+' if k == 2 else ''}: median {statistics.median(v):.0f} (n={len(v)})" for k, v in sorted(load.items())))

    print("\nSame number, first half vs second half of the month (1-14 Sep / 15-24 Sep):")
    for pod in PODS:
        parts = []
        for lo, hi in [("2026-09-01", "2026-09-14"), ("2026-09-15", "2026-09-30")]:
            rows = [r for r in by_pod[pod] if lo <= r["date"] <= hi]
            ok = sum(1 for r in rows if r["recap_posted_at"] and minutes_to_post(r) <= 60)
            by_am = sum(r["posted_by"] == "AM" for r in rows)
            parts.append(f"{ok}/{len(rows)} ({ok / len(rows):.0%}, {by_am} by AM)")
        print(f"  {pod:<6} {parts[0]:<22} -> {parts[1]}")

    print("\nCalls the agent never saw (not recorded), by platform:")
    for pod in PODS:
        missed = defaultdict(int)
        for r in by_pod[pod]:
            if r["recorded"] == "no":
                missed[r["platform"]] += 1
        print(f"  {pod:<6} {dict(missed)}")

    print("\nRecorded calls with no recap at all:")
    for r in calls:
        if r["recorded"] == "yes" and not r["recap_posted_at"]:
            print(f"  {r['call_id']} {r['date']} {r['pod']} {r['account']}")


if __name__ == "__main__":
    main(*sys.argv[1:])
