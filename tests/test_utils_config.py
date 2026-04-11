from pathlib import Path

from agent.utils import common_util

def test_utils_find_project_root():
    path = common_util.find_project_root()
    assert  path == Path(__file__).parent.parent

    path = common_util.find_project_root(Path(__file__))
    assert  path == Path(__file__).parent.parent