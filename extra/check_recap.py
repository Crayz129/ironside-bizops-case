"""Check a recap against the brain's rules before it gets posted.

Usage: python3 extra/check_recap.py RECAP.md [--transcript CALL.md] [--sheet accounts-sheet.csv]

Exit code 0 if every check passes, 1 otherwise. Stdlib only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FRONT = ["type", "date", "account", "attendees", "source"]
REQUIRED_SECTIONS = ["Summary", "Action items", "Open questions", "Flags for a person"]
PERF_WORDS = re.compile(r"\b(gmv|ad spend|active affiliates|affiliates|retention|revenue|sales)\b", re.I)
DECISION_WORDS = re.compile(r"\b(target|goal|by \d{1,2} \w{3}|by 31)\b", re.I)
NUMBER = re.compile(r"\$?\b\d[\d,.]*\s?[kK]?\b")
PERIOD = re.compile(r"\b\d+[- ](day|days|hour|hours|week|weeks|month|months)\b", re.I)
DATE_LIKE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2} (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\b", re.I)
PRIVATE_WORDS = re.compile(r"\b(dm|dms|dm'd|dmed|between us|don't mention|off the record|agency fees?|our fees?|margin)\b", re.I)
OPINION_WORDS = re.compile(r"\b(great call|flaky|difficult|checked out|lazy|annoying|frustrated)\b", re.I)
FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$")
SHEET_MENTION = re.compile(r"accounts-sheet|\bthe sheet\b|\bsheet row\b", re.I)
SHEET_DENIAL = re.compile(r"\b(not in the sheet|isn't in the sheet|aren't in the sheet|only has|does not match|doesn't match|"
                          r"disagree|not copied|unchanged|not changed|check which)", re.I)
# What a sentence may claim the sheet holds, and the column-name parts that would have to exist for it to be true.
SHEET_METRICS = [
    (re.compile(r"\bweekly\b|\bthis week\b|\bper week\b", re.I), ["week"]),
    (re.compile(r"\baffiliate gmv\b|\bgmv from affiliates\b", re.I), ["affiliate", "gmv"]),
    (re.compile(r"\bposts?\b", re.I), ["post"]),
    (re.compile(r"\bnew affiliates\b", re.I), ["new"]),
    (re.compile(r"\bretention\b", re.I), ["retention"]),
]


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    return dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else None


def body_lines(text):
    # Lines a reader sees, without front matter and links, so file names and dates in links don't count.
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"`[^`]*`", "", text)
    return [line for line in text.splitlines() if line.strip()]


def find_sheet(recap_path):
    """The brain's sheet, found by walking up from the recap: meetings/ -> knowledge/reference/."""
    for parent in Path(recap_path).resolve().parents:
        for candidate in (parent / "reference" / "accounts-sheet.csv",
                          parent / "knowledge" / "reference" / "accounts-sheet.csv",
                          parent / "brain" / "knowledge" / "reference" / "accounts-sheet.csv"):
            if candidate.exists():
                return candidate
    return None


def false_sheet_claims(text, sheet_path):
    columns = Path(sheet_path).read_text().splitlines()[0].lower().split(",")
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    wrong = []
    for sentence in re.split(r"(?<=[.;])\s+|\n", body):
        if not SHEET_MENTION.search(sentence) or SHEET_DENIAL.search(sentence):
            continue
        for pattern, parts in SHEET_METRICS:
            if pattern.search(sentence) and not any(all(p in c for p in parts) for c in columns):
                wrong.append(sentence.strip()[:90])
                break
    return wrong


CANT_TELL = "can't tell where the client left, needs a person"
SYSTEM_LINE = re.compile(r"^(?:\d\d:\d\d )?(\[[^\]]*\])\s*$")
# Bracketed lines a person has confirmed: the ones that mean someone left ({name} is the person) and the ones that don't.
# Any other bracketed line could be a leave in a new format, so it escalates until it's added here.
SYSTEM_LINES_FILE = Path(__file__).parent / "system-lines.json"
_known = json.loads(SYSTEM_LINES_FILE.read_text())
LEFT_LINES = [re.compile(re.escape(p).replace(re.escape("{name}"), "(?P<name>.+?)") + "$") for p in _known["left"]]
NOT_LEFT_LINES = set(_known["not_left"])


class CantTell(Exception):
    """The transcript doesn't say clearly where the client left, so a person has to look."""

    def __init__(self, why):
        super().__init__(f"{CANT_TELL}: {why}")


def system_lines(transcript):
    """Bracketed lines of the call itself, like [Recording ended], without the attendee list."""
    return [line.strip() for line in transcript.splitlines() if SYSTEM_LINE.match(line)]


def attendees(transcript):
    """[(name, company or None)] from the front matter."""
    m = re.search(r"attendees:\s*\[(.*?)\]", transcript)
    if not m:
        return []
    people = []
    for item in re.findall(r"[^,(]+(?:\([^)]*\))?", m.group(1)):
        name, _, org = item.partition("(")
        if name.strip():
            people.append((name.strip(), org.rstrip(")").strip() or None))
    return people


def client_names(transcript):
    """Everyone not from Brightline. At most one attendee may have no company tag, or nobody can tell who it is."""
    people = attendees(transcript)
    untagged = [name for name, org in people if org is None]
    if len(untagged) > 1:
        raise CantTell(f"{len(untagged)} attendees have no company: {', '.join(untagged)}")
    clients = {name for name, org in people if org is None or "brightline" not in org.lower()}
    if not clients:
        raise CantTell("no client among the attendees")
    return clients


def client_left_at(transcript):
    """Index of the line where the last client attendee left, or None if the client stayed to the end.

    The one place that decides this, for both the leak check and recap.py's cut. Raises CantTell when it can't.
    """
    clients = client_names(transcript)
    people = [name for name, _ in attendees(transcript)]
    lines = transcript.splitlines()
    cut = None
    shared = {}  # first name that several attendees have -> lines where "[<first name> left the call]" appeared
    for i, line in enumerate(lines):
        m = SYSTEM_LINE.match(line)
        if not m or m.group(1) in NOT_LEFT_LINES:
            continue
        said = next((left.match(m.group(1)).group("name").strip() for left in LEFT_LINES if left.match(m.group(1))), None)
        if said is None:
            raise CantTell(f"unknown bracketed line {line.strip()!r}, add it to {SYSTEM_LINES_FILE} "
                           f"under \"left\" or \"not_left\"")
        same_first = [name for name in people if name.split()[0] == said]
        if said in people or len(same_first) == 1:
            if (said if said in people else same_first[0]) in clients:
                cut = i
        elif same_first:
            shared.setdefault(said, []).append(i)
        else:
            raise CantTell(f"{line.strip()!r} names nobody on the attendee list")
    for said, at in shared.items():
        same_first = [name for name in people if name.split()[0] == said]
        if not clients & set(same_first):
            continue
        # Only once every attendee with that first name has left do we know the client among them is gone.
        if len(at) < len(same_first):
            raise CantTell(f"[{said} left the call] {len(at)} time(s), but {len(same_first)} attendees are "
                           f"called {said}: {', '.join(same_first)}")
        cut = max(at[-1], -1 if cut is None else cut)
    if cut is None:
        last = next((line for line in reversed(lines) if line.strip()), "")
        if not last.strip().endswith("[Recording ended]"):
            raise CantTell("no client leave marker and no [Recording ended] at the end")
    return cut


def after_client_left(transcript):
    """Transcript lines spoken after the last client attendee left."""
    cut = client_left_at(transcript)
    if cut is None:
        return []
    spoken = []
    for line in transcript.splitlines()[cut + 1:]:
        m = re.match(r"^\d\d:\d\d [^:]+: (.*)$", line)
        if m:
            spoken.append(m.group(1))
    return spoken


def word_ngrams(text, n=4):
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def run_checks(recap_path, transcript_path=None, sheet_path=None):
    text = Path(recap_path).read_text()
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))

    check("file name YYYY-MM-DD-slug.md", bool(FILENAME.match(Path(recap_path).name)), Path(recap_path).name)

    fm = front_matter(text)
    missing = [k for k in REQUIRED_FRONT if not fm.get(k, "").strip()]
    check("front matter complete", not missing, "missing: " + ", ".join(missing) if missing else "")

    missing = [s for s in REQUIRED_SECTIONS if section(text, s) is None]
    check("all template sections", not missing, "missing: " + ", ".join(missing) if missing else "")

    summary = section(text, "Summary") or ""
    bullets = [line for line in summary.splitlines() if line.lstrip().startswith("- ")]
    check("summary is 3 to 6 bullets", 3 <= len(bullets) <= 6, f"{len(bullets)} bullets")

    actions = section(text, "Action items") or ""
    rows = [line for line in actions.splitlines() if line.startswith("|") and not re.match(r"^\|[\s|:-]+\|$", line)]
    rows = [r for r in rows if not re.match(r"^\|\s*Owner\s*\|", r, re.I)]
    bad = []
    for r in rows:
        cells = [c.strip() for c in r.strip("|").split("|")]
        if len(cells) != 3 or not cells[0] or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[2]):
            bad.append(r)
    if not rows and "none" not in actions.lower():
        bad.append("no action item table")
    check("every action item has owner and YYYY-MM-DD due", not bad, "; ".join(bad))

    typed = []
    for line in body_lines(text):
        if not PERF_WORDS.search(line) or DECISION_WORDS.search(line):
            continue
        # "30-day GMV" or "within 48 hours" name a period, not a performance figure.
        nums = [n for n in NUMBER.findall(PERIOD.sub("", DATE_LIKE.sub("", line))) if n.strip()]
        if nums:
            typed.append(line.strip()[:80])
    check("no performance numbers typed in", not typed, " | ".join(typed))

    hits = [line.strip()[:80] for line in body_lines(text)
            if PRIVATE_WORDS.search(line) and "held back" not in line.lower()]
    check("no private or commercial content", not hits, " | ".join(hits))

    hits = [line.strip()[:80] for line in body_lines(text) if OPINION_WORDS.search(line)]
    check("no opinions about people or the call", not hits, " | ".join(hits))

    sheet_path = sheet_path or find_sheet(recap_path)
    if sheet_path:
        wrong = false_sheet_claims(text, sheet_path)
        check("claims about the sheet match its columns", not wrong, " | ".join(wrong))

    if transcript_path:
        try:
            after = after_client_left(Path(transcript_path).read_text())
        except CantTell as e:
            check("nothing from after the client left", False, str(e))
        else:
            leaked = set()
            recap_grams = word_ngrams(text)
            for line in after:
                leaked |= word_ngrams(line) & recap_grams
            check("nothing from after the client left", not leaked, ", ".join(sorted(leaked))[:120])

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("recap")
    parser.add_argument("--transcript")
    parser.add_argument("--sheet", help="accounts-sheet.csv; found from the recap's brain if left out")
    args = parser.parse_args()
    results = run_checks(args.recap, args.transcript, args.sheet)
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))
    failed = sum(not ok for _, ok, _ in results)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
