"""Common utility functions."""
import ast
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Set, Callable, Any, Optional, Union, Tuple

def find_python_files(directory: Path) -> List[Path]:
    """Recursively find all Python files in a directory."""
    python_files = []
    for path in directory.rglob('*.py'):
        if path.is_file():
            python_files.append(path)
    return python_files

def scan_imports(file_path: Path) -> Set[str]:
    """
    Quickly scan a Python file for imports using AST.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Set of fully qualified import paths 
    """
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            # Import statements like "import foo.bar"
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            
            # Import from statements like "from foo import bar"
            elif isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                for name in node.names:
                    if name.name == '*':
                        imports.add(module)
                    else:
                        imports.add(f"{module}.{name.name}")
        
        return imports
    except Exception:
        # If there's any error parsing the file, return an empty set
        return set()

def build_import_map(directory: Path, max_workers: Optional[int] = None) -> Dict[str, Set[Path]]:
    """
    Build a map of imports to the files that contain them.
    Uses parallel processing for speed.
    
    Args:
        directory: Root directory to process
        max_workers: Maximum number of concurrent workers
        
    Returns:
        Dict mapping import paths to sets of file paths
    """
    python_files = find_python_files(directory)
    import_map: Dict[str, Set[Path]] = {}
    
    # Process files in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(scan_imports, file_path): file_path 
                          for file_path in python_files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                imports = future.result()
                for import_path in imports:
                    if import_path not in import_map:
                        import_map[import_path] = set()
                    import_map[import_path].add(file_path)
            except Exception:
                # If processing a file fails, just skip it
                continue
    
    return import_map

def process_files_parallel(
    files: List[Path],
    processor: Callable[..., Any],
    *args: Any,
    max_workers: Optional[int] = None,
    **kwargs: Any
) -> List[Any]:
    """
    Process files in parallel using the specified processor function.
    
    Args:
        files: List of file paths to process
        processor: Function that processes a single file
        *args: Positional arguments to pass to the processor
        max_workers: Maximum number of concurrent workers
        **kwargs: Keyword arguments to pass to the processor
        
    Returns:
        List of results from the processor function
    """
    results = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}
        
        # Submit all jobs
        for file_path in files:
            future = executor.submit(processor, file_path, *args, **kwargs)
            future_to_file[future] = file_path
        
        # Process as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # If a job fails, append None to keep the same length
                results.append(None)
    
    return results 