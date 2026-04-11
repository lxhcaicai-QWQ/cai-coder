<!-- This file is managed by AI agents. Do not manually edit unless necessary. -->

# AGENTS.md — cai-coder

## Project Overview

**cai-coder** is an AI coding agent built with **Python 3.11+**, powered by **LangChain** + **LangGraph**. It features a progressive skill-loading mechanism, a set of built-in tools (file I/O, shell, HTTP, weather), and a middleware-based architecture for extensible agent behavior.

- **Primary language**: Python 3.11+
- **Key frameworks**: LangChain, LangGraph, langchain-openai
- **Build system**: Hatchling (`pyproject.toml`)

## Project Structure

```
cai-coder/
├── agent/                   # Core agent package
│   ├── cli.py               # CLI entry point (interactive REPL)
│   ├── server.py            # Agent factory (LLM, tools, middleware, memory)
│   ├── prompt.py            # System prompt construction
│   ├── middleware/           # Agent middleware (e.g. SkillMiddleware)
│   ├── tools/               # Built-in tools
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
│       └── skill.py         # Skill discovery, parsing, rendering
├── app/                     # Application layer (e.g. snake-game demo)
├── tests/                   # Test suite
├── pyproject.toml           # Project metadata & dependencies
├── Dockerfile               # Docker image definition
├── .example.env             # Environment variable template
└── .local.env               # Local environment (git-ignored)
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
# With dev dependencies (pytest, etc.)
pip install -e ".[dev]"
```

### Run the CLI agent

```bash
python -m agent.cli
```

### Run tests

```bash
pytest
# With verbose output
pytest -v
# Run a specific test file
pytest tests/test_agent.py
```

> Tests read environment variables from `.local.env` via `pytest-env`.

### Docker

```bash
docker build -t cai-coder .
docker run --env-file .local.env -it cai-coder python -m agent.cli
```

## Architecture & Conventions

- **Progressive Skill Loading**: Skills are defined as subdirectories under `agent/skills/`, each containing a `SKILL.md` with YAML frontmatter (`name`, `description`) and a markdown body. The `SkillMiddleware` injects available skill summaries into the system prompt at runtime; agents call `load_skill(name)` to pull in full instructions on demand.
- **Tool Registration**: All tools live in `agent/tools/` as individual modules, exported via `agent/tools/__init__.py`. New tools should follow the same pattern — define a function decorated with `@tool` and register it in `server.py`.
- **Prompt Construction**: The system prompt is assembled in `agent/prompt.py` from modular sections (role, working environment, editing constraints, tool usage, git hygiene). Modifications should be made in the corresponding section constant, not hardcoded elsewhere.
- **Memory**: Uses `InMemorySaver` (LangGraph checkpointer) for conversation state. Thread ID is generated per CLI session.
- **Config via env**: All runtime configuration (LLM credentials, model, working dir) is sourced from environment variables. Never hardcode secrets.

## Rules for Agents

- **Do not** modify files under `agent/skills/*/SKILL.md` unless explicitly asked.
- **Do not** commit `.local.env` — it is git-ignored and contains secrets.
- **Do** run `pytest` after making changes to `agent/` to verify nothing is broken.
- **Do** follow the existing pattern when adding new tools (one module per tool, export from `__init__.py`, register in `server.py`).
- Code identifiers and error messages should be in **English**; user-facing explanations in **Chinese**.
- Keep the project compatible with Python 3.11+ (no version-exclusive syntax beyond 3.11).
