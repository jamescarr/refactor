"""Core functionality for import replacement."""
import libcst as cst
from libcst import matchers as m
from typing import Tuple, List
from pathlib import Path

from ..display import display
from .utils import find_python_files, process_files_parallel

class ImportReplacer(cst.CSTTransformer):
    """Transform imports in a Python module using libCST."""

    def __init__(self, old_import: str, new_import: str):
        """
        Initialize the transformer with the old and new import paths.

        Args:
            old_import: The import to be replaced (e.g., 'foo.bar.baz.PermissionDenied')
            new_import: The replacement import (e.g., 'rest_framework.exc.PermissionDenied')
        """
        self.old_module, self.old_name = self._split_import(old_import)
        self.new_module, self.new_name = self._split_import(new_import)
        self.changes_made = False

    def _split_import(self, import_path: str) -> Tuple[str, str]:
        """Split an import path into module and name parts."""
        parts = import_path.split('.')
        # Handle cases like 'module.submodule.Name'
        return '.'.join(parts[:-1]), parts[-1]

    def _create_module_node(self, module_path: str) -> cst.BaseExpression:
        """Create a module node from a dot-separated path."""
        parts = module_path.split('.')
        if not parts or parts[0] == '':
            return cst.Name(value='')
            
        result = cst.Name(value=parts[0])
        for part in parts[1:]:
            result = cst.Attribute(value=result, attr=cst.Name(value=part))
        return result

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        """Process 'from x import y' style imports."""
        # Check if this is the module we're looking to replace
        if m.matches(updated_node.module, m.Name(value=self.old_module)) or (
            isinstance(updated_node.module, cst.Attribute) and
            self._get_full_module_name(updated_node.module) == self.old_module
        ):
            # Check if the target name is in the imports
            for import_alias in updated_node.names:
                if m.matches(import_alias.name, m.Name(value=self.old_name)):
                    self.changes_made = True

                    # Remove the target name from the imports while preserving formatting
                    new_names = []
                    for alias in updated_node.names:
                        if not m.matches(alias.name, m.Name(value=self.old_name)):
                            new_names.append(alias)

                    # If this was the only import, replace the whole statement
                    if not new_names:
                        return cst.ImportFrom(
                            module=self._create_module_node(self.new_module),
                            names=[cst.ImportAlias(name=cst.Name(value=self.new_name))],
                            whitespace_after_from=updated_node.whitespace_after_from,
                            whitespace_before_import=updated_node.whitespace_before_import,
                            whitespace_after_import=updated_node.whitespace_after_import,
                        )

                    # Otherwise, keep the existing import with the name removed
                    return updated_node.with_changes(
                        names=new_names
                    )

        return updated_node

    def _get_full_module_name(self, node: cst.CSTNode) -> str:
        """Recursively build a full module name from an Attribute node."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{self._get_full_module_name(node.value)}.{node.attr.value}"
        return ""

    def visit_Module(self, node: cst.Module) -> None:
        """Process the entire module and prepare for modifications."""
        self.changes_made = False

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """
        After processing the module, add new import if we removed one.
        This ensures we add the replacement import if we removed one from an existing import.
        """
        if self.changes_made:
            # Add the new import at the top of the file
            new_import = cst.SimpleStatementLine(
                body=[
                    cst.ImportFrom(
                        module=self._create_module_node(self.new_module),
                        names=[cst.ImportAlias(name=cst.Name(value=self.new_name))],
                    )
                ]
            )

            # Add to the beginning of the imports section
            return updated_node.with_changes(
                body=[new_import] + list(updated_node.body)
            )
        return updated_node


def process_file(file_path: Path, old_import: str, new_import: str, dry_run: bool) -> bool:
    """
    Process a single Python file to replace imports.

    Args:
        file_path: Path to the Python file
        old_import: The import to be replaced
        new_import: The replacement import
        dry_run: If True, don't actually modify the file

    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Parse the source code into a CST
        module = cst.parse_module(source_code)

        # Apply our transformer
        transformer = ImportReplacer(old_import, new_import)
        modified_module = module.visit(transformer)

        # If changes were made, write them back or print them
        if transformer.changes_made:
            modified_code = modified_module.code

            # Show the changes as a diff
            display.show_diff(source_code, modified_code, file_path)

            # Write changes if not in dry run mode
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_code)
                display.success(f"Updated {file_path}")
            else:
                display.warning("Dry run - no changes written")

            return True

        return False

    except Exception as e:
        display.error(f"Error processing {file_path}: {str(e)}")
        return False

def replace_import(
    directory: Path,
    old_import: str,
    new_import: str,
    dry_run: bool = False,
    max_workers: int = None
) -> int:
    """
    Replace imports across Python files in a directory.
    
    Args:
        directory: Root directory to process
        old_import: Original import path (e.g., 'foo.bar.Baz')
        new_import: New import path (e.g., 'lorem.ipsum.Baz')
        dry_run: If True, don't modify files
        max_workers: Maximum number of parallel workers
    
    Returns:
        int: Number of files modified
    """
    python_files = find_python_files(directory)
    if not python_files:
        display.warning(f"No Python files found in {directory}")
        return 0
    
    display.info(f"Searching {len(python_files)} files")
    
    results = process_files_parallel(
        python_files,
        process_file,
        old_import,
        new_import,
        dry_run=dry_run,
        max_workers=max_workers
    )
    
    modified_count = sum(1 for r in results if r)
    
    if dry_run:
        display.show_dry_run_notice()
    
    return modified_count