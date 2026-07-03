# FAQ

> Built on the Second Brain framework by [Asadulelah](https://github.com/Asadulelah).

### Do I need to know how to code?

No. If you can install an app and hold a conversation, you can run this — the [Getting Started guide](GETTING-STARTED.md) assumes zero technical background. Coding knowledge only matters if you want to modify the hooks or contribute.

### Is my data private?

Structurally yes: your brain is a folder of plain-text Markdown files **on your own machine**. Nothing you file is sent to this project — this repository is the empty framework; your content never flows back. Your *conversations* with the assistant go through Claude like any other Claude Code session, covered by your Anthropic plan's data terms.

### What does it cost?

The framework is free (MIT). Running it requires a Claude subscription that includes Claude Code — the assistant is Claude. There are no other costs.

### Do I need Obsidian?

No. Obsidian is an optional, free viewer — the brain is just Markdown files and works entirely without it. Install it if you want the graph view (you probably do — watching your life map grow is half the fun).

### What actually happens when I "file" something?

You mention something worth keeping (a meeting, a person, a decision). The assistant distills it — never dumps raw text — into the right pages: a dated journal entry, an updated person page, a link between them, a memory update if priorities changed. Then it confirms in one line what it saved. This is default behavior; you never ask it to save.

### What's the difference between this and just using Claude with memory turned on?

Built-in memory is a black box you can't browse, organize, or own. This gives you the memory **as files**: inspectable, searchable, versionable, portable, yours. Plus the conventions (citations, back-links, timelines) that keep it trustworthy at scale, and the maintenance cycle that keeps it healthy.

### What if I skip all the optional stuff?

Everything core still works — that's the design (graceful degradation). Skipping claude-mem loses automatic recall of past *chat sessions* (the wiki still remembers everything filed). Skipping the hooks loses automatic context-routing (the assistant still finds things by searching). Run `/brain-doctor` anytime to see what you're missing and what each piece would add.

### Can I rename my assistant / change its personality later?

Yes. Its identity lives in `_system/SOUL.md` — edit it directly, or ask the assistant to update it. Re-running `/onboard` rebuilds the foundation from scratch (it backs up existing files first).

### How do I update the framework?

`git pull` this repo (or re-download the ZIP) for new skill versions. Your vault is separate from the framework, so updates never touch your data. That separation is deliberate — see [ARCHITECTURE.md](ARCHITECTURE.md).

### Can I use this for a team?

It's designed as a single-person brain — one user, one assistant, one vault. Teams can each run their own instance. A shared-vault mode is an interesting fork idea; the conventions already support source attribution per person.

### Windows / Mac / Linux?

All three. The vault is plain files; Claude Code runs on all of them. The optional hooks are Python scripts — you'll need Python 3 installed for those (the core works without them).

### Something's broken. Where do I start?

`/brain-doctor` — it self-diagnoses the stack and reports what's missing or miswired, with the fix for each. If the assistant seems to not know who you are, check that `/onboard` completed (a `.claude/.onboarded` file should exist in your vault).

### Who made this, and what's gbrain?

Built by [Asadulelah](https://github.com/Asadulelah), evolved from months of running the real thing daily. The convention framework traces back to Garry Tan's **gbrain** — full credit and genealogy in [LINEAGE.md](LINEAGE.md).

---

*Built on the Second Brain framework by Asadulelah.*
