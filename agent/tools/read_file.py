

def read_file(file_path: str):
    """Read the contents of a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content