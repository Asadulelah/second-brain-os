---
name: brain-tier-audit
description: Scan entity pages in this Obsidian vault to find tier mismatches per _system/conventions/tiered-enrichment.md. Reports under-enriched stubs (3+ mentions but skeleton page) and over-enriched bloat (1 mention but full Tier-1 page). Report only — never auto-fixes. Use weekly via /brain-dream --weekly or on demand. Trigger phrases — "brain tier-audit", "audit enrichment tiers", "find under-enriched people", "/brain-tier-audit".
---

# /brain-tier-audit

> Walk every entity page (people/, ventures/), count how many times each entity is mentioned across the vault, compare to the page's enrichment depth, and report mismatches. Read-only. Surfaces both under-enriched (deserves more) and over-enriched (deserves less).

## When to fire

- User invokes `/brain-tier-audit`
- User says "audit tiers" / "find under-enriched people" / "find pages that shouldn't exist"
- During `/brain-dream --weekly` (Phase 6)
- Monthly check for vault hygiene

**Read-only.** Never modifies pages. Outputs a report. User decides what to act on.

## Contract

- Every entity page is checked against its mention count
- Tier classification follows `_system/conventions/tiered-enrichment.md`
- Report distinguishes under-enriched (need more) vs over-enriched (need less)
- Each finding includes mention count + locations
- Edge cases (stubs vs full pages) classified by content length + structural markers
- No false positives for known-T1 entities (active collaborators, warm leads, close contacts)

## Tier definitions (per convention)

| Tier | Page depth signal | Mention count threshold |
|---|---|---|
| **T3 — Stub** | <300 words, frontmatter + 1-2 sections, no Assessment/Trajectory | 1-2 mentions OK; 3+ = under-enriched |
| **T2 — Substantive** | 300-1000 words, State + What They Believe / What They're Building, minimal Assessment | 3-7 mentions OK; 8+ = under-enriched; 1 mention = over-enriched |
| **T1 — Full** | 1000+ words, all sections (State, Beliefs, Communication, Assessment, Trajectory, Timeline), source-type labels | 8+ mentions OK or has meeting attended; 1 mention = over-enriched (bloat) |

## Process

### Phase 1: Enumerate entity pages

```
Scope:
  - people/*.md (excluding README.md)
  - ventures/**/*.md (excluding README.md, *.bak.md, INDEX files)

Exclude:
  - Pages tagged status: archived
  - Backup files (*.bak.md)
  - Files inside _system/, raw/, summaries/
```

### Phase 2: Classify each page's CURRENT tier

For each entity page:

1. Read the page
2. Count word count of synthesis zone (above `---`, or whole page if legacy format)
3. Detect structural markers:
   - Has Assessment section? (T1 signal)
   - Has Trajectory section? (T1 signal)
   - Has source-type labels (observed/self-described/inferred)? (T1 signal)
   - Has What They Believe with multiple claims? (T2+ signal)
   - Has only State + frontmatter? (T3 signal)
4. Classify as T1 / T2 / T3 based on combined depth signal

### Phase 3: Count mentions across the vault

For each entity page:

1. Build a list of name + aliases (from frontmatter `aliases:` field)
2. Grep across journal/, ventures/, knowledge/, summaries/ for each variant
3. Count distinct source pages (not raw mention count — one journal entry mentioning the entity 5 times = 1 mention)
4. **Exclude:**
   - Self-mentions (the entity's own page)
   - Mentions inside `raw/` (immutable source, doesn't count)
   - Mentions inside `_system/` (operational, doesn't count)
   - Mentions in `.bak.md` backup files

### Phase 4: Apply tier rules

For each entity:

| Current tier | Mention count | Verdict |
|---|---|---|
| T3 | 1-2 | ✅ Correctly stub |
| T3 | 3-7 | ⚠️ **Under-enriched** — should be T2 |
| T3 | 8+ | ⚠️⚠️ **Severely under-enriched** — should be T1 |
| T2 | 1 | ⚠️ **Over-enriched** — should be T3 (or archive) |
| T2 | 2 | ⚠️ Borderline — consider downgrade or wait |
| T2 | 3-7 | ✅ Correctly substantive |
| T2 | 8+ | ⚠️ Under-enriched — promote to T1 |
| T1 | 1 | ⚠️⚠️ **Severely over-enriched** — should be T3 (bloat) |
| T1 | 2-4 | ⚠️ Over-enriched — consider downgrade |
| T1 | 5-7 | ⚠️ Borderline — likely OK if meeting attended |
| T1 | 8+ | ✅ Correctly full |
| Any | Meeting attended (per journal grep) | ✅ Any tier valid (meeting attendance auto-qualifies T1) |

### Phase 5: Report

Group findings by severity:

```
Tier Audit Report — YYYY-MM-DD

=== UNDER-ENRICHED (should be larger) ===

⚠️⚠️ Severely under-enriched (T3 stub with 8+ mentions):
- people/<Name>.md — current: stub (180 words), mentions: 12 in journal/
  Top sources: journal/2026-05-11..., journal/2026-04-28..., ventures/...
  Recommendation: promote to T1 via /brain-compile + research

⚠️ Under-enriched (T3 with 3-7 mentions):
- people/<Name>.md — current: stub (220 words), mentions: 4
  Recommendation: promote to T2 — web/social check

=== OVER-ENRICHED (should be smaller or archived) ===

⚠️⚠️ Severely over-enriched (T1 with 1 mention):
- people/<Name>.md — current: full page (1400 words), mentions: 1 (in journal/2026-04-12)
  Recommendation: downgrade to T3 stub OR archive if no relationship

⚠️ Over-enriched (T2 with 1 mention):
- people/<Name>.md — current: substantive (450 words), mentions: 1
  Recommendation: downgrade or wait for second mention

=== CORRECTLY TIERED ===

✅ N pages correctly tiered (no action needed)

=== FLAGS ===

⚠️ Pages with no aliases frontmatter but ambiguous name:
- people/Jordan.md — common name; suggest aliases: ["Jordan Smith", "@jordan-handle"]
```

## Reference inputs

- `_system/conventions/tiered-enrichment.md` — tier definitions
- `_system/conventions/aliases.md` — alias expansion for grep
- `_system/conventions/notability-gate.md` — to know if archiving is the right call
- All entity pages (people/, ventures/)
- All source pages (journal/, knowledge/, summaries/) for mention counts

## Output format

```
✅ Tier Audit Complete — <date>

Pages scanned: <N>
Verdicts:
  ✅ Correctly tiered: <N>
  ⚠️ Under-enriched: <N> (severe: <X>, regular: <Y>)
  ⚠️ Over-enriched: <N> (severe: <X>, regular: <Y>)
  ⚠️ Other flags: <N>

Recommended next actions:
- Run /brain-compile on <N> under-enriched pages to promote
- Review <N> over-enriched pages for downgrade or archive
- Add aliases frontmatter to <N> pages (see Flags section)

[Full report saved to journal/<DATE> Tier Audit Report.md]
```

Optional: save the full report to `journal/YYYY-MM-DD Tier Audit Report.md` for future reference.

## Anti-patterns

- ❌ Auto-fixing tier mismatches — report only, user decides
- ❌ Counting raw mention occurrences instead of distinct source pages (5 mentions in 1 file = 1 mention)
- ❌ Counting self-mentions or backup files
- ❌ Counting `raw/` or `_system/` mentions (those don't drive tier decisions)
- ❌ Classifying pages without checking for meeting attendance (meeting auto-qualifies T1)
- ❌ Reporting too many false positives (>10% rate = tune thresholds)

## Tools used

- Read — load entity pages + conventions
- Glob — enumerate people/, ventures/
- Grep — count mentions across vault
- Write — optionally save report to journal/

## See also

- [[_system/conventions/tiered-enrichment]] — tier spec
- [[_system/conventions/notability-gate]] — for archive decisions
- [[_system/conventions/aliases]] — for grep expansion
- `/brain-compile` — fires this for promote actions
- `/brain-dream --weekly` — invokes this as Phase 6
