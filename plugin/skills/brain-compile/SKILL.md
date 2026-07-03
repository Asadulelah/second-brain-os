---
name: brain-compile
description: Refactor a legacy entity page in this Obsidian vault into the compiled-truth + timeline two-layer format. Reads existing prose, identifies synthesis vs. evidence, restructures with `---` separator, asks for missing source citations, and produces a page that follows _system/conventions/. Use when an existing people/, ventures/, or project page is in free-form prose and needs to be brought into convention. Trigger phrases — "brain compile this page", "refactor this page to compiled-truth", "convert to two-layer format", "/brain-compile <page>".
---

# /brain-compile

> Refactor an existing wiki page into the compiled-truth + timeline two-layer format. Single-page operation. Asks for confirmation on ambiguous source attributions instead of guessing.

## When to fire

- User says "brain compile <page>" or "/brain-compile <page>"
- User asks to "refactor <page> to the new format" or "convert <page> to compiled-truth + timeline"
- User says "apply the new convention to <page>"
- During `/brain-dream --full` cycle as part of opportunistic refactor of top-stale pages
- When the user explicitly batches: "compile all people pages" → fire once per page, sequentially

**Do NOT fire on:**
- Daily notes (`journal/YYYY-MM-DD.md`) — these are timeline entries, not entities
- Meeting pages (`journal/YYYY-MM-DD <topic>.md`) — these are single-event records
- Source summaries (`summaries/`) — distilled content, not entities
- Pages already in compiled-truth + timeline format (check for `---` separator + Timeline section first)

## Contract

This skill guarantees:
- Original page preserved at `<page>.bak.md` before any modification
- Result follows all 9 conventions in `_system/conventions/`
- Frontmatter augmented with `aliases:` (for person pages) and `status:` (active/dormant/archived)
- Every factual claim has a `[Source: ...]` citation per [[_system/conventions/source-attribution]]
- Belief/style/assessment claims labeled per [[_system/conventions/source-types]]
- `---` separator placed between synthesis and timeline
- Timeline newest-first, append-only, every entry sourced
- Cross-references preserved (no broken wikilinks)
- Reports any unsourced claims that need user input before finalizing

## Process

### Phase 1: Read + classify (no writes yet)

1. Read the target page completely
2. Read the conventions it must follow:
   - `_system/conventions/compiled-truth.md`
   - `_system/conventions/source-attribution.md`
   - `_system/conventions/source-types.md` (if person page)
   - `_system/conventions/aliases.md` (if person page)
3. Classify each content block as **synthesis** (current state of play, beliefs, assessment) or **evidence** (dated events, meetings, decisions, quotes)

### Phase 2: Map to compiled-truth structure

Build the new page structure:

**For person pages:**
- frontmatter (preserve + add `aliases`, `status`)
- Executive Summary (1 paragraph distillation)
- State (current factual position — role, company, key context)
- What They Believe (synthesis only — beliefs with source-type labels)
- What They're Building (current projects)
- Communication Style (observed-only claims)
- Open Threads (active items, pending)
- Assessment (Strengths / Gaps / Net Read / Confidence / Last assessed)
- Trajectory (Ascending / plateauing / pivoting / declining + evidence)
- Team Around Them (if applicable)
- See Also (cross-links)
- `---`
- Timeline (every dated event as `- **YYYY-MM-DD** | summary  [Source: ...]`, newest first)

**For venture/project pages:**
- frontmatter (preserve + add `status`)
- Executive Summary
- State (current state, stage, key metrics)
- What's Being Built (current scope)
- Open Threads
- Team / Roles
- Active Risks / Blockers
- Trajectory
- See Also
- `---`
- Timeline

### Phase 3: Identify unsourced claims

For every claim in the synthesis sections, attempt to source from:
1. Existing inline context in the source page (e.g., "Decided at 2026-03-30 meeting")
2. Original `source:` frontmatter field
3. Timeline entries that support the claim
4. Recent journal entries that mention the entity (`grep journal/`)
5. MEMORY rules that reference the claim

**If a claim cannot be sourced from the above, flag it.** Don't guess. Present to user:
```
Unsourced claim found:
  "Entity is in a pivotal growth stage"
Where did this come from? (paste source attribution or say "remove" / "skip")
```

User responds → apply the citation.

### Phase 4: Add source-type labels (person pages only)

For each claim in What They Believe / Communication Style / Assessment:
- Label as `observed` (you saw it) / `self-described` (they said it) / `inferred` (reading between lines)
- Add confidence: `high` (5+ interactions) / `medium` (2-4) / `low` (1 or thin)
- Add last date

Same flagging rule: if unsure, ask.

### Phase 5: Write

1. Move original to `<page>.bak.md`
2. Write the new page at the original path
3. Verify in Obsidian (file opens, links work, frontmatter parses)

### Phase 6: Back-link reconciliation

Run a partial back-link sweep — for every entity wikilinked in the refactored page, check if their page has a corresponding back-link to this page. Flag missing back-links to the user (don't auto-add to other pages — that's `/brain-back-link-sweep`'s job).

### Phase 7: Report

Output to user:
```
Refactored: <page>
Original backed up to: <page>.bak.md

Sections produced:
- Executive Summary
- State (N facts, all sourced)
- What They Believe (N beliefs labeled)
- ...

Timeline: N entries, all sourced.

Unresolved:
- N unsourced claims removed per user instruction
- N back-link gaps in other pages (run /brain-back-link-sweep)

Diff summary: <old line count> → <new line count>
```

## Reference inputs

Read these files before refactoring:
- The target page itself
- `_system/conventions/compiled-truth.md` — the format spec
- `_system/conventions/source-attribution.md` — citation format
- `_system/conventions/source-types.md` — observed/self-described/inferred labels
- `_system/conventions/aliases.md` — alias frontmatter (if person)
- `_system/MEMORY.md` — for source attribution context (recent activity, decisions)

## Output format

```markdown
✅ Refactored people/<Name>.md to compiled-truth + timeline.

Backup: people/<Name>.bak.md
Diff: <N> lines → <M> lines

Convention compliance:
- ✅ frontmatter has aliases (N variants)
- ✅ --- separator present
- ✅ N facts sourced, 0 unsourced
- ✅ N beliefs labeled (observed/self-described/inferred)
- ✅ Timeline: N entries, all sourced, newest-first

Outstanding:
- <list of back-link gaps found in other pages>
```

## Anti-patterns

- ❌ Guessing source attribution — always ask the user when unsure
- ❌ Writing the refactored page without backing up the original
- ❌ Adding source-type labels to claims with no real basis ("observed" when never observed)
- ❌ Inflating confidence — confidence tracks interaction count, not how strongly you feel about the claim
- ❌ Editing existing timeline entries during refactor — they're immutable. Add new entries if corrections needed.
- ❌ Dropping wikilinks during refactor — preserve every existing link, just relocate to the right section
- ❌ Refactoring pages that don't need it (daily notes, meeting pages, summaries)

## Tools used

- Read — load target page + conventions + reference pages
- Edit / Write — produce refactored page + backup
- Grep — search journal/ and other pages for source attribution + back-link verification
- AskUserQuestion — for unsourced claims that need user input

## See also

- [[_system/conventions/compiled-truth]] — the format being applied
- [[_system/conventions/source-attribution]] — Iron Law of citations
- [[_system/conventions/source-types]] — observed/self-described/inferred labels
- `/brain-back-link-sweep` — runs after refactor to clean other pages' back-links
- `/brain-source-fix` — alternative when only the citations need fixing (not full refactor)
