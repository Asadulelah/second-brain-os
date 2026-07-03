---
name: brain-back-link-sweep
description: Scan recent journal/meeting/entity pages in this Obsidian vault for entity wikilinks that lack corresponding back-link timeline entries on the target entity pages. Adds the missing back-links. Enforces the Iron Law of Back-Linking from _system/conventions/back-linking.md. Use as part of /brain-dream maintenance cycle, after a /brain-compile refactor, or weekly cleanup. Trigger phrases — "brain back-link sweep", "find missing back-links", "enforce back-link iron law", "/brain-back-link-sweep [--since DATE]".
---

# /brain-back-link-sweep

> Walk forward through recent source pages. For every entity wikilink found, verify the entity's page has a corresponding back-link timeline entry. Add the missing ones. Enforces bidirectional graph consistency.

## When to fire

- User invokes `/brain-back-link-sweep` (manual)
- User says "find missing back-links" / "do a back-link sweep"
- After `/brain-compile` finishes refactoring a page — sweep immediately for that page's references
- During `/brain-dream` (Phase 2: backlinks)
- Weekly via `/schedule "every Sunday 9am" /brain-dream --weekly`

**Default scope**: pages modified in the last 14 days under `journal/`, `people/`, `ventures/`. Override with `--since YYYY-MM-DD`.

## Contract

This skill guarantees:
- Every entity wikilink in source pages gets verified against the entity's timeline
- Missing back-links get added with proper format: `- **YYYY-MM-DD** | Referenced in [[Source Page]] — brief context  [Source: ...]`
- No duplicate back-links created (idempotent)
- Source page timestamps preserved (only entity pages are modified)
- Per-entity additions reported to user
- Stops at first irreconcilable case (don't ploughing through bad data)

## Process

### Phase 1: Gather source pages

```
Default: all pages in journal/, people/, ventures/ modified in last 14 days
Override: --since YYYY-MM-DD limits scope
Override: --page <path> sweeps one specific source page
```

### Phase 2: Extract entity references

For each source page:
1. Parse all `[[Wikilinks]]` (including aliased `[[Page|alias]]` form)
2. Resolve each wikilink to a target file path
3. Skip if target doesn't exist (those are creation signals, not back-link candidates)
4. Skip self-references (page links to itself)
5. Skip references inside code blocks or fenced quotes (these are source material, not brain claims)

### Phase 3: Check each entity page

For each target entity:
1. Read the entity's page
2. Locate the `## Timeline` section (the part below `---` if compiled-truth format, or any Timeline section if legacy)
3. Search for an existing back-link to the source page (by source page slug or title)
4. **If present:** skip
5. **If missing:** prepare a new timeline entry

### Phase 4: Generate back-link entries

Format:
```
- **YYYY-MM-DD** | Referenced in [[Source Page Title]] — <auto-extracted context>  [Source: derived from source page modification]
```

**Context extraction:**
- For meetings (`journal/YYYY-MM-DD <topic>.md`): extract from the meeting title + 1-line summary if available
- For person pages (`people/<Name>.md`): extract from the closest paragraph mentioning the entity
- For venture pages: extract from the section title or surrounding sentence

**Source attribution for the back-link itself:**
- Use the source page's metadata: `[Source: <source page path>, modified <YYYY-MM-DD>]`
- This is acceptable because the source page is the authoritative trace

### Phase 5: Apply edits

For each entity page with new back-links:
1. Read the page
2. Find the Timeline section (or create one if compiled-truth format and missing)
3. **Insert newest-first** — new entries go at the top of Timeline (most recent date)
4. Preserve existing entries unchanged
5. Write the updated page

### Phase 6: Report

Output to user:

```
Back-link sweep — scope: last 14 days

Source pages scanned: N
Entity references found: N
Existing back-links: N (skipped)
Missing back-links: N (added)

Modified entity pages:
- people/Alex Chen.md (+3 back-links)
- people/Jordan.md (+1 back-link)
- ventures/venture-alpha/Product.md (+2 back-links)

Unresolved:
- 2 wikilinks point to pages that don't exist:
  - [[Network Alpha]] (mentioned in journal/2026-05-17, no page)
  - [[Morgan last name unknown]] (mentioned in personal notes)
  Suggest creating these or fixing the link.
```

## Edge cases

| Case | Handling |
|---|---|
| Wikilink inside a code block | Skip (source material, not a brain claim) |
| Wikilink in a quoted transcript | Skip (transcript fragment, not authoritative) |
| Aliased wikilink `[[Full Name\|alias]]` | Resolve to Full Name's page, use alias as context |
| Entity page is in legacy format (no `---` separator) | Add Timeline section if missing; insert at end of file |
| Entity page is a stub (very short) | Add back-link anyway — stubs need timeline entries to grow |
| Self-reference (page links to itself) | Skip |
| Source page is in `summaries/` | Skip the wikilinks — summaries link to entities for reference, not as evidence |
| Source page is itself a Dream Cycle Report | Skip — derivative output, not authoritative |
| Multiple wikilinks to same entity in same source page | Only one back-link entry (newest mention wins) |

## Reference inputs

- `_system/conventions/back-linking.md` — the Iron Law spec
- `_system/conventions/source-attribution.md` — citation format for the back-link entry
- `_system/conventions/compiled-truth.md` — Timeline section structure (newest-first, append-only)

## Output format

```
✅ Back-link sweep complete — scope: --since YYYY-MM-DD to YYYY-MM-DD

Scanned: 28 source pages
Verified: 142 entity references
Added: 14 back-links across 9 entity pages

Modified:
- people/Alex Chen.md  +3
- people/Jordan.md     +1
- ventures/venture-alpha/Product.md  +2
- ...

Outstanding:
- 2 wikilinks to non-existent pages (suggest creating or fixing)
```

## Anti-patterns

- ❌ Adding back-links to pages without verifying the wikilink actually exists (broken links propagated)
- ❌ Auto-adding back-links from source pages that are themselves derivative (summaries, reports)
- ❌ Editing source pages — only entity pages get modified, sources are read-only
- ❌ Duplicate back-link entries — must check existing Timeline before inserting
- ❌ Inserting at end of Timeline — Timeline is newest-first, new entries go at top
- ❌ Generating back-links inside code blocks or quoted text — those aren't real mentions

## Tools used

- Read — load source pages + entity pages + conventions
- Grep — search for existing back-links in entity pages
- Glob — enumerate source pages in scope
- Edit — apply back-link insertions to entity pages
- AskUserQuestion — for unresolved cases (missing target pages, ambiguous aliases)

## See also

- [[_system/conventions/back-linking]] — Iron Law spec
- [[_system/conventions/compiled-truth]] — Timeline format
- `/brain-compile` — fires this for the refactored page automatically
- `/brain-dream` — invokes this as Phase 2
