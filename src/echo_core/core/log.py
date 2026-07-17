"""Append-only agent log writer with schema validation.

Every agent action is logged to a shared JSONL file. The log is append-only
— never deleted, never modified. This is the system's audit trail.

All agents use this module to log their actions.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Default path, overridable via set_log_path()
AGENT_LOG_PATH = Path("~/.echo-core/logs/agent-log.jsonl").expanduser()

# Standard Python logger for console output
logger = logging.getLogger("echo_core")


def log_agent(
    agent_name: str,
    action: str,
    details: dict = None,
    path: str = None,
) -> dict:
    """Append a structured entry to the agent log.

    This is the primary logging function all agents should use.

    Args:
        agent_name: Name of the agent (e.g. 'orchestrator', 'code-agent').
        action: Action being logged (e.g. 'cycle_start', 'checkin', 'generate').
        details: Dict of additional fields to include in the log entry.
        path: Override path to the log file.

    Returns:
        The log entry dict that was written.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "action": action,
        **(details or {}),
    }

    p = Path(path or AGENT_LOG_PATH).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)

    # Append — never overwrite
    with open(p, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def log_entry(entry: dict, path: str = None) -> dict:
    """Write a pre-built entry dict to the log. Useful for complex entries.

    Args:
        entry: Dict to write. Must be JSON-serializable.
        path: Override path to the log file.

    Returns:
        The entry dict.
    """
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()

    p = Path(path or AGENT_LOG_PATH).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(p, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def get_latest_logs(n: int = 10, path: str = None) -> list[dict]:
    """Read the N most recent log entries.

    Args:
        n: Number of entries to return.
        path: Override path to the log file.

    Returns:
        List of dicts, most recent first.
    """
    p = Path(path or AGENT_LOG_PATH).expanduser()
    if not p.exists():
        return []

    entries = []
    try:
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []

    return entries[-n:][::-1]  # Most recent first


def count_cycles(agent: str = "orchestrator", path: str = None) -> int:
    """Count how many cycles an agent has completed.

    Args:
        agent: Agent name to count cycles for.
        path: Override path to the log file.

    Returns:
        Number of cycle_complete actions for the given agent.
    """
    p = Path(path or AGENT_LOG_PATH).expanduser()
    if not p.exists():
        return 0

    count = 0
    try:
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if (entry.get("agent") == agent
                            and entry.get("action") == "cycle_complete"):
                        count += 1
                except json.JSONDecodeError:
                    continue
    except OSError:
        return 0

    return count


def get_logger(name: str = None) -> logging.Logger:
    """Get a standard Python logger for console output during agent runs.

    Usage:
        log = get_logger("framehead")
        log.info("Generating observation...")
        log.warning("No images found, skipping")
        log.error("Generation failed: %s", e)
    """
    log = logging.getLogger(f"echo_core.{name}" if name else "echo_core")
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        ))
        log.addHandler(handler)
        log.setLevel(logging.INFO)
    return log


def set_agent_log_path(path: str):
    """Override the default agent log path."""
    global AGENT_LOG_PATH
    AGENT_LOG_PATH = Path(path).expanduser()