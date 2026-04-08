import os
from pathlib import Path


def ls(path: str):
    """List files and directories in a given path"""
    p = Path(path)

    if not p.exists():
        return f"ls: '{path}' is not exist"


    if p.is_file():
        return p.name

    filelist = []
    for item in sorted(p.iterdir()):
        suffix = '/' if item.is_dir() else ''
        filelist.append(f"{item.name}{suffix}")
    return filelist
