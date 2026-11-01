---
type: skill
step: recap
owner: Brightline ops
updated: 2026-09-28
---

# Skill: recap a client call

You turn the transcript of one recorded client call into one recap in `brain/knowledge/meetings/`. The client reads it: it is posted to their Slack channel.

## Rules come from the brain
1. Read `brain/RESOLVER.md` and `brain/SANITIZER.md` first. Their rules, template and file naming apply as written, and they override this file.
2. Read the account page, the attendees' people pages, earlier recaps for the account, and its row in `brain/knowledge/reference/accounts-sheet.csv`.
3. Name the file like the existing recaps in `meetings/`.

This file only adds what the brain leaves open.

## What the brain leaves open
- **Where the call ends.** Use only what was said while a client attendee was on the call. After the last client attendee leaves (a line like `[Name left the call]`), stop. Only a cut marker that follows may be used, for its timecodes. Nothing said after that goes in, in any form.
- **What a flag may say.** When you hold something back, the flag says only that something was held back, where in the recording (timecodes, e.g. "01:47-02:15"; a cut marker in the transcript may give them), and that its review is an action item. Don't say what kind of thing it was (a DM, an opinion, about whom), because the client reads the page.
- **Held-back content gets a review item.** It is the one action item that doesn't come from the call: owner is the account's pod lead (from the account page), due the next working day after the call. The action: review what was held back (with the timecodes) and decide whether to drop it, handle it outside the brain, or restore it.
- **Numbers on a flag.** When a call's performance number disagrees with the sheet, flag the disagreement without the figure.
- **Owners and dates are never guessed.** Apart from the review item above, an action item needs a person who committed to it on the call and a date that was said. Work out weekdays ("by Friday") from the call date. If either is missing, the item goes under Open questions with what is missing. If a date can be read two ways, use the likely one and say so under Open questions.
- **Tone.** Facts and decisions only, no adjectives about the call or the people.

## Before you save
Go through the check at the end of `SANITIZER.md` line by line. Then check every other action item for a committed owner and a said date. Don't edit people pages, account pages or the sheet.
