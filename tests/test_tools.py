from pathlib import Path

from agent.tools import (
    get_weather,
    read_file,
    write_file,
    ls,
    bash
)

def test_get_weather() -> None:
    result = get_weather("shenzhen")
    assert result["location"] == "shenzhen" and isinstance(result["temperature"], int)

def test_read_file() -> None:
    path = str(Path(__file__).parent / 'file/a.txt')
    content = read_file(path)
    assert content == """this is a content\nhello world"""

def test_write_file() -> None:
    path = str(Path(__file__).parent / 'file/b.txt')
    result = write_file(path, "hello world")
    assert result["success"] == True

def test_ls() -> None:
    path = str(Path(__file__).parent / 'file')
    result = ls(path)
    assert result.__len__() == 3

def test_bash_echo_test() -> None:
    result = bash("echo 'test'")
    assert result == "test\n"

def test_bash_ls() -> None:
    path = str(Path(__file__).parent / 'file')
    result = bash(f"ls {path}")
    assert result == "a.txt\nb.txt\nc.txt\n"