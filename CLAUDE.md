# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install
pip install -e .
pip install -e ".[dev]"          # with pytest, pytest-env, pytest-asyncio, python-dotenv

# Run tests
pytest                           # all tests
pytest tests/test_cron.py        # single file
pytest -v                        # verbose

# Run the agent
python agent/main.py             # unified entry (Web API + Feishu + Heartbeat + Cron + Memory)
python -m agent.cli              # interactive CLI REPL
python -m agent.webapp           # Web API only (port 8000)

# Docker
docker build -t cai-coder:0.2 .
docker compose up -d
```

Tests use `asyncio_mode = "auto"` (no `@pytest.mark.asyncio` needed) and load env vars from `.local.env` via `pytest-env`.

## Architecture

**cai-coder** is an AI coding agent (Python 3.11+, LangChain, LangGraph) with progressive skill loading, multi-agent dispatching, three-layer long-term memory, and IM channel integrations.

### Core Data Flow

```
Channel (feishu/cli/web) → MessageBus.inbound → AgentLoop → Agent → MessageBus.outbound → Channel.send()
```

- **MessageBus** (`agent/bus/bus.py`): Two `queue.Queue` instances — inbound/outbound. Central decoupling point.
- **AgentLoop** (`agent/server.py`): Daemon thread consuming inbound, invoking the agent, publishing outbound. Per-chat sequential processing.
- **BaseChannel** (`agent/integration/base.py`): ABC for platform integrations. Register new channels in `agent/integration/register.py`.

### Key Subsystems

| Subsystem | Location | Role |
|---|---|---|
| Agent factory + AgentLoop | `agent/server.py` | Creates LLM, tools, middleware; runs agent loop |
| System prompt | `agent/prompt.py` | Modular sections assembled into prompt |
| Long-term memory | `agent/memory/` | L1 (daily logs), L2 (rolling summaries, planned), L3 (persistent knowledge in `long-term/`) |
| Multi-agent dispatching | `agent/multi_agent/` | LLM-based routing to specialized agents (code-review, bug-fix, devops, general) |
| Sub-agent factory | `agent/subagents/service.py` | `get_sub_agent()`, `get_memory_agent()` for isolated instances |
| Cron service | `agent/cron/service.py` | Scheduled tasks (one-time `at` or periodic `every`) via `add_cronjob` tool |
| Heartbeat service | `agent/heartbeat/heatbeat.py` | Reads `HEARTBEAT.md` every 30min, LLM decides whether to act |
| Skills | `skills/*/SKILL.md` | On-demand loaded via `SkillMiddleware`; YAML frontmatter + markdown instructions |
| Session manager | `agent/session/manager.py` | Tracks `{channel}:{chat_id}` sessions in `sessions/sessions.json` |

### Middleware Stack (order matters, configured in `server.py`)

SkillMiddleware → MemoryMiddleware → TodoListMiddleware → ToolRetryMiddleware → ModelRetryMiddleware → SummarizationMiddleware → ContextEditingMiddleware → ConversationSummarizerMiddleware

### Extending Patterns

- **New tool**: Create module in `agent/tools/` with `@tool` decorator → export from `__init__.py` → register in `server.py`
- **New skill**: Create dir under `skills/` with `SKILL.md` (YAML frontmatter `name`/`description` + markdown body) → auto-discovered by `SkillMiddleware`
- **New channel**: Implement `BaseChannel` in `agent/integration/<platform>/` → register in `agent/integration/register.py`
- **New middleware**: Implement `AgentMiddleware` → add to list in `server.py`
- **New specialized agent**: Define `AgentDefinition` → register via `agent_registry.register()` in `agent/multi_agent/registry.py`

## Conventions

- Config via env vars in `.local.env` (never committed): `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, optionally `FEISHU_APP_ID`, `FEISHU_APP_SECRET`
- Logging: loguru via `get_logger(name)` from `agent/utils/logger.py`
- Code identifiers and error messages in English; user-facing explanations in Chinese
- IM responses must use `send_im_messages` tool (not plain text) for proper bus routing
- Memory writes use atomic file operations (`tempfile` + `os.replace`)
- Dockerfile uses Tsinghua PyPI mirror for China builds
- `agent/tools/delegate_agent.py` added for multi-agent dispatching — it's a `BaseTool` (not `@tool`) because it holds state