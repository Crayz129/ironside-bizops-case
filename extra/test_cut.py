"""Tests for where recap.py cuts the transcript. No model calls.

Usage: python3 -I extra/test_cut.py
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_recap  # noqa: E402
from check_recap import CANT_TELL, CantTell, after_client_left, system_lines  # noqa: E402
from recap import cut_transcript  # noqa: E402

ROOT = Path(__file__).parent.parent


def call(attendees, *body):
    return f"---\ntitle: test\nattendees: [{attendees}]\n---\n\n" + "\n".join(body) + "\n"


TWO = "Dana Reyes (Kettle & Crumb), Marcus Obi (Brightline)"


class Cut(unittest.TestCase):
    def assertCantTell(self, text):
        with self.assertRaises(CantTell) as e:
            cut_transcript(text)
        self.assertIn(CANT_TELL, str(e.exception))

    def test_left_the_call_cuts_exactly_the_lines_after_it(self):
        text = call(TWO, "00:01 Dana Reyes: Hi.", "00:05 [Dana Reyes left the call]",
                    "00:06 Marcus Obi: Between us.", "00:09 Marcus Obi: Margin.", "00:10 [Recording ended]")
        kept, dropped, span = cut_transcript(text)
        self.assertEqual(dropped, 3)
        self.assertEqual(span, "00:06-00:10")
        self.assertIn("00:05 [Dana Reyes left the call]", kept)
        self.assertNotIn("Between us", kept)
        self.assertEqual(after_client_left(text), ["Between us.", "Margin."])

    def test_left_the_call_as_last_line_cuts_nothing_after_it(self):
        _, dropped, _ = cut_transcript(call(TWO, "00:01 Dana Reyes: Hi.", "00:05 [Dana Reyes left the call]"))
        self.assertEqual(dropped, 0)

    def test_no_marker_with_recording_ended_cuts_0(self):
        text = call(TWO, "00:01 Dana Reyes: Hi.", "00:02 Marcus Obi: Bye.", "00:03 [Recording ended]")
        self.assertEqual(cut_transcript(text), (text, 0, None))

    def test_no_marker_without_recording_ended_escalates(self):
        self.assertCantTell(call(TWO, "00:01 Dana Reyes: Hi.", "00:02 Marcus Obi: Bye."))

    def test_unknown_bracketed_line_escalates_and_says_where_to_add_it(self):
        text = call(TWO, "00:01 Dana Reyes: Hi.", "00:02 [Dana Reyes disconnected]",
                    "00:03 Marcus Obi: Margin.", "00:04 [Recording ended]")
        self.assertCantTell(text)
        with self.assertRaises(CantTell) as e:
            cut_transcript(text)
        self.assertIn("[Dana Reyes disconnected]", str(e.exception))
        self.assertIn("system-lines.json", str(e.exception))
        self.assertIn("00:02 [Dana Reyes disconnected]", system_lines(text))

    def test_line_added_to_the_known_lists_is_handled(self):
        text = call(TWO, "00:01 [Dana Reyes disconnected]", "00:02 Marcus Obi: Margin.",
                    "00:03 [Transcription paused]", "00:04 [Recording ended]")
        left, not_left = list(check_recap.LEFT_LINES), set(check_recap.NOT_LEFT_LINES)
        try:
            check_recap.LEFT_LINES.append(re.compile(r"\[(?P<name>.+?) disconnected\]$"))
            check_recap.NOT_LEFT_LINES.add("[Transcription paused]")
            self.assertEqual(cut_transcript(text)[1], 3)
        finally:
            check_recap.LEFT_LINES[:], check_recap.NOT_LEFT_LINES = left, not_left

    def test_brightline_leaving_is_not_the_client_leaving(self):
        text = call(TWO, "00:01 [Marcus Obi left the call]", "00:02 Dana Reyes: Hi.", "00:03 [Recording ended]")
        self.assertEqual(cut_transcript(text)[1], 0)

    def test_cut_is_after_the_last_client_to_leave(self):
        text = call("Dana Reyes (Kettle & Crumb), Jess Park (Kettle & Crumb), Marcus Obi (Brightline)",
                    "00:01 [Dana Reyes left the call]", "00:02 Jess Park: One more thing.",
                    "00:03 [Jess Park left the call]", "00:04 Marcus Obi: Margin.", "00:05 [Recording ended]")
        self.assertEqual(cut_transcript(text)[1], 2)

    def test_one_untagged_attendee_is_the_client(self):
        text = call("Theo Grant, Lena Varga (Brightline)", "00:01 [Theo Grant left the call]",
                    "00:02 Lena Varga: Fees.", "00:03 [Recording ended]")
        self.assertEqual(cut_transcript(text)[1], 2)

    def test_two_untagged_attendees_escalate(self):
        self.assertCantTell(call("Theo Grant, Lena Varga", "00:01 [Theo Grant left the call]",
                                 "00:02 Lena Varga: Fees.", "00:03 [Recording ended]"))

    def test_no_client_escalates(self):
        self.assertCantTell(call("Marcus Obi (Brightline), Tomas Leal (Brightline)", "00:01 [Recording ended]"))

    def test_no_attendee_list_escalates(self):
        self.assertCantTell("---\ntitle: test\n---\n\n00:01 Dana: Hi.\n00:02 [Recording ended]\n")

    def test_unique_first_name_matches(self):
        text = call(TWO, "00:01 [Dana left the call]", "00:02 Marcus Obi: Margin.", "00:03 [Recording ended]")
        self.assertEqual(cut_transcript(text)[1], 2)

    def test_two_danas_with_first_name_marker_escalates(self):
        self.assertCantTell(call("Dana Reyes (Kettle & Crumb), Dana Fox (Brightline)",
                                 "00:01 [Dana left the call]", "00:02 Dana Fox: Margin.", "00:03 [Recording ended]"))

    def test_two_client_danas_both_left_cuts_after_the_second(self):
        text = call("Dana Reyes (Kettle & Crumb), Dana Fox (Kettle & Crumb), Marcus Obi (Brightline)",
                    "00:01 [Dana left the call]", "00:02 Dana Fox: Bye.", "00:03 [Dana left the call]",
                    "00:04 Marcus Obi: Margin.", "00:05 [Recording ended]")
        self.assertEqual(cut_transcript(text)[1], 2)

    def test_two_client_danas_one_left_escalates(self):
        self.assertCantTell(call("Dana Reyes (Kettle & Crumb), Dana Fox (Kettle & Crumb), Marcus Obi (Brightline)",
                                 "00:01 [Dana left the call]", "00:02 Marcus Obi: Margin.", "00:03 [Recording ended]"))

    def test_two_danas_with_full_name_marker_is_clear(self):
        text = call("Dana Reyes (Kettle & Crumb), Dana Fox (Brightline)",
                    "00:01 [Dana Reyes left the call]", "00:02 Dana Fox: Margin.", "00:03 [Recording ended]")
        self.assertEqual(cut_transcript(text)[1], 2)

    def test_real_transcripts(self):
        for path, lines in [("inbox/call-1.md", 5), ("inbox/call-2.md", 0), ("workers/output/bad-recap-source.md", 2)]:
            with self.subTest(path):
                self.assertEqual(cut_transcript((ROOT / path).read_text())[1], lines)


if __name__ == "__main__":
    unittest.main(verbosity=2)
