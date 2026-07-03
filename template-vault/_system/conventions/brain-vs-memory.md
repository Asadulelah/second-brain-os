---
date: YYYY-MM-DD
type: convention
status: active
source: _system/external/gbrain/docs/guides/brain-vs-memory.md
tags:
  - convention
  - routing
  - architecture
---

# Brain vs. Memory vs. Session (the routing rule)

> Three layers. Three purposes. Every new piece of information lands in exactly one. Routing it to the wrong layer is what makes systems decay.

## The three layers

| Layer | What lives here | Persistence | Examples |
|---|---|---|---|
| **The Wiki** (vault content) | World knowledge — facts about people, ventures, projects, concepts | Durable. Versioned in git. Visible in Obsidian. | "Alex is CEO of Acme Corp", "ProjectCRM has 300K LOC", "Sam runs Learning Academy" |
| **MEMORY** (`_system/MEMORY.md`) | Operational state — assistant's preferences, rules, learned corrections, tool config | Durable. Hidden from Obsidian. Survives session restarts. | "User prefers concise responses", "Don't touch settings.json without permission", "Casual register for peers, formal for managers" |
| **Session** (current conversation context) | Current task, immediate state, what was just said | Ephemeral. Auto-compacts. | "We were just discussing the client demo", "You asked me to plan a tool adoption", "Reading file X right now" |

## The routing rule

Every time the assistant learns something new, ask: **is this about the WORLD, or about how to OPERATE?**

```
on new_information(info):
    if info.is_about_the_world:
        # WIKI — file as people/, ventures/, knowledge/, etc.
        Write entity page or append to existing page

    elif info.is_about_operations:
        # MEMORY — update _system/MEMORY.md
        Add to relevant memory entry

    elif info.is_current_conversation:
        # SESSION — already in window, no storage needed
        Continue
```

## Examples (where this often goes wrong)

| Input | Right layer | Wrong layer (common mistake) | Why |
|---|---|---|---|
| "Alex is CEO of Acme Corp" | Wiki (`people/Alex Chen.md`) | Memory | Fact about a person — durable world knowledge |
| "User prefers casual register for peers" | Memory | Wiki | Preference about the assistant's behavior, not a fact about the world |
| "Acme raised Series B at $50M" | Wiki (`ventures/acme.md`) | Memory | Fact about a company |
| "Don't use em-dashes in copy user will send" | Memory | Wiki | Rule about the assistant's output formatting |
| "Tuesday's meeting covered Q2 priorities" | Wiki (`journal/2026-MM-DD <topic>.md`) | Memory | Specific event, durable |
| "Last time subagents stalled on >25K-token files at 10 min" | Memory | Wiki | Operational learning about tools, not world knowledge |
| "Sam was the user's former colleague, worked together 1yr" | Wiki (`people/Sam Kim.md`) | Memory | Fact about a relationship |
| "The Sam conversation should use casual register" | Memory | Wiki | Rule about how to draft messages |
| "User's synthesis of Karpathy's LLM wiki pattern" | Wiki (under `knowledge/`) | Memory | Original thinking by the user = world knowledge from their POV |

## Why this matters

Without the rule:
- People dossiers leak into Memory → lost on agent reset, not browsable in Obsidian
- User preferences leak into the Wiki → clutters knowledge pages with operational noise
- Session detail gets filed prematurely → vault fills with one-off junk

With the rule:
- World knowledge stays in the Wiki where the user can browse it
- Operational state stays in Memory where the assistant can recall it next session
- Current chatter stays in session

## Sub-rule: synthesis of others' ideas

If the user synthesizes someone else's framework into their own take:
- The **original framework** belongs in `knowledge/` (world concept)
- **The user's specific synthesis / spin / application** belongs in the Wiki under their domain
- Their **operational rule derived from it** ("therefore I will do X") belongs in MEMORY

Example: GBrain analysis →
- World concept (gbrain framework): [[knowledge/GBrain]]
- User's synthesis (the adoption plan): `_system/docs/Adoption Plan.md`
- Operational rule (recommended ship order): rule in MEMORY

## Sub-rule: corrections override

When the user corrects the assistant on something:
- If the correction is about the **world** (e.g., "you got Alex's role wrong"), update the relevant Wiki page
- If the correction is about **assistant behavior** (e.g., "stop signing messages with a sign-off"), update MEMORY
- Both can happen in one correction — file both layers in the same turn

## What this convention replaces

Without this convention, the line is blurry — some operational preferences leak into Wiki pages, and some world facts leak into MEMORY. The convention is a routing decision tree to apply on every ingest.

## Verification

After a session, scan the diffs:
1. ✅ Wiki changes are all world-knowledge updates (facts about people/ventures/projects)
2. ✅ MEMORY changes are all operational (preferences, rules, learnings about tools/communication-style)
3. ✅ No person dossiers in MEMORY
4. ✅ No "User prefers X" rules buried in `people/` or `ventures/` pages

## See also

- [[compiled-truth]] — Wiki page format (only applies to Wiki)
- [[filing-rules]] — once we know it's Wiki, which directory
- [[_system/MEMORY.md]] — current memory file
- [[CLAUDE.md]] — auto-ingest rule (this convention specifies the routing inside that rule)
