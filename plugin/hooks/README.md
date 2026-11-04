# plugin/hooks — Attentional Memory + Instance Pool Hooks

Four Python scripts that wire Claude Code's hook system into a working
**attentional memory engine** and a **multi-instance coordination pool**.
These are the "actually works" core — every Claude Code session that uses
them gets persistent context routing and cross-instance signalling for free.

---

## Recall (v1.1, wired by default)

### `brain_recall.py` — past-session memory
**Hook:** `SessionStart` (runs `index`; incremental, ~2 s)

A local SQLite FTS5 index of every Claude Code conversation on the machine, across every
`~/.claude*` login. Text only; rows outlive the transcripts Claude Code deletes.

```bash
python3 brain_recall.py search "pricing decision" [-n 8] [--since 2026-10-01]
python3 brain_recall.py read <session-id-prefix> --around "pricing"
python3 brain_recall.py digest --limit 20 --workers 2   # optional: Haiku summary + atoms per session; run hourly
python3 brain_recall.py stats
python3 brain_recall.py selftest
```

Env: `BRAIN_RECALL_DB` (default `~/.claude/brain-recall.db`), `BRAIN_RECALL_MODEL` (default `haiku`).

### `entity-recall.py` — people and ventures named in a prompt
**Hook:** `UserPromptSubmit`

Keys come from page names and `aliases:` in `people/*.md` and `ventures/*/*.md` (pages with
`type: person|venture`). Injects the current-state zone of up to 3 matched pages, once per session.
`python3 entity-recall.py --test "what did maya say"` dry-runs; `--selftest` checks it.
Replaces `context-router-v2.py` in the default wiring (the keyword map drifted from the vault).

## The v1 hooks

### `context-router-v2.py` — Attentional Context Router
**Hook:** `UserPromptSubmit`

Implements tiered working memory for Claude Code context injection.
On every user prompt it reads the prompt, scores `.claude/` docs by
relevance, and injects the most relevant content back into context at
one of three tiers:

| Tier | Score | What gets injected |
|------|-------|--------------------|
| HOT  | ≥ 0.8 | Full file content |
| WARM | 0.25–0.8 | First 25 lines (header) only |
| COLD | < 0.25 | Nothing (evicted) |

Scores decay each turn; direct keyword mentions reset a file's score to
1.0; co-activation boosts related files. State persists between turns in
`.claude/attn_state.json`.

**Customising keywords:**
Create `.claude/keywords.json` (project-local) or
`~/.claude/keywords.json` (global). If neither exists the script falls
back to generic example defaults in the `_DEFAULT_KEYWORDS` dict. Format:

```json
{
  "keywords": {
    "relative/path/to/doc.md": ["keyword1", "keyword2"],
    "another/doc.md": ["term1", "term2"]
  },
  "co_activation": {
    "relative/path/to/doc.md": ["related/doc.md"]
  }
}
```

**Environment variable override:**
```
CONTEXT_DOCS_ROOT=/path/to/your/docs/dir
```
Priority: `CONTEXT_DOCS_ROOT` > project `.claude/` > global `~/.claude/`.

---

### `pool-loader.py` — Instance Pool Loader
**Hook:** `SessionStart`

On session start, reads the shared instance pool JSONL and injects a
brief summary of recent activity by all instances (and full detail if
`POOL_COMPACT=0`). Lets a new session pick up where others left off.

Pool file location: `.claude/pool/instance_state.jsonl` (project-local)
or `~/.claude/pool/instance_state.jsonl` (global fallback).

---

### `pool-extractor.py` — Instance Pool Extractor
**Hook:** `Stop`

When a session ends, reads the transcript, finds the last assistant
response, extracts any ` ```pool ``` ` block Claude wrote, and appends a
structured entry to the pool JSONL.

Claude writes pool blocks when it wants to signal state to other
instances:

````
```pool
action: completed
topic: auth refactor
summary: Moved JWT logic to middleware, all tests pass
affects: src/auth/
blocks: PR #17
```
````

---

### `pool-auto-update.py` — Pool Auto-Updater
**Hook:** `UserPromptSubmit`

Runs on every user prompt. Like `pool-extractor.py` but fires during
the session, not at the end — useful for long-running sessions. Extracts
explicit `pool` blocks first; falls back to heuristic detection of
completion/blocker/signal phrases. Respects a 5-minute cooldown to
prevent spam writes.

---

## settings.json wiring block

Paste this into your `~/.claude/settings.json` (global) or
`.claude/settings.json` (project-local) under the `"hooks"` key.

Replace `python` with the full path to your Python 3 interpreter if it
is not on `PATH`. On Windows this might be
`C:/Users/YourName/AppData/Local/Programs/Python/Python312/python.exe`.
On macOS/Linux `python3` usually suffices.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$HOME/.claude/scripts/context-router-v2.py\"",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "python \"$HOME/.claude/scripts/pool-auto-update.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$HOME/.claude/scripts/pool-loader.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$HOME/.claude/scripts/pool-extractor.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Install steps:**
1. Copy the four `.py` files to `~/.claude/scripts/` (create if needed).
2. Add the block above to your `settings.json`.
3. Create `.claude/keywords.json` in each project with your keyword map
   (or rely on the generic defaults for a quick start).
4. Optionally set `CLAUDE_INSTANCE` in your environment to a short label
   (e.g. `main`, `worker-1`) so pool entries are attributed correctly.

---

## File layout produced at runtime

```
.claude/
  attn_state.json          — per-project attention scores (created by context-router)
  keywords.json            — your project's keyword map (you create this)
  pool/
    instance_state.jsonl   — shared pool (created by pool hooks)
    active_instances.json  — instance registry
    loader_errors.log      — pool-loader error log
    extractor_errors.log   — pool-extractor error log
    auto_update_errors.log — pool-auto-update error log

~/.claude/
  attn_state.json          — global fallback attention state
  attention_history.jsonl  — per-turn history log
  context_injection.log    — injection debug log
  keywords.json            — global keyword map fallback
  pool/                    — global pool fallback (same structure as above)
```

---

## Dependencies

- Python 3.8+
- No third-party packages — standard library only (`json`, `re`, `pathlib`, `uuid`, `hashlib`, `subprocess`)

## Graceful degradation

All four hooks exit cleanly on failure (non-zero exit is swallowed,
errors go to their respective `.log` files). A missing or corrupt pool
file / state file causes a clean re-init, not a crash.
