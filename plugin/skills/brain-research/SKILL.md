---
name: brain-research
description: Run the last30days multi-source research engine (Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, Bluesky, Threads, Perplexity) on any topic, then auto-ingest the result into the Obsidian vault as distilled wiki pages per the conventions. Use this whenever the user wants the last-30-days community truth on a person, company, product, niche, or competitor — before a sales call, before building, for content research, or for competitor/prospect profiling. Trigger phrases — "research the last 30 days of X", "what's the community saying about X", "/brain-research <topic>", "run last30days on X and file it", "pull recent signal on <prospect>", "competitor research on X".
---

# /brain-research

> Bridge between the `last30days` engine and the second brain. Engine surfaces what real people said/upvoted/bet on in the last 30 days; this skill distills that raw signal into the vault as proper wiki pages — entity pages, journal entries, competitor profiles, knowledge pages — cross-linked and source-attributed. Research that isn't filed is research lost to chat history.

## When to fire

- User invokes `/brain-research <topic>` (manual).
- User asks for recent/community signal on a **person** (prospect, founder, creator), **company/product**, **niche/market**, **content topic**, or a **competitor comparison** ("X vs Y").
- Before a sales call / meeting where reading the prospect's last-30-days truth is the point.
- Content research for the user's brand — "what are people actually saying about <topic>".
- Whenever the auto-ingest rule would fire on a research request that needs *fresh external signal*, not just vault recall.

## Dependency (graceful degradation)

This skill wraps the separate **`last30days`** skill/engine — it is NOT bundled with this plugin. If `last30days` is not installed, don't fail: fall back to a plain multi-query `WebSearch` pass over the same topic (recent-signal queries across Reddit/X/YouTube/HN via site-scoped searches), then continue from step 2 (distill + file) exactly the same way, citing `[Source: WebSearch, <platform>, YYYY-MM-DD]` instead. Tell the user the dedicated engine would give deeper engagement-scored results and where to get it. `/brain-doctor` reports whether it's installed.

## What it is

`last30days` is an AI-agent-led search engine scored by **upvotes, likes, and real money — not editors**. It searches Reddit, X, YouTube, TikTok, Instagram, Hacker News, Polymarket, GitHub, Bluesky, Threads, and Perplexity in parallel, scores by engagement, and synthesizes one cited brief. Raw output lands in `raw/last30days/` (hidden from Obsidian, treated as immutable source).

## Process

### 1. Run the engine

Invoke the `last30days` skill (it has its own contract — follow it; do not improvise its output format). Do the full pre-flight (WebSearch handle + subreddit + GitHub resolution) — a **bare keyword run returns thin/empty evidence**. For autonomous filing, pass `--agent` and set the save path explicitly:

- **Always pass `--save-dir="{{VAULT_ROOT}}/raw/last30days"`** — the `.env` `LAST30DAYS_MEMORY_DIR` is only honored as a shell env var, so the explicit flag is the reliable vault-save path.
- `--agent` skips the interactive pauses.

- Person / prospect / founder → let the engine resolve `--x-handle`, `--github-user`, `--subreddits` (its pre-flight handles this).
- Product / company → `--github-repo`, subreddits, founder handle.
- Comparison ("X vs Y") → the engine's COMPARISON path.
- Niche / market / content topic → plain topic, mind the keyword-trap classes.

The engine writes `raw/last30days/<slug>-raw.md` (+ a SQLite row via `LAST30DAYS_STORE=1`). Note the path it prints.

### 2. Read the raw brief

Read `raw/last30days/<slug>-raw.md`. This is the source document. Extract the high-signal claims, quotes (with engagement counts), handles, repos, and Polymarket odds. Apply the transcript-accuracy rule: label uncertain self-claims as `self-described`, never file garbled noise as fact — but DO file the substance.

### 3. Distill into vault pages (the auto-ingest step)

Map the brief to the right destination via `_system/conventions/filing-rules.md` — **primary subject decides the folder**:

| Topic class | Lands in | Notes |
|---|---|---|
| Person (prospect, founder, creator) | `people/Full Name.md` + `journal/YYYY-MM-DD <topic> Research.md` | Use source-types labels (observed/self-described/inferred). If it's a live prospect, this feeds your engagement prep workflow. |
| Company / product | relevant `ventures/` or `people/` page + journal | Live GitHub stars/PR velocity are more current than any blog. |
| Competitor (one or vs-comparison) | `knowledge/<competitor>.md` or a competitor profile | Position vs your own offers where relevant. |
| Niche / market / content trend | `knowledge/<topic>.md` or `strategy/<topic>.md` | The "what users actually want" signal — gold for offer + content work. |

Enforce the Iron Laws on every page written:
- **Compiled-truth two zones** — synthesis above `---` (rewrite on update), timeline below (append-only).
- **Source attribution** — every claim cites `[Source: last30days engine, <platform>, YYYY-MM-DD]` pointing back to the raw file and the original platform.
- **Back-linking** — every entity mention gets a back-link on the entity page.
- **Tiered enrichment** — don't over-build a one-off mention into a full page.
- **Notability gate** — if the topic was a throwaway query, file the raw and a short note; don't manufacture a full entity page.

### 4. Cross-link + update active surfaces

- Cross-link aggressively with `[[wikilinks]]`.
- If a new **active prospect / competitor / deadline / status flip** landed, update `_system/dashboard/state.json` (DATA, no rebuild) and `_system/Active Todos.md` if it changes priorities.
- If it changed active priorities, update `_system/MEMORY.md`.

### 5. Confirm what got filed

1-2 line acknowledgment: raw path + which wiki pages created/updated + any dashboard/MEMORY change. Then answer the user's actual question grounded in the brief.

## Guardrails (vault hard rules still apply)

- **PII iron rule**: never let real vault-people data leak into client-facing artifacts built from this research. Research → vault is fine; vault → prospect deck strips PII.
- **Paid sources**: TikTok/IG/Threads and Perplexity (OpenRouter) are PAID and opt-in via `.env`. The free sources (Reddit, HN, Polymarket, GitHub, YouTube) + X-via-session run with no spend. Don't enable paid sources without the standing green-light already on file.
- **Absolute dates** in every page written.
- Don't paste raw engine markdown as a wiki page — always distill (rule: never file literal raw text as a page).

## Related

- [[last30days Research Engine]] — the capability doc (sources, keys, flags, trend-monitoring).
- [[_system/conventions/filing-rules]] — where different topic classes land in the vault.
- [[_system/conventions/compiled-truth]] — the two-zone format for pages written.
