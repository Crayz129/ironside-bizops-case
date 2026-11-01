# Ironside Biz Ops case study: Arsenii Solovev

Time: about 2 hours of mine, plus about 1.7 hours of AI time (agent runs and reviews). Skipped: none. Extra credit: done (`extra/`).

| Q | File |
|---|---|
| A1 | [brain/knowledge/meetings/2026-09-22-kettle-and-crumb-weekly.md](brain/knowledge/meetings/2026-09-22-kettle-and-crumb-weekly.md) |
| A2 | [brain/knowledge/meetings/2026-09-24-kettle-and-crumb-monthly-business-review.md](brain/knowledge/meetings/2026-09-24-kettle-and-crumb-monthly-business-review.md), [proposed-changes.md](proposed-changes.md) |
| A3 | [answer.md](answer.md) |
| B1, B2 | [b-analysis.md](b-analysis.md), numbers from [analysis/pod_numbers.py](analysis/pod_numbers.py) |
| B3 | [plan.md](plan.md) |
| C1 | [c1-whats-wrong.md](c1-whats-wrong.md) |
| C2 | [workers/skills/skill-recap.md](workers/skills/skill-recap.md) (old version: [skill-recap.before.md](workers/skills/skill-recap.before.md)), [c2-before-after.md](c2-before-after.md), runs in [c2-runs/](c2-runs/) |
| C3 | [fde-ticket.md](fde-ticket.md) |
| Extra | [extra/](extra/): `recap.py` (one command, rules in code), `check_recap.py`, `eval_checker.py` |
| Log | [log.md](log.md) |

To reproduce the numbers and checks:
```
python3 analysis/pod_numbers.py calls.csv adoption.csv
python3 extra/check_recap.py workers/output/bad-recap.md --transcript workers/output/bad-recap-source.md
python3 extra/eval_checker.py
python3 extra/test_cut.py      # where the client left: cut, or hold for a person
python3 extra/recap.py inbox/call-1.md --brain extra/brain-at-start --runs recap-runs --posted recap-runs/posted   # needs the claude CLI
```

**What I'd automate next:** the gate is built (`extra/recap.py`), so next is owner checking: an action item's owner must be someone who committed to it in the transcript, the one failure the gate still lets through. Then a weekly pod number built from `calls.csv` that separates AM-posted recaps from the agent's, because the current dashboard hides that the target is being hit by hand and already gets one pod's share wrong. Then per-stage timing in the real recap pipeline, because the 45-minute floor is the biggest lever on the number and nobody knows where it goes.

`extra/system-lines.json` lists the bracketed lines a person has confirmed (which mean someone left, which don't). Any other bracketed line holds the recap and is printed, so a new recording format shows up on its first call.

`extra/brain-at-start/` is the brain as it came in the zip, before my two recaps, so `recap.py` can be rerun on the inbox calls.
