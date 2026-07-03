---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/docs/GBRAIN_RECOMMENDED_SCHEMA.md (Enrichment Tiers section)
tags:
  - convention
  - enrichment
  - pages
---

# Tiered Enrichment

> Not every entity deserves the same depth of page. The brain learns who matters by signal frequency. Don't over-enrich one-off mentions. Do enrich anyone who shows up repeatedly. Three tiers — they map cleanly to interaction count.

## The three tiers

| Tier | Trigger | Enrichment depth | Page state |
|---|---|---|---|
| **T3 — Stub** | 1-2 mentions, single passing reference, no follow-through | Name + 1-2 line context. **No web search, no enrichment APIs.** | Skeleton page only |
| **T2 — Substantive** | 3+ mentions across different sources, or single notable event | Web search + social check (LinkedIn / X / IG). Brief State + Beliefs + What They're Building if findable. | Substantive page, ~200-500 words |
| **T1 — Full** | Meeting attended (1:1 or small group), 8+ mentions, or user-flagged "I work with this person" | Full pipeline: web + social + meeting history + cross-reference + Assessment + Trajectory | Full page following [[compiled-truth]] format |

## The escalation rule

**Pages start at T3 and escalate** as signal accumulates. They don't downgrade automatically — once a person is T1, they stay T1 unless explicitly archived (relationship ended, deal closed dead).

```
Trigger: Person mentioned for first time in journal
  → Apply [[notability-gate]]: notable enough to page?
  → If yes: create T3 stub
  → If no: just note in source page, no page yet

Trigger: Same person mentioned 3+ times across different sources
  → Auto-escalate: T3 → T2
  → Run web + social check
  → Fill in State, What They Believe (with source-types), What They're Building

Trigger: Meeting attended with this person OR 8+ mentions
  → Auto-escalate: T2 → T1
  → Full pipeline + Assessment + Trajectory + Communication Style
```

## Tier examples

**T1 (full pages, frequent updates):**
- A co-founder — daily standups, every meeting filed
- A key collaborator — recent joint project processed
- An active client — demo site shipped, ongoing engagement
- A close partner — partnership track, deep synthesis done

**T2 (substantive, occasional updates):**
- A teammate on a specific initiative
- A warm lead in active conversation
- A contact who followed back and engages regularly
- A local partner with an in-flight deal

**T3 (stub, one-time mention):**
- Most names from transcripts that came up once
- People mentioned in summaries/articles without further engagement

## Don't over-enrich

A fat page stuffed with generic web search results is **worse** than a thin page with real interaction data. Specific anti-pattern: someone gets mentioned once, the assistant creates a "comprehensive" page with their LinkedIn bio + tweets + company background. That's noise. It dilutes the signal of the people who actually matter.

The discipline:
- **No web search for T3.** Period.
- **No LinkedIn API call for T3.** Period.
- **For T2, web search is OK** but synthesize aggressively. Don't dump bullet lists.
- **Only T1 gets a full Assessment / Trajectory / Communication Style section** (those sections require multiple interactions to write honestly).

## Don't under-enrich either

A person who's appeared 5 times across journal entries deserves more than a one-line stub. The escalation rule auto-fires. `/brain-tier-audit` finds:
- **Under-enriched:** 3+ mentions but page is still a stub → escalate
- **Over-enriched:** 1 mention but page has full pipeline → demote / archive

## What "mention" means

A "mention" counts when:
- ✅ Name appears in a journal entry, meeting page, or substantive note
- ✅ Distinct context (not the same event reported twice)
- ✅ User acknowledged the person (vs. just being a name in a transcript)

A "mention" does NOT count when:
- ❌ Name appears in raw/ (immutable source, doesn't drive brain decisions)
- ❌ Name appears in summaries/ if it's not the primary subject
- ❌ Bulk transcript lists where the user never interacted

## Tier changes are visible

When a tier escalates, log it in the page's timeline:
```
- **YYYY-MM-DD** | Tier 3 → Tier 2 — substantive enrichment after 3rd mention  [Source: tier-audit run]
```

This makes the brain auditable. Future sessions can ask "when did this person become important?"

## What this convention replaces

Without this convention, every person mentioned tends to either (a) get a full page right away, or (b) never get one. There's no middle. Result: some pages are basically stubs that didn't need to exist; others are missing for people who clearly deserve them (because the threshold to create felt high).

## Verification

`/brain-tier-audit` checks:
1. ✅ Every T1 page has at least 8 timeline entries OR a meeting attended
2. ✅ Every T2 page has 3+ mentions in journal/meetings
3. ✅ No T3 stubs have web-search bullet lists (sign of over-enrichment)
4. ✅ No T2/T1 pages have only 1 mention (sign of premature creation)

## See also

- [[notability-gate]] — does this entity get any page at all
- [[compiled-truth]] — page format for T1/T2
- [[source-types]] — source labeling required on T1 pages
