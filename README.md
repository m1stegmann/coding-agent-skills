# coding-agent-skills

Skills, agents and small tools for coding agents. The repository is a plugin marketplace in the Claude Code format, which Claude Code, GitHub Copilot CLI and Grok read; every plugin's skills follow the [Agent Skills](https://agentskills.io) format (`SKILL.md`).

| Plugin | What it does |
|---|---|
| [backlog](plugins/backlog/) | A file-based backlog that coding agents keep: items with checkable **Done when** bullets, decisions, and finishing only after an independent check |
| [scripting](plugins/scripting/) | Cross-platform rules for agents' helper scripts: Python through uv, and C# file-based apps in .NET 10+ solutions; writes them into a repository's `AGENTS.md` |

## Install

| Tool | Add the marketplace, then install a plugin |
|---|---|
| Claude Code | `claude plugin marketplace add m1stegmann/coding-agent-skills`, then `claude plugin install backlog@coding-agent-skills` (or `/plugin` in a session) |
| GitHub Copilot CLI | `copilot plugin marketplace add m1stegmann/coding-agent-skills`, then `copilot plugin install backlog@coding-agent-skills` |
| Grok | `grok plugin marketplace add m1stegmann/coding-agent-skills`, then install from `grok plugin marketplace list` |
| Claude desktop app, Cowork | **Customize > Plugins > Add marketplace**, `m1stegmann/coding-agent-skills`. The plugins are built for coding work in a repository; installed on your account they also reach Claude Code as synced plugins |

For a whole repository, run `claude plugin marketplace add m1stegmann/coding-agent-skills --scope project` there once and commit the `.claude/settings.json` it writes: Claude Code then offers the marketplace to everyone who trusts the folder.

While you work on the library itself, add your local checkout instead (`claude plugin marketplace add ./coding-agent-skills`): Claude Code then loads the files in place, and edits take effect at the next session or `/reload-plugins`.

## Where it works

The marketplace and plugin manifests are `.claude-plugin/marketplace.json` and `plugins/<name>/.claude-plugin/plugin.json`. Copilot CLI and Grok read the same files.

| | Claude Code | Grok | Copilot CLI | Cowork | Chat |
|---|---|---|---|---|---|
| Skills | yes, as `<plugin>:<skill>` | yes, as `<plugin>:<skill>` | yes (documented) | yes (documented) | yes (documented) |
| Agents (`agents/*.md`) | yes | yes | expects `*.agent.md` | yes (documented) | ignored |
| Scripts in `scripts/` | yes: `${CLAUDE_PLUGIN_ROOT}` is filled in | yes | not tested | not tested | not tested |
| A top-level `bin/` | on the `PATH` | not tested | not documented | refuses the plugin | refuses the plugin |

"Yes" without a note was tested with a plugin of this library; "documented" is from the tool's documentation only. Each plugin's README says what was tested where.

## Rules for a plugin

`python3 tools/check.py` enforces them, and the [check workflow](.github/workflows/check.yml) runs it with every plugin's tests on Linux and Windows.

- **Layout.** `plugins/<name>/` with `.claude-plugin/plugin.json` (`name` equal to the folder and to the marketplace entry, a `version`, a `description`), `skills/<skill>/SKILL.md`, optionally `agents/<agent>.md`, `scripts/` and `tests/`, and a `README.md`. Every plugin folder is listed in the marketplace.
- **No top-level `bin/`.** Cowork and the chat refuse a plugin that has one. Put executables in `scripts/` and call them as `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/<tool>"`, with a fallback for tools that don't fill the variable in (a path relative to the skill's folder).
- **Skill and agent names** are lowercase words joined by hyphens, at most 64 characters, equal to the folder (skills) or file (agents) name, and unique across the whole library: not every tool prefixes them with the plugin name. Every `SKILL.md` and agent starts with frontmatter that has `name` and `description`.
- **Portable text.** No paths of one machine (`~/…`, `/home/…`, `C:\…`) in skills or agents, and no names of a company, customer or private project.
- **Scripts** use the Python standard library only and work on Linux, macOS and Windows; they have tests in `tests/`, and start with a PEP 723 block (`# /// script`) so that skills call them as `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/<tool>"`, with `python3` (Windows: `py -3`) as the fallback when `uv` is missing.
- **Versions.** Raise a plugin's `version` with every change that should reach users: installs stay on their cached copy until it changes.

## License

[MIT](LICENSE)
