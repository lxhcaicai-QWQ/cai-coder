from pathlib import Path

from agent.utils.common_util import ensure_dir

# ─── L2 滚动记忆模板 ───

WEEKLY_TEMPLATE = """\
# This Week's Memory

> Updated: {date}
> Coverage: {start_date} ~ {end_date}

## Current Goals


## In Progress


## Key Decisions


## Lessons Learned


## TODO

"""

MONTHLY_TEMPLATE = """\
# This Month's Memory

> Updated: {date}
> Coverage: {start_date} ~ {end_date}

## Major Goals


## Major Decisions


## Lessons & Patterns


## Carried Forward

"""

# ─── L3 长期记忆模板 ───

PROFILE_TEMPLATE = """\
# User Profile

## Role


## Work Context


## Tools


## Communication

"""

PREFERENCES_TEMPLATE = """\
# User Preferences

## Language


## Code Style


## Output Format


## Avoid

"""

RULES_TEMPLATE = """\
# Hard Rules


"""

GLOSSARY_TEMPLATE = """\
# Glossary


"""

AGENT_INDEX_TEMPLATE = """\
# Agent Memory Index

This file tells the agent what knowledge exists and when to read it.

## Structure

- `profile.md` -- User role, work context, tools. Read at session start.
- `preferences.md` -- Language, style, formatting preferences. Read at session start.
- `rules.md` -- Hard rules and constraints. Read at session start.
- `glossary.md` -- Terminology definitions. Read when domain terms appear.
- `projects/` -- Per-project background files. Read when working on that project.
- `knowledge/` -- Domain knowledge articles. Read when relevant topic arises.
- `decisions/` -- Decision records (dated). Read when revisiting a past decision.
- `lessons/` -- Lessons learned (dated). Read when encountering similar problems.
- `journal/` -- Journal entries (dated). Read for historical context.
"""

# ─── 上下文注入提示 ───

MEMORY_CONTEXT_PROMPT = """\

## Long-Term Memory Context
Below is a summary of relevant memory from previous sessions. Use this context to maintain continuity, respect user preferences, and apply learned lessons. Do NOT repeat or dump this context back to the user verbatim.

---BEGIN MEMORY CONTEXT---
"""

# ─── L1 会话日志条目模板 ───

SESSION_LOG_ENTRY = """\

---

### Session {session_id}
- **Time**: {timestamp}
- **Summary**: {summary}
- **Key Decisions**: {decisions}
- **Errors/Issues**: {errors}
"""

# ─── L3 经验教训模板 ───

LESSON_TEMPLATE = """\
# Lesson: {task}

- **Date**: {date}
- **Task**: {task}
- **Mistake**: {mistake}
- **Solution**: {solution}
"""

# ─── L3 决策记录模板 ───

DECISION_TEMPLATE = """\
# Decision: {topic}

- **Date**: {date}
- **Topic**: {topic}
- **Context**: {context}
- **Decision**: {decision}
- **Rationale**: {rationale}
"""

# ─── L3 领域知识模板 ───

KNOWLEDGE_TEMPLATE = """\
# Knowledge: {topic}

{content}
"""

# ─── L3 项目背景模板 ───

PROJECT_TEMPLATE = """\
# Project: {name}

> Last Updated: {date}

{background}
"""

# ─── 精炼提示词 ───

CONSOLIDATION_PROMPT = """\
You are a memory consolidation agent. Your job is to merge new information from raw session logs into a structured {layer} memory document.

## Current {layer} memory document:
{existing}

## New raw session logs to incorporate:
{logs}

## Instructions:
1. Read the existing memory and the new logs carefully.
2. Merge the new information into the existing document.
3. Remove items that are clearly outdated or resolved.
4. Keep the document focused and concise (800-1500 words).
5. Follow this template structure:
{template}
6. Update the "Updated" date to today.
7. Output ONLY the final markdown document, nothing else.

Consolidated document:"""

# ─── 初始化工作区模板文件 ───


def init_memory_templates(workspace: Path) -> list[str]:
    """Initialize default memory files in workspace. Only creates missing files."""
    ensure_dir(workspace / "memory" / "logs")

    long_term = ensure_dir(workspace / "long-term")
    for sub in ("projects", "knowledge", "decisions", "lessons", "journal"):
        ensure_dir(long_term / sub)

    templates = {
        "long-term/AGENT.md": AGENT_INDEX_TEMPLATE,
        "long-term/profile.md": PROFILE_TEMPLATE,
        "long-term/preferences.md": PREFERENCES_TEMPLATE,
        "long-term/rules.md": RULES_TEMPLATE,
        "long-term/glossary.md": GLOSSARY_TEMPLATE,
    }

    added: list[str] = []
    for rel_path, content in templates.items():
        target = workspace / rel_path
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            added.append(rel_path)

    return added