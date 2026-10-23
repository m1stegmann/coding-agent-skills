# scripting

Cross-platform rules for the helper scripts and tooling that coding agents write and run: **Python through uv** by default, and in **.NET 10 or later** solutions **C# file-based apps** (`dotnet run --file`) where C# fits better or the solution's own classes and libraries are needed.

| Part | What it does |
|---|---|
| `skills/scripting-guidelines` | The rules an agent loads before it writes or runs a script: `uv run`, PEP 723 blocks, portable code, when and how to use a C# file-based app, what to keep in the repository. |
| `skills/scripting-init` | Writes the same rules into the repository's `AGENTS.md` (the C# part only for a .NET 10+ solution), so agents without this plugin and teammates follow them too. |

The plugin has no script of its own and no agent: agents of a repository get the rules through its `AGENTS.md`, which `scripting-init` writes.

## Checked

| | Result |
|---|---|
| uv 0.13.5 | A script with a PEP 723 block, run with `uv run` inside a folder with a `pyproject.toml`, ignores the project: no `.venv`, no lock file. |
| .NET SDK 10.0.402 | `dotnet run --file tools/hello.cs` with `#:project ../Lib/Lib.csproj` runs. A `.cs` file inside a project's folder fails that project's build with CS9298. `dotnet run ../tools/hello.cs` with a `.csproj` in the current folder runs the project, not the file. |
| Claude Code, Grok, Copilot CLI | Not tested yet with this plugin. |

## License

[MIT](../../LICENSE)
