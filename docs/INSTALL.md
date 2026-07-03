# Install — Second Brain OS

> *Every other second brain remembers. This one works.*
>
> Built on the Second Brain framework by Asadulelah.

This guide follows the framework's core principle: **graceful degradation.** The brain runs on **just Claude Code + this plugin**. Everything else is an opt-in **enhancement** — install it to unlock more, skip it and the core still works. There is no "install 20 things or nothing works." At any point, run `/brain-doctor` and the assistant tells you exactly what's present, what's missing, and the one command to add each missing piece.

---

## TL;DR

1. Install the plugin → get the core (memory + conventions + onboarding + maintenance skills).
2. Run `/onboard` → the assistant interviews you and writes your foundation. The brain is now live.
3. Run `/brain-doctor` → see which optional enhancements would unlock more, with exact install commands.
4. Add enhancements whenever you want — never required.

---

## Part 1 — Core (required)

The core is the brain that *acts*: the memory architecture, the knowledge conventions, auto-ingest, the onboarding flow, the dependency-checker, and the maintenance skills.

### 1. Install Claude Code

If you don't have it: install Claude Code (CLI, desktop, or IDE extension). This is the only hard prerequisite.

### 2. Install the plugin

In any Claude Code session:

```
/plugin marketplace add Asadulelah/second-brain-os
/plugin install second-brain-os@second-brain-os
```

This gives you the `/onboard`, `/brain-doctor`, and `/brain-*` maintenance skills, plus the hook scripts in `plugin/hooks/`.

### 3. Get the template vault

Clone / copy the template vault scaffold to where you want your brain to live (e.g. an Obsidian vault folder). It ships near-empty on purpose — the onboarding builds it out.

```bash
git clone https://github.com/Asadulelah/second-brain-os.git
cp -r second-brain-os/template-vault ~/my-brain
cd ~/my-brain && claude
```

(No git? Download the ZIP from GitHub and copy `template-vault` by hand — same thing.)

### 4. Run onboarding

```
/onboard
```

The assistant interviews you — names itself, learns who you are and what you're building, seeds your first ventures and people, captures your tone — then **writes your foundation**: `CLAUDE.md`, `_system/SOUL.md`, `me/<You>.md`, the folder scaffold, and an empty `_system/MEMORY.md`. When it writes `.claude/.onboarded`, the brain flips to **normal operation**: from then on, anything you share gets filed automatically. You never run `/onboard` again.

**At this point the brain is fully working.** Everything below is optional.

---

## Part 2 — Enhancements (optional, graceful degradation)

Run `/brain-doctor` first — it reads `manifest.json`, checks your actual stack, and reports present vs missing with the exact command for each. The list below is the same set the doctor reports against.

### Plugins

| Plugin | Unlocks | Without it |
|---|---|---|
| **claude-mem** — `/plugin install claude-mem@thedotmack` | Semantic search across all past sessions, auto-injected at session start. | The wiki + MEMORY still persist everything that gets filed — you just lose automatic recall of past *conversations*. |
| **superpowers** — `/plugin install superpowers@claude-plugins-official` | Planning, debugging, code-review, multi-session workflow skills. | The brain's core filing/memory loop is unaffected. |

> Use the exact marketplace handles in `manifest.json` → `dependencies.plugins.recommended` as the source of truth; `/brain-doctor` reports from there.

### MCP servers

| MCP | Unlocks | How |
|---|---|---|
| **Notion** | Two-way sync with Notion docs/tasks. | Enable the Notion connector in Claude settings, or `claude mcp add` the server. |
| **Google Drive** | Read/ingest Drive files directly into the wiki. | Enable the Google Drive connector in Claude settings. |

The brain ingests anything you paste or describe regardless of MCPs — these just let the assistant *fetch* sources directly instead of waiting for them to be pasted.

### Hooks (the attentional + memory engine)

These make the brain self-collect and route the right context at the right moment. They wire into your **user-level** `settings.json`, not the vault.

**To wire them:**

1. Open `plugin/settings.template.json`.
2. Merge its `hooks` block (and the `env.CONTEXT_DOCS_ROOT` entry) into your `~/.claude/settings.json`.
3. Replace the placeholders:
   - `{{PLUGIN_HOOKS_DIR}}` → the absolute path to this plugin's `plugin/hooks/` directory.
   - `{{VAULT_ROOT}}` → the absolute path to your vault.
4. Restart Claude Code. Run `/brain-doctor` to confirm all four hooks report ✅.

| Hook | Event | Unlocks |
|---|---|---|
| `context-router-v2.py` | `UserPromptSubmit` | Routes relevant vault docs into context based on the prompt — the attentional layer. |
| `pool-auto-update.py` | `UserPromptSubmit` | Keeps the live session pool fresh as the conversation moves. |
| `pool-loader.py` | `SessionStart` | A new session self-collects prior state instead of starting cold. |
| `pool-extractor.py` | `Stop` | Persists session state for the next session to load. |

Prefer not to hand-edit JSON? Run `/update-config` and ask the assistant to wire the hooks for you (it'll confirm before touching `settings.json`).

---

## Editions

An edition is just a manifest of core + chosen modules (`manifest.json` → `editions`):

- **Light** — core only. The bare brain; already beats any filing cabinet.
- **Loaded** — core + all modules.
- **Vertical** — core + a curated set (Agency Brain / Design Brain / Builder Brain).

Start with Light. Add modules when you want them — same engine, cheap packaging on top.

---

## Verify your install

```
/brain-doctor
```

Leads with **"Core: healthy"** (it always is, if the plugin is installed), then lists enhancements present vs missing with the exact command for each. Nothing missing is an error — it's just an enhancement you haven't added yet.

---

*Built on the Second Brain framework by Asadulelah. An evolved fork of Garry Tan's gbrain convention framework — credited as inspiration, rebuilt as its own system.*
