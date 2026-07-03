---
type: resolver
---

# systems/

Technical architectures, tools, and infrastructure the user has built or is actively building. The **artifact**, not the business around it.

## What goes here

- Personal AI infrastructure (assistant dashboards, curator tools, schedulers)
- Technical systems and pipelines the user built
- Architectural designs and specs
- Integrations and automation tooling

## What does NOT go here

- The venture or business built on top of a system → that's `ventures/`
- Strategy and positioning around a product → that's `strategy/`
- Conceptual frameworks and mental models → that's `knowledge/`
- Meeting notes about a system's development → those are `journal/`

## Venture vs. System distinction

`ventures/acme/` = the business (offers, team, positioning, clients)
`systems/acme-platform/` = the technical artifact (architecture, APIs, data model)

Both can exist and cross-link. Don't conflate them.

## Format

Top-level systems get their own `.md` page. Complex systems get a sub-directory.
System pages typically include: overview, architecture diagram (or description), key components, status, changelog.

## See also

- [[_system/conventions/filing-rules]] — system vs. venture vs. knowledge
