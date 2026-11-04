# Changelog

## 1.1.0 — 2026-11-04: recall

- **`brain_recall.py`**: every past Claude Code conversation, indexed locally (SQLite FTS5) and searchable in about 0.2 s. Text only, across every `~/.claude*` login, kept after Claude Code deletes old transcripts. Recency-weighted ranking: a year-old match counts half.
- **Digests**: optional Haiku summary, find-me questions and exact atoms (errors and their fixes, commands, decisions) per session, matched by search. Runs on your Claude Code login, never a per-token key.
- **`entity-recall.py`**: names a person or venture you have a page for, and its current state is in context. Keyed off page names and `aliases:`, so no keyword map to maintain. Replaces `context-router-v2.py` in the default wiring (the router still ships, optional).
- `claude-mem` is now optional; nothing core depends on it.

## 1.0.0 — 2026-07-03

First release.
