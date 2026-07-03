---
name: brain-resolver-write
description: Generate or update the README.md MECE resolver for one or all top-level directories in this Obsidian vault. The resolver answers (a) what goes here, (b) what does NOT go here, (c) key disambiguation rules vs neighboring directories. Reads actual directory contents to ground the spec in reality. Use once to bootstrap all resolvers, then on schema changes. Trigger phrases — "brain resolver write", "generate README resolvers", "build MECE resolver for X", "/brain-resolver-write [--dir <name> | --all]".
---

# /brain-resolver-write

> Walk a directory, sample its existing pages, infer the rule for what belongs there + what doesn't, write a `README.md` MECE resolver. Either single-directory or all-at-once. Resolvers are how the assistant and user agree on filing without re-litigating every page.

## When to fire

- User invokes `/brain-resolver-write --all` (initial bootstrap — generates all resolvers)
- User invokes `/brain-resolver-write --dir people` (one directory)
- User adds a new top-level directory and wants its resolver
- Once per quarter to refresh resolvers when the vault has evolved

## Contract

This skill guarantees:
- Each generated `README.md` is grounded in the actual contents of the directory (not just the convention)
- Resolver answers 3 questions: what goes here, what does NOT, disambiguations vs neighbors
- Includes 2-4 concrete examples pulled from existing pages
- References the master `_system/RESOLVER.md` + `_system/conventions/filing-rules.md`
- Does NOT overwrite a hand-customized existing README without backup
- Preserves any frontmatter in existing README
- Visible-to-Obsidian (so the resolver appears at the top of each folder when browsed)

## Process

### Phase 1: Determine scope

```
Input: --dir <name> | --all
  --all: enumerate top-level non-hidden directories with at least 3 .md files
  --dir <name>: just that directory

Excluded from --all:
  - _system/ (has _system/RESOLVER.md instead)
  - raw/ (immutable, hidden from Obsidian)
  - workspace-export/ (hidden)
  - .claude/ (hidden)
```

### Phase 2: Sample contents

For each target directory:

1. List files (top-level + 1 level of subdirectories)
2. Pick 4-6 example pages — prioritize:
   - The most-linked pages (highest in-bound wikilink count)
   - The most-recent modifications
   - Pages spanning sub-categories within the directory
3. Read the first ~50 lines of each example for context

### Phase 3: Identify neighbors

For disambiguation rules:
- Identify the 2-3 directories most likely to be confused with this one
- Common pairs in a typical second-brain vault:
  - `people/` vs `me/` (others vs the vault owner)
  - `people/` vs `ventures/clients/` (human vs the org)
  - `ventures/` vs `systems/` (the agency/product vs the technical artifact)
  - `strategy/` vs `knowledge/` (actionable offer vs reusable framework)
  - `journal/` vs `summaries/` (dated event vs distilled source)
  - `knowledge/` vs `me/` (frameworks used vs identity)

### Phase 4: Write the resolver

Template:

```markdown
---
date: YYYY-MM-DD
type: convention
status: active
tags:
  - resolver
  - directory-spec
---

# {directory-name}/

> One-line statement of what this directory is.

## What goes here

- Clear positive definitions with concrete tests
- Examples of pages currently filed here:
  - `<example 1>` — <one-line note>
  - `<example 2>` — <one-line note>
  - `<example 3>` — <one-line note>

## What does NOT go here

- Boundary 1: <what could be confused, why it goes elsewhere>
- Boundary 2: ...
- Boundary 3: ...

## Key disambiguation rules

### vs. {neighbor 1}
- Test: <one-question test>
- Example: <ambiguous case → resolution>

### vs. {neighbor 2}
- Test: <one-question test>
- Example: <ambiguous case → resolution>

## Sub-structure (if applicable)

- `<sub-dir>/` — <one-line note>

## File-naming convention

Per `_system/_CLAUDE.md` + `_system/conventions/filing-rules.md`:
- Format: <pattern>
- Example: <concrete filename>

## Page format

Pages in this directory follow:
- `_system/conventions/compiled-truth.md` for two-layer format (if entity pages)
- `_system/conventions/source-attribution.md` for citation iron law
- <directory-specific rules if any>

## When the schema needs to evolve

If you find content that genuinely doesn't fit this directory, file in `inbox/` (create if needed) and surface to the user — the schema has a gap.

## See also

- `_system/RESOLVER.md` — master filing decision tree
- `_system/conventions/filing-rules.md` — MECE rule
- Neighbor directories: <links>
```

### Phase 5: Handle existing README

If a README.md already exists in the directory:

1. Read it
2. Check for `<!-- assistant-resolver:managed -->` marker → if present, this is assistant-managed; safe to overwrite (preserve frontmatter)
3. If NOT managed (user-customized), backup to `README.bak.md` and warn user
4. Inject `<!-- assistant-resolver:managed -->` HTML comment at end of frontmatter

### Phase 6: Write

Write `<directory>/README.md`. Verify file appears in Obsidian.

### Phase 7: Update master resolver

If `_system/RESOLVER.md` doesn't exist, create it (template below). If it exists, add/update the entry pointing to this new resolver.

### Phase 8: Report

```
✅ Generated MECE resolvers for: people/, ventures/, journal/, knowledge/, systems/, strategy/, summaries/, me/

Per-directory:
- people/README.md (N example pages indexed, 3 neighbor disambiguations)
- ventures/README.md (sub-dirs covered: primary-venture, side-projects, clients)
- ...

Master: _system/RESOLVER.md (updated with N directory pointers)

Existing READMEs backed up: 0 (none existed previously)
```

## Master RESOLVER.md template

If creating fresh:

```markdown
---
date: YYYY-MM-DD
type: convention
status: active
tags:
  - resolver
  - master-decision-tree
---

# Master RESOLVER (Filing Decision Tree)

> Walk this tree when filing any new content. First match wins.

## The rule (one line)

The PRIMARY SUBJECT of the content determines where it goes. Not the format. Not the source. Not the skill that's running.

## Decision tree

[Adapted from _system/conventions/filing-rules.md decision table]

## Per-directory resolvers

| Directory | What's there | Resolver |
|---|---|---|
| people/ | One page per human relevant to the vault owner | [[people/README]] |
| ventures/ | The owner's ventures, agencies, partnerships | [[ventures/README]] |
| ...

## When this resolver evolves

Edit triggers:
- New top-level directory created → add row + new sub-resolver
- New canonical disambiguation rule emerges from a repeated filing dispute
- Convention file changed in a way that affects routing

## See also

- _system/conventions/filing-rules.md (the source)
- _system/_CLAUDE.md (vault schema)
```

## Special handling per directory

| Directory | Special notes |
|---|---|
| `people/` | Multiple sub-clusters by relationship type (co-founders, clients, mentors, contacts) |
| `ventures/` | May have sub-directories per venture — resolver needs to address sub-structure |
| `ventures/clients/` | Sub-resolver — each client gets a page or folder |
| `journal/` | Dated entries only — meeting pages, milestone days, daily notes |
| `summaries/` | One distilled summary per ingested source |
| `knowledge/` | Reusable frameworks + research artifacts |
| `systems/` | Technical infrastructure (assistant systems, dashboards, integrations) |
| `strategy/` | Actionable offers, pricing, positioning, niche playbooks |
| `me/` | The vault owner's identity + values + goals |

## Anti-patterns

- ❌ Generating a resolver from the convention alone, ignoring actual page contents
- ❌ Overwriting a user-customized README without backup
- ❌ Forgetting to update master `_system/RESOLVER.md` after generating per-directory resolvers
- ❌ Adding resolvers for hidden directories (`raw/`, `_system/`, `.claude/`)
- ❌ Resolvers without concrete examples (abstract resolvers don't help — examples ground the rule)
- ❌ Resolvers that don't address neighbor disambiguation (this is where confusion lives)

## Tools used

- Read — sample example pages + existing README + conventions
- Glob — enumerate directory contents
- Grep — find inbound wikilink counts (popularity proxy)
- Write — produce README.md files + master RESOLVER.md
- Edit — update master resolver incrementally

## See also

- `_system/conventions/filing-rules.md` — MECE decision tree source
- `_system/_CLAUDE.md` — vault schema
- `_system/RESOLVER.md` — master resolver (this skill maintains it)
