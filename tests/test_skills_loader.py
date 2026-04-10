from pathlib import Path

from agent.utils import skill


def test_find_skill():
    path = Path(__file__).parent / 'skills'
    result = skill.find_skill_dirs_in_root(path)
    assert len(result) == 2


def test_parse_skill_md():
    path = Path(__file__).parent / 'skills/python-testing/SKILL.md'
    result = skill.parse_skill_md(path)
    assert result.name == "python-testing"
    assert result.description == "Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements."
    assert result.body is None

    path = Path(__file__).parent / 'skills/python-patterns/SKILL.md'
    result = skill.parse_skill_md(path)
    assert result.name == "python-patterns"
    assert result.description == "Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications."
    assert result.body is None

def test_parse_skill_md_content():
    path = Path(__file__).parent / 'skills/python-testing/SKILL.md'
    result = skill.parse_skill_md(path,read_body_now=True)
    assert result.name == "python-testing"
    assert result.description == "Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements."
    assert result.body is not None

def test_render_skills_json():
    path = Path(__file__).parent / 'skills'
    result = skill.render_skills_json(path)
    assert result is not None
