# Block B: the number

Every figure here comes from `python3 analysis/pod_numbers.py calls.csv adoption.csv`. The data covers 1 to 24 Sep, 140 calls.

## B1. Ranking

| Rank | Pod | Lead | Calls held | Recap within 1h | Share |
|---|---|---|---|---|---|
| 1 | North | Sam Whitaker | 40 | 36 | **90%** |
| 2 | East | Aisha Rahman | 30 | 21 | **70%** (dashboard says 75%) |
| 3 | South | Marcus Obi | 40 | 14 | **35%** |
| 4 | West | Lena Varga | 30 | 3 | **10%** |

The dashboard has one error: East's share is divided by recorded calls (21/28 = 75%), every other pod by calls held. On the definition, "share of client calls", East is at 70%. The counts in `adoption.csv` all match `calls.csv`.

**The extra number: the agent posts within an hour only 49% of the time** (29 of 59 recaps, median 65 minutes, never under 45). When an AM posts the recap by hand, it is 100% within the hour (45 of 45, median 18 minutes).

Why it matters: the pods that hit the number hit it by hand. North's 36 on-time recaps include 33 written by AMs. East jumped from 50% to 93% in the second half of the month, when its AMs started posting (North is helping East copy its routine, `brain/NOW.md`). No pod gets anywhere near 80% on the agent alone. So the number currently measures whether a pod works around the agent, and the agent's own speed is the main thing to fix.

Two smaller things the dashboard doesn't show:
- It measures speed, not quality. The 15 Sep Loop Athletic recap (call `c084`) counts as a success at 55 minutes, but it's `bad-recap.md`: a private DM and an untracked GMV figure, posted to the client's channel.
- The two Kettle & Crumb calls from this week (`c117`, `c140`) were recorded but never got a recap. They are the two calls in `inbox/`.

## B2. Which pod first: South

South has the biggest gap that can close this month. It needs 32 of 40 calls to hit 80% and has 14, so it's 18 calls short. West is 21 short, but its gap is structural and needs a new capture path.

**What's causing South's gap is the agent's delay, not missing recordings or bad content.**
- The agent sees almost everything: 36 of 40 calls are recorded, 34 got a recap.
- But only 14 of the 34 came within the hour. The rest came at 69 to 91 minutes. The agent is also slower for South than for the other pods: median 74 minutes against 55 to 59 (small samples elsewhere, worth checking with engineering). Load doesn't explain it: the delay doesn't grow when several recorded calls end within the same hour.
- South's AMs already write their own summary and send it to the client before the bot posts, so they ignore the bot: "slower than my own notes", "if it posted in 10-15 min I'd use it", "the content is fine when it shows up" (`slack-thread.txt`, 18 Sep).
- Zero South recaps were posted by an AM. The work is done, it just never reaches the channel or the brain.

So South's problem is a routing one: the summary exists, it just goes to email. That's fixable in a week, and the North and East data shows what happens when AMs post.

**On Priya's proposal** to count emailed summaries as recaps: I'd push back. It would raise South's number without changing anything. Those summaries don't land in the brain, nobody can check their action items, owners and due dates, and they skip the SANITIZER check. The better fix is to get that same summary posted in the channel, which costs the AM about the same as emailing it.

**West** is next, and it's a different problem: 26 of its 30 calls are on WhatsApp and never recorded, so even a perfect agent tops out at 13%. Lena is already looking for a capture path. That's the engineering ticket in `fde-ticket.md`. Two levers work now: AMs post a manual recap like North's, and clients are asked to move some calls to Meet. Loop Athletic already did that on 10 and 15 Sep ("Thanks for doing Meet this week instead of WhatsApp").
