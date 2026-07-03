---
name: brain-source-fix
description: Find unsourced factual claims in target wiki pages and append [Source: ...] citations. For each unsourced claim, asks the user (or auto-derives from journal entries) and appends inline citation per _system/conventions/source-attribution.md. Ported from Garry Tan's gbrain citation-fixer skill. Use when refactoring legacy pages, doing periodic citation audits, or as part of /brain-dream --full. Trigger phrases — "brain source-fix", "audit citations on this page", "fix unsourced claims", "/brain-source-fix <page|dir>".
---

# /brain-source-fix

> Scan a page (or directory) for synthesis claims missing `[Source: ...]` citations. For each, attempt to derive the source from journal entries, MEMORY rules, or existing context — and ask the user when ambiguous. Append citations inline. Lighter than `/brain-compile` (only fixes citations, doesn't restructure).

## When to fire

- User invokes `/brain-source-fix <page|dir>` (manual)
- User says "audit citations on <page>" / "find unsourced claims"
- During `/brain-dream --full` cycle (after lint, before tier-audit)
- After a bulk import that brought in unsourced content

**Default scope:** the specified page or directory. If no scope, asks user.

## Contract

This skill guarantees:
- Every factual claim in the target gets a `[Source: ...]` citation OR is removed per user instruction
- Citation format matches `_system/conventions/source-attribution.md`
- Existing citations are preserved (not overwritten)
- Source precedence respected: User's direct statement > compiled truth > timeline > external
- Conflicting sources flagged inline, not silently resolved
- Original page backed up to `<page>.bak.md` before modification

## Process

### Phase 1: Identify scope + load conventions

```
Input: <page> OR <directory>
  - Single page: process it alone
  - Directory: enumerate all .md files, process each sequentially

Load:
  - _system/conventions/source-attribution.md (citation format)
  - _system/conventions/source-types.md (if any claims need observed/self-described/inferred labels)
```

### Phase 2: Parse claims

For each page in scope:

1. Read the page
2. **Identify the synthesis zone** (everything above `---`, OR the whole page if legacy)
3. **Skip** these elements (they don't need citations):
   - Headings (`#`, `##`, etc.)
   - Wikilinks (`[[X]]`)
   - List labels ("Open Threads:", "State:")
   - Code blocks / fenced quotes
   - Structural separators (`---`, `> `, etc.)
4. **Find claims** in remaining prose / bullet lines:
   - Sentences that assert a fact (someone is X, did Y, has Z)
   - Bullet points stating something verifiable
   - Quoted statements (need attribution)

### Phase 3: Classify each claim

For each claim found:
- **Already cited:** has `[Source: ...]` directly after or on the line → skip
- **Sourceable from context:** find source in same paragraph, frontmatter `source:` field, nearby timeline entry → use that
- **Sourceable from elsewhere:** grep journal/ for the claim text or related context → use the closest match
- **Sourceable from MEMORY:** check `_system/MEMORY.md` for matching rule → use MEMORY citation
- **Unsourceable:** flag for user input

### Phase 4: For each unsourceable claim, ask user

Use `AskUserQuestion` (or interactive prompt) with options:

```
Unsourced claim found in <page>:

  "Entity is in a pivotal growth stage"

Where did this come from?
  A) User chat — paste date and brief context
  B) A meeting — which meeting (date + title)?
  C) An external source — paste URL or attribution
  D) Remove this claim (no source available)
  E) Skip for now (leave unsourced, flag in report)
```

User responds → build citation.

### Phase 5: Append citations inline

For each claim with a derived source:

1. Locate the exact line in the page
2. Append `  [Source: ...]` at the end of the line (two-space prefix per markdown convention)
3. Preserve existing line content
4. Don't insert line breaks

**For conflicting sources** (e.g., two facts about same field with different sources):
```
Role: CEO of Acme Corp  [Source: company website, 2026-04-12]
      | CTO per LinkedIn  [Source: linkedin.com/in/x, 2026-04-08]
      ⚠️ Conflict — verify next interaction
```

### Phase 6: Backup + write

1. Move original to `<page>.bak.md` (unless already backed up by `/brain-compile`)
2. Write the page with citations added
3. Verify file opens correctly

### Phase 7: Report

```
Source-fix complete — scope: <page>

Claims found: N
Already cited: N (skipped)
Sourced from context: N (auto-derived)
Sourced from journal/MEMORY: N (auto-derived)
User-provided: N
Removed at user request: N
Remaining unsourced (flagged): N

Modified: <page> (+N citations)
```

## Special handling

| Case | Handling |
|---|---|
| Claim has partial citation `[Source: User]` (no date) | Flag as undated → ask user for date |
| Claim has vague source `[Source: somewhere in chat]` | Flag → ask for date and context |
| Multiple claims in one sentence | Cite at sentence end with all sources comma-separated |
| Direct quote (in `"..."`) | Always require source — quotes without attribution are forbidden |
| Speculative language ("possibly", "might be") | Still needs source — say where you got the speculation from |
| Future statement ("Graduation September 2026") | Cite the source of the future commitment ("[Source: User chat, YYYY-MM-DD]") |

## Reference inputs

- The target page
- `_system/conventions/source-attribution.md` — citation format spec
- `_system/conventions/source-types.md` — for belief claims (if scope includes person page)
- `_system/MEMORY.md` — for context-derivable claims
- `journal/` directory — for grep-based source derivation
- Source: `_system/external/gbrain/skills/citation-fixer/SKILL.md` (gbrain version, adapted)

## Output format

```
✅ Source-fix complete — people/<Name>.md

Citations added: N
Auto-derived from context: N
Auto-derived from journal/MEMORY: N
User-provided: N
Removed at user request: N
Unresolved (left unsourced, flagged): N

Backup: people/<Name>.bak.md
Diff: <N lines added>
```

## Anti-patterns

- ❌ Guessing sources from training data — always ask the user when unsure
- ❌ Using `[Source: brain]` or `[Source: synthesis]` as a catch-all — that's not a source, that's an admission of laziness
- ❌ Silently picking one of two conflicting sources — surface the conflict
- ❌ Adding citations to wikilinks (they're not claims) or headings (they're structure)
- ❌ Removing claims without user consent (claim removal needs explicit instruction)
- ❌ Re-citing already-cited claims (idempotency)

## Tools used

- Read — load target page + conventions + MEMORY + journal context
- Grep — search journal/ and other pages for source derivation
- Edit — append citations inline
- AskUserQuestion — for unresolved cases

## See also

- [[_system/conventions/source-attribution]] — Iron Law spec
- [[_system/conventions/source-types]] — orthogonal label rule for person-page beliefs
- `/brain-compile` — full refactor (includes source-fix as one phase)
- `/brain-dream --full` — invokes this on top-10 stale pages
- Source: gbrain's `citation-fixer/SKILL.md` at `_system/external/gbrain/skills/citation-fixer/SKILL.md`
