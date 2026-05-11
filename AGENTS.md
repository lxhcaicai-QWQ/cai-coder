# AGENTS.md

Compact instructions for AI coding agents working in this repository.

## Commands

```bash
pip install -e ".[dev]"              # install with dev deps (pytest, pytest-asyncio, pytest-env, python-dotenv)
pytest                               # run all tests
pytest tests/test_cron.py            # single test file
pytest -v                            # verbose

python agent/main.py                 # unified entry (Web API + Feishu + Heartbeat + Cron + Memory)
python -m agent.cli                  # interactive CLI REPL (uses AsyncSqliteSaver, persistent)
python -m agent.webapp               # Web API only on port 8000 (uses InMemorySaver, ephemeral)
```

## Setup Requirements

- Copy `.example.env` to `.local.env` and fill in `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`. These are required — the app raises `EnvironmentError` at startup if any are missing.
- `WORKING_DIR` env var (note: `.example.env` has a typo `WOKRING_DIR`) overrides the workspace root. Defaults to the project directory.
- Feishu integration requires `FEISHU_APP_ID` and `FEISHU_APP_SECRET`.
- Tests load env from `.local.env` via `pytest-env` plugin.

## Architecture Gotchas

- **Entry point is `agent/main.py`**, not `agent/server.py`. `server.py` contains the agent factory (`_build_llm`, `_build_tools`, `_build_agent`) and `AgentLoop` class. `main.py` wires everything together.
- **MessageBus is the core decoupling layer**: inbound/outbound `queue.Queue` pairs in `agent/bus/bus.py`. All channels publish to inbound; AgentLoop consumes and publishes to outbound.
- **New channels** must implement `BaseChannel` (`agent/integration/base.py`) and be registered in `agent/integration/register.py`.
- **`delegate_agent` is a `BaseTool` subclass** (not `@tool`) because it holds state (references to factory/registry). See `agent/tools/delegate_agent.py`.
- **CLI vs Web API checkpointing differs**: CLI uses `AsyncSqliteSaver` (persistent `cai-coder-sqlite.db`), Web API uses `InMemorySaver` (lost on restart).
- **Middleware order matters** (configured in `server.py`): Skill → Memory → TodoList → ToolRetry → ModelRetry → Summarization → ContextEditing → ConversationSummarizer.
- **Skills live in top-level `skills/`** (not `agent/skills/`, which is legacy). Each skill is a directory with a `SKILL.md` containing YAML frontmatter (`name`, `description`) and markdown instructions. Auto-discovered by `SkillMiddleware`.
- **Long-term memory** uses atomic writes (`tempfile` + `os.replace`). Never write directly to files in `long-term/` or `memory/` without going through `MemoryManager`.
- **Heartbeat service** filename has a typo: `agent/heartbeat/heatbeat.py` (double "t" missing).
- **Dockerfile uses Tsinghua PyPI mirror** — builds are optimized for China.

## Testing Quirks

- `asyncio_mode = "auto"` in `pyproject.toml` — no `@pytest.mark.asyncio` decorator needed on async tests.
- No CI workflows configured (no `.github/`). Tests run locally only.
- Tests require `.local.env` with valid `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` for agent-related tests.

## Conventions

- Logging: `loguru` via `get_logger(name)` from `agent/utils/logger.py`. Do not use stdlib `logging`.
- Code identifiers and error messages in English; user-facing explanations often in Chinese.
- IM responses must use `send_im_messages` tool for proper bus routing, never plain text return.
- MCP servers configured in root `mcp.json` (not inside `agent/`).
- Session state persisted to `sessions/sessions.json` — git-ignored at runtime.
- `HEARTBEAT.md` in workspace root is auto-created from template on first startup.

## Extending

- **New tool**: `agent/tools/<name>.py` with `@tool` → export from `agent/tools/__init__.py` → add to tool list in `server.py`.
- **New skill**: `skills/<name>/SKILL.md` with YAML frontmatter → auto-discovered.
- **New channel**: subclass `BaseChannel` in `agent/integration/<platform>/` → register in `agent/integration/register.py`.
- **New middleware**: implement `AgentMiddleware` → add to list in `server.py`.
- **New specialized agent**: define `AgentDefinition` → `agent_registry.register()` in `agent/multi_agent/registry.py`.
