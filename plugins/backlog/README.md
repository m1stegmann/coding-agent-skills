# backlog

A file-based backlog that coding agents keep. Open work is one file per item, finished work and decisions go to an append-only history, and an item is closed only when an independent check has verified every **Done when** bullet against the repository.

```
backlog/<id>-<slug>.md   one open item per file: title, context, **Depends on:**, **Blocked:**, **Done when**
backlog/history.jsonl    append-only: completed items (with verification), decisions (section/part), corrections
BACKLOG.md               optional index (`backlog init --index`): free text plus a generated list; not needed, `backlog list` shows the same
```

| Part | What it does |
|---|---|
| `scripts/backlog.py` | The CLI for all bookkeeping: ids, `seq`, JSON lines, the overview (`list`, `next`), locking, `check`. Agents never edit `history.jsonl` by hand. |
| `skills/backlog-init` | Sets up a repository and writes the backlog rules into its `AGENTS.md`, so agents without this plugin follow them too. |
| `skills/backlog-add` | Writes an item an agent can pick up cold, with checkable **Done when** bullets. |
| `skills/backlog-finish` | Verifies every bullet fresh (with `backlog-verifier`), records the evidence, or blocks the item. |
| `skills/backlog-decide` | Records or replaces a decision part, or corrects a history line. |
| `agents/backlog-verifier.md` | Independent, read-only check of one item; returns JSON that `backlog finish` takes. |

**0.2.0:** `BACKLOG.md` is optional. `backlog init` no longer creates it (`--index` does), `backlog list` shows blocked reasons and waits, and a repository that still has the generated list in a `BACKLOG.md` keeps working: the CLI refreshes and checks it as before.

The skills call the CLI as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog.py"`, with a path relative to the skill's folder for tools that don't fill the variable in. It needs Python 3.10 or later and nothing else; on Windows it runs without a file lock (one agent at a time per checkout), and its input and output are UTF-8 whatever the console's code page is.

A repository that wants the CLI in its own build (for example `backlog check` as a test) copies `scripts/backlog.py` in.

## Tested (2026-10-23)

| | Result |
|---|---|
| Claude Code 2.1.309 | `claude plugin validate --strict` passes for the marketplace and the plugin. Added and installed from a local checkout: 4 skills and 1 agent, about 460 tokens always on. In a headless session, `backlog:backlog-init` and `backlog:backlog-add` set up a backlog in a fresh repository (with the `AGENTS.md` section, and without a `BACKLOG.md`, as 0.2.0 does) and added a correct item; every call went to the bundled CLI with `${CLAUDE_PLUGIN_ROOT}` filled in. |
| Grok 1.0.67 | `grok plugin validate` passes. Added and installed from a local checkout: the skills appear as `backlog:backlog-add` and so on, the agent as `backlog:backlog-verifier`. The same headless task gave the same result, with the CLI called from the installed copy. |
| GitHub Copilot CLI | Not tested (not installed). Its documentation says it reads `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json` and `skills/`; it expects agents as `*.agent.md`, which this plugin does not ship yet. |
| Cowork, chat | Not tested. The plugin has no top-level `bin/`, so they accept it; the skills assume a Git repository and a shell. |
| CLI | 16 unit tests, including the run without `fcntl`, a cp1252 console and a repository without a `BACKLOG.md`; the check workflow runs them on Linux and Windows. |

## License

[MIT](../../LICENSE)
