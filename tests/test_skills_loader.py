from pathlib import Path

from agent.utils import skill
from agent.middleware import load_skill

def test_find_skill():
    path = Path(__file__).parent / 'skills'
    result = skill.find_skill_dirs_in_root(path)
    assert len(result) == 2


def test_parse_skill_md():
    path = Path(__file__).parent / 'skills/python-testing/SKILL.md'
    result = skill.parse_skill_md(path)
    assert result.name == "python-testing"
    assert result.description == "Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements."
    assert result.content is None

    path = Path(__file__).parent / 'skills/python-patterns/SKILL.md'
    result = skill.parse_skill_md(path)
    assert result.name == "python-patterns"
    assert result.description == "Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications."
    assert result.content is None

def test_parse_skill_md_content():
    path = Path(__file__).parent / 'skills/python-testing/SKILL.md'
    result = skill.parse_skill_md(path,read_body_now=True)
    assert result.name == "python-testing"
    assert result.description == "Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements."
    assert result.content is not None

def test_render_skills_json():
    path = Path(__file__).parent / 'skills'
    result = skill.render_skills_json(path)
    assert result is not None


def test_middleware_load_skill():
    result = load_skill.invoke({"skill_name":"python-testing"})
    assert result is not None
    assert result.__contains__("Loaded skill: python-testing")