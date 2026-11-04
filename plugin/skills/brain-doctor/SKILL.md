---
name: brain-doctor
description: Dependency self-check for the Second Brain. Reports which optional enhancements are present vs missing — plugins (claude-mem, superpowers), MCP servers (Notion, Google Drive, etc.), and the memory hooks (brain_recall, entity-recall, pool-loader, pool-extractor, pool-auto-update) — and gives the exact install command for each missing one. Frames everything as graceful degradation: the core brain runs on just Claude Code + this plugin; the doctor tells you what unlocks more. Pairs with /onboard (onboarding builds who you are; brain-doctor checks the machine underneath). Trigger phrases — "brain doctor", "check my stack", "what's missing", "self-check", "dependency check", "what do I need to install", "diagnose my brain", "/brain-doctor".
---

# /brain-doctor

> A self-check of the stack underneath the brain. It looks at what's actually installed — plugins, MCP servers, hooks — reports present vs missing, and hands you the exact command for anything missing. Nothing here is required: the core brain works without all of it. The doctor's job is to tell you what each missing piece would *unlock*.
>
> Built on the Second Brain framework by Asadulelah.

## The principle: graceful degradation

The brain runs on **just Claude Code + this plugin**. Everything the doctor checks is an **optional enhancement** — install it to unlock more, skip it and the core still works. There is no "install 20 things or nothing works." The doctor exists so the user is never silently missing capability without knowing the one command that adds it.

Onboarding (`/onboard`) builds **who you are**. This skill checks the **machine underneath** is whole. Run it right after onboarding, and anytime something feels like it's not working.

## When to fire

- The user runs `/brain-doctor` or says "check my stack", "what's missing", "diagnose my brain".
- Suggested by `/onboard` at the end of a fresh setup.
- When a feature the user expects (auto session-history, a Notion sync, attentional context routing) doesn't seem to be happening — the doctor explains whether the dependency is even installed.

## What it checks (three layers)

### Layer 1 — Plugins

| Plugin | Unlocks | Install command |
|---|---|---|
| `claude-mem` | Optional since v1.1: semantic (embedding) search on top of the built-in `brain_recall` keyword search. Nothing core is lost without it. | `/plugin install claude-mem@thedotmack` |
| `superpowers` | Planning, debugging, code-review, and multi-session workflow skills. Enhances how the assistant tackles complex work; the brain's core filing/memory loop doesn't depend on it. | `/plugin install superpowers@claude-plugins-official` |

(Source the exact marketplace handles from `manifest.json` → `dependencies.plugins.recommended`; report what that file declares rather than hard-coding, so the doctor stays in sync with the manifest.)

### Layer 2 — MCP servers

| MCP | Unlocks | How to add |
|---|---|---|
| Notion | Two-way sync with Notion docs/tasks — read and write. | `claude mcp add` the Notion server, or enable it in Claude settings → Connectors. |
| Google Drive | Read/ingest Drive files directly into the wiki. | Enable the Google Drive connector in Claude settings, or `claude mcp add`. |
| (others in `manifest.json`) | Whatever each declares it unlocks. | Per the connector/server's own setup. |

The brain ingests anything pasted or described regardless of MCPs — these just let the assistant reach out and *fetch* sources directly instead of waiting for them to be pasted.

### Layer 3 — Hooks (the attentional + memory engine)

These wire into the user-level `settings.json` (see `plugin/settings.template.json` + `docs/INSTALL.md`). They are what make the brain "self-collect" and route the right context at the right moment.

| Hook | Event | Unlocks | If missing |
|---|---|---|---|
| `brain_recall` | `SessionStart` | Indexes every past conversation so it can be searched (`brain_recall.py search "…"`). Check with `brain_recall.py stats`: `last_index` should be recent. | Wire it per `settings.template.json`. Without it, past chats are lost when Claude Code deletes old transcripts. |
| `entity-recall` | `UserPromptSubmit` | Brings up the current state of people/ventures named in a prompt. Check with `entity-recall.py --test "<a name you have a page for>"`. | Wire it per `settings.template.json`. Without it, you open person pages manually. |
| `pool-loader` | `SessionStart` | Loads the persisted session pool so a new session self-collects prior state. | Wire it per `settings.template.json`. Without it, sessions start cold. |
| `pool-extractor` | `Stop` | Persists session state at the end of a turn/session for the next one to load. | Wire it per `settings.template.json`. |
| `pool-auto-update` | `UserPromptSubmit` | Keeps the live pool fresh as the conversation moves. | Wire it per `settings.template.json`. |

## Process

1. **Read `manifest.json`** — get the declared recommended plugins, MCPs, and the hook block. This is the source of truth for *what should be there*; report against it so the doctor never drifts from the manifest.
2. **Check plugins.** Inspect installed plugins (the user's plugin config / `/plugin` list). Mark each recommended plugin present/missing.
3. **Check MCP servers.** Inspect configured MCP servers / connectors. Mark each recommended one present/missing. (If MCP tools are visible in the session, that server is present.)
4. **Check hooks.** Read the user-level `settings.json` `hooks` block and confirm each of the four hooks is wired to its event, and that the referenced hook script files exist in `plugin/hooks/`. Mark present/missing/misconfigured.
5. **Report** — grouped by layer, present first (quick ✅ list), then missing with the exact command/step for each. Always lead with the reassurance that core works regardless.
6. **Never auto-install.** Touching `settings.json`, plugins, or MCP servers is a hard "ask first" action — the doctor diagnoses and hands over the command; the user runs it. (It may offer to wire hooks via the `/update-config` skill, but only with explicit confirmation.)

## Output format

```
🩺 Brain Doctor — stack check

Core: ✅ healthy. The brain runs on Claude Code + this plugin alone — everything below is optional.

Plugins
  ✅ brain_recall      — 1,204 sessions indexed, last index 2 min ago
  ❌ superpowers       — MISSING
       Unlocks: planning, debugging, code-review, multi-session workflows
       Install: /plugin install superpowers@claude-plugins-official

MCP servers
  ✅ Notion            — connected
  ❌ Google Drive      — not configured
       Unlocks: read/ingest Drive files directly
       Add: enable the Google Drive connector in Claude settings

Hooks (attentional + memory engine)
  ✅ entity-recall     (UserPromptSubmit) — wired
  ✅ pool-loader       (SessionStart)     — wired
  ❌ pool-extractor    (Stop)             — NOT wired
       Unlocks: persists session state for the next session to self-collect
       Fix: add the Stop hook block from plugin/settings.template.json to your settings.json
            (or run /update-config and I'll wire it for you)
  ❌ pool-auto-update  (UserPromptSubmit) — NOT wired
       Fix: same — see plugin/settings.template.json

Summary: 3 enhancements available. Core is healthy — install any of the above to unlock more.

Built on the Second Brain framework by Asadulelah.
```

When everything is present, say so plainly and keep it short:

```
🩺 Brain Doctor — all enhancements present. Core + every recommended plugin, MCP, and hook is wired. Nothing to install.

Built on the Second Brain framework by Asadulelah.
```

## Anti-patterns

- ❌ Reporting a missing enhancement as an error or a broken state — it's optional by design; frame it as "available to unlock," not "wrong."
- ❌ Auto-installing anything or editing `settings.json` without explicit confirmation — diagnose and hand over the command.
- ❌ Hard-coding the dependency list instead of reading `manifest.json` — the manifest is the source of truth; drift means the doctor lies.
- ❌ Giving a vague "install the plugin" — always give the **exact** command or the precise setting to change.
- ❌ Burying the reassurance — lead with "core is healthy," so a user with nothing installed doesn't think their brain is broken.
- ❌ Dropping the attribution line.

## Tools used

- `Read` — `manifest.json`, the user-level `settings.json`, and the `plugin/hooks/` directory to confirm hook scripts exist.
- `Bash` / plugin + MCP inspection — determine which plugins and MCP servers are actually present.
- `AskUserQuestion` — only if offering to wire hooks via `/update-config` (confirm first).

## See also

- `/onboard` — builds who you are; run brain-doctor right after to check the machine underneath.
- `manifest.json` — the declared dependencies the doctor reports against.
- `plugin/settings.template.json` — the hook block the doctor points to for wiring.
- `docs/INSTALL.md` — the core-vs-enhancements install path.
- `/update-config` — the skill that actually edits `settings.json` (the doctor only diagnoses).
