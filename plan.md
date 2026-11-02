# South pod: one-week plan (Mon 28 Sep to Fri 2 Oct)

## Message to Marcus

> Marcus, you said it in #pod-south on the 18th: the bot is slower than your notes, and you'd use it at 10-15 minutes. You're right, it's the delay: 20 of your 34 recaps this month came after the hour.
> This week, let's post the summary you already write for the client into their Slack channel instead of emailing it. Same text, the client still gets it, and it counts.
> I'll join your calls Monday and Tuesday and post the recaps myself, so it costs you nothing to try.
> Meanwhile I'm getting engineering to stop the bot posting on top of you and to make it faster.
> If it isn't easier than email by Friday, we stop.

## What he'll push back with, and what keeps it going

- **"That's the bot's job, not mine."** True, and the engineering ticket is in. But your summary already exists, and moving it from email to Slack is the fastest way to stop losing the hour while the bot gets faster.
- **"Priya said emailed summaries count."** They'd move the number, not the outcome. Nothing lands in the brain, and nobody can see the action items. Posting it is the same effort.
- **"I'm swamped this week"** (fall flavor plan due Tuesday, sample list for Jess on Thursday). That's why I post Monday and Tuesday myself, and the recap's action items give him both deadlines in one place.
- **"The template takes longer than my email."** Then the template is wrong. I'll time it on Monday and cut it down to what he writes anyway: summary bullets plus owner, action, due date.

What keeps it going: the routine has to be cheaper than the old one, not just checked. The channel replaces the email, so there's one place to write, not two. The action items feed his Wednesday affiliates summary for Dana. A pod-by-pod line from `calls.csv` goes to `#pod-south` every Monday. And the AM's post is the only one in the channel; the agent keeps the brain in step behind it, so nothing doubles up for the client.

## What I do myself

- **Mon-Tue:** join South's calls, or watch the recording right after, and post the recap in the template within 15 minutes, using the AM's notes. Time each one.
- **Mon:** post the two missing Kettle & Crumb recaps (22 and 24 Sep, `c117` and `c140`) and send the proposed page edits to Marcus for approval.
- **Mon:** agree with Priya that the number stays "posted within the hour" and that emailed summaries don't count. Otherwise the pod has no reason to change.
- **Mon:** ask Sam Whitaker how North does it in 9-24 minutes, and write it up as a half-page routine for South.
- **Daily:** run `extra/recap.py` on every South call and check its recap against the AM's post before it goes into the brain (see above).
- **Daily:** check every South call in `calls.csv`. For each one without a recap inside the hour, write down why.
- **Fri:** share the week's number with Marcus and Priya, together with the list of reasons.

## What I ask of the pod

- Marcus and Tomas: from Wednesday, whoever runs the call posts the recap in the client channel within the hour, instead of emailing it: summary bullets plus owner, action, due date. That post is what the client sees and what counts.
- Internal talk happens after the recording stops. On 22 Sep the recording caught a side comment and a pasted DM after Dana left. `recap.py` cuts that out of the recap, but it stays in the recording tool.
- Keep recording every Meet call. The 4 phone calls this month were never recorded: move them to Meet, or post a manual recap.
- Two minutes on Friday: what was annoying about it?

## How the AM's post reaches the brain

One recap per call in the client's channel, and one in the brain:
1. The AM posts the summary in the client channel within the hour. It counts, and the client has it.
2. When the transcript is ready, the agent takes **the AM's post plus the transcript**. It puts them into the template, checks the post against the transcript (missing action items, wrong dates, no owner), runs the gate, and writes **only to the brain**. It does not post in the client channel.
3. If the post and the transcript disagree, the agent messages the AM directly, not the client channel: "your post has no action item for Jess, due 1 Oct". The AM decides whether to edit the post.

The agent's role changes from racing the hour to keeping the brain right and backing up the AM, so its delay stops costing the number. This week, until engineering ships AM-first mode, I run it by hand. The agent's channel post is switched off for South, so the client doesn't get two recaps of one call. After each South call I run `extra/recap.py` on the transcript, compare its recap with the AM's post, message the AM about any gap, and put the recap in the brain. That's the beta run on a live pod, and it shows engineering exactly what AM-first mode has to do.

Before Monday, ask Sam how North does this. In `calls.csv` every North call has one post (`posted_by=AM`), so the data doesn't show whether their AM posts also reach the brain.

## What I ask of engineering

- **Speed:** where do the 45 to 90 minutes go (recording export, transcription, model, posting)? Target a draft within 15 minutes of the call ending.
- **AM-first mode:** if an AM already posted in the channel, the agent doesn't post again. It uses the AM's post as input, writes the brain recap, and sends the AM any differences from the transcript.
- **Draft mode:** for calls the AM doesn't post, a draft for the AM to approve, instead of a final recap at 80 minutes.
- **Checks before posting:** the bad Loop Athletic recap got posted and counted as a success. Details in `fde-ticket.md`.

## The number I expect by Friday

**At least 75% of South's calls this week** (about 9 of 12, at 2.35 calls a day), up from 35% in September. Monday and Tuesday should be hits, because I post those. The risk is Wednesday to Friday, when the AMs take over in a heavy week, and phone calls stay uncovered. If the routine holds, the following week should reach 80%. If engineering ships the faster draft, it gets there without depending on habit.
