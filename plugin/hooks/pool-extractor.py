#!/usr/bin/env python3
"""
Pool Extractor - Stop Hook
Extracts ```pool blocks from assistant responses and writes to instance pool.

When a Claude Code session ends (Stop hook), this script reads the transcript,
finds any ```pool blocks in the last assistant response, and writes a structured
entry to the shared instance pool JSONL file.

```pool blocks are written by Claude when it wants to signal state to other
instances. Format:
  ```pool
  action: completed
  topic: feature X
  summary: Implemented the login flow
  affects: src/auth/
  blocks: PR #42
  ```

Environment variables:
  CLAUDE_INSTANCE    — identity of this instance
  CLAUDE_SESSION_ID  — current session identifier (set by Claude Code)
"""
import json
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime
import hashlib
import uuid
import os

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
ACTIVE_INSTANCES = POOL_FILE.parent / "active_instances.json"

def extract_pool_block(text):
    """Extract structured pool update from response."""
    pattern = r'```pool\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return parse_pool_block(match.group(1))
    return None

def parse_pool_block(block):
    """Parse pool block into structured data."""
    data = {}
    for line in block.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip().lower()] = value.strip()
    return data

def get_last_assistant_response(transcript_path):
    """Get last assistant message from transcript."""
    if not Path(transcript_path).exists():
        return ""

    with open(transcript_path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Look for last assistant message
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            if entry.get("type") == "assistant" or entry.get("role") == "assistant":
                # Handle both formats
                content = entry.get("message", {}).get("content", [])
                if not content:
                    content = entry.get("content", [])

                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif "text" in block:
                            text_parts.append(block["text"])
                    elif isinstance(block, str):
                        text_parts.append(block)

                result = "\n".join(text_parts)
                if result:
                    return result
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    return ""

def compress_summary(text, max_chars=200):
    """Compress summary to fit within character limit."""
    if len(text) <= max_chars:
        return text

    # Smart truncation - try to keep complete sentences
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars // 2:
        return truncated[:last_period + 1]
    else:
        return truncated + "..."

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
        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in text)
        score = min(matches / len(keywords) * 2, 1.0)
        relevance[instance] = round(score, 2)

    return relevance

def get_instance_id():
    """Get current instance ID from env or active registration."""
    instance_id = os.environ.get("CLAUDE_INSTANCE")
    if instance_id:
        return instance_id

    # Default to unknown if not set
    return "?"

def write_pool_entry(entry):
    """Append entry to pool."""
    POOL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(POOL_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    try:
        # Read hook input
        input_data = json.load(sys.stdin)
        transcript_path = input_data.get("transcript_path")
        session_id = input_data.get("session_id", "unknown")

        if not transcript_path:
            # No transcript path - suppress output and exit
            print(json.dumps({"suppressOutput": True}))
            sys.exit(0)

        # Get last assistant response
        response = get_last_assistant_response(transcript_path)
        if not response:
            print(json.dumps({"suppressOutput": True}))
            sys.exit(0)

        # Extract pool data
        pool_data = extract_pool_block(response)
        if not pool_data:
            # No pool update in this response
            print(json.dumps({"suppressOutput": True}))
            sys.exit(0)

        # Build entry
        summary = pool_data.get("summary", "")
        if len(summary) > 200:
            summary = compress_summary(summary)

        topic = pool_data.get("topic", "unknown")
        affects = pool_data.get("affects", "")

        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": int(datetime.now().timestamp()),
            "source_instance": get_instance_id(),
            "session_id": session_id[:8],  # Truncate for privacy
            "action": pool_data.get("action", "signaling"),
            "topic": topic,
            "summary": summary,
            "relevance": compute_relevance(topic, summary, affects),
            "affects": affects,
            "blocks": pool_data.get("blocks", ""),
            "ttl": 3600,  # 1 hour
            "raw_hash": hashlib.sha256(response.encode()).hexdigest()[:16]
        }

        # Write to pool
        write_pool_entry(entry)

        # Suppress output (don't show in transcript)
        print(json.dumps({"suppressOutput": True}))

    except Exception as e:
        # Fail gracefully - don't block hook
        import traceback
        log_path = Path.home() / ".claude/pool/extractor_errors.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"{datetime.now()}: {e}\n")
            traceback.print_exc(file=f)
        print(json.dumps({"suppressOutput": True}))

    sys.exit(0)

if __name__ == "__main__":
    main()
