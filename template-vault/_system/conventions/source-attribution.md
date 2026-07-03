---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/skills/conventions/quality.md
tags:
  - convention
  - iron-law
  - quality
---

# Source Attribution (Iron Law)

> Every factual claim written to a brain page carries an inline `[Source: ...]` citation. Unsourced synthesis = forbidden. Timeline entries are always sourced. No exceptions.

## The format

`[Source: who, channel, YYYY-MM-DD, timezone]`

| Type | Format | Example |
|---|---|---|
| User's direct statement | `[Source: User, {context}, YYYY-MM-DD]` | `[Source: User, in chat re: project meeting, 2026-05-17]` |
| Meeting | `[Source: Meeting "{title}", YYYY-MM-DD]` | `[Source: Meeting "Acme CRM Walkthrough", 2026-05-11]` |
| Email / message | `[Source: email from {name} re: {subject}, YYYY-MM-DD]` | `[Source: WhatsApp from Alex re: outreach, 2026-04-23]` |
| Web content | `[Source: {publication}, {URL}, YYYY-MM-DD]` | `[Source: paulgraham.com, http://..., 2013-07-01]` |
| Social media | `[Source: X/@handle, YYYY-MM-DD]` or `[Source: Instagram/@handle, 2026-05-17]` | |
| Synthesis from multiple | `[Source: compiled from {list}]` | `[Source: compiled from Jordan questionnaire + 2026-05-13 Taylor call]` |
| Personal observation | `[Source: User direct observation, YYYY-MM-DD]` | |

## Source precedence (highest to lowest)

1. **User's direct statements** — highest authority. If the user said it, that's the truth-of-record.
2. **Compiled truth** — pre-existing synthesis in the brain. Trust this over external sources.
3. **Timeline entries** — raw evidence already filed.
4. **External sources** — API enrichment, web search, social media scrape. Lowest.

**When sources conflict, note the contradiction with both citations.** Don't silently pick one. Example:
```
Role: VP Engineering at Acme Corp [Source: company website, 2026-04-12]
      | CTO per LinkedIn [Source: linkedin.com/in/x, 2026-04-08]
      ⚠️ Conflict — verify next interaction
```

## Where attribution is required

| Location | Required? |
|---|---|
| Synthesis claims (above `---`) | **YES** — every claim |
| Timeline entries (below `---`) | **YES** — every entry |
| Frontmatter `source:` field | Recommended for ingested content |
| Wikilinks `[[X]]` | No — links are structural, not factual claims |
| Headings | No |
| Open Threads | YES, on the underlying claim (e.g., "send proposal" doesn't need source; "Alex wants a 50/50 split" does) |

## What counts as a "factual claim"

A factual claim is anything an outsider could fact-check or anything that could be wrong. Examples:

| Counts as a fact (needs source) | Doesn't count |
|---|---|
| "Alex is CEO of Acme Corp" | "## Relationship" (heading) |
| "Q2 target: $15,000/month" | "Open Threads:" (label) |
| "Jordan pushed back on the timeline" | "See also: [[X]]" |
| "Campaign got 50+ leads" | Section structure |
| "Prefers async messages over calls" | |
| "Has a launch scheduled for September 2026" (future fact) | |

## Direct quotes

Use quote marks and a source. Always preserve the user's exact phrasing — never paraphrase memorable quotes.

```
"Quality always beats speed." — User [Source: User, 2026-05-14]
"Not ready yet." — a co-founder's first reaction to the draft [Source: User, 2026-05-07]
```

## Confidence vs. source

Source attribution is WHERE the claim came from. Confidence (high/medium/low) is HOW MUCH you trust it. They're different. Most claims need source; only beliefs/assessments on person pages need confidence labels (see [[source-types]]).

## What this convention replaces

Most existing pages have unsourced claims buried in prose. "Alex is short on budget" — true, but where did we learn it? When? From whom? Without a source, the claim drifts: future sessions can't tell if it's still current, can't verify, can't retract if the situation changes.

## Verification

A page complies if:
1. ✅ Every fact in synthesis has `[Source: ...]` directly after it (or grouped at end of paragraph)
2. ✅ Every timeline entry ends with `[Source: ...]`
3. ✅ Source format matches the table above (consistent, not free-form)
4. ✅ Conflicting sources are flagged inline, not silently resolved

## Anti-patterns

- ❌ `Alex is short on budget.` (no source — UNCITED)
- ❌ `Alex is short on budget. [Source: User]` (no date — UNDATED)
- ❌ `Alex is short on budget. [Source: somewhere in chat]` (too vague — UNVERIFIABLE)
- ❌ Bulk citations: "Most of these facts: [Source: chat]" — must be inline per claim
- ✅ `Alex is short on budget — can't fund {{assistant_name}}'s API credits even though Acme Corp uses it. [Source: User, in chat re: Acme cashflow, 2026-04-15]`

## See also

- [[compiled-truth]] — both zones require attribution
- [[source-types]] — additional labels (observed/self-described/inferred) for beliefs
- [[back-linking]] — orthogonal Iron Law for entity references
