---
name: backlog-add
description: Adds an item to the repository backlog (backlog/<id>-<slug>.md). Use when work is found that is not done now (a request the user defers, a follow-up or bug noticed outside the current item's scope, a step the current item depends on), or when the user asks to add, record or plan backlog items. Needs a backlog/ folder; see backlog-init.
---

# Add a backlog item

The reader of an item is usually an agent in a later session or another tool, with none of the current context. Write so that it can start, and know when it is finished, from the item and the repository alone.

The `backlog` command, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog.py"` (written `backlog` below; if that path is not absolute, the script is `scripts/backlog.py` two folders above this skill's folder), assigns the id, writes the file and updates `BACKLOG.md`. Never pick an id or edit `BACKLOG.md` yourself.

## Before writing

1. Run `backlog list` and `backlog parts`. If an open item already aims at the same end state, extend that item (edit its file) instead of adding a duplicate. Search `backlog/history.jsonl` for the key terms: maybe the work was done or decided against.
2. Size: an item is finished as a whole in one working session. If the work is bigger, add several items now, linked with `**Depends on:**`. Never plan to finish part of an item.

## Format

```markdown
# <Title: one sentence that states the end state, not the activity>

<Context: why, what is there now (paths, commands, figures), constraints, the decisions it follows (by part slug), what is out of scope.>

**Depends on:** 12, 14

**Done when**

- <check an agent can verify now in the repo: a command and its expected result, a test, a file and what it contains, a figure>
- **Person:** <role> <what that person confirms>
- <the repository's standard gate from AGENTS.md, e.g. "`dotnet build` and `dotnet test` pass">
```

- Title: "The export writes UTF-8", not "Fix export encoding". The title is copied into the history unchanged.
- Context names files, commands and decision parts instead of "as discussed" or "see chat". Leave out nothing a cold reader needs, and put nothing in that the item doesn't need. No secrets.
- **Done when** bullets are checks, not wishes. "Works well" or "is clean" is not a check. Each bullet should fail visibly if the work is missing. Name the evidence: which test, which command and output, which file.
- A `**Person:**` bullet is a check only a person can make (an approval, a manual test on real hardware). Agents can't finish the item until that person has confirmed, so use it only when it's really needed.
- Leave out `**Depends on:**` if there are no dependencies. Never write `**Blocked:**` by hand; use `backlog block`.
- Write in the repository's language (see AGENTS.md). Use English if nothing says otherwise.

## Add

```bash
backlog add --slug <short-english-slug> <<'EOF'
# ...
EOF
```

It prints the new id and path. A refusal names what is missing (title line, **Done when** bullets, an unknown dependency): fix it and run it again.

Report the id and title. Don't start the work unless the user or the running workflow asks for it.
