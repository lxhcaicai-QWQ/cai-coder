<!-- This file is managed by AI agents. Do not manually edit unless necessary. -->

# AGENTS.md — cai-coder

## Project Overview

**cai-coder** is an AI coding agent built with **Python 3.11+**, powered by **LangChain** + **LangGraph**. It features a progressive skill-loading mechanism, a set of built-in tools (file I/O, shell, HTTP, weather), MCP tool integration, and a middleware-based architecture for extensible agent behavior.

- **Primary language**: Python 3.11+
- **Key frameworks**: LangChain (`>=1.2.9`), LangGraph (`>=1.0.8`), langchain-openai (`==1.1.10`)
- **Key libraries**: langgraph-checkpoint-sqlite (`>=3.0.3`), langchain-mcp-adapters (`>=0.2.0`), pyyaml (`>=6.0`), requests (`>=2.31.0`)
- **Build system**: Hatchling (`pyproject.toml`)

## Project Structure

```
cai-coder/
├── agent/                   # Core agent package
│   ├── cli.py               # CLI entry point (interactive async REPL)
│   ├── server.py            # Agent factory (LLM, tools, middleware, memory)
│   ├── prompt.py            # System prompt construction (modular sections)
│   ├── middleware/           # Agent middleware
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
│   └── utils/
│       ├── common_util.py   # Project root finder
│       ├── mcp_util.py      # MCP tool loader (reads mcp.json)
│       └── skill.py         # Skill discovery, parsing, rendering
├── app/                     # Application layer (e.g. snake-game demo)
│   └── snake-game/
├── tests/                   # Test suite
│   ├── file/                # File-related test fixtures
│   ├── skills/              # Skill-specific tests
│   ├── snake-game/          # Snake game tests (git-ignored)
│   ├── test_agent.py
│   ├── test_agent_generate_code.py
│   ├── test_agent_mcp.py
│   ├── test_http_request.py
│   ├── test_skills_loader.py
│   ├── test_tools.py
│   └── test_utils_config.py
├── pyproject.toml           # Project metadata & dependencies
├── mcp.json                 # MCP server configuration
├── Dockerfile               # Docker image definition
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
| `WORKING_DIR` | (Optional) Override the working directory for the agent |

## Common Commands

### Install dependencies

```bash
pip install -e .
# With dev dependencies (pytest, pytest-env, pytest-asyncio, python-dotenv)
pip install -e ".[dev]"
```

### Run the CLI agent

```bash
python -m agent.cli
```

> The CLI uses `AsyncSqliteSaver` with `cai-coder-sqlite.db` for persistent conversation state. Enter `exit` to quit.

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
docker build -t cai-coder .
docker run --env-file .local.env -it cai-coder python -m agent.cli
```

> The Dockerfile uses Tsinghua PyPI mirror (`pypi.tuna.tsinghua.edu.cn`) for faster builds in China.

## Architecture & Conventions

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

### MCP Tool Integration
MCP (Model Context Protocol) tools are loaded at startup via `agent/utils/mcp_util.py`, which reads `mcp.json` from the project root. MCP tools are merged with built-in tools and passed to the agent. To add MCP servers, edit `mcp.json`.

### Tool Registration
All tools live in `agent/tools/` as individual modules, exported via `agent/tools/__init__.py`. New tools should follow the same pattern — define a function decorated with `@tool` and register it in `server.py`.

### Prompt Construction
The system prompt is assembled in `agent/prompt.py` from modular sections (role, working environment, project setup, editing constraints, tool usage, git hygiene). Modifications should be made in the corresponding section constant, not hardcoded elsewhere.

### Memory & Checkpointing
- **Default**: `InMemorySaver` (ephemeral, for testing/programmatic use).
- **CLI**: `AsyncSqliteSaver` backed by `cai-coder-sqlite.db` for persistent conversation state across sessions.

### Config via env
All runtime configuration (LLM credentials, model, working dir) is sourced from environment variables. Never hardcode secrets.

## Rules for Agents

- **Do not** modify files under `agent/skills/*/SKILL.md` unless explicitly asked.
- **Do not** commit `.local.env` or `*.db` files — they are git-ignored and contain secrets/data.
- **Do not** commit `tests/snake-game/` — it is git-ignored.
- **Do** run `pytest` after making changes to `agent/` to verify nothing is broken.
- **Do** follow the existing pattern when adding new tools (one module per tool, export from `__init__.py`, register in `server.py`).
- **Do** follow the existing pattern when adding new skills (subdirectory under `agent/skills/` with a `SKILL.md` containing YAML frontmatter).
- Code identifiers and error messages should be in **English**; user-facing explanations in **Chinese**.
- Keep the project compatible with Python 3.11+ (no version-exclusive syntax beyond 3.11).
