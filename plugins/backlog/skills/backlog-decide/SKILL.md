---
name: backlog-decide
description: Records a decision or other standing fact (architecture choice, scope, out of scope, how to test, a convention) as a section in backlog/history.jsonl, replaces it when it changes, or corrects an earlier history line. Use when the user or the work settles something that later work must follow, when an existing decision changes, or when a history line turns out to be wrong.
---

# Record a decision

Decisions are the standing rules of a repository's backlog. Agents read the current text of a part (`backlog part <slug>`) before changing behavior it covers, and they read only the latest version. Write each part so it stands alone.

The `backlog` command, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog.py"` (written `backlog` below; if that path is not absolute, the script is `scripts/backlog.py` two folders above this skill's folder), appends the line. Never edit `history.jsonl` by hand.

## Decision or item?

- A decision states how things are or must be ("Short answers are graded by model X, with Y as the fallback").
- An item is work to get there. Often you need both: the decision now, and the work with `backlog-add`.
- Facts that only the current session needs belong in neither.

## Steps

1. `backlog parts`. If a part covers the topic, reuse its slug and read it with `backlog part <slug>`. Create a new slug only for a new topic: lowercase words joined by hyphens, stable and general (`grading`, `out-of-scope`, `how-to-test`).
2. Write the full current text, not a diff. When you change a part, start from its current text, change what changed, and keep what still holds.
   - State the rule, the reason in one sentence, and the boundary (what it does not cover).
   - Name files, settings and commands where they make the rule checkable.
   - Leave out how the discussion went, and alternatives that only matter as history.
3. Append it:

```bash
backlog decide --part grading --title "Short-answer grading" --source "user, 2026-10-23" <<'EOF'
<body; a "## <title>" heading is added if the body has none>
EOF
```

`--source` says where it came from: a user message with its date, an item ("item 27"), a review or an incident.

## Corrections

A correction says that an earlier line was wrong as written: a wrong fact in a finished item's body, a wrong title, a wrong date. A decision that changed is not a correction; append the new version of the part instead.

```bash
backlog correct --refers-to <seq> --source "<where the error was found>" <<'EOF'
<what was wrong, and what is right>
EOF
```

`backlog part <slug>` shows corrections together with the part they refer to. Run `backlog check` at the end.
