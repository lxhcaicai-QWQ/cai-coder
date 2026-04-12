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


# --- Bash timeout & path restriction tests ---

def test_bash_timeout_expired() -> None:
    """Command exceeding timeout should return a timeout error message."""
    result = bash.invoke({"command": "sleep 10", "timeout": 1})
    assert "timed out" in result


def test_bash_custom_timeout_ok() -> None:
    """Command finishing within custom timeout should succeed."""
    result = bash.invoke({"command": "echo 'fast'", "timeout": 5})
    assert "fast" in result


def test_bash_default_timeout_param() -> None:
    """Default timeout should be 300 seconds (check module constant)."""
    from agent.tools.bash import DEFAULT_TIMEOUT
    assert DEFAULT_TIMEOUT == 300


def test_bash_cwd_restricted() -> None:
    """bash should execute within the project working directory."""
    result = bash.invoke({"command": "pwd"})
    from agent.utils.common_util import get_working_dir
    working_dir = get_working_dir()
    assert working_dir in result


def test_bash_stderr_included_on_error() -> None:
    """Non-zero exit code should include stderr in the output."""
    result = bash.invoke({"command": "cat /nonexistent_path_xyz_12345"})
    assert "STDERR:" in result or "No such file" in result


def test_bash_exit_code_on_failure() -> None:
    """Non-zero exit code should be reported."""
    result = bash.invoke({"command": "false"})
    assert "Exit code:" in result


# --- Path validation tests ---

def test_read_file_rejects_path_traversal() -> None:
    """read_file must reject paths that escape WORKING_DIR."""
    result = read_file.invoke({"file_path": "/etc/passwd"})
    assert "outside" in result


def test_read_file_rejects_relative_traversal() -> None:
    """read_file must reject relative paths like '../../../etc/passwd'."""
    result = read_file.invoke({"file_path": "../../../etc/passwd"})
    assert "outside" in result


def test_write_file_rejects_path_traversal() -> None:
    """write_file must reject paths that escape WORKING_DIR."""
    result = write_file.invoke(
        {"file_path": "/tmp/evil_write.txt", "content": "pwned"}
    )
    assert result["success"] is False
    assert "outside" in result["error"]


def test_ls_rejects_path_traversal() -> None:
    """ls must reject paths that escape WORKING_DIR."""
    result = ls.invoke({"path": "/etc"})
    assert "outside" in result


def test_ls_relative_path_inside_working_dir() -> None:
    """ls should accept relative paths that resolve inside WORKING_DIR."""
    result = ls.invoke({"path": "tests/file"})
    assert isinstance(result, list)


def test_read_file_relative_path_inside_working_dir() -> None:
    """read_file should accept relative paths that resolve inside WORKING_DIR."""
    result = read_file.invoke({"file_path": "tests/file/a.txt"})
    assert "this is a content" in result


def test_write_and_read_relative_path() -> None:
    """write_file + read_file should work with relative paths inside WORKING_DIR."""
    write_result = write_file.invoke(
        {"file_path": "tests/file/c.txt", "content": "path validation ok"}
    )
    assert write_result["success"] is True

    read_result = read_file.invoke({"file_path": "tests/file/c.txt"})
    assert read_result == "path validation ok"


def test_resolve_path_raises_on_escape() -> None:
    """resolve_path should raise ValueError for escaping paths."""
    from agent.utils.common_util import resolve_path
    import pytest

    with pytest.raises(ValueError, match="outside"):
        resolve_path("/etc/passwd")


def test_resolve_path_ok_for_working_dir_subpath() -> None:
    """resolve_path should succeed for paths inside WORKING_DIR."""
    from agent.utils.common_util import resolve_path, get_working_dir

    resolved = resolve_path("tests/file/a.txt")
    working_dir = get_working_dir()
    assert resolved.startswith(working_dir)
