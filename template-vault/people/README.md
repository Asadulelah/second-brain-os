---
type: resolver
---

# people/

One page per person who meets the [[_system/conventions/notability-gate]] threshold.

## What goes here

- Anyone the user has had a 1:1 conversation with
- Anyone mentioned 3+ times across different sources/dates
- Anyone who attends a meeting the user is in with follow-through
- Any person the user explicitly marks as "track this"

## What does NOT go here

- One-off names from transcripts with no follow-through
- Public figures cited as examples but not engaged with
- Generic contacts from import lists (CSV, CRM export) with zero relationship signal
- Organizations or companies — those go in `ventures/`

## Format

Each file follows the [[_system/conventions/compiled-truth]] two-layer format:
- **Above `---`**: compiled synthesis (State, Beliefs, What They're Building, Assessment, Trajectory)
- **Below `---`**: append-only Timeline

Filename: `Full Name.md` (e.g., `Alex Chen.md`)

## Enrichment tier

Pages start as T3 stubs and escalate per [[_system/conventions/tiered-enrichment]]:
- T3: name + 1-2 lines, no web search
- T2: web + social check, substantive sections
- T1: full pipeline, all sections, Assessment + Trajectory

## See also

- [[_system/conventions/notability-gate]] — when to create a page
- [[_system/conventions/tiered-enrichment]] — how deep to enrich
- [[_system/conventions/aliases]] — prevent split-brain duplicates
- [[_system/conventions/back-linking]] — link back from entity pages
