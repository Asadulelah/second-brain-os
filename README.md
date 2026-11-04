# Second Brain OS

> **Every other second brain remembers. This one works.**

A personal AI assistant with a real memory — built on [Claude Code](https://claude.com/claude-code), stored as plain files you own, and set up by having a conversation, not by editing config files.

You talk to it like a person. It files everything worth keeping into a wiki of your life — the people you meet, the projects you run, the decisions you make — and then *uses* that wiki to actually help you: it recalls the right context at the right moment, follows up on your commitments, and maintains itself while you sleep.

Built by [Asadulelah](https://github.com/Asadulelah). MIT licensed. Your data never leaves your machine.

---

## Start here (pick your lane)

| You are... | Read this |
|---|---|
| **Not technical at all** — you just want a personal AI that remembers your life | [Getting Started](docs/GETTING-STARTED.md) — a plain-English, click-by-click walkthrough. No jargon. |
| **Comfortable installing things** — you want it running in 10 minutes | [Install guide](docs/INSTALL.md) — plugin, `/onboard`, done. |
| **An engineer** — you want to know how the memory engine actually works | [Architecture](docs/ARCHITECTURE.md) — the attention router, the session pool, the five layers. |

---

## What is this, in plain words?

Most "second brain" apps are **filing cabinets**: you put notes in, and they sit there. When you need something, *you* have to remember where you put it. The app remembers nothing on its own.

This is different. It's an **assistant with a filing cabinet** — and the assistant does the filing, the finding, and the follow-up:

- **You mention a meeting** → it writes the meeting page, updates the person's page, links them together, and adds the deadline you agreed to.
- **You start a new session tomorrow** → it already knows who you are, what you're working on, and what happened yesterday.
- **You ask "what do I know about Sarah?"** → it answers from every note that ever mentioned her, with sources.
- **You do nothing for a week** → its maintenance cycle (the "dream cycle") lints, cross-links, and de-duplicates the wiki on its own.

There is no form to fill out and no template to edit. On first run, the assistant **interviews you** — asks its own name, learns who you are and what you're building — and writes its own configuration from your answers. Five minutes of conversation, and it's yours.

## Why it's different (the honest version)

Three design decisions carry the whole system:

1. **The storage serves an agent, not the other way around.** Every page follows conventions (source citations, back-links, a synthesis zone + an append-only timeline) that exist so an *AI* can read, trust, and update them — which is exactly what makes them pleasant for a human to read too.

2. **Recall, not just storage.** Storing everything is easy; surfacing the *right thing at the right moment* is the hard part. Name a person and their page's current state is already in context. Ask "what did we decide about pricing" and every past conversation is searchable in a fraction of a second, each with a short summary and the exact fixes, commands and decisions it contained. Plain keyword search over local files: no vector database, no API key.

3. **Graceful degradation.** The core runs on just Claude Code + this plugin. Session-history search, integrations, the hook engine — all optional enhancements. Run `/brain-doctor` any time and the assistant tells you exactly what's installed, what's missing, and the one command to add each piece. Nothing breaks because you skipped a step.

## What's in the box

```
second-brain-os/
├── plugin/                  The Claude Code plugin
│   ├── skills/
│   │   ├── onboard/         /onboard — the conversational setup wizard (the centerpiece)
│   │   ├── brain-doctor/    /brain-doctor — self-check: what's installed, what's missing
│   │   ├── brain-dream/     /brain-dream — the self-maintenance cycle (nightly/weekly/full)
│   │   └── brain-*/         9 more maintenance + research skills (lint, back-links,
│   │                        dedup, tier-audit, source-fix, compile, graph, resolver, research)
│   ├── hooks/               The memory engine: recall, entity recall, session pool (optional)
│   └── settings.template.json
├── template-vault/          Your brain's starting structure — near-empty on purpose;
│   │                        /onboard fills it in from your answers
│   ├── CLAUDE.md            The assistant's operating manual (generated for you)
│   ├── _system/             Identity, memory, and the 9 filing conventions
│   └── me/ people/ ventures/ systems/ strategy/ knowledge/ journal/ summaries/
├── manifest.json            Editions + optional dependencies (what /brain-doctor reads)
└── docs/                    Install · Getting Started · Architecture · FAQ · Lineage
```

Works beautifully with [Obsidian](https://obsidian.md) (the graph view of your life is genuinely something), but doesn't require it — everything is plain Markdown in folders you own.

## Quick start

```bash
# 1. Get the code
git clone https://github.com/Asadulelah/second-brain-os.git

# 2. Copy the template vault to wherever you want your brain to live
cp -r second-brain-os/template-vault ~/my-brain

# 3. Open it in Claude Code and let it set itself up
cd ~/my-brain && claude
> /onboard
```

The assistant takes it from there: it names itself, interviews you, writes its own foundation files, and flips into normal operation. From then on, anything you share — a meeting, a document, a new person, a decision — gets filed automatically.

Then run `/brain-doctor` to see which optional enhancements (automatic session history, the attention hooks, integrations) you might want. Details, including plugin installation, in the [Install guide](docs/INSTALL.md).

## The maintenance cycle ("the dream cycle")

Brains decay without sleep. `/brain-dream` is the maintenance pass that keeps the wiki healthy:

| Variant | What it does | Cadence |
|---|---|---|
| `--light` (~5 min) | lint frontmatter + sweep missing back-links + health check | nightly, or whenever |
| `--weekly` (~15 min) | adds synthesis, contradiction-reconciling, enrichment-tier audit, recap | Sundays |
| `--full` (~30 min) | adds citation fixing + typed-graph extraction | after heavy ingest days |

Each run writes a report to `journal/` so you can see what your brain did while you weren't looking.

## Is my stuff private?

Yes, structurally: **your brain is a local folder of Markdown files on your machine.** This repository contains the *framework only* — when you use it, your data lives in your own private vault and never flows back here or anywhere else. Your conversations with the assistant are covered by whatever Claude plan you use, same as any Claude Code session. More in the [FAQ](docs/FAQ.md).

## Lineage

This is an evolved descendant of [Garry Tan's gbrain](docs/LINEAGE.md) convention framework — the conventions-as-law idea and the dream cycle trace back to it, with credit and gratitude. The attentional router, session pool, conversational onboarding, dependency doctor, and the plugin packaging are original to this project. Full genealogy in [LINEAGE.md](docs/LINEAGE.md).

## License

[MIT](LICENSE) — use it, fork it, build your own assistant on it. Every brain built from this template carries one line of attribution: *Built on the Second Brain framework by Asadulelah.* Please leave it in; it's the maker's mark.

---

*Built on the Second Brain framework by [Asadulelah](https://github.com/Asadulelah).*
