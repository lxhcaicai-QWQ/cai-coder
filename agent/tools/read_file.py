

def read_file(file_path: str):
    """Read the contents of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"No such file or directory: '{file_path}'"
