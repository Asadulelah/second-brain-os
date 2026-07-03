---
type: resolver
---

# _system/

Operational files the assistant uses. Hidden from Obsidian graph view. The user doesn't typically browse here — this is the assistant's infrastructure layer.

## What goes here

- `CLAUDE.md` — operating manual: how the assistant behaves, auto-ingest rules, file naming, conventions index
- `SOUL.md` — assistant personality and interaction style
- `MEMORY.md` — curated long-term memory: active priorities, learned rules, corrections
- `conventions/` — the 9 core page-format and filing conventions
- `index.md` — content catalog of the vault (auto-maintained)
- `log.md` — operations log (what sessions did)
- `docs/` — design specs, plans, architectural decisions
- `dashboard/` — dashboard state and config (if using a live dashboard)

## What does NOT go here

- World knowledge (facts about people, ventures, projects) → those belong in the Wiki directories
- Meeting notes or event records → `journal/`
- Source summaries → `summaries/`

## The three operational files

| File | Purpose | Who reads it |
|---|---|---|
| `SOUL.md` | Assistant's personality and tone | Assistant on session start |
| `MEMORY.md` | Curated long-term memory and rules | Assistant on session start |
| `CLAUDE.md` | Full operating manual | Assistant on session start |

**Read order on every session start:** SOUL.md → `me/{{user_name}}.md` → MEMORY.md → skim conventions index.

## Hiding from Obsidian

Add `_system` to the Obsidian excluded files list (Settings → Files & Links → Excluded files). This keeps the graph clean — the assistant's infrastructure doesn't pollute the knowledge graph.

## See also

- [[_system/conventions/brain-vs-memory]] — why _system/ exists separately from the Wiki
- [[_system/conventions/filing-rules]] — _system/ in the decision tree
