from pathlib import Path

from agent.tools import (
    get_weather,
    read_file,
    write_file,
    ls,
    bash
)


def test_get_weather() -> None:
    result = get_weather.invoke({"location": "Shenzhen"})
    assert result["location"] is not None
    assert isinstance(result["temperature"], (int, float))


def test_get_weather_not_found() -> None:
    result = get_weather.invoke({"location": "zzzz_nonexistent_city_xyz"})
    assert "error" in result


def test_read_file() -> None:
    path = str(Path(__file__).parent / 'file/a.txt')
    content = read_file.invoke({"file_path": path})
    assert content == "this is a content\nhello world"


def test_write_file() -> None:
    path = str(Path(__file__).parent / 'file/b.txt')
    result = write_file.invoke({"file_path": path, "content": "hello world"})
    assert result["success"] is True


def test_ls() -> None:
    path = str(Path(__file__).parent / 'file')
    result = ls.invoke({"path": path})
    assert result.__len__() == 3


def test_bash_echo_test() -> None:
    result = bash.invoke({"command": "echo 'test'"})
    assert result == "test\n"


def test_bash_ls() -> None:
    path = str(Path(__file__).parent / 'file')
    result = bash.invoke({"command": f"ls {path}"})
    assert result == "a.txt\nb.txt\nc.txt\n"
