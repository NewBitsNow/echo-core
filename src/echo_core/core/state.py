"""System state file CRUD — tracks cycle number, status, and flags.

The state file is a lightweight JSON file that the orchestrator reads and
writes each cycle. Agents read it for context but should never modify it.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Default path, overridable via set_state_path()
STATE_PATH = Path("~/.echo-core/state/system-state.json").expanduser()


def read_state(path: str = None) -> dict:
    """Read the current system state.

    Args:
        path: Override path to the state file.

    Returns:
        Dict with system state, or a default dict if the file doesn't exist.
    """
    p = Path(path or STATE_PATH).expanduser()
    if not p.exists():
        return {
            "twin_id": "unknown",
            "status": "uninitialized",
            "current_cycle": 0,
            "last_wake": None,
        }
    try:
        with open(p) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {
            "twin_id": "unknown",
            "status": "corrupted",
            "current_cycle": 0,
            "last_wake": None,
        }


def update_state(updates: dict, path: str = None) -> dict:
    """Update specific fields in the system state and save.

    Args:
        updates: Dict of fields to update.
        path: Override path to the state file.

    Returns:
        The updated state dict.
    """
    state = read_state(path)
    state.update(updates)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()

    p = Path(path or STATE_PATH).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(state, f, indent=2)

    return state


def increment_cycle(path: str = None) -> dict:
    """Increment the cycle counter and update the last_wake timestamp.

    This is the primary action the orchestrator takes each cycle.

    Returns:
        The updated state dict with the new cycle number.
    """
    return update_state({
        "current_cycle": read_state(path).get("current_cycle", 0) + 1,
        "last_wake": datetime.now(timezone.utc).isoformat(),
    }, path=path)


def system_status(path: str = None) -> str:
    """Quick one-line status check. Returns 'active', 'paused', 'revoked', etc."""
    state = read_state(path)
    return state.get("status", "unknown")


def init_state(
    twin_id: str = "echo-twin-v1",
    twin_name: str = "Project Echo Twin",
    path: str = None,
) -> dict:
    """Initialize a fresh state file.

    Args:
        twin_id: Unique identifier for this twin.
        twin_name: Human-readable name.
        path: Override path to the state file.

    Returns:
        The initialized state dict.
    """
    state = {
        "twin_id": twin_id,
        "twin_name": twin_name,
        "status": "active",
        "current_cycle": 0,
        "last_wake": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None,
        "last_report_sent": None,
        "active_domains": [],
        "pending_escalations": [],
        "consent_contract_hash": None,
    }

    p = Path(path or STATE_PATH).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(state, f, indent=2)

    return state


def set_state_path(path: str):
    """Override the default state file path."""
    global STATE_PATH
    STATE_PATH = Path(path).expanduser()