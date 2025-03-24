"""Common utility functions."""
from pathlib import Path
from typing import List

def find_python_files(directory: Path) -> List[Path]:
    """Recursively find all Python files in a directory."""
    python_files = []
    for path in directory.rglob('*.py'):
        if path.is_file():
            python_files.append(path)
    return python_files 