import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import backlog  # noqa: E402

ITEM = """# The export writes UTF-8.

The export writes Latin-1 today (`src/export.py`).

**Done when**

- `pytest tests/test_export.py` passes.
- The README names the encoding.
"""


class BacklogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.run_cli("init")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, stdin="", code=0):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(stdin)), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = backlog.main(["-C", str(self.root), *args])
        self.assertEqual(result, code, err.getvalue() + out.getvalue())
        return out.getvalue()

    def history(self):
        return [json.loads(line) for line in (self.root / "backlog" / "history.jsonl").read_text().splitlines()]

    def test_init_creates_layout_and_passes_check(self):
        self.assertTrue((self.root / "backlog" / "history.jsonl").exists())
        self.assertIn("None.", (self.root / "BACKLOG.md").read_text())
        self.run_cli("check")

    def test_add_assigns_next_id_and_lists_item(self):
        self.assertEqual(self.run_cli("add", "--slug", "utf8-export", stdin=ITEM).split()[0], "1")
        self.assertEqual(self.run_cli("add", "--slug", "second", stdin=ITEM).split()[0], "2")
        self.assertIn("[1 The export writes UTF-8.](backlog/1-utf8-export.md)", (self.root / "BACKLOG.md").read_text())
        self.run_cli("check")

    def test_add_refuses_item_without_done_when_or_bad_slug(self):
        self.run_cli("add", "--slug", "x", stdin="# Title\n\nNo checks.\n", code=2)
        self.run_cli("add", "--slug", "Bad_Slug", stdin=ITEM, code=2)
        self.run_cli("add", "--slug", "x", stdin=ITEM.replace("**Done when**", "**Depends on:** 9\n\n**Done when**"), code=2)
        self.assertEqual(list((self.root / "backlog").glob("*.md")), [])

    def test_next_skips_blocked_and_waiting_items(self):
        self.run_cli("add", "--slug", "a", stdin=ITEM)
        self.run_cli("add", "--slug", "b", stdin=ITEM.replace("**Done when**", "**Depends on:** 1\n\n**Done when**"))
        self.run_cli("block", "1", "an API key from the platform team")
        self.run_cli("next", code=1)
        md = (self.root / "BACKLOG.md").read_text()
        self.assertIn("): an API key from the platform team", md)
        self.assertIn("(after 1)", md)
        self.run_cli("unblock", "1")
        self.assertEqual(self.run_cli("next").split()[0], "1")
        self.assertEqual((self.root / "backlog" / "1-a.md").read_text(), ITEM)
        self.run_cli("check")

    def test_finish_requires_evidence_for_every_check(self):
        self.run_cli("add", "--slug", "a", stdin=ITEM)
        one = json.dumps([{"check": "tests", "evidence": "pytest: 4 passed"}])
        self.run_cli("finish", "1", stdin=one, code=2)
        unmet = json.dumps({"allMet": True, "checks": [{"evidence": "ok", "met": True}, {"evidence": "no", "met": False, "gap": "README silent"}]})
        self.run_cli("finish", "1", stdin=unmet, code=2)
        self.assertTrue((self.root / "backlog" / "1-a.md").exists())
        self.assertEqual(self.history(), [])

    def test_finish_records_item_with_verification_and_removes_file(self):
        self.run_cli("add", "--slug", "a", stdin=ITEM)
        verdict = {"id": 1, "allMet": True, "checks": [
            {"check": "pytest", "met": True, "evidence": "pytest tests/test_export.py: 4 passed", "gap": ""},
            {"check": "README", "met": True, "evidence": "README.md line 12: 'UTF-8'", "gap": ""}]}
        self.run_cli("finish", "1", stdin=json.dumps(verdict))
        [entry] = self.history()
        self.assertEqual((entry["seq"], entry["kind"], entry["id"], entry["source"]), (1, "completed", 1, "backlog/1-a.md"))
        self.assertEqual(entry["body"], ITEM)
        self.assertEqual(entry["verification"][1], {"check": "README", "evidence": "README.md line 12: 'UTF-8'"})
        self.assertFalse((self.root / "backlog" / "1-a.md").exists())
        self.assertIn("finished", self.run_cli("show", "1"))
        self.assertEqual(self.run_cli("next-id").strip(), "2")
        self.run_cli("check")

    def test_finish_refuses_blocked_item(self):
        self.run_cli("add", "--slug", "a", stdin=ITEM)
        self.run_cli("block", "1", "a decision by the product owner")
        both = json.dumps([{"evidence": "x"}, {"evidence": "y"}])
        self.run_cli("finish", "1", stdin=both, code=2)

    def test_decide_latest_part_wins_and_correction_is_shown(self):
        self.run_cli("decide", "--part", "ui-stack", "--title", "UI stack", "--source", "user 2026-10-23", stdin="Razor Pages.")
        self.run_cli("decide", "--part", "ui-stack", "--title", "UI stack", "--source", "item 4", stdin="Razor Pages + htmx.")
        self.run_cli("correct", "--refers-to", "2", "--source", "review", stdin="htmx is pinned to 2.0.")
        text = self.run_cli("part", "ui-stack")
        self.assertIn("## UI stack\n\nRazor Pages + htmx.", text)
        self.assertIn("htmx is pinned to 2.0.", text)
        self.assertNotIn("Razor Pages.\n", text)
        correction = self.history()[2]
        self.assertEqual((correction["kind"], correction["refersTo"], correction["part"]), ("correction", 2, "ui-stack"))
        self.run_cli("check")

    def test_check_finds_tampering(self):
        self.run_cli("add", "--slug", "a", stdin=ITEM)
        history = self.root / "backlog" / "history.jsonl"
        history.write_text('{"seq": 5, "kind": "completed", "id": 1, "title": "t", "recorded": "x", "source": "s", "body": "b"}')
        (self.root / "backlog" / "notes.txt").write_text("x")
        out = self.run_cli("check", code=1)
        for expected in ("does not end with a newline", "must be the line number", "notes.txt", "already finished"):
            self.assertIn(expected, out)

    def test_check_finds_hand_edited_list(self):
        self.run_cli("add", "--slug", "a", stdin=ITEM)
        md = self.root / "BACKLOG.md"
        md.write_text(md.read_text().replace("- [1 ", "- [7 "))
        self.assertIn("out of date", self.run_cli("check", code=1))
        self.run_cli("render")
        self.run_cli("check")

    def test_render_keeps_free_text_around_the_block(self):
        md = self.root / "BACKLOG.md"
        md.write_text("# Project\n\nIntro.\n\n<!-- backlog:start -->\n<!-- backlog:end -->\n\nFooter.\n")
        self.run_cli("render")
        text = md.read_text()
        self.assertTrue(text.startswith("# Project\n\nIntro.\n\n<!-- backlog:start (generated"))
        self.assertTrue(text.endswith("<!-- backlog:end -->\n\nFooter.\n"))

    def test_without_fcntl_the_cli_still_writes(self):
        """Windows has no fcntl: no lock, but every command works."""
        with mock.patch.object(backlog, "fcntl", None):
            self.run_cli("add", "--slug", "no-lock", stdin=ITEM)
            self.run_cli("decide", "--part", "p", "--title", "P", "--source", "test", stdin="Body.\n")
            self.run_cli("check")

    def test_text_is_utf8_even_when_the_console_is_not(self):
        """The console of Windows is cp1252: umlauts and arrows must still reach the files and the output unchanged."""
        text = "# Ärger → Übersicht\n\nWährend der Fahrt.\n\n**Done when**\n\n- Die Prüfung läuft → grün.\n"
        stdin = io.TextIOWrapper(io.BytesIO(text.encode("utf-8")), encoding="cp1252")
        stdout_bytes = io.BytesIO()
        stdout = io.TextIOWrapper(stdout_bytes, encoding="cp1252", write_through=True)
        with mock.patch("sys.stdin", stdin), mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(backlog.main(["-C", str(self.root), "add", "--slug", "umlauts"]), 0)
            self.assertEqual(backlog.main(["-C", str(self.root), "show", "1"]), 0)
        self.assertEqual((self.root / "backlog" / "1-umlauts.md").read_text(encoding="utf-8"), text)
        self.assertIn("Prüfung läuft → grün".encode("utf-8"), stdout_bytes.getvalue())


if __name__ == "__main__":
    unittest.main()
