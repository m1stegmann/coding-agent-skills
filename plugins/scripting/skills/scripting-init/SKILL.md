---
name: scripting-init
description: Writes the scripting rules (Python through uv, C# file-based apps in .NET 10 or later solutions) into a repository's AGENTS.md, so every agent and teammate follows them, also without this plugin. Use when the user asks to set up or standardize scripting, uv or cross-platform tooling in a repository.
---

# Put the scripting rules into a repository

The rules of `scripting-guidelines` apply where this plugin is installed. A repository gets them for every agent and every machine by carrying them in `AGENTS.md`.

## Steps

1. Go to the repository root (`git rev-parse --show-toplevel`). Read `AGENTS.md` and `CLAUDE.md` if they exist.
2. Find out what the repository is: `*.sln`, `*.slnx`, `*.csproj`, `global.json` and the `TargetFramework` values, and `dotnet --version`. It is a **.NET 10+ solution** only if it targets `net10.0` or later; then use both parts of the section below, otherwise leave out the part on C#.
3. Add the section to `AGENTS.md` at the root (create the file if it is missing), in the language of that file. If a section on scripts already exists, replace it. Keep the rules in the section itself.
4. If `CLAUDE.md` exists and does not import `AGENTS.md`, add a line `@AGENTS.md`. If there is no `CLAUDE.md`, create it with exactly that line.
5. If the repository has scripts that call `python`, `python3` or `pip`, list them in your report. Change them only when the user asks.
6. Report what was written. Don't commit unless the user or the repository's workflow says so.

## Section for AGENTS.md

```markdown
## Scripts and tooling

Everything here must run on Linux, macOS and Windows.

- **Python only through uv.** `uv run script.py`; never `pip install`, a hand-made venv or a bare `python`/`python3`. A script lists its dependencies in a PEP 723 block (`# /// script` with `requires-python` and `dependencies`) and runs isolated from the project; a script without that block, run inside a project folder, needs `uv run --no-project`. In a Python project use `uv add`, `uv sync`, `uv run <command>` and commit `uv.lock`. If `uv` is missing, say so; don't fall back silently.
- **Portable code.** `pathlib` for paths, `subprocess` with an argument list and no `shell=True`, UTF-8 set explicitly, no bash-only tools (`sed`, `grep`) inside a script.
- **Kept or thrown away.** A script that is used again lives in `scripts/` or `tools/` with a usage comment (and a test if it has logic); a throwaway script stays out of the repository.
```

Only in a .NET 10+ solution, add to the section:

```markdown
- **C# file-based apps are allowed** (.NET SDK 10.0.100 or later) when a script needs classes or libraries of this solution (`#:project <path to .csproj>`) or C# is plainly the better tool; everything else stays Python. Run `dotnet run --file tools/name.cs -- args`, never `dotnet run name.cs` (with a `.csproj` in the current folder that runs the project). Keep the file in a folder without a `.csproj` (`tools/` or `scripts/` at the solution root): inside a project's folder it is compiled into that project and breaks its build. No quotes in `#:` directives; `#:package` needs a version unless the solution uses central package management; add `#:property PublishAot=false` for packages that are not AOT-compatible.
```
