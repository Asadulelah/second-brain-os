---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/docs/guides/compiled-truth.md
tags:
  - convention
  - page-format
  - iron-law
---

# Compiled Truth + Timeline (the two-layer page format)

> Every entity page in this vault has TWO zones, separated by a horizontal rule `---`. Above is synthesis. Below is evidence. They follow different update rules.

## The format

```markdown
---
date: YYYY-MM-DD
type: person | venture | project | concept
aliases: [name variants if person]
tags: [...]
---

# Entity Name

> Executive summary: one paragraph. If you read only this, you know the state of play.

## State
Current role, current company, key context in 2-4 bullets.

## What They Believe   (person pages only)
Worldview, positions, first principles — each claim labeled with source-type per
[[_system/conventions/source-types.md]].

## What They're Building   (person/venture pages)
Current projects, recent ships, product direction.

## Communication Style   (person pages only)
How they prefer to communicate. Strict sourcing — observed only.

## Open Threads
Active items, pending decisions, follow-ups. **Remove when resolved** (entry moves to Timeline with resolution).

## Assessment   (person pages only)
- **Strengths:** specific
- **Gaps:** specific
- **Net read:** one-line synthesis
- **Confidence:** high (5+ interactions) / medium (2-4) / low (1 or inferred)
- **Last assessed:** YYYY-MM-DD

## Trajectory   (person/venture pages)
Ascending / plateauing / pivoting / declining? Evidence.

## See Also
Cross-links to related entities.

---

## Timeline

- **YYYY-MM-DD** | Source — What happened.   [Source: ...]
- **YYYY-MM-DD** | Source — What happened.   [Source: ...]
```

## The two update rules

| Zone | Action | Why |
|---|---|---|
| Above `---` (compiled truth) | **REWRITE** | Synthesis is always current. Old assessments that no longer hold get replaced, not kept alongside. |
| Below `---` (timeline) | **APPEND** only | Evidence trail. Immutable. Adding new entries is the only legal mutation. |

**REWRITE means rewrite, not append.** Don't add a second paragraph to compiled truth. Rewrite the whole section integrating the new evidence. Stale assessments that no longer hold get replaced, not preserved next to contradictory new ones.

**Timeline entries are immutable.** Never edit a past entry. If information turns out to be wrong, add a NEW entry correcting it:
```
- 2026-04-10 | Correction: Alex is VP Eng, not CTO. Earlier 2026-04-03 entry was wrong.
```

## Traceability rule

**Every claim in compiled truth must trace to evidence in timeline.** If the Assessment says "under-appreciated internally," there must be timeline entries supporting that read. If you can't trace a claim to evidence, either find the evidence or remove the claim.

## Search behavior

When a future retrieval skill (or human grep) scans this vault, the convention is that compiled-truth chunks rank higher than timeline chunks. **The freshest synthesis surfaces first.** This is the killer feature of the format vs append-only logs: you don't have to read 200 timeline entries to know the state of play.

## What this convention replaces

Pages used to be free-form prose. Some had timelines (informally), some didn't. Some had Open Threads, some had Pending sections, some buried decisions in narrative. The format above replaces that ambiguity with one repeatable structure.

## When NOT to use this format

- **Daily notes** (`journal/YYYY-MM-DD.md`) — these ARE timeline entries, not entities. No `---` needed.
- **Meeting pages** (`journal/YYYY-MM-DD <topic>.md`) — these are records of one event. Use full prose with attendees/decisions/action items. No compiled truth.
- **Source summaries** (`summaries/`) — distilled content from one source. Compiled-truth style optional.
- **Concept pages** (`knowledge/`) — for distilled ideas; compiled truth + small timeline of "where this concept appeared" works well.

## Verification

A page follows this convention if:
1. ✅ It has YAML frontmatter
2. ✅ Synthesis sections appear ABOVE a `---` separator
3. ✅ A `## Timeline` section appears BELOW the `---`
4. ✅ Every claim in synthesis is traceable to a timeline entry
5. ✅ No claim in synthesis lacks a source attribution (per [[source-attribution]])
6. ✅ Old synthesis got rewritten (not appended) when last updated

## Anti-patterns

- ❌ Two separate synthesis sections separated by `---` (the second one is shadow truth)
- ❌ Editing a timeline entry to "correct" it — add a new entry instead
- ❌ Compiled-truth claims with no traceable evidence
- ❌ Pages with timeline but no synthesis ("event log" pages — fine for journal, not for entities)
- ❌ Pages with synthesis but no timeline ("essay" pages — fine for writing/, not for entities)

## See also

- [[source-attribution]] — citation format for both zones
- [[back-linking]] — Iron Law for entity references
- [[source-types]] — labeling beliefs on person pages
- [[filing-rules]] — which directories use this format
