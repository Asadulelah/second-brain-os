---
name: brain-dedup
description: Find potential duplicate person pages in this Obsidian vault. Detects similar names, shared email addresses, shared company/venture, shared social handles, and shared aliases. Proposes merges — never auto-merges. Use weekly via /brain-dream --weekly or on demand to prevent split-brain entities. Trigger phrases — "brain dedup", "find duplicate person pages", "check for split-brain entities", "/brain-dedup".
---

# /brain-dedup

> Walk `people/` pages looking for likely duplicates. Three signal types: name similarity, shared identifiers (email, handle), shared affiliations (company, ventures). Reports candidates with confidence scores. User decides which to merge. Read-only on vault content.

## When to fire

- User invokes `/brain-dedup`
- During `/brain-dream --weekly` (after `/brain-tier-audit`)
- Monthly hygiene check
- After bulk import of contacts or new person pages

## Contract

- Read-only on the vault — never modifies pages
- Reports candidates with confidence scores (low / medium / high)
- High-confidence pairs flagged for immediate user attention
- Low-confidence pairs flagged for review only
- No false-merges — strongly prefer false negatives (miss a duplicate) over false positives (merging different people)
- Output written to a journal-style report

## Detection signals

### Signal 1: Name similarity (Levenshtein + phonetic)

- **High confidence:** names differ by 1-2 characters (transposition, misspelling) AND same role/venture context
  - Example: `Alex Chen` vs `Alex Cheng` — likely the same person
- **Medium confidence:** names share surname OR share first name + share a known affiliation
  - Example: `Sam` vs `Sam Rivera` — likely same if both in same venture context
- **Low confidence:** common first names with different surnames (probably different people)

### Signal 2: Shared identifiers

- **High confidence:** same email address in two pages' aliases OR mentioned in body
  - Example: both pages mention `alex@example.com` → same person
- **High confidence:** same social handle in two pages (X handle, IG handle)
- **High confidence:** same phone number

### Signal 3: Shared affiliations + similar names

- **Medium confidence:** both pages reference the same venture in the same role
  - Example: both pages claim to be "CTO of Acme Corp" — only one can be right
- **Medium confidence:** both pages list the same recurring meeting series

### Signal 4: Alias overlap

- **High confidence:** two pages have overlapping `aliases:` frontmatter lists
  - Example: `aliases: ["Alex", "Alex C"]` on page A AND page B → split-brain confirmed

### Signal 5: Cross-reference fingerprint

- **Medium confidence:** two pages are linked-from largely the same set of journal entries
  - If page A and page B both appear in the same 5+ journal entries with overlapping context, suspect same person

## Process

### Phase 1: Build registry

Read all `people/*.md` files:
- Filename (slug)
- Canonical name (first H1)
- Aliases (frontmatter)
- Body content for email/handle/phone extraction (regex)
- In-bound wikilinks (which other pages reference this one)

### Phase 2: Pairwise comparison

For each unordered pair of people pages:

1. Run all 5 signal checks
2. Compute aggregate confidence:
   - Any high-confidence signal → high overall
   - 2+ medium signals → medium overall
   - 1 medium signal → low overall
   - Only weak signals → ignore
3. If confidence is at least low → add to candidates

### Phase 3: Rank candidates

Sort by confidence (high → medium → low). For each candidate:
- Compute "which page is more complete" — longer page, more sources, more recent activity wins as the merge target

### Phase 4: Report (no merging)

Write to `journal/YYYY-MM-DD Dedup Report.md`:

```markdown
---
date: YYYY-MM-DD
type: journal
tags: [dedup, automated-maintenance, brain-dedup]
---

# Dedup Report — YYYY-MM-DD

## Summary
- Person pages scanned: N
- Candidate duplicate pairs: N
- High confidence: N
- Medium confidence: N
- Low confidence: N

## High-confidence pairs (likely same person — review and merge)

### Pair 1: Alex Chen.md ↔ Alex Cheng.md
- **Name similarity:** 1 character difference (transposition)
- **Shared:** company affiliation (Acme Corp), role (CEO/CTO partnership)
- **Confidence:** high
- **Merge target:** `Alex Chen.md` (more complete, 117 lines vs 12 lines)
- **Action:** Merge timeline entries + aliases into Alex Chen page, delete Alex Cheng page, update wikilinks

## Medium-confidence pairs (probably same person — review)

### Pair 2: Sam.md ↔ Sam Rivera.md
- **Name similarity:** shared first name
- **Shared:** company affiliation, founder role
- **Confidence:** medium
- **Suggest:** confirm with user, then merge

## Low-confidence pairs (worth a glance, probably different)

- ...

## Aliases hygiene

Pages missing aliases frontmatter (recommended for dedup robustness):
- people/<Name>.md — suggest adding aliases: ["<nickname>", "<email>"]
- ...
```

### Phase 5: Output

```
✅ Dedup scan complete — 28 person pages scanned

Candidates found: 4
  High confidence: 1 (likely same person — review)
  Medium: 1 (review)
  Low: 2 (probably different)

Report: journal/YYYY-MM-DD Dedup Report.md

⚠️ Action items:
  1. Review Alex Chen ↔ Alex Cheng (high confidence merge candidate)

Aliases hygiene: 14 person pages missing aliases frontmatter — run /brain-compile or add manually.
```

## Merge protocol (when user approves)

User reviews the report. For each merge:

1. Pick the survivor page (the more complete one — usually proposed in report)
2. Merge timeline entries from duplicate into survivor (chronological order)
3. Merge aliases from duplicate into survivor
4. Update all cross-references that pointed to the duplicate (grep + replace `[[duplicate-name]]` → `[[survivor-name]]`)
5. Delete the duplicate file
6. Commit-like log: append to `_system/log.md`: `merge: [duplicate] into [survivor]`

**This skill does NOT perform the merge automatically.** User confirms each merge interactively. Manual is safer than automated for entity identity decisions.

## Edge cases

| Case | Handling |
|---|---|
| Two pages with same name but different surnames | Likely different people — low confidence |
| Common first name (David, Sarah) across very different contexts | Different people — ignore |
| Same email on two pages, different names | High confidence — same person with name change OR data error |
| Pages with no aliases AND no body identifiers | Compare on name + context only — accept lower precision |
| Person and their brand/persona (e.g., the user and their content brand) | Different entities — brand is `ventures/solo/`, person is `me/`. Should not flag. |

## Anti-patterns

- ❌ Auto-merging without user confirmation
- ❌ Treating common-name collisions as duplicates (David Liu at company A vs David Liu at company B — different people)
- ❌ Ignoring aliases frontmatter when present
- ❌ Generating false positives (better to miss duplicates than merge wrong)
- ❌ Modifying pages in this skill — read-only

## Tools used

- Read — load all person pages + frontmatter
- Glob — enumerate `people/*.md`
- Grep — extract email/handle/phone patterns from page bodies
- Write — produce dedup report in journal/

## See also

- `_system/conventions/aliases.md` — alias frontmatter spec (relevant for hygiene + dedup robustness)
- `_system/conventions/notability-gate.md` — preventing duplicate creation in the first place
- `/brain-compile` — fires on the survivor page after merge to fold in timeline + aliases
- `/brain-dream --weekly` invokes this after tier-audit
