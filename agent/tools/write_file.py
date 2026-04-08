
def write_file(file_path: str, content: str):
    """Write contents to a file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return {"success": True}