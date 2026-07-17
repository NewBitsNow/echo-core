# Project Echo

> Lightweight digital twin infrastructure for autonomous multi-agent systems.

Project Echo is an open-source framework for building persistent, policy-governed autonomous agents — a "digital twin" that works alongside you. It provides model routing, structured delegation, consent management, and a modular agent system — all designed to run locally with zero recurring cost.

## Quick Start

```bash
# Install from source
pip install -e .

# Launch the setup wizard
python -m echo_core.wizard

# Or use the CLI
python -m echo_core
```

## Architecture

```
User ←→ Orchestrator (cron) — delegates → Domain Agents
                    │
                    ├── Core Infrastructure
                    │   ├── classify_task()     — model routing
                    │   ├── build_packet()      — structured delegation
                    │   ├── read_consent()      — policy enforcement
                    │   ├── read_state()        — cycle tracking
                    │   └── log_agent()         — audit trail
                    │
                    ├── Domain Agents (optional)
                    │   ├── code_agent          — repo health, git checks
                    │   ├── content_agent       — YouTube summaries, blogs
                    │   ├── monitor_agent       — disk, files, drift
                    │   ├── research_agent      — arXiv, web research
                    │   ├── framehead_agent     — content generation
                    │   └── archiver_agent      — cleanup, compression
                    │
                    └── Consent Contract (YAML)
                        └── policy file governs every action
```

## Core API

```python
from echo_core import (
    classify_task,      # Task complexity → cheapest adequate model
    build_packet,       # Structured delegation packets
    read_consent,       # Consent contract reader
    read_state,         # System state file reader
    increment_cycle,    # Cycle counter for recurring work
    log_agent,          # Append-only agent audit log
    discover_modules,   # Module discovery and validation
)

# Route a task to the cheapest adequate model
result = classify_task("fix a typo in the README")
# → {"tier": "free", "model": "qwen/qwen3-coder:free", "complexity": 0.05}

# Build a structured delegation packet
packet = build_packet(
    mission="Add rate limiting to the API gateway",
    scope=["src/api/**"],
    verification_commands=["pytest tests/api/ -q"],
)

# Check the consent policy before acting
status = read_consent()
if status["status"] == "active":
    print("System is active — proceeding")

# Track cycles for recurring work
state = increment_cycle()
print(f"Cycle {state['current_cycle']}")

# Log every action for the audit trail
log_agent("orchestrator", "cycle_complete",
          {"summary": "All checks passed", "status": "completed"})
```

## Design Principles

1. **Consent-first** — Every agent checks a YAML policy file before acting. No action is taken without explicit permission.
2. **Cost-optimized** — Tasks are routed to the cheapest adequate model. Local models (Ollama) preferred over API calls.
3. **Auditable** — Every decision is logged to an append-only JSONL file. Nothing is hidden.
4. **Modular** — Domain agents are independent. Enable/disable them via the consent contract.
5. **Local-first** — Designed to run entirely on your machine. Zero cloud dependency for routine operations.

## Model Routing

Tasks are classified by complexity (0.0–1.0) and routed to the cheapest adequate tier:

| Tier | Cost | When | Model |
|------|------|------|-------|
| free | $0 | Simple edits, read-only queries | qwen3-coder:free |
| cheap-local | $0 | Small tasks, tests, code review | Local Ollama |
| paid-cheap | ~$0.0001/K | Medium tasks, docs | qwen3-coder |
| paid-premium | ~$0.015/K | Architecture, complex tasks | claude-sonnet-4 |
| escalation | — | Can't handle | Human operator |

Configure tiers in `src/echo_core/config/model-tiers.yaml`.

## Configuration

All configuration is done through:
1. **Consent contract** — YAML policy file defining domain permissions and global restrictions
2. **System state** — JSON file tracking cycle number, status, and escalation flags
3. **Model tiers** — YAML file defining routing tiers and model endpoints

Default paths are relative to `~/.echo-core/`. Override any path at runtime using the `set_*_path()` functions.

## Testing

```bash
cd echo-core/src
python -m pytest ../tests/ -v
```

## Project Structure

```
echo-core/
├── pyproject.toml           # Package metadata
├── LICENSE                  # MIT license
├── README.md                # This file
├── install.sh               # One-command installer
├── src/
│   └── echo_core/
│       ├── __init__.py      # Public API
│       ├── __main__.py      # CLI entry point
│       ├── wizard.py        # Setup wizard
│       ├── core/
│       │   ├── classify_task.py    # Model routing
│       │   ├── packet_builder.py   # Delegation packets
│       │   ├── routing_logger.py   # Cost tracking
│       │   ├── consent.py          # Contract reader
│       │   ├── state.py            # State file CRUD
│       │   ├── log.py              # Agent log writer
│       │   └── module_loader.py    # Module discovery
│       └── config/
│           └── model-tiers.yaml    # 5-tier model config
├── agents/                  # Domain agent scripts
├── tests/                   # Test suite (40+ tests)
├── examples/                # Example config files
└── docs/                    # Documentation
```

## License

MIT — see LICENSE for details.
