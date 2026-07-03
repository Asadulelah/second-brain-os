---
name: brain-lint-frontmatter
description: Validate YAML frontmatter integrity across all wiki pages in this Obsidian vault. Detects missing ---, nested-quote escape errors, slug-name mismatches, type field violations, null bytes, and date format issues. Auto-fixes mechanical errors with .bak backup; reports semantic issues for user review. Ported from Garry Tan's gbrain frontmatter-guard skill. Use during /brain-dream maintenance or as standalone audit. Trigger phrases — "brain lint frontmatter", "audit frontmatter", "fix yaml errors", "/brain-lint-frontmatter [--fix]".
---

# /brain-lint-frontmatter

> Walk every .md file in the wiki, parse the YAML frontmatter, classify any errors, auto-fix what's safe to auto-fix, report the rest for human review. Read-mostly by default; `--fix` enables mutations with `.bak` backups.

## When to fire

- User invokes `/brain-lint-frontmatter` (audit mode, no changes)
- User invokes `/brain-lint-frontmatter --fix` (auto-fix safe errors)
- During `/brain-dream` (Phase 1: lint)
- After bulk import or migration
- When Obsidian complains about a specific page parsing

**Default scope:** all `.md` files in the wiki (excluding `raw/`, `_system/external/`, `.bak.md`).

## Contract

- Every .md file's frontmatter parsed for compliance
- 7 validation classes checked per gbrain frontmatter-guard
- `--fix` mode only repairs mechanical errors with `.bak` backup
- Semantic errors (missing type, wrong category) reported for user review, never auto-changed
- No file modified without backup
- Idempotent — re-running on a clean vault is a no-op

## Validation classes

### Class 1: Missing or malformed `---` delimiters
- Frontmatter must start at line 1 with `---`
- Must close with `---` before content
- **Auto-fixable** if delimiters are obviously missing on a file that has YAML-looking content at the top

### Class 2: YAML parse errors
- Unescaped quotes inside quoted strings
- Tabs instead of spaces
- Indentation inconsistency
- Invalid characters (null bytes, BOM)
- **Auto-fixable** for trivial cases (BOM removal, null byte strip); **manual** for structural errors

### Class 3: Required fields missing
- `date:` (YYYY-MM-DD format)
- `type:` (must match enum: identity | person | venture | system | strategy | knowledge | journal | summary | convention)
- `tags:` (list, even if single tag)
- **Auto-fixable** if can derive from path (e.g., file in `people/` → `type: person`); **manual** for ambiguous

### Class 4: Date format violations
- Must be `YYYY-MM-DD` (no slashes, no relative dates like "today")
- Must be a valid calendar date
- **Auto-fixable** if value is parseable (e.g., `2026/05/18` → `2026-05-18`)

### Class 5: Type field violations
- Value must match the enum
- Common errors: `type: people` (should be `person`), `type: project` (should be `system` or use venture nesting)
- **Manual** — user picks the right type

### Class 6: Slug-name mismatch
- File name vs frontmatter title vs first H1 alignment
- Example: file is `Alex Cheng.md` but frontmatter says `Alex Chen` and H1 says `# Alex Chen` — file should be renamed
- **Manual** — file renames need user confirmation (breaks wikilinks)

### Class 7: Aliases coverage
- Person pages without `aliases:` frontmatter (per convention)
- Person pages with aliases that include only one variant (suspect — should have nicknames, email, etc.)
- **Auto-fixable** when known clusters apply (see `_system/conventions/aliases.md` for the known list)

## Process

### Phase 1: Enumerate files

```
Scope: glob "{{VAULT_ROOT}}/**/*.md"
Exclude:
  - raw/**
  - _system/external/**
  - **/.bak.md
  - .claude/**
  - workspace-export/**
```

Replace `{{VAULT_ROOT}}` with the absolute path to your Obsidian vault root.

### Phase 2: Parse each file

For each .md file:

1. Read first ~30 lines
2. Detect frontmatter delimiters (`---` at line 1, closing `---` somewhere in first ~30 lines)
3. Parse YAML between delimiters
4. Catch parse exceptions
5. Classify any errors per the 7 classes above

### Phase 3: Apply auto-fixes (if `--fix` enabled)

For each file with auto-fixable errors:

1. Backup original to `<file>.bak.md`
2. Apply the fix:
   - Strip BOM / null bytes
   - Normalize date format
   - Add missing required fields (where derivable)
   - Add aliases for known clusters
3. Re-parse to verify fix worked
4. Write the corrected file
5. Increment auto-fix counter

### Phase 4: Report manual issues

Group remaining errors by severity:

```
Frontmatter Audit — YYYY-MM-DD

Files scanned: N
Files with errors: N
Files auto-fixed: N (--fix was enabled / disabled)

=== CRITICAL (file may not parse in Obsidian) ===
- people/<Name>.md: Missing closing --- (frontmatter never terminates)
- ventures/.../X.md: Invalid YAML — unescaped quote in line 4

=== STRUCTURAL (missing required fields) ===
- knowledge/<Topic>.md: Missing type: field
- summaries/<Source>.md: Missing date: field

=== SEMANTIC (manual review) ===
- people/<Name>.md: type: people should be type: person
- journal/<Date>.md: slug-name mismatch — file says "Foo", frontmatter says "Bar"

=== HYGIENE (recommendations) ===
- 12 person pages missing aliases: frontmatter
- 4 person pages with only 1 alias (consider adding email/handles)
```

## Special handling

| Case | Handling |
|---|---|
| File has no frontmatter at all | Flag CRITICAL — required for all wiki pages |
| Frontmatter has extra fields not in spec | Allow — extra fields are user choice |
| `tags:` is a string instead of list | Auto-fix to single-item list |
| `aliases:` is null or empty | Skip if non-person; flag as HYGIENE if person |
| File is in `_system/` | Skip (different rules) |
| File is in `raw/` | Skip (immutable) |
| File is `.bak.md` | Skip |
| Frontmatter has BOM or null byte | Auto-fix (strip) |
| Date is `today` or relative | Manual — ask user for absolute date |

## Reference inputs

- `_system/_CLAUDE.md` — Page Conventions section (frontmatter spec)
- `_system/conventions/aliases.md` — aliases convention
- `_system/conventions/filing-rules.md` — for derivable type field from path
- Source: `_system/external/gbrain/skills/frontmatter-guard/SKILL.md` (gbrain version, adapted)

## Output format

```
✅ Frontmatter audit — YYYY-MM-DD

Files scanned: 348
Issues found: 23
Auto-fixed: 14
Manual review needed: 9

Critical: 1 (file may not parse)
Structural: 4 (missing required fields)
Semantic: 4 (manual decision)
Hygiene: 14 (aliases coverage)

Backups created: 14 (in-place .bak.md files)

Top issues by category:
- 12 person pages missing aliases frontmatter (run /brain-compile or add manually)
- 1 file with critical parse error (review immediately)

[Full report saved to journal/YYYY-MM-DD Frontmatter Audit.md]
```

## Anti-patterns

- ❌ Auto-fixing semantic errors (wrong type, wrong slug) — those need user judgment
- ❌ Modifying files without `.bak.md` backup
- ❌ Renaming files automatically (breaks wikilinks)
- ❌ Adding required fields with placeholder values (`date: TBD` is worse than no date — it's a lie)
- ❌ Lint passes on `raw/` (immutable) or `.bak.md` files
- ❌ Reporting "all clean" without actually scanning every file

## Tools used

- Read — load files + conventions
- Glob — enumerate scope
- Edit / Write — apply fixes + create backups
- Bash — for BOM/null-byte handling if needed

## See also

- [[_system/_CLAUDE.md]] — frontmatter spec
- [[_system/conventions/aliases]] — aliases hygiene rule
- `/brain-dream` — invokes this as Phase 1 (lint)
- Source: gbrain's `frontmatter-guard/SKILL.md` at `_system/external/gbrain/skills/frontmatter-guard/SKILL.md`
