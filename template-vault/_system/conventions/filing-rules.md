---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/skills/_brain-filing-rules.md (adapted to vault directory structure)
tags:
  - convention
  - filing
  - MECE
---

# Filing Rules (MECE Decision Tree)

> Every piece of content has exactly ONE primary home. The primary subject determines the directory — not the format, not the source, not the skill that's running. This is the master decision tree.

## The rule

**The PRIMARY SUBJECT of the content determines where it goes.**

Not the format. Not the source. Not the skill. Not "where it was generated."

## The decision tree

Walk this in order. First match wins.

| # | Primary subject | Directory | Examples |
|---|---|---|---|
| 1 | A specific named **person** | `people/` | `people/Alex Chen.md`, `people/Sam Kim.md` |
| 2 | A specific **venture / agency / company the user runs or partners on** | `ventures/<venture>/` | `ventures/acme/`, `ventures/nexus/AutoBiz.md`, `ventures/solo/personal-brand/`, `ventures/clients/<client>.md` |
| 3 | A record of a specific **meeting, call, or dated event** | `journal/YYYY-MM-DD <topic>.md` | `journal/2026-05-11 CRM Walkthrough.md`, `journal/2026-05-17 Demo Site Launch.md` |
| 4 | A **technical system or architecture** the user has built or is building (not the venture itself, the technical artifact) | `systems/` | `systems/assistant/`, `systems/Directive Core.md` |
| 5 | A **strategy / offer / pricing / positioning** artifact | `strategy/` | `strategy/Target Market ICP.md`, `strategy/niche-offer-books/`, `strategy/Campaign Strategy.md` |
| 6 | A **distilled mental model, framework, or research artifact** | `knowledge/` | `knowledge/GBrain.md`, `knowledge/Content Creation Skill.md` |
| 7 | A **summary of one ingested source** (article, transcript, doc) | `summaries/` | `summaries/<source>.md` |
| 8 | **Identity content about the user themselves** | `me/` | `me/{{user_name}}.md`, `me/Goals and Vision.md`, `me/Values and Rules.md` |
| 9 | **Raw ingested source** — never modified | `raw/` | `raw/imports/`, `raw/transcripts/`, `raw/articles/` |
| 10 | **Operational / system files the assistant uses** | `_system/` | `_system/MEMORY.md`, `_system/SOUL.md`, `_system/conventions/` |

## Key disambiguation rules

### Person vs. Venture
- About them **as a human** (relationship, beliefs, trajectory)? → `people/`
- About **the organization they run / participate in**? → `ventures/<venture>/`
- Both? → Both pages exist, cross-link aggressively. `people/Jordan Lee.md` AND `ventures/nexus/AutoBiz.md` both exist; they reference each other.

### Venture vs. System
- A **product / agency / business**? → `ventures/`
- The **technical architecture under the product**? → `systems/`
- Example: `ventures/nexus/AutoBiz.md` (the agency, its offer, its positioning) vs `systems/assistant/` (the user's personal AI infrastructure)

### Strategy vs. Knowledge
- **The user's actionable offer/positioning/pricing**? → `strategy/`
- **Reusable mental model or research** the user might apply elsewhere? → `knowledge/`
- Test: is this a thing the user is selling/using directly (`strategy/`) vs a framework they're distilling (`knowledge/`)?

### Journal vs. Summary
- **Record of a dated event** (meeting, call, milestone, daily note)? → `journal/`
- **Distilled content from a source** (article, transcript, paper)? → `summaries/`

### Knowledge vs. Strategy vs. Me
- **Mental model from elsewhere or research** the user references? → `knowledge/`
- **Offer / positioning / pricing** the user uses? → `strategy/`
- **The user's own identity, values, goals**? → `me/`

### Sources/Raw vs. anywhere
- `raw/` is **immutable, never modified**. Bulk transcript dumps, articles clipped, raw API responses
- `summaries/` is **one distilled summary per source**, sourced from `raw/`
- If content has a clear primary subject (a person, venture, concept), it does NOT live in raw/ — file under the appropriate subject directory and cross-reference raw as source

## Sub-directories

Some directories have a sub-structure. Apply the same primary-subject rule within them:

### `ventures/`
- `ventures/acme/` — primary venture + sub-products
- `ventures/nexus/` — partner agency or collaboration
- `ventures/solo/` — user's solo/personal work
- `ventures/partners/` — outreach partnerships
- `ventures/clients/` — per-client engagement folders

### `systems/`
- `systems/assistant/` — personal AI infrastructure
- Top-level systems get their own page (`systems/Directive Core.md`, `systems/ProjectCRM.md`)

### `strategy/`
- `strategy/niche-offer-books/` — per-niche offer playbooks
- Top-level strategy artifacts as single .md files

## What goes in `_system/` (NOT the Wiki)

Files the assistant uses operationally but the user doesn't browse:
- `_system/MEMORY.md` — assistant's curated long-term memory
- `_system/SOUL.md` — assistant's personality
- `CLAUDE.md` — vault schema and operating manual
- `_system/conventions/` — these convention files
- `_system/RESOLVER.md` — master filing decision tree
- `_system/index.md` — content catalog
- `_system/log.md` — operations log
- `_system/docs/` — design specs and plans

**`_system/` is hidden from Obsidian.** Decisions about the assistant's infrastructure live here, not in the Wiki.

## What goes in `raw/` (NOT the Wiki)

Immutable source documents:
- `raw/imports/` — migrated files from prior tools, untouched
- `raw/articles/` — Web Clipper output
- `raw/transcripts/` — meeting/call transcript outputs
- `raw/pdfs/` — PDF documents
- `raw/assets/` — Images, screenshots

**`raw/` is hidden from Obsidian.** Never modify these.

## What goes in `inbox/` (if created later)

If we ever need a place for unsorted captures that don't yet fit a category, use `inbox/`. The existence of an `inbox/` entry is itself a signal the schema needs to evolve. (Currently not in the vault — create only if needed.)

## When to evolve the schema

If you find content that genuinely doesn't fit any directory:
1. Try harder — the primary subject usually does fit
2. If truly novel category, **propose** a new directory in chat with the user
3. Don't unilaterally create new top-level directories — keep the root level clean

## Sanctioned exception: synthesized one-of-one output

The "file by primary subject" rule is for raw ingest. Synthesized output that is one-of-one to a single source AND a specific reader may use format-prefixed paths under `summaries/` or `knowledge/` with a descriptive suffix.

## Cross-references are mandatory

Every page mentions multiple entities. **Wikilink them all.** This is the back-link convention's prerequisite. Specifically:
- A `journal/` entry mentioning `Alex` and `Acme` and a system → 3 wikilinks
- A `people/` page mentioning ventures → wikilinks to each
- A `ventures/` page mentioning team members → wikilinks to each

The graph is the intelligence.

## Verification

A file complies if:
1. ✅ Its directory matches its primary subject per the decision tree above
2. ✅ Cross-references are wikilinks to other vault entities
3. ✅ Back-links exist on the entity pages it mentions (per [[back-linking]])
4. ✅ It doesn't duplicate a page in another directory (per [[aliases]])

## Anti-patterns

- ❌ Filing a meeting summary in `summaries/` instead of `journal/` (journal/ is for dated events)
- ❌ Filing analysis of a venture in `summaries/` instead of the relevant `ventures/` page
- ❌ Putting "research about Jordan" in `knowledge/` instead of `people/Jordan Lee.md`
- ❌ Creating top-level directories without consulting the user
- ❌ Filing a stable strategy/offer in `journal/` (journal is dated events, not durable artifacts)

## See also

- [[compiled-truth]] — how pages within these directories are structured
- [[back-linking]] — cross-references between directories
- [[aliases]] — dedup within directories
- `_system/RESOLVER.md` — master decision tree
- Per-directory `README.md` files
