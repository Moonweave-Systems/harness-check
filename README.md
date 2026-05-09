# harness-check

A `/harness-check` slash command for Claude Code that audits your full hook and plugin configuration and writes a live snapshot to a `workspace_map.md` dashboard.

## What it checks

| Section | Description |
|---------|-------------|
| Hook event pipeline | Mermaid diagram of all registered hooks from `settings.json` |
| Plugins & marketplaces | `enabledPlugins` table with marketplace sources |
| Hook pipeline detail | Per-script logic summary + orphan script detection |
| Skills / Agents / Commands | Filesystem scan of `~/.claude/` |
| Knowledge Base | `knowledge/index.md` entry count and load status |
| **Hook health** | Syntax check + dependency binaries + `guards/` import + live run test |
| **Plugin usage frequency** | 30-day JSONL scan — flags 0-call plugins with 🟡 |
| **MCP process count** | Detects duplicate MCP processes with 🔴 |
| **Project state top 5** | Largest accumulated project states by size |
| Diagnostics | Orphan scripts, dangerous flags, stale patterns |

After updating `workspace_map.md`, it commits the change and regenerates `dashboard.html`.

## Install

```bash
cp harness-check.md ~/.claude/commands/harness-check.md
```

Then run `/harness-check` in any Claude Code session.

## Requirements

- Claude Code with a `workspace_map.md` file containing `<!-- AUTO:START -->` / `<!-- AUTO:END -->` markers
- `uv` for Python execution in hooks
- `git` repo at `~/Vaults/workspace-map/` (or adjust the path in the command)

## Usage

```
/harness-check
```

Claude will collect all settings, run the health checks, overwrite the AUTO section of `workspace_map.md`, commit, and regenerate the dashboard.
