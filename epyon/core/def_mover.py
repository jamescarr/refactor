"""Core functionality for moving definitions between modules."""
import libcst as cst
from libcst import matchers as m
from typing import Tuple, List, Optional, Set
from pathlib import Path

from ..display import display
from .utils import find_python_files, build_import_map, process_files_parallel

class DefinitionExtractor(cst.CSTTransformer):
    """Extract a class or function definition from a module."""
    
    def __init__(self, target_name: str):
        """Initialize with the name of the definition to extract."""
        self.target_name = target_name
        self.extracted_node: Optional[cst.CSTNode] = None
        self.found = False
    
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> Optional[cst.ClassDef]:
        """Extract the target class definition."""
        if original_node.name.value == self.target_name:
            self.extracted_node = original_node
            self.found = True
            return cst.RemoveFromParent()
        return updated_node
    
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> Optional[cst.FunctionDef]:
        """Extract the target function definition."""
        if original_node.name.value == self.target_name:
            self.extracted_node = original_node
            self.found = True
            return cst.RemoveFromParent()
        return updated_node

def _split_import(import_path: str) -> Tuple[str, str]:
    """Split an import path into module and name parts."""
    parts = import_path.split('.')
    return '.'.join(parts[:-1]), parts[-1]

def process_file_move(
    file_path: Path,
    old_path: str,
    new_path: str,
    extracted_def: Optional[cst.CSTNode] = None,
    dry_run: bool = False
) -> Tuple[bool, Optional[cst.CSTNode]]:
    """
    Process a single Python file for the move-def operation.
    
    Args:
        file_path: Path to the Python file
        old_path: The original import path (e.g., 'foo.bar.Baz')
        new_path: The new import path (e.g., 'lorem.ipsum.Baz')
        extracted_def: The definition to add (if this is the target file)
        dry_run: If True, don't modify the file
        
    Returns:
        Tuple[bool, Optional[cst.CSTNode]]: (changes_made, extracted_definition)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        module = cst.parse_module(source_code)
        old_module, name = _split_import(old_path)
        new_module, new_name = _split_import(new_path)
        
        # If this is the source file, extract the definition
        if extracted_def is None and str(file_path).replace('/', '.').endswith(old_module + '.py'):
            extractor = DefinitionExtractor(name)
            modified_module = module.visit(extractor)
            if extractor.found:
                display.info(f"Found definition of {name} in {file_path}")
                extracted_def = extractor.extracted_node
                
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_module.code)
                    display.success(f"Removed definition from {file_path}")
                return True, extracted_def
        
        # If this is the target file, add the definition
        elif extracted_def is not None and str(file_path).replace('/', '.').endswith(new_module + '.py'):
            # Add the definition to the module
            new_body = list(module.body)
            new_body.append(cst.EmptyLine())
            new_body.append(extracted_def)
            modified_module = module.with_changes(body=new_body)
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_module.code)
                display.success(f"Added definition to {file_path}")
            return True, None
        
        # Update imports in all files
        if extracted_def is not None:
            # Use the ImportReplacer to update imports
            from .import_replacer import ImportReplacer
            transformer = ImportReplacer(old_path, new_path)
            modified_module = module.visit(transformer)
            
            if transformer.changes_made:
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_module.code)
                    display.success(f"Updated imports in {file_path}")
                return True, None
        
        return False, None

    except Exception as e:
        display.error(f"Error processing {file_path}: {str(e)}")
        return False, None

def find_module_file(module_path: str, search_path: Path) -> Optional[Path]:
    """Find a Python file corresponding to a module path."""
    file_path = search_path / (module_path.replace('.', '/') + '.py')
    return file_path if file_path.exists() else None

def find_relevant_files(directory: Path, old_path: str) -> Set[Path]:
    """
    Find files that are likely to contain the definition or its imports.
    Uses ast for fast import scanning.
    """
    # Build a map of imports to files
    import_map = build_import_map(directory)
    
    # Find files that import the target
    relevant_files = set()
    old_module, name = _split_import(old_path)
    
    # Add files that import the module or the specific name
    for import_path, files in import_map.items():
        if import_path == old_path or import_path == old_module:
            relevant_files.update(files)
    
    # Add the source and target module files
    source_file = find_module_file(old_module, directory)
    if source_file:
        relevant_files.add(source_file)
    
    return relevant_files

def move_definition(
    directory: Path,
    old_path: str,
    new_path: str,
    dry_run: bool = False,
    max_workers: Optional[int] = None
) -> int:
    """
    Move a class or function definition between modules.
    Uses parallel processing and smart file selection for speed.
    
    Args:
        directory: Root directory to process
        old_path: Original import path (e.g., 'foo.bar.Baz')
        new_path: New import path (e.g., 'lorem.ipsum.Baz')
        dry_run: If True, don't modify files
        max_workers: Maximum number of parallel workers
    
    Returns:
        int: Number of files modified
    """
    # Find relevant files
    display.info("Scanning for relevant files...")
    files = list(find_relevant_files(directory, old_path))
    if not files:
        display.warning(f"No Python files found that use {old_path}")
        return 0
    
    display.info(f"Found {len(files)} relevant files")
    
    # First pass: extract the definition
    extracted_def = None
    old_module, name = _split_import(old_path)
    source_file = find_module_file(old_module, directory)
    
    if source_file:
        changes_made, extracted_def = process_file_move(
            source_file,
            old_path,
            new_path,
            dry_run=dry_run
        )
        if not extracted_def:
            display.error(f"Could not find definition for {old_path}")
            return 0
    else:
        display.error(f"Could not find source module for {old_path}")
        return 0
    
    # Second pass: update imports in parallel
    results = process_files_parallel(
        files,
        process_file_move,
        old_path,
        new_path,
        extracted_def=extracted_def,
        dry_run=dry_run,
        max_workers=max_workers
    )
    
    modified_count = sum(1 for r in results if r)
    
    if dry_run:
        display.show_dry_run_notice()
    
    return modified_count 