# C1. What's wrong with `bad-recap.md`

Compared with `bad-recap-source.md` (Loop Athletic weekly, 15 Sep) and the brain's rules. Ordered by harm.

| # | Problem | Rule it breaks | Which line in the skill caused it |
|---|---|---|---|
| 1 | It quotes a private DM about the client's CEO and agency fees. Lena pasted it after Theo left the call, and the recap posted it to the client's Slack channel. | SANITIZER 2 (said in private) and 3 (our fees) | "Include everything relevant, so nothing gets lost" |
| 2 | "Keep an eye on the account review risk" is an action item built on the same DM. | SANITIZER 2 | same |
| 3 | "$95K GMV this month" is typed in. The sheet has 62K for the last 30 days, and the conflict isn't flagged. | RESOLVER 5, house rule 4 | "Include the key numbers mentioned on the call" |
| 4 | Action items have no owner and no due date. The brief has both on the call (Lena, Friday 18 Sep). The size chart has neither, so it should be an open question. | House rule 3 | "List the next steps" |
| 5 | "Great call with Theo": an opinion, not a fact. | template ("Facts, decisions") | no instruction on tone |
| 6 | The template isn't followed: no attendees or source in the front matter, prose instead of 3-6 bullets, "Next steps" instead of an action items table, no Open questions, no Flags for a person. | RESOLVER template | the skill never points to RESOLVER or the template |
| 7 | The try-on format is presented as new. Theo asked for it on 10 Sep, and the last 4 videos moved to it then. The recap should link that meeting. The size chart was also already an open item from 10 Sep (Theo was to send it). | House rule 5 | no instruction to read earlier meetings |
| 8 | Nothing is flagged for a person, even though the agent held nothing back. A correct recap would flag the content left out after Theo left. | SANITIZER check, template | the skill says "Post it" with no check before |

The root cause is the skill file. It never tells the agent to read `RESOLVER.md` or `SANITIZER.md`, and three of its five steps (2, 3, 5) push the agent straight into these mistakes.
