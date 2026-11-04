#!/usr/bin/env python3
"""brain_recall: a searchable memory of every Claude Code conversation you have had.

  python3 brain_recall.py index                 # incremental; cheap to run often
  python3 brain_recall.py search "pricing decision" [-n 8] [--since 2026-10-01] [--raw]
  python3 brain_recall.py read <session-id-prefix> [--around "text"] [--from N] [-n 20] [--full]
  python3 brain_recall.py digest [--limit 50] [--workers 3]   # Haiku summary + atoms per session
  python3 brain_recall.py stats
  python3 brain_recall.py selftest

Ranked by BM25 with a mild recency weight (a year-old match counts half). Indexes text only: what you typed and what the assistant replied. Tool calls, tool output, thinking,
subagents and injected context are skipped. Rows outlive the transcripts (Claude Code deletes
those after cleanupPeriodDays). The DB is machine-local and never synced: ~/.claude/brain-recall.db
(override with BRAIN_RECALL_DB), shared by every ~/.claude* account. Search needs no LLM.
`digest` asks Haiku (through your Claude Code login, never a per-token API key) for a summary,
the questions a session answers and its exact atoms (errors, fixes, commands, decisions); search
matches those too, so "what was the fix for X" works without remembering the transcript's words.
"""
import json, os, re, sqlite3, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CLAUDE_HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
# One index for every Claude login on this machine (~/.claude, ~/.claude-work, ...):
# a session run on one login must be findable from all the others.
DB_PATH = Path(os.environ.get("BRAIN_RECALL_DB") or Path.home() / ".claude" / "brain-recall.db")
ROOTS = sorted({CLAUDE_HOME / "projects", *Path.home().glob(".claude*/projects")})
MAX_BODY = 30000
MODEL = os.environ.get("BRAIN_RECALL_MODEL", "haiku")  # digests only; search never calls a model
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)

SCHEMA = """
CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, size INT, offset INT, session TEXT, seq INT);
CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, project TEXT, title TEXT, first_prompt TEXT,
  started TEXT, ended TEXT, n INT DEFAULT 0);
CREATE VIRTUAL TABLE IF NOT EXISTS msgs USING fts5(body, session UNINDEXED, role UNINDEXED,
  ts UNINDEXED, seq UNINDEXED, tokenize='porter unicode61');
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS digests USING fts5(summary, body, session UNINDEXED, upto UNINDEXED,
  tokenize='porter unicode61');
"""


def connect(path=None):
    db = sqlite3.connect(str(path or DB_PATH), timeout=60)  # several accounts' sessions index at once
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(SCHEMA)
    return db


def text_of(rec):
    """User/assistant text with injected reminders stripped; '' for everything else."""
    if rec.get("type") not in ("user", "assistant") or rec.get("isMeta") or rec.get("isSidechain"):
        return ""
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    else:
        return ""
    return REMINDER.sub("", "\n".join(parts)).strip()[:MAX_BODY]


def index_file(db, path):
    """Index new complete lines of one transcript. Returns the number of messages added."""
    path = Path(path)
    size = path.stat().st_size
    row = db.execute("SELECT size, offset, session, seq FROM files WHERE path=?", (str(path),)).fetchone()
    if row and size == row[0]:
        return 0
    if row and size < row[0]:  # rewritten or truncated: start this session over
        db.execute("DELETE FROM msgs WHERE session=?", (row[2],))
        db.execute("DELETE FROM sessions WHERE id=?", (row[2],))
        row = None
    offset, seq, session = (row[1], row[3], row[2]) if row else (0, 0, None)
    with open(path, "rb") as fh:
        fh.seek(offset)
        chunk = fh.read()
    end = chunk.rfind(b"\n") + 1  # only complete lines; a half-written tail waits for next run
    added, title, first_prompt, first_ts, last_ts = 0, None, None, None, None
    for line in chunk[:end].splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        session = session or rec.get("sessionId")
        title = rec.get("title") or rec.get("aiTitle") if rec.get("type") == "ai-title" else title
        body = text_of(rec)
        if not body:
            continue
        ts = rec.get("timestamp") or ""
        first_ts = first_ts or ts
        last_ts = ts or last_ts
        if rec["type"] == "user" and not first_prompt:
            first_prompt = body[:200]
        seq += 1
        db.execute("INSERT INTO msgs(body, session, role, ts, seq) VALUES (?,?,?,?,?)",
                   (body, session, rec["type"], ts, seq))
        added += 1
    session = session or path.stem
    db.execute("""INSERT INTO sessions(id, project, title, first_prompt, started, ended, n)
                  VALUES (?,?,?,?,?,?,?)
                  ON CONFLICT(id) DO UPDATE SET
                    title=COALESCE(excluded.title, sessions.title),
                    first_prompt=COALESCE(sessions.first_prompt, excluded.first_prompt),
                    started=COALESCE(sessions.started, excluded.started),
                    ended=COALESCE(excluded.ended, sessions.ended),
                    n=sessions.n + excluded.n""",
               (session, path.parent.name, title, first_prompt, first_ts, last_ts, added))
    db.execute("INSERT OR REPLACE INTO files(path, size, offset, session, seq) VALUES (?,?,?,?,?)",
               (str(path), offset + end, offset + end, session, seq))
    return added


def index_all(db, root=None):
    total = 0
    paths = (p for r in ([Path(root)] if root else ROOTS) for p in sorted(r.glob("*/*.jsonl")))
    for path in paths:  # top level only: subagent transcripts are skipped
        try:
            total += index_file(db, path)
            db.commit()
        except OSError:
            continue
    db.execute("INSERT OR REPLACE INTO meta VALUES ('last_index', ?)", (time.strftime("%Y-%m-%d %H:%M"),))
    db.commit()
    return total


def fts_query(q, mode):
    words = re.findall(r"\w+", q)
    return f" {mode} ".join(f'"{w}"' for w in words)


def _epoch(ts):
    try:
        return time.mktime(time.strptime((ts or "")[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return time.time()


def search(db, q, n=8, since=None, raw=False):
    where, args = "msgs MATCH ?", []
    if since:
        where += " AND ts >= ?"
    queries = [q] if raw else [fts_query(q, "AND"), fts_query(q, "OR")]
    for fq in queries:
        if not fq:
            return []
        args = [fq] + ([since] if since else [])
        rows = db.execute(f"""SELECT session, role, ts, seq, snippet(msgs, 0, '[', ']', '…', 14), bm25(msgs)
                              FROM msgs WHERE {where} ORDER BY bm25(msgs) LIMIT 300""", args).fetchall()
        if rows:
            break
    hits, now = {}, time.time()
    for s, ts, rank in digest_hits(db, queries, since):
        rank = rank / (1 + max(0, now - _epoch(ts)) / 86400 / 365)
        hits[s] = {"session": s, "best": rank, "snips": []}
    for s, role, ts, seq, snip, rank in rows:
        rank = rank / (1 + max(0, now - _epoch(ts)) / 86400 / 365)  # recency weight: a year-old match counts half
        h = hits.setdefault(s, {"session": s, "best": 0, "snips": [], "m": 0})
        if rank < h.get("m", 0):  # best message match, added to any digest match: both = stronger
            h["best"], h["m"] = h["best"] - h.get("m", 0) + rank, rank
        if len(h["snips"]) < 3:
            h["snips"].append((seq, role, ts[:16], snip.replace("\n", " ")))
    out = sorted(hits.values(), key=lambda h: h["best"])[:n]
    for h in out:
        meta = db.execute("SELECT title, first_prompt, started, n FROM sessions WHERE id=?", (h["session"],)).fetchone()
        h["title"], h["first_prompt"], h["started"], h["n"] = meta or (None, None, "", 0)
        d = db.execute("SELECT summary FROM digests WHERE session=?", (h["session"],)).fetchone()
        h["summary"] = d[0] if d else None
    return out


def digest_hits(db, queries, since):
    for fq in queries:
        if not fq:
            return []
        rows = db.execute("""SELECT d.session, s.ended, bm25(digests) FROM digests d JOIN sessions s ON s.id=d.session
                             WHERE digests MATCH ?""" + (" AND s.ended >= ?" if since else "") +
                          " ORDER BY bm25(digests) LIMIT 50", [fq] + ([since] if since else [])).fetchall()
        if rows:
            return rows
    return []


DIGEST_PROMPT = """You index one work chat between a user and their AI assistant, so it can be found
later by keyword search. Return ONLY a JSON object, no prose, no code fence:
{"summary": "2-4 plain sentences: what was asked, what was done, how it ended. Name the people, clients, products, files and tools.",
 "questions": ["3-6 questions someone would later type to find this chat, in plain words"],
 "atoms": ["0-12 exact reusable facts the chat shows: a decision and its reason, an exact error and the fix that worked, a command that worked, a path, a price, a date, a number. Copy exact strings. Skip anything vague."]}
Write only what the transcript shows. Never guess."""


def transcript(db, sid, cap=40000):
    parts = []
    for role, body in db.execute("SELECT role, body FROM msgs WHERE session=? ORDER BY seq", (sid,)):
        parts.append(f"[{'User' if role == 'user' else 'Assistant'}] {body[:2500]}")
    text = "\n\n".join(parts)
    return text if len(text) <= cap else text[:cap // 4] + "\n\n[... middle cut ...]\n\n" + text[-cap * 3 // 4:]


def ask_haiku(text):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}  # your Claude Code login, never a per-token key
    r = subprocess.run(["claude", "-p", "--model", MODEL, "--no-session-persistence", "--tools", "",
                        "--setting-sources", "", "--system-prompt", DIGEST_PROMPT],
                       input=text, capture_output=True, text=True, timeout=300, env=env, cwd=tempfile.gettempdir())
    out = r.stdout.strip()
    m = re.search(r"\{.*\}", out, re.S)
    if r.returncode or not m:
        raise RuntimeError((out or r.stderr)[:200])
    d = json.loads(m.group(0))
    return d.get("summary", ""), "\n".join(d.get("questions", []) + d.get("atoms", []))


def digest(db, limit=50, workers=3, min_msgs=4):
    """Digest quiet sessions (no message for 1h) that have none yet, or have doubled since theirs."""
    cutoff = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - 3600))
    todo = db.execute("""SELECT s.id, s.n FROM sessions s LEFT JOIN digests d ON d.session=s.id
                         WHERE s.n >= ? AND s.ended < ? AND (d.session IS NULL OR s.n >= 2 * d.upto)
                         ORDER BY s.ended DESC LIMIT ?""", (min_msgs, cutoff, limit)).fetchall()
    done = fails = streak = 0
    with ThreadPoolExecutor(workers) as pool:
        jobs = [(sid, n, pool.submit(ask_haiku, transcript(db, sid))) for sid, n in todo]
        for sid, n, job in jobs:
            try:
                summary, body = job.result()
            except Exception as e:  # one bad session never stops the run; a quota wall does
                fails, streak = fails + 1, streak + 1
                print(f"skip {sid[:8]}: {e}", file=sys.stderr)
                if streak >= 5:  # five in a row = quota wall or CLI down: stop, the next run resumes
                    pool.shutdown(cancel_futures=True)
                    break
                continue
            db.execute("DELETE FROM digests WHERE session=?", (sid,))
            db.execute("INSERT INTO digests(summary, body, session, upto) VALUES (?,?,?,?)", (summary, body, sid, n))
            db.commit()
            done, streak = done + 1, 0
    left = db.execute("""SELECT COUNT(*) FROM sessions s LEFT JOIN digests d ON d.session=s.id
                         WHERE s.n >= ? AND d.session IS NULL""", (min_msgs,)).fetchone()[0]
    return done, fails, left


def read(db, prefix, around=None, start=None, n=20, full=False):
    row = db.execute("SELECT id, title, started FROM sessions WHERE id LIKE ? ORDER BY started DESC",
                     (prefix + "%",)).fetchone()
    if not row:
        return None, []
    sid = row[0]
    if around:
        hit = db.execute("SELECT seq FROM msgs WHERE session=? AND body LIKE ? ORDER BY seq LIMIT 1",
                         (sid, f"%{around}%")).fetchone()
        start = max(1, (hit[0] if hit else 1) - n // 2)
    start = start or 1
    msgs = db.execute("""SELECT seq, role, ts, body FROM msgs WHERE session=? AND seq >= ?
                         ORDER BY seq LIMIT ?""", (sid, start, n)).fetchall()
    cap = None if full else 1500
    return row, [(s, r, t[:16], b if cap is None else (b[:cap] + (" …" if len(b) > cap else ""))) for s, r, t, b in msgs]


def stats(db):
    s = db.execute("SELECT COUNT(*), MIN(started), MAX(ended) FROM sessions").fetchone()
    m = db.execute("SELECT COUNT(*) FROM msgs").fetchone()[0]
    last = db.execute("SELECT v FROM meta WHERE k='last_index'").fetchone()
    size = DB_PATH.stat().st_size / 1e6 if DB_PATH.exists() else 0
    return {"sessions": s[0], "messages": m, "from": (s[1] or "")[:10], "to": (s[2] or "")[:10],
            "last_index": last[0] if last else None, "db_mb": round(size, 1)}


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp, "projects", "D--Test")
        proj.mkdir(parents=True)
        f = proj / "s1.jsonl"
        recs = [
            {"type": "ai-title", "title": "Jarvis product call"},
            {"type": "user", "sessionId": "s1", "timestamp": "2026-10-13T08:00:00Z",
             "message": {"content": "<system-reminder>noise</system-reminder>We should build Jarvis for Windows"}},
            {"type": "user", "sessionId": "s1", "isMeta": True, "message": {"content": "skill body, skip me"}},
            {"type": "assistant", "sessionId": "s1", "timestamp": "2026-10-13T08:00:05Z",
             "message": {"content": [{"type": "thinking", "thinking": "hidden"},
                                     {"type": "text", "text": "Windows is 76 percent of desktops."}]}},
            {"type": "user", "sessionId": "s1", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
        ]
        f.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
        db = connect(Path(tmp, "t.db"))
        assert index_all(db, Path(tmp, "projects")) == 2
        assert index_all(db, Path(tmp, "projects")) == 0, "unchanged file must not reindex"
        hits = search(db, "windows desktops")
        assert hits and hits[0]["title"] == "Jarvis product call", hits
        assert not search(db, "hidden") and not search(db, "noise") and not search(db, "skip"), "skipped text leaked"
        with open(f, "a", encoding="utf-8") as fh:  # append a full line and a half-written one
            fh.write(json.dumps({"type": "user", "sessionId": "s1", "timestamp": "2026-10-13T09:00:00Z",
                                 "message": {"content": "remember the pricing: no free plan"}}) + "\n{\"type\": \"us")
        assert index_all(db, Path(tmp, "projects")) == 1
        _, msgs = read(db, "s1", around="pricing")
        assert any("no free plan" in m[3] for m in msgs) and [m[0] for m in msgs] == [1, 2, 3]
        assert db.execute("SELECT n FROM sessions WHERE id='s1'").fetchone()[0] == 3
        db.close()
    print("selftest ok")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "selftest":
        return selftest()

    def opt(name, default=None, cast=str):
        if name in rest:
            i = rest.index(name)
            v = rest[i + 1]
            del rest[i:i + 2]
            return cast(v)
        return default

    def flag(name):
        if name in rest:
            rest.remove(name)
            return True
        return False

    db = connect()
    if cmd == "index":
        print(f"indexed {index_all(db)} new messages · {stats(db)}")
    elif cmd == "search":
        n, since, raw = opt("-n", 8, int), opt("--since"), flag("--raw")
        index_all(db)
        hits = search(db, " ".join(rest), n, since, raw)
        if not hits:
            print("no matches")
        for h in hits:
            label = h["title"] or (h["first_prompt"] or "")[:90]
            print(f"\n■ {h['session'][:8]}  {(h['started'] or '')[:10]}  {label}  ({h['n']} msgs)")
            if h.get("summary"):
                print(f"   ⤷ {h['summary'][:400]}")
            for seq, role, ts, snip in h["snips"]:
                print(f"   #{seq} {role:9} {ts}  {snip[:320]}")
        print("\nread more: brain_recall.py read <id> --around \"<words>\"")
    elif cmd == "read":
        n, start, around, full = opt("-n", 20, int), opt("--from", None, int), opt("--around"), flag("--full")
        index_all(db)
        row, msgs = read(db, rest[0], around, start, n, full)
        if not row:
            print("no such session")
            return
        print(f"■ {row[0]}  {(row[2] or '')[:16]}  {row[1] or ''}")
        for seq, role, ts, body in msgs:
            print(f"\n--- #{seq} {role} {ts}\n{body}")
    elif cmd == "digest":
        limit, workers = opt("--limit", 50, int), opt("--workers", 3, int)
        index_all(db)
        done, fails, left = digest(db, limit, workers)
        print(f"digested {done}, failed {fails}, undigested sessions left {left}")
    elif cmd == "stats":
        print(json.dumps(stats(db), indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
