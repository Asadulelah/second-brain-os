---
type: resolver
---

# ventures/

One directory (or page) per venture, agency, company, or client the user runs, partners on, or has an active commercial relationship with.

## What goes here

- The user's own ventures and businesses
- Active partnerships and collaborations
- Client engagements (under `ventures/clients/`)
- Outreach partner organizations
- Active competitor analyses

## What does NOT go here

- Generic SaaS tools the user subscribes to (no strategic relevance)
- Public companies referenced as examples
- One-off pitches that didn't progress
- The people who run these ventures — they go in `people/`

## Structure

```
ventures/
  acme/           ← primary venture (replace with your venture name)
  nexus/          ← a partner agency or collaboration
  solo/           ← user's independent / personal brand work
  clients/        ← per-client engagement folders
    <client>.md
  partners/       ← outreach / institutional partnerships
```

Sub-directories get their own `README.md`. Single-page ventures use a `.md` file directly under `ventures/`.

## Person vs. Venture

If content is about the **person** behind a venture → `people/`
If content is about the **organization** itself → `ventures/`
Both pages exist for key relationships and cross-link aggressively.

## Format

Venture pages follow [[_system/conventions/compiled-truth]] format where applicable.
Client pages document the engagement: status, offer, deliverables, timeline, decisions.

## See also

- [[_system/conventions/filing-rules]] — disambiguation between ventures, systems, strategy
- [[_system/conventions/back-linking]] — link to people pages from venture pages
