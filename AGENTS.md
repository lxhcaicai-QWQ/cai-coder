<!-- This file is managed by AI agents. Do not manually edit unless necessary. -->

# AGENTS.md — cai-coder

## Project Overview

**cai-coder** is an AI coding agent built with **Python 3.11+**, powered by **LangChain** + **LangGraph**. It features a progressive skill-loading mechanism, a set of built-in tools (file I/O, shell, HTTP, weather), MCP tool integration, a middleware-based architecture for extensible agent behavior, an OpenAI-compatible Web API via FastAPI, a **Feishu (Lark) bot integration** for chat-based interaction, a **heartbeat service** for periodic task execution, and a **session manager** for tracking conversations across channels.

- **Primary language**: Python 3.11+
- **Key frameworks**: LangChain (`>=1.2.9`), LangGraph (`>=1.0.8`), langchain-openai (`==1.1.10`), FastAPI (`>=0.115.0`)
- **Key libraries**: langgraph-checkpoint-sqlite (`>=3.0.3`), langchain-mcp-adapters (`>=0.2.0`), lark-oapi (`>=1.0.0`), pyyaml (`>=6.0`), requests (`>=2.31.0`), uvicorn (`>=0.32.0`), loguru (`>=0.7.0`)
- **Build system**: Hatchling (`pyproject.toml`)
- **Logging**: loguru (configured in `agent/utils/logger.py`, level via `LOG_LEVEL` env var)

## Project Structure

```
cai-coder/
├── agent/                   # Core agent package
│   ├── main.py              # Unified entry: MessageBus + ChannelManager + AgentLoop + HeartbeatService + Web API
│   ├── cli.py               # CLI entry point (interactive async REPL)
│   ├── server.py            # Agent factory (LLM, tools, middleware, memory) + AgentLoop
│   ├── prompt.py            # System prompt construction (modular sections)
│   ├── webapp.py            # OpenAI-compatible Web API (FastAPI + SSE streaming)
│   ├── bus/                 # Message bus for channel-agent communication
│   │   ├── bus.py           # MessageBus (inbound/outbound queues)
│   │   └── events.py        # InMessage / OutMessage dataclasses
│   ├── middleware/           # Agent middleware
│   │   ├── __init__.py      # Middleware exports
│   │   └── skill_middleware.py  # SkillMiddleware — progressive skill loading
│   ├── tools/               # Built-in tools
│   │   ├── __init__.py      # Tool exports
│   │   ├── bash.py
│   │   ├── get_weather.py
│   │   ├── http_request.py  # http_request, http_get, http_post
│   │   ├── ls.py
│   │   ├── read_file.py
│   │   └── write_file.py
│   ├── skills/              # Skill definitions (each subdir has SKILL.md)
│   │   ├── agents-md-generator/
│   │   ├── python-patterns/
│   │   └── python-testing/
│   ├── heartbeat/           # Heartbeat service for periodic task execution
│   │   ├── __init__.py
│   │   └── heatbeat.py      # HeartbeatService — reads HEARTBEAT.md, decides via LLM, executes tasks
│   ├── session/             # Session management for multi-channel conversations
│   │   ├── __init__.py      # Exports Session, SessionManager
│   │   └── manager.py       # SessionManager — CRUD for sessions persisted to sessions.json
│   ├── templates/           # Workspace template files (copied to WORKING_DIR on startup)
│   │   └── HEARTBEAT.md     # Default heartbeat task template
│   ├── integration/         # External platform integrations (channel abstraction)
│   │   ├── base.py          # BaseChannel ABC (send, start, _handle_message)
│   │   ├── manager.py       # ChannelManager (discovers, starts, dispatches)
│   │   ├── register.py      # Channel registry (discovers all channels)
│   │   └── feishu/          # Feishu (Lark) channel
│   │       ├── bot.py       # FeishuChannel(BaseChannel): WS bot, reactions, reply
│   │       └── config.py    # Feishu app credentials & session config
│   └── utils/
│       ├── common_util.py   # Project root finder, path resolver, workspace init
│       ├── logger.py        # loguru setup & get_logger helper
│       ├── mcp_util.py      # MCP tool loader (reads mcp.json)
│       └── skill.py         # Skill discovery, parsing, rendering
├── app/                     # Application layer (e.g. snake-game demo)
│   └── snake-game/
├── tests/                   # Test suite
│   ├── file/                # File-related test fixtures
│   ├── sessions/            # Session test data
│   ├── skills/              # Skill-specific tests
│   ├── snake-game/          # Snake game tests (git-ignored)
│   ├── test_agent.py
│   ├── test_agent_generate_code.py
│   ├── test_agent_loop.py
│   ├── test_agent_mcp.py
│   ├── test_feishu_channel.py
│   ├── test_heartbeat.py
│   ├── test_http_request.py
│   ├── test_session_manager.py
│   ├── test_skills_loader.py
│   ├── test_tools.py
│   ├── test_utils_config.py
│   └── test_web_api.py      # Web API endpoint tests
├── sessions/                # Runtime session data (git-ignored)
│   └── sessions.json        # Persisted session state
├── pyproject.toml           # Project metadata & dependencies
├── mcp.json                 # MCP server configuration
├── HEARTBEAT.md             # Heartbeat task definitions (auto-created from template)
├── Dockerfile               # Docker image definition
├── docker-compose.yaml      # Docker Compose deployment
├── .example.env             # Environment variable template
├── .local.env               # Local environment (git-ignored)
└── AGENTS.md                # This file — AI agent conventions
```

## Prerequisites

- **Python**: >= 3.11
- **pip** (or compatible package manager)

## Environment Variables

Copy `.example.env` to `.local.env` and fill in:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | API key for the LLM provider |
| `OPENAI_BASE_URL` | Custom base URL for the LLM API endpoint |
| `OPENAI_MODEL` | Model name to use |
| `FEISHU_APP_ID` | Feishu (Lark) application ID |
| `FEISHU_APP_SECRET` | Feishu (Lark) application secret |
| `WORKING_DIR` | (Optional) Override the working directory for the agent |
| `LOG_LEVEL` | (Optional) Log level for loguru (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Common Commands

### Install dependencies

```bash
pip install -e .
# With dev dependencies (pytest, pytest-env, pytest-asyncio, python-dotenv)
pip install -e ".[dev]"
```

### Run the unified entry (Web API + all channels + Heartbeat + AgentLoop)

```bash
python agent/main.py
```

> Starts: `init_workspace_templates` (copies template files to `WORKING_DIR`), `SessionManager`, `MessageBus`, `ChannelManager` (discovers and starts all registered channels, e.g. Feishu), `HeartbeatService` (periodic task execution), `AgentLoop` (consumes inbound messages, invokes agent, publishes outbound), and the FastAPI Web API server (port 8000). The Feishu bot, heartbeat, and other services run in daemon threads.

### Run the CLI agent

```bash
python -m agent.cli
```

> The CLI uses `AsyncSqliteSaver` with `cai-coder-sqlite.db` for persistent conversation state. Enter `exit` to quit.

### Run the Web API server only

```bash
python -m agent.webapp
# or
uvicorn agent.webapp:app --host 0.0.0.0 --port 8000
```

> The Web API provides an OpenAI-compatible `/v1/chat/completions` endpoint supporting both streaming (SSE) and non-streaming modes. It uses `InMemorySaver` (no persistent state across restarts). Health check: `GET /health`. Models list: `GET /v1/models`.

### Run tests

```bash
pytest
# With verbose output
pytest -v
# Run a specific test file
pytest tests/test_agent.py
```

> Tests read environment variables from `.local.env` via `pytest-env` (`env_files = ".local.env"`).
> `asyncio_mode = "auto"` is enabled — async tests are automatically detected.

### Docker

```bash
# Build image
docker build -t cai-coder:0.2 .

# Run with Docker Compose
docker compose up -d

# Or run directly
docker run --env-file .local.env -p 8000:8000 -it cai-coder:0.2 python agent/main.py
```

> The Dockerfile uses Tsinghua PyPI mirror (`pypi.tuna.tsinghua.edu.cn`) for faster builds in China.

## Architecture & Conventions

### Message Bus Architecture
The unified entry (`agent/main.py`) uses a centralized `MessageBus` to decouple channels from the agent:

```
Channel (feishu, ...) ──publish_inbound──> MessageBus.inbound ──consume──> AgentLoop ──invoke──> Agent
AgentLoop ──publish_outbound──> MessageBus.outbound ──consume──> ChannelManager ──dispatch──> Channel.send()
```

- **`MessageBus`** (`agent/bus/bus.py`): Two `queue.Queue` instances — `inbound` and `outbound`.
- **`InMessage` / `OutMessage`** (`agent/bus/events.py`): Dataclasses carrying `channel`, `chat_id`, `content`, `metadata`.
- **`AgentLoop`** (`agent/server.py`): Runs in a daemon thread; consumes from `inbound`, invokes the agent, publishes to `outbound`. Accepts an optional `SessionManager` to track sessions per message.

### Channel Abstraction
All external platform integrations implement `BaseChannel` (`agent/integration/base.py`):

- **`BaseChannel`**: Abstract base with `send(msg)` and `start()` methods. Provides `_handle_message()` to publish to the bus.
- **`ChannelManager`** (`agent/integration/manager.py`): Discovers all channels via `register.py`, starts each in a daemon thread, dispatches outbound messages.
- **`register.py`** (`agent/integration/register.py`): Registry mapping channel names to `BaseChannel` instances. To add a new channel, add it here.

### Heartbeat Service (`agent/heartbeat/`)
A periodic task execution service that reads `HEARTBEAT.md` from the workspace:

- **`HeartbeatService`** (`agent/heartbeat/heatbeat.py`): Runs in a daemon thread, checks `HEARTBEAT.md` every 30 minutes by default.
- **Decision flow**: Reads `HEARTBEAT.md` → LLM decides `run` or `skip` → If `run`, executes tasks via the agent → Notifies the most recently active channel session.
- **`HeartBeatResult`**: Pydantic model with `action` (run/skip) and `tasks` (natural language summary).
- **`HEARTBEAT.md`**: Auto-created from `agent/templates/HEARTBEAT.md` on startup via `init_workspace_templates`. Users add periodic tasks here.

### Session Manager (`agent/session/`)
Tracks conversations across channels for session-aware operations:

- **`SessionManager`** (`agent/session/manager.py`): Manages `Session` objects keyed by `{channel}:{chat_id}`. Persists to `sessions/sessions.json` in the workspace.
- **`Session`**: Dataclass with `key`, `created_at`, `updated_at`.
- Used by `AgentLoop` to register each inbound message's session, and by `HeartbeatService` to find the most recently active session for notifications.

### Progressive Skill Loading
Skills are defined as subdirectories under `agent/skills/`, each containing a `SKILL.md` with YAML frontmatter (`name`, `description`) and a markdown body. The `SkillMiddleware` injects available skill summaries into the system prompt at runtime; agents call `load_skill(name)` to pull in full instructions on demand.

### Middleware Stack
The agent uses a layered middleware pipeline (configured in `server.py`):

| Middleware | Purpose |
|---|---|
| `SkillMiddleware` | Injects skill descriptions; provides `load_skill` tool |
| `TodoListMiddleware` | Manages task tracking and progress visibility |
| `ToolRetryMiddleware` | Retries failed tool calls (max 3, exponential backoff) |
| `ModelRetryMiddleware` | Retries failed model calls (max 3, exponential backoff) |
| `SummarizationMiddleware` | Summarizes conversation when token count exceeds 128k, keeps last 80k tokens |
| `ContextEditingMiddleware` | Clears old tool uses when context exceeds 64k tokens, keeps last 5 |

### MCP Tool Integration
MCP (Model Context Protocol) tools are loaded at startup via `agent/utils/mcp_util.py`, which reads `mcp.json` from the project root. MCP tools are merged with built-in tools and passed to the agent. To add MCP servers, edit `mcp.json`.

### Tool Registration
All tools live in `agent/tools/` as individual modules, exported via `agent/tools/__init__.py`. New tools should follow the same pattern — define a function decorated with `@tool` and register it in `server.py`.

### Prompt Construction
The system prompt is assembled in `agent/prompt.py` from modular sections (role, working environment, project setup, editing constraints, tool usage, git hygiene). Modifications should be made in the corresponding section constant, not hardcoded elsewhere.

### Workspace Templates (`agent/templates/`)
Template files are copied to the workspace (`WORKING_DIR`) on startup via `init_workspace_templates()` in `common_util.py`. Only files that don't already exist in the workspace are created. Currently includes `HEARTBEAT.md`.

### Logging
All logging uses **loguru** via `agent/utils/logger.py`. Use `get_logger(name)` to obtain a bound logger instance. Log level is configurable via the `LOG_LEVEL` environment variable (defaults to `INFO`).

### Memory & Checkpointing
- **Default / Web API**: `InMemorySaver` (ephemeral, for testing/programmatic use).
- **CLI**: `AsyncSqliteSaver` backed by `cai-coder-sqlite.db` for persistent conversation state across sessions.
- **Feishu / Channel mode**: `InMemorySaver` via `get_agent()` in `AgentLoop`.

### Web API (`agent/webapp.py`)
A FastAPI application providing an **OpenAI-compatible** chat completions API:

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completions (streaming & non-streaming) |

- Request/response bodies follow the OpenAI API schema (Pydantic models).
- Streaming uses SSE (`text/event-stream`) with `ChatCompletionChunk` events.
- CORS is enabled for all origins.

### Feishu Channel (`agent/integration/feishu/`)
A **Feishu (Lark) long-connection WebSocket channel** implementing `BaseChannel`:

- **`bot.py`** (`FeishuChannel`): Connects via `lark.ws.Client`, processes incoming messages through `BaseChannel._handle_message()`, and replies with markdown-formatted responses. Includes emoji reactions to indicate processing.
- **`config.py`**: Reads `FEISHU_APP_ID` and `FEISHU_APP_SECRET` from environment variables.
- **Session management**: Uses `chat_id` as session ID for per-group conversation isolation.
- **Message deduplication**: Tracks `message_id` in `task_db` to handle WebSocket event replay.

### Config via env
All runtime configuration (LLM credentials, model, working dir, Feishu credentials, log level) is sourced from environment variables. Never hardcode secrets.

## Rules for Agents

- **Do not** modify files under `agent/skills/*/SKILL.md` unless explicitly asked.
- **Do not** commit `.local.env` or `*.db` files — they are git-ignored and contain secrets/data.
- **Do not** commit `tests/snake-game/` — it is git-ignored.
- **Do not** commit `sessions/` — it is git-ignored and contains runtime session data.
- **Do** run `pytest` after making changes to `agent/` to verify nothing is broken.
- **Do** follow the existing pattern when adding new tools (one module per tool, export from `__init__.py`, register in `server.py`).
- **Do** follow the existing pattern when adding new skills (subdirectory under `agent/skills/` with a `SKILL.md` containing YAML frontmatter).
- **Do** follow the existing pattern when adding new integrations (implement `BaseChannel`, register in `register.py`).
- **Do** follow the existing pattern when adding new middleware (implement `AgentMiddleware`, add to the middleware list in `server.py`).
- Code identifiers and error messages should be in **English**; user-facing explanations in **Chinese**.
- Keep the project compatible with Python 3.11+ (no version-exclusive syntax beyond 3.11).
