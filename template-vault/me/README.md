---
type: resolver
---

# me/

Identity content about the user themselves: who they are, what they believe, where they're going, and patterns to be aware of.

## What goes here

- The user profile page: `me/{{user_name}}.md` (created during onboarding)
- Goals and vision: `me/Goals and Vision.md`
- Values and rules: `me/Values and Rules.md`
- Personal patterns (strengths to leverage, habits to break)
- Origin story and background

## What does NOT go here

- The user's ventures and businesses → those go in `ventures/`
- The user's technical systems → those go in `systems/`
- The user's strategy and offers → those go in `strategy/`
- Meeting notes or daily logs → those go in `journal/`
- Preferences and rules for how the assistant operates → those go in `_system/MEMORY.md`

## Me vs. Memory

`me/` contains **world knowledge about the user** (facts about who they are, their goals, their background).
`_system/MEMORY.md` contains **operational rules** (how the assistant should behave with them).

Don't put "User prefers X tone" in `me/` — that's a MEMORY entry.
Don't put "User grew up in X" in MEMORY — that's a `me/` entry.

## Format

The user profile page (`me/{{user_name}}.md`) follows a modified [[_system/conventions/compiled-truth]] format:
- Identity, background, values, goals above the `---`
- Timeline of key life events and decisions below the `---`

## See also

- [[_system/conventions/brain-vs-memory]] — me/ vs. MEMORY routing rule
- [[_system/conventions/filing-rules]] — me/ in the decision tree
