from pathlib import Path

def find_project_root(start_path=None) -> Path:
    current = Path(start_path or __file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("not found pyproject.toml")