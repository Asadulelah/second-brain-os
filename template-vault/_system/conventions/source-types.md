---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/docs/GBRAIN_RECOMMENDED_SCHEMA.md (Epistemic Discipline)
tags:
  - convention
  - epistemic-discipline
  - person-pages
---

# Source Types (Epistemic Discipline on Person Pages)

> Person pages have high-value subjective sections (Beliefs, Communication Style, Assessment) that are also high-risk for hallucination. Every claim in those sections gets a source-type label. Never generalize from one data point.

## The three source types

| Type | Meaning | When to use |
|---|---|---|
| **observed** | I saw it happen | Meeting behavior, language in emails/tweets, visible patterns |
| **self-described** | They said it about themselves | Interview, bio, "I'm an X person", their own framing |
| **inferred** | I'm reading between the lines | Pattern across N interactions, deduction from circumstantial evidence |

## The format

In the page sections that need this discipline (What They Believe, Communication Style, Motivations, Assessment), every bullet looks like:

```
- {claim} — **{type}** [confidence: {high|medium|low}, last: YYYY-MM-DD]  [Source: ...]
```

Examples:

```
- Believes "quality always beats speed" — **self-described**
  [confidence: high, last: 2026-05-14]  [Source: User chat, 2026-05-14]

- Pushes back hard on timeline pressure — **observed**
  [confidence: high, last: 2026-05-11]  [Source: Meeting "Project CRM Walkthrough", 2026-05-11]

- Likely concerned about open-source positioning conflicting with monetization
  — **inferred**
  [confidence: medium, last: 2026-05-08]  [Source: compiled from 2026-05-07 sync + User's read]
```

## Confidence levels

| Level | Rule | Threshold |
|---|---|---|
| **high** | 5+ direct interactions OR explicit user statement | Confident assertion |
| **medium** | 2-4 interactions OR strong but indirect signal | Working assumption |
| **low** | 1 interaction OR pattern inferred from sparse data | Hypothesis, flag for verification |

**Confidence tracks interaction count, not how strongly you feel about the claim.** One vivid meeting ≠ high confidence. Five meetings = high confidence.

## Recency matters

Beliefs change. A belief from 2 years ago may not be current. The `last:` date in the label is the most recent evidence for the claim. When that date is stale (e.g., >12 months), flag for verification in next interaction.

## The rules

1. **Every claim cites source.** Not "she's aggressive" but "she pushed back hard on pricing in the March 15 meeting" — **observed** + source citation.
2. **Three source types only.** observed / self-described / inferred. No "everyone says" or "common knowledge" — those are not valid source types.
3. **Confidence tracks interaction count.** Don't write definitive assessments from thin data.
4. **Recency matters.** Dated labels surface stale beliefs.
5. **Never generalize from a single data point.** "She seemed frustrated in one meeting" is a timeline entry, not an assessment. Patterns require multiple observations.
6. **The user's corrections override everything.** If the user says "that's wrong about her," update immediately — that correction is the highest-confidence signal in the system.

## What this convention replaces

Current person pages make claims like:
- "Short on budget" — true, but observed how? When?
- "Recently refocused on personal development; correlates with big opportunity inbound" — observed or self-described? Which interaction?
- "Selling 'Agentic AI' as premium upgrade over basic automation" — inferred from their pitch? Or stated explicitly?

The labels force the precision. They turn vague reads into auditable claims.

## Sections that require this discipline

On a T1 person page:

| Section | Requires source-types? |
|---|---|
| Executive Summary | Recommended (per major claim) |
| State (role, company, key context) | No (factual, just needs source-attribution) |
| What They Believe | **YES** — every claim |
| What They're Building | No (factual, just sourced) |
| Communication Style | **YES** — every claim |
| Open Threads | No (action items, not beliefs) |
| Assessment (Strengths/Gaps/Net Read) | **YES** — every claim |
| Trajectory | **YES** — the read is inferred |
| Timeline entries | No (events, sourced via [[source-attribution]] only) |

## Examples — bad and good

❌ **Bad:**
```
## What They Believe
- He's territorial about content
- Probably stressed about money
- Doesn't trust outsiders easily
```

✅ **Good:**
```
## What They Believe
- Initial pushback on sharing draft publicly — possibly territorial OR strategic
  timing concern — **inferred** [confidence: low, last: 2026-05-07]
  [Source: User chat re: draft pushback, 2026-05-07]
- Short on budget — "can't fund the tool costs even though the team uses it"
  — **self-described** [confidence: high, last: 2026-04-15]
  [Source: User chat re: budget constraints, 2026-04-15]
- Trusts the user's technical execution; structurally relies on the user for product
  decisions — **observed** [confidence: high, last: 2026-05-11]
  [Source: Meeting "CRM Walkthrough", 2026-05-11]
```

## Verification

A T1 person page complies if:
1. ✅ Every claim in Beliefs / Communication Style / Assessment / Trajectory has a source-type label
2. ✅ Every label includes confidence + last date
3. ✅ Every claim has a `[Source: ...]` citation
4. ✅ No claims with "everyone says" / "people think" — those aren't valid types
5. ✅ Stale dates (>12 months) get flagged

## See also

- [[compiled-truth]] — which sections this discipline applies to
- [[source-attribution]] — orthogonal citation rule
- [[tiered-enrichment]] — only T1 pages need this depth
