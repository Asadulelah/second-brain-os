---
name: brain-graph-extract
description: Scan all wiki pages in this Obsidian vault for entity mentions and role/relationship language. Extract typed edges (works_at, founded, attended, advises, invested_in, mentions, ships_with) into a structured JSON file at _system/graph.json. Adds a queryable typed-graph layer on top of plain Obsidian wikilinks — answers relational questions wikilinks alone can't (who works at Acme, who's mentioned alongside whom, etc.). Use as part of /brain-dream --full or on-demand for dashboard rendering. Trigger phrases — "brain graph extract", "build typed graph", "extract relationships", "/brain-graph-extract".
---

# /brain-graph-extract

> Walk every wiki page. Extract typed entity relationships into `_system/graph.json`. Read-only on the vault — writes only to `_system/graph.json`. The dashboard can read this for a graph view; future skills can query it for relational answers.

## When to fire

- User invokes `/brain-graph-extract`
- During `/brain-dream --full` (Phase 7.5)
- After a major batch refactor (e.g., converting many people pages to compiled-truth)
- Weekly via cron if desired (cheap operation)
- Before generating a dashboard relationship view

## Contract

- Reads vault pages, writes ONLY to `_system/graph.json`
- Output is idempotent — re-running on unchanged input produces same JSON (sorted, deterministic)
- Typed edges follow gbrain's edge types: `works_at`, `founded`, `attended`, `advises`, `invested_in`, `ships_with`, `mentions` (fallback)
- Zero LLM calls — pure regex + heuristic extraction (mirrors gbrain's auto-link post-hook)
- Edges include source page + line number for traceability
- No edges to non-existent target pages (those become "dangling refs" reported separately)

## Edge types

| Edge | Trigger language | Example |
|---|---|---|
| `works_at` | "X is CEO of Y", "X (CTO @ Y)", "X at Y", roles like CEO/CTO/PM/Engineer near a venture name | `Alex works_at AcmeCorp` |
| `founded` | "X founded Y", "X co-founded Y", "founder of Y" | `Alex founded AcmeCorp` |
| `attended` | Meeting pages list person in attendees; `## Attendees` section | `Alex attended 2026-05-11 Product Walkthrough` |
| `advises` | "X advises Y", "X as advisor to Y", "X mentor for Y" | `Jordan advises VentureAlpha` |
| `invested_in` | "X invested in Y", "X is investor in Y", round-related language | `Sam invested_in StartupBeta` |
| `ships_with` | "X and Y both built", "co-built", collaborated on a system or venture | `Alex ships_with Jordan (Acme product)` |
| `mentions` | Wikilink with no role/relationship language detected nearby (fallback edge) | Most generic refs |

## Process

### Phase 1: Enumerate vault pages

```
Glob: {{VAULT_ROOT}}/**/*.md
Exclude:
  - _system/**
  - raw/**
  - .claude/**
  - workspace-export/**
  - **/*.bak.md
  - **/README.md (these are resolvers, not entity pages)
```

Set `{{VAULT_ROOT}}` to the root of your Obsidian vault. In the hook
context this resolves via `CONTEXT_DOCS_ROOT` or the project `.claude/`
parent directory.

### Phase 2: Build entity registry

For each page in `people/`, `ventures/**/`, `systems/`:
1. Slug = filename without .md
2. Canonical title = first H1
3. Aliases = frontmatter `aliases:` field
4. Record (slug, type, canonical-title, aliases)

This is the lookup table for resolving `[[name]]` → entity.

### Phase 3: Extract edges per page

For each source page:

1. Strip code blocks and fenced quotes (those aren't claims)
2. Find all wikilinks `[[Target]]` or `[[Target|Display]]`
3. For each wikilink:
   - Resolve to entity in registry (or alias)
   - Skip if target doesn't exist (record in `dangling_refs`)
   - Look at surrounding context (±100 chars) for role/relationship language
   - Apply edge-type heuristics in priority order:
     - `founded` checked first (most specific)
     - `invested_in` next
     - `advises` next
     - `works_at` next
     - `attended` (only if source is a meeting page in `journal/`)
     - `ships_with` next
     - Fallback: `mentions`
4. Record edge: `{source: <slug>, target: <slug>, type: <edge>, line: <N>, context: "<excerpt>"}`

### Phase 4: Within-page dedup

If a page mentions the same entity multiple times, collapse to ONE edge of the highest-priority detected type. Don't emit 3 `mentions` edges for one source-target pair.

### Phase 5: Write JSON

```json
{
  "generated_at": "2026-05-18T18:30:00Z",
  "vault_path": "{{VAULT_ROOT}}",
  "stats": {
    "pages_scanned": 348,
    "entities": 87,
    "edges": 412,
    "by_type": {
      "works_at": 18,
      "founded": 6,
      "attended": 142,
      "advises": 3,
      "invested_in": 0,
      "ships_with": 24,
      "mentions": 219
    },
    "dangling_refs": 14
  },
  "entities": [
    {"slug": "alex-chen", "type": "person", "canonical": "Alex Chen", "aliases": ["Alex", "A. Chen"]}
  ],
  "edges": [
    {"source": "alex-chen", "target": "acme-corp", "type": "founded", "page": "people/Alex Chen.md", "line": 8, "context": "..."}
  ],
  "dangling_refs": [
    {"source_page": "journal/2026-05-17 Product Demo.md", "target": "Network Alpha", "line": 42}
  ]
}
```

Write atomically: temp file → rename, so concurrent readers always see a valid JSON.

### Phase 6: Report

```
✅ /brain-graph-extract complete

Pages scanned: 348
Entities indexed: 87 (people: 28, ventures: 12, systems: 8, journal-as-event: 39)
Edges extracted: 412
  - works_at: 18
  - founded: 6
  - attended: 142
  - advises: 3
  - ships_with: 24
  - mentions: 219

Dangling refs (wikilinks to non-existent pages): 14
  - See _system/graph.json → dangling_refs[] for full list

Output: _system/graph.json (47 KB)

Sample relational queries this enables:
  - "Who works at Acme Corp?" → grep edges where target=acme-corp AND type=works_at
  - "What has Alex attended?" → grep edges where source=alex-chen AND type=attended
  - "Who's mentioned alongside the user in recent journal entries?" → grep edges where source like "journal/2026-05-*"
```

## Edge heuristic details

### `founded` regex hints
- `[Xx] founded` near `[[Target]]`
- `[Xx] co-?founded` near `[[Target]]`
- `founder of [[Target]]`
- `created [[Target]]` (for systems, not ventures)

### `works_at` regex hints
- Role words: `CEO|CTO|COO|CMO|founder|partner|engineer|head of|VP|director|manager` near `[[Target]]`
- `[Xx] at [[Target]]`
- `[Xx] @ [[Target]]`
- `[Xx]'s role at [[Target]]`

### `attended` regex hints
- Source page is in `journal/` AND filename matches `YYYY-MM-DD.*\.md`
- Page has `## Attendees` section listing the entity
- "Met with [[X]]" or "Call with [[X]]" in a journal entry

### `advises` regex hints
- `advises|advisor|mentor|coaching` near `[[Target]]`

### `ships_with` regex hints
- `co-built|both built|collaborated|worked together on` between two `[[]]` entities
- Person pages listing other people in "Team" sections

## Anti-patterns

- ❌ Calling an LLM for edge typing — heuristics only (gbrain learned this; LLM calls don't scale)
- ❌ Including wikilinks from `summaries/` or `raw/` as primary edges (those are source material, not entity assertions)
- ❌ Generating self-edges (entity linking to itself)
- ❌ Emitting `mentions` when a more specific edge could have been derived (apply priority order)
- ❌ Overwriting `_system/graph.json` non-atomically (use temp-file + rename)
- ❌ Writing to vault content from this skill (read-only on the wiki)

## Reference inputs

- `_system/external/gbrain/skills/maintain/SKILL.md` — gbrain's auto-link post-hook for the heuristic reference
- `_system/conventions/aliases.md` — alias resolution
- `_system/conventions/back-linking.md` — same edge concept, different output

## Output format

```
✅ Graph extracted: 87 entities, 412 edges, 14 dangling refs.
Output: _system/graph.json (47 KB)
Dashboard can now render relationship view.
```

## Tools used

- Read — load entity pages + frontmatter + content
- Glob — enumerate vault pages
- Grep — search for role language patterns
- Write — atomic write to `_system/graph.json`

## See also

- `_system/conventions/back-linking.md` — text-level back-link Iron Law (this skill is the structural counterpart)
- `_system/conventions/aliases.md` — alias resolution
- `/brain-dream --full` invokes this in Phase 7.5
- gbrain's `extract links` command (the model this is ported from)
