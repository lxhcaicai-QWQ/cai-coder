---
name: agents-md-generator
description: Generate or update an AGENTS.md (also called Agents.md) file for the project following the agents.md convention. Use when the user asks to create/refresh the agents file, onboarding for AI coding agents, or project context for AI.
---

# AGENTS.md / Agents.md Generator Skill

## When to use this skill
- User asks to "generate AGENTS.md" / "update Agents.md".
- User wants to improve AI onboarding for this repo.
- User mentions "project context for AI" or "agents documentation".

## How to generate the AGENTS.md
1. Identify the project type and ecosystem (detect files such as go.mod, package.json, composer.json, pyproject.toml, Makefile, Dockerfile, etc.).
2. Collect key context:
   - Build commands (e.g., make build, npm run build, composer install, pip install -r requirements.txt).
   - Test commands and common flags.
   - Lint/format commands.
   - Dev server start command.
   - Important conventions (branch naming, PR process, environment variables, configs).
3. Generate a concise AGENTS.md with these sections (keep it short and high-signal):
   - Project overview (what it does, primary languages).
   - Prerequisites (runtime/tools).
   - Common commands (build/test/lint/dev).
   - Important rules and conventions.
   - Notes for agents (e.g., "do not modify generated files", "always run tests after changes").
4. If the repo is large or monorepo, suggest generating scoped AGENTS.md for subsystems (backend/, frontend/, internal/, etc.).
5. Mark the file as agent-managed (for example, add a comment at the top).
6. After generating, show a diff and ask the user whether to commit or adjust.

## Output format
- Use Markdown.
- Avoid duplication with README.md; focus on "for AI agents" instructions.
- Prefer bullet lists and code blocks for commands.

## Edge cases
- If a similar AGENTS.md already exists, update it while preserving user sections.
- If important files are missing (e.g., package.json), ask the user for key commands or skip that section.
