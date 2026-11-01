# Recap agent: what a skill file can't fix

**1. Speed.** The agent posts 45 to 91 minutes after a call (median 65): only 29 of 59 within the hour. It never posts in under 45, yet writing one takes about 30 seconds in `extra/recap.py`. So the time likely goes outside the model. Load doesn't explain it: latency doesn't rise when calls end together. South is slowest (median 74). Time each stage. If an AM already posted, don't post again: use their post as input and write only to the brain.

**2. Check before posting.** `bad-recap.md` posted a private DM to the client's channel and counted as on time (`c084`). Without the brain, the skill reproduces most of it, 3 of 3 (`c2-before-after.md`). `extra/recap.py` does the fix: load the brain, cut the transcript when the client leaves, gate on the checks, log the skill version.

**3. Capture.** West's WhatsApp calls (26 of 30) never reach the agent.
