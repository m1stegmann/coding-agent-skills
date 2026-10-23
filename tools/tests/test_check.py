import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import check  # noqa: E402

SKILL = "---\nname: {name}\ndescription: Does one thing well.\n---\n\n# {name}\n\nRun the tool.\n"


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.plugin("demo", ["demo-run"])

    def tearDown(self):
        self.tmp.cleanup()

    def plugin(self, name, skills, listed=True):
        folder = self.root / "plugins" / name
        (folder / ".claude-plugin").mkdir(parents=True)
        (folder / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": name, "version": "0.1.0", "description": "d"}))
        (folder / "README.md").write_text("# demo\n")
        for skill in skills:
            (folder / "skills" / skill).mkdir(parents=True)
            (folder / "skills" / skill / "SKILL.md").write_text(SKILL.format(name=skill))
        marketplace = self.root / ".claude-plugin" / "marketplace.json"
        marketplace.parent.mkdir(exist_ok=True)
        catalog = json.loads(marketplace.read_text()) if marketplace.exists() else {"name": "lib", "owner": {"name": "o"}, "plugins": []}
        if listed:
            catalog["plugins"].append({"name": name, "source": f"./plugins/{name}"})
        marketplace.write_text(json.dumps(catalog))
        return folder

    def problems(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return check.check(self.root)[0]

    def test_a_valid_library_passes(self):
        self.assertEqual(self.problems(), [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(check.main(["--root", str(self.root)]), 0)
        self.assertIn("ok: 1 plugin(s)", out.getvalue())

    def test_a_top_level_bin_is_refused(self):
        (self.root / "plugins" / "demo" / "bin").mkdir()
        self.assertTrue(any("bin/" in p for p in self.problems()))

    def test_the_skill_name_must_match_its_folder_and_the_rules(self):
        path = self.root / "plugins" / "demo" / "skills" / "demo-run" / "SKILL.md"
        path.write_text(SKILL.format(name="Demo_Run"))
        problems = self.problems()
        self.assertTrue(any("name must be 'demo-run'" in p for p in problems))
        self.assertTrue(any("lowercase words" in p for p in problems))

    def test_skill_names_are_unique_across_plugins(self):
        self.plugin("other", ["demo-run"])
        self.assertTrue(any("also used by" in p for p in self.problems()))

    def test_paths_of_one_machine_are_found_and_plugin_variables_are_not(self):
        path = self.root / "plugins" / "demo" / "skills" / "demo-run" / "SKILL.md"
        path.write_text(SKILL.format(name="demo-run") + 'Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/x.py"`.\n')
        self.assertEqual(self.problems(), [])
        for line in ("Run `~/.local/bin/x`.", "See /home/someone/x.", "See /Users/Someone/x.", r"See C:\Tools\x."):
            path.write_text(SKILL.format(name="demo-run") + line + "\n")
            self.assertTrue(any("a path of one machine" in p for p in self.problems()), line)

    def test_every_plugin_folder_is_listed_and_named_like_its_entry(self):
        self.plugin("unlisted", ["unlisted-run"], listed=False)
        manifest = self.root / "plugins" / "demo" / ".claude-plugin" / "plugin.json"
        manifest.write_text(json.dumps({"name": "renamed", "description": "d"}))
        problems = self.problems()
        self.assertTrue(any("plugins/unlisted: not listed" in p for p in problems))
        self.assertTrue(any("plugin.json name must be 'demo'" in p for p in problems))
        self.assertTrue(any("has no version" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
