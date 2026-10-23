---
name: backlog-init
description: Sets up the file-based backlog in a repository (backlog/<id>-<slug>.md items, append-only backlog/history.jsonl) and adds the backlog rules to AGENTS.md. Use when the user asks to start a backlog in a repository, or to move an existing TODO list or BACKLOG.md into this format.
---

# Set up a backlog

The backlog is kept mostly by agents. Its files are the shared memory between sessions and tools (Claude Code, Grok, Copilot CLI), so every rule an agent needs must be in the repository, not only in this skill.

The `backlog` command, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog.py"` (written `backlog` below; if that path is not absolute, the script is `scripts/backlog.py` two folders above this skill's folder), does the bookkeeping. `backlog --help` lists the commands.

## Steps

1. Go to the repository root (`git rev-parse --show-toplevel`). Read `AGENTS.md` and `CLAUDE.md` if they exist, and look for an existing backlog, TODO list or issue list in the repo.
2. Run `backlog init`. It creates `backlog/` and an empty `backlog/history.jsonl`, and keeps what already exists. There is no overview file: `backlog list` shows the open items with their state, and `backlog next` names the next workable one.
   - Only if the user wants an index file for readers without the CLI: `backlog init --index` creates a `BACKLOG.md` with a generated list that every `backlog` command keeps current. An existing `BACKLOG.md` without the markers `<!-- backlog:start -->` and `<!-- backlog:end -->` is left alone, and `--index` refuses to write into it.
   - A `BACKLOG.md` from an older version of this format (with the generated list) keeps working. To retire it, move its free text (purpose, notes) into `AGENTS.md` or a decision part, delete the file and run `backlog check`.
3. Move existing content, if there is any:
   - Each open entry becomes an item, written as the `backlog-add` skill says, so an agent can work on it without the old context.
   - Each standing decision or scope note becomes a part, written as the `backlog-decide` skill says.
   - Drop finished entries. If one carries a decision that still holds, record it as a part.
4. Add the section below to `AGENTS.md` at the root (create the file if it is missing), in the language of that file. If a section on the backlog already exists, replace it. Keep the rules in the section: agents without the skills (a teammate's machine, a cloud agent) work from it alone.
5. If `CLAUDE.md` exists and does not import `AGENTS.md`, add a line `@AGENTS.md`. If there is no `CLAUDE.md`, create it with exactly that line.
6. Run `backlog check`. It must print `ok`.
7. Report what was created and moved. Don't commit unless the user or the repository's workflow says so.

## Section for AGENTS.md

```markdown
## Backlog

Open work is one file per item in `backlog/`; `backlog list` shows them with their state. Finished items, decisions and corrections are in `backlog/history.jsonl`. Agents keep both with the `backlog` CLI and the skills `backlog-add`, `backlog-finish` and `backlog-decide`. Without them, follow these rules by hand.

- **Items.** `backlog/<id>-<slug>.md`: the first line is `# <title>`, a sentence that states the end state; then the context an agent needs to start cold; optionally `**Depends on:** <ids>` and `**Blocked:** <what is needed, from whom>`; then `**Done when**` with one bullet per check that can be verified in the repo. A new item takes the next integer above the highest id in the history and in `backlog/`. `backlog next` names the next workable item.
- **Decisions.** Before changing behavior that a decision covers, read it (`backlog parts`, `backlog part <slug>`). A decision is a `section` line with a stable `part` slug; the last line with that slug is the current text. A changed decision is a new line with the full new text.
- **Finish completely or not at all.** Close an item only when every **Done when** bullet is verified against the repository as it stands now, and record how each one was verified. Never close an item partly or split it to call a part finished. A bullet that needs something outside the repo makes the item blocked (`backlog block <id> "<reason>"`), not finished. A `**Person:**` bullet needs that person's confirmation.
- **history.jsonl is append-only.** UTF-8, one JSON object per line, every line ends with a newline, `seq` is the line number. Never edit, reorder or delete a line; a correction is a new `correction` line with `refersTo`.
- Work found on the way that is not part of the current item becomes a new item, not a silent extra.
```
