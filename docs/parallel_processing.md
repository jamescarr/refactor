# Parallel Processing in Epyon

Epyon provides utilities for parallel processing to speed up operations on large codebases. This document explains how to use these features in your own refactoring tools.

## Available Utilities

The main parallel processing utilities are in `epyon.core.utils`:

1. `process_files_parallel`: A general-purpose function for processing multiple files concurrently
2. `build_import_map`: Creates a map of imports to files that contain them, using parallel scanning
3. `scan_imports`: Quickly scans a Python file for imports using Python's AST

## Basic Usage

### Processing Files in Parallel

```python
from pathlib import Path
from epyon.core.utils import find_python_files, process_files_parallel

def process_single_file(file_path, arg1, arg2, dry_run=False):
    # Process a single file and return a result
    # ...
    return result

# Get list of files
python_files = find_python_files(Path("./my_project"))

# Process all files in parallel
results = process_files_parallel(
    python_files,
    process_single_file,
    "arg1_value",
    "arg2_value",
    dry_run=True,
    max_workers=4  # Optional: limit number of workers
)

# Process results
for result in results:
    if result:  # Check if processing was successful
        # Do something with result
        pass
```

### Building an Import Map

An import map is useful for quickly finding which files use particular imports:

```python
from pathlib import Path
from epyon.core.utils import build_import_map

# Build a map of imports to files
import_map = build_import_map(Path("./my_project"))

# Find all files that import a specific module or symbol
files_using_import = import_map.get("module.submodule.ClassName", set())

# Process only these files
for file_path in files_using_import:
    # Process file
    pass
```

## Performance Considerations

1. **Worker Count**: By default, Python's `ProcessPoolExecutor` will use `os.cpu_count()` workers. For I/O-bound tasks, you might want to use more workers than CPUs.

2. **Memory Usage**: Be cautious with very large codebases as each worker needs memory to parse and process files.

3. **AST vs. CST**: The `scan_imports` function uses Python's built-in `ast` module which is much faster than `libcst` for basic import scanning.

## Implementation Example: Optimizing a Refactoring Tool

Here's how you might optimize a refactoring tool:

```python
from pathlib import Path
from typing import Set
from epyon.core.utils import build_import_map, process_files_parallel

def my_refactoring_function(directory: Path, target: str):
    # Step 1: Build an import map to find relevant files
    import_map = build_import_map(directory)
    
    # Step 2: Find files that might need processing
    relevant_files = set()
    
    # Add files that import the target
    if target in import_map:
        relevant_files.update(import_map[target])
    
    # Add files that import the parent module
    parent_module = ".".join(target.split(".")[:-1])
    if parent_module in import_map:
        relevant_files.update(import_map[parent_module])
    
    # Step 3: Process only the relevant files in parallel
    results = process_files_parallel(
        list(relevant_files),
        process_single_file,
        target,
        max_workers=4
    )
    
    # Step 4: Summarize the results
    modified_count = sum(1 for r in results if r)
    print(f"Modified {modified_count} files")
    
    return modified_count
```

## Best Practices

1. **Targeted Processing**: Only process files that are likely to need changes.
2. **Error Handling**: Make sure your file processor functions handle exceptions gracefully.
3. **Progress Reporting**: Consider using `rich.progress` to show progress during long-running operations.
4. **Testing**: Always test parallel processing implementations with both small and large codebases.

## Warnings and Limitations

- The parallel processing uses `ProcessPoolExecutor`, which creates new Python processes. This has more overhead than threads but avoids the Global Interpreter Lock (GIL).
- Functions passed to `process_files_parallel` must be picklable (they can't be lambdas or local functions in some cases).
- Be careful with shared resources across processes. 