---
type: resolver
---

# strategy/

Actionable artifacts the user is actively using: offers, pricing, positioning, ICPs, outreach playbooks, campaign strategies.

## What goes here

- Offer definitions and pricing structures
- Ideal customer profiles (ICPs) and target market analyses
- Positioning and messaging frameworks the user is actively using
- Outreach playbooks and campaign strategies
- Niche-specific offer playbooks (under `strategy/niche-offer-books/`)

## What does NOT go here

- Reusable mental models or research the user might apply elsewhere → that's `knowledge/`
- The user's identity, values, or long-term goals → that's `me/`
- Meeting notes about a strategy discussion → that's `journal/`
- Technical implementation of a strategy → that's `systems/`

## Strategy vs. Knowledge

Test: "Is this a thing the user is selling/using directly?" → `strategy/`
Test: "Is this a framework they're distilling for future reference?" → `knowledge/`

## Structure

```
strategy/
  niche-offer-books/     ← per-niche offer playbooks
  Target Market ICP.md
  Outreach Playbook.md
  Campaign Strategy.md
  Offer Ladder.md
```

## Format

Strategy files are typically durable artifacts — they get updated as strategy evolves, not replaced. Use clear sections: context, the offer/position/tactic, decision rationale, and status.

## See also

- [[_system/conventions/filing-rules]] — strategy vs. knowledge vs. me
