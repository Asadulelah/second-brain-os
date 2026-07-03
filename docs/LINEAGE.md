# Lineage

> Good systems have ancestors. This page credits them honestly and maps what was inherited, what was adapted, and what's original.
>
> Built on the Second Brain framework by [Asadulelah](https://github.com/Asadulelah).

## gbrain — Garry Tan

The single biggest influence. Garry Tan's **gbrain** framework established the idea this project is built on: that a personal knowledge base should be governed by *conventions enforced by an AI agent*, not by human discipline.

**Inherited from gbrain (with gratitude):**
- **Conventions-as-law** — page-format rules the agent enforces on every write, rather than guidelines the human is supposed to remember.
- **Compiled-truth page structure** — synthesis zone above, append-only evidence timeline below.
- **The citation discipline** — every factual claim carries a source.
- **The dream cycle** — the idea that a knowledge base needs autonomous, scheduled maintenance (lint, reconcile, synthesize) or it decays. Several maintenance skills here (`brain-lint-frontmatter`, `brain-source-fix`) began as ports of gbrain's equivalents.

**Adapted:** gbrain assumes an always-on nightly runner; this framework adapts the dream cycle to manual + scheduled triggers with session-start self-healing, because Claude Code isn't always on.

## Original to this framework

- **The attentional context router** — tiered HOT/WARM/COLD context injection with decay, co-activation, and pinned topology. The retrieval half of the memory problem.
- **The session pool** — crash-proof cross-session continuity (loader / auto-update / extractor hooks).
- **Conversational onboarding (`/onboard`)** — the template that builds itself by interviewing you, instead of find-and-replace placeholders.
- **The dependency doctor (`/brain-doctor`)** and the **graceful-degradation packaging law** — core vs. enhancements, self-diagnosed.
- **The two-system model** — the assistant's operational brain (soul/memory) kept strictly separate from the human-browsable reference wiki.
- **Editions-as-manifests** — Light / Loaded / Vertical as configuration, not separate builds.
- **The plugin packaging** — shipping the whole thing as a native Claude Code plugin + template vault.

## Other debts

- **Obsidian** — the wikilink + graph-view culture this vault format is at home in.
- **claude-mem** (thedotmack) — the session-capture plugin recommended as the episodic-memory layer.
- The broader **building-a-second-brain** lineage (Tiago Forte et al.) for the vocabulary, even where this system disagrees with the filing-cabinet philosophy.

---

*Built on the Second Brain framework by Asadulelah — an evolved descendant, not a copy, of what came before.*
