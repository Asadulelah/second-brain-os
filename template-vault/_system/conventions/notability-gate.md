---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/skills/signal-detector/SKILL.md (notability_filtering)
tags:
  - convention
  - filtering
  - page-creation
---

# Notability Gate

> Not every entity deserves a brain page. Apply this gate before creating any new page. A junk page degrades search quality and wastes attention. A missing page can always be created later.

## The gate

Before creating a new entity page, ask three questions:

1. **Will I interact with this entity again?** (Future relevance)
2. **Is it relevant to my work, ventures, or active priorities?** (Topical relevance)
3. **Is there a signal beyond passing reference?** (Notability threshold — see below)

If all three are NO, **don't create the page.** Note the entity in the source page (journal/meeting/summary) and move on. If it becomes notable later, create then.

## Notability signals (any one = create T3 stub minimum)

✅ **Create a page when:**
- User has had a 1:1 conversation with this person
- Person is mentioned 3+ times across different sources/dates
- Person attends a meeting the user is in
- User explicitly says "track this person" / "this is important"
- Direct interaction with follow-through (DM exchange, email thread, scheduled call)
- Recurring engagement pattern (commenting on multiple posts, etc.)
- Person is a recurring participant in an active venture
- User shows or describes something they built that's worth tracking

❌ **Don't create a page when:**
- One-off name from a meeting transcript with no follow-through
- Generic reference in an article or news mention
- Person mentioned once as an example, not the subject
- Public figure cited as a metaphor ("like a famous investor, we should...")
- Low-engagement social interaction (one tweet reply, one comment)
- Name pulled from a CSV/contact import with zero relationship signal

## The "when in doubt, don't create" rule

A missing page can be created in 30 seconds when notability emerges. A junk page sits in search results forever, dilutes the signal of real entities, and creates the impression that the brain is fuller than it is.

**Default to NOT creating.** Notability has to earn its place.

## What about people the user meets briefly?

If the user meets someone at an event / IRL but no follow-through is planned:
- Note in the journal entry for that day
- DO NOT create a person page
- IF they reach out later or come up again → create page then with both data points

## What about people mentioned in transcripts?

Meeting transcripts often include attendees who didn't speak or weren't relevant. **Transcript attendees ≠ automatically notable.** Only create pages for transcript-mentioned people if they meet a notability signal independent of the transcript.

## What about competitors / industry figures the user references but doesn't engage with?

Industry figures the user cites repeatedly → **judgment call**.

- If the user's strategy / mental models actively reference them → page in `knowledge/` or `people/` is fine
- If they're just an example → no page; reference in `knowledge/<concept>.md` instead

## Companies and ventures

Same gate applies:

✅ **Create a company/venture page when:**
- Active commercial relationship
- Active partnership / collaboration
- Active deal in flight
- Active competitor analysis
- User's own venture or sub-venture

❌ **Don't create when:**
- Generic vendor (e.g., a SaaS the user uses but doesn't have strategic relevance)
- Public company referenced as an example
- One-off pitch that didn't progress

## Concepts and ideas

Apply notability slightly differently:

✅ **Create a concept page when:**
- Reusable mental model the user has referenced 3+ times
- Framework the user has explicitly endorsed or built into their thinking
- Idea the user is actively developing

❌ **Don't create when:**
- One-off term from an article that doesn't recur
- Generic concept the user mentioned in passing
- Buzzword used without the user's own framing

## Verification

After a session that involved creating new pages, audit:
1. ✅ Each new page has a clear notability signal
2. ✅ No page was created for a single passing mention
3. ✅ Reasoning for creation is visible (often in the timeline first entry)

`/brain-tier-audit` catches the inverse: pages that were created but never recurred (should they be archived?).

## What this convention replaces

Without this convention, the threshold to create a page is fuzzy. Sometimes pages get created for one-off mentions; other times notable people stay un-paged because the moment didn't trigger creation. This convention makes the trigger explicit.

## Anti-patterns

- ❌ "Just in case" page creation — stubs for everyone mentioned in a transcript
- ❌ Bulk import of contacts as person pages
- ❌ Page created from a single social media engagement
- ❌ Page created because the name "sounded important"
- ❌ Creating concept pages from every term the user uses once

## See also

- [[tiered-enrichment]] — once notable, which tier
- [[filing-rules]] — once created, which directory
- [[brain-vs-memory]] — does this even belong in the Wiki
