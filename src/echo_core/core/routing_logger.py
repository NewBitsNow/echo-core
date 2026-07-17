"""Routing logger — logs every model routing decision to a JSONL file
and provides a summary dashboard for cost tracking.

Moved from Project Echo scripts into echo_core.core.
Original: ~/.echo-core/scripts/routing_logger.py
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter

# Default path, overridable via set_log_path()
LOG_PATH = Path("~/.echo-core/logs/routing-log.jsonl").expanduser()


def log_routing(
    task_id: str,
    task_description: str,
    tier: str,
    model: str,
    provider: str,
    complexity: float,
) -> dict:
    """Append a routing decision to the log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "task_description": task_description[:100],
        "tier": tier,
        "model": model,
        "provider": provider,
        "complexity": complexity,
    }

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def summarize_routing(days: int = 7, json_output: bool = False) -> dict | str:
    """Print or return a summary of routing decisions.

    Args:
        days: Number of days to look back.
        json_output: If True, return dict instead of printing.

    Returns:
        Printed summary string or dict with stats.
    """
    if not LOG_PATH.exists():
        msg = "No routing data yet."
        if json_output:
            return {"status": "empty", "message": msg}
        return msg

    tiers = Counter()
    models = Counter()
    total = 0

    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts < cutoff:
                continue
            tiers[entry["tier"]] += 1
            models[entry["model"] or "none"] += 1
            total += 1

    if json_output:
        return {
            "status": "ok",
            "total_tasks": total,
            "tier_breakdown": dict(tiers.most_common()),
            "model_breakdown": dict(models.most_common()),
            "free_tier_count": tiers.get("free", 0) + tiers.get("cheap-local", 0),
            "paid_tier_count": tiers.get("paid-cheap", 0) + tiers.get("paid-premium", 0),
            "escalation_count": tiers.get("escalation", 0),
        }

    print(f"=== Routing Summary (last {days}d) ===")
    print(f"Total tasks: {total}")
    print()
    if total == 0:
        print("No routing events in this period.")
        return

    for tier, count in tiers.most_common():
        pct = count / total * 100
        print(f"  {tier}: {count} ({pct:.0f}%)")
    print()
    free = tiers.get("free", 0) + tiers.get("cheap-local", 0)
    paid = tiers.get("paid-cheap", 0) + tiers.get("paid-premium", 0)
    print(f"  Free tier usage:  {free} tasks ($0.0000)")
    print(f"  Paid tier usage:  {paid} tasks")
    print(f"  Escalations:      {tiers.get('escalation', 0)} tasks")
    if total > 0:
        print(f"  Offload rate:     {free / total * 100:.0f}% (free/total)")


def set_log_path(path: str):
    """Override the default routing log path."""
    global LOG_PATH
    LOG_PATH = Path(path).expanduser()