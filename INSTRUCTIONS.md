# Ironside: Biz Ops case study

*v1.2 · 2 Oct 2026 · Biz Ops seat*

Ironside runs operations for creator agencies on TikTok Shop. We are an AI-first team: every person runs agents, and the agents run on a shared company brain, a folder of markdown files the team and the agents both read and write.

Biz Ops owns outcome numbers for delivery. You move it three ways: you do the work yourself, you get client pods to adopt the tools, and you turn what you learned into a playbook plus clear feedback for the engineers who build the agents.

This case study is that loop, on made-up data: three blocks, three questions each, going from easy to hard.

## The rules

- **This should take about 60 minutes. Spend as long as you want beyond that.** We know you're excited, but please no more than 6 hours :) Tell us roughly how long you spent.
- **No setup needed.** This folder is a ready-made demo company brain with dummy transcripts and data. No need to spend time installing new tools. Point the AI you already use at the folder.
- **Use AI as much as you can.** Claude Code, Cursor, ChatGPT, whatever you actually use. We want to see how you really work.
- **Every question stands on its own.** Do them in any order and skip any you like. Tell us which you skipped.
- **Keep a short log as you go** in `log.md`: at the top, roughly how many HUMAN hours you spent and how many hours your AI (Claude, ChatGPT or other) spent. Then the first instruction you gave it, and three things it got wrong: how you caught each one, and whether you fixed the instruction or only the output. Ten lines is plenty.
- All names, brands and numbers in this folder are fictional.

## What's in the folder

- `brain/`: a small company brain for a fictional creator agency, Brightline. Start with `RESOLVER.md` (where things go) and `SANITIZER.md` (what never goes in). It also has people pages, account pages, past meeting summaries, a reference sheet and `NOW.md` (this week's priorities).
- `inbox/`: two raw call transcripts, `call-1.md` and `call-2.md`, not processed yet.
- `workers/skills/skill-recap.md`: the skill file our recap agent follows.
- `workers/output/`: `bad-recap.md`, a recap the agent wrote last week that a pod lead complained about, and `bad-recap-source.md`, the transcript it was written from.
- `adoption.csv`: this month's dashboard for the recap step, by pod.
- `calls.csv`: the per-call log the dashboard is built from.
- `slack-thread.txt`: a short thread from one of the pod leads.

A **recap** here always means two things: a summary of the meeting, and a list of action items with an owner and a due date for each.

## Block A: Do the work

1. **A1 (easy).** Write the recap for `inbox/call-1.md` into `brain/knowledge/meetings/`, following the brain's rules.
2. **A2 (medium).** Write the recap for `inbox/call-2.md` the same way. Then, in `proposed-changes.md`, list the edits you would make to people and account pages because of this call, including the new GMV for the reference sheet. Don't make the edits. A person approves them.
3. **A3 (hard).** In `answer.md`, answer this with links to the files you used: **"I'm talking to Dana at Kettle & Crumb about affiliates, end to end. What do I need to know?"**

## Block B: Move the number

The number is **the share of client calls that get a recap posted within an hour.** The target is 80% for every pod by the end of next month.

1. **B1 (easy).** From `adoption.csv` and `calls.csv`, rank the four pods on the number. Then work out one more number from the data that you think matters, and say why.
2. **B2 (medium).** Which pod would you work on first, and what is actually causing its gap? Use anything in the folder.
3. **B3 (hard).** Write your one-week plan for that pod in `plan.md`: what you do yourself, what you ask of the pod, what you ask of engineering, and the number you expect by Friday. At the top of `plan.md`, add the message you'd send that pod's lead to get them on board this week, five lines at most. Under it, in a few lines: what will that lead push back with, and what keeps the change going after you stop checking in?

## Block C: Train the agent

1. **C1 (easy).** List what is wrong with `bad-recap.md`, compared with its source and the brain's rules.
2. **C2 (medium).** Edit `skill-recap.md` so those mistakes don't happen again. Rerun it on `bad-recap-source.md` in a fresh AI session that sees only the skill, the brain and the transcript, and include the before and after.
3. **C3 (hard).** Write `fde-ticket.md` for the engineer who builds the recap agent: what should change that a skill file can't fix, with your evidence. Under 150 words.

## Extra credit (optional)

Build one small thing with AI that you would actually use every day in this job, and tell us in one line why you picked it. Rough is fine, but it should run.

It can be anything: a checker, a skill, a dashboard, a tiny app. Pick whatever would save you the most time here.

Put it in `extra/`, with a README of five lines or fewer: what it does, how to run it, and what you would build next.

## What to send back

- One link to your results: an artifact (a Claude artifact, Google Doc, Notion page or simple web page). Make the artifact as if you were sharing it with a client. We'll look at clarity, conciseness and design.
- Inside it, link your working folder (a GitHub repo or a shared Drive folder) with your files, your log and `extra/` if you did it. No zip needed.
- How long you spent, and which questions you skipped
- Three sentences: what you would automate next, and why

Then book a 20-minute working session: tidycal.com/jeremycarr. It is not a presentation. We will open your folder together, and we will ask you to change something live with your setup.
