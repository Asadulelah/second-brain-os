---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/docs/GBRAIN_RECOMMENDED_SCHEMA.md (Entity Identity)
tags:
  - convention
  - frontmatter
  - dedup
---

# Aliases (anti-split-brain rule for entities)

> Every person and venture has multiple names across sources — meeting transcripts misspell, emails use abbreviations, social handles differ. The `aliases` frontmatter field captures all variants so future ingest doesn't create duplicate pages.

## The format

In page frontmatter:

```yaml
---
date: 2026-05-18
type: person
aliases:
  - "Alex"
  - "A. Chen"
  - "alex@acmecorp.io"
  - "AlexC"
tags: [people, acme]
---
```

For ventures / companies:

```yaml
---
date: 2026-05-18
type: venture
aliases:
  - "AutoBase"
  - "Auto Biz"
  - "Jordan's agency"
tags: [nexus, autobiz]
---
```

## What goes in aliases

| Type | Example |
|---|---|
| Common nicknames | `"Alex"` for Alex Chen |
| Maiden names / former surnames | (if applicable) |
| Misspellings from transcripts | `"Alec"` (transcription tools often misspell) |
| Email addresses | `"alex@acmecorp.io"` |
| Social handles | `"@alex.ventures"`, `"@acmecorp"` |
| Phonetic / Roman variants of non-English names | `"Sam"` / `"Saam"` |
| Initialisms | `"A.C."` if frequently used |
| Phone numbers | (if used as identifier — careful with privacy) |
| Former company names | `"AutoBase"` → now AutoBiz |
| Casual references | `"the Toronto contact"` for Casey (if user uses it consistently) |

## What does NOT go in aliases

- ❌ Roles or titles ("CEO" — that's not an identity, it's a position)
- ❌ Descriptive labels ("the tall guy" — not stable)
- ❌ Random nicknames the user used once
- ❌ Generic terms ("dad" — depends on context; if it ALWAYS refers to one person it can go in)

## The dedup protocol

**Before creating any new person/venture page, the assistant must:**

1. Search by exact name in `people/` or `ventures/`
2. Grep aliases across all pages in the relevant directory:
   ```bash
   grep -l "name_variant" <vault-root>/people/*.md
   ```
3. Check `_system/MEMORY.md` for known associations
4. If a match found → **UPDATE** the existing page (add the new name variant to aliases if unknown)
5. If no match → CREATE a new page

**Never create a duplicate page.** A split-brain (two pages for the same person) is the #1 entity-management failure mode.

## When aliases get added

| Event | Action |
|---|---|
| Page created | Add known aliases at creation time |
| New name variant encountered | **Add to existing page's aliases field** — don't create a new page |
| User mentions a nickname for the first time | Add it (if the nickname will recur) |
| Person's email/social handle becomes known | Add it |
| Person rebrands / changes name | Add new name as alias; rename page only if user explicitly requests |

## Alias clusters to watch for

Seed this section with known alias clusters when onboarding. Example structure:

| Canonical | Variants |
|---|---|
| Alex Chen | Alex, A. Chen, alex@acmecorp.io |
| {{user_name}} | (add personal nicknames/handles here) |
| Sam Kim | Sam, S.K., @sam.builds |
| Jordan Lee | Jordan, JL, jordan@nexus.io |
| AutoBiz | AutoBase (old name), Auto Biz |

## Verification

A page complies if:
1. ✅ Frontmatter has `aliases:` field (even if empty list for entities with one known name)
2. ✅ All known variants for this entity appear in the list
3. ✅ No other page in the vault has any of these aliases (no split-brain)

`/brain-dedup` automates the dedup check.

## Anti-patterns

- ❌ Two pages for the same person (split-brain — `Alex.md` AND `Alex Chen.md`)
- ❌ Aliases include titles or roles instead of identity variants
- ❌ Forgetting to add a new variant after encountering it
- ❌ Creating a new page when an alias would have routed to an existing page (failed dedup check)

## See also

- [[notability-gate]] — does this entity warrant a page at all
- [[filing-rules]] — once notable, which directory
- `/brain-dedup` — automated duplicate detection (to be built)
