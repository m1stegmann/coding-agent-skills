---
name: backlog-finish
description: Closes a backlog item after every Done-when bullet is verified against the repository as it stands now, and records it with the evidence in backlog/history.jsonl. Use whenever work on a backlog item looks complete, before telling anyone it is done. Also use when an item cannot go on without something outside the repository, to mark it blocked.
---

# Finish a backlog item

An item is finished completely or not at all. Other agents trust a `completed` line without checking it again, so a wrong one costs more than an open item.

The `backlog` command, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog.py"` (written `backlog` below; if that path is not absolute, the script is `scripts/backlog.py` two folders above this skill's folder), records the item and deletes its file (and refreshes a `BACKLOG.md` index if the repository keeps one). Never edit `history.jsonl` by hand, nor the generated list of an index.

## Steps

1. `backlog show <id>`. Note each **Done when** bullet, in order.
2. If you made a decision during the work that later work must follow, record it first with the `backlog-decide` skill.
3. Verify each bullet fresh, against the repository as it stands now. A result from earlier in the session doesn't count: later changes can break an earlier check.
   - Prefer the `backlog-verifier` agent. It didn't do the work and checks independently. Claude Code: the Agent tool with `subagent_type: backlog-verifier`. Copilot CLI: the custom agent `backlog-verifier`. Grok: spawn a subagent of type `backlog-verifier`. Give it the item id and the repository path, plus any `**Person:**` confirmation quoted from this conversation. Don't give it your own conclusions.
   - Without subagents, check it yourself the same way: run each command now and read each file now.
4. Act on the result:
   - **Every bullet met:** pass the verdict (the verifier's JSON, or your own list of `{"check", "evidence"}`, one entry per bullet in order) to `backlog finish <id>` on stdin. Evidence says what was run or read and what it showed, briefly quoted: "`dotnet test`: 212 passed, 0 failed", not "tests pass".
   - **A bullet unmet and fixable in the repository:** keep working, then verify again from step 3. Don't close the item partly, split it, or leave a remainder for later.
   - **A bullet unmet because of something outside the repository** (a secret, a permission, a person's decision, an unconfirmed `**Person:**` bullet): `backlog block <id> "<what is needed, from whom>"` and stop work on this item. `backlog next` then skips it.
   - **A bullet that no longer fits** because a recorded decision or the user changed the goal: change the bullet in the item file only on that basis, name the decision or message in the evidence, and verify again.
5. Run `backlog check`.
6. Report each bullet as met or not met, and how it was verified. Don't commit unless the user or the repository's workflow says so.

```bash
backlog finish 27 <<'EOF'
[{"check": "pytest passes", "evidence": "pytest tests/test_export.py: 4 passed"},
 {"check": "README names the encoding", "evidence": "README.md:12 'The export writes UTF-8.'"}]
EOF
```

`finish` refuses when the number of entries differs from the number of bullets, when evidence is empty, when an entry says `"met": false`, when the item is blocked, or when it depends on open items. Treat a refusal as a sign that the item isn't finished. Don't change the input until it gets through.
