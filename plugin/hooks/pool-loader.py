#!/usr/bin/env python3
"""
Pool Loader - SessionStart Hook
Loads recent, relevant pool entries and formats them for context injection.

The instance pool is a shared JSONL file where Claude Code instances signal
their activity. On session start, this hook injects recent relevant activity
into context so the new session knows what other instances are doing.

Environment variables:
  CLAUDE_INSTANCE  — identity of this instance (e.g., "main", "worker-1")
  POOL_COMPACT     — set to "0" for full output, "1" (default) for compact summary
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Pool file location (project-local preferred, global fallback)
PROJECT_POOL = Path(".claude/pool/instance_state.jsonl")
GLOBAL_POOL = Path.home() / ".claude/pool/instance_state.jsonl"

def get_pool_file():
    """Get pool file (project-local first, global fallback)."""
    if PROJECT_POOL.parent.parent.exists():  # Check if .claude/ exists
        return PROJECT_POOL if PROJECT_POOL.exists() else GLOBAL_POOL
    return GLOBAL_POOL

POOL_FILE = get_pool_file()
MAX_ENTRIES = 20
MAX_AGE_SECONDS = 3600  # 1 hour

def get_instance_id():
    """Get current instance ID from env."""
    return os.environ.get("CLAUDE_INSTANCE", "?")

def load_recent_pool():
    """Load recent, relevant pool entries."""
    if not POOL_FILE.exists():
        return []

    now = datetime.now().timestamp()
    entries = []
    instance_id = get_instance_id()

    with open(POOL_FILE) as f:
        for line in f:
            try:
                entry = json.loads(line)

                # Filter by age
                entry_age = now - entry.get("timestamp", 0)
                if entry_age > MAX_AGE_SECONDS:
                    continue

                # Filter by relevance to this instance
                relevance = entry.get("relevance", {}).get(instance_id, 0)
                source = entry.get("source_instance", "?")

                # Include if:
                # 1. From this instance (own history)
                # 2. High relevance (>= 0.3)
                # 3. Blocks something (always relevant)
                if source == instance_id or relevance >= 0.3 or entry.get("blocks"):
                    entries.append(entry)

            except json.JSONDecodeError:
                continue

    # Sort by timestamp desc, take most recent
    entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return entries[:MAX_ENTRIES]

def format_time_ago(seconds):
    """Format seconds as human-readable time ago."""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)}m ago"
    else:
        return f"{int(seconds / 3600)}h ago"

def format_pool_context(entries):
    """Format entries for injection."""
    if not entries:
        return ""

    instance_id = get_instance_id()
    now = datetime.now().timestamp()

    lines = [
        "## Recent Instance Activity",
        f"> You are Instance **{instance_id}** in a distributed development system.",
        "> Recent work by you and other instances:\n"
    ]

    for entry in entries:
        time_ago = format_time_ago(now - entry.get("timestamp", 0))
        source = entry.get("source_instance", "?")
        action = entry.get("action", "signaling")
        topic = entry.get("topic", "unknown")
        summary = entry.get("summary", "")
        affects = entry.get("affects", "")
        blocks = entry.get("blocks", "")
        relevance = entry.get("relevance", {}).get(instance_id, 0)

        # Format based on source
        if source == instance_id:
            prefix = "🔵 **[YOU]**"
        else:
            prefix = f"🟢 **[{source}]**"

        # Format action
        action_emoji = {
            "completed": "✅",
            "blocked": "🚫",
            "signaling": "📡",
            "claimed": "🔒",
            "health": "💚"
        }.get(action, "📌")

        lines.append(f"{prefix} {action_emoji} **{action}** — {topic}")
        lines.append(f"  _{summary}_")

        if affects:
            lines.append(f"  📂 Affects: `{affects}`")

        if blocks:
            lines.append(f"  🔓 Unblocks: {blocks}")

        lines.append(f"  🕐 {time_ago} | Relevance: {relevance:.0%}\n")

    lines.append("---\n")

    return "\n".join(lines)

def get_project_name():
    """Detect project name from various sources."""
    import subprocess

    # Try 1: Git remote URL
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Extract repo name from URL (handles both HTTPS and SSH)
            # https://github.com/user/repo.git -> repo
            # git@github.com:user/repo.git -> repo
            if url:
                name = url.rstrip("/").split("/")[-1].replace(".git", "")
                if name:
                    return name
    except:
        pass

    # Try 2: Git repo root directory name
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            repo_path = result.stdout.strip()
            if repo_path:
                name = os.path.basename(repo_path)
                if name:
                    return name
    except:
        pass

    # Try 3: Current working directory name
    cwd_name = os.path.basename(os.getcwd())
    if cwd_name:
        return cwd_name

    # Fallback
    return "Current Project"

def format_compact_output():
    """Format compact output for SessionStart hook."""
    entries = load_recent_pool()

    if not entries:
        project_name = get_project_name()
        return f"## Session Context\n- **Codebase**: {project_name}\n- **Instance Pool**: No recent activity\n"

    # Get counts
    instance_id = get_instance_id()
    own_count = sum(1 for e in entries if e.get("source_instance") == instance_id)
    other_count = len(entries) - own_count
    blocked_count = sum(1 for e in entries if e.get("action") == "blocked")
    completed_count = sum(1 for e in entries if e.get("action") == "completed")

    # Compact summary
    lines = [
        "## Session Context",
        f"- **Instance**: {instance_id}",
        f"- **Pool**: {len(entries)} recent ({own_count} own, {other_count} others)",
        f"- **Status**: {completed_count} completed, {blocked_count} blocked"
    ]

    # Show only most relevant/recent 5
    top_entries = entries[:5]
    if top_entries:
        lines.append("\n### Recent Activity")
        for entry in top_entries:
            source = entry.get("source_instance", "?")
            action = entry.get("action", "")
            topic = entry.get("topic", "")
            lines.append(f"- [{source}] {action}: {topic}")

    return "\n".join(lines) + "\n"

def main():
    try:
        # Check if we want compact or full output
        compact = os.environ.get("POOL_COMPACT", "1") == "1"

        if compact:
            output = format_compact_output()
        else:
            entries = load_recent_pool()
            output = format_pool_context(entries)

        if output:
            print(output)

    except Exception as e:
        # Fail gracefully - don't block session start
        import traceback
        with open(Path.home() / ".claude/pool/loader_errors.log", "a") as f:
            f.write(f"{datetime.now()}: {e}\n")
            traceback.print_exc(file=f)

    sys.exit(0)

if __name__ == "__main__":
    main()
