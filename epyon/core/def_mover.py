"""Core functionality for moving definitions between modules."""
import libcst as cst
from libcst import matchers as m
from typing import Tuple, List, Optional
from pathlib import Path

from ..display import display
from .utils import find_python_files

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