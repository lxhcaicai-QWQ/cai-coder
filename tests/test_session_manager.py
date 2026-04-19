from pathlib import Path

from agent.session import SessionManager


def _make_session_manager():
    return SessionManager(workspace = Path(__file__).parent)

def test_session_path():
    manager = _make_session_manager()
    assert manager._get_session_path() == Path(__file__).parent/'sessions/sessions.json'

def test_load_session():
    manager = _make_session_manager()
    dict = manager._load()
    assert dict.get("feishu:abcd1234").to_dict() == {
    "key": "feishu:abcd1234",
    "created_at": "2026-04-19T23:39:27.113342",
    "updated_at": "2026-04-19T23:39:27.113343"
  }


def test_session_get_or_create():
    manager = _make_session_manager()
    session = manager.get_or_create("feishu:abcd1234")
    assert session.key == "feishu:abcd1234"

def test_list_sessions():
    manager = _make_session_manager()
    list = manager.list_sessions()
    assert list[0].key == "feishu:asd123"
    assert list[1].key == "feishu:abcd1234"
    assert list[0].updated_at > list[1].updated_at