"""echo_core - Project Echo Core Infrastructure.

A lightweight, modular framework for building autonomous digital twin systems.
Provides model routing, structured delegation, consent management, state tracking,
and a setup wizard for installing modules.

Usage:
    pip install echo-core
    python -m echo_core          # CLI help
    python -m echo_core.wizard   # Setup wizard
"""

from echo_core.core.classify_task import classify_task
from echo_core.core.packet_builder import build_packet, packet_to_delegation
from echo_core.core.routing_logger import log_routing, summarize_routing
from echo_core.core.consent import (
    read_consent,
    check_consent,
    is_consent_valid,
    load_contract,
    consent_status,
)
from echo_core.core.state import (
    read_state,
    update_state,
    increment_cycle,
    system_status,
    init_state,
)
from echo_core.core.log import (
    log_agent,
    get_latest_logs,
    count_cycles,
    log_entry,
    get_logger,
)
from echo_core.core.module_loader import (
    discover_modules,
    load_module_manifest,
    module_status,
    validate_module,
    list_available_modules,
)

__version__ = "1.0.0"
__all__ = [
    "classify_task",
    "build_packet",
    "packet_to_delegation",
    "log_routing",
    "summarize_routing",
    "read_consent",
    "check_consent",
    "is_consent_valid",
    "load_contract",
    "consent_status",
    "read_state",
    "update_state",
    "increment_cycle",
    "system_status",
    "init_state",
    "log_agent",
    "get_latest_logs",
    "count_cycles",
    "log_entry",
    "get_logger",
    "discover_modules",
    "load_module_manifest",
    "module_status",
    "validate_module",
    "list_available_modules",
]