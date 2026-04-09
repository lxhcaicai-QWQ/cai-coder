import os


def write_file(file_path: str, content: str):
    """Write contents to a file"""
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return {"success": True}