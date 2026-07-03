# Architecture

> The technical deep-dive: what the system actually is, layer by layer, and why the design decisions fall where they do. For the friendly version, read the [README](../README.md); to just get running, read [INSTALL](INSTALL.md).
>
> Built on the Second Brain framework by [Asadulelah](https://github.com/Asadulelah).

## The one-sentence thesis

A second brain fails not at *storage* but at *retrieval-at-the-right-moment*; this system solves retrieval by making the storage format agent-legible (conventions), the context injection attentional (the router), and the maintenance autonomous (the dream cycle).

## The five layers

The brain is a **stack, not a repo**. Only one layer is git-cloneable; the rest are configuration, dependencies, and state:

| # | Layer | What it is | Ships as |
|---|---|---|---|
| 1 | **Vault** | The Markdown wiki: conventions, `CLAUDE.md`, folder scaffold | `template-vault/` — cloneable |
| 2 | **Claude Code config** | `settings.json`: hooks, permissions, env | `plugin/settings.template.json` — merged by the user |
| 3 | **Plugins + MCPs** | claude-mem, integrations | Declared in `manifest.json`, installed not committed |
| 4 | **Infra** | Dashboards, schedulers, always-on hosts | Optional add-ons, out of scope for core |
| 5 | **Memory state** | Attention scores, session pool, realtime memory | Empty in the template; `.gitignore`d in a live brain |

Two consequences worth internalizing:

- **Two repos per instance.** The framework repo (this one — the user pulls updates from it) and the user's private vault repo (their data; never flows back). One-repo designs recreate the PII-backflow problem and fight the user's files on every update.
- **The installer must wire two targets:** the plugin (skills) and the user-level `~/.claude/settings.json` (the hook engine). Skills travel with the plugin; hooks live at user level because they must fire for every session against the vault.

## The memory model (five kinds of memory, deliberately separate)

| Kind | Lives in | Written by | Analogy |
|---|---|---|---|
| Session capture | claude-mem (optional plugin) | automatic | episodic memory |
| Realtime working memory | `project_memory.json` | `pool-auto-update.py`, every prompt | scratchpad |
| Session pool | `~/.claude/pool/*.jsonl` | `pool-extractor.py` on Stop | short-term consolidation |
| Curated long-term | `_system/MEMORY.md` | the assistant, deliberately | semantic memory |
| The wiki itself | vault pages | the assistant, per conventions | the world model |

The separation is a convention (`brain-vs-memory.md`): world-facts go on wiki pages, operational state goes in MEMORY, current-task state stays in session. Mixing layers is how brains rot — MEMORY bloats into an archive, or facts get trapped in session logs where retrieval can't reach them.

## The attentional context router (the crown jewel)

`plugin/hooks/context-router-v2.py`, fired on `UserPromptSubmit`. Implements working-memory dynamics over the vault:

- **Scoring:** every tracked doc gets an attention score. Keyword/topic hits from the current prompt reset a file's score to 1.0; related files get a **co-activation boost**; everything else **decays** per turn (decay rate configurable per category).
- **Tiers:** score ≥ 0.8 → **HOT** (full file injected into context) · 0.25–0.8 → **WARM** (header/first-25-lines only) · < 0.25 → **COLD** (evicted).
- **Pinned topology:** files marked as structural (the operating manual, conventions index) never fall below WARM.
- **Persistence:** scores survive across turns in `.claude/attn_state.json` — attention has momentum, like the real thing.

The effect: the assistant's context always contains *what the current conversation is about* at full resolution, *what it might swing to* at header resolution, and nothing else. This is the difference between a brain and a folder full of notes stapled to every prompt — token budgets stay sane no matter how large the vault grows.

Keyword→file mappings are configurable via `keywords.json` (project-local `.claude/keywords.json` overrides global `~/.claude/keywords.json`); the docs root resolves from `CONTEXT_DOCS_ROOT` env → project `.claude/` → global, in that priority order.

## The session pool (crash-proof continuity)

Three hooks around the router make sessions continuous instead of amnesiac:

- `pool-loader.py` (`SessionStart`) — hydrates the new session with persisted recent state.
- `pool-auto-update.py` (`UserPromptSubmit`) — appends decisions/projects/corrections to the realtime store as they happen, not at session end (surviving crashes and force-quits).
- `pool-extractor.py` (`Stop`) — consolidates session state into `~/.claude/pool/*.jsonl`; a cleanup pass keeps the realtime store at 5–7 high-signal entries instead of an ever-growing log.

All four hooks are **optional enhancements** — the vault + conventions work without them; you lose auto-continuity, not correctness. `/brain-doctor` reports their wiring state.

## Conventions: the storage format as an operating system

Nine rules in `template-vault/_system/conventions/`, enforced by the assistant on every write. The load-bearing ones:

- **compiled-truth** — every entity page is two zones split by `---`: above is *synthesis* (rewritten freely as understanding improves), below is an *append-only timeline* of dated evidence. Reads like a briefing, audits like a ledger.
- **source-attribution** — every factual claim cites `[Source: who, channel, date]`. An uncited claim is a rumor.
- **back-linking** — every entity mention creates a link *from* that entity's page back to the mention. An unlinked mention is invisible to retrieval — a broken brain.
- **filing-rules / notability-gate / tiered-enrichment** — a MECE decision tree for where pages go, a bar for what deserves a page at all, and a budget for how much enrichment a page earns (1–2 mentions = stub; recurring = full page). These three keep the graph high-signal instead of sprawling.

The insight: these exist so an **agent** can trust and update the store mechanically — human readability falls out as a side effect.

## Onboarding as personalization (no placeholders)

`/onboard` replaces find-and-replace-the-template with a progressive interview: name the assistant → who the user is → seed ventures/people → tone preferences. It then *generates* the foundation — root `CLAUDE.md` (the operating manual Claude Code auto-loads), `_system/SOUL.md`, `me/<User>.md`, the scaffold — and writes `.claude/.onboarded` as the done-state marker that flips the brain to normal auto-ingest operation. The `.onboarded` marker is what prevents re-onboarding loops; its absence on a fresh vault is what triggers the offer to onboard.

## The dream cycle (autonomous maintenance)

`/brain-dream` chains the maintenance skills into light (~5 min: lint, back-link sweep, health) / weekly (~15 min: + synthesis, reconciliation, tier audit) / full (~30 min: + citation fixing, typed-graph extraction) passes, writing a report to `journal/` and state to `.claude/`. Failures degrade per-phase, never whole-cycle; missing optional subskills are skipped and reported. Wire it to a scheduler if you have one; run it manually if you don't.

`/brain-graph-extract` deserves a note: it lifts the implicit wikilink graph into **typed edges** (`works_at`, `founded`, `advises`, ...) in `_system/graph.json` — answering relational queries plain links can't ("who works at Acme?").

## Graceful degradation (the packaging law)

Dependency tiers, checked by `/brain-doctor` against `manifest.json`:

```
CORE      Claude Code + this plugin          → the brain works
ENHANCE   claude-mem, the 4 hooks            → auto-continuity + attention
EXTEND    MCPs, research engine, schedulers  → reach + autonomy
```

The doctor never auto-installs (settings are a hard ask-first boundary); it diagnoses and hands the user the exact command. Design rule for contributors: **any new capability must state what happens when its dependency is absent**, and that fallback must be functional, not an error.

---

*Built on the Second Brain framework by Asadulelah. Lineage and prior art in [LINEAGE.md](LINEAGE.md).*
