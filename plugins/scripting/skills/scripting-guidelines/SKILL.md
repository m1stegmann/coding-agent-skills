---
name: scripting-guidelines
description: Rules for helper scripts and tooling that must run on Linux, macOS and Windows: Python through uv by default, and in .NET 10 or later solutions C# file-based apps (`dotnet run --file`) where C# fits better or the solution's own classes and libraries are needed. Use before writing, running or committing any script, one-off automation, data conversion or build/test helper, and when about to call pip, python, python3, bash or sed for such a task.
---

# Scripts and tooling

Work in this repository must run on Linux, macOS and Windows. For anything that is not the product's own code (a helper script, a conversion, a check, a generator) use the tools below, in this order of preference.

## Python through uv (the default)

- Run Python only through `uv`: `uv run script.py`. Never `pip install`, never a hand-made venv, never a bare `python` or `python3` (on Windows they may be a Store stub or missing).
- A script declares its own dependencies in a PEP 723 block at the top, and `uv run` resolves them in an isolated environment, also when called inside a project (the project's dependencies are ignored):

  ```python
  # /// script
  # requires-python = ">=3.10"
  # dependencies = ["requests"]
  # ///
  ```

  Without dependencies, still write the block: it pins the Python version and keeps the run isolated. A script without the block, run inside a folder with a `pyproject.toml`, makes `uv run` sync that project first; use `uv run --no-project script.py` then.
- In a Python project use `uv add <package>`, `uv sync` and `uv run <command>` (for example `uv run pytest`), and commit `uv.lock`.
- A shebang `#!/usr/bin/env -S uv run --script` is a Unix extra. Documentation, skills and other scripts call `uv run script.py`, which works everywhere.
- Write portable code: `pathlib` for paths, `subprocess` with a list of arguments and no `shell=True`, `encoding="utf-8"` for every text file, no assumption about line endings or the console's code page, no bash-only tools (`sed`, `grep`, `xargs`) inside a script. Take the standard library first.
- If `uv` is missing, say so and propose installing it (`winget install astral-sh.uv`, `brew install uv`, or the installer from astral.sh). Do not fall back to pip or a system Python silently. A script that ships in a plugin or must run without uv stays on the standard library and is called with `python3` (Windows: `py -3`) when `uv` is not there.

## C# file-based apps (.NET 10 or later only)

Allowed without asking when all of this holds: the repository is a .NET solution or project (`*.sln`, `*.slnx`, `*.csproj`, `global.json`) that targets `net10.0` or later, and `dotnet --version` prints 10.0.100 or later. Use one when

- the script needs classes or libraries of the solution (`#:project ../src/Lib/Lib.csproj`), or
- C# is plainly the better tool: it works on the solution's own models, parses C# or MSBuild files, or shares code that would otherwise be written twice in Python.

Otherwise stay with Python. Everything outside a .NET 10+ solution is Python.

Rules, checked with the .NET 10.0.402 SDK:

- Run it with `dotnet run --file tools/name.cs -- args`. Do not write `dotnet run name.cs`: with a `.csproj` in the current folder, that runs the project and passes `name.cs` to it as an argument.
- Put the file in a folder without a `.csproj` (`tools/` or `scripts/` at the solution root, not inside a project's folder). A `.cs` file inside a project's folder is compiled into that project, and its `#:` directives then fail that project's build with CS9298.
- Directives are `#:project <path>`, `#:package Name@version` (a version is required unless the solution uses central package management), `#:property Name=value` and `#:sdk`. Quotes are not allowed in a directive; put such values in a `Directory.Build.props`. The file picks up the nearest `Directory.Build.props` and `Directory.Packages.props`.
- `dotnet publish name.cs` targets native AOT by default; add `#:property PublishAot=false` for packages that do not support it.
- A shebang `#!/usr/bin/env dotnet` is a Unix extra. Call it with `dotnet run --file` everywhere else.
- If the solution needs an older SDK than 10, or none is installed, use Python.

## Keeping or throwing away

A script that will be used again goes into the repository (`scripts/` or `tools/`) with a short usage comment and, when it has logic worth testing, a test. A throwaway script goes into the session's scratch or temp folder and is not committed. Follow the repository's `AGENTS.md` where it is more specific.
