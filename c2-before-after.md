# C2. Skill edit: before and after

**Change:** [`workers/skills/skill-recap.md`](workers/skills/skill-recap.md). The original is kept as [`skill-recap.before.md`](workers/skills/skill-recap.before.md). The new skill doesn't restate the brain's rules. It points to RESOLVER and SANITIZER as the source and only adds what the brain leaves open: where the call ends (the last `[client left the call]`), what a flag may say, and that owners and dates are never guessed. Each of these answers a row in [C1](c1-whats-wrong.md).

**How it was run:** every run is a fresh session (Claude Sonnet, one subagent each) with its own copy of the original `brain/`, one transcript and one version of the skill, told to read nothing else. Every output was checked by [`extra/check_recap.py`](extra/check_recap.py) and read by hand. All outputs are in [`c2-runs/`](c2-runs/).

| Runs | Skill | Transcript | Invented owner or date | All checks pass (current checker, 10 checks) |
|---|---|---|---|---|
| `before-1..3` | original | `bad-recap-source.md` | **3 of 3** | 0 of 3 |
| `after-v1-1..3` | first edit | same | 0 of 3 | 3 of 3 |
| `after-v2-1..3` | + review fixes | same | 0 of 3 | 3 of 3 |
| `after-v3-1..3` | shorter, points to the brain | same | 0 of 3 | 3 of 3 |
| `heldout-call1-1..2` | v3 | `inbox/call-1.md` (not used for tuning) | 0 of 2 | 0 of 2 (false claim about the sheet, caught by the sheet rule) |
| `heldout-call2-1..2` | v3 | `inbox/call-2.md` (not used for tuning) | 0 of 2 | 1 of 2 (a note inside the date cell: a false alarm) |

`bad-recap.md` itself passes 1 of 10 checks (the sheet rule finds nothing to object to). The current skill adds one more rule after v3, the review task for held-back content; it was run 5 times in `recap-runs-review/` (below).

**Before** (`before-3`), the size chart item:
> `| Lena Varga | Look into the size chart issue ... | 2026-09-22 (proposed, no date set on the call) |`

The call gave no owner and no date ("someone should look at", "we'll look into it"). All three original-skill runs still made it an action item.

**After** (`after-v3-1`): it goes under Open questions, "no owner and no date were agreed".

**Is that a real effect or noise?** If the edit changed nothing, the chance that all 3 failures land in the 3 original runs out of 12 runs on this transcript is 1 in 220. And the cause is visible in the outputs: it's the same item every time. So the edit works on this failure.

**On transcripts the skill was not tuned on**, the final skill held up where it matters. All 4 runs kept everything from after the client left out of the recap, and their flags don't hint at what was held back. Neither call-1 run made up an owner for "samples go out Thursday". (My own hand-written A1 recap did, and the reviewer caught it.) None typed the GMV figure. It also showed one failure that the tuning transcript couldn't show: both call-1 runs claim the weekly affiliate figures are in the sheet, and they aren't, because the sheet only has 30-day GMV. I didn't patch the skill for this, because tuning on the held-out calls would make them useless as a test. Instead the checker got a rule that compares claims about the sheet with its columns. On 26 recaps labeled by hand ([`extra/eval_checker.py`](extra/eval_checker.py)), the checker now catches 9 of 9 bad recaps (7 of 9 before this rule), with 1 false alarm out of 17 good ones. The rule was written after I saw those two failures, so 9 of 9 is a fit, not a test. It did catch a third case in the command runs below, which it had never seen.

**Where `bad-recap.md` came from: tested, not assumed.** With the brain, the original skill didn't reproduce `bad-recap.md`: `RESOLVER.md` says "Read this first, human or agent", and the model did. So I ran the original skill 3 more times with **no brain at all** (`nobrain-1..3`), which is what a pipeline that doesn't load the brain would do:

| Original skill | GMV typed in | No template, no action table | Earlier meeting linked | DM or post-call content |
|---|---|---|---|---|
| with the brain (`before-*`) | 0 of 3 | 0 of 3 | 3 of 3 | 0 of 3 |
| without the brain (`nobrain-*`) | **3 of 3** | **3 of 3** | 0 of 3 | 0 of 3 |

So a missing brain explains most of the bad recap: the typed GMV, the missing template and owners, the missing link to 10 Sep. It does not explain the leaked DM. This model left it out in all 6 runs, with or without the brain. The likely cause is a weaker model or an older prompt. Either way, the conclusion is the same: the rule has to be enforced in code, which is what [`extra/recap.py`](extra/recap.py) does. That's in [`fde-ticket.md`](fde-ticket.md).

**The same skill through the real command.** [`extra/recap.py`](extra/recap.py) runs one recap end to end. It cuts the transcript in code at the moment the client leaves, runs a fresh `claude -p` session in a temp copy of the brain, then gates the result in code: exactly one new file, and every check passing. 22 runs of v3 and the original skill, all in `recap-runs/` and `recap-runs-oldskill/`:

| Skill | Transcript | Posted | Held back, and why |
|---|---|---|---|
| v3 | `bad-recap-source.md` | 6 of 7 | 1: the agent's write was denied (my sandbox path bug; every run after the fix wrote its recap) |
| v3 | `call-1.md` | 5 of 6 | 1: "weekly results are in the sheet" |
| v3 | `call-2.md` | 4 of 5 | 1: a note inside the due-date cell |
| original | `bad-recap-source.md` | 0 of 2 | 2: invented size chart owner, date "TBC" |
| original | `call-1.md` | 1 of 1 | **posted with an invented owner** ("Marcus Obi, ship samples, 2026-09-24") |
| original | `call-2.md` | 1 of 1 | |

Agent time per recap: median 27 s, max 45 s, $0.10 to $0.13 with v3. One run of the current skill cost $0.20. On the 6 call-1 runs of v3, nobody was made owner of the Thursday samples. On the original skill's run, the gate let an invented owner through, because it had a plausible date. That's the gate's known blind spot, and it's why the skill fix and the gate are both needed.

**A held-back flag is a task, not a note.** A flag that only says "held back, someone review" leads nowhere. Now `recap.py` writes the cut span into the transcript marker ("Recording 01:47-02:15 held back"). The skill turns it into the one action item that doesn't come from the call: owner is the account's pod lead, due the next working day, and the action is to review that span and decide whether to drop it, handle it outside the brain, or restore it. The span points the reviewer to the right place without saying what was there. 5 runs (`recap-runs-review/`): 4 of 4 with held-back content got the right pod lead (Lena for Loop Athletic, Marcus for Kettle & Crumb), the right date and the span. The call with nothing after the client left got no review item. All 5 posted.

**Would one run have been enough?** For the invented owners, no: one run each side is a coin flip. For rare failures, like the DM leaking, even 12 clean runs say little. That's why those rules belong in code (the checker, and the cut at the moment the client leaves), not only in the prompt.
