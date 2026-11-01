"""Recap one call end to end, with the brain's hard rules enforced in code around the model.

Usage: python3 extra/recap.py TRANSCRIPT.md [--model sonnet] [--skill workers/skills/skill-recap.md]
                              [--brain brain] [--runs runs] [--posted posted]

1. Cut: the transcript is cut after the last client attendee leaves, before the model sees it.
2. Agent: a fresh `claude -p` session in a temp copy that holds only the skill, the brain and the cut
   transcript. It may read there and write only to brain/knowledge/meetings/.
3. Gate: the brain copy must be unchanged except for exactly one new recap, and the recap must pass
   check_recap.py against the full transcript. Only then is it "posted" (copied to --posted).

Every run leaves runs/<stamp>-<call>/ with the recap, run.json (stage timings, cost, skill hash,
cut span, permission denials, check results) and the agent's raw output. Exit code 0 if posted, 1 if held back,
2 if escalated: the transcript doesn't show where the client left, so no model runs and a person has to look.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_recap import CantTell, client_left_at, run_checks, system_lines  # noqa: E402

PROMPT = """You are the recap agent of a creator agency. Work only inside the current folder.
Follow the skill file workers/skills/skill-recap.md. The transcript to recap is the one file in inbox/.
The company brain is brain/. Write exactly one recap file into brain/knowledge/meetings/.
Instead of posting, just save the file. When done, reply with only the path of the file you wrote."""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def snapshot(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(Path(root).rglob("*")) if p.is_file()}


TIMECODE = re.compile(r"^(\d\d:\d\d)\b")


def cut_transcript(text):
    """Drop everything after the last client attendee leaves.

    Returns (kept text, dropped line count, "mm:ss-mm:ss" range of the dropped part or None). The range goes
    into the marker line, so the recap can point a reviewer at the spot without repeating what was said.
    Raises CantTell when it can't tell where the client left.
    """
    lines = text.splitlines()
    cut = client_left_at(text)
    if cut is None:
        return text, 0, None
    dropped = lines[cut + 1:]
    stamps = [m.group(1) for m in map(TIMECODE.match, dropped) if m]
    span = f"{stamps[0]}-{stamps[-1]}" if stamps else None
    if dropped:
        marker = f"[Transcript cut here by recap.py: the client has left the call. Recording {span} held back]"
    else:
        marker = "[Transcript cut here by recap.py: the client has left the call. Nothing after it]"
    kept = lines[:cut + 1] + [marker]
    return "\n".join(kept) + "\n", len(dropped), span


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transcript")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--skill", default="workers/skills/skill-recap.md")
    ap.add_argument("--brain", default="brain")
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--posted", default="posted")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    transcript = Path(args.transcript)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(args.runs) / f"{stamp}-{transcript.stem}"
    run_dir.mkdir(parents=True)
    log = {"transcript": str(transcript), "model": args.model, "skill": args.skill,
           "skill_sha": sha(args.skill), "stages_s": {}}
    t0 = time.monotonic()

    # 1. Cut, in code.
    try:
        kept, dropped, span = cut_transcript(transcript.read_text())
    except CantTell as e:
        log.update(escalated=True, posted=False, problems=[str(e)], system_lines=system_lines(transcript.read_text()))
        (run_dir / "run.json").write_text(json.dumps(log, indent=2))
        print(f"ESCALATED  {e}  ->  {run_dir}")
        print("  bracketed lines in the transcript:")
        for line in log["system_lines"] or ["(none)"]:
            print("    " + line)
        sys.exit(2)
    log["escalated"] = False
    log["lines_cut_after_client_left"] = dropped
    log["held_back_span"] = span
    log["stages_s"]["cut"] = round(time.monotonic() - t0, 2)

    # 2. Agent, in a temp copy outside the repo so no CLAUDE.md or settings from here leak in.
    with tempfile.TemporaryDirectory(prefix="recap-") as tmp:
        box = Path(tmp).resolve()  # /var is a symlink on macOS; permission rules match the real path
        shutil.copytree(args.brain, box / "brain")
        (box / "workers" / "skills").mkdir(parents=True)
        shutil.copy(args.skill, box / "workers" / "skills" / "skill-recap.md")
        (box / "inbox").mkdir()
        (box / "inbox" / transcript.name).write_text(kept)
        before = snapshot(box / "brain")

        t1 = time.monotonic()
        cmd = ["claude", "-p", PROMPT, "--model", args.model, "--output-format", "json",
               "--no-session-persistence", "--setting-sources", "project", "--permission-mode", "dontAsk",
               "--allowedTools", f"Read(/{box}/**)", "Glob", "Grep",
               f"Write(/{box}/brain/knowledge/meetings/**)", f"Edit(/{box}/brain/knowledge/meetings/**)"]
        proc = subprocess.run(cmd, cwd=box, capture_output=True, text=True, timeout=args.timeout,
                              stdin=subprocess.DEVNULL)
        log["stages_s"]["agent"] = round(time.monotonic() - t1, 2)
        (run_dir / "agent-output.json").write_text(proc.stdout + proc.stderr)
        try:
            result = json.JSONDecoder().raw_decode(proc.stdout)[0]
            log["cost_usd"] = result.get("total_cost_usd")
            log["permission_denials"] = [(d["tool_name"], d["tool_input"].get("file_path"))
                                         for d in result.get("permission_denials", [])]
        except json.JSONDecodeError:
            log["agent_error"] = (proc.stderr or proc.stdout)[:500]

        # 3. Gate, in code.
        t2 = time.monotonic()
        after = snapshot(box / "brain")
        new = [p for p in after if p not in before]
        changed = [p for p in before if after.get(p) != before[p]]
        problems = []
        if changed:
            problems.append(f"agent changed existing brain files: {changed}")
        recaps = [p for p in new if p.startswith("knowledge/meetings/") and p.endswith(".md")]
        if len(recaps) != 1 or len(new) != 1:
            problems.append(f"expected exactly one new recap, got new files: {new}")
        checks = []
        if recaps:
            out = box / "brain" / recaps[0]
            shutil.copy(out, run_dir / out.name)
            checks = run_checks(run_dir / out.name, transcript, box / "brain/knowledge/reference/accounts-sheet.csv")
            problems += [f"check failed: {name} ({detail})" for name, ok, detail in checks if not ok]
        log["recap"] = recaps[0] if recaps else None
        log["checks"] = {name: ok for name, ok, _ in checks}
        log["stages_s"]["gate"] = round(time.monotonic() - t2, 2)

    log["stages_s"]["total"] = round(time.monotonic() - t0, 2)
    log["posted"] = not problems
    log["problems"] = problems
    if not problems:
        Path(args.posted).mkdir(parents=True, exist_ok=True)
        shutil.copy(run_dir / Path(recaps[0]).name, Path(args.posted) / Path(recaps[0]).name)
    (run_dir / "run.json").write_text(json.dumps(log, indent=2))

    print(f"{'POSTED' if not problems else 'HELD BACK'}  {log['recap']}  "
          f"cut {dropped} lines, agent {log['stages_s']['agent']}s, total {log['stages_s']['total']}s, "
          f"${log.get('cost_usd') or 0:.3f}  ->  {run_dir}")
    for p in problems:
        print("  " + p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
