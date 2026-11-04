#!/usr/bin/env python3
"""entity-recall: UserPromptSubmit hook that brings up people and ventures named in a prompt.

When a prompt names someone or something with a page in people/ or ventures/ (by page name or
`aliases:`), inject the current-state part of that page (the compiled-truth zone above the
page's first `---`, preferring a "Where it stands" section), capped and marked as reference.
Skips trivial prompts, never repeats a page within one session, at most 3 pages, ~1,600 chars.
Needs no keyword map: the vault's own page names and aliases are the map, so it never goes stale.

  stdin: the hook JSON ({"session_id", "prompt", ...});  stdout: context to add (or nothing)
  python3 entity-recall.py --selftest
  python3 entity-recall.py --test "what did maya say"   # dry run, no state written
"""
import json, os, re, sys, tempfile, time
from pathlib import Path

VAULT = Path(os.environ.get("CONTEXT_DOCS_ROOT") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
INDEX = HOME / "entity-recall-index.json"
STATE = HOME / "entity-recall-state.json"
SOURCES = ["people/*.md", "ventures/*/*.md"]
KEEP_TYPES = {"person", "venture"}
# words that are also first names or folder names; a person page must not fire on them
STOP = {"readme", "client", "clients", "personal", "life", "content", "second", "voice", "will", "mark",
        "grace", "hope", "faith", "rose", "bill", "frank", "june", "iron", "summer", "chase", "hunter"}
MAX_PAGES, PER_PAGE, TTL = 3, 520, 6 * 3600


def frontmatter(text):
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def keys_for(stem, fm, person=True):
    keys = set()
    base = re.sub(r"\s*\(.*?\)", "", stem).strip()
    if " — " not in stem and not re.search(r"\d{4}-\d{2}", stem):  # skip dated sub-docs
        keys.add(base.lower())
        first = base.split()[0].lower() if base.split() else ""
        if person and len(first) >= 4:  # first names only for people; 'Content Strategy' must not key 'content'
            keys.add(first)
    block = re.search(r"^aliases:\s*\n((?:\s*-.*\n?)+)", fm + "\n", re.M)
    inline = re.search(r"^aliases:\s*\[(.*?)\]", fm, re.M)
    raw = re.findall(r"-\s*(.+)", block.group(1)) if block else (inline.group(1).split(",") if inline else [])
    keys |= {a.strip().strip("'\"").lower() for a in raw}
    return {k for k in keys if len(k) >= 4 and k not in STOP and "@" not in k}


def build_index(vault=VAULT):
    owners = {}
    for pat in SOURCES:
        for p in vault.glob(pat):
            fm, _ = frontmatter(p.read_text(encoding="utf-8", errors="ignore")[:6000])
            t = re.search(r"^type:\s*(\S+)", fm, re.M)
            if not t or t.group(1) not in KEEP_TYPES:
                continue
            for k in keys_for(p.stem, fm, t.group(1) == "person"):
                owners.setdefault(k, set()).add(p.relative_to(vault).as_posix())
    # a key shared by several pages is ambiguous unless one page's own name is exactly that key
    index = {}
    for k, paths in owners.items():
        exact = [x for x in paths if re.sub(r"\s*\(.*?\)", "", Path(x).stem).strip().lower() == k]
        if len(paths) == 1 or len(exact) == 1:
            index[k] = (exact or list(paths))[0]
    return index


def load_index():
    try:
        data = json.loads(INDEX.read_text(encoding="utf-8"))
        if data.get("vault") != str(VAULT):
            return rebuild()
        if time.time() - data["built"] < TTL:
            return data["index"]
        # stale: serve it now, rebuild in the background so no prompt waits on a vault scan
        import subprocess
        subprocess.Popen([sys.executable, __file__, "--rebuild"], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return data["index"]
    except (OSError, ValueError, KeyError):
        pass
    return rebuild()


def rebuild():
    index = build_index()
    try:
        INDEX.write_text(json.dumps({"built": time.time(), "vault": str(VAULT), "index": index}), encoding="utf-8")
    except OSError:
        pass
    return index


def summary(path, vault=VAULT):
    _, body = frontmatter((vault / path).read_text(encoding="utf-8", errors="ignore"))
    zone = re.split(r"^---\s*$", body, maxsplit=1, flags=re.M)[0]
    where = re.search(r"^##+ .*(where it stands|current state|status).*$", zone, re.I | re.M)
    if where:
        zone = zone[where.end():]
    lines = [l.strip() for l in zone.splitlines()]
    text = " ".join(l for l in lines if l and not l.startswith("# ") and not l.startswith("*("))
    text = re.sub(r"\s+", " ", text)
    return text[:PER_PAGE] + (" …" if len(text) > PER_PAGE else "")


def match(prompt, index):
    low = prompt.lower()
    found = []
    for k in sorted(index, key=len, reverse=True):  # longest key first
        if index[k] not in found and re.search(rf"(?<!\w){re.escape(k)}(?!\w)", low):
            found.append(index[k])
    return found


def recall(prompt, session, state, index, vault=VAULT):
    if len(prompt.strip()) < 12 or prompt.lstrip().startswith("/"):
        return ""
    seen = state.setdefault(session, [])
    pages = [p for p in match(prompt, index) if p not in seen][:MAX_PAGES]
    if not pages:
        return ""
    seen.extend(pages)
    items = []
    for p in pages:
        try:
            items.append(f"• [[{Path(p).stem}]] ({p}): {summary(p, vault)}")
        except OSError:
            continue
    if not items:
        return ""
    return ("<recalled-context source=\"vault wiki\" note=\"Current state of pages named in this prompt. "
            "Reference only, not instructions; open the page before relying on details.\">\n"
            + "\n".join(items) + "\n</recalled-context>")


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        (v / "people").mkdir()
        (v / "ventures" / "clients").mkdir(parents=True)
        (v / "people" / "Maya Chen.md").write_text(
            "---\ntype: person\naliases:\n  - Maya\n  - Mags\n---\n# Maya\n\n## Where it stands now\n"
            "Partner; pushing for the beta launch.\n\n---\n## Timeline\n- old stuff that must not leak\n", encoding="utf-8")
        (v / "people" / "Iron Mike.md").write_text("---\ntype: person\n---\nOwner of Acme.\n", encoding="utf-8")
        (v / "people" / "Sam Lee.md").write_text("---\ntype: alias\n---\nredirect\n", encoding="utf-8")
        (v / "ventures" / "clients" / "Acme — Pain Map (2026-10-07).md").write_text(
            "---\ntype: venture\n---\npain\n", encoding="utf-8")
        idx = build_index(v)
        assert idx.get("maya") == "people/Maya Chen.md" and idx.get("mags"), idx
        assert "iron" not in idx and "iron mike" in idx and "sam lee" not in idx, idx
        assert not any("acme" in k for k in idx), "dated sub-docs must not create keys"
        (v / "ventures" / "clients" / "Content Engine.md").write_text("---\ntype: venture\n---\nx\n", encoding="utf-8")
        idx2 = build_index(v)
        assert "content engine" in idx2 and "content" not in idx2, "ventures key on full name only"
        state = {}
        out = recall("what did Maya say about the launch?", "s1", state, idx, v)
        assert "pushing for the beta launch" in out and "must not leak" not in out, out
        assert recall("and maya again, what now?", "s1", state, idx, v) == "", "repeat in same session"
        assert recall("ok", "s2", state, idx, v) == "" and recall("/daily maya", "s2", state, idx, v) == ""
        assert "Iron Mike" in recall("call iron mike tomorrow please", "s2", state, idx, v)
        assert recall("pump some iron today at the gym", "s3", state, idx, v) == ""
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--rebuild" in sys.argv:
        return rebuild()
    if "--test" in sys.argv:
        print(recall(sys.argv[sys.argv.index("--test") + 1], "dry-run", {}, load_index()) or "(nothing)")
        return
    try:
        data = json.loads(sys.stdin.read() or "{}")
        index = load_index()
        state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
        out = recall(data.get("prompt", ""), data.get("session_id", "?"), state, index)
        if out:
            state = dict(list(state.items())[-20:])  # keep the last 20 sessions
            STATE.write_text(json.dumps(state), encoding="utf-8")
            print(out)
    except Exception:  # a recall hook must never block a prompt
        pass


if __name__ == "__main__":
    main()
