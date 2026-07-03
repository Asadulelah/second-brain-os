#!/usr/bin/env python3
"""
Pool Auto-Updater - UserPromptSubmit Hook
Continuously writes pool updates during long-running sessions.

Unlike pool-extractor.py (Stop hook, session-end only), this runs on EVERY
user prompt and extracts coordination signals from the conversation flow.

Works with persistent sessions (days/weeks long) by detecting:
- Task completions in previous assistant responses
- Explicit pool blocks (same as extractor)
- Implicit coordination signals (heuristic detection)

Environment variables:
  CLAUDE_INSTANCE        — identity of this instance
  CLAUDE_SESSION_ID      — current session identifier (set by Claude Code)
  CLAUDE_SESSION_ENV     — path to session directory (set by Claude Code)
"""
import json
import sys
import re
import os
import time
import uuid
import hashlib
from pathlib import Path
from datetime import datetime

# Pool file location (project-local preferred, global fallback)
PROJECT_POOL = Path(".claude/pool/instance_state.jsonl")
GLOBAL_POOL = Path.home() / ".claude/pool/instance_state.jsonl"

def get_pool_file():
    """Get pool file (project-local first, global fallback)."""
    if PROJECT_POOL.parent.parent.exists():  # Check if .claude/ exists
        PROJECT_POOL.parent.mkdir(parents=True, exist_ok=True)
        return PROJECT_POOL
    GLOBAL_POOL.parent.mkdir(parents=True, exist_ok=True)
    return GLOBAL_POOL

POOL_FILE = get_pool_file()
SESSION_ENV = Path(os.environ.get("CLAUDE_SESSION_ENV", ""))
COOLDOWN_FILE = SESSION_ENV / "last_pool_update.txt" if SESSION_ENV else None

# Minimum time between auto-updates (prevent spam)
COOLDOWN_SECONDS = 300  # 5 minutes

# === Explicit Pool Block Detection (same as extractor) ===

def extract_pool_block(text):
    """Extract explicit ```pool blocks."""
    pattern = r'```pool\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return parse_pool_block(match.group(1))
    return None

def parse_pool_block(block):
    """Parse pool block fields."""
    data = {}
    for line in block.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip().lower()] = value.strip()
    return data

# === Implicit Signal Detection (heuristic) ===

def detect_implicit_signals(text):
    """
    Detect coordination-worthy events from conversation flow.
    Returns (action, topic, summary) or None.
    """
    text_lower = text.lower()

    # Completion signals
    completion_patterns = [
        (r'(fixed|resolved|completed|deployed|merged|pushed)\s+([^.!?\n]{10,80})', 'completed'),
        (r'(successfully|✓|✅)\s+([^.!?\n]{10,80})', 'completed'),
        (r'(implementation|fix|feature)\s+(done|complete|finished)', 'completed'),
    ]

    # Blocker signals
    blocker_patterns = [
        (r'(blocked by|cannot|unable to|waiting for)\s+([^.!?\n]{10,80})', 'blocked'),
        (r'(error|failure|crash|bug)\s+in\s+([^.!?\n]{10,80})', 'blocked'),
    ]

    # Signaling patterns
    signal_patterns = [
        (r'(discovered|found|noticed)\s+([^.!?\n]{10,80})', 'signaling'),
        (r'(warning|note|fyi):\s+([^.!?\n]{10,80})', 'signaling'),
    ]

    # Check patterns in order of priority
    for patterns, action in [(completion_patterns, 'completed'),
                              (blocker_patterns, 'blocked'),
                              (signal_patterns, 'signaling')]:
        for pattern, detected_action in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                topic = match.group(2).strip()
                # Clean up topic
                topic = re.sub(r'\s+', ' ', topic)
                topic = topic[:60]  # Limit length

                # Extract summary (sentence containing the match)
                sentences = re.split(r'[.!?]\s+', text)
                for sentence in sentences:
                    if topic.lower() in sentence.lower():
                        summary = sentence.strip()[:200]
                        return (detected_action, topic, summary)

    return None

# === Relevance Scoring ===

def compute_relevance(topic, summary, affects):
    """
    Score relevance to each instance domain.

    Keys should match your CLAUDE_INSTANCE values. Customize these domain
    keywords to reflect your project's structure and multi-agent setup.

    Example setup for a web project:
      "frontend" — UI/design/component work
      "backend"  — API/server/database work
      "data"     — pipeline/analytics/ML work
      "infra"    — deployment/CI/config work
    """
    domains = {
        "frontend": ["ui", "interface", "component", "design", "style", "layout", "view", "css", "react"],
        "backend":  ["api", "server", "endpoint", "database", "query", "auth", "service", "route", "model"],
        "data":     ["pipeline", "transform", "schema", "migration", "index", "analytics", "etl", "batch"],
        "infra":    ["deploy", "docker", "ci", "build", "config", "environment", "cloud", "terraform", "k8s"],
    }

    relevance = {}
    text = f"{topic} {summary} {affects}".lower()

    for instance, keywords in domains.items():
        matches = sum(1 for kw in keywords if kw in text)
        score = min(matches / len(keywords) * 2, 1.0)
        relevance[instance] = round(score, 2)

    return relevance

# === Pool Entry Writing ===

def write_pool_entry(action, topic, summary, affects="", blocks=""):
    """Write entry to pool."""
    instance_id = os.environ.get("CLAUDE_INSTANCE", "?")

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "source_instance": instance_id,
        "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown")[:8],
        "action": action,
        "topic": topic[:60],
        "summary": summary[:200],
        "relevance": compute_relevance(topic, summary, affects),
        "affects": affects,
        "blocks": blocks,
        "ttl": 3600,
        "raw_hash": hashlib.sha256(f"{topic}{summary}".encode()).hexdigest()[:16]
    }

    # Append to pool
    POOL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(POOL_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry

# === Cooldown Management ===

def check_cooldown():
    """Check if enough time has passed since last auto-update."""
    if not COOLDOWN_FILE or not COOLDOWN_FILE.exists():
        return True

    try:
        last_update = float(COOLDOWN_FILE.read_text().strip())
        return (time.time() - last_update) > COOLDOWN_SECONDS
    except:
        return True

def update_cooldown():
    """Record time of this update."""
    if COOLDOWN_FILE:
        COOLDOWN_FILE.write_text(str(time.time()))

# === Main Logic ===

def get_last_assistant_response():
    """Get last assistant message from current session."""
    if not SESSION_ENV:
        return ""

    transcript = SESSION_ENV / "transcript.jsonl"
    if not transcript.exists():
        return ""

    try:
        with open(transcript) as f:
            lines = f.readlines()

        # Find last assistant message
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get("type") == "assistant" or entry.get("role") == "assistant":
                    content = entry.get("message", {}).get("content", [])
                    if not content:
                        content = entry.get("content", [])

                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            text_parts.append(block)

                    return "\n".join(text_parts)
            except:
                continue
    except:
        pass

    return ""

def main():
    """Main entry point."""
    # Get last assistant response
    last_response = get_last_assistant_response()
    if not last_response:
        return

    # Check for explicit pool block first (takes priority)
    explicit = extract_pool_block(last_response)
    if explicit:
        write_pool_entry(
            action=explicit.get("action", "signaling"),
            topic=explicit.get("topic", "Pool update"),
            summary=explicit.get("summary", ""),
            affects=explicit.get("affects", ""),
            blocks=explicit.get("blocks", "")
        )
        update_cooldown()
        return

    # Check cooldown before implicit detection (prevent spam)
    if not check_cooldown():
        return

    # Try implicit signal detection
    implicit = detect_implicit_signals(last_response)
    if implicit:
        action, topic, summary = implicit
        write_pool_entry(
            action=action,
            topic=topic,
            summary=summary,
            affects="auto-detected",
            blocks=""
        )
        update_cooldown()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Silent fail - don't block conversation
        error_log = Path.home() / ".claude/pool/auto_update_errors.log"
        with open(error_log, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {e}\n")
