# /harness-check

Collect and analyze the full Claude Code harness configuration, then overwrite the `<!-- AUTO:START -->` … `<!-- AUTO:END -->` section of `~/Vaults/workspace-map/workspace_map.md` with a live snapshot.

## Sources to read (all, without exception)

1. `~/.claude/settings.json` — model, language, effortLevel, advisorModel, env, permissions (allow/deny), enabledPlugins, extraKnownMarketplaces, all other keys
2. `~/.claude/settings.local.json` — local overrides
3. `~/.claude/hooks/` — read each script in full (include logic summary)
4. `~/.claude/skills/` — full list of installed skills
5. `~/.claude/agents/*.md` — frontmatter for each agent (name, description, model, color)
6. `~/.claude/commands/*.md` — first-line description of each command
7. `~/.claude/knowledge/index.md` — KB index entry count and status
8. `~/.claude/CLAUDE.md` — full global guidelines
9. `~/CLAUDE.md` — full root project guidelines
10. `hooks` field in `settings.json` — per-event matcher + command

## Health checks to run (alongside collection)

### A. Hook script health

```bash
# 1. Syntax check
for f in ~/.claude/hooks/*.py; do
    uv run python3 -m py_compile "$f" 2>&1 && echo "✅ $(basename $f)" || echo "❌ $(basename $f)"
done

# 2. Dependency binaries
which agent-notify mempalace ruff 2>/dev/null

# 3. guards/ package import
uv run python3 -c "import sys; sys.path.insert(0,'$HOME/.claude/hooks'); from guards import bash,files,mcp_github,mcp_playwright,web; print('✅ guards/')"

# 4. Live test of context_inject.py
echo '{}' | uv run python3 ~/.claude/hooks/context_inject.py
```

### B. Plugin usage frequency (JSONL, last 30 days)

```python
import json, os, glob, re
from datetime import datetime, timedelta
from collections import Counter

cutoff = datetime.now() - timedelta(days=30)
skill_calls = Counter()
pattern = re.compile(r'"skill"\s*:\s*"([^"]+)"')

for jsonl in glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True):
    if datetime.fromtimestamp(os.path.getmtime(jsonl)) < cutoff:
        continue
    try:
        content = open(jsonl).read()
        for m in pattern.finditer(content):
            skill_calls[m.group(1)] += 1
    except:
        pass

# Output top 15 + cross-reference with enabled plugins to flag 0-call entries
```

### C. MCP process duplicate detection

```bash
ps aux | grep -E "(playwright|firecrawl|context7|github|mempalace|brave|duckdb)" \
  | grep -v grep \
  | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}' \
  | grep -oE '(playwright|firecrawl|context7|github|mempalace|brave|duckdb)' \
  | sort | uniq -c | sort -rn
```

Flag any count > 1 as a duplicate warning.

### D. Project state top 5

```python
# Scan ~/.claude/projects/ — per directory: total JSONL size + session count + last active date
# Output sorted by size descending, top 5
```

## AUTO section content

Write the following markdown structure. Include a refresh timestamp.

```
## 🔀 Hook Event Pipeline

(mermaid flowchart LR — one node per event)
- Derive event order from the hooks field in settings.json
- Each node: event name + script name + [matcher]
- Colors: SessionStart=#4ade80, UserPromptSubmit=#60a5fa, PreToolUse=#f97316,
  PostToolUse=#a78bfa, Stop=#f43f5e, PreCompact=#fbbf24, SessionEnd=#94a3b8
- Apply style with fill/stroke/color (dark-theme fills)

## 🔬 Research Workflow Pipeline

(mermaid flowchart LR — Athena research pipeline)
- /ingest → /solve → /visualize → /draft → /ppt
- Each node: slash-command name + one-line description
- Colors: ingest=#4ade80, solve=#60a5fa, visualize=#a78bfa, draft=#fbbf24, ppt=#f97316

## Harness Snapshot
_Last updated: YYYY-MM-DD — /harness-check_

### ⚙️ Core Settings
- model / advisorModel / effortLevel / language / defaultMode
- env variables
- permissions allow list (one line)
- permissions deny list (one line)
- settings.local.json overrides (if absent: "none ✅")
- cleanupPeriodDays, other boolean flags

### 🔌 Plugins & Marketplaces
- enabledPlugins table (plugin | marketplace | status | 30-day calls)
- extraKnownMarketplaces one line

### 🪝 Hook Pipeline
event | matcher | script | logic summary
(read each script and summarize in 1–2 lines)
List orphan scripts (present in hooks/ but not wired in settings.json)

### 📦 Skills
Full list in one line (note gstack and other bundles in parentheses)

### 🤖 Agents
name | model | role summary

### 🌐 Commands
name | description

### 📚 Knowledge Base
index.md entry count, daily log path, compile status, load mechanism

### 📋 CLAUDE.md Layers
- global: section list
- project: section list

### 🏥 Hook Health
(Results of check A)
script | syntax | notes
Dependencies: agent-notify / mempalace / ruff — installed?
guards/ package — import successful?

### 📊 Plugin Usage (30 days)
(Results of check B)
plugin | 30-day calls — flag 0-call entries with 🟡

### 🔄 MCP Process Count
(Results of check C)
MCP | process count — flag count > 1 with 🔴

### 💾 Project State Top 5
(Results of check D)
project | last active | sessions | size

### 🔍 Diagnostics
Analyze collected data and output as a table:
item | type | detail

Types:
- 🔴 Error: missing matcher, broken script path, invalid event name
- 🟠 Duplicate: overlapping skills/agents/commands, duplicate MCP processes
- 🟡 Warning: potential risk, design improvement opportunity, 0-call plugins
- 🟢 Info: intentional design with potential for misunderstanding
- ✅ OK: note this if no issues found

Diagnostic criteria:
- Orphan scripts (in hooks/ but not registered in settings.json)
- Conflicts between settings layers
- Hook pipeline ordering / missing / duplicate behavior
- Unused, duplicate, or no-op items (including 0-call plugins over 30 days)
- Dangerous flags (skipDangerousModePermissionPrompt, etc.)
- Duplicate MCP processes
- Outdated patterns relative to current Claude Code features
- Hook script syntax or runtime errors
```

## Notes

- Only overwrite the AUTO section (`<!-- AUTO:START -->` … `<!-- AUTO:END -->`). Do not touch anything outside.
- If the markers are missing, append them with the section content at the end of the file.
- All diagnostics must be inside the AUTO section. Do not create separate sections.

## Commit after updating workspace_map.md

Run in order after the file is written:

```bash
# 1. Show diff stats before committing
git -C ~/Vaults/workspace-map diff --stat HEAD -- workspace_map.md

# 2. Commit
git -C ~/Vaults/workspace-map add workspace_map.md && git -C ~/Vaults/workspace-map commit -m "harness-check: $(date +%Y-%m-%d) auto-update"
```

Show the `--stat` output to the user. If there are no changes, exit without committing.

## Regenerate HTML dashboard

After updating `workspace_map.md`, regenerate the dashboard:

```bash
uv run python3 ~/Vaults/workspace-map/gen_dashboard.py
```

Do not pass `--open` (no need to launch the browser automatically).
