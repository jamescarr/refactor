"""Core functionality for replacing function calls."""
import libcst as cst
from libcst import matchers as m
from pathlib import Path
from typing import List, Tuple, Optional

from ..display import display
from .utils import find_python_files, process_files_parallel

class CallReplacer(cst.CSTTransformer):
    """Replace a function call with another function call."""
    
    def __init__(self, old_call: str, new_call: str):
        """
        Initialize with the old and new function call strings.
        
        Args:
            old_call: String representation of the old function call (e.g., "self.assert_401_UNAUTHORIZED")
            new_call: String representation of the new function call (e.g., "self.assert_403_FORBIDDEN")
        """
        self.old_call = old_call
        self.new_call = new_call
        self.changes_made = False
        
        # Parse the call strings to get components
        self._parse_call_strings()
    
    def _parse_call_strings(self):
        """Parse call strings into components for matching."""
        # Split by dots to get attributes/methods
        if '(' in self.old_call:
            # Handle case with arguments
            path_part, args_part = self.old_call.split('(', 1)
            self.old_parts = path_part.split('.')
            self.old_has_args = True
            self.old_args = args_part.rstrip(')')
        else:
            # Handle case without arguments
            self.old_parts = self.old_call.split('.')
            self.old_has_args = False
            self.old_args = ""
        
        self.old_method = self.old_parts[-1]
        
        if '(' in self.new_call:
            # Handle case with arguments
            path_part, args_part = self.new_call.split('(', 1)
            self.new_parts = path_part.split('.')
            self.new_has_args = True
            self.new_args = args_part.rstrip(')')
        else:
            # Handle case without arguments
            self.new_parts = self.new_call.split('.')
            self.new_has_args = False
            self.new_args = self.old_args  # Use the old args if new call doesn't specify
        
        self.new_method = self.new_parts[-1]
    
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        """Process a call expression, replacing it if it matches the target."""
        if self._matches_target_call(original_node):
            replacement = self._create_replacement_call(original_node)
            self.changes_made = True
            return replacement
        return updated_node
    
    def _matches_target_call(self, node: cst.Call) -> bool:
        """Check if a Call node matches our target function call."""
        # Check if it's a simple attribute access or a more complex call
        if not isinstance(node.func, cst.Attribute):
            return False
        
        # Extract the attribute chain
        current = node.func
        parts = [current.attr.value]
        
        while isinstance(current.value, cst.Attribute):
            current = current.value
            parts.append(current.attr.value)
        
        # Check the base name
        if not isinstance(current.value, cst.Name):
            return False
        
        parts.append(current.value.value)
        parts.reverse()
        
        # Compare attribute chain with our target parts
        if parts != self.old_parts:
            return False
            
        # If we have specific arguments to match and the call has arguments
        if self.old_has_args and node.args:
            try:
                # Convert the args to a string for comparison
                args_str = self._args_to_string(node.args)
                # Compare with expected args
                return args_str.strip() == self.old_args.strip()
            except Exception:
                # If we can't convert the args, assume no match
                return False
        
        return True
    
    def _args_to_string(self, args: List[cst.Arg]) -> str:
        """Convert a list of CST Arg nodes to a string representation."""
        result = []
        for arg in args:
            if arg.keyword:
                result.append(f"{arg.keyword.value}={self._node_to_string(arg.value)}")
            else:
                result.append(self._node_to_string(arg.value))
        return ", ".join(result)
    
    def _node_to_string(self, node: cst.CSTNode) -> str:
        """Convert a CST node to string representation for comparison."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Integer):
            return str(node.value)
        elif isinstance(node, cst.Float):
            return str(node.value)
        elif isinstance(node, cst.Attribute):
            return f"{self._node_to_string(node.value)}.{node.attr.value}"
        elif isinstance(node, cst.Call):
            args_str = self._args_to_string(node.args)
            func_str = self._node_to_string(node.func)
            return f"{func_str}({args_str})"
        # Add more types as needed
        return str(node)
    
    def _create_replacement_call(self, original_node: cst.Call) -> cst.Call:
        """Create a replacement Call node."""
        # Start building from the innermost name
        updated_func = cst.Name(value=self.new_parts[0])
        
        # Build the attribute chain
        for part in self.new_parts[1:]:
            updated_func = cst.Attribute(value=updated_func, attr=cst.Name(value=part))
        
        # If we specified new args and the call is different
        if self.new_has_args and self.new_args != self.old_args:
            # Parse and create new args - this is simplified and might need enhancement
            args = []
            for arg in self.new_args.split(','):
                arg = arg.strip()
                if arg:  # Skip empty args
                    args.append(cst.Arg(value=cst.parse_expression(arg)))
            
            return original_node.with_changes(func=updated_func, args=args)
        
        # Otherwise just replace the function name but keep original args
        return original_node.with_changes(func=updated_func)

def process_file_call(
    file_path: Path,
    old_call: str,
    new_call: str,
    dry_run: bool = False
) -> bool:
    """
    Process a single Python file for the replace-call operation.
    
    Args:
        file_path: Path to the Python file
        old_call: Original function call pattern
        new_call: New function call pattern
        dry_run: If True, don't modify the file
    
    Returns:
        bool: Whether changes were made
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        module = cst.parse_module(source_code)
        transformer = CallReplacer(old_call, new_call)
        modified_module = module.visit(transformer)
        
        if transformer.changes_made:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_module.code)
                display.success(f"Updated calls in {file_path}")
            else:
                display.info(f"Would update calls in {file_path}")
            return True
        
        return False

    except Exception as e:
        display.error(f"Error processing {file_path}: {str(e)}")
        return False

def replace_call(
    directory: Path,
    old_call: str,
    new_call: str,
    dry_run: bool = False,
    max_workers: int = None
) -> int:
    """
    Replace function calls across Python files in a directory.
    
    Args:
        directory: Root directory to process
        old_call: Original function call pattern (e.g., "self.assert_401_UNAUTHORIZED")
        new_call: New function call pattern (e.g., "self.assert_403_FORBIDDEN")
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
        process_file_call,
        old_call,
        new_call,
        dry_run=dry_run,
        max_workers=max_workers
    )
    
    modified_count = sum(1 for r in results if r)
    
    if dry_run:
        display.show_dry_run_notice()
    
    return modified_count 