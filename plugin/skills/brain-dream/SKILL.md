---
name: brain-dream
description: Master orchestrator that chains existing /obsidian-* commands and new /brain-* commands into a single maintenance cycle. Mirrors gbrain's nightly dream cycle adapted to manual + scheduled triggers since Claude Code isn't always-on. Variants — /brain-dream --light (5 min nightly), /brain-dream --weekly (15 min Sunday), /brain-dream --full (30 min on-demand). Writes a per-run report to journal/ and updates state. Use to maintain vault hygiene without manually invoking each subskill. Trigger phrases — "brain dream", "run dream cycle", "do the maintenance pass", "/brain-dream [--light|--weekly|--full]".
---

# /brain-dream

> Run the vault maintenance cycle. Three variants by cost. State persisted between runs. Report written to journal/. The user's manual equivalent of gbrain's autonomous overnight dream cycle.

## Variants

| Variant | Phases | Time | When |
|---|---|---|---|
| `--light` (default if no flag) | lint + back-link sweep + health | ~5 min | Nightly via `/schedule "every night at 2am" /brain-dream --light` |
| `--weekly` | adds emerge + synthesize + reconcile + tier-audit + recap | ~15 min | Sundays via `/schedule "every Sunday 9am" /brain-dream --weekly` |
| `--full` | adds source-fix on top-10 stale pages + graph-extract | ~30 min | On-demand after heavy ingest days |

## Phase chain

```
/brain-dream --light:
  Phase 1: /brain-lint-frontmatter          (audit YAML, --fix only on safe-mechanical)
  Phase 2: /brain-back-link-sweep --since 14d
  Phase 7: /obsidian-health                  (orphans + dead links + general lint)
  Phase 9: write report + update state

/brain-dream --weekly:
  Phase 1: /brain-lint-frontmatter
  Phase 2: /brain-back-link-sweep --since 14d
  Phase 3: /obsidian-synthesize              (auto-write synthesis pages from patterns)
  Phase 4: /obsidian-emerge                  (surface unnamed recurring themes)
  Phase 5: /obsidian-reconcile               (find + resolve contradictions)
  Phase 6: /brain-tier-audit                 (under/over-enriched report)
  Phase 7: /obsidian-health
  Phase 8: /obsidian-recap today             (summarize the dream cycle itself)
  Phase 9: write report + update state

/brain-dream --full:
  All --weekly phases PLUS:
  Phase 6.5: /brain-source-fix on top-10 stale pages by last-modified-date in synthesis zone
  Phase 7.5: /brain-graph-extract            (refresh _system/graph.json typed edges)
```

(gbrain's `sync` and `embed` phases don't apply — Obsidian vault is the source of truth, no separate index. gbrain's `recompute_emotional_weight` is gbrain-specific.)

## When to fire

- User invokes `/brain-dream [variant]`
- Scheduled cron firing via `/schedule`
- User says "run the dream cycle" / "maintenance pass" / "do the nightly"
- After a big multi-page edit session (likely user-prompted, not automatic)

**Single-instance lock:** if the state file shows a run in-progress (`status: running`), refuse to fire a second cycle until the first completes or 30 min timeout. Prevents double-fire when both cron and manual invocation collide.

## Contract

This skill guarantees:
- Variant determines exact phase set — no surprise phases
- Each phase runs sequentially (not parallel — phases depend on each other's outputs)
- A phase failure doesn't kill the cycle; remaining phases still run; failure logged in report
- State persisted to `.claude/brain-dream.state.json` after EACH phase (durability — partial progress on crash)
- Report written to `journal/YYYY-MM-DD Dream Cycle Report.md` even if some phases failed
- Per-run state appended to a rolling log `.claude/brain-dream.history.jsonl`
- No phase modifies user-facing content beyond what its underlying skill is allowed to modify
- Quiet on success — verbose only on issues found

## Process

### Phase 0: Pre-flight

1. Check `.claude/brain-dream.state.json` — if `status: running` and `started_at` < 30 min ago, abort with "already running" message
2. Parse variant flag — default to `--light`
3. Mark state `status: running`, `started_at: <now>`, `variant: <variant>`
4. Read `_system/conventions/` for context (load convention rules)
5. Read recent state from prior runs (last 7 days) — used to skip phases that already ran clean

### Phase 1: Lint frontmatter

- Invoke `/brain-lint-frontmatter` (read-only audit mode for `--light`, `--fix` for `--weekly`/`--full`)
- Capture: files scanned, errors found, fixes applied, remaining manual
- Log to state

### Phase 2: Back-link sweep

- Invoke `/brain-back-link-sweep --since 14d`
- Capture: source pages scanned, missing back-links added, unresolved
- Log to state

### Phase 3: Synthesize (weekly+ only)

- Invoke `/obsidian-synthesize`
- Capture: synthesis pages written, themes detected

### Phase 4: Patterns / Emerge (weekly+ only)

- Invoke `/obsidian-emerge`
- Capture: unnamed patterns surfaced, recurring themes identified

### Phase 5: Reconcile (weekly+ only)

- Invoke `/obsidian-reconcile`
- Capture: contradictions found, resolutions proposed

### Phase 6: Tier audit (weekly+ only)

- Invoke `/brain-tier-audit`
- Capture: under-enriched count, over-enriched count, recommendations

### Phase 6.5: Source-fix on stale (full only)

- Identify top-10 entity pages by (synthesis-zone last-modified > 60 days OR `last assessed` field > 60 days)
- Invoke `/brain-source-fix <page>` on each
- Capture: pages audited, citations added, manual reviews needed

### Phase 7: Health

- Invoke `/obsidian-health`
- Capture: orphans, dead links, stale claims, missing cross-refs

### Phase 7.5: Graph extract (full only)

- Invoke `/brain-graph-extract`
- Capture: typed edges written to `_system/graph.json`, entity coverage

### Phase 8: Recap (weekly+ only)

- Invoke `/obsidian-recap today` to summarize the cycle itself

### Phase 9: Report + state finalization

1. Write `journal/YYYY-MM-DD Dream Cycle Report.md` with per-phase summary
2. Update `.claude/brain-dream.state.json`:
   ```json
   {
     "last_run_at": "<iso>",
     "last_variant": "<variant>",
     "last_phase_results": [...],
     "total_duration_s": <N>,
     "status": "complete",
     "report_path": "journal/<DATE> Dream Cycle Report.md"
   }
   ```
3. Append history entry to `.claude/brain-dream.history.jsonl`

## State file schema

```json
{
  "last_run_at": "2026-05-19T02:00:14Z",
  "last_variant": "light",
  "last_phase_results": [
    {"phase": "lint", "status": "ok", "duration_s": 8, "issues_found": 0, "fixed": 0},
    {"phase": "back-link-sweep", "status": "ok", "duration_s": 42, "issues_found": 3, "fixed": 3},
    {"phase": "health", "status": "warning", "duration_s": 12, "issues_found": 2, "details": "2 orphan pages flagged for review"}
  ],
  "total_duration_s": 287,
  "status": "complete",
  "report_path": "journal/2026-05-19 Dream Cycle Report.md",
  "next_scheduled": "2026-05-20T02:00:00Z"
}
```

## Report template (`journal/YYYY-MM-DD Dream Cycle Report.md`)

```markdown
---
date: YYYY-MM-DD
type: journal
tags: [dream-cycle, automated-maintenance, brain-dream]
status: complete | partial-failure
---

# Dream Cycle Report — YYYY-MM-DD (variant: light|weekly|full)

## Summary
- **Phases run:** N of N
- **Total duration:** Xs (~Y min)
- **Issues found:** N (auto-fixed: A, outstanding: O)
- **Status:** Clean | Action items below

## Per-phase

### Phase 1: Lint frontmatter
- Files scanned: N
- Errors: critical=N, structural=N, semantic=N, hygiene=N
- Auto-fixed: N (with .bak backups)
- Manual review: <list>

### Phase 2: Back-link sweep
- Source pages scanned: N
- Missing back-links added: N
- Unresolved (target page missing): <list>

[... per phase ...]

## Outstanding items requiring user attention

- <list of things the orchestrator couldn't auto-resolve>

## Recommended next actions

- Run `/brain-compile <page>` on N under-enriched pages
- Review N orphan pages flagged in Phase 7
- ...

---

## Timeline

- **YYYY-MM-DD HH:MM** | Cycle complete (variant: <X>) — <N> issues found, <N> auto-fixed.  [Source: automated dream cycle]
```

## Edge cases

| Case | Handling |
|---|---|
| An `/obsidian-*` subskill is not installed | **Skip that phase gracefully** — the `/obsidian-*` commands come from a separate Obsidian skills plugin and are optional. Note "phase skipped (skill not installed)" in the report; never fail the cycle over a missing optional subskill. The `/brain-*` phases alone are a complete light cycle. |
| One phase fails | Log error in state, continue remaining phases, mark cycle as `partial-failure` in report |
| All phases fail | Mark state `status: failed`, write report with failure summary, alert in next briefing |
| Cron-fire while manual run in-progress | Abort with "already running" — first run wins |
| State file corrupted | Re-init with `status: idle`, log corruption to history.jsonl |
| No issues found across all phases | Report still written, summary says "Clean — no action needed" — quiet success |

## Reference inputs

- `_system/conventions/` — all 9 conventions inform the underlying skills
- Existing `/obsidian-*` skills — invoke as subskills (they own their own logic)
- Existing `/brain-*` skills — invoke as subskills (compile, back-link-sweep, source-fix, tier-audit, lint-frontmatter, graph-extract)

## Output format (after run)

```
✅ /brain-dream --light complete

Duration: 4 min 47 s
Phases: 3/3 OK
Issues found: 5 (fixed: 3, outstanding: 2)

Report: journal/YYYY-MM-DD Dream Cycle Report.md

Outstanding:
- 2 orphan pages flagged for review (see report Phase 7)
```

## Anti-patterns

- ❌ Running phases in parallel (they depend on each other's outputs)
- ❌ Failing the whole cycle on first phase failure (continue, log, report)
- ❌ Skipping the state-file write between phases (no durability on crash)
- ❌ Writing a noisy report when nothing happened (quiet on success)
- ❌ Firing during an in-progress run (single-instance lock)
- ❌ Modifying convention files or source pages directly — orchestrator only calls subskills, never edits content

## Tools used

- Read — load conventions, state file, journal context
- Skill (via Skill tool invocation) — call subskills `/brain-*` and `/obsidian-*`
- Write — produce state file + journal report
- Bash — for sleep/timing if needed, state file lock

## See also

- All 9 `_system/conventions/*.md` — the rules underlying every phase
- `_system/external/gbrain/skills/maintain/SKILL.md` — gbrain's dream cycle for comparison
