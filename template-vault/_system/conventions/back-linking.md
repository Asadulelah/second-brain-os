---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/skills/conventions/quality.md
tags:
  - convention
  - iron-law
  - graph
---

# Back-Linking (Iron Law)

> Every mention of a person, company, or venture WITH a brain page MUST create a back-link FROM that entity's page TO the source page. **An unlinked mention is a broken brain.** The graph is the intelligence.

## The format

When a page mentions an entity that has its own page, two things happen:

1. **The mentioning page links TO the entity** using a wikilink:
   ```
   Met with [[Alex Chen]] re: Acme project timeline.
   ```

2. **The entity's page links BACK to the mention** in its Timeline section:
   ```
   - **YYYY-MM-DD** | Referenced in [[2026-05-17 Project Sync]] — discussed timeline pressure
   ```

The wikilink in #1 is one direction. The back-link in #2 is the other. **Both must exist.** Obsidian shows backlinks via its panel, but our convention is that the back-link is **explicit in the markdown**, not just inferred from Obsidian.

## Why explicit (not just Obsidian-implicit)

- Obsidian's backlinks panel only shows links to the file. Our convention captures **when** and **in what context** the mention happened — that becomes timeline data.
- Future skills (graph extraction, dashboard rendering) need structured back-links to query.
- The discipline of writing the back-link forces the act of cross-checking: "did I correctly attribute this to the right entity?"

## When the rule fires

| Scenario | Action |
|---|---|
| Journal entry mentions [[Alex Chen]] | Add timeline entry to `people/Alex Chen.md` |
| New meeting page lists Alex as attendee | Add timeline entry to Alex's page with context |
| Concept page references a venture | Add timeline entry to that venture's page |
| A piece of content ships about a topic | If the topic has a concept page, add timeline entry there |
| User mentions a new person who already has a page | Add timeline entry; do NOT create duplicate page |
| User mentions a new person who does NOT have a page | Apply notability gate per [[notability-gate]] — if notable, create page + cross-link; if not, just note in source page |

## The format for back-links

```
## Timeline

- **YYYY-MM-DD** | Referenced in [[Source Page Title]] — brief context  [Source: ...]
- **YYYY-MM-DD** | Direct interaction — what happened  [Source: ...]
```

Two flavors:
- **"Referenced in"** — the entity was mentioned (third-person)
- **Direct interaction** — the entity was the subject of the event (meeting, email, call)

## Timing — back-links are not optional later

Back-links happen **at the same time** as the source page write. Not "I'll batch them later." Reasons:

1. Future-you forgets context. Back-links written next day have lower fidelity.
2. The graph stays consistent. No drift between source and entity pages.
3. `/brain-back-link-sweep` is for catching misses, not for routine workflow. If we always need the sweep, the iron law isn't being followed.

## Exceptions (small list)

| Case | Exception |
|---|---|
| Mention is in a code block / quote / transcript fragment | No back-link (it's source material, not a brain claim) |
| Mention is incidental in a daily note with no notability | No back-link if entity has no brain page and isn't notable |
| Self-reference (user's page mentions the user) | No back-link to self |
| Auto-generated reports (Dream Reports, daily briefs) | No back-link required — these are derivative, not authoritative |

## What this convention replaces

Most existing pages mention entities with wikilinks in one direction, but the reverse links are inconsistent. Some entity pages have backlinks, some don't. The convention enforces bidirectional consistency.

## Verification

A back-link is correctly applied if:
1. ✅ The entity page has a timeline entry corresponding to the source page
2. ✅ The timeline entry has a date matching the source event
3. ✅ The timeline entry links back to the source page via wikilink
4. ✅ The entry has a `[Source: ...]` attribution per [[source-attribution]]
5. ✅ The entry has brief context — not just "mentioned"

## Anti-patterns

- ❌ Source page links to entity via `[[X]]` but X's page has no corresponding timeline entry
- ❌ Back-link is just `- Referenced` with no date / context / source
- ❌ Bulk-creating back-links from old pages without verifying context (creates noise)
- ❌ Back-linking trivial mentions (e.g., "saw Alex at coffee, didn't speak" — not back-link-worthy)
- ❌ Back-linking transient mentions to a person who doesn't have a page yet — apply notability gate first

## See also

- [[compiled-truth]] — back-links live in the Timeline zone
- [[source-attribution]] — every back-link entry needs a source
- [[notability-gate]] — does this entity get a page at all
- `/brain-back-link-sweep` — automated audit (to be built)
