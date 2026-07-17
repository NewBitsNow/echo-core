"""Consent contract reader and validator.

Reads the YAML consent contract, validates structure, checks expiry,
and provides domain-level permission checks.

Every agent in the system must check consent before acting.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

# Default path, overridable via set_contract_path()
CONTRACT_PATH = Path("~/.echo-core/state/consent-contract.yaml").expanduser()


def load_contract(path: str = None) -> dict:
    """Load and parse the consent contract YAML file.

    Args:
        path: Override path to the consent contract.

    Returns:
        Dict representing the parsed YAML contract.

    Raises:
        FileNotFoundError: If the contract file doesn't exist.
        yaml.YAMLError: If the file is invalid YAML.
    """
    p = Path(path or CONTRACT_PATH).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Consent contract not found: {p}")
    with open(p) as f:
        return yaml.safe_load(f)


def is_consent_valid(contract: dict = None) -> bool:
    """Check if the consent contract is still valid (not expired).

    Args:
        contract: Parsed contract dict. Loaded if not provided.

    Returns:
        True if the contract is valid, False if expired.
    """
    if contract is None:
        try:
            contract = load_contract()
        except (FileNotFoundError, yaml.YAMLError):
            return False

    expiry = contract.get("expiry", {})
    duration_days = expiry.get("duration_days")
    if duration_days is None:
        return True  # No expiry set

    created_str = contract.get("created")
    if not created_str:
        return True

    try:
        created = datetime.fromisoformat(created_str)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        expiry_date = created + timedelta(days=duration_days)
        return datetime.now(timezone.utc) < expiry_date
    except (ValueError, TypeError):
        return True


def check_consent(domain: str, contract: dict = None) -> dict:
    """Check if a specific domain agent is enabled and permitted.

    Args:
        domain: Domain name (e.g. 'code', 'content', 'communications').
        contract: Parsed contract dict. Loaded if not provided.

    Returns:
        dict with keys: enabled (bool), domain (str), restrictions (list),
        tools (list), write_paths (list).
    """
    if contract is None:
        try:
            contract = load_contract()
        except (FileNotFoundError, yaml.YAMLError):
            return {"enabled": False, "domain": domain, "error": "contract_not_found"}

    domain_config = contract.get("domains", {}).get(domain, {})
    if not domain_config:
        return {"enabled": False, "domain": domain, "error": "domain_not_configured"}

    return {
        "enabled": domain_config.get("enabled", False),
        "domain": domain,
        "label": domain_config.get("label", domain),
        "tools": domain_config.get("tools", []),
        "write_paths": domain_config.get("write_paths", []),
        "restrictions": domain_config.get("restrictions", []),
    }


def read_consent(path: str = None) -> dict:
    """Read the consent contract and return full status.

    This is the primary function agents should call.
    Returns a dict with status, expiry, enabled domains, and global restrictions.
    """
    try:
        contract = load_contract(path)
    except FileNotFoundError:
        return {
            "status": "not_found",
            "error": f"Consent contract not found at {path or CONTRACT_PATH}",
        }
    except yaml.YAMLError as e:
        return {
            "status": "invalid",
            "error": f"Invalid YAML: {e}",
        }

    valid = is_consent_valid(contract)
    if not valid:
        return {
            "status": "expired",
            "twin_id": contract.get("twin_id"),
            "subject": contract.get("subject"),
            "error": "Consent contract has expired",
        }

    # Compute enabled domains
    enabled = {}
    for domain, config in contract.get("domains", {}).items():
        if config.get("enabled", False):
            enabled[domain] = {
                "label": config.get("label", domain),
                "tools": config.get("tools", []),
            }

    return {
        "status": "active",
        "twin_id": contract.get("twin_id"),
        "subject": contract.get("subject"),
        "created": contract.get("created"),
        "enabled_domains": enabled,
        "global_restrictions": contract.get("global_restrictions", []),
        "write_whitelist": contract.get("write_whitelist", []),
    }


def consent_status(path: str = None) -> str:
    """Quick one-line status check. Returns 'active', 'expired', or 'not_found'."""
    try:
        contract = load_contract(path)
        if is_consent_valid(contract):
            return "active"
        return "expired"
    except FileNotFoundError:
        return "not_found"
    except yaml.YAMLError:
        return "invalid"


def set_contract_path(path: str):
    """Override the default consent contract path."""
    global CONTRACT_PATH
    CONTRACT_PATH = Path(path).expanduser()