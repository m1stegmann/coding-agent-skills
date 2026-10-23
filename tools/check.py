#!/usr/bin/env python3
"""Checks the library against the rules in README.md ("Rules for a plugin"). Standard library only.

    python3 tools/check.py            # exit 0 and "ok: ..." or exit 1 and one line per problem
    python3 tools/check.py --root DIR # check another checkout (used by the tests)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
# Paths of one machine: a home directory, a Linux or macOS user folder, a Windows drive.
MACHINE_PATH = re.compile(r"(?<![\w$])~/|/home/[a-z]|/Users/[A-Za-z]|\b[A-Za-z]:\\\\?[A-Za-z]")


def frontmatter(path: pathlib.Path) -> dict[str, str] | None:
    """The `key: value` lines between the leading `---` lines, or None without frontmatter."""
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    if not match:
        return None
    return {k.strip(): v.strip() for k, v in (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)}


def check(root: pathlib.Path) -> tuple[list[str], int]:
    """Problems found, and the number of plugins checked."""
    problems: list[str] = []
    marketplace = root / ".claude-plugin" / "marketplace.json"
    try:
        catalog = json.loads(marketplace.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"{marketplace.relative_to(root)}: {error}"], 0

    if not NAME.match(str(catalog.get("name", ""))):
        problems.append("marketplace.json: name must be lowercase words joined by hyphens")
    if not (catalog.get("owner") or {}).get("name"):
        problems.append("marketplace.json: owner.name is missing")

    listed: set[str] = set()
    skills: dict[str, str] = {}
    agents: dict[str, str] = {}
    for entry in catalog.get("plugins", []):
        name = str(entry.get("name", ""))
        listed.add(name)
        where = f"plugin {name or '?'}"
        if not NAME.match(name):
            problems.append(f"{where}: the marketplace name must be lowercase words joined by hyphens")
        if entry.get("source") != f"./plugins/{name}":
            problems.append(f"{where}: source must be ./plugins/{name}")
        plugin = root / "plugins" / name
        if not plugin.is_dir():
            problems.append(f"{where}: plugins/{name} does not exist")
            continue
        problems += check_plugin(root, plugin, skills, agents)

    for folder in sorted(p for p in (root / "plugins").iterdir() if p.is_dir()) if (root / "plugins").is_dir() else []:
        if folder.name not in listed:
            problems.append(f"plugins/{folder.name}: not listed in .claude-plugin/marketplace.json")
    return problems, len(listed)


def check_plugin(root: pathlib.Path, plugin: pathlib.Path, skills: dict[str, str], agents: dict[str, str]) -> list[str]:
    problems: list[str] = []
    rel = plugin.relative_to(root).as_posix()
    manifest_path = plugin / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"{rel}: .claude-plugin/plugin.json: {error}"]
    if manifest.get("name") != plugin.name:
        problems.append(f"{rel}: plugin.json name must be {plugin.name!r}")
    for field in ("version", "description"):
        if not manifest.get(field):
            problems.append(f"{rel}: plugin.json has no {field}")
    if (plugin / "bin").exists():
        problems.append(f"{rel}: a top-level bin/ makes Cowork and the chat refuse the plugin; use scripts/")
    if not (plugin / "README.md").is_file():
        problems.append(f"{rel}: README.md is missing")

    skill_dirs = sorted(p for p in (plugin / "skills").iterdir() if p.is_dir()) if (plugin / "skills").is_dir() else []
    if not skill_dirs:
        problems.append(f"{rel}: no skills/<name>/SKILL.md")
    for folder in skill_dirs:
        problems += check_component(root, folder / "SKILL.md", folder.name, skills, "skill")
    for agent in sorted((plugin / "agents").glob("*.md")) if (plugin / "agents").is_dir() else []:
        problems += check_component(root, agent, agent.stem, agents, "agent")
    return problems


def check_component(root: pathlib.Path, path: pathlib.Path, expected: str, seen: dict[str, str], kind: str) -> list[str]:
    rel = path.relative_to(root).as_posix()
    if not path.is_file():
        return [f"{rel}: missing"]
    meta = frontmatter(path)
    if meta is None:
        return [f"{rel}: no frontmatter"]
    problems = []
    name = meta.get("name", "")
    if name != expected:
        problems.append(f"{rel}: name must be {expected!r}, the {kind}'s {'folder' if kind == 'skill' else 'file'} name")
    if not NAME.match(name) or len(name) > MAX_NAME:
        problems.append(f"{rel}: name must be lowercase words joined by hyphens, at most {MAX_NAME} characters")
    description = meta.get("description", "")
    if not description or len(description) > MAX_DESCRIPTION:
        problems.append(f"{rel}: description must be 1 to {MAX_DESCRIPTION} characters")
    if name in seen:
        problems.append(f"{rel}: {kind} name {name!r} is also used by {seen[name]}; names are unique across the library")
    seen.setdefault(name, rel)
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if MACHINE_PATH.search(line):
            problems.append(f"{rel}:{number}: a path of one machine; use ${{CLAUDE_PLUGIN_ROOT}} or a path relative to the plugin")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    problems, plugins = check(args.root)
    for problem in problems:
        print(problem)
    if not problems:
        print(f"ok: {plugins} plugin(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
