# MEMORY.md — {{assistant_name}}'s Long-Term Memory

> Operational state. Survives session restarts. **Not** world knowledge (that goes in the wiki). Only: preferences, rules, learned corrections, tool config, and active priorities.
>
> Read this at session start. Update when something changes.

---

## Active Priorities

*(What {{user_name}} is working on right now. Rewrite this section as priorities shift.)*

<!-- Add active priorities here during onboarding and update as they evolve -->

---

## Rules and Preferences

*(How {{assistant_name}} should behave with {{user_name}}. Add as feedback accumulates.)*

### Communication
<!-- e.g., "User prefers concise responses — no trailing summaries" -->

### Tone and Register
<!-- e.g., "Casual register for peers, formal for senior contacts" -->

### Filing and Writing
<!-- e.g., "Always distill, never dump raw text" -->

### Vault Hygiene
<!-- e.g., "Don't create new top-level directories without checking with the user" -->

---

## Learned Corrections

*(Things {{assistant_name}} got wrong and the user corrected. Prevents repeat mistakes.)*

<!-- Format: "Rule: [the corrected behavior]. Reason: [what went wrong]." -->

---

## Key Relationships

*(Quick-reference context for the most important people in {{user_name}}'s world. Full dossiers are in `people/`. This is the cheat sheet — who matters and one-line context.)*

<!-- Format: "[[Person Name]] — one-line context (relationship + status)" -->

---

## Active Ventures (Quick Reference)

*(Status snapshot for active ventures. Full detail in `ventures/`. Update as status changes.)*

<!-- Format: "[[Venture Name]] — status: active/paused/dead. One-line note." -->

---

## Tool and Setup Notes

*(Operational notes about the assistant's tooling, installed plugins, known limitations.)*

<!-- e.g., "claude-mem installed and working", "browser-harness connected to X browser" -->

---

## Open Threads for Next Session

*(Things to pick up at the start of the next session.)*

<!-- Add items here at end of session; remove when resolved -->

---

*Last updated: {{last_updated_date}}*
*Built on Second Brain OS — framework conventions at `_system/conventions/`*
